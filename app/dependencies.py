from fastapi import Header

from app.config import get_settings
from app.exceptions import AuthenticationException
from app.security import verify_token


async def optional_jwt_auth(authorization: str | None = Header(default=None)) -> dict | None:
    settings = get_settings()

    if not settings.ENABLE_JWT_AUTH:
        return None

    if not authorization:
        raise AuthenticationException("Missing Authorization header")

    if not authorization.startswith("Bearer "):
        raise AuthenticationException("Authorization header must use Bearer token")

    token = authorization.replace("Bearer ", "", 1).strip()
    if not token:
        raise AuthenticationException("Missing bearer token")

    return verify_token(token)