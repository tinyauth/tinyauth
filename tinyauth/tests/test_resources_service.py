import base64
import json

from tinyauth.app import db
from tinyauth.audit import format_json
from tinyauth.models import UserPolicy

from . import base


class TestCaseToken(base.TestCase):

    def test_authorize_service_invalid_outer_auth(self):
        policy = UserPolicy(name='myserver', user=self.user, policy={
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'myservice:*',
                'Resource': '*',
                'Effect': 'Allow',
            }]
        })
        db.session.add(policy)

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
                    base64.b64encode(b'AKIDEXAMPLE:pword').decode('utf-8')
                )
            },
            content_type='application/json',
        )
        assert response.status_code == 401
        assert json.loads(response.get_data(as_text=True)) == {
            'errors': {'authorization': 'InvalidSignature'}
        }

        args, kwargs = self.audit_log.call_args_list[0]
        assert args[0] == 'AuthorizeByToken'
        assert kwargs['extra'] == {
            'request-id': 'a823a206-95a0-4666-b464-93b9f0606d7b',
            'http.status': 401,
            'request.legacy': True,
            'errors': {'authorization': 'InvalidSignature'},
        }

    def test_authorize_service_invalid_params(self):
        policy = UserPolicy(name='myserver', user=self.user, policy={
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'myservice:*',
                'Resource': '*',
                'Effect': 'Allow',
            }]
        })
        db.session.add(policy)

        db.session.commit()

        response = self.client.post(
            '/api/v1/authorize',
            data=json.dumps({
                'action': 'myservice:LaunchRocket',
                'reesource': 'arn:myservice:rockets/thrift',
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
        assert response.status_code == 400
        assert json.loads(response.get_data(as_text=True)) == {
            'errors': {
                'reesource': 'Unexpected argument',
                'resource': 'Missing required parameter in the JSON body'
            }
        }

        args, kwargs = self.audit_log.call_args_list[0]
        assert args[0] == 'AuthorizeByToken'
        assert kwargs['extra'] == {
            'request-id': 'a823a206-95a0-4666-b464-93b9f0606d7b',
            'http.status': 400,
            'request.legacy': True,
            'errors': {
                'reesource': 'Unexpected argument',
                'resource': 'Missing required parameter in the JSON body'
            }
        }

    def test_authorize_service(self):
        policy = UserPolicy(name='myserver', user=self.user, policy={
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'myservice:*',
                'Resource': '*',
                'Effect': 'Allow',
            }]
        })
        db.session.add(policy)

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
        assert json.loads(response.get_data(as_text=True)) == {'Authorized': True, 'Identity': 'charles'}

        args, kwargs = self.audit_log.call_args_list[0]
        assert args[0] == 'AuthorizeByToken'
        assert kwargs['extra'] == {
            'request-id': 'a823a206-95a0-4666-b464-93b9f0606d7b',
            'http.status': 200,
            'request.legacy': True,
            'request.permit': format_json({
                'myservice:LaunchRocket': ['arn:myservice:rockets/thrift'],
            }),
            'request.actions': ['myservice:LaunchRocket'],
            'request.resources': ['arn:myservice:rockets/thrift'],
            'request.headers': ['Authorization: ** NOT LOGGED **'],
            'request.context': {},
            'response.authorized': True,
            'response.identity': 'charles',
        }

    def test_authorize_service_failure(self):
        policy = UserPolicy(name='myserver', user=self.user, policy={
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'myservice:*',
                'Resource': '*',
                'Effect': 'Deny',
            }]
        })
        db.session.add(policy)

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
            'Status': 403,
        }

        args, kwargs = self.audit_log.call_args_list[0]
        assert args[0] == 'AuthorizeByToken'
        assert kwargs['extra'] == {
            'request-id': 'a823a206-95a0-4666-b464-93b9f0606d7b',
            'http.status': 200,
            'request.legacy': True,
            'request.permit': format_json({
                'myservice:LaunchRocket': ['arn:myservice:rockets/thrift'],
            }),
            'request.actions': ['myservice:LaunchRocket'],
            'request.resources': ['arn:myservice:rockets/thrift'],
            'request.headers': ['Authorization: ** NOT LOGGED **'],
            'request.context': {},
            'response.authorized': False,
        }


class TestCaseBatchToken(base.TestCase):

    def test_invalid_outer_auth(self):
        response = self.client.post(
            '/api/v1/services/myservice/authorize-by-token',
            data=json.dumps({
                'permit': {
                    'LaunchRocket': ['arn:myservice:rockets/thrift'],
                },
                'headers': [
                    ('Authorization', 'Basic {}'.format(
                        base64.b64encode(b'AKIDEXAMPLE:password').decode('utf-8')))
                ],
                'context': {},
            }),
            headers={
                'Authorization': 'Basic {}'.format(
                    base64.b64encode(b'AKIDEXAMPLE:wrongpassword').decode('utf-8')
                ),
            },
            content_type='application/json',
        )
        assert response.status_code == 401
        assert json.loads(response.get_data(as_text=True)) == {
            'errors': {
                'authorization': 'InvalidSignature',
            }
        }

        args, kwargs = self.audit_log.call_args_list[0]
        assert args[0] == 'AuthorizeByToken'
        assert kwargs['extra'] == {
            'request-id': 'a823a206-95a0-4666-b464-93b9f0606d7b',
            'http.status': 401,
            'errors': {'authorization': 'InvalidSignature'},
            'request.service': 'myservice',
            'response.authorized': False,
        }

    def test_validate_input_failure(self):
        response = self.client.post(
            '/api/v1/services/myservice/authorize-by-token',
            data=json.dumps({
                'permote': {
                    'LaunchRocket': ['arn:myservice:rockets/thrift'],
                },
                'headers': [
                    ('Authorization', 'Basic {}'.format(
                        base64.b64encode(b'AKIDEXAMPLE:password').decode('utf-8')))
                ],
                'context': {},
            }),
            headers={
                'Authorization': 'Basic {}'.format(
                    base64.b64encode(b'AKIDEXAMPLE:password').decode('utf-8')
                ),
            },
            content_type='application/json',
        )
        assert 'X-Request-Id' in response.headers
        assert response.status_code == 400
        assert json.loads(response.get_data(as_text=True)) == {
            'errors': {
                'permit': 'Missing required parameter in the JSON body',
                'permote': 'Unexpected argument',
            }
        }

        args, kwargs = self.audit_log.call_args_list[0]
        assert args[0] == 'AuthorizeByToken'
        assert kwargs['extra'] == {
            'request-id': 'a823a206-95a0-4666-b464-93b9f0606d7b',
            'http.status': 400,
            'errors': {
                'permit': 'Missing required parameter in the JSON body',
                'permote': 'Unexpected argument',
            },
            'request.service': 'myservice',
            'response.authorized': False,
        }

    def test_authorize_service(self):
        policy = UserPolicy(name='myserver', user=self.user, policy={
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'myservice:*',
                'Resource': '*',
                'Effect': 'Allow',
            }]
        })
        db.session.add(policy)

        db.session.commit()

        response = self.client.post(
            '/api/v1/services/myservice/authorize-by-token',
            data=json.dumps({
                'permit': {
                    'LaunchRocket': ['arn:myservice:rockets/thrift'],
                },
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
            'Authorized': True,
            'Identity': 'charles',
            'Permitted': {'LaunchRocket': ['arn:myservice:rockets/thrift']},
            'NotPermitted': {},
        }

        args, kwargs = self.audit_log.call_args_list[0]
        assert args[0] == 'AuthorizeByToken'
        assert kwargs['extra'] == {
            'request-id': 'a823a206-95a0-4666-b464-93b9f0606d7b',
            'http.status': 200,
            'request.service': 'myservice',
            'request.permit': format_json({
                'LaunchRocket': ['arn:myservice:rockets/thrift'],
            }),
            'request.actions': ['myservice:LaunchRocket'],
            'request.resources': ['arn:myservice:rockets/thrift'],
            'request.headers': ['Authorization: ** NOT LOGGED **'],
            'request.context': {},
            'response.authorized': True,
            'response.identity': 'charles',
            'response.permitted': format_json({'LaunchRocket': ['arn:myservice:rockets/thrift']}),
            'response.not-permitted': format_json({}),
        }

    def test_authorize_service_failure(self):
        policy = UserPolicy(name='myserver', user=self.user, policy={
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'myservice:*',
                'Resource': '*',
                'Effect': 'Deny',
            }]
        })
        db.session.add(policy)

        db.session.commit()

        response = self.client.post(
            '/api/v1/services/myservice/authorize-by-token',
            data=json.dumps({
                'permit': {
                    'LaunchRocket': ['arn:myservice:rockets/thrift'],
                },
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
            'NotPermitted': {'LaunchRocket': ['arn:myservice:rockets/thrift']},
            'Permitted': {},
        }

        args, kwargs = self.audit_log.call_args_list[0]
        assert args[0] == 'AuthorizeByToken'
        assert kwargs['extra'] == {
            'request-id': 'a823a206-95a0-4666-b464-93b9f0606d7b',
            'http.status': 200,
            'request.service': 'myservice',
            'request.permit': format_json({
                'LaunchRocket': ['arn:myservice:rockets/thrift'],
            }),
            'request.actions': ['myservice:LaunchRocket'],
            'request.resources': ['arn:myservice:rockets/thrift'],
            'request.headers': ['Authorization: ** NOT LOGGED **'],
            'request.context': {},
            'response.authorized': False,
            # 'response.identity': 'charles',
            'response.permitted': format_json({}),
            'response.not-permitted': format_json({'LaunchRocket': ['arn:myservice:rockets/thrift']}),
        }


class TestCaseLogin(base.TestCase):

    def test_authorize_service(self):
        policy = UserPolicy(name='myserver', user=self.user, policy={
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'myservice:*',
                'Resource': '*',
                'Effect': 'Allow',
            }]
        })
        db.session.add(policy)

        db.session.commit()

        response = self.client.post(
            '/api/v1/authorize-login',
            data=json.dumps({
                'action': 'myservice:LaunchRocket',
                'resource': 'arn:myservice:rockets/thrift',
                'headers': [
                    ('Authorization', 'Basic {}'.format(
                        base64.b64encode(b'charles:mrfluffy').decode('utf-8')))
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
        assert json.loads(response.get_data(as_text=True)) == {'Authorized': True, 'Identity': 'charles'}

        args, kwargs = self.audit_log.call_args_list[0]
        assert args[0] == 'AuthorizeByLogin'
        assert kwargs['extra'] == {
            'request-id': 'a823a206-95a0-4666-b464-93b9f0606d7b',
            'http.status': 200,
            'request.permit': format_json({
                'myservice:LaunchRocket': ['arn:myservice:rockets/thrift']
            }),
            'request.actions': ['myservice:LaunchRocket'],
            'request.resources': ['arn:myservice:rockets/thrift'],
            'request.headers': ['Authorization: ** NOT LOGGED **'],
            'request.context': {},
            'response.authorized': True,
            'response.identity': 'charles',
        }

    def test_authorize_service_failure(self):
        policy = UserPolicy(name='myserver', user=self.user, policy={
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'myservice:*',
                'Resource': '*',
                'Effect': 'Deny',
            }]
        })
        db.session.add(policy)

        db.session.commit()

        response = self.client.post(
            '/api/v1/authorize-login',
            data=json.dumps({
                'action': 'myservice:LaunchRocket',
                'resource': 'arn:myservice:rockets/thrift',
                'headers': [
                    ('Authorization', 'Basic {}'.format(
                        base64.b64encode(b'charles:mrfluffy').decode('utf-8')))
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
            'Status': 403
        }

        args, kwargs = self.audit_log.call_args_list[0]
        assert args[0] == 'AuthorizeByLogin'
        assert kwargs['extra'] == {
            'request-id': 'a823a206-95a0-4666-b464-93b9f0606d7b',
            'http.status': 200,
            'request.permit': format_json({
                'myservice:LaunchRocket': ['arn:myservice:rockets/thrift']
            }),
            'request.actions': ['myservice:LaunchRocket'],
            'request.resources': ['arn:myservice:rockets/thrift'],
            'request.headers': ['Authorization: ** NOT LOGGED **'],
            'request.context': {},
            'response.authorized': False,
        }


class TestCaseLoginToToken(base.TestCase):

    def test_authorize_service(self):
        policy = UserPolicy(name='myserver', user=self.user, policy={
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'myservice:*',
                'Resource': '*',
                'Effect': 'Allow',
            }]
        })
        db.session.add(policy)

        db.session.commit()

        response = self.client.post(
            '/api/v1/services/myservice/get-token-for-login',
            data=json.dumps({
                'username': 'charles',
                'password': 'mrfluffy',
                'csrf-strategy': 'header-token',
            }),
            headers={
                'Authorization': 'Basic {}'.format(
                    base64.b64encode(b'AKIDEXAMPLE:password').decode('utf-8')
                )
            },
            content_type='application/json',
        )
        assert response.status_code == 200
        payload = json.loads(response.get_data(as_text=True))
        assert 'token' in payload
        assert 'csrf' in payload

        args, kwargs = self.audit_log.call_args_list[0]
        assert args[0] == 'GetTokenForLogin'
        assert kwargs['extra'] == {
            'request-id': 'a823a206-95a0-4666-b464-93b9f0606d7b',
            'http.status': 200,
            'request.service': 'myservice',
            'request.username': 'charles',
            'request.csrf-strategy': 'header-token',
        }

    def test_authorize_service_failure(self):
        policy = UserPolicy(name='myserver', user=self.user, policy={
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'myservice:*',
                'Resource': '*',
                'Effect': 'Deny',
            }]
        })
        db.session.add(policy)

        db.session.commit()

        response = self.client.post(
            '/api/v1/services/myservice/get-token-for-login',
            data=json.dumps({
                'username': 'charles',
                'password': 'password',
                'csrf-strategy': 'header-token',
            }),
            headers={
                'Authorization': 'Basic {}'.format(
                    base64.b64encode(b'AKIDEXAMPLE:password').decode('utf-8')
                )
            },
            content_type='application/json',
        )
        assert response.status_code == 401
        assert json.loads(response.get_data(as_text=True)) == {
            'errors': {'authentication': 'Invalid credentials'}
        }

        args, kwargs = self.audit_log.call_args_list[0]
        assert args[0] == 'GetTokenForLogin'
        assert kwargs['extra'] == {
            'request-id': 'a823a206-95a0-4666-b464-93b9f0606d7b',
            'http.status': 401,
            'request.service': 'myservice',
            'errors': {'authentication': 'Invalid credentials'},
            'request.username': 'charles',
            'request.csrf-strategy': 'header-token',
        }
