# EGG Graph Schema

egg_graph.json contains:
- graph_metadata
- rooms[]
- objects[] with time_variant_history
- events[]
- event_edges[] (event → object roles)
- room_edges[] (room → object)
- temporal_edges[] (event BEFORE event)
