from functools import wraps

from config.config import Config
from middleware.tokens import update_tokens


def token_validate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not Config().TOKEN_DICT.get("access_token"):
            raise RuntimeError("Access token is missing")
        else:
            update_tokens()
        return f(*args, **kwargs)
    return decorated_function