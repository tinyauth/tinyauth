from werkzeug.http import parse_authorization_header

from . import exceptions
from ..models import AccessKey


def parse(headers):
    if 'Authorization' not in headers:
        raise exceptions.Unsigned()

    auth_header = headers.get('Authorization')
    if not auth_header.startswith('Basic '):
        raise exceptions.Unsigned()

    auth = parse_authorization_header(auth_header)
    if not auth:
        raise exceptions.InvalidSignature()

    access_key = AccessKey.query.filter(AccessKey.access_key_id == auth.username).first()
    if not access_key:
        raise exceptions.NoSuchKey(identity=auth.username)

    if access_key.secret_access_key != auth.password:
        raise exceptions.InvalidSignature()

    return access_key.user, False
