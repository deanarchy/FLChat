import unittest
from app import create_app, db
from app.models import User


class ClientTestCase(unittest.TestCase):
    def setUp(self):
        self.fragment_user_data = \
            fr'''
                fragment userData on User {{
                    email,
                    phone,
                    firstName,
                    lastName,
                    createdAt,
                    isAdmin
                    isActive

                }}
            '''
        self.test_email = 'test@test.com'
        self.test_phone = '02179187676'
        self.test_password = 'testing123'
        self.test_first_name = 'test'
        self.test_last_name = '123'

        self.endpoint = '/api/graphql'

        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_headers(self, access_tokens):
        return {
            'Authorization':
                'Bearer ' + access_tokens,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

    def test_endpoint(self):
        response_get = self.client.get('/api/graphql?query={hello}')
        response_post = self.client.post(
            self.endpoint, json={'query': '{hello}'}
        )
        self.assertEqual(response_get.status_code, 200)
        self.assertEqual(response_post.status_code, 200)
        self.assertTrue('hello' in response_get.get_json()['data'])
        self.assertTrue('hello' in response_post.get_json()['data'])

    def test_register_login(self):
        response = self.client.post(
            self.endpoint, json={
                'query':
                    fr'''
                    mutation {{
                        register (
                            email: "{self.test_email}",
                            phone: "{self.test_phone}",
                            password: "{self.test_password}",
                            passwordConfirm: "{self.test_password}",
                            firstName: "{self.test_first_name}",
                            lastName: "{self.test_last_name}",
                        ) {{
                            success
                            user {{
                                ...userData
                            }}
                        }}
                    }}
                    
                    {self.fragment_user_data}
                    '''
            }
        )
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()['data']['register']
        self.assertTrue(response_data['success'])

        response = self.client.post(
            self.endpoint, json={
                'query':
                    fr'''
                    mutation {{
                        login (
                            email: "{self.test_email}",
                            password: "{self.test_password}"
                        ) {{
                            accessToken
                            refreshToken
                        }}
                    }}
                    '''
            }
        )
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()['data']['login']
        access_token = response_data['accessToken']
        refresh_token = response_data['refreshToken']

        self.assertTrue(access_token)
        self.assertTrue(refresh_token)

        response = self.client.post(
            self.endpoint, json={
                'query':
                    fr'''
                    query {{
                        me {{
                            ...userData
                        }}
                    }} 
                    
                    {self.fragment_user_data}
                    '''
            }, headers=self.get_headers(access_token)
        )

        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()['data']['me']

        self.assertEqual(self.test_email, response_data['email'])
        self.assertEqual(self.test_phone, response_data['phone'])
        self.assertEqual(self.test_first_name, response_data['firstName'])
        self.assertEqual(self.test_last_name, response_data['lastName'])
        self.assertTrue(response_data['isActive'])
        self.assertFalse(response_data['isAdmin'])
