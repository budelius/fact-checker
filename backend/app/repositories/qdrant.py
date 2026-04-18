from uuid import uuid5

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, FieldCondition, Filter, MatchAny, MatchValue, PointStruct, VectorParams

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
        point_id = str(uuid5(payload.uuid, payload.chunk_id))
        point = PointStruct(
            id=point_id,
            vector=vector,
            payload=payload.model_dump(mode="json"),
        )
        self.client.upsert(collection_name=self.collection_name, points=[point])

    def scroll_payloads(self, limit: int = 1000) -> list[dict]:
        if not self.client.collection_exists(self.collection_name):
            return []

        points, _offset = self.client.scroll(
            collection_name=self.collection_name,
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )
        return [point.payload or {} for point in points]

    def search_payloads(
        self,
        query_vector: list[float],
        limit: int = 10,
        entity_types: list[str] | None = None,
        source: str | None = None,
    ) -> list[dict]:
        if not self.client.collection_exists(self.collection_name):
            return []

        conditions = []
        if entity_types:
            conditions.append(
                FieldCondition(
                    key="entity_type",
                    match=MatchAny(any=entity_types),
                )
            )
        if source:
            conditions.append(FieldCondition(key="source", match=MatchValue(value=source)))
        query_filter = Filter(must=conditions) if conditions else None

        if hasattr(self.client, "query_points"):
            response = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                query_filter=query_filter,
                limit=limit,
            )
            points = getattr(response, "points", response)
        else:
            points = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=limit,
            )

        return [
            {"payload": point.payload or {}, "score": getattr(point, "score", None)}
            for point in points
        ]
