import datetime

from flask import abort, request
from werkzeug.http import parse_authorization_header

from .models import AccessKey
from .policy import allow


def _authorize(action, resource, headers, context):
    if 'Authorization' not in headers:
        return {
            'Authorized': False,
            'ErrorCode': 'NoSuchKey',
        }

    auth = parse_authorization_header(headers.get('Authorization'))
    if not auth:
        return {
            'Authorized': False,
            'ErrorCode': 'NoSuchKey',
        }

    access_key = AccessKey.query.filter(AccessKey.access_key_id == auth.username).first()
    if not access_key:
        return {
            'Authorized': False,
            'ErrorCode': 'NoSuchKey',
        }

    if access_key.secret_access_key != auth.password:
        return {
            'Authorized': False,
            'ErrorCode': 'InvalidSecretKey',
        }

    ctx = dict(context)
    ctx['Mfa'] = False

    policy = {
        'Statement': []
    }

    for p in access_key.user.policies:
        policy['Statement'].extend(p.policy.get('Statement', []))

    if allow(policy, action, resource, ctx) != 'Allow':
        return {
            'Authorized': False,
            'ErrorCode': 'NotPermitted',
        }

    return {
        'Authorized': True,
        'Identity': access_key.user.username,
    }


def external_authorize(action, resource, headers, context):
    return _authorize(action, resource, headers, context)


def internal_authorize(action, resource, ctx=None):
    context = {
        'SourceIp': request.remote_addr,
        'RequestDateTime': datetime.datetime.utcnow(),
    }
    context.update(ctx or {})

    authorized = _authorize(
        'microauth:' + action,
        resource,
        request.headers,
        context,
    )

    if authorized['Authorized'] is not True:
        abort(401, authorized)

    return authorized
