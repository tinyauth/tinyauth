import requests


class Backend(object):

    def __init__(self):
        self.session = requests.Session()

    def get_policy(self, identity):
        policy = self.session.get(
        ).json()

        return policy

    def get_access_key(self, identity):
        policy = self.session.get(
        ).json()

        return policy
