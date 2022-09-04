class InvalidCSRFToken(Exception):
    """
    Raised when a CSRF token is invalid.
    """

    pass


def generate_csrf_token() -> str:
    """
    Generate a CSRF token and store it in the redis session store.
    The token expires after 5 minutes.
    A new token is generated with each call.

    The token is used as the cache key, the value is the user ID.
    When validating we lookup the key in the cache and verify the value is the current user's ID.
    """
    import secrets

    from app.controllers.user.util import get_user
    from app.lib.redis import session

    user = get_user()
    token = secrets.token_hex()

    csrf_key = f"csrf:{token}"
    session.set(csrf_key, user.id)
    session.expire(csrf_key, 300)  # Expire tokens after 5 minutes

    return token


def validate_csrf_token(token: str):
    """
    Validate a provided CSRF token against the one stored in the `g` store.
    If invalid an `InvalidCSRFToken` exception is raised.
    When a token is validated it is removed from the session.
    """
    from app.controllers.user.util import get_user
    from app.lib.redis import session

    user = get_user()
    cache_value = session.get(f"csrf:{token}")

    if not cache_value:
        raise InvalidCSRFToken("Invalid CSRF token")

    try:
        if int(cache_value.decode("utf-8")) != user.id:
            raise InvalidCSRFToken("Invalid CSRF token")
    except ValueError:
        raise InvalidCSRFToken("Invalid CSRF token")


def enable_csrf_protection(app):

    from werkzeug.datastructures import ImmutableDict

    from app.lib.util.security import validate_csrf_token

    @app.before_request
    def validate():
        from flask import request

        if request.form and "csrf_token" in request.form:
            validate_csrf_token(request.form["csrf_token"])
            form_data = request.form.to_dict()
            form_data.pop("csrf_token")
            request.form = ImmutableDict(form_data)  # type:ignore
