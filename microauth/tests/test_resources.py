import base64
import json
import unittest

from microauth.app import app, db


class TestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_get_keys_no_keys(self):
        response = self.client.get('/api/v1/users')
        assert response.status_code == 200
        assert response.get_data(as_text=True) == '[]\n'
        assert b''.join(response.response) == b'[]\n'
