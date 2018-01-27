import collections
import datetime
import json
import logging
import uuid

import jwt
from flask import Blueprint, Response, jsonify
from werkzeug.datastructures import Headers

from ..audit import audit_request, format_headers_for_audit_log
from ..authorize import (
    external_authorize,
    external_authorize_login,
    internal_authorize,
)
from ..models import User
from ..reqparse import RequestParser

service_blueprint = Blueprint('service', __name__)

authorize_parser = RequestParser()
authorize_parser.add_argument('action', type=str, location='json', required=True)
authorize_parser.add_argument('resource', type=str, location='json', required=True)
authorize_parser.add_argument('headers', type=list, location='json', required=True)
authorize_parser.add_argument('context', type=dict, location='json', required=True)

batch_authorize_parser = RequestParser()
batch_authorize_parser.add_argument('permit', type=dict, location='json', required=True)
batch_authorize_parser.add_argument('headers', type=list, location='json', required=True)
batch_authorize_parser.add_argument('context', type=dict, location='json', required=True)

logger = logging.getLogger("tinyauth.audit")


@service_blueprint.route('/api/v1/authorize-login', methods=['POST'])
def service_authorize_login():
    internal_authorize('Authorize', f'arn:tinyauth:')

    args = authorize_parser.parse_args()

    result = external_authorize_login(
        action=args['action'],
        resource=args['resource'],
        headers=Headers(args['headers']),
        context=args['context'],
    )

    logger.info("authorize-by-login", extra={
        'request.permit': args['action'],
        'request.headers': format_headers_for_audit_log(args['headers']),
        'request.context': args['context'],
        'response': result,
    })

    return jsonify(result)


@service_blueprint.route('/api/v1/authorize', methods=['POST'])
def service_authorize():
    internal_authorize('Authorize', f'arn:tinyauth:')

    args = authorize_parser.parse_args()

    result = external_authorize(
        action=args['action'],
        resource=args['resource'],
        headers=Headers(args['headers']),
        context=args['context'],
    )

    logger.info("authorize-by-token", extra={
        'request.legacy': True,
        'request.permit': args['action'],
        'request.headers': [': '.join((k, v)) for (k, v) in args['headers']],
        'request.context': args['context'],
        'response': result,
    })

    return jsonify(result)


@service_blueprint.route('/api/v1/services/<service>/get-token-for-login', methods=['POST'])
def get_token_for_login(service):
    internal_authorize('GetTokenForLogin', f'arn:tinyauth:')

    user_parser = RequestParser()
    user_parser.add_argument('username', type=str, location='json', required=True)
    user_parser.add_argument('password', type=str, location='json', required=True)
    user_parser.add_argument('csrf-strategy', type=str, location='json', required=True)
    req = user_parser.parse_args()

    if req['csrf-strategy'] not in ('header-token', 'cookie', 'none'):
        return Response('', 401)

    user = User.query.filter(User.username == req['username']).first()
    if not user or not user.password:
        return Response(json.dumps({'message': 'Invalid credentials'}), 401)

    if not user.is_valid_password(req['password']):
        return Response(json.dumps({'message': 'Invalid credentials'}), 401)

    expires = datetime.datetime.utcnow() + datetime.timedelta(hours=8)

    token_contents = {
        'user': user.id,
        'mfa': False,
        'exp': expires,
        'iat': datetime.datetime.utcnow(),
    }

    if req['csrf-strategy'] == 'header-token':
        token_contents['csrf-token'] = str(uuid.uuid4())

    jwt_token = jwt.encode(token_contents, 'secret', algorithm='HS256')

    response = {'token': jwt_token.decode('utf-8')}
    if 'csrf-token' in token_contents:
        response['csrf'] = token_contents['csrf-token']

    logger.info("get-token-for-login", extra={
        'request.username': req['username'],
        'request.csrf-strategy': req['csrf-strategy'],
        'result.error-code': 'ok',
    })

    return jsonify(response)


@service_blueprint.route('/api/v1/services/<service>/authorize-by-token', methods=['POST'])
@audit_request('authorize-by-token')
def batch_service_authorize(audit_ctx, service):
    audit_ctx['request.service'] = service
    audit_ctx['response.authorized'] = False

    internal_authorize('BatchAuthorizeByToken', f'arn:tinyauth:')

    args = batch_authorize_parser.parse_args()

    audit_ctx.update({
        'request.permit': args['permit'],
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
                action=':'.join((service, action)),
                resource=resource,
                headers=Headers(args['headers']),
                context=args['context'],
            )

            grant_set = result['Permitted' if step_result['Authorized'] else 'NotPermitted']
            grant_set[action].append(resource)

            if not step_result['Authorized']:
                result['ErrorCode'] = step_result['ErrorCode']

    audit_ctx['response.permitted'] = dict(result['Permitted'])
    audit_ctx['response.not-permitted'] = dict(result['NotPermitted'])

    if len(result['NotPermitted']) == 0 and len(result['Permitted']) > 0:
        audit_ctx['response.authorized'] = result['Authorized'] = True
        audit_ctx['response.identity'] = result['Identity'] = step_result['Identity']

    return jsonify(result)
