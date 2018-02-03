import base64
import json

from tinyauth.app import db
from tinyauth.models import AccessKey, User

from .base import TestCase


class TestCase(TestCase):

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
            'id': 'charles',
            'username': 'charles',
        }, {
            'groups': [],
            'id': 'freddy',
            'username': 'freddy',
        }]

        args, kwargs = self.audit_log.call_args_list[0]
        assert args[0] == 'ListUsers'
        assert kwargs['extra'] == {
            'request-id': 'a823a206-95a0-4666-b464-93b9f0606d7b',
            'http.status': 200,
        }

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

        args, kwargs = self.audit_log.call_args_list[0]
        assert args[0] == 'CreateUser'
        assert kwargs['extra'] == {
            'request-id': 'a823a206-95a0-4666-b464-93b9f0606d7b',
            'http.status': 401,
            'request.username': 'freddy',
            'errors': {'authorization': 'UnsignedRequest'},
        }

    def test_create_user_with_auth(self):
        response = self.client.post(
            '/api/v1/users',
            data=json.dumps({
                'username': 'mruser',
                'password': 'pAssword',
            }),
            headers={
                'Authorization': 'Basic {}'.format(
                    base64.b64encode(b'AKIDEXAMPLE:password').decode('utf-8')
                )
            },
            content_type='application/json',
        )
        assert response.status_code == 200
        assert json.loads(response.get_data(as_text=True)) == {'id': 'mruser', 'username': 'mruser', 'groups': []}

        args, kwargs = self.audit_log.call_args_list[0]
        assert args[0] == 'CreateUser'
        assert kwargs['extra'] == {
            'request-id': 'a823a206-95a0-4666-b464-93b9f0606d7b',
            'request.username': 'mruser',
            'http.status': 200,
        }

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
            '/api/v1/users/charles',
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

        args, kwargs = self.audit_log.call_args_list[0]
        assert args[0] == 'DeleteUser'
        assert kwargs['extra'] == {
            'request-id': 'a823a206-95a0-4666-b464-93b9f0606d7b',
            'http.status': 403,
            'errors': {'authorization': 'NotPermitted'},
            'request.username': 'charles',
        }

    def test_delete_user_with_auth(self):
        user = User(username='freddy')
        db.session.add(user)

        db.session.commit()

        response = self.client.delete(
            '/api/v1/users/freddy',
            headers={
                'Authorization': 'Basic {}'.format(
                    base64.b64encode(b'AKIDEXAMPLE:password').decode('utf-8')
                )
            },
            content_type='application/json',
        )
        assert response.status_code == 201
        assert json.loads(response.get_data(as_text=True)) == {}

        args, kwargs = self.audit_log.call_args_list[0]
        assert args[0] == 'DeleteUser'
        assert kwargs['extra'] == {
            'request-id': 'a823a206-95a0-4666-b464-93b9f0606d7b',
            'http.status': 201,
            'request.username': 'freddy',
        }

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
            '/api/v1/users/charles',
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

        args, kwargs = self.audit_log.call_args_list[0]
        assert args[0] == 'UpdateUser'
        assert kwargs['extra'] == {
            'request-id': 'a823a206-95a0-4666-b464-93b9f0606d7b',
            'http.status': 403,
            'errors': {'authorization': 'NotPermitted'},
            'request.username': 'charles',
        }

    def test_put_user_with_auth(self):
        user = User(username='freddy')
        db.session.add(user)

        db.session.commit()

        response = self.client.put(
            '/api/v1/users/freddy',
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
            'id': 'freddy',
            'username': 'freddy'
        }

        args, kwargs = self.audit_log.call_args_list[0]
        assert args[0] == 'UpdateUser'
        assert kwargs['extra'] == {
            'request-id': 'a823a206-95a0-4666-b464-93b9f0606d7b',
            'http.status': 200,
            'request.username': 'freddy',
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
            '/api/v1/users/charles',
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

        args, kwargs = self.audit_log.call_args_list[0]
        assert args[0] == 'GetUser'
        assert kwargs['extra'] == {
            'request-id': 'a823a206-95a0-4666-b464-93b9f0606d7b',
            'http.status': 403,
            'errors': {'authorization': 'NotPermitted'},
            'request.username': 'charles',
        }

    def test_get_user_with_auth(self):
        user = User(username='freddy')
        db.session.add(user)

        db.session.commit()

        response = self.client.get(
            '/api/v1/users/freddy',
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
            'id': 'freddy',
            'username': 'freddy'
        }

        args, kwargs = self.audit_log.call_args_list[0]
        assert args[0] == 'GetUser'
        assert kwargs['extra'] == {
            'request-id': 'a823a206-95a0-4666-b464-93b9f0606d7b',
            'http.status': 200,
            'request.username': 'freddy',
        }

    def test_get_user_with_auth_but_no_perms_404(self):
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
            '/api/v1/users/james',
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

        args, kwargs = self.audit_log.call_args_list[0]
        assert args[0] == 'GetUser'
        assert kwargs['extra'] == {
            'request-id': 'a823a206-95a0-4666-b464-93b9f0606d7b',
            'http.status': 403,
            'errors': {'authorization': 'NotPermitted'},
            'request.username': 'james',
        }

    def test_get_user_with_auth_404(self):
        response = self.client.get(
            '/api/v1/users/james',
            headers={
                'Authorization': 'Basic {}'.format(
                    base64.b64encode(b'AKIDEXAMPLE:password').decode('utf-8')
                )
            },
            content_type='application/json',
        )
        assert response.status_code == 404

        args, kwargs = self.audit_log.call_args_list[0]
        assert args[0] == 'GetUser'
        assert kwargs['extra'] == {
            'request-id': 'a823a206-95a0-4666-b464-93b9f0606d7b',
            'http.status': 404,
            'request.username': 'james',
        }
