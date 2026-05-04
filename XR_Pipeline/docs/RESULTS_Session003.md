# XR-EGG Pipeline — Results (Session 003)

Results from the XR pipeline run on **session_003**: a 61-frame Quest 3 capture
of a hand interacting with two lego pieces on a workstation surface.

---

## 📚 Key Concepts

Plain-English explanations of every term used throughout this document.
Terms marked with ★ appeared in the session_003 results; the rest are part of
the full pipeline vocabulary and may appear in other sessions.

---

### Events (Layer 2 — Memory)

The pipeline watches every frame and fires an **event** whenever something
meaningful happens to an object or a pair of objects. Events are the atoms of
the story — everything higher up is built from them.

There are 13 event types in total, grouped by what kind of thing they describe.

**Lifecycle events** — an object entering or leaving the scene

| Event | ★ | Plain meaning |
|-------|---|---------------|
| **APPEAR** | ★ | An object comes into view for the first time, or re-enters the scene after being absent. |
| **DISAPPEAR** | ★ | An object leaves the scene or goes permanently out of view. |
| **INSPECT** | | The camera or hand pauses over an object — the worker is looking at it closely. |

**Motion events** — an object changing location

| Event | ★ | Plain meaning |
|-------|---|---------------|
| **MOVE** | | An object has shifted position noticeably between frames — something moved it. |
| **PLACE** | | An object was set down and is now in contact with a surface or another part. |

**Proximity events** — two objects changing their spatial relationship

| Event | ★ | Plain meaning |
|-------|---|---------------|
| **CO_LOCATE** | | Two objects have come close to each other — they are now in the same neighbourhood. |
| **SEPARATE** | | Two objects that were close have moved apart. |
| **INTERACTION** | ★ | The hand and an object are touching or very close — the hand is actively doing something to the object. |

**Candidate events** — tentative signals that need further confirmation

These are "maybe" events: the pipeline detected a signal strong enough to flag but not yet strong enough to assert with confidence. A candidate event triggers higher layers to gather more evidence before promoting it to a confirmed subtask.

| Event | Plain meaning |
|-------|---------------|
| **ALIGN_CANDIDATE** | Two parts appear to be lined up with each other — could be the start of an assembly step. |
| **ATTACH_CANDIDATE** | Two parts may have been joined or fastened together. |
| **STATE_CHANGE_CANDIDATE** | Something about the scene changed in a way that could indicate a completed procedure step. |
| **ASSEMBLY_CHANGE_CANDIDATE** | The assembly state may have changed — a part may have been added to a sub-assembly. |
| **USE_TOOL_CANDIDATE** | A tool (screwdriver, pin, etc.) may have been used on a part. |

---

### Operations (Layer 3 — Storyline, level 2)

A run of interaction events involving the same hand–object pair is collapsed
into a single **operation** — a named action with a clear start and end frame.
There are 14 operation types, split into confirmed and candidate.

**Confirmed operations** — the pipeline is certain these happened

| Operation | ★ | Plain meaning |
|-----------|---|---------------|
| **HOLD** | ★ | The hand gripped an object and kept holding it for a sustained period. The most fundamental assembly action. |
| **PICK_UP** | | The hand lifted an object off a surface — the object went from resting to being carried. |
| **PUT_DOWN** | | The hand set an object back down onto a surface. |
| **CONTACT** | | The hand briefly touched an object without lifting it — a tap, press, or push. |
| **TRANSFER** | | An object moved from one location to another under the guidance of the hand. |
| **USE_TOOL** | | A tool was picked up and applied to a workpiece (e.g. driving a screw). |
| **APPROACH** | | The hand or an object moved deliberately toward another object — the beginning of a larger action. |

**Candidate operations** — probable actions that need more evidence

| Operation | Plain meaning |
|-----------|---------------|
| **PICK_UP_CANDIDATE** | Looks like a pick-up but confidence is below the threshold to confirm it. |
| **PUT_DOWN_CANDIDATE** | Looks like a set-down but not yet confirmed. |
| **PLACE_ONTO_CANDIDATE** | One part may have been placed onto another (e.g. stacking). |
| **INSERT_CANDIDATE** | One part may have been inserted into another (e.g. a pin into a hole). |
| **ALIGN_CANDIDATE** | Two parts appear to have been lined up — precursor to attaching. |
| **ATTACH_CANDIDATE** | Two parts may have been fastened together. |

---

### Subtasks (Layer 3 — Storyline, level 3)

Operations are interpreted into **subtasks** — the smallest named steps in an
assembly procedure. Each subtask maps to one or more operations and describes
*what was accomplished*, not just *what motion occurred*.

**Generic subtasks** (available in every session)

| Subtask | ★ | Plain meaning |
|---------|---|---------------|
| **hold_part(X)** | ★ | The hand successfully gripped and held part X. |
| **release_part(X)** | ★ | The hand let go of part X, setting it back down. |
| **pick_up_part(X)** | | Part X was lifted off the surface by the hand. |
| **place_part(X)** | | Part X was set down onto a surface or another part. |
| **contact_parts(X, Y)** | | The hand made brief contact with X (possibly also touching Y). |
| **insert_part(X into Y)** | | Part X was inserted into part Y (e.g. a pin into a socket). |
| **align_part(X with Y)** | | Part X was lined up with part Y in preparation for attachment. |
| **attach_part(X to Y)** | | Part X was fastened or joined to part Y. |
| **use_tool(T on X)** | | Tool T was used on part X (e.g. a screwdriver on a screw). |
| **transfer_part(X)** | | Part X was moved from one location to another. |
| **approach_target(X → Y)** | | Object X moved deliberately toward object Y. |
| **co_held_parts(X, Y)** | ★ | Both X and Y were held or manipulated at the same time. |

Subtask **status** values:

| Status | Meaning |
|--------|---------|
| **achieved** | Enough evidence to be confident the subtask completed successfully. |
| **candidate** | The subtask probably happened but the evidence is not strong enough for full confidence (e.g. only one hand track was confirmed when two would be needed). |

---

### Support States (Layer 3 — Storyline)

Between subtasks the pipeline tracks the **physical support state** of every
part — essentially, what is the part resting on (or being held by)?

| State | ★ | Plain meaning |
|-------|---|---------------|
| **RESTING** | ★ | The part is stationary on the workstation surface — nothing is actively holding it. |
| **CARRIED** | ★ | A hand has picked the part up and is actively moving or holding it in the air. |
| **IN_CONTACT** | | The part is touching another object (not the table) — it may be resting on a sub-assembly or being placed onto something. |

A **state transition** is the moment a part switches between these states:
- RESTING → CARRIED = picked up
- CARRIED → RESTING = set down on the table
- CARRIED → IN_CONTACT = placed onto another part

---

### State Facts (Layer 3 — Storyline)

A **state fact** is a single true statement about the scene at a specific moment
in time — e.g. *"at frame 20, the blue lego is being held."* Facts are produced
in bulk and form the knowledge base that Layer 4 queries.

The full pipeline produces 22 distinct fact types, grouped by what they describe.

**Lifecycle facts** — is an object present?

| Predicate | ★ | Plain meaning |
|-----------|---|---------------|
| `present(X)` | ★ | Object X is visible and tracked in the scene right now. |
| `appeared(X)` | ★ | Object X just entered the scene (fired once per APPEAR event). |
| `disappeared(X)` | ★ | Object X just left the scene. |

**Motion facts** — is an object moving?

| Predicate | Plain meaning |
|-----------|---------------|
| `started_moving(X)` | Object X began moving this frame — something is pushing or carrying it. |
| `stopped_moving(X)` | Object X came to rest this frame. |

**Proximity facts** — how close are two objects?

| Predicate | Plain meaning |
|-----------|---------------|
| `near(X, Y)` | Objects X and Y are spatially close but not necessarily touching. |
| `touching_candidate(X, Y)` | X and Y appear to be in contact — could be the start of an assembly action. |

**Support state facts** — what is the object resting on?

| Predicate | ★ | Plain meaning |
|-----------|---|---------------|
| `resting(X)` | ★ | Object X is sitting on the table surface. |
| `carried(X)` | ★ | Object X is being held in the air by a hand. |
| `surface_contact(X)` | | Object X is touching another part's surface (placed on, not the table). |

**Action/relation facts** — what is the hand doing to an object?

| Predicate | ★ | Plain meaning |
|-----------|---|---------------|
| `holding(hand, X)` | ★ | The hand is actively gripping object X right now. |
| `released(hand, X)` | ★ | The hand just let go of object X. |
| `in_contact(hand, X)` | | The hand is touching X without a full grip (a tap, press, or push). |
| `inserted_into_candidate(X, Y)` | | X appears to have been inserted into Y. |
| `placed_on_candidate(X, Y)` | | X appears to have been placed on top of Y. |
| `aligned_with_candidate(X, Y)` | | X appears to be aligned with Y — ready for attachment. |
| `attached_to_candidate(X, Y)` | | X appears to have been fastened to Y. |
| `used_tool_on(T, X)` | | Tool T was used on object X. |

**Co-manipulation facts** — are two objects being manipulated together?

| Predicate | ★ | Plain meaning |
|-----------|---|---------------|
| `co_held(X, Y)` | ★ | Both X and Y are being held or manipulated simultaneously. |
| `co_held_started(X, Y)` | | The co-held state for X and Y just began this frame. |
| `co_held_ended(X, Y)` | | The co-held state for X and Y just ended this frame. |

---

### Workflow Phases (Layer 3 — Storyline)

Operations that happen close together in time are grouped into a **phase** — a
higher-level chunk of the procedure that gives a bird's-eye view of what the
worker was doing over a stretch of time. The pipeline defines 8 phase labels:

| Phase | ★ | What it represents |
|-------|---|--------------------|
| **hold** | ★ | The worker was gripping and holding one or more parts — a steady-state grip. |
| **manipulation** | | General picking-up and putting-down without a specific assembly outcome. |
| **placement** | | Parts were being positioned onto, into, or alongside each other for assembly. |
| **tool_use** | | A tool was being actively used (screwdriver, pin, etc.). |
| **approach** | | The hand or part was moving toward a target — a transitional, preparatory movement. |
| **transfer** | | A part was being moved from one place to another. |
| **contact** | | Brief, intentional contact with a part — a touch or light press. |
| **idle** | | No operation was active — the worker may have paused or been repositioning. |

---

### Object Roles

Every tracked object is assigned a **role** that tells the pipeline how to
reason about it. Roles determine which operations and subtasks make sense for
that object.

| Role | Plain meaning |
|------|---------------|
| **hand** | The worker's hand — the agent that performs all operations. |
| **workpiece** | A part being assembled — the primary target of operations. |
| **tool** | An instrument used to manipulate workpieces (screwdriver, pin tool, etc.). |
| **fixture** | A jig or stand that holds parts in place during assembly. |
| **container** | A tray, bin, or holder that stores parts before use. |
| **machine_part** | A component that is part of a larger machine, not a hand-assembled piece. |
| **context** | Background objects that are tracked for spatial reference but not directly assembled. |

---

### Confidence Scores

Every detection, event, operation, and subtask carries a **confidence** value
between 0 and 1. Think of it as the pipeline's certainty:

| Range | Interpretation |
|-------|---------------|
| 0.90 – 1.00 | Very confident — treat as fact |
| 0.75 – 0.89 | Confident — likely correct |
| 0.50 – 0.74 | Moderate — probably correct but worth reviewing |
| < 0.50 | Low — treat as a weak signal only |

---

## Layer 1 — Eyes

**Detector:** Grounding DINO (`IDEA-Research/grounding-dino-base`)
**Prompt:** `"red block. blue block."`
**Input:** 61 RGB-D frames with 6-DOF pose

### Detections

| Class | Observations | Mean confidence | Min | Max |
|-------|-------------|-----------------|-----|-----|
| hand | 57 | 0.647 | 0.301 | 0.954 |
| red_lego | 56 | 0.499 | 0.304 | 0.880 |
| blue_lego | 39 | 0.531 | 0.300 | 0.868 |
| **Total** | **152** | **0.563** | | |

Hand detections have the highest mean confidence, consistent with the model's
strong prior on hand appearance. The lego pieces score lower — both are small
objects whose labels (`"red block"`, `"blue block"`) are more ambiguous than
everyday object names.

### 3D positions (depth-projected world coordinates, metres)

| Track | Class | Mean X | Mean Y | Mean Z |
|-------|-------|--------|--------|--------|
| trk_0001 | blue_lego | 0.043 | 0.939 | 0.889 |
| trk_0003 | hand | 0.180 | 1.103 | 1.020 |
| trk_0004 | red_lego | −0.116 | 0.776 | 0.928 |

The two lego pieces sit ~9 cm apart in the horizontal plane, at roughly the
same depth (~0.91 m from the camera). The hand is consistently higher and
further from the camera, as expected when reaching over the workpiece.

---

## Layer 2 — Memory

### Object tracks

| Track | Class | Observations | Frame span |
|-------|-------|-------------|------------|
| trk_0001 | blue_lego | 38 | 3 → 61 |
| trk_0003 | hand | 40 | 6 → 61 |
| trk_0004 | red_lego | 32 | 7 → 58 |

All three objects were tracked for nearly the full session (58–59 frames out of 61).

### EGG graph

| Element | Count |
|---------|-------|
| Rooms | 1 (`workstation_A`) |
| Object nodes | 3 |
| Event nodes | 11 |

### Event breakdown

| Event type | Count | Objects involved |
|------------|-------|-----------------|
| APPEAR | 3 | blue_lego, hand, red_lego (one each) |
| INTERACTION | 5 | hand ↔ blue_lego (×3), hand ↔ red_lego (×2) |
| DISAPPEAR | 3 | blue_lego, hand, red_lego (one each) |

Event confidence: APPEAR = 0.90 · INTERACTION = 0.80 · DISAPPEAR = 0.70

The 5 INTERACTION events — hand making contact with a lego piece — are the
key inputs that drive all higher-level reasoning in layers 3 and 4.

---

## Layer 3 — Storyline

### Operation events (level 2)

3 HOLD operations inferred from the INTERACTION events above:

| Operation | Agent → Object | Frame span | Duration | Confidence |
|-----------|---------------|------------|----------|-----------|
| op_0001 | hand → blue_lego | 13 → 40 | 28 frames | 0.80 |
| op_0002 | hand → red_lego | 13 → 35 | 23 frames | 0.80 |
| op_0003 | hand → red_lego | 49 → 58 | 10 frames | 0.80 |

### Subtask events (level 3)

6 subtasks resolved from the operations above:

| Subtask | Template | Status | Confidence | Frame span |
|---------|----------|--------|-----------|------------|
| sub_0001 | hold_part(blue_lego) | **achieved** | 0.80 | 13 → 40 |
| sub_0002 | hold_part(red_lego) | **achieved** | 0.80 | 13 → 35 |
| sub_0003 | hold_part(red_lego) | **achieved** | 0.80 | 49 → 58 |
| sub_0004 | release_part(blue_lego) | **achieved** | 0.75 | 40 → 41 |
| sub_0005 | release_part(red_lego) | **achieved** | 0.75 | 35 → 36 |
| sub_0006 | co_held_parts(blue_lego, red_lego) | candidate | 0.576 | 13 → 35 |

5 out of 6 subtasks resolved with full confidence. The `co_held_parts` subtask
is marked **candidate** (conf 0.576) because the evidence for simultaneous
two-hand holding is partial — the hand track covers both objects in the same
frame window but a dedicated second-hand track was not confirmed.

### Support state transitions

8 transitions tracked across the two workpieces:

| Object | State | Frame span | Trigger |
|--------|-------|------------|---------|
| blue_lego | RESTING | 3 → 12 | — |
| blue_lego | **CARRIED** | 13 → 40 | op_0001 |
| blue_lego | RESTING | 41 → 61 | release at frame 41 |
| red_lego | RESTING | 7 → 12 | — |
| red_lego | **CARRIED** | 13 → 35 | op_0002 |
| red_lego | RESTING | 36 → 48 | release at frame 36 |
| red_lego | **CARRIED** | 49 → 58 | op_0003 |
| red_lego | RESTING | 59 → 61 | — |

### State facts

**35 state facts** produced, spanning four predicate types:

| Predicate | Count | Confidence range |
|-----------|-------|-----------------|
| `present` | 3 | 0.795 – 0.828 |
| `appeared` / `disappeared` | 6 | 0.900 |
| `co_located`, `held`, `co_held` | 26 | 0.800 – 0.900 |

### Workflow phases

2 phases identified from the operation sequence:

| Phase | Label | Frame span | Operations | Objects |
|-------|-------|------------|------------|---------|
| phase_0001 | hold | 13 → 40 | HOLD ×2 | blue_lego + red_lego |
| phase_0002 | hold | 49 → 58 | HOLD ×1 | red_lego |

---

## Layer 4 — Brain

The EGG graph for session_003 was exported to Neo4j Aura.
At query time the full graph contains **3 objects, 11 events** — small enough
that pruning is minimal for this session.

The brain layer has been exercised with demo queries but not yet benchmarked
against a ground-truth Q&A set for this session. Quantitative evaluation
is planned as part of the next steps.

---

## Summary

| Layer | What ran | Result |
|-------|----------|--------|
| Eyes | Grounding DINO on 61 frames | 152 detections across 3 classes, mean conf 0.563 |
| Memory | Track linking + EGG graph | 3 persistent tracks, 11 events, exported to Neo4j |
| Storyline | Operation → subtask → state reasoning | 6/6 subtasks resolved (5 achieved, 1 candidate) |
| Storyline | State transitions | 8 RESTING ↔ CARRIED transitions, 35 state facts |
| Brain | Graph export + demo queries | Graph live in Neo4j; Q&A benchmark pending |
