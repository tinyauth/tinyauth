from flask import current_app
from sqlalchemy.orm.exc import NoResultFound

from .. import exceptions
from ..models import AccessKey, User
from ..subkey import make_basic_auth_key, make_jwt_key


class Backend(object):

    def get_policy(self, identity):
        user = ...

        policy = {
            'Statement': []
        }

        for group in user.groups:
            for p in group.policies:
                policy['Statement'].extend(p.policy.get('Statement', []))

        for p in user.policies:
            policy['Statement'].extend(p.policy.get('Statement', []))

        return policy

    def get_user_key(self, protocol, region, service, date, username):
        try:
            User.query.filter(User.username == username).one()
        except NoResultFound:
            raise exceptions.NoSuchKey(identity=username)

        make_key = {
            'jwt': make_jwt_key,
        }[protocol]

        secret = make_key(
            region,
            service,
            date,
            username,
            current_app.config['SECRET_SIGNING_KEY'],
        )

        return {
            'identity': username,
            'key': secret,
        }

    def get_access_key(self, protocol, region, service, date, access_key_id):
        try:
            access_key = AccessKey.query.filter(AccessKey.access_key_id == access_key_id).one()
        except NoResultFound:
            raise exceptions.NoSuchKey(identity=access_key_id)

        make_key = {
            'basic-auth': make_basic_auth_key,
            'jwt': make_jwt_key,
        }[protocol]

        secret = make_key(
            region,
            service,
            date,
            access_key_id,
            access_key.secret_access_key,
        )

        return {
            'identity': access_key.user.username,
            'key': secret,
        }
