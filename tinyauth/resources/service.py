from flask import Blueprint, jsonify
from flask_restful import reqparse
from werkzeug.datastructures import Headers

from ..authorize import (
    external_authorize,
    external_authorize_login,
    internal_authorize,
)

service_blueprint = Blueprint('service', __name__)

authorize_parser = reqparse.RequestParser()
authorize_parser.add_argument('action', type=str, location='json', required=True)
authorize_parser.add_argument('resource', type=str, location='json', required=True)
authorize_parser.add_argument('headers', type=list, location='json', required=True)
authorize_parser.add_argument('context', type=dict, location='json', required=True)

batch_authorize_parser = reqparse.RequestParser()
batch_authorize_parser.add_argument('steps', type=list, location='json', required=True)
batch_authorize_parser.add_argument('headers', type=list, location='json', required=True)
batch_authorize_parser.add_argument('context', type=dict, location='json', required=True)



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

    return jsonify(result)


@service_blueprint.route('/api/v1/batch-authorize-by-token', methods=['POST'])
def batch_service_authorize():
    internal_authorize('BatchAuthorizeByToken', f'arn:tinyauth:')

    args = batch_authorize_parser.parse_args()

    result = {
       'Steps': [],
       'Authorized': True,
       'Identity': 'guest',
    }

    # FIXME: Refactor this to only need to verify identity once and reuse the extracted policies for multiple verifications
    for step in args['steps']:
        step_result = external_authorize(
            action=step['action'],
            resource=step['resource'],
            headers=Headers(args['headers']),
            context=args['context'],
        )

        result['Steps'].append(step_result['Authorized'])

        if not step_result['Authorized']:
            result['Authorized'] = False

    if result['Authorized']:
        result['Identity'] = step_result['Identity']

    return jsonify(result)
