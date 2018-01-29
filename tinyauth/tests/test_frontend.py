import json

from . import base


class TestLoggedInUI(base.TestCase):

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

    def test_index(self):
        self.app.config['DEBUG'] = True
        response = self.client.get('/')
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'text/html; charset=utf-8'
        assert response.get_data(as_text=True).strip().endswith('</html>')

    def test_login(self):
        self.app.config['DEBUG'] = True
        response = self.client.get('/login')
        assert response.status_code == 302
        assert response.headers['Location'] == 'http://localhost/'

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


class TestLoggedOutUI(base.TestCase):

    def test_index(self):
        self.app.config['DEBUG'] = True

        response = self.client.get('/')

        assert response.status_code == 302
        assert response.headers['Location'] == 'http://localhost/login'

    def test_login(self):
        self.app.config['DEBUG'] = True

        response = self.client.get('/login')
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'text/html; charset=utf-8'
        assert response.get_data(as_text=True).strip().endswith('</html>')
