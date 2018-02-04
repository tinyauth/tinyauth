import json
from unittest import mock

from . import base


class TestCase(base.TestCase):

    def test_list_access_keys(self):
        response = self.req('get', '/api/v1/users/charles/keys')

        assert response.status_code == 200
        assert json.loads(response.get_data(as_text=True)) == [{
            'id': 'AKIDEXAMPLE',
            'access_key_id': 'AKIDEXAMPLE',
        }]

        args, kwargs = self.audit_log.call_args_list[0]
        assert args[0] == 'ListAccessKeys'
        assert kwargs['extra'] == {
            'request-id': 'a823a206-95a0-4666-b464-93b9f0606d7b',
            'http.status': 200,
            'request.username': 'charles',
        }

    def test_get_access_key(self):
        response = self.req('get', '/api/v1/users/charles/keys/AKIDEXAMPLE')

        assert response.status_code == 200
        assert json.loads(response.get_data(as_text=True)) == {
            'id': 'AKIDEXAMPLE',
            'access_key_id': 'AKIDEXAMPLE',
        }

        args, kwargs = self.audit_log.call_args_list[0]
        assert args[0] == 'GetAccessKey'
        assert kwargs['extra'] == {
            'request-id': 'a823a206-95a0-4666-b464-93b9f0606d7b',
            'http.status': 200,
            'request.username': 'charles',
            'request.access_key_id': 'AKIDEXAMPLE',
        }

    def test_create_access_key(self):
        with mock.patch('tinyauth.resources.access_key.ACCESS_KEY_ID_LETTERS', new='I'):
            response = self.req('post', '/api/v1/users/charles/keys')
        d = json.loads(response.get_data(as_text=True))
        assert len(d['access_key_id']) == 20
        assert d['access_key_id'] == d['access_key_id'].upper()
        assert len(d['secret_access_key']) == 40

        response = self.req('get', '/api/v1/users/charles/keys')
        assert len(json.loads(response.get_data(as_text=True))) == 2

        args, kwargs = self.audit_log.call_args_list[0]
        assert args[0] == 'CreateAccessKey'
        assert kwargs['extra'] == {
            'request-id': 'a823a206-95a0-4666-b464-93b9f0606d7b',
            'http.status': 200,
            'request.username': 'charles',
            'response.access_key_id': 'AKIIIIIIIIIIIIIIIIII',
        }

    def test_delete_access_key(self):
        with mock.patch('tinyauth.resources.access_key.ACCESS_KEY_ID_LETTERS', new='I'):
            response = self.req('post', '/api/v1/users/charles/keys')

        response = self.req('get', '/api/v1/users/charles/keys')
        payload = json.loads(response.get_data(as_text=True))
        assert len(payload) == 2

        access_key_id = payload[-1]['access_key_id']
        response = self.req('delete', f'/api/v1/users/charles/keys/{access_key_id}')

        assert response.status_code == 201
        assert json.loads(response.get_data(as_text=True)) == {}

        response = self.req('get', '/api/v1/users/charles/keys')
        assert len(json.loads(response.get_data(as_text=True))) == 1

        args, kwargs = self.audit_log.call_args_list[2]
        assert args[0] == 'DeleteAccessKey'
        assert kwargs['extra'] == {
            'request-id': 'a823a206-95a0-4666-b464-93b9f0606d7b',
            'http.status': 201,
            'request.username': 'charles',
            'request.access_key_id': 'AKIIIIIIIIIIIIIIIIII'
        }
