// XR_Pipeline — Neo4j import commands
// Run these in order against your Neo4j Aura instance

CREATE CONSTRAINT room_id IF NOT EXISTS
FOR (r:Room) REQUIRE r.room_id IS UNIQUE;

CREATE CONSTRAINT object_id IF NOT EXISTS
FOR (o:Object) REQUIRE o.track_id IS UNIQUE;

CREATE CONSTRAINT event_id IF NOT EXISTS
FOR (e:Event) REQUIRE e.event_id IS UNIQUE;

// Import nodes (replace $url with actual hosted CSV URLs or use local path)
LOAD CSV WITH HEADERS FROM $rooms_url AS row
MERGE (r:Room {room_id: row.`room_id:ID(Room)`})
SET r.name = row.name,
    r.x = toFloat(row.`x:float`),
    r.y = toFloat(row.`y:float`),
    r.z = toFloat(row.`z:float`);

LOAD CSV WITH HEADERS FROM $objects_url AS row
MERGE (o:Object {track_id: row.`track_id:ID(Object)`})
SET o.semantic_class = row.semantic_class,
    o.label = row.label,
    o.caption = row.caption;

LOAD CSV WITH HEADERS FROM $events_url AS row
MERGE (e:Event {event_id: row.`event_id:ID(Event)`})
SET e.event_type = row.event_type,
    e.summary = row.summary,
    e.start_ts_ns = toInteger(row.`start_ts_ns:long`),
    e.end_ts_ns = toInteger(row.`end_ts_ns:long`),
    e.pos_x = toFloat(row.`pos_x:float`),
    e.pos_y = toFloat(row.`pos_y:float`),
    e.pos_z = toFloat(row.`pos_z:float`);

// Import edges
LOAD CSV WITH HEADERS FROM $room_object_url AS row
MATCH (r:Room {room_id: row.`:START_ID(Room)`})
MATCH (o:Object {track_id: row.`:END_ID(Object)`})
MERGE (r)-[:CONTAINS]->(o);

LOAD CSV WITH HEADERS FROM $event_object_url AS row
MATCH (e:Event {event_id: row.`:START_ID(Event)`})
MATCH (o:Object {track_id: row.`:END_ID(Object)`})
MERGE (e)-[rel:INVOLVES]->(o)
SET rel.role = row.role,
    rel.role_description = row.role_description;

LOAD CSV WITH HEADERS FROM $before_url AS row
MATCH (e1:Event {event_id: row.`:START_ID(Event)`})
MATCH (e2:Event {event_id: row.`:END_ID(Event)`})
MERGE (e1)-[:BEFORE]->(e2);
