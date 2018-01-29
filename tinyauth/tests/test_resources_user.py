import base64
import json

from tinyauth.app import db
from tinyauth.models import AccessKey, User

from .base import TestCase


class TestCase(TestCase):

    def fixture_charles(self):
        pass

    def test_list_users(self):
        response = self.client.get(
            '/api/v1/users',
            headers={
                'Authorization': 'Basic {}'.format(
                    base64.b64encode(b'AKIDEXAMPLE:password').decode('utf-8')
                ),
            }
        )

        assert response.status_code == 200
        assert json.loads(response.get_data(as_text=True)) == [{
            'groups': [],
            'id': 1,
            'username': 'charles',
        }]

    def test_create_user_noauth(self):
        response = self.client.post(
            '/api/v1/users',
            data=json.dumps({
                'username': 'freddy',
            }),
            content_type='application/json',
        )
        assert response.status_code == 401
        assert json.loads(response.get_data(as_text=True)) == {
            'errors': {
                'authorization': 'UnsignedRequest'
            }
        }

    def test_create_user_with_auth(self):
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
        assert json.loads(response.get_data(as_text=True)) == {'id': 2, 'username': 'freddy', 'groups': []}

    def test_delete_user_with_auth_but_no_perms(self):
        user = User(username='freddy')
        db.session.add(user)

        access_key = AccessKey(
            access_key_id='AKIDEXAMPLE2',
            secret_access_key='password',
            user=user,
        )
        db.session.add(access_key)

        db.session.commit()

        response = self.client.delete(
            '/api/v1/users/1',
            headers={
                'Authorization': 'Basic {}'.format(
                    base64.b64encode(b'AKIDEXAMPLE2:password').decode('utf-8')
                )
            },
            content_type='application/json',
        )
        assert response.status_code == 403
        assert json.loads(response.get_data(as_text=True)) == {
            'errors': {
                'authorization': 'NotPermitted',
            }
        }

    def test_delete_user_with_auth(self):
        user = User(username='freddy')
        db.session.add(user)

        db.session.commit()

        response = self.client.delete(
            '/api/v1/users/2',
            headers={
                'Authorization': 'Basic {}'.format(
                    base64.b64encode(b'AKIDEXAMPLE:password').decode('utf-8')
                )
            },
            content_type='application/json',
        )
        assert response.status_code == 201
        assert json.loads(response.get_data(as_text=True)) == {}

    def test_put_user_with_auth_but_no_perms(self):
        user = User(username='freddy')
        db.session.add(user)

        access_key = AccessKey(
            access_key_id='AKIDEXAMPLE2',
            secret_access_key='password',
            user=user,
        )
        db.session.add(access_key)

        db.session.commit()

        response = self.client.put(
            '/api/v1/users/1',
            data=json.dumps({
                'username': 'freddy',
                'password': 'password',
            }),
            headers={
                'Authorization': 'Basic {}'.format(
                    base64.b64encode(b'AKIDEXAMPLE2:password').decode('utf-8')
                )
            },
            content_type='application/json',
        )
        assert response.status_code == 403
        assert json.loads(response.get_data(as_text=True)) == {
            'errors': {
                'authorization': 'NotPermitted',
            }
        }

    def test_put_user_with_auth(self):
        user = User(username='freddy')
        db.session.add(user)

        db.session.commit()

        response = self.client.put(
            '/api/v1/users/2',
            data=json.dumps({
                'username': 'freddy',
                'password': 'password',
            }),
            headers={
                'Authorization': 'Basic {}'.format(
                    base64.b64encode(b'AKIDEXAMPLE:password').decode('utf-8')
                )
            },
            content_type='application/json',
        )
        assert response.status_code == 200
        assert json.loads(response.get_data(as_text=True)) == {
            'groups': [],
            'id': 2,
            'username': 'freddy'
        }

    def test_get_user_with_auth_but_no_perms(self):
        user = User(username='freddy')
        db.session.add(user)

        access_key = AccessKey(
            access_key_id='AKIDEXAMPLE2',
            secret_access_key='password',
            user=user,
        )
        db.session.add(access_key)

        db.session.commit()

        response = self.client.get(
            '/api/v1/users/1',
            headers={
                'Authorization': 'Basic {}'.format(
                    base64.b64encode(b'AKIDEXAMPLE2:password').decode('utf-8')
                )
            },
            content_type='application/json',
        )
        assert response.status_code == 403
        assert json.loads(response.get_data(as_text=True)) == {
            'errors': {
                'authorization': 'NotPermitted',
            }
        }

    def test_get_user_with_auth(self):
        user = User(username='freddy')
        db.session.add(user)

        db.session.commit()

        response = self.client.get(
            '/api/v1/users/2',
            headers={
                'Authorization': 'Basic {}'.format(
                    base64.b64encode(b'AKIDEXAMPLE:password').decode('utf-8')
                )
            },
            content_type='application/json',
        )
        assert response.status_code == 200
        assert json.loads(response.get_data(as_text=True)) == {
            'groups': [],
            'id': 2,
            'username': 'freddy'
        }
