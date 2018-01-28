import base64
import json
import unittest

from tinyauth.app import create_app, db
from tinyauth.models import AccessKey, Group, User, UserPolicy


class TestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(self)
        self.app.debug = True
        self.app.config['BUNDLE_ERRORS'] = True
        self.app.config['TESTING'] = True
        self.app.config['DEBUG'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        db.create_all(app=self.app)

        self._ctx = self.app.test_request_context()
        self._ctx.push()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self._ctx.pop()

    def fixture_charles(self):
        user = User(username='charles')
        db.session.add(user)

        policy = UserPolicy(name='tinyauth', user=user, policy={
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'tinyauth:*',
                'Resource': 'arn:tinyauth:*',
                'Effect': 'Allow',
            }]
        })
        db.session.add(policy)

        access_key = AccessKey(
            access_key_id='AKIDEXAMPLE',
            secret_access_key='password',
            user=user,
        )
        db.session.add(access_key)

        db.session.commit()

    def test_get_groups_no_groups(self):
        self.fixture_charles()

        response = self.client.get(
            '/api/v1/groups',
            headers={
                'Authorization': 'Basic {}'.format(
                    base64.b64encode(b'AKIDEXAMPLE:password').decode('utf-8')
                ),
            }
        )

        assert response.status_code == 200
        assert response.get_data(as_text=True) == '[]\n'
        assert b''.join(response.response) == b'[]\n'

    def test_create_group_noauth(self):
        response = self.client.post(
            '/api/v1/groups',
            data=json.dumps({
                'name': 'devs',
            }),
            content_type='application/json',
        )
        assert response.status_code == 401
        assert json.loads(response.get_data(as_text=True)) == {
            'errors': {
                'authorization': 'UnsignedRequest'
            }
        }

    def test_create_group_with_auth(self):
        self.fixture_charles()

        response = self.client.post(
            '/api/v1/groups',
            data=json.dumps({
                'name': 'devs',
            }),
            headers={
                'Authorization': 'Basic {}'.format(
                    base64.b64encode(b'AKIDEXAMPLE:password').decode('utf-8')
                )
            },
            content_type='application/json',
        )
        assert response.status_code == 200
        assert json.loads(response.get_data(as_text=True)) == {'id': 1, 'name': 'devs'}

    def test_delete_group_with_auth_but_no_perms(self):
        user = User(username='charles')
        db.session.add(user)

        policy = UserPolicy(name='tinyauth', user=user, policy={
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'tinyauth:DeleteUser',
                'Resource': 'arn:tinyauth:*',
                'Effect': 'Allow',
            }]
        })
        db.session.add(policy)

        grp = Group(name='freddy')
        db.session.add(grp)

        access_key = AccessKey(
            access_key_id='AKIDEXAMPLE',
            secret_access_key='password',
            user=user,
        )
        db.session.add(access_key)

        db.session.commit()

        response = self.client.delete(
            '/api/v1/groups/1',
            headers={
                'Authorization': 'Basic {}'.format(
                    base64.b64encode(b'AKIDEXAMPLE:password').decode('utf-8')
                )
            },
            content_type='application/json',
        )
        assert response.status_code == 403
        assert json.loads(response.get_data(as_text=True)) == {
            'errors': {
                'authorization': 'NotPermitted'
            }
        }

    def test_delete_group_with_auth(self):
        user = User(username='charles')
        db.session.add(user)

        policy = UserPolicy(name='tinyauth', user=user, policy={
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'tinyauth:*',
                'Resource': 'arn:tinyauth:*',
                'Effect': 'Allow',
            }]
        })
        db.session.add(policy)

        access_key = AccessKey(
            access_key_id='AKIDEXAMPLE',
            secret_access_key='password',
            user=user,
        )
        db.session.add(access_key)

        grp = Group(name='devs')
        db.session.add(grp)

        db.session.commit()

        response = self.client.delete(
            '/api/v1/groups/1',
            headers={
                'Authorization': 'Basic {}'.format(
                    base64.b64encode(b'AKIDEXAMPLE:password').decode('utf-8')
                )
            },
            content_type='application/json',
        )
        assert response.status_code == 201
        assert json.loads(response.get_data(as_text=True)) == {}
