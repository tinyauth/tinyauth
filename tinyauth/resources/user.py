from flask import Blueprint, jsonify, make_response, request
from flask_restful import Resource, abort, fields, marshal, reqparse

from tinyauth.api import Api
from tinyauth.app import db
from tinyauth.audit import audit_request_cbv
from tinyauth.authorize import internal_authorize
from tinyauth.models import User
from tinyauth.simplerest import build_response_for_request

user_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'groups': fields.List(fields.Nested({
        'id': fields.String,
        'name': fields.String,
    })),
}

user_parser = reqparse.RequestParser()
user_parser.add_argument('username', type=str, location='json', required=True)
user_parser.add_argument('password', type=str, location='json')

user_blueprint = Blueprint('user', __name__)


class UserResource(Resource):

    def _get_or_404(self, user_id):
        user = User.query.filter(User.id == user_id).first()
        if not user:
            abort(404, message=f'user {user_id} does not exist')
        return user

    @audit_request_cbv('GetUser')
    def get(self, audit_ctx, user_id):
        internal_authorize('GetUser', f'arn:tinyauth:users/{user_id}')

        user = self._get_or_404(user_id)
        audit_ctx['request.username'] = user.username
        return jsonify(marshal(user, user_fields))

    @audit_request_cbv('UpdateUser')
    def put(self, audit_ctx, user_id):
        internal_authorize('UpdateUser', f'arn:tinyauth:users/{user_id}')

        args = user_parser.parse_args()

        user = self._get_or_404(user_id)
        audit_ctx['request.username'] = user.username

        if 'username' in args:
            user.username = args['username']
        if 'password' in args:
            user.set_password(args['password'])
        db.session.add(user)

        db.session.commit()

        return jsonify(marshal(user, user_fields))

    @audit_request_cbv('DeleteUser')
    def delete(self, audit_ctx, user_id):
        internal_authorize('DeleteUser', f'arn:tinyauth:users/{user_id}')

        user = self._get_or_404(user_id)
        audit_ctx['request.username'] = user.username
        db.session.delete(user)

        return make_response(jsonify({}), 201, [])


class UsersResource(Resource):

    @audit_request_cbv('ListUsers')
    def get(self, audit_ctx):
        internal_authorize('ListUsers', f'arn:tinyauth:users/')

        return build_response_for_request(User, request, user_fields)

    @audit_request_cbv('CreateUser')
    def post(self, audit_ctx):
        args = user_parser.parse_args()

        audit_ctx['request.username'] = args['username']

        internal_authorize('CreateUser', f'arn:tinyauth:users/args["username"]')

        user = User(
            username=args['username'],
        )
        if args['password']:
            user.set_password(args['password'])

        db.session.add(user)
        db.session.commit()

        return jsonify(marshal(user, user_fields))


user_api = Api(user_blueprint, prefix='/api/v1')
user_api.add_resource(UsersResource, '/users')
user_api.add_resource(UserResource, '/users/<user_id>')
