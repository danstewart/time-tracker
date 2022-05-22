from app.controllers.user.exceptions import TokenNotFound


def create_token(payload: dict, timeout: int = 3600) -> str:
    """
    Generates a cryptographically secure token and stores the `payload` JSON encoded in the redis session
    The token is then returned

    This is designed to be used to send email verification or password reset links
    The email includes the token then we fetch out the payload to verify the user

    `payload`
        A JSON encodable dictionary to store in the session attached to the token
    `timeout`
        The number of seconds the token is valid for
    """
    import json
    import secrets

    from app.lib.redis import session

    token = secrets.token_hex()
    token_key = "token:{}".format(token)

    session.set(token_key, json.dumps(payload))
    session.expire(token_key, timeout)
    return token


def parse_token(token: str) -> dict:
    """
    Looks up a token from the redis session
    If it exists then the payload is returned

    If not found then a TokenNotFound exception is raised
    """
    import json

    from app.lib.redis import session

    if payload := session.get(f"token:{token}"):
        return json.loads(payload.decode("utf-8"))
    raise TokenNotFound(f"Could not find session value for token:{token}")
