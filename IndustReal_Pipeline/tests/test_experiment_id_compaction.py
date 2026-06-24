from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS_DIR = REPO_ROOT / "experiments"
ABLATION_SRC = EXPERIMENTS_DIR / "llm_guidance_ablation" / "src"
QUERY_SRC = EXPERIMENTS_DIR / "query_driven_graph" / "src"
sys.path.insert(0, str(EXPERIMENTS_DIR))
sys.path.insert(0, str(ABLATION_SRC))
sys.path.insert(0, str(QUERY_SRC))

from answer_builder import build_answer_prompt  # noqa: E402
from context_builders import build_steps_only_context  # noqa: E402
from shared.id_compaction import (  # noqa: E402
    compact_prompt_text,
    compact_prompt_value,
    compact_step_id,
    parse_step_id,
    step_provenance,
)


STEP_1 = "raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_001"
CANONICAL_STEP_1 = "step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_1"
CANONICAL_STEP_2 = "step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_2"


def test_parse_and_compact_step_id() -> None:
    assert parse_step_id(CANONICAL_STEP_1) == {
        "run_id": "raw_cad_dataset__all_test_clips",
        "evidence_mode": "od_only",
        "archive": "test_p1",
        "clip_id": "03_assy_0_1",
        "step_index": 1,
        "clip_result_id": "raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1",
    }
    assert compact_step_id(STEP_1) == "step_1"
    assert step_provenance("custom_step") is None


def test_compaction_is_recursive_and_scoped_to_the_reference_clip() -> None:
    other_clip = "step::raw_cad_dataset__all_test_clips::od_only::test_p1::other_clip::event_2"
    value = {"ids": [CANONICAL_STEP_1, CANONICAL_STEP_2, other_clip]}
    assert compact_prompt_value(value, STEP_1) == {
        "ids": ["step_1", "step_2", other_clip]
    }


def test_query_driven_prompt_compacts_ids_but_not_query_plan() -> None:
    class Plan:
        intent = "sequence_context"
        cypher = "MATCH (s:Step) WHERE s.step_id = $step_id RETURN s"

    prompt = build_answer_prompt(
        {"step_id": STEP_1, "question": "What is next?"},
        Plan(),
        [{"step_id": CANONICAL_STEP_1, "next_step_id": CANONICAL_STEP_2}],
        f"Current {CANONICAL_STEP_1}; next {CANONICAL_STEP_2}",
        {
            "answer_generation": {
                "system_with_evidence": "system",
                "system_missing_evidence": "missing",
                "user_template": "{step_id}\n{question}\n{intent}\n{cypher}\n{query_result}\n{step_context}",
            }
        },
    )

    assert "step_1" in prompt["user_prompt"]
    assert "step_2" in prompt["user_prompt"]
    assert "raw_cad_dataset__all_test_clips" not in prompt["user_prompt"]
    assert Plan.cypher in prompt["user_prompt"]


def test_ablation_steps_prompt_compacts_current_id_and_step_list() -> None:
    prompt = build_steps_only_context(
        {"step_id": STEP_1, "question": "What is next?"},
        {
            "step_list": f"{CANONICAL_STEP_1}\n{CANONICAL_STEP_2}",
            "prompt_templates": {
                "steps_only": {
                    "system_with_context": "system",
                    "system_missing_context": "missing",
                    "user_template": "{step_id}\n{step_context}\n{question}",
                }
            },
        },
    )

    assert prompt["user_prompt"].splitlines()[:3] == ["step_1", "step_1", "step_2"]
    assert "raw_cad_dataset__all_test_clips" not in prompt["user_prompt"]


def test_compact_prompt_text_handles_graph_node_prefixes() -> None:
    text = f"Step::{CANONICAL_STEP_1} depends on {CANONICAL_STEP_2}"
    assert compact_prompt_text(text, STEP_1) == "step_1 depends on step_2"
