import json

from flask import Blueprint, jsonify, make_response, request
from flask_restful import Api, Resource, abort, fields, marshal, reqparse

from tinyauth.app import db
from tinyauth.audit import audit_request_cbv
from tinyauth.authorize import format_arn, internal_authorize
from tinyauth.models import User, UserPolicy
from tinyauth.simplerest import build_response_for_request


class Json(fields.Raw):
    def format(self, value):
        return json.dumps(value)


user_policy_fields = {
    'id': fields.String(attribute='name'),
    'name': fields.String,
    'policy': Json,
}

user_policy_parser = reqparse.RequestParser()
user_policy_parser.add_argument('name', type=str, location='json', required=True)
user_policy_parser.add_argument('policy', type=str, location='json', required=True)

user_policy_blueprint = Blueprint('user_policy', __name__)


class UserPolicyResource(Resource):

    def _get_or_404(self, user, policy_name):
        policy = UserPolicy.query.filter(UserPolicy.user == user, UserPolicy.name == policy_name).first()
        if not policy:
            abort(404, message=f'Policy {policy_name} for user {user} does not exist')
        return policy

    @audit_request_cbv('GetUserPolicy')
    def get(self, audit_ctx, username, policy_name):
        audit_ctx['request.username'] = username
        internal_authorize('GetUserPolicy', format_arn('users', username))

        user = User.query.filter(User.username == username).first()
        if not user:
            abort(404, message=f'User doesn\'t exist')

        policy = self._get_or_404(user, policy_name)
        return jsonify(marshal(policy, user_policy_fields))

    @audit_request_cbv('UpdateUserPolicy')
    def put(self, audit_ctx, username, policy_name):
        audit_ctx['request.username'] = username
        internal_authorize('UpdateUserPolicy', format_arn('users', username))

        user = User.query.filter(User.username == username).first()
        if not user:
            abort(404, message=f'User doesn\'t exist')

        args = user_policy_parser.parse_args()

        policy = self._get_or_404(user, policy_name)
        policy.name = args['name']
        policy.policy = json.loads(args['policy'])
        db.session.add(policy)

        db.session.commit()

        return jsonify(marshal(policy, user_policy_fields))

    @audit_request_cbv('DeleteUserPolicy')
    def delete(self, audit_ctx, username, policy_name):
        audit_ctx['request.username'] = username
        internal_authorize('DeleteUserPolicy', format_arn('users', username))

        user = User.query.filter(User.username == username).first()
        if not user:
            abort(404, message=f'User doesn\'t exist')

        policy = self._get_or_404(user, policy_name)
        db.session.delete(policy)
        db.session.commit()

        return make_response(jsonify({}), 201, [])


class UserPoliciesResource(Resource):

    @audit_request_cbv('ListUserPolicies')
    def get(self, audit_ctx, username):
        audit_ctx['request.username'] = username
        internal_authorize('ListUserPolicies', format_arn('users', username))

        user = User.query.filter(User.username == username).first()
        if not user:
            abort(404, message=f'User doesn\'t exist')

        return build_response_for_request(
            UserPolicy,
            request,
            user_policy_fields,
            UserPolicy.query.filter(UserPolicy.user == user),
        )

    @audit_request_cbv('CreateUserPolicy')
    def post(self, audit_ctx, username):
        audit_ctx['request.username'] = username
        internal_authorize('CreateUserPolicy', format_arn('users', username))

        user = User.query.filter(User.username == username).first()
        if not user:
            abort(404, message=f'User doesn\'t exist')

        args = user_policy_parser.parse_args()

        policy = UserPolicy(
            user=user,
            name=args['name'],
            policy=json.loads(args['policy']),
        )

        db.session.add(policy)
        db.session.commit()

        return jsonify(marshal(policy, user_policy_fields))


user_policy_api = Api(user_policy_blueprint, prefix='/api/v1')
user_policy_api.add_resource(UserPoliciesResource, '/users/<username>/policies')
user_policy_api.add_resource(UserPolicyResource, '/users/<username>/policies/<policy_name>')
