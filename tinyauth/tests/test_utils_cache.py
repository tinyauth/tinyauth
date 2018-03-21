import datetime
import unittest
import uuid
from unittest import mock

from tinyauth.utils.cache import cache


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

    def test_serve_stale_on_error(self):
        expires = datetime.datetime.utcnow() - datetime.timedelta(hours=1)

        callable = mock.Mock()
        fn = cache()(callable)

        callable.side_effect = lambda *args: (expires, uuid.uuid4())
        result2 = fn('key', 'key2')

        callable.side_effect = RuntimeError('Temporary error')
        result3 = fn('key', 'key2')

        assert result2 == result3
        assert len(callable.call_args_list) == 2

    def test_error_on_error_if_no_cache(self):
        callable = mock.Mock()
        callable.side_effect = RuntimeError('Temporary error')
        fn = cache()(callable)

        self.assertRaises(RuntimeError, fn, 'key', 'key2')
        assert len(callable.call_args_list) == 1

        # Test that a 2nd call does hit the server
        self.assertRaises(RuntimeError, fn, 'key', 'key2')
        assert len(callable.call_args_list) == 2

    def test_is_not_cached_lru(self):
        expires = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

        callable = mock.Mock()
        callable.side_effect = lambda *args: (expires, uuid.uuid4())

        fn = cache(max_size=1)(callable)
        result2 = fn('key', 'key2')
        result3 = fn('key', 'key3')
        result4 = fn('key', 'key3')
        result5 = fn('key', 'key2')

        assert result2 != result3
        assert result2 != result5
        assert result3 == result4
        assert result3 != result5

        assert len(callable.call_args_list) == 3
