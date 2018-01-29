import base64
import contextlib
import json
import unittest
from unittest import mock

from tinyauth.app import create_app, db
from tinyauth.models import AccessKey, User, UserPolicy


class TestCase(unittest.TestCase):

    def patch(self, *args, **kwargs):
        patcher = mock.patch(*args, **kwargs)
        self.addCleanup(patcher.stop)
        return patcher.start()

    def patch_object(self, *args, **kwargs):
        patcher = mock.patch.object(*args, **kwargs)
        self.addCleanup(patcher.stop)
        return patcher.start()

    def patch_dict(self, *args, **kwargs):
        patcher = mock.patch.dict(*args, **kwargs)
        self.addCleanup(patcher.stop)
        return patcher.start()

    def setUp(self):
        self.stack = contextlib.ExitStack()

        self.app = create_app(self)
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        db.create_all(app=self.app)

        self._ctx = self.app.test_request_context()
        self._ctx.push()

        self.user = user = User(username='charles')
        user.set_password('mrfluffy')
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

        self.user2 = user = User(username='freddy')
        user.set_password('mrfluffy2')
        db.session.add(user)

        db.session.add(AccessKey(
            access_key_id='AKIDEXAMPLE2',
            secret_access_key='password',
            user=user,
        ))

        db.session.commit()

        uuid4 = self.stack.enter_context(mock.patch('uuid.uuid4'))
        uuid4.return_value = 'a823a206-95a0-4666-b464-93b9f0606d7b'

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self._ctx.pop()
        self.stack.close()

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
