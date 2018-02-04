import json

from . import base


class TestCase(base.TestCase):

    def test_list_user_policies(self):
        response = self.req('get', '/api/v1/users/charles/policies')

        assert response.status_code == 200
        assert json.loads(response.get_data(as_text=True)) == [{
            'id': 'tinyauth',
            'name': 'tinyauth',
            'policy': json.dumps({
                'Version': '2012-10-17',
                'Statement': [{
                    'Action': 'tinyauth:*',
                    'Resource': 'arn:tinyauth:*',
                    'Effect': 'Allow',
                }],
            }),
        }]

        args, kwargs = self.audit_log.call_args_list[0]
        assert args[0] == 'ListUserPolicies'
        assert kwargs['extra'] == {
            'request-id': 'a823a206-95a0-4666-b464-93b9f0606d7b',
            'http.status': 200,
            'request.username': 'charles',
        }

    def test_get_user_policy(self):
        response = self.req('get', '/api/v1/users/charles/policies/tinyauth')

        assert response.status_code == 200
        assert json.loads(response.get_data(as_text=True)) == {
            'id': 'tinyauth',
            'name': 'tinyauth',
            'policy': json.dumps({
                'Version': '2012-10-17',
                'Statement': [{
                    'Action': 'tinyauth:*',
                    'Resource': 'arn:tinyauth:*',
                    'Effect': 'Allow',
                }],
            }),
        }

        args, kwargs = self.audit_log.call_args_list[0]
        assert args[0] == 'GetUserPolicy'
        assert kwargs['extra'] == {
            'request-id': 'a823a206-95a0-4666-b464-93b9f0606d7b',
            'http.status': 200,
            'request.username': 'charles',
            'request.policy': 'tinyauth',
        }

    def test_create_user_policy(self):
        response = self.req('post', '/api/v1/users/charles/policies', body={
            'name': 'example1',
            'policy': json.dumps({'Statement': []})
        })

        assert json.loads(response.get_data(as_text=True)) == {
            'id': 'example1',
            'name': 'example1',
            'policy': json.dumps({'Statement': []}),
        }

        response = self.req('get', '/api/v1/users/charles/policies')
        assert len(json.loads(response.get_data(as_text=True))) == 2

        args, kwargs = self.audit_log.call_args_list[0]
        assert args[0] == 'CreateUserPolicy'
        assert kwargs['extra'] == {
            'request-id': 'a823a206-95a0-4666-b464-93b9f0606d7b',
            'http.status': 200,
            'request.username': 'charles',
            'request.policy': 'example1',
        }

    def test_delete_user_policy(self):
        response = self.req('post', '/api/v1/users/charles/policies', body={
            'name': 'example1',
            'policy': json.dumps({'Statement': []})
        })
        assert response.status_code == 200

        response = self.req('get', '/api/v1/users/charles/policies')
        assert len(json.loads(response.get_data(as_text=True))) == 2

        response = self.req('delete', '/api/v1/users/charles/policies/example1')

        assert response.status_code == 201
        assert json.loads(response.get_data(as_text=True)) == {}

        response = self.req('get', '/api/v1/users/charles/policies')
        assert len(json.loads(response.get_data(as_text=True))) == 1

        args, kwargs = self.audit_log.call_args_list[2]
        assert args[0] == 'DeleteUserPolicy'
        assert kwargs['extra'] == {
            'request-id': 'a823a206-95a0-4666-b464-93b9f0606d7b',
            'http.status': 201,
            'request.username': 'charles',
            'request.policy': 'example1',
        }
