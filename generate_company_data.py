"""Create deterministic, connected synthetic data for the Northstar Commerce demo."""

import json
from pathlib import Path

DATA_PATH = Path(__file__).with_name("company_data.json")


def entities(prefix, values):
    return [{"id": f"{prefix}-{key}", **details} for key, details in values]


def main():
    data = {
        "teams": entities("team", [
            ("platform", {"name": "Platform"}), ("commerce", {"name": "Commerce"}),
            ("experience", {"name": "Experience"}), ("finance", {"name": "Finance"}),
            ("support", {"name": "Support"}),
        ]),
        "people": entities("person", [
            ("sarah", {"name": "Sarah Chen", "role": "Engineering Manager", "team": "Platform"}),
            ("priya", {"name": "Priya Shah", "role": "Senior Backend Engineer", "team": "Platform"}),
            ("marcus", {"name": "Marcus Lee", "role": "Site Reliability Engineer", "team": "Platform"}),
            ("diego", {"name": "Diego Ramos", "role": "Product Manager", "team": "Commerce"}),
            ("amina", {"name": "Amina Yusuf", "role": "Product Analyst", "team": "Commerce"}),
            ("leo", {"name": "Leo Martin", "role": "Staff Designer", "team": "Experience"}),
            ("nina", {"name": "Nina Patel", "role": "Frontend Engineer", "team": "Experience"}),
            ("oliver", {"name": "Oliver Grant", "role": "Finance Systems Lead", "team": "Finance"}),
            ("mei", {"name": "Mei Tan", "role": "Revenue Operations Analyst", "team": "Finance"}),
            ("jordan", {"name": "Jordan Brooks", "role": "Support Operations Lead", "team": "Support"}),
        ]),
        "projects": entities("project", [
            ("atlas", {"name": "Atlas", "status": "at risk", "description": "Modernize checkout services before holiday release."}),
            ("mobile-checkout", {"name": "Mobile Checkout", "status": "blocked", "description": "A faster one-page mobile payment flow."}),
            ("ledger-sync", {"name": "LedgerSync", "status": "on track", "description": "Reconcile payment events with the finance ledger."}),
            ("trust-shield", {"name": "TrustShield", "status": "at risk", "description": "Reduce fraud losses with risk-scored payment flows."}),
            ("partner-portal", {"name": "Partner Portal", "status": "planning", "description": "Give retail partners self-service order visibility."}),
        ]),
        "systems": entities("system", [
            ("payments", {"name": "Payment Platform", "criticality": "high"}),
            ("checkout-api", {"name": "Checkout API", "criticality": "high"}),
            ("tax", {"name": "Tax Service", "criticality": "high"}),
            ("identity", {"name": "Identity Service", "criticality": "high"}),
            ("ledger", {"name": "Finance Ledger", "criticality": "medium"}),
            ("fraud", {"name": "Fraud Engine", "criticality": "high"}),
            ("customer-gateway", {"name": "Customer Gateway", "criticality": "medium"}),
        ]),
        "tasks": entities("task", [
            ("token", {"name": "Token migration", "status": "in progress", "priority": "high"}),
            ("tax-contract", {"name": "Tax service contract", "status": "blocked", "priority": "high"}),
            ("mobile-ui", {"name": "Mobile payment UI", "status": "in progress", "priority": "high"}),
            ("checkout-observability", {"name": "Checkout observability", "status": "not started", "priority": "medium"}),
            ("ledger-replay", {"name": "Ledger replay pipeline", "status": "in progress", "priority": "medium"}),
            ("fraud-rules", {"name": "Fraud rule review", "status": "blocked", "priority": "high"}),
            ("risk-explanations", {"name": "Risk explanation UX", "status": "not started", "priority": "medium"}),
            ("partner-auth", {"name": "Partner SSO design", "status": "not started", "priority": "medium"}),
        ]),
        "documents": entities("doc", [
            ("mobile-launch", {"title": "Mobile Checkout launch brief", "source": "Product document", "excerpt": "Launch requires a stable Checkout API and completed tax contract."}),
            ("payment-ownership", {"title": "Payment Platform ownership", "source": "Architecture document", "excerpt": "Sarah Chen is accountable for Payment Platform reliability."}),
            ("fraud-policy", {"title": "Fraud escalation policy", "source": "Operations policy", "excerpt": "High-risk payments require an explainable human review path."}),
            ("ledger-rfc", {"title": "LedgerSync design RFC", "source": "Engineering RFC", "excerpt": "The ledger pipeline consumes immutable payment events."}),
            ("partner-discovery", {"title": "Partner Portal discovery", "source": "Research document", "excerpt": "Partners need order status and support-case visibility."}),
        ]),
        "tickets": entities("ticket", [
            ("atlas-42", {"key": "ATLAS-42", "title": "Finalize tax service contract", "status": "blocked"}),
            ("atlas-57", {"key": "ATLAS-57", "title": "Migrate payment token format", "status": "in progress"}),
            ("mobile-18", {"key": "MOBILE-18", "title": "Add mobile payment accessibility checks", "status": "in progress"}),
            ("ledger-8", {"key": "LEDGER-8", "title": "Replay payment events safely", "status": "in progress"}),
            ("trust-12", {"key": "TRUST-12", "title": "Explain fraud review decisions", "status": "blocked"}),
            ("portal-4", {"key": "PORTAL-4", "title": "Confirm partner identity flow", "status": "open"}),
        ]),
        "messages": entities("chat", [
            ("checkout-risk", {"channel": "#checkout-launch", "author": "Priya Shah", "text": "Tax contract blocks Payment Platform validation and therefore the mobile launch."}),
            ("fraud-risk", {"channel": "#trust-shield", "author": "Amina Yusuf", "text": "Support needs a trace explaining every fraud hold."}),
            ("ledger-update", {"channel": "#finance-systems", "author": "Oliver Grant", "text": "Ledger replay must be completed before reconciliation can be trusted."}),
            ("partner-update", {"channel": "#partner-portal", "author": "Jordan Brooks", "text": "Support tickets show SSO is the first partner friction point."}),
        ]),
        "customers": entities("customer", [
            ("northwind", {"name": "Northwind Retail", "segment": "enterprise"}),
            ("contoso", {"name": "Contoso Market", "segment": "mid-market"}),
            ("fabrikam", {"name": "Fabrikam Stores", "segment": "enterprise"}),
        ]),
        "incidents": entities("incident", [
            ("pay-202", {"title": "Payment authorization latency", "severity": "SEV-2", "status": "resolved"}),
            ("tax-77", {"title": "Tax calculation timeout", "severity": "SEV-2", "status": "monitoring"}),
        ]),
    }
    data["relationships"] = {
        "member_of": [["person-sarah", "team-platform"], ["person-priya", "team-platform"], ["person-marcus", "team-platform"], ["person-diego", "team-commerce"], ["person-amina", "team-commerce"], ["person-leo", "team-experience"], ["person-nina", "team-experience"], ["person-oliver", "team-finance"], ["person-mei", "team-finance"], ["person-jordan", "team-support"]],
        "owns": [["person-sarah", "system-payments"], ["person-priya", "system-checkout-api"], ["person-oliver", "system-ledger"], ["person-marcus", "system-identity"], ["person-amina", "system-fraud"]],
        "leads": [["person-diego", "project-atlas"], ["person-diego", "project-mobile-checkout"], ["person-oliver", "project-ledger-sync"], ["person-amina", "project-trust-shield"], ["person-jordan", "project-partner-portal"]],
        "works_on": [["person-priya", "task-token"], ["person-priya", "task-tax-contract"], ["person-nina", "task-mobile-ui"], ["person-marcus", "task-checkout-observability"], ["person-mei", "task-ledger-replay"], ["person-amina", "task-fraud-rules"], ["person-leo", "task-risk-explanations"], ["person-marcus", "task-partner-auth"]],
        "part_of": [["task-token", "project-atlas"], ["task-tax-contract", "project-atlas"], ["task-mobile-ui", "project-mobile-checkout"], ["task-checkout-observability", "project-mobile-checkout"], ["task-ledger-replay", "project-ledger-sync"], ["task-fraud-rules", "project-trust-shield"], ["task-risk-explanations", "project-trust-shield"], ["task-partner-auth", "project-partner-portal"]],
        "depends_on": [["task-tax-contract", "task-token"], ["project-mobile-checkout", "system-checkout-api"], ["system-checkout-api", "system-payments"], ["system-payments", "system-tax"], ["project-ledger-sync", "system-payments"], ["project-ledger-sync", "system-ledger"], ["project-trust-shield", "system-fraud"], ["system-fraud", "system-identity"], ["project-partner-portal", "system-customer-gateway"], ["system-customer-gateway", "system-identity"]],
        "blocks": [["task-tax-contract", "system-payments"], ["task-fraud-rules", "system-fraud"]],
        "relates_to": [["doc-mobile-launch", "project-mobile-checkout"], ["doc-mobile-launch", "task-tax-contract"], ["doc-payment-ownership", "system-payments"], ["doc-fraud-policy", "project-trust-shield"], ["doc-ledger-rfc", "project-ledger-sync"], ["doc-partner-discovery", "project-partner-portal"], ["ticket-atlas-42", "task-tax-contract"], ["ticket-atlas-57", "task-token"], ["ticket-mobile-18", "task-mobile-ui"], ["ticket-ledger-8", "task-ledger-replay"], ["ticket-trust-12", "task-fraud-rules"], ["ticket-portal-4", "task-partner-auth"], ["chat-checkout-risk", "task-tax-contract"], ["chat-fraud-risk", "task-fraud-rules"], ["chat-ledger-update", "task-ledger-replay"], ["chat-partner-update", "task-partner-auth"]],
        "uses": [["project-atlas", "system-payments"], ["project-mobile-checkout", "system-checkout-api"], ["project-ledger-sync", "system-ledger"], ["project-trust-shield", "system-fraud"], ["project-partner-portal", "system-customer-gateway"]],
        "affected_by": [["customer-northwind", "incident-pay-202"], ["customer-contoso", "incident-tax-77"], ["incident-pay-202", "system-payments"], ["incident-tax-77", "system-tax"]],
    }
    DATA_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Wrote {DATA_PATH.name}: {sum(len(v) for k, v in data.items() if k != 'relationships')} nodes and {sum(len(v) for v in data['relationships'].values())} relationships.")


if __name__ == "__main__":
    main()
