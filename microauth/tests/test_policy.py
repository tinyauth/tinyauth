import unittest

from microauth.policy import allow


class TestSimplePolicy(unittest.TestCase):

    policy = {
        'Version': '2012-10-17',
        'Statement': [{
            'Action': 'myservice:ListInstances',
            'Resource': 'arn::myservice:::instances/foo_*',
            'Effect': 'Allow',
        }, {
            'Action': 'myservice:ListInstances',
            'Resource': 'arn::myservice:::instances/foo_bar_*',
            'Effect': 'Deny',
        }]
    }

    def test_simple_policy_default_deny(self):
        assert allow(
            self.policy,
            'myservice:GetInstance',
            'arn::myservice:::instances/foo_baz_1',
        ) == "Default"

    def test_simple_policy_allow(self):
        assert allow(
            self.policy,
            'myservice:ListInstances',
            'arn::myservice:::instances/foo_baz_1',
        ) == "Allow"

    def test_simple_policy_deny(self):
        assert allow(
            self.policy,
            'myservice:ListInstances',
            'arn::myservice:::instances/foo_bar_1',
        ) == "Deny"


class TestPolicyConditions(unittest.TestCase):

    def test_ip_address_allow(self):
        policy = {
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'myservice:ListInstances',
                'Resource': 'arn::myservice:::instances/foo_*',
                'Condition': {
                    'IpAddress': {'SourceIp': '127.0.0.0/24'}
                },
                'Effect': 'Allow',
            }]
        }

        assert allow(
            policy,
            'myservice:ListInstances',
            'arn::myservice:::instances/foo_1',
            context={
                'SourceIp': '127.0.0.1',
            }
        ) == "Allow"

    def test_ip_address_deny(self):
        policy = {
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'myservice:ListInstances',
                'Resource': 'arn::myservice:::instances/foo_*',
                'Condition': {
                    'IpAddress': {'SourceIp': '127.0.0.0/24'}
                },
                'Effect': 'Allow',
            }]
        }

        assert allow(
            policy,
            'myservice:ListInstances',
            'arn::myservice:::instances/foo_1',
            context={
                'SourceIp': '192.168.0.1',
            }
        ) == "Default"

    def test_not_ip_address_allow(self):
        policy = {
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'myservice:ListInstances',
                'Resource': 'arn::myservice:::instances/foo_*',
                'Condition': {
                    'NotIpAddress': {'SourceIp': '127.0.0.0/24'}
                },
                'Effect': 'Allow',
            }]
        }

        assert allow(
            policy,
            'myservice:ListInstances',
            'arn::myservice:::instances/foo_1',
            context={
                'SourceIp': '192.168.0.1',
            }
        ) == "Allow"

    def test_not_ip_address_deny(self):
        policy = {
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'myservice:ListInstances',
                'Resource': 'arn::myservice:::instances/foo_*',
                'Condition': {
                    'NotIpAddress': {'SourceIp': '127.0.0.0/24'}
                },
                'Effect': 'Allow',
            }]
        }

        assert allow(
            policy,
            'myservice:ListInstances',
            'arn::myservice:::instances/foo_1',
            context={
                'SourceIp': '127.0.0.1',
            }
        ) == "Default"
