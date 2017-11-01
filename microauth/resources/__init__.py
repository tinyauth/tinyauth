from ..app import api
from .user import UserResource, UsersResource
from .group import GroupResource, GroupsResource

from . import service
del service

api.add_resource(UsersResource, '/users')
api.add_resource(UserResource, '/users/<user_id>')

api.add_resource(GroupsResource, '/groups')
api.add_resource(GroupResource, '/groups/<group_id>')
