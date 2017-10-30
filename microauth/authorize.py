from flask import abort, request

from .policy import allow
from .models import AccessKey


def authorize(action, resource, context=None):
    if not request.authorization:
        abort(401, 'NoSuchKey')

    auth = request.authorization

    access_key = AccessKey.query.filter(AccessKey.access_key_id==auth.username).first()
    if not access_key:
        abort(401, 'NoSuchKey')

    if access_key.secret_access_key != auth.password:
        abort(401, 'InvalidSecretKey')

    policy = {
        'Version': '2012-10-17',
        'Statement': []
    }

    for p in access_key.user.policies:
        policy['Statement'].extend(p.policy.get('Statement', []))

    if allow(policy, action, resource, context or {}) != 'Allow':
        abort(401, 'NotPermitted')

    return True
