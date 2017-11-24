import datetime

from flask import abort, request
from werkzeug.http import parse_authorization_header

from .identity import identify
from .identity.exceptions import IdentityError
from .models import User
from .policy import allow


def _authorize_user(user, action, resource, headers, context):
    ctx = dict(context)

    policy = {
        'Statement': []
    }

    for group in user.groups:
        for p in group.policies:
            policy['Statement'].extend(p.policy.get('Statement', []))

    for p in user.policies:
        policy['Statement'].extend(p.policy.get('Statement', []))

    if allow(policy, action, resource, ctx) != 'Allow':
        return {
            'Authorized': False,
            'ErrorCode': 'NotPermitted',
        }

    return {
        'Authorized': True,
        'Identity': user.username,
    }


def _authorize_access_key(action, resource, headers, context):
    try:
        user, mfa = identify(headers)
    except IdentityError as e:
        return e.asdict()

    context = dict(context)
    context['Mfa'] = mfa

    return _authorize_user(user, action, resource, headers, context)


def _authorize_login(action, resource, headers, context):
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

    user = User.query.filter(User.username == auth.username).first()
    if not user or not user.password:
        return {
            'Authorized': False,
            'ErrorCode': 'NoSuchKey',
        }

    if not user.is_valid_password(auth.password):
        return {
            'Authorized': False,
            'ErrorCode': 'InvalidSecretKey',
        }

    return _authorize_user(user, action, resource, headers, context)


def external_authorize_login(action, resource, headers, context):
    return _authorize_login(action, resource, headers, context)


def external_authorize(action, resource, headers, context):
    return _authorize_access_key(action, resource, headers, context)


def internal_authorize(action, resource, ctx=None):
    context = {
        'SourceIp': request.remote_addr,
        'RequestDateTime': datetime.datetime.utcnow(),
    }
    context.update(ctx or {})

    authorized = _authorize_access_key(
        'tinyauth:' + action,
        resource,
        request.headers,
        context,
    )

    if authorized['Authorized'] is not True:
        abort(401, authorized)

    return authorized
