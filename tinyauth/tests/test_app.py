import os

from tinyauth.app import createdevuser
from tinyauth.models import AccessKey, User

from .base import TestCase


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
