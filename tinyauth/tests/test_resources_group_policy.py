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
        response = self.req('get', '/api/v1/groups/1/policies')

        assert response.status_code == 200
        assert json.loads(response.get_data(as_text=True)) == [{
            'id': 1,
            'name': 'test-policy',
            'policy': json.dumps({}),
        }]

    def test_get_group_policy(self):
        response = self.req('get', '/api/v1/groups/1/policies/1')

        assert response.status_code == 200
        assert json.loads(response.get_data(as_text=True)) == {
            'id': 1,
            'name': 'test-policy',
            'policy': json.dumps({}),
        }

    def test_create_group_policy(self):
        response = self.req('post', '/api/v1/groups/1/policies', body={
            'name': 'example1',
            'policy': json.dumps({'Statement': []})
        })

        assert json.loads(response.get_data(as_text=True)) == {
            'id': 2,
            'name': 'example1',
            'policy': json.dumps({'Statement': []}),
        }

        response = self.req('get', '/api/v1/groups/1/policies')
        assert len(json.loads(response.get_data(as_text=True))) == 2

    def test_delete_group_policy(self):
        response = self.req('post', '/api/v1/groups/1/policies', body={
            'name': 'example1',
            'policy': json.dumps({'Statement': []})
        })
        assert response.status_code == 200

        response = self.req('get', '/api/v1/groups/1/policies')
        assert len(json.loads(response.get_data(as_text=True))) == 2

        response = self.req('delete', '/api/v1/groups/1/policies/2')

        assert response.status_code == 201
        assert json.loads(response.get_data(as_text=True)) == {}

        response = self.req('get', '/api/v1/groups/1/policies')
        assert len(json.loads(response.get_data(as_text=True))) == 1
