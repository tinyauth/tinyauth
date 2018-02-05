import json

from tinyauth.models import Group, GroupPolicy, db

from . import base


class TestCase(base.TestCase):

    def setUp(self):
        super().setUp()

        group = Group(name='test-group')
        db.session.add(group)

        gp = GroupPolicy(name='test-policy', policy={}, group=group)
        db.session.add(gp)

        db.session.commit()

    def test_list_group_policies(self):
        response = self.req('get', '/api/v1/groups/test-group/policies')

        assert response.status_code == 200
        assert json.loads(response.get_data(as_text=True)) == [{
            'id': 'test-policy',
            'name': 'test-policy',
            'policy': json.dumps({}),
        }]

        args, kwargs = self.audit_log.call_args_list[0]
        assert args[0] == 'ListGroupPolicies'
        assert kwargs['extra'] == {
            'request-id': 'a823a206-95a0-4666-b464-93b9f0606d7b',
            'http.status': 200,
            'request.group': 'test-group',
        }

    def test_get_group_policy(self):
        response = self.req('get', '/api/v1/groups/test-group/policies/test-policy')

        assert response.status_code == 200
        assert json.loads(response.get_data(as_text=True)) == {
            'id': 'test-policy',
            'name': 'test-policy',
            'policy': json.dumps({}),
        }

        args, kwargs = self.audit_log.call_args_list[0]
        assert args[0] == 'GetGroupPolicy'
        assert kwargs['extra'] == {
            'request-id': 'a823a206-95a0-4666-b464-93b9f0606d7b',
            'http.status': 200,
            'request.group': 'test-group',
            'request.policy': 'test-policy',
        }

    def test_create_group_policy(self):
        policy = {'Statement': []}

        response = self.req('post', '/api/v1/groups/test-group/policies', body={
            'name': 'example1',
            'policy': json.dumps(policy),
        })

        assert json.loads(response.get_data(as_text=True)) == {
            'id': 'example1',
            'name': 'example1',
            'policy': json.dumps(policy),
        }

        response = self.req('get', '/api/v1/groups/test-group/policies')
        assert len(json.loads(response.get_data(as_text=True))) == 2

        args, kwargs = self.audit_log.call_args_list[0]
        assert args[0] == 'CreateGroupPolicy'
        assert kwargs['extra'] == {
            'request-id': 'a823a206-95a0-4666-b464-93b9f0606d7b',
            'http.status': 200,
            'request.group': 'test-group',
            'request.policy': 'example1',
            'request.policy-json': json.dumps(policy, indent=4, separators=(',', ': ')),
        }

    def test_delete_group_policy(self):
        response = self.req('post', '/api/v1/groups/test-group/policies', body={
            'name': 'example1',
            'policy': json.dumps({'Statement': []})
        })
        assert response.status_code == 200

        response = self.req('get', '/api/v1/groups/test-group/policies')
        assert len(json.loads(response.get_data(as_text=True))) == 2

        response = self.req('delete', '/api/v1/groups/test-group/policies/example1')

        assert response.status_code == 201
        assert json.loads(response.get_data(as_text=True)) == {}

        response = self.req('get', '/api/v1/groups/test-group/policies')
        assert len(json.loads(response.get_data(as_text=True))) == 1

        args, kwargs = self.audit_log.call_args_list[2]
        assert args[0] == 'DeleteGroupPolicy'
        assert kwargs['extra'] == {
            'request-id': 'a823a206-95a0-4666-b464-93b9f0606d7b',
            'http.status': 201,
            'request.group': 'test-group',
            'request.policy': 'example1',
        }
