# Design Notes

## Data source
Quest 3 mixed-reality capture: RGBA32 raw bytes + float32 depth (meters) + JSON pose metadata.

## Timestamps
Windows FILETIME ticks → convert to relative nanoseconds (first frame = 0).

## Camera intrinsics
Not embedded in metadata. Using Quest 3 approximate defaults:
  fx=240, fy=240, cx=160, cy=120 for 320x240 resolution.
Override in configs/pipeline.yaml.

## Object detection
Layer A: depth-blob segmentation (no model required).
Layer B: YOLO (optional, set yolo_model in pipeline.yaml).

## EGG graph
Following EGG paper architecture but pragmatic:
no requirement for perfect 3D reconstruction.
