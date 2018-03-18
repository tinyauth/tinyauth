import os
from unittest import mock

from tinyauth.app import createdevuser
from tinyauth.backends.proxy import Backend
from tinyauth.models import AccessKey, User

from .base import BaseTestCase, TestCase


class TestApp(TestCase):

    def test_create_dev_user(self):
        os.environ['FLASK_APP'] = os.path.join(os.path.dirname(__file__), '..', 'wsgi.py')
        try:
            createdevuser([])
        except SystemExit as e:
            assert e.code == 0
        else:
            raise RuntimeError('Did not raise SystemExit')

        assert User.query.filter(User.username == 'root').count() == 1
        assert AccessKey.query.filter(AccessKey.access_key_id == 'gatekeeper').count() == 1


class TestProxyMode(BaseTestCase):

    def setUp(self):
        with mock.patch.dict(os.environ, {'TINYAUTH_AUTH_MODE': 'proxy'}):
            super().setUp()

    def test_configure_worked(self):
        assert isinstance(self.app.auth_backend, Backend)
