"""Tests for src/detectors/base.py — DetectionResult contract and load_detector factory."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
import numpy as np

from src.detectors.base import DetectionResult, BaseDetector, load_detector


# ── DetectionResult ───────────────────────────────────────────────────────────

def test_detection_result_bbox_area():
    det = DetectionResult(
        raw_label="red_lego", score=0.9,
        bbox_xyxy=(10.0, 20.0, 60.0, 70.0),
        source="grounding_dino", model_id="test",
    )
    assert abs(det.bbox_area_px - 50.0 * 50.0) < 1e-6


def test_detection_result_zero_area():
    det = DetectionResult(
        raw_label="x", score=0.5,
        bbox_xyxy=(10.0, 10.0, 10.0, 10.0),
        source="test", model_id="test",
    )
    assert det.bbox_area_px == 0.0


def test_detection_result_inverted_box_area():
    # Inverted box (x2 < x1) → area = 0
    det = DetectionResult(
        raw_label="x", score=0.5,
        bbox_xyxy=(60.0, 10.0, 10.0, 50.0),
        source="test", model_id="test",
    )
    assert det.bbox_area_px == 0.0


def test_detection_result_default_metadata():
    det = DetectionResult(
        raw_label="blue_lego", score=0.7,
        bbox_xyxy=(0, 0, 100, 100),
        source="yolo", model_id="yolov8n.pt",
    )
    assert det.metadata == {}
    assert det.prompt is None


def test_detection_result_prompt_stored():
    det = DetectionResult(
        raw_label="red lego", score=0.8,
        bbox_xyxy=(0, 0, 50, 50),
        source="grounding_dino", model_id="test",
        prompt="red lego. blue lego.",
    )
    assert det.prompt == "red lego. blue lego."


# ── BaseDetector interface ────────────────────────────────────────────────────

class _StubDetector(BaseDetector):
    @property
    def model_id(self) -> str:
        return "stub"

    @property
    def source(self) -> str:
        return "stub"

    def detect(self, rgb, depth=None, frame_context=None):
        return [DetectionResult(
            raw_label="thing", score=0.9,
            bbox_xyxy=(10, 10, 50, 50),
            source=self.source, model_id=self.model_id,
        )]


def test_stub_detector_returns_list():
    det = _StubDetector()
    rgb = np.zeros((240, 640, 3), dtype=np.uint8)
    results = det.detect(rgb)
    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0].raw_label == "thing"


def test_stub_detector_accepts_none_depth():
    det = _StubDetector()
    rgb = np.zeros((240, 640, 3), dtype=np.uint8)
    results = det.detect(rgb, depth=None)
    assert len(results) == 1


def test_stub_detector_accepts_frame_context():
    det = _StubDetector()
    rgb = np.zeros((240, 640, 3), dtype=np.uint8)
    ctx = {"fx": 448.0, "fy": 432.0, "cx": 320.0, "cy": 120.0}
    results = det.detect(rgb, frame_context=ctx)
    assert len(results) == 1


# ── load_detector factory ─────────────────────────────────────────────────────

def test_load_detector_unknown_raises():
    with pytest.raises(ValueError, match="Unknown"):
        load_detector("nonexistent_backend", {}, {})


def test_load_detector_yolo_requires_model():
    with pytest.raises(ValueError, match="yolo_model"):
        load_detector("yolo", {}, {})


def test_load_detector_depth_blobs_no_import_needed():
    from src.detectors.depth_blobs import DepthBlobDetector
    det = load_detector("depth_blobs", {}, {})
    assert isinstance(det, DepthBlobDetector)
    assert det.source == "depth_blobs"


def test_depth_blob_detector_no_depth_returns_empty():
    from src.detectors.depth_blobs import DepthBlobDetector
    det = DepthBlobDetector()
    rgb = np.zeros((240, 640, 3), dtype=np.uint8)
    assert det.detect(rgb, depth=None) == []


def test_depth_blob_detector_flat_depth_returns_blobs():
    from src.detectors.depth_blobs import DepthBlobDetector
    det = DepthBlobDetector(min_blob_pixels=10)
    rgb = np.zeros((240, 640, 3), dtype=np.uint8)
    # Create a depth image with a single foreground blob at 1.0m
    depth = np.zeros((240, 640), dtype=np.float32)
    depth[50:100, 100:200] = 1.0  # ~5000px blob
    results = det.detect(rgb, depth=depth)
    assert len(results) >= 1
    assert all(r.source == "depth_blobs" for r in results)
    assert all(isinstance(r.score, float) for r in results)
