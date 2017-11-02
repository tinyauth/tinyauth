import base64
import json
import unittest

from microauth.app import create_app, db
from microauth.models import AccessKey, Policy, User


class TestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(self)
        self.app.debug = True
        self.app.config['BUNDLE_ERRORS'] = True
        self.app.config['TESTING'] = True
        self.app.config['DEBUG'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        db.create_all(app=self.app)

        self._ctx = self.app.test_request_context()
        self._ctx.push()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self._ctx.pop()

    def test_authorize_service(self):
        policy = Policy(name='microauth', policy={
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'microauth:*',
                'Resource': 'arn:microauth:*',
                'Effect': 'Allow',
            }, {
                'Action': 'myservice:*',
                'Resource': '*',
                'Effect': 'Allow',
            }]
        })
        db.session.add(policy)

        user = User(username='charles')
        user.policies.append(policy)
        db.session.add(user)

        access_key = AccessKey(
            access_key_id='AKIDEXAMPLE',
            secret_access_key='password',
            user=user,
        )
        db.session.add(access_key)

        db.session.commit()

        response = self.client.post(
            '/api/v1/authorize',
            data=json.dumps({
                'action': 'myservice:LaunchRocket',
                'resource': 'arn:myservice:rockets/thrift',
                'headers': [
                    ('Authorization', 'Basic {}'.format(
                        base64.b64encode(b'AKIDEXAMPLE:password').decode('utf-8')))
                ],
                'context': {},
            }),
            headers={
                'Authorization': 'Basic {}'.format(
                    base64.b64encode(b'AKIDEXAMPLE:password').decode('utf-8')
                )
            },
            content_type='application/json',
        )
        assert response.status_code == 200
        assert json.loads(response.get_data(as_text=True)) == {'Authorized': True}

    def test_authorize_service_failure(self):
        policy = Policy(name='microauth', policy={
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'microauth:*',
                'Resource': 'arn:microauth:*',
                'Effect': 'Allow',
            }, {
                'Action': 'myservice:*',
                'Resource': 'arn:myservice:rockets/lander1',
                'Effect': 'Allow',
            }]
        })
        db.session.add(policy)

        user = User(username='charles')
        user.policies.append(policy)
        db.session.add(user)

        access_key = AccessKey(
            access_key_id='AKIDEXAMPLE',
            secret_access_key='password',
            user=user,
        )
        db.session.add(access_key)

        db.session.commit()

        response = self.client.post(
            '/api/v1/authorize',
            data=json.dumps({
                'action': 'myservice:LaunchRocket',
                'resource': 'arn:myservice:rockets/thrift',
                'headers': [
                    ('Authorization', 'Basic {}'.format(
                        base64.b64encode(b'AKIDEXAMPLE:password').decode('utf-8')))
                ],
                'context': {},
            }),
            headers={
                'Authorization': 'Basic {}'.format(
                    base64.b64encode(b'AKIDEXAMPLE:password').decode('utf-8')
                )
            },
            content_type='application/json',
        )
        assert response.status_code == 200
        assert json.loads(response.get_data(as_text=True)) == {
            'Authorized': False,
            'ErrorCode': 'NotPermitted',
        }
