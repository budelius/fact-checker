from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.schemas.vector_payloads import QdrantPayload


class QdrantRepository:
    def __init__(self, url: str, collection_name: str) -> None:
        self.client = QdrantClient(url=url)
        self.collection_name = collection_name

    def ensure_collection(self, vector_size: int) -> None:
        if self.client.collection_exists(self.collection_name):
            return

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )

    def upsert_payload(self, payload: QdrantPayload, vector: list[float]) -> None:
        point = PointStruct(
            id=str(payload.uuid),
            vector=vector,
            payload=payload.model_dump(mode="json"),
        )
        self.client.upsert(collection_name=self.collection_name, points=[point])
