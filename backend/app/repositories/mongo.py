from uuid import UUID

from pymongo import MongoClient

from app.schemas.entities import KnowledgeEntity
from app.schemas.relationships import KnowledgeRelationship


class MongoRepository:
    entity_collection_name = "entities"
    relationship_collection_name = "relationships"

    def __init__(self, client: MongoClient, database_name: str) -> None:
        self.database = client[database_name]

    @property
    def entities(self):
        return self.database[self.entity_collection_name]

    @property
    def relationships(self):
        return self.database[self.relationship_collection_name]

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
