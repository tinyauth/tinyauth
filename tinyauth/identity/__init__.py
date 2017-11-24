from . import basicauth, jwt, exceptions


token_identifiers = [
    jwt.parse,
    basicauth.parse,
]


def identify(headers):
    for fn in token_identifiers:
        try:
            return fn(headers)
        except exceptions.Unsigned:
            continue

    raise exceptions.Unsigned()
