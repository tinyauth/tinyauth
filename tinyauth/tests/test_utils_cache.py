import datetime
import unittest
import uuid
from unittest import mock

from tinyauth.utils import cache


class TestCacheDecorator(unittest.TestCase):

    def test_is_cached(self):
        expires = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

        callable = mock.Mock()
        callable.side_effect = lambda *args: (expires, uuid.uuid4())

        result1 = callable('key', 'key2')
        assert len(callable.call_args_list) == 1

        fn = cache()(callable)
        result2 = fn('key', 'key2')
        result3 = fn('key', 'key2')

        assert result1 != result2
        assert result2 == result3
        assert len(callable.call_args_list) == 2

    def test_is_not_cached(self):
        expires = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

        callable = mock.Mock()
        callable.side_effect = lambda *args: (expires, uuid.uuid4())

        fn = cache()(callable)
        result2 = fn('key', 'key3')
        result3 = fn('key', 'key2')

        assert result2 != result3
        assert len(callable.call_args_list) == 2

    def test_is_not_cached_expired(self):
        expires = datetime.datetime.utcnow() - datetime.timedelta(hours=1)

        callable = mock.Mock()
        callable.side_effect = lambda *args: (expires, uuid.uuid4())

        fn = cache()(callable)
        result2 = fn('key', 'key2')
        result3 = fn('key', 'key2')

        assert result2 != result3
        assert len(callable.call_args_list) == 2
