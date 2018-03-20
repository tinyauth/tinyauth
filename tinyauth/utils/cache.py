import collections
import datetime
import functools


class Cache(collections.OrderedDict):

    def __init__(self, max_size=1000):
        super().__init__()
        self.max_size = max_size
        self.cache = {}

    def set(self, key, value, expiry):
        for i in range(max(0, len(self) - self.max_size)):
            self.popitem(last=False)
        self.cache[key] = (value, expiry)

    def get(self, key):
        value, expiry = self.cache[key]
        expired = expiry <= datetime.datetime.utcnow()
        return expired, value


def cache(**kwargs):
    cache = Cache(**kwargs)

    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            try:
                expired, cache_value = cache.get(args)
                should_raise = False
            except KeyError:
                cache_value = None
                expired = True
                should_raise = True

            if not expired:
                return cache_value

            try:
                expires, value = f(*args, **kwargs)
            except Exception as e:
                if not should_raise:
                    return cache_value
                raise

            cache.set(args, value, expires)
            return value

        return wrapper

    return decorator
