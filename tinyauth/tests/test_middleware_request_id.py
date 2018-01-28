from .base import TestCase


class TestRequestIdMiddleware(TestCase):

    def test_issue_request_id(self):
        response = self.client.get(
            '/api/v1/404',
        )

        assert response.status_code == 404
        assert response.headers['X-Request-Id'] == 'a823a206-95a0-4666-b464-93b9f0606d7b'

    def test_reuse_request_id(self):
        response = self.client.get(
            '/api/v1/404',
            headers={
                'X-Request-Id': 'deadbeef-feedbee5-deadbeef-feedbee5',
            }
        )

        assert response.status_code == 404
        assert response.headers['X-Request-Id'] == 'deadbeef-feedbee5-deadbeef-feedbee5'
