from typing import AsyncGenerator
from openai import AsyncOpenAI

from app.config import get_settings
from app.exceptions import AIServiceException
from app.models import ChatMessage, GenerationConfig
from app.services.ai_service import BaseAIService


class OpenAIService(BaseAIService):
    def __init__(self):
        settings = get_settings()
        if not settings.OPENAI_API_KEY:
            raise AIServiceException("OPENAI_API_KEY is not configured")
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self._model = settings.OPENAI_MODEL

    def model_name(self) -> str:
        return self._model

    async def generate_text(
        self,
        messages: list[ChatMessage],
        generation_config: GenerationConfig,
    ) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self._model,
                messages=[{"role": m.role, "content": m.content} for m in messages],
                max_tokens=generation_config.max_tokens,
                temperature=generation_config.temperature,
                top_p=generation_config.top_p,
                stream=False,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            raise AIServiceException(f"OpenAI request failed: {str(exc)}") from exc

    async def stream_text(
        self,
        messages: list[ChatMessage],
        generation_config: GenerationConfig,
    ) -> AsyncGenerator[str, None]:
        try:
            stream = await self.client.chat.completions.create(
                model=self._model,
                messages=[{"role": m.role, "content": m.content} for m in messages],
                max_tokens=generation_config.max_tokens,
                temperature=generation_config.temperature,
                top_p=generation_config.top_p,
                stream=True,
            )

            async for event in stream:
                if event.choices and event.choices[0].delta:
                    token = event.choices[0].delta.content
                    if token:
                        yield token
        except Exception as exc:
            raise AIServiceException(f"OpenAI streaming failed: {str(exc)}") from exc