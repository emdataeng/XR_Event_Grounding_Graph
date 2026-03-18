# Object Observations Schema

One row per detected/observed object per frame.

| Column | Description |
|---|---|
| observation_id | Unique ID |
| frame_idx | Frame index |
| timestamp_ns | Timestamp ns |
| semantic_class | Object class |
| x,y,z | World-frame centroid (m) |
| w,h,d | Bounding box extents (m) |
| confidence | Detection confidence 0-1 |
| source | depth_blobs / detection / manual |
