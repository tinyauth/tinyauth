from .base import TestCase


class TestRequestIdMiddleware(TestCase):

    def test_issue_request_id(self):
        response = self.client.get(
            '/api/v1/404',
        )

        assert response.status_code == 404

        # Our default X-Request-Id is a 36 byte string with 4 '-' and made up of hex values
        assert len(response.headers['X-Request-Id']) == 36
        assert response.headers['X-Request-Id'].count('-') == 4
        assert set('abcdefgh0123456789-').issuperset(set(response.headers['X-Request-Id']))

    def test_reuse_request_id(self):
        response = self.client.get(
            '/api/v1/404',
            headers={
                'X-Request-Id': 'deadbeef-feedbee5-deadbeef-feedbee5',
            }
        )

        assert response.status_code == 404
        assert response.headers['X-Request-Id'] == 'deadbeef-feedbee5-deadbeef-feedbee5'
