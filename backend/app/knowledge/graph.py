from collections import Counter, defaultdict
from uuid import UUID

from app.schemas.entities import EntityType
from app.schemas.knowledge import KnowledgeGraphEdge, KnowledgeGraphNode, KnowledgeGraphResponse


def _entity_map(repository) -> dict[str, dict]:
    if repository is None or not hasattr(repository, "list_entities"):
        return {}
    return {str(entity["uuid"]): entity for entity in repository.list_entities()}


def _relationships_for(repository, entity_uuid: UUID) -> list[dict]:
    if repository is None or not hasattr(repository, "list_relationships"):
        return []
    return repository.list_relationships(source_uuid=entity_uuid, target_uuid=entity_uuid)


def _node(entity_uuid: str, entities: dict[str, dict], degree: int) -> KnowledgeGraphNode:
    entity = entities.get(entity_uuid) or {}
    entity_type = EntityType(str(entity.get("entity_type") or "topic"))
    return KnowledgeGraphNode(
        uuid=UUID(entity_uuid),
        entity_type=entity_type,
        title=str(entity.get("title") or entity.get("slug") or entity_uuid),
        vault_path=entity.get("vault_path"),
        degree=degree,
    )


def build_entity_graph(entity_uuid: UUID, repository, depth: int = 1) -> KnowledgeGraphResponse:
    entities = _entity_map(repository)
    relationships = _relationships_for(repository, entity_uuid)
    seen_relationships = {str(relationship["uuid"]): relationship for relationship in relationships}

    if depth > 1:
        neighbor_ids = {
            str(relationship["target_uuid"])
            if str(relationship["source_uuid"]) == str(entity_uuid)
            else str(relationship["source_uuid"])
            for relationship in relationships
        }
        for neighbor_id in neighbor_ids:
            for relationship in _relationships_for(repository, UUID(neighbor_id)):
                seen_relationships.setdefault(str(relationship["uuid"]), relationship)

    degree_counts: Counter[str] = Counter()
    edges = []
    for relationship in seen_relationships.values():
        source_uuid = str(relationship["source_uuid"])
        target_uuid = str(relationship["target_uuid"])
        degree_counts[source_uuid] += 1
        degree_counts[target_uuid] += 1
        if source_uuid == str(entity_uuid):
            direction = "outgoing"
        elif target_uuid == str(entity_uuid):
            direction = "incoming"
        else:
            direction = "related"
        edges.append(
            KnowledgeGraphEdge(
                uuid=relationship["uuid"],
                relationship_type=str(relationship["relationship_type"]),
                source_uuid=relationship["source_uuid"],
                target_uuid=relationship["target_uuid"],
                provenance=str(relationship.get("provenance") or ""),
                direction=direction,
            )
        )

    node_ids = set(degree_counts)
    node_ids.add(str(entity_uuid))
    nodes = [_node(node_id, entities, degree_counts[node_id]) for node_id in sorted(node_ids)]

    clusters: dict[str, list[UUID]] = defaultdict(list)
    for node in nodes:
        clusters[node.entity_type.value].append(node.uuid)

    important_nodes = sorted(nodes, key=lambda node: node.degree, reverse=True)[:3]
    return KnowledgeGraphResponse(
        selected_uuid=entity_uuid,
        nodes=nodes,
        edges=edges,
        important_nodes=important_nodes,
        clusters=dict(clusters),
    )
