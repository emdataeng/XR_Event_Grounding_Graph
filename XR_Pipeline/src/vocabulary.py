"""vocabulary.py — Canonical label mapping and prompt generation.

The vocabulary layer sits between the detector's raw text output and the
observation schema. It answers two questions:
  1. "What canonical class does this raw detector label map to?"
  2. "What dot-separated prompt text should I give to Grounding DINO?"

Config format (pipeline.yaml → object_vocabulary):

    object_vocabulary:
      red_lego:
        prompts: ["red lego", "red brick", "red block"]
        aliases: ["red lego blue", "red lego blue lego"]
        object_role: workpiece          # industrial role (see VALID_ROLES)
        ignore_for_object_tracks: false # optional, default false
      blue_lego:
        prompts: ["blue lego", "blue brick", "blue block"]
        object_role: workpiece
      hand:
        prompts: ["hand", "human hand", "fingers"]
        object_role: hand
        ignore_for_object_tracks: false
      sleeve:
        prompts: ["sleeve", "arm", "forearm"]
        object_role: context
        ignore_for_object_tracks: true

Industrial roles (object_role):
  hand         — the human agent performing actions
  tool         — instrument used to act on a workpiece (screwdriver, wrench …)
  workpiece    — the object being manipulated / assembled (default)
  fixture      — stationary reference / mount (vice, jig, table surface …)
  container    — bin, tray, or storage holding other objects
  machine_part — a component of a machine that moves or is assembled
  context      — background / environmental object, not part of the workflow

Matching is case-insensitive and strips leading/trailing whitespace.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

# Controlled vocabulary for object roles in industrial workflows.
VALID_ROLES = frozenset({
    "hand", "tool", "workpiece", "fixture",
    "container", "machine_part", "context",
})

# Default role used when object_role is absent from the config entry.
DEFAULT_ROLE = "workpiece"


@dataclass
class VocabEntry:
    canonical: str
    prompts: List[str]
    aliases: List[str] = field(default_factory=list)
    object_role: str = DEFAULT_ROLE
    ignore_for_object_tracks: bool = False


class Vocabulary:
    """Maps raw detector labels to canonical class names.

    If object_vocabulary is not set in the config, the vocabulary is
    *permissive*: every raw label passes through unchanged as its own
    canonical class. This preserves backward-compatible behaviour.
    """

    def __init__(self, entries: List[VocabEntry]):
        self._entries = entries
        # Build lookup: normalised string → (canonical, entry)
        self._lookup: Dict[str, VocabEntry] = {}
        for entry in entries:
            for phrase in entry.prompts + entry.aliases + [entry.canonical]:
                key = _normalise(phrase)
                if key and key not in self._lookup:
                    self._lookup[key] = entry

    # ── Factory ───────────────────────────────────────────────────────────────

    @classmethod
    def from_config(cls, cfg: Dict) -> "Vocabulary":
        """Build a Vocabulary from a loaded pipeline config dict.

        If 'object_vocabulary' is absent, returns an empty (permissive) Vocabulary.
        """
        raw = cfg.get("object_vocabulary") or {}
        entries: List[VocabEntry] = []
        for canonical, spec in raw.items():
            if not isinstance(spec, dict):
                continue
            raw_role = str(spec.get("object_role") or DEFAULT_ROLE).lower()
            role = raw_role if raw_role in VALID_ROLES else DEFAULT_ROLE
            entries.append(VocabEntry(
                canonical=canonical,
                prompts=spec.get("prompts") or [],
                aliases=spec.get("aliases") or [],
                object_role=role,
                ignore_for_object_tracks=bool(spec.get("ignore_for_object_tracks", False)),
            ))
        return cls(entries)

    # ── Public API ────────────────────────────────────────────────────────────

    @property
    def is_empty(self) -> bool:
        """True when no vocabulary entries are configured (permissive mode)."""
        return len(self._entries) == 0

    def canonicalize(self, raw_label: str) -> Optional[str]:
        """Map a raw detector label to its canonical class name.

        Returns:
            canonical class string  — if a match is found
            raw_label unchanged     — if vocabulary is empty (permissive)
            None                    — if vocabulary is non-empty and no match

        In permissive mode (empty vocabulary), every raw label is accepted
        as its own canonical class. This keeps pre-vocabulary runs working.
        """
        if self.is_empty:
            return raw_label

        key = _normalise(raw_label)
        entry = self._lookup.get(key)
        if entry is not None:
            return entry.canonical

        # Partial/substring match: check if any known phrase is contained
        # within the raw label. This catches composite outputs like
        # "red lego blue lego" → could match "red lego" and "blue lego".
        # We return None here — composite labels are a known detector artefact
        # and should be rejected so postprocess NMS can apply prompt hygiene.
        return None

    def object_role(self, canonical_class: str) -> str:
        """Return the industrial role for a canonical class.

        Returns DEFAULT_ROLE ("workpiece") for unknown classes so callers
        can always rely on a valid role string.
        """
        for entry in self._entries:
            if entry.canonical == canonical_class:
                return entry.object_role
        return DEFAULT_ROLE

    def classes_with_role(self, role: str) -> List[str]:
        """Return all canonical class names that carry the given role."""
        return [e.canonical for e in self._entries if e.object_role == role]

    def should_ignore_for_tracks(self, canonical_class: str) -> bool:
        for entry in self._entries:
            if entry.canonical == canonical_class:
                return entry.ignore_for_object_tracks
        return False

    def build_prompt(self, separator: str = ". ") -> str:
        """Build a Grounding DINO prompt string from all vocabulary entries.

        Uses the first prompt phrase for each entry. Returns empty string if
        vocabulary is empty (caller should fall back to detection_prompt).

        Example output: "a red lego brick. a blue lego brick."
        """
        if self.is_empty:
            return ""
        phrases = []
        for entry in self._entries:
            if entry.prompts:
                phrases.append(entry.prompts[0])
        return separator.join(phrases) + ("." if phrases else "")

    def all_prompts_flat(self) -> List[str]:
        """Return all prompt phrases across all entries (for MM-GDINO list format)."""
        out = []
        for entry in self._entries:
            out.extend(entry.prompts)
        return out

    def canonical_classes(self) -> List[str]:
        return [e.canonical for e in self._entries]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _normalise(s: str) -> str:
    return s.strip().lower().rstrip(".")
