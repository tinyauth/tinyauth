import hashlib
import hmac


def sign(key, msg):
    return hmac.new(key, msg, hashlib.sha256).digest()


def _make_scoped_subkey(region, service, date, identity, key, protocol):
    key = key.encode('utf-8')

    prefix = b'TINYAUTH'
    if protocol == 'aws-sig4':
        prefix = b'AWS4'

    request_type = {
        'jwt': b'jwt_request',
        'basic-auth': b'basic_auth_request',
        'aws-sig4': b'aws4_request',
    }

    # In the current impl there is a single secret for all JWT tokens
    # Make it per-user by mixing in username..
    identity = identity.encode('utf-8')
    if protocol not in ('aws-sig4', ):
        key = sign(key, identity)

    date = date.strftime('%Y%m%d').encode('utf-8')
    key = sign(prefix + key, date)

    region = region.encode('utf-8')
    key = sign(key, region)

    service = service.encode('utf-8')
    key = sign(key, service)

    request_type = request_type[protocol]
    key = sign(key, request_type)

    return key


def make_basic_auth_key(region, service, date, identity, key):
    return _make_scoped_subkey(region, service, date, identity, key, 'basic-auth')


def make_jwt_key(region, service, date, identity, key):
    return _make_scoped_subkey(region, service, date, identity, key, 'jwt')


def make_aws_sig4_key(region, service, date, identity, key):
    return _make_scoped_subkey(region, service, date, identity, key, 'aws-sig4')
