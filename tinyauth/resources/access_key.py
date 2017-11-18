import random
import string

from flask import Blueprint, jsonify, make_response, request
from flask_restful import Api, Resource, abort, fields, marshal

from tinyauth.app import db
from tinyauth.authorize import internal_authorize
from tinyauth.models import AccessKey
from tinyauth.simplerest import build_response_for_request

ACCESS_KEY_ID_LETTERS = string.ascii_uppercase + string.digits
SECRET_ACCESS_KEY_LETTERS = string.ascii_uppercase + string.ascii_lowercase + string.digits


access_key_fields = {
    'id': fields.Integer,
    'access_key_id': fields.String,
}

access_key_fields__initial = {
    'id': fields.Integer,
    'access_key_id': fields.String,
    'secret_access_key': fields.String,
}


access_key_blueprint = Blueprint('access_key', __name__)


class AccessKeyResource(Resource):

    def _get_or_404(self, user_id, key_id):
        policy = AccessKey.query.filter(AccessKey.user_id == user_id, AccessKey.id == key_id).first()
        if not policy:
            abort(404, message=f'Policy {key_id} for user {user_id} does not exist')
        return policy

    def get(self, user_id, key_id):
        internal_authorize('GetAccessKey', f'arn:tinyauth:users/{user_id}')

        policy = self._get_or_404(user_id, key_id)
        return jsonify(marshal(policy, access_key_fields))

    def delete(self, user_id, key_id):
        internal_authorize('DeleteAccessKey', f'arn:tinyauth:users/{user_id}')

        policy = self._get_or_404(user_id, key_id)
        db.session.delete(policy)

        return make_response(jsonify({}), 201, [])


class AccessKeysResource(Resource):

    def get(self, user_id):
        internal_authorize('ListAccessKeys', f'arn:tinyauth:users/')

        return build_response_for_request(
            AccessKey,
            request,
            access_key_fields,
            AccessKey.query.filter(AccessKey.user_id == user_id),
        )

    def post(self, user_id):
        internal_authorize('CreateAccessKey', f'arn:tinyauth:users/{user_id}')

        access_key = AccessKey(
            user_id=user_id,
            access_key_id='AK' + ''.join(random.SystemRandom().choice(ACCESS_KEY_ID_LETTERS) for _ in range(18)),
            secret_access_key=''.join(random.SystemRandom().choice(SECRET_ACCESS_KEY_LETTERS) for _ in range(40)),
        )

        db.session.add(access_key)
        db.session.commit()

        return jsonify(marshal(access_key, access_key_fields__initial))


access_key_api = Api(access_key_blueprint, prefix='/api/v1')
access_key_api.add_resource(AccessKeysResource, '/users/<user_id>/keys')
access_key_api.add_resource(AccessKeyResource, '/users/<user_id>/keys/<key_id>')
