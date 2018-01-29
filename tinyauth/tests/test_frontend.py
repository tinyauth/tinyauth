import json
from unittest import mock

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

    def test_index_DEBUG(self):
        self.app.config['DEBUG'] = True
        response = self.client.get('/')
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'text/html; charset=utf-8'

        body = response.get_data(as_text=True).strip()
        assert '<script type="text/javascript" src="/static/js/bundle.js">' in body
        assert body.endswith('</html>')

    def test_index(self):
        assets = json.dumps({
            'main.js': 'static/js/bundle.c0ff33.js',
            'main.css': 'static/css/main.c0ff33.css',
        })

        with mock.patch('tinyauth.frontend.open', mock.mock_open(read_data=assets)):
            response = self.client.get('/')

        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'text/html; charset=utf-8'

        body = response.get_data(as_text=True).strip()
        assert '<script type="text/javascript" src="/static/js/bundle.c0ff33.js">' in body
        assert '<link href="/static/css/main.c0ff33.css" rel="stylesheet">' in body
        assert body.endswith('</html>')

    def test_login(self):
        response = self.client.get('/login')
        assert response.status_code == 302
        assert response.headers['Location'] == 'http://localhost/'

    def test_logout(self):
        assert len(self.client.cookie_jar._cookies['localhost.local']['/']) == 2

        response = self.client.get('/logout')
        assert response.status_code == 302
        assert response.headers['Location'] == 'http://localhost/login'

        assert len(self.client.cookie_jar._cookies['localhost.local']['/']) == 0

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
        response = self.client.get('/')

        assert response.status_code == 302
        assert response.headers['Location'] == 'http://localhost/login'

    def test_login_DEBUG(self):
        self.app.config['DEBUG'] = True

        response = self.client.get('/login')
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'text/html; charset=utf-8'

        body = response.get_data(as_text=True).strip()
        assert '<script type="text/javascript" src="/login/static/js/bundle.js">' in body
        assert body.endswith('</html>')

    def test_login(self):
        assets = json.dumps({
            'main.js': 'static/js/bundle.c0ff33.js',
        })

        with mock.patch('tinyauth.frontend.open', mock.mock_open(read_data=assets)):
            response = self.client.get('/login')

        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'text/html; charset=utf-8'

        body = response.get_data(as_text=True).strip()
        assert '<script type="text/javascript" src="/login/static/js/bundle.c0ff33.js">' in body
        assert body.endswith('</html>')
