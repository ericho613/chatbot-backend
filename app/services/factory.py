from app.config import get_settings
from app.services.openai_service import OpenAIService
from app.services.bedrock_service import BedrockService
from app.services.openai_embedding_service import OpenAIEmbeddingService
from app.services.bedrock_embedding_service import BedrockEmbeddingService
from app.services.chroma_store import ChromaVectorStore
from app.services.s3_vectors_store import S3VectorsStore


def get_ai_service():
    settings = get_settings()
    if settings.is_production:
        return BedrockService()
    return OpenAIService()


def get_embedding_service():
    settings = get_settings()
    if settings.is_production:
        return BedrockEmbeddingService()
    return OpenAIEmbeddingService()


def get_vector_store():
    settings = get_settings()
    if settings.is_production:
        return S3VectorsStore()
    return ChromaVectorStore()