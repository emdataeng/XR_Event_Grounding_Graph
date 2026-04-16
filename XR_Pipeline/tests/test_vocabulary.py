"""Tests for src/vocabulary.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from src.vocabulary import Vocabulary, VocabEntry, _normalise


# ── Fixtures ──────────────────────────────────────────────────────────────────

def _make_vocab():
    return Vocabulary.from_config({
        "object_vocabulary": {
            "red_lego": {
                "prompts": ["a red lego brick", "red lego"],
                "aliases": ["red lego blue lego", "red lego blue"],
            },
            "blue_lego": {
                "prompts": ["a blue lego brick", "blue lego"],
            },
            "hand": {
                "prompts": ["hand", "human hand"],
                "ignore_for_object_tracks": True,
            },
        }
    })


# ── Normalisation ─────────────────────────────────────────────────────────────

def test_normalise_strips_whitespace():
    assert _normalise("  red lego  ") == "red lego"


def test_normalise_lowercases():
    assert _normalise("Red Lego") == "red lego"


def test_normalise_strips_trailing_period():
    assert _normalise("red lego.") == "red lego"


# ── Permissive mode (empty vocabulary) ───────────────────────────────────────

def test_empty_vocab_is_permissive():
    v = Vocabulary.from_config({})
    assert v.is_empty
    assert v.canonicalize("anything") == "anything"
    assert v.canonicalize("red lego blue lego") == "red lego blue lego"


def test_empty_vocab_build_prompt_is_empty():
    v = Vocabulary.from_config({})
    assert v.build_prompt() == ""


# ── Canonicalization ──────────────────────────────────────────────────────────

def test_canonicalize_exact_prompt_match():
    v = _make_vocab()
    assert v.canonicalize("red lego") == "red_lego"


def test_canonicalize_alias_match():
    v = _make_vocab()
    # Composite label common with Grounding DINO
    assert v.canonicalize("red lego blue lego") == "red_lego"


def test_canonicalize_canonical_name_itself():
    v = _make_vocab()
    assert v.canonicalize("red_lego") == "red_lego"


def test_canonicalize_unknown_returns_none():
    v = _make_vocab()
    assert v.canonicalize("table") is None


def test_canonicalize_case_insensitive():
    v = _make_vocab()
    assert v.canonicalize("RED LEGO") == "red_lego"


def test_canonicalize_trailing_period_stripped():
    v = _make_vocab()
    assert v.canonicalize("blue lego.") == "blue_lego"


# ── Ignore for tracks ─────────────────────────────────────────────────────────

def test_ignore_for_object_tracks_true():
    v = _make_vocab()
    assert v.should_ignore_for_tracks("hand") is True


def test_ignore_for_object_tracks_false():
    v = _make_vocab()
    assert v.should_ignore_for_tracks("red_lego") is False


def test_ignore_for_object_tracks_unknown_class():
    v = _make_vocab()
    assert v.should_ignore_for_tracks("nonexistent") is False


# ── Prompt building ───────────────────────────────────────────────────────────

def test_build_prompt_includes_all_entries():
    v = _make_vocab()
    prompt = v.build_prompt()
    assert "a red lego brick" in prompt
    assert "a blue lego brick" in prompt
    assert "hand" in prompt


def test_build_prompt_ends_with_period():
    v = _make_vocab()
    assert v.build_prompt().endswith(".")


def test_all_prompts_flat():
    v = _make_vocab()
    flat = v.all_prompts_flat()
    assert "red lego" in flat
    assert "blue lego" in flat
    assert isinstance(flat, list)


def test_canonical_classes_list():
    v = _make_vocab()
    classes = v.canonical_classes()
    assert "red_lego" in classes
    assert "blue_lego" in classes


# ── Config with missing optional fields ──────────────────────────────────────

def test_vocab_no_aliases_key():
    v = Vocabulary.from_config({
        "object_vocabulary": {
            "widget": {"prompts": ["widget", "small widget"]}
        }
    })
    assert v.canonicalize("widget") == "widget"
    assert v.canonicalize("unknown") is None


def test_vocab_non_dict_spec_ignored():
    # Malformed entries should not crash
    v = Vocabulary.from_config({
        "object_vocabulary": {
            "good_entry": {"prompts": ["good"]},
            "bad_entry": "this is a string not a dict",
        }
    })
    assert v.canonicalize("good") == "good_entry"
