import base64
import datetime
from unittest import mock

from tinyauth.backends.proxy import Backend

from . import base


class TestBackendProxy(base.TestCase):

    @mock.patch('tinyauth.backends.proxy.requests')
    def test_get_policies(self, requests):
        self.app.config['TINYAUTH_ENDPOINT'] = 'http://localhost'
        self.app.config['TINYAUTH_ACCESS_KEY_ID'] = 'access-key'
        self.app.config['TINYAUTH_SECRET_ACCESS_KEY'] = 'secret-key'

        requests.Session.return_value.get.return_value.json.return_value = {
            'Statement': [],
        }

        backend = Backend()
        policies = backend.get_policies('region', 'service', 'username')
        assert policies == {
            'Statement': [],
        }

        requests.Session.return_value.get.assert_called_with(
            'http://localhost/api/v1/regions/region/services/service/user-policies/username',
            auth=('access-key', 'secret-key'),
            headers={'Accept': 'application/json'},
            verify=True,
        )

    @mock.patch('tinyauth.backends.proxy.requests')
    def test_get_user_key(self, requests):
        self.app.config['TINYAUTH_ENDPOINT'] = 'http://localhost'
        self.app.config['TINYAUTH_ACCESS_KEY_ID'] = 'access-key'
        self.app.config['TINYAUTH_SECRET_ACCESS_KEY'] = 'secret-key'

        requests.Session.return_value.get.return_value.json.return_value = {
            'key': base64.b64encode(b'hello').decode('utf-8'),
            'identity': 'username',
        }

        date = datetime.datetime(2016, 8, 4)

        backend = Backend()
        secret = backend.get_user_key('basic-auth', 'region', 'service', date, 'username')
        assert secret == {
            'key': b'hello',
            'identity': 'username',
        }

        requests.Session.return_value.get.assert_called_with(
            'http://localhost/api/v1/regions/region/services/service/user-signing-tokens/username/basic-auth/20160804',
            auth=('access-key', 'secret-key'),
            headers={'Accept': 'application/json'},
            verify=True,
        )

    @mock.patch('tinyauth.backends.proxy.requests')
    def test_get_access_key(self, requests):
        self.app.config['TINYAUTH_ENDPOINT'] = 'http://localhost'
        self.app.config['TINYAUTH_ACCESS_KEY_ID'] = 'access-key'
        self.app.config['TINYAUTH_SECRET_ACCESS_KEY'] = 'secret-key'

        requests.Session.return_value.get.return_value.json.return_value = {
            'key': base64.b64encode(b'hello').decode('utf-8'),
            'identity': 'username',
        }

        date = datetime.datetime(2016, 8, 4)

        backend = Backend()
        secret = backend.get_access_key('basic-auth', 'region', 'service', date, 'AKIDEXAMPLE')
        assert secret == {
            'key': b'hello',
            'identity': 'username',
        }

        requests.Session.return_value.get.assert_called_with(
            'http://localhost/api/v1/regions/region/services/service/access-key-signing-tokens/AKIDEXAMPLE/basic-auth/20160804',
            auth=('access-key', 'secret-key'),
            headers={'Accept': 'application/json'},
            verify=True,
        )
