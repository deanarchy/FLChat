from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from . import db, jwt


class Contact(db.Model):
    adder_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    added_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)


participants = db.Table(
    'participants',
    db.Column('conversation_id', db.Integer, db.ForeignKey('conversation.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)


class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(), default=f'conversation-{creator_id}')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    creator = db.relationship(
        'User', back_populates='conversations'
    )
    participants = db.relationship(
        'User', secondary=participants,
        back_populates='participates', lazy='dynamic'
    )
    messages = db.relationship(
        'Message', back_populates='conversation', lazy='dynamic'
    )

    def __repr__(self):
        return f'<CONV {self.title}>'

    def add_user_to_mpc(self, user):
        self.participants.append(user)

        db.session.add(self)
        db.session.commit()


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'))
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    message = db.Column(db.Text, nullable=False)

    conversation = db.relationship('Conversation', back_populates='messages')
    sender = db.relationship('User', back_populates='messages')

    def __repr__(self):
        return f'<MSG: {self.message[:20]}>'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(16), unique=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    first_name = db.Column(db.String(32), nullable=False)
    last_name = db.Column(db.String(32))
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(255), nullable=False)

    conversations = db.relationship(
        'Conversation', back_populates='creator', lazy='dynamic'
    )
    participates = db.relationship(
        'Conversation', secondary=participants,
        back_populates='participants', lazy='dynamic'
    )
    messages = db.relationship(
        'Message', back_populates='sender', lazy='dynamic'
    )
    contacts_added = db.relationship(
        'Contact',
        foreign_keys=[Contact.adder_id],
        backref=db.backref('adder', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'

    )
    contacts_adders = db.relationship(
        'Contact',
        foreign_keys=[Contact.added_id],
        backref=db.backref('added', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<USER: {self.email}>'

    @property
    def password(self):
        raise AttributeError('password is not readable')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_contact(self, user):
        if user.id is None:
            return False
        return self.contacts_added.filter_by(added_id=user.id).first() is not None

    def add_contact(self, user):
        if not self.is_contact(user):
            contact = Contact(adder=self, added=user)
            db.session.add(contact)
            db.session.commit()

    @property
    def contacts(self):
        return [x.added for x in self.contacts_added]

    def create_chat(self, pc=True):
        conversation = Conversation(
            title=f'{"pc" if pc else "mpc"}-{self.first_name}',
            creator=self,
            participants=[self]
        )
        return conversation

    def start_personal_chat(self, target):
        conversation = Conversation.query.filter(
            Conversation.participants.contains(self),
            Conversation.participants.contains(target),
            Conversation.title.startswith("pc")
        ).first()

        if not conversation:
            conversation = self.create_chat()
            conversation.participants.append(target)
            conversation.title += f' to {target.first_name}'
            db.session.add(conversation)
            db.session.commit()
        return conversation

    def start_multiperson_chat(self, mpc_id=0, name=None, targets=None):
        conversation = Conversation.query.get(mpc_id)

        if not conversation:
            conversation = self.create_chat(pc=False)
            if name:
                conversation.title += f' {name}'
            if targets:
                for target in targets:
                    conversation.add_user_to_mpc(target)
            db.session.add(conversation)
            db.session.commit()
        return conversation

    def send_message(self, conv, message):
        msg = Message(sender=self, conversation=conv, message=message)
        conv.updated_at = datetime.utcnow()

        db.session.add(conv)
        db.session.add(msg)
        db.session.commit()


@jwt.user_identity_loader
def user_identity_lookup(user):
    return user


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(email=identity).one_or_none()
