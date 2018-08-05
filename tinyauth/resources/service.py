import base64
import collections
import datetime
import itertools
import json
import logging
import uuid

import jwt
from flask import (
    Blueprint,
    abort,
    current_app,
    jsonify,
    make_response,
    request,
    session,
)
from werkzeug.datastructures import Headers

from .. import const
from ..audit import audit_request, format_headers_for_audit_log
from ..authorize import (
    external_authorize,
    external_authorize_login,
    format_arn,
    get_arn_base,
    internal_authorize,
)
from ..exceptions import AuthenticationError, NoSuchKey
from ..models import AccessKey, User, WebAuthnCredential, db
from ..reqparse import RequestParser

service_blueprint = Blueprint('service', __name__)

authorize_parser = RequestParser()
authorize_parser.add_argument('region', type=str, location='json', required=False)
authorize_parser.add_argument('action', type=str, location='json', required=True)
authorize_parser.add_argument('resource', type=str, location='json', required=True)
authorize_parser.add_argument('headers', type=list, location='json', required=True)
authorize_parser.add_argument('context', type=dict, location='json', required=True)

batch_authorize_parser = RequestParser()
batch_authorize_parser.add_argument('region', type=str, location='json', required=False)
batch_authorize_parser.add_argument('permit', type=dict, location='json', required=True)
batch_authorize_parser.add_argument('headers', type=list, location='json', required=True)
batch_authorize_parser.add_argument('context', type=dict, location='json', required=True)

logger = logging.getLogger("tinyauth.audit")


@service_blueprint.route('/api/v1/authorize-login', methods=['POST'])
@audit_request('AuthorizeByLogin')
def service_authorize_login(audit_ctx):
    internal_authorize('Authorize', get_arn_base())

    args = authorize_parser.parse_args()

    audit_ctx['request.region'] = args['region'] or const.REGION_GLOBAL
    audit_ctx['request.actions'] = [args['action']]
    audit_ctx['request.resources'] = [args['resource']]
    audit_ctx['request.permit'] = json.dumps({args['action']: [args['resource']]}, indent=4, separators=(',', ': '))
    audit_ctx['request.headers'] = format_headers_for_audit_log(args['headers'])
    audit_ctx['request.context'] = args['context']

    result = external_authorize_login(
        args['region'] or const.REGION_GLOBAL,
        args['action'].split(':', 1)[0] if ':' in args['action'] else '',
        action=args['action'],
        resource=args['resource'],
        headers=Headers(args['headers']),
        context=args['context'],
    )

    audit_ctx['response.authorized'] = result['Authorized']
    if 'Identity' in result:
        audit_ctx['response.identity'] = result['Identity']

    return jsonify(result)


@service_blueprint.route('/api/v1/authorize', methods=['POST'])
@audit_request('AuthorizeByToken')
def service_authorize(audit_ctx):
    audit_ctx['request.legacy'] = True

    internal_authorize('Authorize', get_arn_base())

    args = authorize_parser.parse_args()

    audit_ctx['request.region'] = args['region'] or const.REGION_GLOBAL
    audit_ctx['request.actions'] = [args['action']]
    audit_ctx['request.resources'] = [args['resource']]
    audit_ctx['request.permit'] = json.dumps({args['action']: [args['resource']]}, indent=4, separators=(',', ': '))
    audit_ctx['request.headers'] = format_headers_for_audit_log(args['headers'])
    audit_ctx['request.context'] = args['context']

    result = external_authorize(
        args['region'] or const.REGION_GLOBAL,
        args['action'].split(':', 1)[0] if ':' in args['action'] else '',
        action=args['action'],
        resource=args['resource'],
        headers=Headers(args['headers']),
        context=args['context'],
    )

    audit_ctx['response.authorized'] = result['Authorized']
    if 'Identity' in result:
        audit_ctx['response.identity'] = result['Identity']

    return jsonify(result)


@service_blueprint.route('/api/v1/services/<service>/get-token-for-login', methods=['POST'])
@audit_request('GetTokenForLogin')
def get_token_for_login(audit_ctx, service):
    audit_ctx['request.service'] = service
    internal_authorize('GetTokenForLogin', format_arn('services', service))

    user_parser = RequestParser()
    user_parser.add_argument('username', type=str, location='json', required=True)
    user_parser.add_argument('password', type=str, location='json', required=True)
    user_parser.add_argument('csrf-strategy', type=str, location='json', required=True)
    user_parser.add_argument('region', type=str, location='json', required=False)
    req = user_parser.parse_args()

    audit_ctx['request.username'] = req['username']
    audit_ctx['request.csrf-strategy'] = req['csrf-strategy']

    errors = {
        'authentication': 'Invalid credentials',
    }
    response = jsonify(errors=errors)
    response.status_code = 401

    if req['csrf-strategy'] not in ('header-token', 'cookie', 'none'):
        raise AuthenticationError(description=errors, response=response)

    user = User.query.filter(User.username == req['username']).first()
    if not user or not user.password:
        raise AuthenticationError(description=errors, response=response)

    if not user.is_valid_password(req['password']):
        raise AuthenticationError(description=errors, response=response)

    iat = datetime.datetime.utcnow()
    expires = iat + datetime.timedelta(hours=8)

    token_contents = {
        'user': user.username,
        'mfa': False,
        'exp': expires,
        'iat': iat,
    }

    if req['csrf-strategy'] == 'header-token':
        token_contents['csrf-token'] = str(uuid.uuid4())

    secret = current_app.auth_backend.get_user_key(
        'jwt',
        req['region'] or const.REGION_GLOBAL,
        service,
        iat.date(),
        user.username,
    )

    jwt_token = jwt.encode(
        token_contents,
        secret['key'],
        algorithm='HS256',
    )

    response = {'token': jwt_token.decode('utf-8')}
    if 'csrf-token' in token_contents:
        response['csrf'] = token_contents['csrf-token']

    return jsonify(response)


@service_blueprint.route('/api/v1/services/<service>/authorize-by-token', methods=['POST'])
@audit_request('AuthorizeByToken')
def batch_service_authorize(audit_ctx, service):
    audit_ctx['request.service'] = service
    audit_ctx['response.authorized'] = False

    internal_authorize('BatchAuthorizeByToken', format_arn('services', service))

    args = batch_authorize_parser.parse_args()

    audit_ctx.update({
        'request.region': args['region'] or const.REGION_GLOBAL,
        'request.actions': [':'.join((service, action)) for action in args['permit'].keys()],
        'request.resources': list(itertools.chain(*args['permit'].values())),
        'request.permit': json.dumps(args['permit'], indent=4, separators=(',', ': ')),
        'request.headers': format_headers_for_audit_log(args['headers']),
        'request.context': args['context'],
    })

    result = {
       'Permitted': collections.defaultdict(list),
       'NotPermitted': collections.defaultdict(list),
       'Authorized': False,
    }

    # FIXME: Refactor this to only need to verify identity once and reuse the extracted policies for multiple verifications
    for action, resources in args['permit'].items():
        for resource in resources:
            step_result = external_authorize(
                args['region'] or const.REGION_GLOBAL,
                service,
                action=':'.join((service, action)),
                resource=resource,
                headers=Headers(args['headers']),
                context=args['context'],
            )

            grant_set = result['Permitted' if step_result['Authorized'] else 'NotPermitted']
            grant_set[action].append(resource)

            if not step_result['Authorized']:
                result['ErrorCode'] = step_result['ErrorCode']

    audit_ctx['response.permitted'] = json.dumps(dict(result['Permitted']), indent=4, separators=(',', ': '))
    audit_ctx['response.not-permitted'] = json.dumps(dict(result['NotPermitted']), indent=4, separators=(',', ': '))

    if len(result['NotPermitted']) == 0 and len(result['Permitted']) > 0:
        audit_ctx['response.authorized'] = result['Authorized'] = True
        audit_ctx['response.identity'] = result['Identity'] = step_result['Identity']

    return jsonify(result)


@service_blueprint.route('/api/v1/regions/<region>/services/<service>/user-signing-tokens/<user>/<protocol>/<date>', methods=['GET'])
@audit_request('GetServiceUserSigningToken')
def get_service_user_signing_token(audit_ctx, region, service, user, protocol, date):
    audit_ctx['request.region'] = region
    audit_ctx['request.service'] = service
    audit_ctx['request.protocol'] = protocol
    audit_ctx['request.user'] = user
    audit_ctx['request.date'] = date

    internal_authorize('GetServiceUserSigningToken', format_arn('services', service))

    try:
        secret = current_app.auth_backend.get_user_key(
            protocol,
            region,
            service,
            datetime.datetime.strptime(date, '%Y%m%d').date(),
            user,
        )
    except NoSuchKey:
        abort(make_response(jsonify(message='No such key'), 404))

    response = jsonify({
        'key': base64.b64encode(secret['key']).decode('utf-8'),
        'identity': secret['identity'],
    })

    expiry = 60 * 60 * 24 * 3
    expire_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=expiry)
    response.headers['Expires'] = expire_time.strftime("%a, %d %b %Y %H:%M:%S GMT")
    response.headers['Cache-Control'] = f'max-age={expiry}'

    return response


@service_blueprint.route('/api/v1/regions/<region>/services/<service>/access-key-signing-tokens/<access_key>/<protocol>/<date>', methods=['GET'])
@audit_request('GetServiceAccessKeySigningToken')
def get_service_accessKey_signing_token(audit_ctx, region, service, access_key, protocol, date):
    audit_ctx['request.region'] = region
    audit_ctx['request.service'] = service
    audit_ctx['request.protocol'] = protocol
    audit_ctx['request.access-key'] = access_key
    audit_ctx['request.date'] = date

    internal_authorize('GetServiceAccessKeySigningToken', format_arn('services', service))

    try:
        secret = current_app.auth_backend.get_access_key(
            protocol,
            region,
            service,
            datetime.datetime.strptime(date, '%Y%m%d'),
            access_key,
        )
    except NoSuchKey:
        abort(make_response(jsonify(message='No such key'), 404))

    response = jsonify({
        'key': base64.b64encode(secret['key']).decode('utf-8'),
        'identity': secret['identity'],
    })

    expiry = 60 * 60 * 24 * 3
    expire_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=expiry)
    response.headers['Expires'] = expire_time.strftime("%a, %d %b %Y %H:%M:%S GMT")
    response.headers['Cache-Control'] = f'max-age={expiry}'

    return response


@service_blueprint.route('/api/v1/regions/<region>/services/<service>/user-policies/<user>', methods=['GET'])
@audit_request('GetServiceUserPolicies')
def get_service_user_policies(audit_ctx, region, service, user):
    audit_ctx['request.region'] = region
    audit_ctx['request.service'] = service
    audit_ctx['request.user'] = user

    internal_authorize('GetServiceUserPolicies', format_arn('services', service))

    # FIXME: Return a filtered subset of the policies
    try:
        policies = current_app.auth_backend.get_policies(region, service, user)
    except NoSuchKey:
        abort(make_response(jsonify(message='No such key'), 404))

    response = jsonify(policies)

    expiry = 60
    expire_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=expiry)
    response.headers['Expires'] = expire_time.strftime("%a, %d %b %Y %H:%M:%S GMT")
    response.headers['Cache-Control'] = f'max-age={expiry}'

    return response


@service_blueprint.route('/api/v1/regions/<region>/services/<service>/begin-challenge', methods=['POST'])
@audit_request('FidoChallenge')
def authenticate_begin(audit_ctx, region, service):
    access_key = AccessKey.query.filter_by(access_key_id=request.get_json()['access_key_id']).first()
    if not access_key:
        return make_response(jsonify({'fail': 'Credential does not exist.'}), 401)

    challenge = 'HARD CODED'

    session['challenge'] = challenge

    webauthn_user = webauthn.WebAuthnUser(
        access_key.user.ukey,
        access_key.user.username,
        access_key.user.display_name,
        access_key.user.icon_url,
        access_key.user.credential_id,
        access_key.user.pub_key,
        access_key.user.sign_count,
        "https://localhost",
    )

    webauthn_assertion_options = webauthn.WebAuthnAssertionOptions(
        webauthn_user,
        challenge,
    )

    return jsonify(webauthn_assertion_options.assertion_dict)


@service_blueprint.route('/api/v1/regions/<region>/services/<service>/complete-challenge', methods=['POST'])
@audit_request('FidoChallenge')
def authenticate_complete(audit_ctx, region, service):
    challenge = session.get('challenge')
    assertion_response = request.form
    credential_id = assertion_response.get('id')

    reg = WebAuthnCredential.query.filter_by(credential_id=credential_id).first()
    if not reg:
        return make_response(jsonify({'fail': 'Credential does not exist.'}), 401)

    webauthn_user = webauthn.WebAuthnUser(
        reg.user.ukey,
        reg.user.username,
        reg.user.display_name,
        reg.user.icon_url,
        reg.credential_id,
        reg.pub_key,
        reg.sign_count,
        "https://localhost",
    )

    webauthn_assertion_response = webauthn.WebAuthnAssertionResponse(
        webauthn_user,
        assertion_response,
        challenge,
        'https://localhost',
        uv_required=False
    )

    try:
        sign_count = webauthn_assertion_response.verify()
    except Exception as e:
        return jsonify({'fail': 'Assertion failed. Error: {}'.format(e)})

    # Update counter.
    reg.sign_count = sign_count
    db.session.add(reg)
    db.session.commit()

    iat = datetime.datetime.utcnow()
    expires = iat + datetime.timedelta(hours=8)

    token_contents = {
        'user': reg.user.username,
        'mfa': True,
        'exp': expires,
        'iat': iat,
    }

    # if req['csrf-strategy'] == 'header-token':
    #    token_contents['csrf-token'] = str(uuid.uuid4())

    secret = current_app.auth_backend.get_user_key(
        'jwt',
        region or const.REGION_GLOBAL,
        service,
        iat.date(),
        reg.user.username,
    )

    jwt_token = jwt.encode(
        token_contents,
        secret['key'],
        algorithm='HS256',
    )

    response = {'token': jwt_token.decode('utf-8')}
    if 'csrf-token' in token_contents:
        response['csrf'] = token_contents['csrf-token']

    return jsonify(response)
