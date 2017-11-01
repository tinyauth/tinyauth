import base64
import json
import unittest

from microauth.app import app, db
from microauth.models import AccessKey, Group, Policy, User


class TestCase(unittest.TestCase):

    def setUp(self):
        app.debug = True
        app.config['BUNDLE_ERRORS'] = True
        app.config['TESTING'] = True
        app.config['DEBUG'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_get_groups_no_users(self):
        response = self.client.get('/api/v1/groups')
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
            'message': {
                'Authorized': False,
                'ErrorCode': 'NoSuchKey',
            }
        }

    def test_create_group_with_auth(self):
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
        policy = Policy(name='microauth', policy={
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'microauth:DeleteUser',
                'Resource': 'arn:microauth:*',
                'Effect': 'Allow',
            }]
        })
        db.session.add(policy)

        user = User(username='charles')
        user.policies.append(policy)
        db.session.add(user)

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
        assert response.status_code == 401
        assert json.loads(response.get_data(as_text=True)) == {
            'message': {
                'Authorized': False,
                'ErrorCode': 'NotPermitted',
            }
        }

    def test_delete_group_with_auth(self):
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
