# Frame Manifest Schema

Canonical CSV with one row per captured frame.

| Column | Type | Description |
|---|---|---|
| frame_idx | int | Frame index |
| timestamp_ns | int | Timestamp in nanoseconds (relative to first frame) |
| rgb_path | str | Relative path to RGBA file |
| depth_path | str | Relative path to depth .npy file (or empty) |
| depth_encoding | str | npy / f32 / none |
| depth_scale | float | Scale factor (1.0 = already meters) |
| fx, fy, cx, cy | float | Camera intrinsics |
| width, height | int | Image dimensions |
| T_world_cam_00..15 | float | Flattened 4x4 pose matrix row-major |
| room_id | str | Room/workstation label |
| source_stream | str | e.g. quest3_capture |
| notes | str | Optional warnings |
