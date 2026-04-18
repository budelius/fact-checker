from uuid import UUID

from pymongo import MongoClient

from app.schemas.entities import KnowledgeEntity
from app.schemas.relationships import KnowledgeRelationship


class MongoRepository:
    entity_collection_name = "entities"
    relationship_collection_name = "relationships"
    annotation_collection_name = "annotations"
    ingestion_job_collection_name = "ingestion_jobs"
    pipeline_event_collection_name = "pipeline_events"

    def __init__(self, client: MongoClient, database_name: str) -> None:
        self.database = client[database_name]

    @property
    def entities(self):
        return self.database[self.entity_collection_name]

    @property
    def relationships(self):
        return self.database[self.relationship_collection_name]

    @property
    def annotations(self):
        return self.database[self.annotation_collection_name]

    @property
    def ingestion_jobs(self):
        return self.database[self.ingestion_job_collection_name]

    @property
    def pipeline_events(self):
        return self.database[self.pipeline_event_collection_name]

    def upsert_entity(self, entity: KnowledgeEntity) -> None:
        document = entity.model_dump(mode="json")
        self.entities.update_one({"uuid": str(entity.uuid)}, {"$set": document}, upsert=True)

    def upsert_relationship(self, relationship: KnowledgeRelationship) -> None:
        document = relationship.model_dump(mode="json")
        self.relationships.update_one(
            {"uuid": str(relationship.uuid)},
            {"$set": document},
            upsert=True,
        )

    def get_entity(self, uuid: UUID) -> dict | None:
        return self.entities.find_one({"uuid": str(uuid)}, {"_id": False})

    def list_entities(self, entity_type: str | None = None) -> list[dict]:
        query = {"entity_type": entity_type} if entity_type else {}
        return list(self.entities.find(query, {"_id": False}))

    def list_relationships(
        self,
        source_uuid: UUID | None = None,
        target_uuid: UUID | None = None,
    ) -> list[dict]:
        if source_uuid and target_uuid:
            query = {
                "$or": [
                    {"source_uuid": str(source_uuid)},
                    {"target_uuid": str(target_uuid)},
                ]
            }
        elif source_uuid:
            query = {"source_uuid": str(source_uuid)}
        elif target_uuid:
            query = {"target_uuid": str(target_uuid)}
        else:
            query = {}
        return list(self.relationships.find(query, {"_id": False}))

    def upsert_annotation(self, annotation: dict) -> None:
        self.annotations.update_one(
            {"uuid": str(annotation["uuid"])},
            {"$set": annotation},
            upsert=True,
        )

    def list_annotations(self, target_entity_uuid: UUID) -> list[dict]:
        return list(
            self.annotations.find(
                {"target_entity_uuid": str(target_entity_uuid)},
                {"_id": False},
            )
        )
