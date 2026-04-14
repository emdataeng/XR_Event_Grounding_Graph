"""egg_builder.py — Standalone EGG-style graph for IndustReal PSR output.

Converts PSR step predictions into a lightweight temporal graph of
StateEvents and an AssemblyGraph.  Intentionally separate from the
XR_Pipeline schema so the IndustReal PoC is self-contained.

Event types mirror the EGG taxonomy:
  INSTALL   — component was correctly placed (PSR install=True, conf=1)
  REMOVE    — component was taken off      (PSR install=False)
  ERROR     — component incorrectly placed  (action_id % 3 == 1)
  CORRECT   — error corrected               (transition from error→correct)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

FPS = 10  # IndustReal HoloLens 2 capture rate


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class StateEvent:
    """A single detected assembly step mapped to an EGG-style event."""
    event_id:    int
    frame:       int
    time_s:      float
    event_type:  str          # INSTALL | REMOVE | ERROR | CORRECT
    component:   str          # human-readable component name
    action_desc: str          # full action description from proc_info
    conf:        float = 1.0

    def __repr__(self) -> str:
        return (f"[{self.event_type:8s}] t={self.time_s:6.2f}s  "
                f"{self.component} — {self.action_desc}")


@dataclass
class AssemblyGraph:
    """Temporal graph of assembly events for one recording."""
    clip:       str
    n_frames:   int
    events:     list[StateEvent] = field(default_factory=list)

    # Final inferred component states after all events are applied.
    # None = never observed, False = removed, True = installed.
    component_states: dict[str, Optional[bool]] = field(default_factory=dict)

    def summary(self) -> str:
        lines = [
            f"AssemblyGraph: {self.clip}",
            f"  frames : {self.n_frames}  ({self.n_frames / FPS:.1f} s)",
            f"  events : {len(self.events)}",
        ]
        for ev in self.events:
            lines.append(f"  {ev}")
        lines.append("  Component states at end:")
        for comp, state in self.component_states.items():
            mark = "✓" if state else ("✗" if state is False else "?")
            lines.append(f"    {mark} {comp}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Component name index (state_idx → readable name)
# ---------------------------------------------------------------------------

_COMPONENT_NAMES = {
    0:  "base",
    1:  "front chassis",
    2:  "front chassis pin",
    3:  "rear chassis",
    4:  "short rear chassis",
    5:  "front rear chassis pin",
    6:  "rear rear chassis pin",
    7:  "front bracket",
    8:  "front bracket screw",
    9:  "front wheel assy",
    10: "rear wheel assy",
}


def _action_type(proc_step: dict) -> str:
    """Classify a proc_info step as INSTALL / REMOVE / ERROR / CORRECT."""
    action_id = proc_step["id"]
    remainder = action_id % 3
    if remainder == 0:
        # id % 3 == 0: "Install ..." or "Corrected from error ..."
        return "INSTALL"
    elif remainder == 1:
        return "ERROR"
    else:
        return "REMOVE"


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

def build_assembly_graph(
    clip: str,
    n_frames: int,
    psr_steps: list[dict],
    proc_info: list,
) -> AssemblyGraph:
    """Convert PSR step predictions into an AssemblyGraph.

    psr_steps: output of run_psr() — list of dicts with keys
               frame, id, description, conf.
    proc_info: loaded procedure_info.json list.
    """
    proc_by_id = {s["id"]: s for s in proc_info}
    graph = AssemblyGraph(clip=clip, n_frames=n_frames)

    # Track component states for final summary.
    comp_states: dict[str, Optional[bool]] = {
        name: None for name in _COMPONENT_NAMES.values()
    }

    for i, step in enumerate(psr_steps):
        pid = step["id"]
        proc_step = proc_by_id.get(pid)
        if proc_step is None:
            continue

        comp_name  = _COMPONENT_NAMES.get(proc_step["state_idx"], f"component_{proc_step['state_idx']}")
        etype      = _action_type(proc_step)
        frame      = step["frame"]
        time_s     = frame / FPS

        event = StateEvent(
            event_id    = i,
            frame       = frame,
            time_s      = time_s,
            event_type  = etype,
            component   = comp_name,
            action_desc = step["description"],
            conf        = step.get("conf", 1.0),
        )
        graph.events.append(event)

        # Update running component state.
        if etype == "INSTALL":
            comp_states[comp_name] = True
        elif etype == "REMOVE":
            comp_states[comp_name] = False
        # ERROR leaves state as-is (not yet correctly installed).

    graph.component_states = comp_states
    return graph


def diff_graphs(gt_graph: AssemblyGraph, pred_graph: AssemblyGraph) -> str:
    """Return a human-readable diff between GT and predicted graphs."""
    gt_types  = [e.event_type for e in gt_graph.events]
    pred_types = [e.event_type for e in pred_graph.events]

    lines = [
        f"Graph diff: {gt_graph.clip}",
        f"  GT events   : {len(gt_graph.events)}",
        f"  Pred events : {len(pred_graph.events)}",
        "",
        "  GT steps:",
    ]
    for ev in gt_graph.events:
        lines.append(f"    {ev}")
    lines.append("")
    lines.append("  Predicted steps:")
    if pred_graph.events:
        for ev in pred_graph.events:
            lines.append(f"    {ev}")
    else:
        lines.append("    (none — model produced no predictions)")
    return "\n".join(lines)
