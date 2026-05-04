import json
import uuid
import boto3

from app.config import get_settings
from app.exceptions import VectorStoreException
from app.services.vector_store import BaseVectorStore


class S3VectorsStore(BaseVectorStore):
    """
    Production adapter for Amazon S3 Vectors.

    IMPORTANT:
    Replace the marked TODO sections with the exact API operations supported
    in your AWS account / boto3 version for S3 vector indexes.
    """
    def __init__(self):
        settings = get_settings()

        if not settings.S3_VECTORS_BUCKET:
            raise VectorStoreException("S3_VECTORS_BUCKET is not configured")
        if not settings.S3_VECTORS_INDEX_NAME:
            raise VectorStoreException("S3_VECTORS_INDEX_NAME is not configured")

        self.bucket = settings.S3_VECTORS_BUCKET
        self.index_name = settings.S3_VECTORS_INDEX_NAME
        self.region = settings.S3_VECTORS_REGION or settings.AWS_REGION

        session = boto3.session.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_session_token=settings.AWS_SESSION_TOKEN,
            region_name=self.region,
        )

        # Placeholder until exact S3 vector client is available in your environment.
        self.s3_client = session.client("s3")

        # Fallback metadata storage location for debugging / temporary persistence.
        self.metadata_prefix = f"vector-index-debug/{self.index_name}/"

    def backend_name(self) -> str:
        return "amazon-s3-vectors"

    def add_document_chunks(
        self,
        filename: str,
        chunks: list[str],
        embeddings: list[list[float]],
        citation: str
    ) -> int:
        try:
            if len(chunks) != len(embeddings):
                raise VectorStoreException("Chunks and embeddings length mismatch")

            # TODO:
            # Replace with actual AWS S3 Vector upsert API calls.
            #
            # Pseudo-example:
            # vector_records = [
            #   {
            #      "id": str(uuid.uuid4()),
            #      "vector": embedding,
            #      "metadata": {"filename": filename, "text": chunk}
            #   }
            #   for chunk, embedding in zip(chunks, embeddings)
            # ]
            # s3vectors_client.put_vectors(bucket=..., indexName=..., vectors=vector_records)

            # Temporary debug persistence so uploads are not silently lost during integration.
            for chunk, embedding in zip(chunks, embeddings):
                key = f"{self.metadata_prefix}{uuid.uuid4()}.json"
                record = {
                    "filename": filename,
                    "text": chunk,
                    "embedding": embedding,
                    "citation": citation
                }
                self.s3_client.put_object(
                    Bucket=self.bucket,
                    Key=key,
                    Body=json.dumps(record).encode("utf-8"),
                    ContentType="application/json",
                )

            return len(chunks)
        except Exception as exc:
            raise VectorStoreException(f"S3 Vectors add failed: {str(exc)}") from exc

    def search(self, query_embedding: list[float], top_k: int = 5) -> list[str]:
        try:
            # TODO:
            # Replace with actual AWS S3 Vector similarity search API call.
            #
            # Pseudo-example:
            # results = s3vectors_client.query_vectors(
            #    bucket=...,
            #    indexName=...,
            #    queryVector=query_embedding,
            #    topK=top_k
            # )
            # return [item["metadata"]["text"] for item in results["matches"]]

            # Temporary fallback:
            # Read a subset of debug objects and compute naive cosine similarity in application memory.
            # This keeps the production adapter demonstrable until exact S3 Vector APIs are plugged in.
            listing = self.s3_client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=self.metadata_prefix,
                MaxKeys=1000,
            )

            objects = listing.get("Contents", [])
            if not objects:
                return []

            candidates = []
            for obj in objects:
                body = self.s3_client.get_object(Bucket=self.bucket, Key=obj["Key"])["Body"].read()
                record = json.loads(body.decode("utf-8"))
                score = self._cosine_similarity(query_embedding, record["embedding"])
                candidates.append((score, record["text"]))

            candidates.sort(key=lambda x: x[0], reverse=True)
            return [text for _, text in candidates[:top_k]]
        except Exception as exc:
            raise VectorStoreException(f"S3 Vectors search failed: {str(exc)}") from exc

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        if not a or not b or len(a) != len(b):
            return -1.0

        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(y * y for y in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return -1.0

        return dot / (norm_a * norm_b)