from flask import Blueprint, jsonify, make_response, request
from flask_restful import Api, Resource, abort, fields, marshal, reqparse

from tinyauth.app import db
from tinyauth.authorize import internal_authorize
from tinyauth.models import UserPolicy
from tinyauth.simplerest import build_response_for_request

user_policy_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'policy': fields.String,
}

user_policy_parser = reqparse.RequestParser()
user_policy_parser.add_argument('name', type=str, location='json', required=True)
user_policy_parser.add_argument('policy', type=str, location='json', required=True)

user_policy_blueprint = Blueprint('user_policy', __name__)


class UserPolicyResource(Resource):

    def _get_or_404(self, user_id, policy_id):
        policy = UserPolicy.query.filter(UserPolicy.user_id == user_id, UserPolicy.id == policy_id).first()
        if not policy:
            abort(404, message=f'Policy {policy_id} for user {user_id} does not exist')
        return policy

    def get(self, user_id, policy_id):
        internal_authorize('GetUserPolicy', f'arn:tinyauth:users/{user_id}')

        policy = self._get_or_404(user_id, policy_id)
        return jsonify(marshal(policy, user_policy_fields))

    def put(self, user_id, policy_id):
        internal_authorize('UpdateUserPolicy', f'arn:tinyauth:users/{user_id}')

        args = user_policy_parser.parse_args()

        policy = self._get_or_404(user_id, policy_id)
        policy.name = args['name']
        policy.policy = args['policy']
        db.session.add(policy)

        db.session.commit()

        return jsonify(marshal(policy, user_policy_fields))

    def delete(self, user_id, policy_id):
        internal_authorize('DeleteUserPolicy', f'arn:tinyauth:users/{user_id}')

        policy = self._get_or_404(user_id, policy_id)
        db.session.delete(policy)

        return make_response(jsonify({}), 201, [])


class UserPoliciesResource(Resource):

    def get(self, user_id):
        internal_authorize('ListUserPolicies', f'arn:tinyauth:users/')

        # FIXME Need to filter by user_id here
        return build_response_for_request(UserPolicy, request, user_policy_fields)

    def post(self, user_id):
        args = user_policy_parser.parse_args()

        internal_authorize('CreateUserPolicy', f'arn:tinyauth:users/args["username"]')

        policy = UserPolicy(
            user_id = user_id,
            name=args['name'],
            policy=args['policy'],
        )

        db.session.add(user)
        db.session.commit()

        return jsonify(marshal(user, user_policy_fields))


user_policy_api = Api(user_policy_blueprint, prefix='/api/v1')
user_policy_api.add_resource(UserPoliciesResource, '/users/<user_id>/policies')
user_policy_api.add_resource(UserPolicyResource, '/users/<user_id>/policies/<policy_id>')
