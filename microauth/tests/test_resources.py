import base64
import json
import unittest

from microauth.app import app, db
from microauth.models import AccessKey, Policy, User


class TestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_get_users_no_users(self):
        response = self.client.get('/api/v1/users')
        assert response.status_code == 200
        assert response.get_data(as_text=True) == '[]\n'
        assert b''.join(response.response) == b'[]\n'

    def test_create_user_noauth(self):
        response = self.client.post(
            '/api/v1/users',
            data=json.dumps({
                'username': 'freddy',
            }),
            content_type='application/json',
        )
        assert response.status_code == 401
        assert response.get_data(as_text=True) == '{"message": "NoSuchKey"}\n'

    def test_create_user_with_auth(self):
        policy = Policy(name='microauth', policy={
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'microauth:*',
                'Resource': 'arn:microauth:*',
                'Effect': 'Allow',
            }]
        })
        db.session.add(policy)

        user = User(username='charles')
        user.policies.append(policy)
        db.session.add(user)

        access_key = AccessKey(
            access_key_id='AKIDEXAMPLE',
            secret_access_key='password',
            user=user,
        )
        db.session.add(access_key)

        db.session.commit()

        response = self.client.post(
            '/api/v1/users',
            data=json.dumps({
                'username': 'freddy',
            }),
            headers={
                'Authorization': 'Basic {}'.format(
                    base64.b64encode(b'AKIDEXAMPLE:password').decode('utf-8')
                )
            },
            content_type='application/json',
        )
        assert response.status_code == 200
        assert json.loads(response.get_data(as_text=True)) == {'id': 2, 'username': 'freddy'}
