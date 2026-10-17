"""A local, explainable graph agent for the ContextPilot demo."""

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from graph_db import get_graph, rows


@dataclass
class AgentResponse:
    answer: str
    sources: list[str]
    trace: list[str]


def format_rows(result):
    return "\n".join("• " + " — ".join(str(value) for value in row) for row in result) or "No matching records found."


def answer(question: str) -> AgentResponse:
    normalized = question.lower().strip()
    if "handoff" in normalized or "open work" in normalized:
        result = rows("MATCH (:Agent)-[:HANDOFF_TO]->(handoff:AgentHandoff)-[:CREATED]->(work:WorkItem {status: 'open'})-[:ASSIGNED_TO]->(owner:Person) OPTIONAL MATCH (work)-[:TRIAGED_FROM]->(incident:Incident) RETURN handoff.from_agent, handoff.to_agent, work.title, owner.name, incident.title ORDER BY handoff.created_at DESC")
        return AgentResponse("Open agent handoffs:\n" + format_rows(result), ["Persistent shared coordination state in FalkorDB."], ["Risk analyst → AgentHandoff → WorkItem → assigned person"])
    if "memory" in normalized or "history" in normalized or "episode" in normalized:
        result = rows("MATCH (:Tenant {id: 'tenant-northstar'})-[:HAS_EPISODE]->(episode:Episode) RETURN episode.question, episode.created_at ORDER BY episode.created_at DESC LIMIT 5")
        return AgentResponse("Recent persistent agent memory:\n" + format_rows(result), ["Episodes are stored in FalkorDB, not only Streamlit session state."], ["Tenant ─HAS_EPISODE→ Episode"])
    if "decision" in normalized or "decisions" in normalized:
        project_name = "Mobile Checkout" if "mobile checkout" in normalized else "Atlas"
        project_id = "project-mobile-checkout" if project_name == "Mobile Checkout" else "project-atlas"
        result = rows(
            "MATCH (owner:Person)-[:MADE]->(decision:Decision)-[:ABOUT]->(project:Project {id: $project_id}) "
            "RETURN decision.title, owner.name, decision.created_at ORDER BY decision.created_at DESC",
            {"project_id": project_id},
        )
        return AgentResponse(
            f"Saved decisions for {project_name}:\n" + format_rows(result),
            ["Decision records are persisted in the ContextPilot graph."],
            ["Person ─MADE→ Decision ─ABOUT→ Project"],
        )
    if "payment" in normalized and any(word in normalized for word in ("own", "owner", "responsible")):
        result = rows("MATCH (person:Person {id: 'person-sarah'})-[:OWNS]->(system:System {id: 'system-payments'}) OPTIONAL MATCH (doc:Document {id: 'doc-payment-ownership'})-[:RELATES_TO]->(system) RETURN person.name, person.role, person.team, doc.title")
        return AgentResponse("Payment Platform ownership:\n" + format_rows([row[:3] for row in result]), [row[3] for row in result if row[3]], ["Person ─OWNS→ System", "Document ─RELATES_TO→ System"])
    if "fraud" not in normalized and any(word in normalized for word in ("block", "blocking", "risk", "impact")):
        result = rows("MATCH (task:Task {id: 'task-tax-contract'})-[:BLOCKS]->(system:System {id: 'system-payments'})<-[:DEPENDS_ON]-(api:System {id: 'system-checkout-api'})<-[:DEPENDS_ON]-(project:Project {id: 'project-mobile-checkout'}) OPTIONAL MATCH (ticket:Ticket {id: 'ticket-atlas-42'})-[:RELATES_TO]->(task) OPTIONAL MATCH (chat:ChatMessage {id: 'chat-checkout-risk'})-[:RELATES_TO]->(task) RETURN task.name, system.name, project.name, ticket.key, chat.channel")
        return AgentResponse("Mobile Checkout is blocked through this dependency path:\n" + format_rows([row[:3] for row in result]), [f"{row[3]}: Finalize tax service contract" for row in result if row[3]] + [f"{row[4]} message from Priya Shah" for row in result if row[4]], ["Mobile Checkout ─DEPENDS_ON→ Checkout API ─DEPENDS_ON→ Payment Platform", "Tax service contract ─BLOCKS→ Payment Platform"])
    if "fraud" in normalized and any(word in normalized for word in ("block", "risk", "impact", "status")):
        result = rows("MATCH (task:Task {id: 'task-fraud-rules'})-[:BLOCKS]->(system:System {id: 'system-fraud'})<-[:DEPENDS_ON]-(project:Project {id: 'project-trust-shield'}) OPTIONAL MATCH (ticket:Ticket {id: 'ticket-trust-12'})-[:RELATES_TO]->(task) OPTIONAL MATCH (doc:Document {id: 'doc-fraud-policy'})-[:RELATES_TO]->(project) RETURN task.name, system.name, project.status, ticket.key, doc.title")
        return AgentResponse("TrustShield risk path:\n" + format_rows([row[:3] for row in result]), [value for row in result for value in (row[3], row[4]) if value], ["TrustShield ─DEPENDS_ON→ Fraud Engine", "Fraud rule review ─BLOCKS→ Fraud Engine"])
    if "incident" in normalized or "customer" in normalized:
        result = rows("MATCH (customer:Customer)-[:AFFECTED_BY]->(incident:Incident)-[:AFFECTED_BY]->(system:System) RETURN customer.name, incident.title, incident.severity, system.name ORDER BY incident.severity")
        return AgentResponse("Customer impact from recorded incidents:\n" + format_rows(result), [], ["Customer ─AFFECTED_BY→ Incident ─AFFECTED_BY→ System"])
    if "atlas" in normalized and any(word in normalized for word in ("task", "show", "work")):
        result = rows("MATCH (person:Person)-[:WORKS_ON]->(task:Task)-[:PART_OF]->(:Project {id: 'project-atlas'}) WHERE person.id STARTS WITH 'person-' RETURN task.name, task.status, person.name ORDER BY task.name")
        return AgentResponse("Atlas tasks:\n" + format_rows(result), [], ["Person ─WORKS_ON→ Task ─PART_OF→ Atlas"])
    if "mobile checkout" in normalized and any(word in normalized for word in ("status", "project", "launch")):
        result = rows("MATCH (project:Project {id: 'project-mobile-checkout'}) OPTIONAL MATCH (lead:Person)-[:LEADS]->(project) OPTIONAL MATCH (doc:Document {id: 'doc-mobile-launch'})-[:RELATES_TO]->(project) RETURN project.status, lead.name, doc.title")
        return AgentResponse("Mobile Checkout status:\n" + format_rows([row[:2] for row in result]), [row[2] for row in result if row[2]], ["Person ─LEADS→ Project", "Document ─RELATES_TO→ Project"])
    if "sarah" in normalized and any(word in normalized for word in ("connect", "relationship", "payment")):
        result = rows("MATCH (sarah:Person {id: 'person-sarah'})-[relationship]->(connected) RETURN type(relationship), labels(connected), connected.name")
        return AgentResponse("Sarah's direct graph connections:\n" + format_rows(result), [], ["Sarah Chen ─[relationship]→ connected node"])
    return AgentResponse("Try a company question, such as **Who owns the payment platform?**, **What is blocking the mobile checkout launch?**, or **Show tasks for the Atlas program**.", [], [])


def record_episode(question: str, response: str) -> str:
    episode_id = f"episode-{uuid4().hex[:8]}"
    get_graph().query("MATCH (tenant:Tenant {id: 'tenant-northstar'}) MERGE (episode:Episode {id: $id}) SET episode.question = $question, episode.response = $response, episode.created_at = $created_at MERGE (tenant)-[:HAS_EPISODE]->(episode)", {"id": episode_id, "question": question[:600], "response": response[:1200], "created_at": datetime.now(timezone.utc).isoformat()})
    return episode_id


def triage_incident(incident_id: str, owner_name: str, priority: str) -> str:
    owners = {"Sarah Chen": "person-sarah", "Priya Shah": "person-priya", "Marcus Lee": "person-marcus", "Amina Yusuf": "person-amina"}
    if incident_id not in {"incident-pay-202", "incident-tax-77"} or owner_name not in owners or priority not in {"P1", "P2", "P3"}:
        raise ValueError("Invalid triage details.")
    work_id, handoff_id = f"work-{uuid4().hex[:8]}", f"handoff-{uuid4().hex[:8]}"
    get_graph().query("MATCH (incident:Incident {id: $incident_id}), (owner:Person {id: $owner_id}), (risk:Agent {id: 'agent-risk'}), (delivery:Agent {id: 'agent-delivery'}), (tenant:Tenant {id: 'tenant-northstar'}) MERGE (work:WorkItem {id: $work_id}) SET work.title = 'Triage: ' + incident.title, work.status = 'open', work.priority = $priority, work.created_at = $created_at MERGE (work)-[:TRIAGED_FROM]->(incident) MERGE (work)-[:ASSIGNED_TO]->(owner) MERGE (tenant)-[:HAS_WORK]->(work) MERGE (handoff:AgentHandoff {id: $handoff_id}) SET handoff.from_agent = 'Risk analyst', handoff.to_agent = 'Delivery coordinator', handoff.created_at = $created_at MERGE (risk)-[:HANDOFF_TO]->(handoff) MERGE (handoff)-[:CREATED]->(work) MERGE (handoff)-[:ROUTED_TO]->(delivery)", {"incident_id": incident_id, "owner_id": owners[owner_name], "work_id": work_id, "handoff_id": handoff_id, "priority": priority, "created_at": datetime.now(timezone.utc).isoformat()})
    return work_id


def record_decision(title: str, rationale: str, owner_name: str, project_name: str) -> str:
    """Persist a human-approved decision for future agents and sessions."""
    decision_id = f"decision-{uuid4().hex[:8]}"
    project_ids = {"Atlas": "project-atlas", "Mobile Checkout": "project-mobile-checkout"}
    owner_ids = {"Sarah Chen": "person-sarah", "Diego Ramos": "person-diego", "Priya Shah": "person-priya", "Leo Martin": "person-leo"}
    if project_name not in project_ids or owner_name not in owner_ids or len(title) > 140 or len(rationale) > 600:
        raise ValueError("Invalid decision details.")
    get_graph().query(
        "MERGE (decision:Decision {id: $id}) SET decision.title = $title, decision.rationale = $rationale, decision.created_at = $created_at WITH decision MATCH (owner:Person {id: $owner_id}), (project:Project {id: $project_id}) MERGE (owner)-[:MADE]->(decision) MERGE (decision)-[:ABOUT]->(project)",
        {"id": decision_id, "title": title, "rationale": rationale, "created_at": datetime.now(timezone.utc).isoformat(), "owner_id": owner_ids[owner_name], "project_id": project_ids[project_name]},
    )
    return decision_id
