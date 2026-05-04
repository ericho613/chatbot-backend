import uuid
import chromadb

from app.config import get_settings
from app.exceptions import VectorStoreException
from app.services.vector_store import BaseVectorStore


class ChromaVectorStore(BaseVectorStore):
    def __init__(self):
        settings = get_settings()
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        self.collection = self.client.get_or_create_collection(name=settings.CHROMA_COLLECTION_NAME)

    def backend_name(self) -> str:
        return "chroma"

    def add_document_chunks(
        self,
        filename: str,
        chunks: list[str],
        embeddings: list[list[float]],
        citation: str
    ) -> int:
        try:
            ids = [str(uuid.uuid4()) for _ in chunks]
            metadatas = [{"filename": filename, "citation": citation} for _ in chunks]

            self.collection.add(
                ids=ids,
                documents=chunks,
                embeddings=embeddings,
                metadatas=metadatas,
            )
            return len(chunks)
        except Exception as exc:
            raise VectorStoreException(f"Chroma add failed: {str(exc)}") from exc

    def search(self, query_embedding: list[float], top_k: int = 5) -> list[str]:
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
            )
            # return results.get("documents", [[]])[0]

            combinedDocsAndMetadatas = [{"document": document, "metadata": metadata } for document, metadata in zip(results.get("documents", [[]])[0], results.get("metadatas", [[]])[0])]
            print(combinedDocsAndMetadatas)
            return combinedDocsAndMetadatas

        except Exception as exc:
            raise VectorStoreException(f"Chroma search failed: {str(exc)}") from exc