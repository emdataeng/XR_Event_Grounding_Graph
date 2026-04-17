"""detection_groups.py — Multi-pass detection group support (Phase 1).

Solves token competition between object classes of different semantic roles
(e.g. "hand" fighting against "red block. blue block." in a single prompt).
Each group runs a separate detector pass with its own prompt subset, then
results are merged and deduplicated.

Config format (pipeline.yaml → detection_groups):

    detection_groups:
      hands:
        enabled: true
        classes: ["hand"]          # keys in object_vocabulary
      workpieces:
        enabled: true
        classes: ["red_lego", "blue_lego"]
      tools:
        enabled: false
        classes: []

If detection_groups is absent, stage 05 uses single-pass behaviour unchanged.

Merging strategy
----------------
1.  Each enabled group is run as a separate detector pass.
2.  Within each pass, standard postprocess_detections() applies (vocab
    mapping + confidence filter + class-aware NMS + area filter).
3.  After all passes, a final cross-pass NMS is applied to remove
    duplicate boxes that span multiple groups (rare but possible).
4.  Each observation is tagged with detector_group and detector_pass_id
    for full provenance.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .vocabulary import Vocabulary, VocabEntry


# ── Data classes ──────────────────────────────────────────────────────────────

@dataclass
class DetectionGroup:
    """One detection pass configuration."""
    name: str                    # e.g. "hands"
    classes: List[str]           # canonical class names in this group
    enabled: bool = True
    prompt_override: Optional[str] = None  # if set, use this prompt directly
    pass_id: str = "pass_00"     # set externally when building from config


@dataclass
class GroupPass:
    """A detector run for one group: the group config + resolved prompt."""
    group: DetectionGroup
    vocab: Vocabulary            # sub-vocabulary for this group
    prompt: str                  # resolved detection prompt


# ── Config parsing ────────────────────────────────────────────────────────────

def parse_detection_groups(
    cfg: Dict[str, Any],
    base_vocab: Vocabulary,
) -> List[GroupPass]:
    """Parse detection_groups from pipeline config.

    Returns an ordered list of GroupPass objects (one per enabled group).
    Returns an empty list if detection_groups is absent → caller uses
    single-pass.

    Parameters
    ----------
    cfg :        Full pipeline config dict.
    base_vocab : Vocabulary built from the full object_vocabulary.  Used to
                 resolve which VocabEntry each class name maps to.
    """
    raw_groups = cfg.get("detection_groups")
    if not raw_groups:
        return []

    passes: List[GroupPass] = []
    for pass_idx, (group_name, spec) in enumerate(raw_groups.items()):
        if not isinstance(spec, dict):
            continue
        enabled = bool(spec.get("enabled", True))
        if not enabled:
            continue

        classes: List[str] = list(spec.get("classes") or [])
        if not classes:
            continue  # skip empty groups

        prompt_override: Optional[str] = spec.get("prompt_override")

        group = DetectionGroup(
            name=group_name,
            classes=classes,
            enabled=True,
            prompt_override=prompt_override,
            pass_id=f"pass_{pass_idx:02d}",
        )

        sub_vocab = _build_sub_vocab(group, base_vocab)
        prompt = prompt_override or _build_group_prompt(sub_vocab)

        passes.append(GroupPass(group=group, vocab=sub_vocab, prompt=prompt))

    return passes


# ── Sub-vocabulary builder ────────────────────────────────────────────────────

def _build_sub_vocab(group: DetectionGroup, base_vocab: Vocabulary) -> Vocabulary:
    """Build a Vocabulary containing only the entries listed in group.classes."""
    # Access the internal entry list from the base vocabulary.
    # We rely on the fact that Vocabulary stores _entries as a list of VocabEntry.
    base_entries: List[VocabEntry] = base_vocab._entries  # type: ignore[attr-defined]

    group_class_set = set(group.classes)
    selected = [e for e in base_entries if e.canonical in group_class_set]

    # Warn about unmapped classes (they won't produce detections)
    known = {e.canonical for e in base_entries}
    for cls in group.classes:
        if cls not in known:
            import warnings
            warnings.warn(
                f"detection_groups.{group.name}: class '{cls}' not found in "
                "object_vocabulary — it will be ignored.",
                UserWarning,
                stacklevel=3,
            )

    return Vocabulary(selected)


def _build_group_prompt(sub_vocab: Vocabulary) -> str:
    """Build a Grounding DINO dot-separated prompt for a sub-vocabulary."""
    if sub_vocab.is_empty:
        return "object."
    return sub_vocab.build_prompt()


# ── Cross-pass NMS ────────────────────────────────────────────────────────────

def cross_pass_nms(
    all_detections: List[Dict[str, Any]],
    iou_threshold: float = 0.5,
) -> List[Dict[str, Any]]:
    """Remove duplicates produced by multiple detection passes.

    Applies class-aware NMS across observations from all passes.  Two
    observations are considered duplicates if they share the same
    canonical_class and their pixel-space bounding boxes have IoU ≥ iou_threshold.
    Higher-confidence observation wins.

    Parameters
    ----------
    all_detections : list of observation dicts (as returned by
                     _detection_to_observation in script 05, before
                     stripping private keys).
    iou_threshold  : IoU threshold above which the lower-confidence detection
                     is suppressed.  0 disables cross-pass NMS.

    Returns
    -------
    Filtered list of observation dicts.
    """
    if iou_threshold <= 0 or len(all_detections) <= 1:
        return all_detections

    # Group by (frame_idx, canonical_class) for efficient comparison
    from collections import defaultdict
    groups: Dict[Tuple, List[int]] = defaultdict(list)
    for i, obs in enumerate(all_detections):
        key = (
            obs.get("frame_idx"),
            obs.get("canonical_class") or obs.get("semantic_class"),
        )
        groups[key].append(i)

    keep = set(range(len(all_detections)))

    for indices in groups.values():
        if len(indices) <= 1:
            continue
        # Sort by confidence descending within this group
        indices_sorted = sorted(
            indices,
            key=lambda i: float(all_detections[i].get("confidence", 0)),
            reverse=True,
        )
        suppressed: set = set()
        for i_idx, i in enumerate(indices_sorted):
            if i in suppressed:
                continue
            obs_i = all_detections[i]
            box_i = _get_bbox(obs_i)
            if box_i is None:
                continue
            for j in indices_sorted[i_idx + 1:]:
                if j in suppressed:
                    continue
                obs_j = all_detections[j]
                box_j = _get_bbox(obs_j)
                if box_j is None:
                    continue
                if _iou(box_i, box_j) >= iou_threshold:
                    suppressed.add(j)
                    keep.discard(j)

    return [all_detections[i] for i in range(len(all_detections)) if i in keep]


# ── IoU helpers ───────────────────────────────────────────────────────────────

def _get_bbox(obs: Dict[str, Any]) -> Optional[Tuple[float, float, float, float]]:
    """Extract (x1, y1, x2, y2) from an observation dict, or None."""
    try:
        x1 = float(obs["bbox_x1"])
        y1 = float(obs["bbox_y1"])
        x2 = float(obs["bbox_x2"])
        y2 = float(obs["bbox_y2"])
        return (x1, y1, x2, y2)
    except (KeyError, TypeError, ValueError):
        return None


def _iou(a: Tuple[float, float, float, float],
         b: Tuple[float, float, float, float]) -> float:
    """Compute 2D IoU between two (x1, y1, x2, y2) boxes."""
    ix1 = max(a[0], b[0])
    iy1 = max(a[1], b[1])
    ix2 = min(a[2], b[2])
    iy2 = min(a[3], b[3])
    inter_w = max(0.0, ix2 - ix1)
    inter_h = max(0.0, iy2 - iy1)
    inter = inter_w * inter_h
    if inter == 0.0:
        return 0.0
    area_a = max(0.0, a[2] - a[0]) * max(0.0, a[3] - a[1])
    area_b = max(0.0, b[2] - b[0]) * max(0.0, b[3] - b[1])
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0
