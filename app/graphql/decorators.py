from functools import wraps
from flask_jwt_extended import (
    verify_jwt_in_request, current_user
)
from flask_jwt_extended.exceptions import NoAuthorizationError


def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            if not current_user.is_admin:
                raise NoAuthorizationError('insufficient permission')
            return fn(*args, **kwargs)

        return decorator

    return wrapper
