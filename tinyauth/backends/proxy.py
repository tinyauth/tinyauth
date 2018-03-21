import base64
import datetime

import requests
from flask import current_app

from tinyauth.utils.cache import cache


class Backend(object):

    def __init__(self):
        self.session = requests.Session()

    @cache()
    def get_policies(self, region, service, username):
        endpoint = current_app.config['TINYAUTH_ENDPOINT']
        uri = f'/api/v1/regions/{region}/services/{service}/user-policies/{username}'

        response = self.session.get(
            f'{endpoint}{uri}',
            auth=(
                current_app.config['TINYAUTH_ACCESS_KEY_ID'],
                current_app.config['TINYAUTH_SECRET_ACCESS_KEY'],
            ),
            headers={
                'Accept': 'application/json',
            },
            verify=current_app.config.get('TINYAUTH_VERIFY', True),
        )

        expires = datetime.datetime.strptime(response.headers['Expires'], '%a, %d %b %Y %H:%M:%S GMT')

        return expires, response.json()

    @cache()
    def get_user_key(self, protocol, region, service, date, username):
        endpoint = current_app.config['TINYAUTH_ENDPOINT']
        token_id = '/'.join((
            username,
            protocol,
            date.strftime('%Y%m%d'),
        ))
        uri = f'/api/v1/regions/{region}/services/{service}/user-signing-tokens/{token_id}'

        response = self.session.get(
            f'{endpoint}{uri}',
            auth=(
                current_app.config['TINYAUTH_ACCESS_KEY_ID'],
                current_app.config['TINYAUTH_SECRET_ACCESS_KEY'],
            ),
            headers={
                'Accept': 'application/json',
            },
            verify=current_app.config.get('TINYAUTH_VERIFY', True),
        )

        expires = datetime.datetime.strptime(response.headers['Expires'], '%a, %d %b %Y %H:%M:%S GMT')

        token = response.json()
        token['key'] = base64.b64decode(token['key'])
        return expires, token

    @cache()
    def get_access_key(self, protocol, region, service, date, access_key_id):
        endpoint = current_app.config['TINYAUTH_ENDPOINT']
        token_id = '/'.join((
            access_key_id,
            protocol,
            date.strftime('%Y%m%d'),
        ))
        uri = f'/api/v1/regions/{region}/services/{service}/access-key-signing-tokens/{token_id}'

        response = self.session.get(
            f'{endpoint}{uri}',
            auth=(
                current_app.config['TINYAUTH_ACCESS_KEY_ID'],
                current_app.config['TINYAUTH_SECRET_ACCESS_KEY'],
            ),
            headers={
                'Accept': 'application/json',
            },
            verify=current_app.config.get('TINYAUTH_VERIFY', True),
        )

        expires = datetime.datetime.strptime(response.headers['Expires'], '%a, %d %b %Y %H:%M:%S GMT')

        token = response.json()
        token['key'] = base64.b64decode(token['key'])
        return expires, token
