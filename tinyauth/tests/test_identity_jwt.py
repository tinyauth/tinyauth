import base64
import json

from tinyauth.app import db
from tinyauth.models import UserPolicy

from . import base


class TestCaseIdentityJWT(base.TestCase):

    def setUp(self):
        super().setUp()

        policy = UserPolicy(name='myserver', user=self.user, policy={
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'myservice:*',
                'Resource': '*',
                'Effect': 'Allow',
            }]
        })
        db.session.add(policy)

        db.session.commit()

        response = self.client.post(
            '/api/v1/services/myservice/get-token-for-login',
            data=json.dumps({
                'username': 'charles',
                'password': 'mrfluffy',
                'csrf-strategy': 'header-token',
            }),
            headers={
                'Authorization': 'Basic {}'.format(
                    base64.b64encode(b'AKIDEXAMPLE:password').decode('utf-8')
                )
            },
            content_type='application/json',
        )
        assert response.status_code == 200

        payload = json.loads(response.get_data(as_text=True))
        self.token = payload['token']
        self.csrf = payload['csrf']

    def test_csrf_failure(self):
        self.client.set_cookie('localhost', 'tinysess', self.token)

        response = self.client.get(
            '/api/v1/users'
        )

        assert response.status_code == 401
        assert json.loads(response.get_data(as_text=True)) == {
            'errors': {'authorization': 'CsrfError'}
        }

    def test_authorize_service(self):
        self.client.set_cookie('localhost', 'tinysess', self.token)

        response = self.client.get(
            '/api/v1/users',
            headers={
                'X-CSRF-Token': self.csrf,
            }
        )

        assert response.status_code == 200
        assert json.loads(response.get_data(as_text=True)) == [{
            'groups': [],
            'id': 1,
            'username': 'charles',
        }]
