import json

from . import base


class TestFrontendJWT(base.TestCase):

    def setUp(self):
        super().setUp()

        response = self.client.post(
            '/login',
            data=json.dumps({
                'username': 'charles',
                'password': 'mrfluffy',
            }),
            content_type='application/json',
        )
        assert response.status_code == 200

        assert {} == json.loads(response.get_data(as_text=True))

    def test_use_api_with_token(self):
        response = self.client.get(
            '/api/v1/users',
            headers={
                'X-CSRF-Token': self.client.cookie_jar._cookies['localhost.local']['/']['tinycsrf'].value,
            }
        )

        assert response.status_code == 200
        assert json.loads(response.get_data(as_text=True)) == [{
            'groups': [],
            'id': 1,
            'username': 'charles',
        }, {
            'groups': [],
            'id': 2,
            'username': 'freddy',
        }]
