from openai import OpenAI

from app.config import get_settings
from app.exceptions import AIServiceException
from app.services.embedding_service import BaseEmbeddingService


class OpenAIEmbeddingService(BaseEmbeddingService):
    def __init__(self):
        settings = get_settings()
        if not settings.OPENAI_API_KEY:
            raise AIServiceException("OPENAI_API_KEY is not configured")
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self._model = settings.OPENAI_EMBEDDING_MODEL

    def model_name(self) -> str:
        return self._model

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        try:
            response = self.client.embeddings.create(
                model=self._model,
                input=texts,
            )
            return [item.embedding for item in response.data]
        except Exception as exc:
            raise AIServiceException(f"OpenAI embeddings failed: {str(exc)}") from exc

    def embed_query(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]