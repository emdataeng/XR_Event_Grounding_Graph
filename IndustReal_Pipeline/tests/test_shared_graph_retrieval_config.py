from __future__ import annotations

import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS_DIR = REPO_ROOT / "experiments"
QUERY_SRC = EXPERIMENTS_DIR / "query_driven_graph" / "src"
sys.path.insert(0, str(EXPERIMENTS_DIR))
sys.path.insert(0, str(QUERY_SRC))

from query_planner import build_query_plan, load_query_template_config  # noqa: E402
from shared.graph_retrieval_config import load_graph_retrieval_config  # noqa: E402


SHARED_CONFIG = EXPERIMENTS_DIR / "shared" / "configs" / "graph_retrieval.yaml"
QUERY_TEMPLATES = (
    EXPERIMENTS_DIR / "query_driven_graph" / "configs" / "query_templates.yaml"
)


def test_shared_graph_retrieval_config_is_the_source_of_hop_budgets() -> None:
    assert load_graph_retrieval_config(SHARED_CONFIG) == {
        "step_hops": 1,
        "evidence_hops": 2,
    }


def test_missing_shared_hyperparameter_fails_clearly(tmp_path: Path) -> None:
    path = tmp_path / "retrieval.yaml"
    path.write_text("context_retrieval:\n  step_hops: 1\n", encoding="utf-8")

    with pytest.raises(ValueError, match="evidence_hops"):
        load_graph_retrieval_config(path)


def test_query_templates_render_shared_sequence_and_semantic_depths() -> None:
    templates = load_query_template_config(QUERY_TEMPLATES)
    retrieval = {"step_hops": 3, "evidence_hops": 4}

    sequence = build_query_plan(
        {
            "step_id": "clip::event_001",
            "question": "What comes next?",
            "risk_type": "sequence_error",
        },
        templates,
        "graph",
        25,
        retrieval,
    )
    semantic = build_query_plan(
        {
            "step_id": "clip::event_001",
            "question": "Is this part correct?",
            "risk_type": "component_confusion",
        },
        templates,
        "graph",
        25,
        retrieval,
    )

    assert "[:NEXT*0..3]" in sequence.cypher
    assert "*0..4]" in semantic.cypher
    assert "{step_hops}" not in sequence.cypher
    assert "{evidence_hops}" not in semantic.cypher
