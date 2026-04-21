"""tests/test_psr.py — Unit tests for the PSR module."""
import json
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.psr import (
    _weighted_dam_lev,
    procedure_order_similarity,
    state_string_to_list,
    convert_states_to_steps,
    NaivePSR,
    AccumulatedConfidencePSR,
    evaluate,
    CATEGORIES,
)

# Full proc_info from the real dataset (33 entries covering all 11 components).
PROC_INFO = json.loads((ROOT / "configs" / "procedure_info.json").read_text())


class TestWeightedDamLev:
    def test_identical(self):
        assert _weighted_dam_lev([1, 2, 3], [1, 2, 3]) == 0.0

    def test_empty_both(self):
        assert _weighted_dam_lev([], []) == 0.0

    def test_empty_s(self):
        assert _weighted_dam_lev([], [1, 2]) == 2.0

    def test_empty_t(self):
        assert _weighted_dam_lev([1, 2], []) == 2.0

    def test_single_insert(self):
        assert _weighted_dam_lev([1], [1, 2]) == 1.0

    def test_single_delete(self):
        assert _weighted_dam_lev([1, 2], [1]) == 1.0

    def test_transposition(self):
        # [1,2] vs [2,1] — one transposition costs 1, not 2.
        assert _weighted_dam_lev([1, 2], [2, 1]) == 1.0

    def test_substitution_costs_2(self):
        # Substitution costs 2, so [1] vs [2] = 2 (not 1).
        assert _weighted_dam_lev([1], [2]) == 2.0


class TestPOS:
    def test_perfect(self):
        assert procedure_order_similarity([1, 2, 3], [1, 2, 3]) == 1.0

    def test_both_empty(self):
        assert procedure_order_similarity([], []) == 1.0

    def test_gt_empty_pred_non_empty(self):
        assert procedure_order_similarity([], [1]) == 0.0

    def test_worst_case_capped(self):
        # All wrong, but POS is clamped at 0.
        result = procedure_order_similarity([1, 2], [3, 4, 5, 6])
        assert result == 0.0


class TestStateStringToList:
    def test_basic(self):
        assert state_string_to_list("10110") == [1, 0, 1, 1, 0]

    def test_all_zeros(self):
        assert state_string_to_list("00000") == [0, 0, 0, 0, 0]

    def test_length(self):
        assert len(state_string_to_list("10000000000")) == 11


class TestConvertStatesToSteps:
    def test_install_component_1(self):
        # 11-bit vectors: component 1 (front chassis) goes 0→1.
        prev = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        curr = [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        actions, n_err = convert_states_to_steps(prev, curr, 10, PROC_INFO)
        assert len(actions) == 1
        assert actions[0]["id"] == 3   # k=1, install → k*3+0=3
        assert n_err == 0

    def test_remove_component_1(self):
        prev = [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        curr = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        actions, n_err = convert_states_to_steps(prev, curr, 10, PROC_INFO)
        assert len(actions) == 1
        assert actions[0]["id"] == 5   # k=1, remove → k*3+2=5

    def test_no_change(self):
        state = [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        actions, n_err = convert_states_to_steps(state, state, 10, PROC_INFO)
        assert actions == []
        assert n_err == 0


class TestNaivePSR:
    def test_basic_install(self):
        psr = NaivePSR(PROC_INFO)
        # Feed state 1 (class 1 = "10000000000") → sets initial state
        psr.update([[1, 0.9, [0, 0, 10, 10]]], 0)
        # Feed state 2 (class 2 = "10010010000") → triggers steps
        psr.update([[2, 0.9, [0, 0, 10, 10]]], 5)
        assert len(psr.y_hat) > 0

    def test_low_conf_ignored(self):
        psr = NaivePSR(PROC_INFO, conf_threshold=0.8)
        psr.update([[1, 0.9, [0, 0, 10, 10]]], 0)
        psr.update([[2, 0.3, [0, 0, 10, 10]]], 5)  # conf below threshold
        assert len(psr.y_hat) == 0


class TestEvaluate:
    def test_perfect_prediction(self):
        # id=3 is "Install front chassis" — a valid step in the real proc_info.
        gt   = [{"frame": 10, "id": 3, "conf": 1.0}]
        pred = [{"frame": 12, "id": 3, "conf": 1.0}]
        m = evaluate(gt, pred, PROC_INFO)
        assert m["pos"] == 1.0
        assert m["f1"] > 0.0

    def test_empty_gt_empty_pred(self):
        m = evaluate([], [], PROC_INFO)
        assert m["pos"] == 1.0
        assert m["f1"] == 1.0

    def test_empty_pred_has_fn(self):
        gt = [{"frame": 10, "id": 3, "conf": 1.0}]
        m = evaluate(gt, [], PROC_INFO)
        assert m["system_FNs"] == 1
        assert m["f1"] < 1.0


class TestCATEGORIES:
    def test_length(self):
        assert len(CATEGORIES) == 24

    def test_first_is_background(self):
        assert CATEGORIES[0] == "background"

    def test_last_is_error(self):
        assert CATEGORIES[23] == "error_state"

    def test_state_lengths(self):
        for cat in CATEGORIES[1:23]:
            assert len(cat) == 11, f"State {cat!r} is not 11 chars"
