from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt

from app.config import get_settings
from app.exceptions import AuthenticationException


def create_access_token(subject: str, expires_minutes: Optional[int] = None) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.JWT_EXPIRE_MINUTES
    )

    payload = {
        "sub": subject,
        "iat": datetime.now(timezone.utc),
        "exp": expire,
    }

    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def verify_token(token: str) -> dict:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as exc:
        raise AuthenticationException("Invalid or expired token") from exc