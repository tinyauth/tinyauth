import unittest

from tinyauth.models import AccessKey, Group, GroupPolicy, User, UserPolicy


class TestAccessKey(unittest.TestCase):

    def test_repr(self):
        access_key = AccessKey(access_key_id='ABCDEFG')
        assert str(access_key) == '<AccessKey \'ABCDEFG\'>'


class TestGroupPolicy(unittest.TestCase):

    def test_repr(self):
        group_policy = GroupPolicy(name='my-policy')
        assert str(group_policy) == '<GroupPolicy \'my-policy\'>'


class TestGroup(unittest.TestCase):

    def test_repr(self):
        group = Group(name='my-user')
        assert str(group) == '<Group \'my-user\'>'


class TestUserPolicy(unittest.TestCase):

    def test_repr(self):
        user_policy = UserPolicy(name='my-policy')
        assert str(user_policy) == '<UserPolicy \'my-policy\'>'


class TestUser(unittest.TestCase):

    def test_repr(self):
        user = User(username='my-user')
        assert str(user) == '<User \'my-user\'>'
