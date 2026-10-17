import streamlit as st

from agent import answer, record_decision, record_episode, triage_incident
from graph_db import rows

st.set_page_config(page_title="NexusPilot", page_icon=":material/account_tree:", layout="wide")
st.session_state.setdefault("messages", [])

st.title("NexusPilot")
st.caption("A local, evidence-backed company brain powered by FalkorDB.")

@st.cache_data(ttl="15s", max_entries=1)
def overview_metrics():
    """Small, bounded cache keeps the first screen fast without hiding new decisions."""
    return {
        "people": rows("MATCH (p:Person) WHERE p.id STARTS WITH 'person-' RETURN count(p)")[0][0],
        "projects": rows("MATCH (p:Project) WHERE p.id STARTS WITH 'project-' RETURN count(p)")[0][0],
        "evidence": rows("MATCH (n) WHERE (n:Document OR n:Ticket OR n:ChatMessage) AND (n.id STARTS WITH 'doc-' OR n.id STARTS WITH 'ticket-' OR n.id STARTS WITH 'chat-') RETURN count(n)")[0][0],
        "open_risks": rows("MATCH (t:Task {status: 'blocked'}) WHERE t.id STARTS WITH 'task-' RETURN count(t)")[0][0],
        "handoffs": rows("MATCH (h:AgentHandoff) RETURN count(h)")[0][0],
    }

try:
    metrics = overview_metrics()
    with st.container(horizontal=True):
        st.metric("People", metrics["people"], border=True)
        st.metric("Projects", metrics["projects"], border=True)
        st.metric("Evidence records", metrics["evidence"], border=True)
        st.metric("Open risks", metrics["open_risks"], border=True)
        st.metric("Agent handoffs", metrics["handoffs"], border=True)
except Exception:
    st.warning("FalkorDB is not reachable yet. Open Docker Desktop and run `docker compose up -d`.", icon=":material/database:")

with st.sidebar:
    st.header("Track completion", divider=True)
    st.success("Track 1: triage actions", icon=":material/bolt:")
    st.success("Track 2: persistent memory and handoffs", icon=":material/memory:")
    st.success("Track 3: sourced company brain", icon=":material/account_tree:")
    st.header("Track 1: triage an incident", divider=True)
    st.caption("This turns graph impact into an assigned work item and a persisted agent handoff.")
    with st.form("triage_form", clear_on_submit=True):
        incident = st.selectbox("Incident", {"Payment authorization latency": "incident-pay-202", "Tax calculation timeout": "incident-tax-77"})
        assignee = st.selectbox("Assign to", ["Sarah Chen", "Priya Shah", "Marcus Lee", "Amina Yusuf"])
        priority = st.selectbox("Priority", ["P1", "P2", "P3"])
        triage = st.form_submit_button("Create triage handoff", icon=":material/assignment:", type="primary", width="stretch")
    if triage:
        try:
            work_id = triage_incident({"Payment authorization latency": "incident-pay-202", "Tax calculation timeout": "incident-tax-77"}[incident], assignee, priority)
            overview_metrics.clear()
            st.success(f"Track 1 work item created: {work_id}")
        except Exception as error:
            st.error(f"Could not create handoff: {error}")
    st.header("Record a decision", divider=True)
    st.caption("This writes approved company knowledge to FalkorDB so it remains available in a new session.")
    with st.form("decision_form", clear_on_submit=True):
        title = st.text_input("Decision title", placeholder="Delay launch until tax validation passes", max_chars=140)
        rationale = st.text_area("Rationale", placeholder="The graph shows an unresolved dependency on Payment Platform.", max_chars=600)
        owner = st.selectbox("Decision owner", ["Sarah Chen", "Diego Ramos", "Priya Shah", "Leo Martin"])
        project = st.selectbox("Related project", ["Atlas", "Mobile Checkout"])
        save_decision = st.form_submit_button("Save decision", icon=":material/save:", type="primary", width="stretch")
    if save_decision:
        if not title.strip() or not rationale.strip():
            st.error("Add both a decision title and a rationale.")
        else:
            try:
                decision_id = record_decision(title.strip(), rationale.strip(), owner, project)
                overview_metrics.clear()
                st.success(f"Decision saved to the graph: {decision_id}")
            except Exception as error:
                st.error(f"Could not save the decision: {error}")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and message.get("sources"):
            with st.expander("Evidence and graph path"):
                st.markdown("**Sources**\n\n" + "\n".join(f"- {source}" for source in message["sources"]))
                st.markdown("**Graph path**\n\n" + "\n".join(f"- {step}" for step in message["trace"]))

prompt = st.chat_input("Ask about people, projects, risks, or dependencies", key="company_question", submit_mode="disable")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        try:
            response = answer(prompt)
            record_episode(prompt, response.answer)
            st.markdown(response.answer)
            if response.sources or response.trace:
                with st.expander("Evidence and graph path"):
                    if response.sources:
                        st.markdown("**Sources**\n\n" + "\n".join(f"- {source}" for source in response.sources))
                    if response.trace:
                        st.markdown("**Graph path**\n\n" + "\n".join(f"- {step}" for step in response.trace))
            st.session_state.messages.append({"role": "assistant", "content": response.answer, "sources": response.sources, "trace": response.trace})
        except Exception as error:
            st.error(f"I could not reach FalkorDB: {error}")
