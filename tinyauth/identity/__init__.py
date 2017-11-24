from . import basicauth, jwt, exceptions


token_identifiers = [
    basicauth.parse,
    jwt.parse,
]


def identify(headers):
    for fn in token_identifiers:
        try:
            return fn(headers)
        except exceptions.Unsigned:
            raise
            continue

    raise exceptions.Unsigned()
