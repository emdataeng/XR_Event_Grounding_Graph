"""Validation helpers for read-only Cypher templates."""

from __future__ import annotations

import re


_FORBIDDEN_KEYWORDS = re.compile(
    r"\b(CREATE|MERGE|SET|DELETE|DETACH|DROP|LOAD\s+CSV|CALL\s+DBMS|CALL\s+APOC|REMOVE|FOREACH)\b",
    re.IGNORECASE,
)
_ALLOWED_START = re.compile(r"^\s*(MATCH|OPTIONAL\s+MATCH)\b", re.IGNORECASE)


def validate_read_only_cypher(cypher: str) -> None:
    """Reject Cypher that is not safe for read-only experiment retrieval."""
    text = str(cypher or "").strip()
    if not text:
        raise ValueError("Cypher template is empty.")
    if not _ALLOWED_START.search(text):
        raise ValueError("Cypher must start with MATCH or OPTIONAL MATCH.")
    forbidden = _FORBIDDEN_KEYWORDS.search(text)
    if forbidden:
        raise ValueError(f"Cypher contains forbidden keyword: {forbidden.group(0)}")
    if "$graph_name" not in text:
        raise ValueError("Cypher must be scoped by $graph_name.")
    if "$step_id" not in text:
        raise ValueError("Cypher must be anchored by $step_id.")
    if "LIMIT" not in text.upper():
        raise ValueError("Cypher must include LIMIT.")

