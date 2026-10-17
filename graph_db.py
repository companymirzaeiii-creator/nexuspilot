"""Small FalkorDB helpers shared by the seed, validation, agent, and UI."""

from functools import lru_cache
from time import sleep

from falkordb import FalkorDB

GRAPH_NAME = "contextpilot"


@lru_cache(maxsize=1)
def get_graph():
    return FalkorDB(host="localhost", port=6379).select_graph(GRAPH_NAME)


def rows(query: str, params: dict | None = None):
    """Run a read-only Cypher query, optionally with safe query parameters."""
    last_error = None
    for attempt in range(2):
        try:
            return get_graph().ro_query(query, params=params, timeout=5).result_set
        except Exception as error:  # FalkorDB client errors vary by transport/version.
            last_error = error
            get_graph.cache_clear()
            if attempt == 0:
                sleep(0.2)
    raise RuntimeError("FalkorDB is unavailable. Ensure Docker Desktop and the FalkorDB container are running.") from last_error
