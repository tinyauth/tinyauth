import json

from flask import Blueprint, jsonify, make_response, request
from flask_restful import Api, Resource, abort, fields, marshal, reqparse

from tinyauth.app import db
from tinyauth.audit import audit_request_cbv
from tinyauth.authorize import internal_authorize
from tinyauth.models import Group, GroupPolicy
from tinyauth.simplerest import build_response_for_request


class Json(fields.Raw):
    def format(self, value):
        return json.dumps(value)


group_policy_fields = {
    'id': fields.String(attribute='name'),
    'name': fields.String,
    'policy': Json,
}

group_policy_parser = reqparse.RequestParser()
group_policy_parser.add_argument('name', type=str, location='json', required=True)
group_policy_parser.add_argument('policy', type=str, location='json', required=True)

group_policy_blueprint = Blueprint('group_policy', __name__)


class GroupPolicyResource(Resource):

    def _get_or_404(self, group, policy_name):
        policy = GroupPolicy.query.filter(GroupPolicy.group == group, GroupPolicy.name == policy_name).first()
        if not policy:
            abort(404, message=f'Policy {policy_name} for user {group} does not exist')
        return policy

    @audit_request_cbv('GetGroupPolicy')
    def get(self, audit_ctx, group_id, policy_name):
        internal_authorize('GetGroupPolicy', f'arn:tinyauth:groups/{group_id}')

        group = Group.query.filter(Group.name == group_id).first()
        if not group:
            abort(404, message=f'group {group_id} does not exist')

        policy = self._get_or_404(group, policy_name)
        audit_ctx['request.group'] = policy.group.name
        return jsonify(marshal(policy, group_policy_fields))

    @audit_request_cbv('UpdateGroupPolicy')
    def put(self, audit_ctx, group_id, policy_name):
        internal_authorize('UpdateGroupPolicy', f'arn:tinyauth:groups/{group_id}')

        group = Group.query.filter(Group.name == group_id).first()
        if not group:
            abort(404, message=f'group {group_id} does not exist')

        args = group_policy_parser.parse_args()

        policy = self._get_or_404(group, policy_name)
        audit_ctx['request.group'] = policy.group.name
        policy.name = args['name']
        policy.policy = json.loads(args['policy'])
        db.session.add(policy)

        db.session.commit()

        return jsonify(marshal(policy, group_policy_fields))

    @audit_request_cbv('DeleteGroupPolicy')
    def delete(self, audit_ctx, group_id, policy_name):
        internal_authorize('DeleteGroupPolicy', f'arn:tinyauth:groups/{group_id}')

        group = Group.query.filter(Group.name == group_id).first()
        if not group:
            abort(404, message=f'group {group_id} does not exist')

        policy = self._get_or_404(group, policy_name)
        audit_ctx['request.group'] = policy.group.name
        db.session.delete(policy)
        db.session.commit()

        return make_response(jsonify({}), 201, [])


class GroupPoliciesResource(Resource):

    @audit_request_cbv('ListGroupPolicies')
    def get(self, audit_ctx, group_id):
        group = Group.query.filter(Group.name == group_id).first()
        if not group:
            abort(404, message=f'Group {group_id} does not exist')

        audit_ctx['request.group'] = group.name

        internal_authorize('ListGroupPolicies', f'arn:tinyauth:groups/')

        return build_response_for_request(
            GroupPolicy,
            request,
            group_policy_fields,
            GroupPolicy.query.filter(GroupPolicy.group == group),
        )

    @audit_request_cbv('CreateGroupPolicy')
    def post(self, audit_ctx, group_id):
        group = Group.query.filter(Group.name == group_id).first()
        if not group:
            abort(404, message=f'Group {group_id} does not exist')

        audit_ctx['request.group'] = group.name

        args = group_policy_parser.parse_args()

        internal_authorize('CreateGroupPolicy', f'arn:tinyauth:groups/args["name"]')

        policy = GroupPolicy(
            group=group,
            name=args['name'],
            policy=json.loads(args['policy']),
        )

        db.session.add(policy)
        db.session.commit()

        return jsonify(marshal(policy, group_policy_fields))


group_policy_api = Api(group_policy_blueprint, prefix='/api/v1')
group_policy_api.add_resource(GroupPoliciesResource, '/groups/<group_id>/policies')
group_policy_api.add_resource(GroupPolicyResource, '/groups/<group_id>/policies/<policy_name>')
