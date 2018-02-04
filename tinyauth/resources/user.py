from flask import Blueprint, jsonify, make_response, request
from flask_restful import Resource, abort, fields, marshal, reqparse

from tinyauth.api import Api
from tinyauth.app import db
from tinyauth.audit import audit_request_cbv
from tinyauth.authorize import format_arn, internal_authorize
from tinyauth.models import User
from tinyauth.simplerest import build_response_for_request

user_fields = {
    'id': fields.String(attribute='username'),
    'username': fields.String,
    'groups': fields.List(fields.Nested({
        'id': fields.String(attribute='name'),
        'name': fields.String,
    })),
}

user_parser = reqparse.RequestParser()
user_parser.add_argument('username', type=str, location='json', required=True)
user_parser.add_argument('password', type=str, location='json')

user_blueprint = Blueprint('user', __name__)


class UserResource(Resource):

    def _get_or_404(self, username):
        user = User.query.filter(User.username == username).first()
        if not user:
            abort(404, message=f'user {username} does not exist')
        return user

    @audit_request_cbv('GetUser')
    def get(self, audit_ctx, username):
        audit_ctx['request.username'] = username
        internal_authorize('GetUser', format_arn('users', username))

        user = self._get_or_404(username)
        return jsonify(marshal(user, user_fields))

    @audit_request_cbv('UpdateUser')
    def put(self, audit_ctx, username):
        audit_ctx['request.username'] = username
        internal_authorize('UpdateUser', format_arn('users', username))

        args = user_parser.parse_args()

        if 'username' in args:
            audit_ctx['request.new-username'] = args['username']
        if 'password' in args:
            audit_ctx['request.password'] = '********'

        user = self._get_or_404(username)

        if 'username' in args:
            user.username = args['username']
        if 'password' in args:
            user.set_password(args['password'])
        db.session.add(user)

        db.session.commit()

        return jsonify(marshal(user, user_fields))

    @audit_request_cbv('DeleteUser')
    def delete(self, audit_ctx, username):
        audit_ctx['request.username'] = username
        internal_authorize('DeleteUser', format_arn('users', username))

        user = self._get_or_404(username)
        db.session.delete(user)

        return make_response(jsonify({}), 201, [])


class UsersResource(Resource):

    @audit_request_cbv('ListUsers')
    def get(self, audit_ctx):
        internal_authorize('ListUsers', format_arn('users'))

        return build_response_for_request(User, request, user_fields)

    @audit_request_cbv('CreateUser')
    def post(self, audit_ctx):
        args = user_parser.parse_args()

        audit_ctx['request.username'] = args['username']

        internal_authorize('CreateUser', format_arn('users', args['username']))

        user = User(
            username=args['username'],
        )
        if args['password']:
            user.set_password(args['password'])
            audit_ctx['request.password'] = '********'

        db.session.add(user)
        db.session.commit()

        return jsonify(marshal(user, user_fields))


user_api = Api(user_blueprint, prefix='/api/v1')
user_api.add_resource(UsersResource, '/users')
user_api.add_resource(UserResource, '/users/<username>')
