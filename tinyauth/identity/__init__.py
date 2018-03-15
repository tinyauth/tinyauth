from . import basicauth, jwt
from .. import exceptions


token_identifiers = [
    jwt.parse,
    basicauth.parse,
]


def identify(region, service, headers):
    for fn in token_identifiers:
        try:
            return fn(region, service, headers)
        except exceptions.Unsigned:
            continue

    raise exceptions.Unsigned()
