"""psr.py — Procedure Step Recognition algorithms (B1, B2, B3).

Ported from IndustReal/PSR/psr_utils.py (Apache 2.0).
Key changes vs. original:
  - Replaced weighted_levenshtein C extension with pure-Python weighted DamLev.
  - Removed all CV2 / video-rendering code (display is handled by egg_builder).
  - Accepts data already loaded as Python lists; no file I/O here.
"""
from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional

# ---------------------------------------------------------------------------
# Assembly state category strings (index → binary state string, 11 components)
# ---------------------------------------------------------------------------
CATEGORIES: list[str] = [
    "background",     # 0
    "10000000000",    # 1
    "10010010000",    # 2
    "10010100000",    # 3
    "10010110000",    # 4
    "11100000000",    # 5
    "11110010000",    # 6
    "11110100000",    # 7
    "11110110000",    # 8
    "11110111100",    # 9
    "11110111110",    # 10
    "11110110001",    # 11
    "11110111101",    # 12
    "11110111111",    # 13
    "11110101111",    # 14
    "11110011111",    # 15
    "11110011110",    # 16
    "11110101110",    # 17
    "11100001110",    # 18
    "11101101110",    # 19
    "11101011110",    # 20
    "11101111110",    # 21
    "11101111111",    # 22
    "error_state",    # 23
]

N_COMPONENTS = 11   # bits in each state string

FPS = 10


# ---------------------------------------------------------------------------
# Pure-Python weighted Damerau-Levenshtein (no C extension required)
# Costs match the original: delete=1, insert=1, substitute=2, transpose=1.
# Substitution cost of 2 is equivalent to delete+insert, effectively
# eliminating substitutions as an edit operation (per the IndustReal paper).
# ---------------------------------------------------------------------------

def _weighted_dam_lev(s: list, t: list) -> float:
    n, m = len(s), len(t)
    if n == 0:
        return float(m)
    if m == 0:
        return float(n)

    d = [[0.0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        d[i][0] = float(i)
    for j in range(m + 1):
        d[0][j] = float(j)

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            sub_cost = 0.0 if s[i - 1] == t[j - 1] else 2.0
            d[i][j] = min(
                d[i - 1][j] + 1.0,          # delete
                d[i][j - 1] + 1.0,          # insert
                d[i - 1][j - 1] + sub_cost, # match / substitute
            )
            # transposition
            if i > 1 and j > 1 and s[i - 1] == t[j - 2] and s[i - 2] == t[j - 1]:
                d[i][j] = min(d[i][j], d[i - 2][j - 2] + 1.0)

    return d[n][m]


def procedure_order_similarity(gt_order: list, pred_order: list) -> float:
    """POS metric (Section 3.2.1 of the IndustReal paper)."""
    if len(gt_order) == 0:
        return 1.0 if len(pred_order) == 0 else 0.0
    distance = _weighted_dam_lev(gt_order, pred_order)
    return 1.0 - min(distance / len(gt_order), 1.0)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def state_string_to_list(state_str: str) -> list:
    """'11010…' → [1, 1, 0, 1, 0, …]"""
    return [int(c) for c in state_str if c in "01"]


def make_entry(frame: int, action_id: int, proc_info: list, conf: float = 1.0) -> dict:
    """Create a PSR prediction entry. conf=1 → observed, conf=0 → implied."""
    return {
        "frame": frame,
        "id": action_id,
        "description": proc_info[action_id]["description"],
        "conf": conf,
    }


def convert_states_to_steps(
    prev: list, curr: list, frame: int, proc_info: list, conf: float = 1.0
) -> tuple[list, int]:
    """Translate a (prev_state, curr_state) pair into procedure step entries.

    Returns (actions, n_error_steps).
    """
    actions = []
    n_error_steps = 0
    for k, (p, c) in enumerate(zip(prev, curr)):
        if p == c:
            continue
        if p == -1 and c == 0:
            continue  # undoing an error is not completing a step
        elif p == -1 and c == 1:
            action_id = k * 3 + 0   # corrected from error
        elif p == 0 and c == -1:
            action_id = k * 3 + 1   # incorrectly installed
            n_error_steps += 1
        elif p == 0 and c == 1:
            action_id = k * 3 + 0   # correctly installed
        elif p == 1 and c == -1:
            action_id = k * 3 + 1   # went wrong from correct state
            n_error_steps += 1
        elif p == 1 and c == 0:
            action_id = k * 3 + 2   # removed
        else:
            continue
        actions.append(make_entry(frame, action_id, proc_info, conf))
    return actions, n_error_steps


def get_highest_conf_prediction(predictions: list) -> tuple:
    best = max(predictions, key=lambda p: p[1])
    return best[0], best[1]


# ---------------------------------------------------------------------------
# PSR Baseline 1 — Naive
# ---------------------------------------------------------------------------

class NaivePSR:
    """B1: each new detected state triggers completion of all steps required
    to reach it from the previous state."""

    def __init__(self, proc_info: list, conf_threshold: float = 0.5):
        self.proc_info = proc_info
        self.thresh = conf_threshold
        self.current_state: Optional[list] = None
        self.current_state_str: Optional[str] = None
        self.y_hat: list = []

    def update(self, preds: list, frame_n: int):
        if not preds:
            return
        pred_class, conf = get_highest_conf_prediction(preds)
        pred_state_str = CATEGORIES[int(pred_class)]

        if self.current_state is None:
            if pred_state_str not in ("background", "error_state"):
                self.current_state = state_string_to_list(pred_state_str)
                self.current_state_str = pred_state_str
            return

        if pred_state_str in (self.current_state_str, "error_state"):
            return
        if conf <= self.thresh:
            return

        pred_state = state_string_to_list(pred_state_str)
        actions, _ = convert_states_to_steps(
            self.current_state, pred_state, frame_n, self.proc_info, conf=1.0
        )
        self.y_hat.extend(actions)
        self.current_state_str = pred_state_str
        self.current_state = pred_state


# ---------------------------------------------------------------------------
# PSR Baselines 2 & 3 — Accumulated Confidence
# ---------------------------------------------------------------------------

class AccumulatedConfidencePSR:
    """B2/B3: accumulate detection confidences per step over time.

    procedure=None → B2 (no procedural constraint).
    procedure='assy'|'main' → B3 (constrained to expected steps).
    """

    def __init__(
        self,
        proc_info: list,
        cum_conf_threshold: float = 8.0,
        cum_decay: float = 0.75,
        procedure: Optional[str] = None,
    ):
        self.proc_info = proc_info
        self.cum_threshold = cum_conf_threshold
        self.decay = cum_decay
        self.procedure = procedure

        self.cum_confs = np.zeros(len(proc_info))
        self.y_hat: list = []
        self.frame_n = -1
        self._updated_idxes: list = []
        self._all_idxes = list(range(len(proc_info)))

        if procedure is None:
            self.expected_actions = self._all_idxes.copy()
            self.current_state: Optional[list] = None
            self.current_state_str: Optional[str] = None
        else:
            key = f"expected_in_{procedure}"
            self.expected_actions = [a["id"] for a in proc_info if a[key]]
            self.current_state_str = "10000000000" if procedure == "assy" else "11110111111"
            self.current_state = state_string_to_list(self.current_state_str)

    def update(self, preds: list, frame_n: int):
        self.frame_n = frame_n

        if preds:
            pred_class, pred_conf = preds[0][0], preds[0][1]
            pred_state_str = CATEGORIES[int(pred_class)]

            if pred_state_str not in ("background", "error_state"):
                pred_state = state_string_to_list(pred_state_str)

                if self.current_state is None:
                    self.current_state = pred_state
                    self.current_state_str = pred_state_str
                else:
                    suggested, _ = convert_states_to_steps(
                        self.current_state, pred_state, frame_n, self.proc_info, conf=1.0
                    )
                    if suggested:
                        self._accumulate(suggested, pred_conf)
                        self._check_completed()

        self._tick()

    def _accumulate(self, actions: list, conf: float):
        for a in actions:
            self.cum_confs[a["id"]] += conf
            self._updated_idxes.append(a["id"])

    def _tick(self):
        for idx in self._all_idxes:
            if idx not in self._updated_idxes:
                self.cum_confs[idx] *= self.decay
        self._updated_idxes = []

    def _check_completed(self):
        triggered = list(np.nonzero(self.cum_confs > self.cum_threshold)[0])
        for idx in triggered:
            if idx in self.expected_actions:
                self._process(idx)
            else:
                self.cum_confs[idx] = 0.0

    def _process(self, idx: int):
        self.cum_confs[idx] = 0.0
        state_idx = self.proc_info[idx]["state_idx"]
        if self.proc_info[idx]["install"]:
            self.current_state[state_idx] = 1
        else:
            self.current_state[state_idx] = 0
        self.y_hat.append(make_entry(self.frame_n, idx, self.proc_info))


# ---------------------------------------------------------------------------
# Evaluation metrics
# ---------------------------------------------------------------------------

def _match_indices(idxes_a, times_a_arr, idxes_b, times_b_arr):
    """Match each b index to the temporally closest a index (one-to-one)."""
    assert len(idxes_a) >= len(idxes_b)
    avail = np.ones(len(times_a_arr)) * 1e9
    for i in idxes_a:
        avail[i] = times_a_arr[i]
    matched = []
    for ib in idxes_b:
        t_diff = avail - times_b_arr[ib]
        t_diff_pen = np.where(t_diff >= 0, t_diff, np.inf)
        best = int(np.argmin(t_diff_pen))
        matched.append(best)
        avail[best] = 1e9
    return matched


def evaluate(gt: list, pred: list, proc_info: list) -> dict:
    """Compute POS, F1, and average delay between GT and predictions.

    gt / pred: lists of dicts with keys 'frame', 'id', 'conf'.
    """
    if not gt:
        return {"pos": 1.0, "f1": 1.0 if not pred else 0.0, "avg_delay_s": 0.0,
                "system_TPs": 0, "system_FPs": len(pred), "system_FNs": 0}

    gt_times = np.array([e["frame"] for e in gt], dtype=int)
    gt_ids   = np.array([e["id"]    for e in gt], dtype=int)
    pred_times = np.array([e["frame"] for e in pred], dtype=int) if pred else np.array([], dtype=int)
    pred_ids   = np.array([e["id"]    for e in pred], dtype=int) if pred else np.array([], dtype=int)

    sys_FPs = sys_FNs = 0
    delays = np.full(len(gt_times), np.nan)

    for step in proc_info:
        sid = step["id"]
        ig = list(np.where(gt_ids == sid)[0])
        ip = list(np.where(pred_ids == sid)[0])

        if not ig and ip:
            sys_FPs += len(ip)
        elif ig and not ip:
            sys_FNs += len(ig)
        else:
            if len(ig) > len(ip):
                sys_FNs += len(ig) - len(ip)
                ig = _match_indices(ig, gt_times, ip, pred_times)
            elif len(ip) > len(ig):
                sys_FPs += len(ip) - len(ig)
                ip = _match_indices(ip, pred_times, ig, gt_times)

            for i_gt, i_pred in zip(ig, ip):
                delta = int(pred_times[i_pred]) - int(gt_times[i_gt])
                if delta < 0:
                    sys_FPs += 1
                else:
                    delays[i_gt] = delta

    pos = procedure_order_similarity(list(gt_ids), list(pred_ids))
    sys_TPs = max(0, len(pred_ids) - sys_FPs)
    denom = sys_TPs + sys_FNs + sys_FPs
    f1 = (2 * sys_TPs) / (2 * sys_TPs + sys_FNs + sys_FPs + 1e-9) if denom else 0.0
    avg_delay_frames = float(np.nanmean(delays)) if not np.all(np.isnan(delays)) else np.nan
    avg_delay_s = avg_delay_frames / FPS if not np.isnan(avg_delay_frames) else np.nan

    return {
        "pos": round(pos, 4),
        "f1": round(f1, 4),
        "avg_delay_s": round(avg_delay_s, 2) if not np.isnan(avg_delay_s) else None,
        "system_TPs": int(sys_TPs),
        "system_FPs": int(sys_FPs),
        "system_FNs": int(sys_FNs),
    }


# ---------------------------------------------------------------------------
# Top-level runner
# ---------------------------------------------------------------------------

def run_psr(
    asd_predictions: list,
    proc_info: list,
    implementation: str = "expected",
    procedure: Optional[str] = None,
    cum_conf_threshold: float = 8.0,
    cum_decay: float = 0.75,
    conf_threshold: float = 0.5,
) -> list:
    """Run one PSR implementation over a sequence of per-frame ASD predictions.

    asd_predictions: list of length n_frames; each element is a list of
                     [pred_class, conf, [x, y, w, h]] prediction tuples.
    Returns y_hat: list of recognised step dicts.
    """
    if implementation == "naive":
        psr = NaivePSR(proc_info, conf_threshold=conf_threshold)
    elif implementation in ("confidence", "expected"):
        proc_arg = procedure if implementation == "expected" else None
        psr = AccumulatedConfidencePSR(
            proc_info,
            cum_conf_threshold=cum_conf_threshold,
            cum_decay=cum_decay,
            procedure=proc_arg,
        )
    else:
        raise ValueError(f"Unknown PSR implementation: {implementation!r}")

    for frame_n, frame_preds in enumerate(asd_predictions):
        psr.update(frame_preds, frame_n)

    return psr.y_hat
