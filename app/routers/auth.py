from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.models import TokenRequest, TokenResponse
from app.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=TokenResponse)
async def create_token(request: TokenRequest):
    settings = get_settings()

    if request.username != settings.DEMO_AUTH_USERNAME or request.password != settings.DEMO_AUTH_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token(subject=request.username)
    return TokenResponse(access_token=token)