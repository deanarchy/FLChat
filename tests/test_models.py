import unittest
from app import create_app, db
from app.models import User, Message, Conversation, Contact


class UserTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u = User(password='test123')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='test123')
        self.assertTrue(u.verify_password('test123'))
        self.assertFalse(u.verify_password('test321'))


class ConversationTestCase(unittest.TestCase):
    def setUp(self):
        self.test_email = 'test@test.com'
        self.test_phone = '02179187676'
        self.test_password = 'testing123'
        self.test_first_name = 'test'
        self.test_last_name = '123'

        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.test_user = User(
            email=self.test_email,
            phone=self.test_phone,
            password=self.test_password,
            first_name=self.test_first_name,
            last_name=self.test_last_name
        )
        db.session.add(self.test_user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_personal_chat(self):
        u = User(
            email="target@test.com",
            first_name='target',
            password='test123'
        )
        db.session.add(u)
        db.session.commit()

        c = self.test_user.start_personal_chat(u)
        db.session.add(c)
        db.session.commit()

        self.assertEqual(c.creator, self.test_user)
        self.assertTrue(c.title.startswith('pc'))
        self.assertIn(u, c.participants.all())
        self.assertIn(self.test_user, c.participants.all())
        self.assertTrue(len(c.participants.all()) == 2)

        self.assertIn(c, self.test_user.conversations)
        self.assertIn(c, self.test_user.participates)
        self.assertIn(c, u.participates)
        self.assertNotIn(c, u.conversations)

    def test_multiperson_chat(self):
        u1 = User(
            email="target1@test.com",
            first_name='target1',
            password='test123'
        )
        u2 = User(
            email="target2@test.com",
            first_name='target2',
            password='test123'
        )
        db.session.add_all([u1, u2])
        db.session.commit()

        c = self.test_user.start_multiperson_chat(name='test_group')
        db.session.add(c)
        db.session.commit()

        self.assertEqual(c.creator, self.test_user)
        self.assertTrue(c.title.startswith('mpc'))
        self.assertIn('test_group', c.title)

        c.add_user_to_mpc(u1)
        c.add_user_to_mpc(u2)

        self.assertIn(self.test_user, c.participants.all())
        self.assertIn(u1, c.participants.all())
        self.assertIn(u2, c.participants.all())

        self.assertIn(c, self.test_user.conversations)
        self.assertIn(c, u1.participates)
        self.assertIn(c, u2.participates)
        self.assertNotIn(c, u1.conversations)
        self.assertNotIn(c, u2.conversations)


class MessageContactTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.test_user1 = User(
            email='user1@test.com',
            password='test123',
            first_name='user1',
        )

        self.test_user2 = User(
            email='user2@test.com',
            password='test123',
            first_name='user2',
        )

        self.test_user3 = User(
            email='user3@test.com',
            password='test123',
            first_name='user3',
        )
        db.session.add_all([self.test_user1, self.test_user2, self.test_user3])
        db.session.commit()

        self.test_pc = self.test_user1.start_personal_chat(self.test_user2)
        self.test_mpc = self.test_user1.start_multiperson_chat()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_send_message_init_pc(self):
        self.test_user1.send_message(self.test_pc, 'Test321')
        message = self.test_pc.messages.filter_by(message='Test321').first()

        self.assertEqual(len(message.conversation.participants.all()), 2)
        self.assertTrue(message)
        self.assertEqual(message.sender, self.test_user1)
        for participant in self.test_pc.participants:
            m = participant.participates.filter(Conversation.title.startswith('pc')).first().messages.filter_by(message='Test321').first()
            self.assertTrue(m)

    def test_send_message_init_mpc(self):
        self.test_user1.send_message(self.test_mpc, 'Test123')
        message = self.test_mpc.messages.filter_by(message='Test123').first()

        self.assertTrue(message)
        self.assertEqual(message.sender, self.test_user1)

        message.conversation.add_user_to_mpc(self.test_user2)
        message.conversation.add_user_to_mpc(self.test_user3)

        self.assertEqual(len(message.conversation.participants.all()), 3)

        for participant in message.conversation.participants:
            m = participant.participates.filter(Conversation.title.startswith('mpc')).first().messages.filter_by(message='Test123').first()
            self.assertTrue(m)

    def test_add_contact(self):
        self.test_user1.add_contact(self.test_user2)
        self.test_user1.add_contact(self.test_user3)

        for contact in self.test_user1.contacts:
            self.assertTrue(self.test_user1.is_contact(contact))
            self.assertFalse(contact.is_contact(self.test_user1))


