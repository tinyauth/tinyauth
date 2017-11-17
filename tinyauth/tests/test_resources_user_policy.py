import json

from . import base


class TestCase(base.TestCase):

    def test_list_user_policies(self):
        response = self.req('get', '/api/v1/users/1/policies')

        assert response.status_code == 200
        assert json.loads(response.get_data(as_text=True)) == [{
            'id': 1,
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

    def test_get_user_policy(self):
        response = self.req('get', '/api/v1/users/1/policies/1')

        assert response.status_code == 200
        assert json.loads(response.get_data(as_text=True)) == {
            'id': 1,
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

    def test_create_user_policy(self):
        response = self.req('post', '/api/v1/users/1/policies', body={
            'name': 'example1',
            'policy': json.dumps({'Statement': []})
        })

        assert json.loads(response.get_data(as_text=True)) == {
            'id': 2,
            'name': 'example1',
            'policy': json.dumps({'Statement': []}),
        }

        response = self.req('get', '/api/v1/users/1/policies')
        assert len(json.loads(response.get_data(as_text=True))) == 2

    def test_delete_user_policy(self):
        response = self.req('post', '/api/v1/users/1/policies', body={
            'name': 'example1',
            'policy': json.dumps({'Statement': []})
        })
        assert response.status_code == 200

        response = self.req('get', '/api/v1/users/1/policies')
        assert len(json.loads(response.get_data(as_text=True))) == 2

        response = self.req('delete', '/api/v1/users/1/policies/2')

        assert response.status_code == 201
        assert json.loads(response.get_data(as_text=True)) == {}

        response = self.req('get', '/api/v1/users/1/policies')
        assert len(json.loads(response.get_data(as_text=True))) == 1
