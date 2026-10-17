"""Optional local performance benchmark in an isolated FalkorDB graph.

It never changes the ContextPilot demo graph. It creates 1,000 payment events
and 40 connected high-risk alerts in `contextpilot_benchmark`.
"""

from time import perf_counter

from falkordb import FalkorDB

EVENTS = 1_000
BATCH_SIZE = 200


def main():
    graph = FalkorDB(host="localhost", port=6379).select_graph("contextpilot_benchmark")
    started = perf_counter()
    for start in range(0, EVENTS, BATCH_SIZE):
        events = [{"id": f"event-{index:04d}", "amount": 20 + (index % 500), "risk": "high" if index % 25 == 0 else "normal"} for index in range(start, min(start + BATCH_SIZE, EVENTS))]
        graph.query("UNWIND $events AS event MERGE (payment:PaymentEvent {id: event.id}) SET payment += event", {"events": events})
        alerts = [{"id": f"alert-{event['id']}", "event_id": event["id"]} for event in events if event["risk"] == "high"]
        if alerts:
            graph.query("UNWIND $alerts AS alert MATCH (payment:PaymentEvent {id: alert.event_id}) MERGE (risk:RiskAlert {id: alert.id}) SET risk.severity = 'high' MERGE (risk)-[:FLAGS]->(payment)", {"alerts": alerts})
    count = graph.ro_query("MATCH (n) WHERE n:PaymentEvent OR n:RiskAlert RETURN count(n)").result_set[0][0]
    print(f"Benchmark graph contains {count} nodes after {perf_counter() - started:.2f}s.")
    print("The production/demo graph named contextpilot was not changed.")


if __name__ == "__main__":
    main()
