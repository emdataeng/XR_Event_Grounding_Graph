"""thesis_constraint_reasoner.py - Thesis Layer 3 rule evaluation.

This module implements Algorithm 1 from the thesis design: evaluate explicit
rules over the active predicate set P_t and emit interval-scoped constraints
and incompatibilities. It is intentionally independent from Layer 4.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import pandas as pd
import yaml


CONSTRAINT_COLS = [
    "constraint_id", "name", "args", "conf", "start_frame_idx", "end_frame_idx",
    "rule_id", "supporting_predicates", "aggregation",
]

INCOMPATIBILITY_COLS = [
    "incompatibility_id", "name", "action", "args", "conf", "start_frame_idx",
    "end_frame_idx", "rule_id", "reason", "supporting_predicates",
]


@dataclass(frozen=True)
class PredicateInstance:
    fact_id: str
    name: str
    args: Tuple[str, ...]
    conf: float
    start_frame_idx: int
    end_frame_idx: int
    source: str = ""


@dataclass
class RuleMatch:
    name: str
    args: Tuple[str, ...]
    conf: float
    rule_id: str
    supporting_predicates: Tuple[str, ...]
    aggregation: str = "min"
    action: str = ""
    reason: str = ""


@dataclass
class OpenInterval:
    match: RuleMatch
    start_frame_idx: int
    end_frame_idx: int

    def extend(self, frame_idx: int, match: RuleMatch) -> None:
        self.end_frame_idx = frame_idx
        self.match = match


@dataclass
class EntityMeta:
    class_label: str = ""
    semantic_type: str = ""
    role: str = ""
    entity_type: str = ""
    existence_confidence: Optional[float] = None


@dataclass
class ReasoningResult:
    constraints: pd.DataFrame
    incompatibilities: pd.DataFrame
    diagnostics: Dict[str, Any] = field(default_factory=dict)


def load_yaml(path: Path | str) -> Dict[str, Any]:
    """Load a YAML file, returning an empty dict when the file is absent."""
    p = Path(path)
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_scene_state_package(path: Path | str) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def run_layer3_reasoning(
    state_facts: pd.DataFrame | Path | str,
    scene_state_package: Mapping[str, Any] | Path | str | None = None,
    domain_config: Mapping[str, Any] | Path | str | None = None,
    thesis_rules: Mapping[str, Any] | Path | str | None = None,
    include_ssp_predicates: bool = True,
) -> ReasoningResult:
    """Evaluate Layer 3 rules over active state facts.

    Parameters
    ----------
    state_facts:
        DataFrame or path to ``state_facts.csv``. Rows form the time-scoped
        predicate base used to construct P_t.
    scene_state_package:
        Dict or path to ``scene_state_package.json``. Used for metadata such as
        class labels and, when ``include_ssp_predicates`` is true, supplemental
        relations/hypotheses not already represented in ``state_facts``.
    domain_config:
        Dict or path to a domain YAML. Used only for metadata such as object
        roles and optional compatibility defaults.
    thesis_rules:
        Dict or path to ``thesis_rules.yaml``. Expected top-level keys:
        ``inference_rules``/``rules`` and ``compatibility_rules``.

    Returns
    -------
    ReasoningResult containing ``constraints`` and ``incompatibilities`` data
    frames with interval-scoped outputs.
    """
    facts_df = _load_facts_df(state_facts)
    rules_cfg = _load_mapping(thesis_rules)
    ssp = _load_mapping_or_json(scene_state_package)
    domain = _load_mapping(domain_config)
    entity_meta = _build_entity_metadata(ssp, domain)

    state_fact_instances = _normalise_facts(facts_df)
    ssp_fact_instances = (
        _normalise_ssp_predicates(ssp, facts_df, state_fact_instances)
        if include_ssp_predicates else []
    )
    facts = _merge_predicate_sources(state_fact_instances, ssp_fact_instances)
    diagnostics = _build_source_diagnostics(
        state_fact_instances, ssp_fact_instances, facts, rules_cfg
    )
    if not facts:
        return ReasoningResult(
            constraints=pd.DataFrame(columns=CONSTRAINT_COLS),
            incompatibilities=pd.DataFrame(columns=INCOMPATIBILITY_COLS),
            diagnostics=diagnostics,
        )

    frames = _frame_domain(facts)
    inference_rules = _rules_from_config(rules_cfg, ("constraint_rules", "inference_rules", "rules"))
    compatibility_rules = _rules_from_config(rules_cfg, ("compatibility_rules",))

    open_constraints: Dict[Tuple[Any, ...], OpenInterval] = {}
    open_incompat: Dict[Tuple[Any, ...], OpenInterval] = {}
    closed_constraints: List[OpenInterval] = []
    closed_incompat: List[OpenInterval] = []

    facts_sorted = sorted(facts, key=lambda p: (p.start_frame_idx, p.end_frame_idx))

    for t in frames:
        active = [
            p for p in facts_sorted
            if p.start_frame_idx <= t <= p.end_frame_idx
        ]
        constraint_matches = _evaluate_rules(
            inference_rules, active, entity_meta, output_kind="constraint"
        )
        incompat_matches = _evaluate_rules(
            compatibility_rules, active, entity_meta, output_kind="incompatibility"
        )

        _advance_intervals(
            open_constraints, closed_constraints, constraint_matches, t,
            key_fn=_constraint_key,
        )
        _advance_intervals(
            open_incompat, closed_incompat, incompat_matches, t,
            key_fn=_incompatibility_key,
        )

    closed_constraints.extend(open_constraints.values())
    closed_incompat.extend(open_incompat.values())

    constraints_df = _constraints_to_df(closed_constraints)
    incompat_df = _incompatibilities_to_df(closed_incompat)
    return ReasoningResult(
        constraints=constraints_df,
        incompatibilities=incompat_df,
        diagnostics=diagnostics,
    )


def write_layer3_outputs(
    result: ReasoningResult,
    constraints_path: Path | str,
    incompatibilities_path: Path | str,
) -> None:
    """Write Layer 3 outputs to CSV files."""
    constraints_p = Path(constraints_path)
    incompat_p = Path(incompatibilities_path)
    constraints_p.parent.mkdir(parents=True, exist_ok=True)
    incompat_p.parent.mkdir(parents=True, exist_ok=True)
    result.constraints.to_csv(constraints_p, index=False)
    result.incompatibilities.to_csv(incompat_p, index=False)


def _load_facts_df(state_facts: pd.DataFrame | Path | str) -> pd.DataFrame:
    if isinstance(state_facts, pd.DataFrame):
        return state_facts.copy()
    return pd.read_csv(state_facts)


def _load_mapping(value: Mapping[str, Any] | Path | str | None) -> Dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, Mapping):
        return dict(value)
    return load_yaml(value)


def _load_mapping_or_json(value: Mapping[str, Any] | Path | str | None) -> Dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, Mapping):
        return dict(value)
    path = Path(value)
    if not path.exists():
        return {}
    if path.suffix.lower() == ".json":
        return load_scene_state_package(path)
    return load_yaml(path)


def _normalise_facts(facts_df: pd.DataFrame) -> List[PredicateInstance]:
    if facts_df.empty:
        return []

    required = {"predicate", "confidence", "start_frame_idx", "end_frame_idx"}
    missing = required - set(facts_df.columns)
    if missing:
        raise ValueError(f"state_facts missing required columns: {sorted(missing)}")

    out: List[PredicateInstance] = []
    for idx, row in facts_df.sort_values("start_frame_idx").iterrows():
        args = tuple(
            str(v) for v in (row.get("subject_id"), row.get("object_id"))
            if _valid_value(v)
        )
        out.append(PredicateInstance(
            fact_id=str(row.get("fact_id", f"fact_row_{idx}")),
            name=str(row.get("predicate", "")),
            args=args,
            conf=float(row.get("confidence", 0.0)),
            start_frame_idx=int(row.get("start_frame_idx", 0)),
            end_frame_idx=int(row.get("end_frame_idx", row.get("start_frame_idx", 0))),
            source=str(row.get("source_stage", row.get("source", ""))),
        ))
    return out


def _normalise_ssp_predicates(
    ssp: Mapping[str, Any],
    facts_df: pd.DataFrame,
    state_facts: Sequence[PredicateInstance],
) -> List[PredicateInstance]:
    """Convert SSP relations/hypotheses into Layer 3 predicate instances.

    SSP stores wall-clock validity intervals, while Layer 3 operates on frame
    indices. Event-backed SSP predicates are aligned through source_event_id and
    state_facts.evidence_refs. Live geometry snapshots are treated as point facts
    at the last known state-facts frame.
    """
    if not ssp:
        return []

    event_frames = _event_frame_index(facts_df)
    last_frame = max((p.end_frame_idx for p in state_facts), default=0)

    out: List[PredicateInstance] = []
    for section, id_key, source in (
        ("relations", "relation_id", "ssp_relation"),
        ("hypotheses", "hypothesis_id", "ssp_hypothesis"),
    ):
        for idx, item in enumerate(ssp.get(section, []) or [], start=1):
            if not isinstance(item, Mapping):
                continue
            predicate = str(item.get("predicate", ""))
            if not predicate:
                continue
            args_raw = item.get("arguments", [])
            if not isinstance(args_raw, list):
                continue
            interval = _ssp_frame_interval(item, event_frames, last_frame)
            if interval is None:
                continue
            start_frame, end_frame = interval
            ssp_id = str(item.get(id_key, f"{section}_{idx:04d}"))
            out.append(PredicateInstance(
                fact_id=f"{source}:{ssp_id}",
                name=predicate,
                args=tuple(str(v) for v in args_raw if _valid_value(v)),
                conf=float(item.get("confidence", 0.0)),
                start_frame_idx=start_frame,
                end_frame_idx=end_frame,
                source=source,
            ))
    return out


def _event_frame_index(facts_df: pd.DataFrame) -> Dict[str, Tuple[int, int]]:
    if facts_df.empty or "evidence_refs" not in facts_df.columns:
        return {}

    index: Dict[str, Tuple[int, int]] = {}
    for _, row in facts_df.iterrows():
        refs = _parse_evidence_refs(row.get("evidence_refs"))
        if not refs:
            continue
        start = int(row.get("start_frame_idx", 0))
        end = int(row.get("end_frame_idx", start))
        for ref in refs:
            prev = index.get(ref)
            if prev is None:
                index[ref] = (start, end)
            else:
                index[ref] = (min(prev[0], start), max(prev[1], end))
    return index


def _parse_evidence_refs(value: Any) -> List[str]:
    if not _valid_value(value):
        return []
    if isinstance(value, list):
        return [str(v) for v in value if _valid_value(v)]
    try:
        decoded = json.loads(str(value))
    except (TypeError, json.JSONDecodeError):
        return []
    if not isinstance(decoded, list):
        return []
    return [str(v) for v in decoded if _valid_value(v)]


def _ssp_frame_interval(
    item: Mapping[str, Any],
    event_frames: Mapping[str, Tuple[int, int]],
    last_frame: int,
) -> Optional[Tuple[int, int]]:
    event_id = item.get("source_event_id")
    if _valid_value(event_id) and str(event_id) in event_frames:
        return event_frames[str(event_id)]

    valid_time = item.get("valid_time")
    if isinstance(valid_time, Mapping) and valid_time.get("start") == valid_time.get("end"):
        return last_frame, last_frame
    return None


def _merge_predicate_sources(
    state_facts: Sequence[PredicateInstance],
    ssp_facts: Sequence[PredicateInstance],
) -> List[PredicateInstance]:
    merged = list(state_facts)
    for ssp_fact in ssp_facts:
        if any(
            _same_predicate_instance(existing, ssp_fact)
            and _intervals_overlap(existing, ssp_fact)
            for existing in state_facts
        ):
            continue
        merged.append(ssp_fact)
    return merged


def _same_predicate_instance(left: PredicateInstance, right: PredicateInstance) -> bool:
    return left.name == right.name and left.args == right.args


def _intervals_overlap(left: PredicateInstance, right: PredicateInstance) -> bool:
    return left.start_frame_idx <= right.end_frame_idx and right.start_frame_idx <= left.end_frame_idx


def _build_source_diagnostics(
    state_facts: Sequence[PredicateInstance],
    ssp_facts: Sequence[PredicateInstance],
    merged_facts: Sequence[PredicateInstance],
    rules_cfg: Mapping[str, Any],
) -> Dict[str, Any]:
    state_preds = {p.name for p in state_facts}
    ssp_preds = {p.name for p in ssp_facts}
    imported_ssp = [p for p in merged_facts if p.source in {"ssp_relation", "ssp_hypothesis"}]
    skipped_overlap = [
        p for p in ssp_facts
        if any(
            _same_predicate_instance(existing, p) and _intervals_overlap(existing, p)
            for existing in state_facts
        )
    ]

    confidence_diffs = []
    for ssp_fact in skipped_overlap:
        for state_fact in state_facts:
            if not _same_predicate_instance(state_fact, ssp_fact):
                continue
            if not _intervals_overlap(state_fact, ssp_fact):
                continue
            delta = abs(state_fact.conf - ssp_fact.conf)
            if delta >= 0.2:
                confidence_diffs.append({
                    "predicate": ssp_fact.name,
                    "args": list(ssp_fact.args),
                    "state_fact_id": state_fact.fact_id,
                    "ssp_fact_id": ssp_fact.fact_id,
                    "state_conf": round(state_fact.conf, 3),
                    "ssp_conf": round(ssp_fact.conf, 3),
                    "delta": round(delta, 3),
                })
            break

    available_preds = {p.name for p in merged_facts}
    virtual_preds = {"isA"}
    rule_antecedents = _rule_antecedent_predicates(rules_cfg)

    return {
        "state_predicates": sorted(state_preds),
        "ssp_predicates": sorted(ssp_preds),
        "available_predicates": sorted(available_preds | virtual_preds),
        "shared_predicates": sorted(state_preds & ssp_preds),
        "state_only_predicates": sorted(state_preds - ssp_preds),
        "ssp_only_predicates": sorted(ssp_preds - state_preds),
        "rule_antecedents": sorted(rule_antecedents),
        "missing_rule_antecedents": sorted(rule_antecedents - available_preds - virtual_preds),
        "imported_ssp_predicate_count": len(imported_ssp),
        "imported_ssp_predicates": sorted({p.name for p in imported_ssp}),
        "skipped_overlapping_ssp_count": len(skipped_overlap),
        "confidence_discrepancies": confidence_diffs,
    }


def _rule_antecedent_predicates(rules_cfg: Mapping[str, Any]) -> set:
    predicates = set()
    for section in ("constraint_rules", "inference_rules", "rules", "compatibility_rules"):
        rules = rules_cfg.get(section)
        if not isinstance(rules, list):
            continue
        for rule in rules:
            if not isinstance(rule, Mapping):
                continue
            conditions = rule.get("when", rule.get("conditions", rule.get("antecedents", [])))
            _collect_condition_predicates(conditions, predicates)
    return predicates


def _collect_condition_predicates(conditions: Any, predicates: set) -> None:
    if isinstance(conditions, Mapping):
        if "not" in conditions:
            _collect_condition_predicates(conditions.get("not"), predicates)
        pred = conditions.get("predicate", conditions.get("name"))
        if pred is not None:
            predicates.add(str(pred))
        return
    if isinstance(conditions, list):
        for condition in conditions:
            _collect_condition_predicates(condition, predicates)


def _frame_domain(facts: Sequence[PredicateInstance]) -> List[int]:
    return list(range(
        min(p.start_frame_idx for p in facts),
        max(p.end_frame_idx for p in facts) + 1,
    ))


def _rules_from_config(
    cfg: Mapping[str, Any],
    keys: Sequence[str],
) -> List[Dict[str, Any]]:
    for key in keys:
        val = cfg.get(key)
        if isinstance(val, list):
            return [dict(r) for r in val if isinstance(r, Mapping)]
    return []


def _evaluate_rules(
    rules: Sequence[Mapping[str, Any]],
    active: Sequence[PredicateInstance],
    entity_meta: Mapping[str, EntityMeta],
    output_kind: str,
) -> List[RuleMatch]:
    matches: List[RuleMatch] = []
    for rule in rules:
        if output_kind == "incompatibility" and "disallowed_pairs" in rule:
            matches.extend(_evaluate_disallowed_pair_rule(rule, active, entity_meta))
            continue

        threshold = float(rule.get("threshold", rule.get("min_conf", 0.0)))
        conditions = rule.get("when", rule.get("conditions", rule.get("antecedents", [])))
        bindings = _find_bindings(conditions, active, entity_meta)
        for binding, support in bindings:
            if not support:
                continue
            conf = min(p.conf for p in support)
            if conf < threshold:
                continue
            spec = _output_spec(rule, output_kind)
            name = str(spec.get("name", rule.get("name", rule.get("id", ""))))
            args = tuple(_resolve_arg(a, binding) for a in spec.get("args", rule.get("args", [])))
            rule_id = str(rule.get("rule_id", rule.get("id", name)))
            support_ids = tuple(p.fact_id for p in support)
            matches.append(RuleMatch(
                name=name,
                args=args,
                conf=conf,
                rule_id=rule_id,
                supporting_predicates=support_ids,
                aggregation=str(rule.get("aggregation", "min")),
                action=str(spec.get("action", rule.get("action", ""))),
                reason=str(spec.get("reason", rule.get("reason", ""))),
            ))
    return matches


def _output_spec(rule: Mapping[str, Any], output_kind: str) -> Mapping[str, Any]:
    if output_kind == "constraint":
        val = rule.get("consequents")
        if isinstance(val, list) and val and isinstance(val[0], Mapping):
            return val[0]
        for key in ("then", "infer", "constraint", "output"):
            val = rule.get(key)
            if isinstance(val, Mapping):
                return val
    else:
        for key in ("then", "incompatible", "incompatibility", "output"):
            val = rule.get(key)
            if isinstance(val, Mapping):
                return val
    return rule


def _evaluate_disallowed_pair_rule(
    rule: Mapping[str, Any],
    active: Sequence[PredicateInstance],
    entity_meta: Mapping[str, EntityMeta],
) -> List[RuleMatch]:
    """Evaluate compatibility rules expressed as disallowed class pairs."""
    pairs = rule.get("disallowed_pairs") or []
    if not isinstance(pairs, list):
        return []

    class_bindings = _active_class_bindings(active, entity_meta)
    output = rule.get("output") if isinstance(rule.get("output"), Mapping) else {}
    name = str(output.get("name", rule.get("name", "incompatibleAction")))
    action = str(rule.get("action", output.get("action", "")))
    reason = str(rule.get("reason", output.get("reason", "")))
    rule_id = str(rule.get("rule_id", rule.get("id", name)))
    conf = float(rule.get("confidence", rule.get("threshold", 1.0)))
    arg_spec = output.get("args", ["?x", "?y", action])

    matches: List[RuleMatch] = []
    for pair in pairs:
        if not isinstance(pair, list) or len(pair) != 2:
            continue
        left_class, right_class = str(pair[0]), str(pair[1])
        left_entities = class_bindings.get(left_class, [])
        right_entities = class_bindings.get(right_class, [])
        for left_id, left_support in left_entities:
            for right_id, right_support in right_entities:
                if left_id == right_id:
                    continue
                binding = {"x": left_id, "y": right_id}
                support = tuple(
                    p.fact_id for p in (left_support, right_support)
                    if p is not None
                )
                matches.append(RuleMatch(
                    name=name,
                    args=tuple(_resolve_arg(a, binding) for a in arg_spec),
                    conf=conf,
                    rule_id=rule_id,
                    supporting_predicates=support,
                    aggregation=str(rule.get("aggregation", "compatibility")),
                    action=action,
                    reason=reason,
                ))
    return matches


def _match_condition(
    condition: Mapping[str, Any],
    binding: Mapping[str, str],
    support: Sequence[PredicateInstance],
    active: Sequence[PredicateInstance],
    entity_meta: Mapping[str, EntityMeta],
) -> Iterable[Tuple[Dict[str, str], List[PredicateInstance]]]:
    if "not" in condition:
        inner = condition.get("not")
        if isinstance(inner, Mapping):
            has_match = any(_match_condition(inner, binding, support, active, entity_meta))
            if not has_match:
                yield dict(binding), list(support)
        return

    if "predicate" in condition or "name" in condition:
        pred_name = str(condition.get("predicate", condition.get("name", "")))
        expected_args = list(condition.get("args", []))
        if pred_name == "isA":
            yield from _match_virtual_isa_condition(
                expected_args, binding, support, active, entity_meta
            )
            return

        for pred in active:
            if pred.name != pred_name:
                continue
            new_binding = _bind_args(expected_args, pred.args, binding)
            if new_binding is not None:
                yield new_binding, list(support) + [pred]
        return

    if any(k in condition for k in ("class", "semantic_type", "role", "entity_type")):
        var = str(condition.get("var", condition.get("entity", condition.get("arg", ""))))
        entity_id = _resolve_arg(var, binding)
        if not entity_id:
            return
        meta = entity_meta.get(entity_id, EntityMeta())
        if _metadata_condition_holds(condition, meta):
            yield dict(binding), list(support)
        return

    yield dict(binding), list(support)


def _match_virtual_isa_condition(
    expected_args: Sequence[Any],
    binding: Mapping[str, str],
    support: Sequence[PredicateInstance],
    active: Sequence[PredicateInstance],
    entity_meta: Mapping[str, EntityMeta],
) -> Iterable[Tuple[Dict[str, str], List[PredicateInstance]]]:
    for pred in active:
        if pred.name != "isA":
            continue
        new_binding = _bind_args(expected_args, pred.args, binding)
        if new_binding is not None:
            yield new_binding, list(support) + [pred]

    if len(expected_args) != 2:
        return

    # Virtual isA facts come from scene_state_package.entities metadata. This
    # keeps class identity decoupled from temporal state_facts.csv predicates.
    # TODO: Include entity existence/class confidence in rule confidence aggregation.
    entity_token, class_token = [str(v) for v in expected_args]
    entity_id = _resolve_arg(entity_token, binding)
    expected_class = _resolve_arg(class_token, binding)

    if entity_id:
        meta = entity_meta.get(entity_id, EntityMeta())
        for observed in _isa_observed_pairs(entity_id, meta):
            new_binding = _bind_args(expected_args, observed, binding)
            if new_binding is not None:
                yield new_binding, list(support)
        return

    for candidate_id, meta in entity_meta.items():
        if not _entity_matches_type(meta, expected_class):
            continue
        for observed in _isa_observed_pairs(candidate_id, meta):
            new_binding = _bind_args(expected_args, observed, binding)
            if new_binding is not None:
                yield new_binding, list(support)


def _isa_observed_pairs(entity_id: str, meta: EntityMeta) -> List[Tuple[str, str]]:
    pairs = []
    seen = set()
    for label in (meta.class_label, meta.semantic_type):
        if not label or label in seen:
            continue
        seen.add(label)
        pairs.append((entity_id, label))
    return pairs


def _entity_matches_type(meta: EntityMeta, expected_type: str) -> bool:
    if not expected_type:
        return bool(meta.class_label or meta.semantic_type)
    return expected_type in {meta.class_label, meta.semantic_type}


def _entity_type_labels(meta: EntityMeta) -> List[str]:
    labels = []
    seen = set()
    for label in (meta.class_label, meta.semantic_type):
        if not label or label in seen:
            continue
        seen.add(label)
        labels.append(label)
    return labels


def _entity_matches_expected(actual_values: Sequence[str], expected: Any) -> bool:
    if isinstance(expected, list):
        expected_values = {str(v) for v in expected}
    else:
        expected_values = {str(expected)}
    return bool(set(actual_values) & expected_values)


def _bind_entity_metadata(
    bindings: Dict[str, List[Tuple[str, Optional[PredicateInstance]]]],
    entity_id: str,
    meta: EntityMeta,
) -> None:
    for label in _entity_type_labels(meta):
        existing = {eid for eid, _ in bindings.get(label, [])}
        if entity_id not in existing:
            bindings.setdefault(label, []).append((entity_id, None))


def _metadata_values_for_key(meta: EntityMeta, key: str) -> List[str]:
    if key == "class":
        return _entity_type_labels(meta)
    if key == "semantic_type":
        return [meta.semantic_type] if meta.semantic_type else []
    if key == "role":
        return [meta.role] if meta.role else []
    if key == "entity_type":
        return [meta.entity_type] if meta.entity_type else []
    return []


def _active_class_bindings(
    active: Sequence[PredicateInstance],
    entity_meta: Mapping[str, EntityMeta],
) -> Dict[str, List[Tuple[str, Optional[PredicateInstance]]]]:
    bindings: Dict[str, List[Tuple[str, Optional[PredicateInstance]]]] = {}
    for pred in active:
        if pred.name == "isA" and len(pred.args) == 2:
            bindings.setdefault(pred.args[1], []).append((pred.args[0], pred))

    for entity_id, meta in entity_meta.items():
        _bind_entity_metadata(bindings, entity_id, meta)
    return bindings


def _find_bindings(
    conditions: Any,
    active: Sequence[PredicateInstance],
    entity_meta: Mapping[str, EntityMeta],
) -> List[Tuple[Dict[str, str], List[PredicateInstance]]]:
    if not isinstance(conditions, list):
        conditions = []

    states: List[Tuple[Dict[str, str], List[PredicateInstance]]] = [({}, [])]
    for condition in conditions:
        if not isinstance(condition, Mapping):
            continue
        next_states: List[Tuple[Dict[str, str], List[PredicateInstance]]] = []
        for binding, support in states:
            for new_binding, new_support in _match_condition(condition, binding, support, active, entity_meta):
                next_states.append((new_binding, new_support))
        states = _dedupe_states(next_states)
        if not states:
            return []
    return states


def _bind_args(
    expected: Sequence[Any],
    observed: Sequence[str],
    binding: Mapping[str, str],
) -> Optional[Dict[str, str]]:
    if expected and len(expected) != len(observed):
        return None
    if not expected:
        return dict(binding)

    out = dict(binding)
    for exp, obs in zip(expected, observed):
        token = str(exp)
        if _is_var(token):
            current = out.get(_var_name(token))
            if current is not None and current != obs:
                return None
            out[_var_name(token)] = obs
        elif token != obs:
            return None
    return out


def _metadata_condition_holds(condition: Mapping[str, Any], meta: EntityMeta) -> bool:
    for key in ("class", "semantic_type", "role", "entity_type"):
        if key not in condition:
            continue
        actual_values = _metadata_values_for_key(meta, key)
        if not _entity_matches_expected(actual_values, condition[key]):
            return False
    return True


def _build_entity_metadata(
    ssp: Mapping[str, Any],
    domain: Mapping[str, Any],
) -> Dict[str, EntityMeta]:
    class_to_role = {
        str(entry.get("canonical", "")): str(entry.get("role", ""))
        for entry in domain.get("object_classes", []) or []
        if isinstance(entry, Mapping)
    }
    class_to_semantic_type = {
        str(entry.get("canonical", "")): str(entry.get("semantic_type", ""))
        for entry in domain.get("object_classes", []) or []
        if isinstance(entry, Mapping)
    }
    meta: Dict[str, EntityMeta] = {}
    for entity in ssp.get("entities", []) or []:
        if not isinstance(entity, Mapping):
            continue
        entity_id = str(entity.get("entity_id", ""))
        class_label = str(entity.get("class_label", ""))
        meta[entity_id] = EntityMeta(
            class_label=class_label,
            semantic_type=class_to_semantic_type.get(class_label, ""),
            role=class_to_role.get(class_label, ""),
            entity_type=str(entity.get("entity_type", "")),
            existence_confidence=_optional_float(entity.get("existence_confidence")),
        )
    return meta


def _optional_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _advance_intervals(
    open_intervals: Dict[Tuple[Any, ...], OpenInterval],
    closed: List[OpenInterval],
    matches: Sequence[RuleMatch],
    frame_idx: int,
    key_fn,
) -> None:
    current = {key_fn(m): m for m in matches}

    for key in list(open_intervals.keys()):
        if key not in current:
            interval = open_intervals.pop(key)
            interval.end_frame_idx = frame_idx - 1
            closed.append(interval)

    for key, match in current.items():
        if key in open_intervals:
            open_intervals[key].extend(frame_idx, match)
        else:
            open_intervals[key] = OpenInterval(
                match=match,
                start_frame_idx=frame_idx,
                end_frame_idx=frame_idx,
            )


def _constraints_to_df(intervals: Sequence[OpenInterval]) -> pd.DataFrame:
    rows = []
    for i, interval in enumerate(intervals, start=1):
        m = interval.match
        rows.append({
            "constraint_id": f"constraint_{i:04d}",
            "name": m.name,
            "args": json.dumps(list(m.args)),
            "conf": round(float(m.conf), 3),
            "start_frame_idx": int(interval.start_frame_idx),
            "end_frame_idx": int(interval.end_frame_idx),
            "rule_id": m.rule_id,
            "supporting_predicates": json.dumps(list(m.supporting_predicates)),
            "aggregation": m.aggregation,
        })
    return pd.DataFrame(rows, columns=CONSTRAINT_COLS)


def _incompatibilities_to_df(intervals: Sequence[OpenInterval]) -> pd.DataFrame:
    rows = []
    for i, interval in enumerate(intervals, start=1):
        m = interval.match
        rows.append({
            "incompatibility_id": f"incompatibility_{i:04d}",
            "name": m.name,
            "action": m.action,
            "args": json.dumps(list(m.args)),
            "conf": round(float(m.conf), 3),
            "start_frame_idx": int(interval.start_frame_idx),
            "end_frame_idx": int(interval.end_frame_idx),
            "rule_id": m.rule_id,
            "reason": m.reason,
            "supporting_predicates": json.dumps(list(m.supporting_predicates)),
        })
    return pd.DataFrame(rows, columns=INCOMPATIBILITY_COLS)


def _constraint_key(match: RuleMatch) -> Tuple[Any, ...]:
    return (match.rule_id, match.name, match.args)


def _incompatibility_key(match: RuleMatch) -> Tuple[Any, ...]:
    return (match.rule_id, match.name, match.action, match.args, match.reason)


def _dedupe_states(
    states: Sequence[Tuple[Dict[str, str], List[PredicateInstance]]],
) -> List[Tuple[Dict[str, str], List[PredicateInstance]]]:
    seen = set()
    out = []
    for binding, support in states:
        key = (
            tuple(sorted(binding.items())),
            tuple(p.fact_id for p in support),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append((binding, support))
    return out


def _resolve_arg(value: Any, binding: Mapping[str, str]) -> str:
    token = str(value)
    if _is_var(token):
        return binding.get(_var_name(token), "")
    return token


def _is_var(value: str) -> bool:
    return value.startswith("?") or value.startswith("$")


def _var_name(value: str) -> str:
    return value[1:] if _is_var(value) else value


def _valid_value(value: Any) -> bool:
    if value is None:
        return False
    try:
        if pd.isna(value):
            return False
    except TypeError:
        pass
    text = str(value)
    return bool(text and text.lower() not in {"nan", "none"})
