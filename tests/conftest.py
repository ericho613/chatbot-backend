import io
import json
import pytest
from fastapi.testclient import TestClient
from pypdf import PdfWriter

from app.main import app


class FakeAIService:
    """
    Fake AI service for deterministic tests.
    """
    def model_name(self) -> str:
        return "fake-model"

    async def generate_text(self, messages, generation_config):
        # Return deterministic text based on prompt content
        joined = " ".join([m.content for m in messages])
        if "Summarize" in joined or "summarizes PDF" in joined or "summarize PDF" in joined:
            return "This is a fake summary."
        if "citation" in joined.lower():
            return "Doe, J. (2024). Fake Paper Title. Fake Journal, 1(1), 1-10."
        if "Context:" in joined:
            return "This is a fake RAG response based on retrieved chunks."
        return "This is a fake chat response."

    async def stream_text(self, messages, generation_config):
        chunks = ["fake ", "stream ", "response"]
        for chunk in chunks:
            yield chunk


class FakeEmbeddingService:
    """
    Fake embedding service for deterministic vector tests.
    """
    def model_name(self) -> str:
        return "fake-embedding-model"

    def embed_texts(self, texts):
        return [[0.1, 0.2, 0.3] for _ in texts]

    def embed_query(self, text):
        return [0.1, 0.2, 0.3]


class FakeVectorStore:
    """
    Fake vector store for deterministic indexing and retrieval tests.
    """
    def __init__(self):
        self.docs = []

    def backend_name(self) -> str:
        return "fake-vector-store"

    def add_document_chunks(self, filename, chunks, embeddings, citation):
        for chunk, embedding in zip(chunks, embeddings):
            self.docs.append({
                "filename": filename,
                "text": chunk,
                "embedding": embedding,
                "citation": citation
            })
        return len(chunks)

    def search(self, query_embedding, top_k=5):
        # Return fixed chunks for testing
        return [
            "Chunk 1 about scientific findings.",
            "Chunk 2 with methods and results.",
        ][:top_k]


@pytest.fixture
def fake_vector_store():
    return FakeVectorStore()


@pytest.fixture
def client(monkeypatch, fake_vector_store):
    """
    Create a test client and monkeypatch service factory functions.
    """
    from app.services import factory

    monkeypatch.setattr(factory, "get_ai_service", lambda: FakeAIService())
    monkeypatch.setattr(factory, "get_embedding_service", lambda: FakeEmbeddingService())
    monkeypatch.setattr(factory, "get_vector_store", lambda: fake_vector_store)

    return TestClient(app)


@pytest.fixture
def auth_headers(monkeypatch, client):
    """
    Enable JWT auth during tests and issue a token.
    """
    from app.config import get_settings
    settings = get_settings()

    # Monkeypatch settings for auth-enabled tests
    monkeypatch.setattr(settings, "ENABLE_JWT_AUTH", True, raising=False)
    monkeypatch.setattr(settings, "DEMO_AUTH_USERNAME", "admin", raising=False)
    monkeypatch.setattr(settings, "DEMO_AUTH_PASSWORD", "password", raising=False)

    response = client.post(
        "/auth/token",
        json={"username": "admin", "password": "password"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_pdf_bytes():
    """
    Generate an in-memory PDF with a blank page.
    Note: blank PDFs may extract no text, so tests that depend on actual extraction
    should monkeypatch the PDF text extraction function.
    """
    pdf_buffer = io.BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=300, height=300)
    writer.write(pdf_buffer)
    return pdf_buffer.getvalue()


@pytest.fixture
def mock_pdf_text(monkeypatch):
    """
    Monkeypatch PDF extraction utility to return deterministic text.
    """
    from app.utils import pdf_utils

    monkeypatch.setattr(
        pdf_utils,
        "extract_text_from_pdf_bytes",
        lambda _: "This is a scientific PDF about machine learning, methods, and results."
    )