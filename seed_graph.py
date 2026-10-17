"""Seed the local ContextPilot graph from company_data.json without duplicates."""

import json
from pathlib import Path

from graph_db import get_graph

DATA_PATH = Path(__file__).with_name("company_data.json")
NODE_LABELS = {"people": "Person", "teams": "Team", "projects": "Project", "systems": "System", "tasks": "Task", "documents": "Document", "tickets": "Ticket", "messages": "ChatMessage", "customers": "Customer", "incidents": "Incident"}
RELATIONSHIP_TYPES = {"member_of": "MEMBER_OF", "owns": "OWNS", "leads": "LEADS", "works_on": "WORKS_ON", "part_of": "PART_OF", "depends_on": "DEPENDS_ON", "blocks": "BLOCKS", "relates_to": "RELATES_TO", "uses": "USES", "affected_by": "AFFECTED_BY"}


def seed():
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    graph = get_graph()
    node_count = relationship_count = 0
    for collection, label in NODE_LABELS.items():
        for item in data[collection]:
            graph.query(f"MERGE (n:{label} {{id: $id}}) SET n += $properties", {"id": item["id"], "properties": item})
            node_count += 1
    for relationship_name, pairs in data["relationships"].items():
        for source_id, target_id in pairs:
            graph.query(
                f"MATCH (source {{id: $source_id}}), (target {{id: $target_id}}) MERGE (source)-[:{RELATIONSHIP_TYPES[relationship_name]}]->(target)",
                {"source_id": source_id, "target_id": target_id},
            )
            relationship_count += 1
    graph.query("MERGE (tenant:Tenant {id: 'tenant-northstar'}) SET tenant.name = 'Northstar Commerce' MERGE (risk:Agent {id: 'agent-risk'}) SET risk.name = 'Risk analyst' MERGE (delivery:Agent {id: 'agent-delivery'}) SET delivery.name = 'Delivery coordinator' MERGE (procedure:Procedure {id: 'procedure-triage'}) SET procedure.name = 'Incident triage runbook' MERGE (tenant)-[:USES_PROCEDURE]->(procedure) MERGE (risk)-[:USES_PROCEDURE]->(procedure) MERGE (delivery)-[:USES_PROCEDURE]->(procedure)")
    print(f"Seeded or updated {node_count} nodes and {relationship_count} relationships.")


if __name__ == "__main__":
    seed()
