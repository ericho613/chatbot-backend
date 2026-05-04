from abc import ABC, abstractmethod


class BaseVectorStore(ABC):
    @abstractmethod
    def backend_name(self) -> str:
        pass

    @abstractmethod
    def add_document_chunks(
        self,
        filename: str,
        chunks: list[str],
        embeddings: list[list[float]],
        citation: str
    ) -> int:
        pass

    @abstractmethod
    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[str]:
        pass