from ..app import api
from .user import UserResource, UsersResource

from . import service
del service

api.add_resource(UsersResource, '/users')
api.add_resource(UserResource, '/users/<key_id>')
