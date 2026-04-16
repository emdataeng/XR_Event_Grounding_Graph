"""Detector backends for the XR pipeline.

Each backend implements BaseDetector and returns a list of DetectionResult
objects in RGB image pixel space. Depth back-projection is NOT the detector's
responsibility — script 05 owns that step.
"""
from .base import DetectionResult, BaseDetector

__all__ = ["DetectionResult", "BaseDetector"]
