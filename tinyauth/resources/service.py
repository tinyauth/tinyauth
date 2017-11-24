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
