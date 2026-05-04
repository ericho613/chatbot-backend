from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.dependencies import optional_jwt_auth
from app.models import ChatRequest, ChatResponse
from app.services.factory import get_ai_service
from app.utils.streaming import json_line_stream

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def basic_chat(
    request: ChatRequest,
    _user=Depends(optional_jwt_auth),
):
    ai_service = get_ai_service()

    if request.stream:
        generator = ai_service.stream_text(request.messages, request.generation_config)
        return StreamingResponse(
            json_line_stream(generator),
            media_type="application/x-ndjson",
        )

    text = await ai_service.generate_text(request.messages, request.generation_config)

    return ChatResponse(
        success=True,
        model=ai_service.model_name(),
        response=text,
    )