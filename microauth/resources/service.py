from flask import jsonify, request
from flask_restful import Resource, abort, fields, marshal, reqparse
from werkzeug.datastructures import Headers

from ..app import app
from ..authorize import external_authorize, internal_authorize

authorize_parser = reqparse.RequestParser()
authorize_parser.add_argument('action', type=str, location='json', required=True)
authorize_parser.add_argument('resource', type=str, location='json', required=True)
authorize_parser.add_argument('headers', type=list, location='json', required=True)
authorize_parser.add_argument('context', type=dict, location='json', required=True)


@app.route('/api/v1/authorize', methods=['POST'])
def service_authorize():
    internal_authorize('Authorize', f'arn:microauth:')

    args = authorize_parser.parse_args()

    result = external_authorize(
        action=args['action'],
        resource=args['resource'],
        headers=Headers(args['headers']),
        context=args['context'],
    )

    return jsonify(result)
