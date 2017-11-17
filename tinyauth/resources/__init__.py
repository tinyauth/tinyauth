from .access_key import access_key_blueprint
from .user import user_blueprint
from .user_policy import user_policy_blueprint
from .group import group_blueprint
from .service import service_blueprint

__all__ = [
    'access_key_blueprint',
    'user_blueprint',
    'user_policy_blueprint',
    'group_blueprint',
    'service_blueprint',
]
