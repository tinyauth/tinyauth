import jwt
from werkzeug.http import parse_cookie

from . import exceptions
from ..models import User


def parse_session(headers):
    cookies = {}
    for cookie in headers.getlist('Cookie'):
        cookies.update(parse_cookie(cookie))

    if 'tinysess' not in cookies:
        raise exceptions.Unsigned()

    try:
        token = jwt.decode(cookies['tinysess'], 'secret')
    except:
        token = jwt.decode(cookies['tinysess'], 'secret', verify=False)
        raise exceptions.InvalidSignature(identity=token.get('user', 'unknown'))

    if 'csrf-token' in token:
        if headers.get('X-CSRF-Token') != token['csrf-token']:
            raise exceptions.CsrfError(identity=token.get('user', 'unknown'))

    user = User.query.filter(User.id == token['user']).first()

    return user, token['mfa']


def parse(headers):
    # FIXME: Support JWT tokens passed in Authorization header too
    if 'Cookie' in headers:
        return parse_session(headers)

    raise exceptions.Unsigned()
