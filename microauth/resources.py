from flask import jsonify, request
from flask_restful import Resource, abort, fields, marshal, reqparse

from microauth.app import api, db
from microauth.authorize import authorize
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
        authorize('microauth:GetUser', f'arn:microauth:users/{user_id}')

        user = self._get_or_404(user_id)
        return jsonify(marshal(user, user_fields))

    def put(self, user_id):
        authorize('microauth:UpdateUser', f'arn:microauth:users/{user_id}')

        args = user_parser.parse_args()

        user = self._get_or_404(user_id)
        user.name = args['username']
        db.session.add(user)

        db.session.commit()

        return jsonify(marshal(user, user_fields))

    def delete(self, user_id):
        authorize('microauth:DeleteUser', f'arn:microauth:users/{user_id}')

        user = self._get_or_404(user_id)
        db.session.delete(user)

        return '{}', 201


class UsersResource(Resource):

    def get(self):
        return build_response_for_request(User, request, user_fields)

    def post(self):
        args = user_parser.parse_args()

        authorize('microauth:CreateUser', f'arn:microauth:users/args["username"]')

        user = User(
            username=args['username'],
        )

        db.session.add(user)
        db.session.commit()

        return jsonify(marshal(user, user_fields))


api.add_resource(UsersResource, '/users')
api.add_resource(UserResource, '/users/<key_id>')
