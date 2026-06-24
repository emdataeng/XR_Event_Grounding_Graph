from __future__ import annotations

import json
import sys
from datetime import datetime
from io import StringIO
from pathlib import Path


RUNNER_SRC = (
    Path(__file__).resolve().parents[1]
    / "experiments"
    / "query_driven_graph"
    / "src"
)
sys.path.insert(0, str(RUNNER_SRC))

import run_experiment_query_driven_graph as runner  # noqa: E402


class FakeNeo4jClient:
    def fetch_step_ids(self, graph_name: str) -> set[str]:
        return {"step_1", "step_2"}

    def run_read_query(self, cypher: str, params: dict) -> list[dict]:
        return [{"step_id": params["step_id"], "evidence": "available"}]

    def close(self) -> None:
        pass


class FakePlan:
    def __init__(self, step_id: str) -> None:
        self.intent = "current_step_context"
        self.description = "Test query"
        self.cypher = "RETURN $step_id"
        self.params = {"step_id": step_id}


def test_communication_log_timestamp_uses_local_timezone() -> None:
    handle = StringIO()
    runner.write_log_event(handle, "test_event")

    timestamp = json.loads(handle.getvalue())["timestamp"]
    parsed = datetime.fromisoformat(timestamp)

    assert parsed.utcoffset() == datetime.now().astimezone().utcoffset()


def test_llm_failure_is_logged_and_next_question_is_processed(
    tmp_path: Path, monkeypatch
) -> None:
    test_cases = [
        {"case_id": "case_1", "step_id": "step_1", "question": "First?", "risk_type": "test"},
        {"case_id": "case_2", "step_id": "step_2", "question": "Second?", "risk_type": "test"},
    ]
    output_root = tmp_path / "outputs"
    config = {
        "_config_path": str(tmp_path / "config.yaml"),
        "graph_retrieval_config": "graph_retrieval.yaml",
        "neo4j": {"graph_name": "test_graph", "row_limit": 25},
        "input_paths": {},
        "prompt_paths": {"prompts": "prompts.yaml", "query_templates": "queries.yaml"},
        "output_paths": {"root": str(output_root)},
    }

    monkeypatch.setattr(runner, "load_test_cases", lambda unused: test_cases)
    monkeypatch.setattr(runner, "load_step_context", lambda unused: "")
    monkeypatch.setattr(runner, "load_prompt_templates", lambda unused: {})
    monkeypatch.setattr(runner, "load_query_template_config", lambda unused: {})
    monkeypatch.setattr(
        runner,
        "load_graph_retrieval_config",
        lambda unused: {"step_hops": 1, "evidence_hops": 2},
    )
    monkeypatch.setattr(runner, "client_from_config", lambda unused_config, unused_root: FakeNeo4jClient())
    monkeypatch.setattr(
        runner,
        "build_query_plan",
        lambda case, unused_templates, unused_graph, unused_limit, unused_retrieval: FakePlan(
            case["step_id"]
        ),
    )
    monkeypatch.setattr(
        runner,
        "build_answer_prompt",
        lambda *unused: {"system_prompt": "system", "user_prompt": "user"},
    )
    monkeypatch.setattr(runner, "export_query_reports", lambda rows, path: None)
    monkeypatch.setattr(runner, "set_config_path", lambda path: None)
    monkeypatch.setattr(runner, "local_timestamp_for_filename", lambda: "test-run")

    call_count = 0

    def fake_ask_llm(system_prompt: str, user_prompt: str) -> str:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise RuntimeError("context length exceeded")
        return "second answer"

    monkeypatch.setattr(runner, "ask_llm", fake_ask_llm)

    paths = runner.run_experiment(config)

    rows = [
        json.loads(line)
        for line in paths["responses"].read_text(encoding="utf-8").splitlines()
    ]
    events = [
        json.loads(line)
        for line in paths["log"].read_text(encoding="utf-8").splitlines()
    ]

    assert len(rows) == 2
    assert rows[0]["llm_status"] == "failed"
    assert rows[0]["step_provenance"] is None
    assert rows[0]["llm_error"] == "RuntimeError: context length exceeded"
    assert rows[1]["llm_status"] == "ok"
    assert rows[1]["response"] == "second answer"

    failure_event = next(event for event in events if event["event"] == "llm_call_failed")
    assert failure_event["interaction"] == 1
    assert failure_event["case_id"] == "case_1"
    assert failure_event["error_type"] == "RuntimeError"
    assert failure_event["error_message"] == "context length exceeded"

    completed = [event for event in events if event["event"] == "interaction_completed"]
    assert [event["llm_status"] for event in completed] == ["failed", "ok"]
    run_completed = next(event for event in events if event["event"] == "run_completed")
    assert run_completed["completed_interactions"] == 2
    assert run_completed["failed_llm_interactions"] == 1
