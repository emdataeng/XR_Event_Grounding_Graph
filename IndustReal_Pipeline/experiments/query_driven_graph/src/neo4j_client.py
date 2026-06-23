"""Neo4j client wrapper for query-driven graph retrieval."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any


class Neo4jQueryClient:
    """Small wrapper around the Neo4j Python driver."""

    def __init__(self, uri: str, user: str, password: str) -> None:
        try:
            from neo4j import GraphDatabase
        except ImportError as exc:
            raise RuntimeError("neo4j is required. Install repository requirements.txt.") from exc

        self._driver = GraphDatabase.driver(uri, auth=(user, password))
        self._driver.verify_connectivity()

    def close(self) -> None:
        """Close the underlying driver."""
        self._driver.close()

    def run_read_query(self, cypher: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        """Execute a read query and return plain dictionaries."""
        with self._driver.session() as session:
            result = session.execute_read(lambda tx: list(tx.run(cypher, **params)))
        return [dict(record) for record in result]

    def fetch_step_ids(self, graph_name: str) -> set[str]:
        """Return all Step.step_id values for the configured graph."""
        rows = self.run_read_query(
            (
                "MATCH (s:Step {graph_name: $graph_name}) "
                "WHERE s.step_id IS NOT NULL "
                "RETURN s.step_id AS step_id "
                "ORDER BY s.index, s.step_id"
            ),
            {"graph_name": graph_name},
        )
        return {str(row["step_id"]) for row in rows if row.get("step_id")}


def client_from_config(config: dict[str, Any], repo_root: Path) -> Neo4jQueryClient:
    """Create a Neo4j client from config and an optional dotenv file."""
    neo4j_config = config.get("neo4j") or {}
    env_file = resolve_path(str(neo4j_config.get("env_file") or ".env"), repo_root)
    if env_file.exists():
        try:
            from dotenv import load_dotenv
        except ImportError as exc:
            raise RuntimeError("python-dotenv is required. Install repository requirements.txt.") from exc
        load_dotenv(env_file)

    uri = os.getenv("NEO4J_URI") or str(neo4j_config.get("uri") or "")
    user = os.getenv("NEO4J_USER") or str(neo4j_config.get("user") or "neo4j")
    password = os.getenv("NEO4J_PASSWORD") or str(neo4j_config.get("password") or "")
    if not uri or not password:
        raise RuntimeError(f"NEO4J_URI and NEO4J_PASSWORD must be set in {env_file} or neo4j config.")
    return Neo4jQueryClient(uri, user, password)


def resolve_path(path_value: str, repo_root: Path) -> Path:
    """Resolve a configured path from common execution locations."""
    path = Path(path_value)
    if path.is_absolute():
        return path
    for base in (Path.cwd(), repo_root):
        candidate = base / path
        if candidate.exists():
            return candidate
    return repo_root / path
