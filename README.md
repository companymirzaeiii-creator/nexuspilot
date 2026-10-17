# NexusPilot — Explainable graph-native agents for company operations

> A local, evidence-backed company-context agent built with **FalkorDB** and **Streamlit**.

NexusPilot models a fictional retailer, **Northstar Commerce**, as a connected graph. It helps teams answer questions that ordinary tables struggle with: ownership, dependency risk, customer impact, supporting evidence, and decisions that must persist across sessions.

## Track coverage

| Track | What to do in the app | Proof stored in FalkorDB |
| --- | --- | --- |
| **01 — Agents That Act on Connected Data** | Use **Track 1: triage an incident** in the sidebar, then ask `Show open handoffs`. | `WorkItem`, `AgentHandoff`, the incident, and the assigned person are connected by graph edges. |
| **02 — Agent Memory and Coordination** | Ask any question, refresh the browser, then ask `Show recent memory`. Create a triage handoff and ask `Show open handoffs`. | Each question becomes an `Episode`; decisions, work items, and handoffs remain in the graph under `tenant-northstar`. |
| **03 — Company Brain** | Ask `What is blocking the mobile checkout launch?` and expand evidence. | People, teams, projects, systems, docs, tickets, chats, customers, and incidents provide a sourced multi-hop answer. |

All flows run locally. No API key, cloud account, or paid model is required.

## Start here — for referees and first-time users

No prior knowledge of FalkorDB or Python is required. Follow the setup guide for your operating system, then open the app and use one of the scenarios below.

<details>
<summary><strong>Windows setup — click to open</strong></summary>

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and open it. Wait until Docker says it is running.
2. Install [Python 3](https://www.python.org/downloads/) and [Git](https://git-scm.com/downloads).
3. Download this repository as a ZIP file from GitHub and extract it, or clone it with Git.
4. Open the project folder in PowerShell. A beginner can do this by opening the folder in File Explorer, clicking the address bar, typing `powershell`, and pressing Enter.
5. Copy and run these commands one at a time:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
docker compose up -d
python generate_company_data.py
python seed_graph.py
python validate_graph.py
streamlit run app.py
```

6. Open the address printed by Streamlit, normally `http://localhost:8501`.
7. To see the graph visually, open `http://localhost:3000` in another browser tab.

If PowerShell blocks activation, run this once in the same terminal, then repeat the activation command:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

</details>

<details>
<summary><strong>macOS setup — click to open</strong></summary>

1. Install Docker Desktop for Mac, Python 3, and Git. Open Docker Desktop and wait until it is running.
2. Download/extract this repository, then open **Terminal** in the project folder.
3. Run these commands one at a time:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
docker compose up -d
python generate_company_data.py
python seed_graph.py
python validate_graph.py
streamlit run app.py
```

4. Open `http://localhost:8501` for NexusPilot and `http://localhost:3000` for FalkorDB Browser.

</details>

<details>
<summary><strong>Linux setup — click to open</strong></summary>

1. Install Docker Engine with the Docker Compose plugin, Python 3 with `venv`, and Git using your Linux distribution’s package manager. Ensure the Docker service is running.
2. Download/extract this repository, then open a terminal in the project folder.
3. Run these commands one at a time:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
docker compose up -d
python generate_company_data.py
python seed_graph.py
python validate_graph.py
streamlit run app.py
```

4. Open `http://localhost:8501` for NexusPilot and `http://localhost:3000` for FalkorDB Browser.

If Docker reports a permission error, follow your distribution’s official Docker post-install instructions or run Docker through its supported desktop/runtime setup.

</details>

<details>
<summary><strong>Try Track 1 — agent acts on connected data</strong></summary>

1. In NexusPilot, ask: `Which customers are affected by incidents?`
2. In the left sidebar, find **Track 1: triage an incident**.
3. Choose **Tax calculation timeout**, choose an assignee, choose **P1**, and click **Create triage handoff**.
4. Ask: `Show open handoffs`.

Expected result: the graph-created work item appears with the Risk analyst, Delivery coordinator, incident, and assigned person. This proves the agent did more than answer—it used the graph to take an explainable action.

</details>

<details>
<summary><strong>Try Track 2 — persistent memory and coordination</strong></summary>

1. Ask: `What is blocking the mobile checkout launch?`
2. Refresh the browser page, or close and reopen the app URL.
3. Ask: `Show recent memory`.
4. If you completed Track 1, ask: `Show open handoffs`.

Expected result: the previous question is still available as an `Episode` in FalkorDB, and the handoff is shared state between the two agents. It remains after a browser refresh because it is graph memory, not temporary page memory.

</details>

<details>
<summary><strong>Try Track 3 — company brain with sources</strong></summary>

1. Ask: `What is blocking the mobile checkout launch?`
2. Click **Evidence and graph path** below the answer.
3. Open FalkorDB Browser at `http://localhost:3000` and select graph `contextpilot`.
4. Run the graph query in the **Viewing the FalkorDB graph** section below.

Expected result: the answer connects a blocked tax task, Payment Platform, Checkout API, and Mobile Checkout, with a ticket and chat message as evidence.

</details>

## The scenario

Northstar Commerce is preparing several interdependent initiatives:

- **Mobile Checkout** is a one-page payment launch. It depends on Checkout API, which depends on Payment Platform.
- **Atlas** is a checkout modernization effort. Its blocked tax-service contract blocks Payment Platform validation, which in turn blocks the Mobile Checkout launch.
- **TrustShield** improves fraud review. Its unresolved fraud-rule work blocks the Fraud Engine.
- **LedgerSync** reconciles payment events with Finance Ledger.
- **Partner Portal** gives retail partners order and support visibility.

The app uses only deterministic synthetic data. No customer, company, or cloud data is sent anywhere.

## Why a graph?

The answer to “What is blocking Mobile Checkout?” is not stored in one record. NexusPilot traverses connected evidence:

```mermaid
flowchart LR
    TaxTask[Tax service contract: blocked] -->|BLOCKS| Payments[Payment Platform]
    Mobile[Mobile Checkout] -->|DEPENDS_ON| Checkout[Checkout API]
    Checkout -->|DEPENDS_ON| Payments
    Ticket[ATLAS-42] -->|RELATES_TO| TaxTask
    Chat[#checkout-launch] -->|RELATES_TO| TaxTask
```

This produces an answer, the evidence backing it, and the graph path used.

## Graph model

| Node type | Examples | Purpose |
| --- | --- | --- |
| `Person`, `Team` | Sarah Chen, Platform | Ownership and expertise |
| `Project`, `Task`, `System` | Mobile Checkout, Tax Service | Work and dependency context |
| `Document`, `Ticket`, `ChatMessage` | Launch brief, ATLAS-42, channel update | Traceable supporting evidence |
| `Incident`, `Customer` | Tax timeout, Northwind Retail | Operational and customer impact |
| `Decision`, `Episode`, `Procedure` | Approved decisions, question/answer memory, triage runbook | Semantic, episodic, and procedural memory |
| `Agent`, `AgentHandoff`, `WorkItem`, `Tenant` | Risk analyst, delivery coordinator, assigned triage work | Shared coordination state and tenant boundary |

Important relationships include `OWNS`, `LEADS`, `WORKS_ON`, `DEPENDS_ON`, `BLOCKS`, `RELATES_TO`, `USES`, `AFFECTED_BY`, `MADE`, and `ABOUT`.

## Viewing the FalkorDB graph

Open **http://localhost:3000** while Docker Desktop and `docker compose up -d` are running. In FalkorDB Browser, select the `contextpilot` graph and run:

```cypher
MATCH path = (project:Project {id: 'project-mobile-checkout'})-[:DEPENDS_ON*1..2]->(system:System)<-[:BLOCKS]-(task:Task)
RETURN path
```

This visualizes the Track 3 Mobile Checkout risk path. For Track 1 and Track 2 after you use the app actions, run:

```cypher
MATCH path = (:Agent)-[:HANDOFF_TO]->(:AgentHandoff)-[:CREATED]->(:WorkItem)-[:ASSIGNED_TO]->(:Person)
RETURN path
```

## Optional scale benchmark

Run this only when you want to demonstrate local scale testing:

```powershell
python benchmark_scale.py
```

It uses a separate `contextpilot_benchmark` graph and creates 1,000 payment events plus 40 high-risk alerts. It never changes the `contextpilot` demonstration graph, so it is safe to run before or after a demo.

## Demo questions

- `Who owns the payment platform?`
- `What is blocking the mobile checkout launch?`
- `What is the fraud risk?`
- `Which customers are affected by incidents?`
- `Show tasks for the Atlas program`
- `What decisions have been made for Mobile Checkout?`
- `Show recent memory`
- `Show open handoffs`

Use **Record a decision** in the sidebar to persist a decision. Refresh or open a new browser session, then ask for decisions again: the answer comes from FalkorDB, not Streamlit session state.

## Track implementation

| Track | Current status | Evidence in NexusPilot |
| --- | --- | --- |
| **Track 1 — Agents that act on connected data** | Complete local demo | The risk agent follows the incident/dependency graph and the triage action creates an assigned `WorkItem`; a persisted `AgentHandoff` records the action. |
| **Track 2 — Agent memory and coordination** | Complete local demo | `Episode` nodes retain conversations, `Decision` nodes retain semantic knowledge, `Procedure` nodes represent the runbook, and two graph agents share handoff state inside `tenant-northstar`. |
| **Track 3 — Company Brain** | Complete local demo | The company graph unifies operational work, sources, customers, and incidents. Answers display sources and traversed paths; human decisions are written back to the graph. |

## Reliability and performance choices

- **Safe query templates:** user questions select known read-only Cypher templates; user-provided decision text is passed as query parameters.
- **Connection recovery:** read queries retry once and report a friendly Docker/FalkorDB error if unavailable.
- **Connection reuse:** the local graph client is cached in-process.
- **Bounded UI cache:** dashboard metrics use a 15-second, one-entry cache and are cleared after a decision write.
- **Idempotent seed:** `MERGE` makes re-seeding safe; it updates rather than duplicates the synthetic data.
- **Validation script:** `validate_graph.py` checks source evidence, the launch-risk path, and source-backed ownership.

## Repository layout

```text
nexuspilot/
├── app.py                    # Streamlit chat UI and decision action
├── agent.py                  # Explainable, fixed-query local agent
├── graph_db.py               # Resilient FalkorDB access helpers
├── generate_company_data.py  # Deterministic Northstar Commerce fixture generator
├── company_data.json         # Generated synthetic fixture
├── seed_graph.py             # Idempotent graph seeding
├── validate_graph.py         # Integration checks
├── compose.yaml              # Local FalkorDB service
└── test_db.py                # Original connection smoke test
```

## Limits and next steps

This repository is a local demonstration of each track. Production deployments would add:

1. Authentication and role-based access controls.
2. Multiple isolated tenant graphs and tenant-specific data ingestion.
3. Automated ingestion of approved documents, tickets, and chat exports.
4. Monitoring, backups, and deployment configuration for the selected hosting environment.

## License

Demo project for the Graph Hacks challenge. Replace this section with your chosen license before publishing.
