import base64
import json
import unittest

from tinyauth.app import create_app, db
from tinyauth.models import AccessKey, User, UserPolicy


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

        user = User(username='charles')
        db.session.add(user)

        policy = UserPolicy(name='tinyauth', user=user, policy={
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'tinyauth:*',
                'Resource': 'arn:tinyauth:*',
                'Effect': 'Allow',
            }]
        })
        db.session.add(policy)

        access_key = AccessKey(
            access_key_id='AKIDEXAMPLE',
            secret_access_key='password',
            user=user,
        )
        db.session.add(access_key)

        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self._ctx.pop()

    def req(self, method, uri, headers=None, body=None):
        actual_headers = {
            'Authorization': 'Basic {}'.format(
                base64.b64encode(b'AKIDEXAMPLE:password').decode('utf-8')
            ),
        }
        if headers:
            actual_headers.update(headers)

        method = getattr(self.client, method)

        return method(
            uri,
            headers=actual_headers,
            content_type='application/json',
            data=json.dumps(body) if body else None,
        )
