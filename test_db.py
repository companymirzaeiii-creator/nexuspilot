from falkordb import FalkorDB

db = FalkorDB(host="localhost", port=6379)
graph = db.select_graph("contextpilot")

graph.query("""
MERGE (p:Person {name: 'Sarah'})
MERGE (t:Task {name: 'Fix payment system'})
MERGE (p)-[:RESPONSIBLE_FOR]->(t)
""")

result = graph.ro_query("""
MATCH (p:Person)-[:RESPONSIBLE_FOR]->(t:Task)
RETURN p.name, t.name
""")

for row in result.result_set:
    print(row)