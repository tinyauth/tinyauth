from flask import Blueprint, jsonify, make_response, request
from flask_restful import Api, Resource, abort, fields, marshal, reqparse

from tinyauth.app import db
from tinyauth.authorize import internal_authorize
from tinyauth.models import User
from tinyauth.simplerest import build_response_for_request

user_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'groups': fields.List(fields.String(attribute='id')),
}

user_parser = reqparse.RequestParser()
user_parser.add_argument('username', type=str, location='json', required=True)

user_blueprint = Blueprint('user', __name__)


class UserResource(Resource):

    def _get_or_404(self, user_id):
        user = User.query.filter(User.id == user_id).first()
        if not user:
            abort(404, message=f'user {user_id} does not exist')
        return user

    def get(self, user_id):
        internal_authorize('GetUser', f'arn:tinyauth:users/{user_id}')

        user = self._get_or_404(user_id)
        return jsonify(marshal(user, user_fields))

    def put(self, user_id):
        internal_authorize('UpdateUser', f'arn:tinyauth:users/{user_id}')

        args = user_parser.parse_args()

        user = self._get_or_404(user_id)
        user.name = args['username']
        db.session.add(user)

        db.session.commit()

        return jsonify(marshal(user, user_fields))

    def delete(self, user_id):
        internal_authorize('DeleteUser', f'arn:tinyauth:users/{user_id}')

        user = self._get_or_404(user_id)
        db.session.delete(user)

        return make_response(jsonify({}), 201, [])


class UsersResource(Resource):

    def get(self):
        internal_authorize('ListUsers', f'arn:tinyauth:users/')

        return build_response_for_request(User, request, user_fields)

    def post(self):
        args = user_parser.parse_args()

        internal_authorize('CreateUser', f'arn:tinyauth:users/args["username"]')

        user = User(
            username=args['username'],
        )

        db.session.add(user)
        db.session.commit()

        return jsonify(marshal(user, user_fields))


user_api = Api(user_blueprint, prefix='/api/v1')
user_api.add_resource(UsersResource, '/users')
user_api.add_resource(UserResource, '/users/<user_id>')
