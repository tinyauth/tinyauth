import base64
import json

from tinyauth.app import db
from tinyauth.models import Group

from .base import TestCase


class TestGroups(TestCase):

    def test_get_groups_no_groups(self):
        response = self.client.get(
            '/api/v1/groups',
            headers={
                'Authorization': 'Basic {}'.format(
                    base64.b64encode(b'AKIDEXAMPLE:password').decode('utf-8')
                ),
            }
        )

        assert response.status_code == 200
        assert response.get_data(as_text=True) == '[]\n'
        assert b''.join(response.response) == b'[]\n'

    def test_create_group_noauth(self):
        response = self.client.post(
            '/api/v1/groups',
            data=json.dumps({
                'name': 'devs',
            }),
            content_type='application/json',
        )
        assert response.status_code == 401
        assert json.loads(response.get_data(as_text=True)) == {
            'errors': {
                'authorization': 'UnsignedRequest'
            }
        }

    def test_create_group_with_auth(self):
        response = self.client.post(
            '/api/v1/groups',
            data=json.dumps({
                'name': 'devs',
            }),
            headers={
                'Authorization': 'Basic {}'.format(
                    base64.b64encode(b'AKIDEXAMPLE:password').decode('utf-8')
                )
            },
            content_type='application/json',
        )
        assert response.status_code == 200
        assert json.loads(response.get_data(as_text=True)) == {'id': 1, 'name': 'devs'}

    def test_delete_group_with_auth_but_no_perms(self):
        grp = Group(name='freddy')
        db.session.add(grp)
        db.session.commit()

        response = self.client.delete(
            '/api/v1/groups/1',
            headers={
                'Authorization': 'Basic {}'.format(
                    base64.b64encode(b'AKIDEXAMPLE2:password').decode('utf-8')
                )
            },
            content_type='application/json',
        )
        assert response.status_code == 403
        assert json.loads(response.get_data(as_text=True)) == {
            'errors': {
                'authorization': 'NotPermitted'
            }
        }

    def test_delete_group_with_auth(self):
        grp = Group(name='devs')
        db.session.add(grp)

        db.session.commit()

        response = self.client.delete(
            '/api/v1/groups/1',
            headers={
                'Authorization': 'Basic {}'.format(
                    base64.b64encode(b'AKIDEXAMPLE:password').decode('utf-8')
                )
            },
            content_type='application/json',
        )
        assert response.status_code == 201
        assert json.loads(response.get_data(as_text=True)) == {}

    def test_put_group_with_auth_but_no_perms(self):
        grp = Group(name='devs')
        db.session.add(grp)

        db.session.commit()

        response = self.client.put(
            '/api/v1/groups/1',
            data=json.dumps({
                'name': 'devs',
            }),
            headers={
                'Authorization': 'Basic {}'.format(
                    base64.b64encode(b'AKIDEXAMPLE2:password').decode('utf-8')
                )
            },
            content_type='application/json',
        )
        assert response.status_code == 403
        assert json.loads(response.get_data(as_text=True)) == {
            'errors': {
                'authorization': 'NotPermitted'
            }
        }

    def test_put_group_with_auth(self):
        grp = Group(name='devs')
        db.session.add(grp)

        db.session.commit()

        response = self.client.put(
            '/api/v1/groups/1',
            data=json.dumps({
                'name': 'devs',
            }),
            headers={
                'Authorization': 'Basic {}'.format(
                    base64.b64encode(b'AKIDEXAMPLE:password').decode('utf-8')
                )
            },
            content_type='application/json',
        )
        assert response.status_code == 200
        assert json.loads(response.get_data(as_text=True)) == {'id': 1, 'name': 'devs'}

    def test_get_group_with_auth_but_no_perms(self):
        grp = Group(name='freddy')
        db.session.add(grp)
        db.session.commit()

        response = self.client.get(
            '/api/v1/groups/1',
            headers={
                'Authorization': 'Basic {}'.format(
                    base64.b64encode(b'AKIDEXAMPLE2:password').decode('utf-8')
                )
            },
            content_type='application/json',
        )
        assert response.status_code == 403
        assert json.loads(response.get_data(as_text=True)) == {
            'errors': {
                'authorization': 'NotPermitted'
            }
        }

    def test_get_group_with_auth(self):
        grp = Group(name='devs')
        db.session.add(grp)
        db.session.commit()

        response = self.client.get(
            '/api/v1/groups/1',
            headers={
                'Authorization': 'Basic {}'.format(
                    base64.b64encode(b'AKIDEXAMPLE:password').decode('utf-8')
                )
            },
            content_type='application/json',
        )
        assert response.status_code == 200
        assert json.loads(response.get_data(as_text=True)) == {'id': 1, 'name': 'devs'}
