import datetime
import hmac

from flask import current_app
from werkzeug.http import parse_authorization_header

from .. import exceptions
from ..subkey import make_basic_auth_key


def parse(region, service, headers):
    if 'Authorization' not in headers:
        raise exceptions.Unsigned()

    auth_header = headers.get('Authorization')
    if not auth_header.startswith('Basic '):
        raise exceptions.Unsigned()

    auth = parse_authorization_header(auth_header)
    if not auth:
        raise exceptions.InvalidSignature()

    date = datetime.datetime.utcnow()

    key = current_app.auth_backend.get_access_key(
        'basic-auth',
        region,
        service,
        date.date(),
        auth.username,
    )

    secret = make_basic_auth_key(
        region,
        service,
        date,
        auth.username,
        auth.password,
    )

    if not hmac.compare_digest(key['key'], secret):
        raise exceptions.InvalidSignature()

    return key['identity'], False
