import json
import boto3

from app.config import get_settings
from app.exceptions import AIServiceException
from app.services.embedding_service import BaseEmbeddingService


class BedrockEmbeddingService(BaseEmbeddingService):
    """
    Uses Amazon Titan embedding model in production.
    """
    def __init__(self):
        settings = get_settings()

        session = boto3.session.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_session_token=settings.AWS_SESSION_TOKEN,
            region_name=settings.AWS_REGION,
        )

        self.client = session.client("bedrock-runtime")
        self._model = settings.BEDROCK_EMBEDDING_MODEL_ID

    def model_name(self) -> str:
        return self._model

    def _embed_single(self, text: str) -> list[float]:
        try:
            body = {
                "inputText": text
            }

            response = self.client.invoke_model(
                modelId=self._model,
                body=json.dumps(body),
                contentType="application/json",
                accept="application/json",
            )

            payload = json.loads(response["body"].read())
            embedding = payload.get("embedding")
            if not embedding:
                raise AIServiceException("Bedrock embedding response missing 'embedding'")
            return embedding
        except Exception as exc:
            raise AIServiceException(f"Bedrock embedding failed: {str(exc)}") from exc

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_single(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed_single(text)