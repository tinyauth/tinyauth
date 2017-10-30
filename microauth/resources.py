from flask import jsonify, request
from flask_restful import Resource, abort, fields, marshal, reqparse
from werkzeug.datastructures import Headers

from microauth.app import api, app, db
from microauth.authorize import external_authorize, internal_authorize
from microauth.models import User
from microauth.simplerest import build_response_for_request

user_fields = {
    'id': fields.Integer,
    'username': fields.String,
}

user_parser = reqparse.RequestParser()
user_parser.add_argument('username', type=str, location='json', required=True)


class UserResource(Resource):

    def _get_or_404(self, user_id):
        user = User.query.filter(User.id == user_id).first()
        if not user:
            abort(404, message=f'user {user_id} does not exist')
        return user

    def get(self, user_id):
        internal_authorize('GetUser', f'arn:microauth:users/{user_id}')

        user = self._get_or_404(user_id)
        return jsonify(marshal(user, user_fields))

    def put(self, user_id):
        internal_authorize('UpdateUser', f'arn:microauth:users/{user_id}')

        args = user_parser.parse_args()

        user = self._get_or_404(user_id)
        user.name = args['username']
        db.session.add(user)

        db.session.commit()

        return jsonify(marshal(user, user_fields))

    def delete(self, user_id):
        internal_authorize('DeleteUser', f'arn:microauth:users/{user_id}')

        user = self._get_or_404(user_id)
        db.session.delete(user)

        return '{}', 201


class UsersResource(Resource):

    def get(self):
        return build_response_for_request(User, request, user_fields)

    def post(self):
        args = user_parser.parse_args()

        internal_authorize('CreateUser', f'arn:microauth:users/args["username"]')

        user = User(
            username=args['username'],
        )

        db.session.add(user)
        db.session.commit()

        return jsonify(marshal(user, user_fields))


api.add_resource(UsersResource, '/users')
api.add_resource(UserResource, '/users/<key_id>')


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
