from abc import ABC, abstractmethod
from typing import AsyncGenerator
from app.models import ChatMessage, GenerationConfig


class BaseAIService(ABC):
    @abstractmethod
    async def generate_text(
        self,
        messages: list[ChatMessage],
        generation_config: GenerationConfig,
    ) -> str:
        pass

    @abstractmethod
    async def stream_text(
        self,
        messages: list[ChatMessage],
        generation_config: GenerationConfig,
    ) -> AsyncGenerator[str, None]:
        pass

    @abstractmethod
    def model_name(self) -> str:
        pass