import unittest

from tinyauth.models import User


class TestModel(unittest.TestCase):

    def test_user(self):
        user = User(username='my-user')
        assert isinstance(user.username, str)
