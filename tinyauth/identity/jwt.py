import datetime

import jwt
from flask import current_app
from werkzeug.http import parse_cookie

from .. import exceptions


def parse_session(region, service, headers):
    cookies = {}
    for cookie in headers.getlist('Cookie'):
        cookies.update(parse_cookie(cookie))

    if 'tinysess' not in cookies:
        raise exceptions.Unsigned()

    unverified = jwt.decode(cookies['tinysess'], '', verify=False)

    secret = current_app.auth_backend.get_user_key(
        'jwt',
        region,
        service,
        datetime.datetime.utcfromtimestamp(unverified['iat']).date(),
        unverified.get('user', 'unknown'),
    )

    try:
        token = jwt.decode(cookies['tinysess'], secret['key'])
    except Exception as e:
        raise exceptions.InvalidSignature(identity=unverified.get('user', 'unknown'))

    if 'csrf-token' in token:
        if headers.get('X-CSRF-Token') != token['csrf-token']:
            raise exceptions.CsrfError(identity=token.get('user', 'unknown'))

    return token['user'], token['mfa']


def parse(region, service, headers):
    # FIXME: Support JWT tokens passed in Authorization header too
    if 'Cookie' in headers:
        return parse_session(region, service, headers)

    raise exceptions.Unsigned()
