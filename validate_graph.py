from graph_db import rows

CHECKS = {
    "Source evidence": "MATCH (n) WHERE n.id IN ['doc-mobile-launch', 'doc-payment-ownership', 'doc-fraud-policy', 'doc-ledger-rfc', 'doc-partner-discovery', 'ticket-atlas-42', 'ticket-atlas-57', 'ticket-mobile-18', 'ticket-ledger-8', 'ticket-trust-12', 'ticket-portal-4', 'chat-checkout-risk', 'chat-fraud-risk', 'chat-ledger-update', 'chat-partner-update'] RETURN labels(n), n.id",
    "Explainable launch risk": "MATCH (task:Task {id: 'task-tax-contract'})-[:BLOCKS]->(payment:System {id: 'system-payments'})<-[:DEPENDS_ON]-(:System {id: 'system-checkout-api'})<-[:DEPENDS_ON]-(project:Project {id: 'project-mobile-checkout'}) RETURN task.name, payment.name, project.name",
    "Source-backed ownership": "MATCH (doc:Document {id: 'doc-payment-ownership'})-[:RELATES_TO]->(system:System {id: 'system-payments'})<-[:OWNS]-(person:Person {id: 'person-sarah'}) RETURN doc.title, person.name, system.name",
}


def main():
    for name, query in CHECKS.items():
        result = rows(query)
        if not result:
            raise RuntimeError(f"Validation failed: {name}")
        print(f"[PASS] {name}: {result}")


if __name__ == "__main__":
    main()
