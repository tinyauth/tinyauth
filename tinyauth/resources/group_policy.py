import json

from flask import Blueprint, jsonify, make_response, request
from flask_restful import Api, Resource, abort, fields, marshal, reqparse

from tinyauth.app import db
from tinyauth.authorize import internal_authorize
from tinyauth.models import GroupPolicy
from tinyauth.simplerest import build_response_for_request


class Json(fields.Raw):
    def format(self, value):
        return json.dumps(value)


group_policy_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'policy': Json,
}

group_policy_parser = reqparse.RequestParser()
group_policy_parser.add_argument('name', type=str, location='json', required=True)
group_policy_parser.add_argument('policy', type=str, location='json', required=True)

group_policy_blueprint = Blueprint('group_policy', __name__)


class GroupPolicyResource(Resource):

    def _get_or_404(self, group_id, policy_id):
        policy = GroupPolicy.query.filter(GroupPolicy.group_id == group_id, GroupPolicy.id == policy_id).first()
        if not policy:
            abort(404, message=f'Policy {policy_id} for user {group_id} does not exist')
        return policy

    def get(self, group_id, policy_id):
        internal_authorize('GetGroupPolicy', f'arn:tinyauth:groups/{group_id}')

        policy = self._get_or_404(group_id, policy_id)
        return jsonify(marshal(policy, group_policy_fields))

    def put(self, group_id, policy_id):
        internal_authorize('UpdateGroupPolicy', f'arn:tinyauth:groups/{group_id}')

        args = group_policy_parser.parse_args()

        policy = self._get_or_404(group_id, policy_id)
        policy.name = args['name']
        policy.policy = json.loads(args['policy'])
        db.session.add(policy)

        db.session.commit()

        return jsonify(marshal(policy, group_policy_fields))

    def delete(self, group_id, policy_id):
        internal_authorize('DeleteGroupPolicy', f'arn:tinyauth:groups/{group_id}')

        policy = self._get_or_404(group_id, policy_id)
        db.session.delete(policy)
        db.session.commit()

        return make_response(jsonify({}), 201, [])


class GroupPoliciesResource(Resource):

    def get(self, group_id):
        internal_authorize('ListGroupPolicies', f'arn:tinyauth:groups/')

        return build_response_for_request(
            GroupPolicy,
            request,
            group_policy_fields,
            GroupPolicy.query.filter(GroupPolicy.group_id == group_id),
        )

    def post(self, group_id):
        args = group_policy_parser.parse_args()

        internal_authorize('CreateGroupPolicy', f'arn:tinyauth:groups/args["name"]')

        policy = GroupPolicy(
            group_id=group_id,
            name=args['name'],
            policy=json.loads(args['policy']),
        )

        db.session.add(policy)
        db.session.commit()

        return jsonify(marshal(policy, group_policy_fields))


group_policy_api = Api(group_policy_blueprint, prefix='/api/v1')
group_policy_api.add_resource(GroupPoliciesResource, '/groups/<group_id>/policies')
group_policy_api.add_resource(GroupPolicyResource, '/groups/<group_id>/policies/<policy_id>')
