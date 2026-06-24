# Query-Aware Subgraph Retrieval: Technical Implementation Plan

## 1. Objective

Extend `experiments/query_driven_graph` with a second retrieval strategy that:

- Uses the operator question and current step as inputs
- Does not use evaluation-only `risk_type` metadata
- Retrieves a bounded candidate neighborhood from Neo4j
- Scores candidate paths with transparent heuristics
- Selects a compact connected subgraph
- Sends only selected evidence to the LLM
- Preserves full diagnostics for evaluation

The existing template-based retriever should remain unchanged as a baseline.

## 2. Proposed Experiment Modes

Add a configurable retrieval strategy:

```yaml
retrieval:
  strategy: template_pattern
```

or:

```yaml
retrieval:
  strategy: heuristic_path_expansion
```

Suggested meanings:

- `template_pattern`: current implementation
- `heuristic_path_expansion`: proposed implementation

Do not silently replace the existing strategy. Separate modes are necessary for
controlled comparison.

## 3. Remove Evaluation Metadata from Retrieval

The current planner uses `risk_type` through `intent_by_risk_type`. The new
retriever must ignore it.

Inputs allowed for retrieval:

```yaml
question: operator question
step_id: canonical current-step identifier
graph_name: selected graph
```

Inputs retained only for later evaluation:

```yaml
risk_type: expected risk category
expected_answer_elements: answer-scoring metadata
```

This prevents the expected evaluation category from leaking into retrieval.

## 4. Add Retrieval Configuration

Create:

```text
experiments/query_driven_graph/configs/retrieval_scoring.yaml
```

Prompt text does not belong in this file. It should contain retrieval concepts,
relation weights, scoring weights, and selection budgets. It must not duplicate
the graph traversal budgets. All graph-using experiments must load those from:

```text
experiments/shared/configs/graph_retrieval.yaml
```

Each experiment config references that shared file:

```yaml
graph_retrieval_config: "experiments/shared/configs/graph_retrieval.yaml"
```

Example:

```yaml
concept_keywords:
  sequence:
    - next
    - previous
    - continue
    - before
    - move on

  installation:
    - install
    - installed
    - attached
    - seated
    - fit

  alignment:
    - align
    - aligned
    - orientation
    - oriented
    - correctly

  removal:
    - remove
    - removed
    - detach
    - take off
    - rework

  tool:
    - tool
    - screwdriver
    - force

  evidence:
    - confidence
    - certain
    - evidence
    - video
    - observed

relation_relevance:
  sequence:
    NEXT: 1.0
    DEPENDS_ON: 0.8
    REQUIRES: 0.6

  installation:
    REQUIRES: 1.0
    PRODUCES: 1.0
    SUPPORTED_BY: 0.9
    HAS_CONSTRAINT: 0.8
    DEPENDS_ON: 0.7

  alignment:
    REQUIRES: 1.0
    HAS_CONSTRAINT: 0.9
    HAS_PREDICATE: 0.8
    SUPPORTED_BY: 0.8

  removal:
    INVALIDATED_BY: 1.0
    PRODUCES: 0.9
    REQUIRES: 0.8
    DEPENDS_ON: 0.7

  tool:
    HAS_ENTITY: 1.0
    HAS_PREDICATE: 0.9
    HAS_CONSTRAINT: 0.8

  evidence:
    DERIVED_FROM: 1.0
    SUPPORTED_BY: 1.0
    HAS_PREDICATE: 0.8
    HAS_CONSTRAINT: 0.7

distance_scores:
  sequence:
    0: 1.0
    1: 0.9
  semantic:
    0: 1.0
    1: 1.0
    2: 0.7

support_status_scores:
  observed: 1.0
  supported: 0.9
  provisional: 0.6
  missing: 0.5
  unknown: 0.4

step_status_scores:
  accepted: 1.0
  uncertain: 0.6
  rejected: 0.4

safety_boosts:
  missing_requirement: 0.3
  incompatibility: 0.4
  rejected_support: 0.4
  invalidated_effect: 0.3
  safety_requirement: 0.3

score_weights:
  relation: 0.35
  text: 0.30
  distance: 0.15
  evidence_quality: 0.10
  safety: 0.10

budgets:
  max_candidate_paths: 100
  max_selected_paths: 8
  max_selected_nodes: 20
  max_selected_edges: 25
  minimum_score: 0.35
```

Validate that the final scoring weights sum to `1.0`.

The shared traversal file contains:

```yaml
context_retrieval:
  # Sequence radius for NEXT traversal between Step nodes.
  step_hops: 1
  # Semantic evidence depth starting from the original current Step only.
  evidence_hops: 2
```

Node-type expansion rules remain part of retrieval behavior, while the two
numeric traversal budgets have one shared source of truth.

## 5. Question Analysis

Create:

```text
experiments/query_driven_graph/src/question_analyzer.py
```

Responsibilities:

1. Lowercase and normalize the question.
2. Normalize punctuation and common word variants.
3. Match configured words and phrases.
4. Produce detected concepts and weighted terms.

Suggested output:

```python
@dataclass(frozen=True)
class QuestionAnalysis:
    normalized_question: str
    tokens: tuple[str, ...]
    concepts: tuple[str, ...]
    matched_terms: dict[str, tuple[str, ...]]
```

Example:

```yaml
normalized_question: can i continue if this pin is not aligned correctly
tokens:
  - continue
  - pin
  - aligned
  - correctly
concepts:
  - sequence
  - alignment
matched_terms:
  sequence:
    - continue
  alignment:
    - aligned
    - correctly
```

If no concept matches, use a neutral `general_context` concept rather than
consulting `risk_type`.

## 6. Candidate Neighborhood Retrieval

Create:

```text
experiments/query_driven_graph/src/candidate_retriever.py
```

The candidate query should:

- Anchor at the canonical current `Step`
- Restrict every node to the configured `graph_name`
- Traverse sequence and semantic neighborhoods separately
- Use `sequence_hops` only for `NEXT` traversal between `Step` nodes
- Use `semantic_hops` only for the configured semantic relation allowlist
- Start semantic expansion from the original current step
- Expand semantic traversal further only through configured expandable node
  types, initially `Constraint` and `Predicate`
- Treat neighboring steps, entities, rules, and sources as terminal semantic
  results
- Return paths with nodes and relationships
- Enforce a candidate limit

Avoid unrestricted variable-length queries over every relationship.

A conceptual sequence query is:

```cypher
MATCH (start:Step {graph_name: $graph_name, step_id: $step_id})
MATCH path = (start)-[:NEXT*1..1]-(neighbor:Step {graph_name: $graph_name})
RETURN path
LIMIT $candidate_limit
```

A conceptual semantic query starts independently from `start`:

```cypher
MATCH (start:Step {graph_name: $graph_name, step_id: $step_id})
MATCH path = (start)-[:REQUIRES|PRODUCES|SUPPORTED_BY|DEPENDS_ON|
                      HAS_CONSTRAINT|HAS_PREDICATE|HAS_ENTITY|
                      DERIVED_FROM|INVALIDATED_BY*1..2]-(target)
RETURN path
LIMIT $candidate_limit
```

The final implementation must additionally enforce the expandable and terminal
node-type rules. Relationship types cannot safely be passed as ordinary Cypher
parameters, so construct the allowlist from validated configuration, never from
question text.

The safer first implementation is to use separate fixed queries:

- A sequence-neighborhood query
- A one-hop semantic-evidence query
- A second-hop query that expands only selected `Constraint` and `Predicate`
  nodes

All should return plain path records that can later be combined and deduplicated.

This preserves the behavior already established by `llm_guidance_ablation`:
sequence context and semantic evidence have different meanings and independent
depth controls.

## 7. Candidate Path Representation

Create a stable internal schema:

```python
@dataclass(frozen=True)
class CandidatePath:
    path_id: str
    node_ids: tuple[str, ...]
    node_types: tuple[str, ...]
    relations: tuple[str, ...]
    traversal_kind: str
    sequence_distance: int | None
    semantic_distance: int | None
    source_step_id: str
    target_id: str
    text: str
    confidence: float | None
    support_status: str | None
    step_status: str | None
    flags: tuple[str, ...]
```

`text` should combine only fields useful for lexical comparison:

- Display label
- Action description
- Name
- Kind
- Arguments
- Object labels
- Required condition
- Supporting effect

Do not include full internal IDs in lexical scoring.

## 8. Relation Relevance Score

For each detected concept, read the configured weight for each relationship in
the path.

For one relation:

```text
relation_score = maximum configured weight across detected concepts
```

For a multi-relation path, use either:

```text
average relation weight
```

or:

```text
minimum relation weight
```

Average is less punitive and is a sensible initial choice.

Example:

```text
concepts: installation, alignment
path: DEPENDS_ON -> PRODUCES

DEPENDS_ON = max(0.7, 0.0) = 0.7
PRODUCES   = max(1.0, 0.0) = 1.0

relation_score = (0.7 + 1.0) / 2 = 0.85
```

## 9. Lexical Text Relevance

Create:

```text
experiments/query_driven_graph/src/path_ranker.py
```

Initial scoring should remain dependency-free and inspectable.

Recommended first calculation:

1. Normalize question and candidate tokens.
2. Remove a small configured stop-word list.
3. Treat underscore-separated graph terms as words.
4. Apply optional domain-term weights.
5. Calculate weighted overlap.

Example:

```text
question terms:
front, chassis, pin, aligned

candidate terms:
requires, aligned, front, chassis, pin, front, chassis
```

Possible formula:

```text
text_score =
    sum(weights of matched question terms)
    / sum(weights of all relevant question terms)
```

Normalize the result to `[0, 1]`.

Useful normalization:

```text
front_chassis_pin -> front chassis pin
wheel_assy        -> wheel assembly
installed         -> install
aligned           -> align
removed           -> remove
```

These aliases should be configured rather than scattered through Python.

## 10. Typed Distance Score

Do not score every edge with one generic `hop_count`. Record whether a candidate
came from sequence traversal or semantic traversal.

```text
Sequence distance:
current step:       1.0
previous/next step: 0.9

Semantic distance:
current/direct evidence: 1.0
semantic hop 1:          1.0
semantic hop 2:          0.7
```

The initial limits should remain:

```yaml
sequence_hops: 1
semantic_hops: 2
```

Increasing either radius should require a separate experiment because sequence
distance and evidence depth introduce different kinds of prompt noise.

## 11. Evidence-Quality Score

Read available properties such as:

- `confidence`
- `support_status`
- `status`
- `provisional`

Suggested combination:

```text
quality_score =
    mean(
        numeric confidence when present,
        configured support-status score when present,
        configured step-status score when present
    )
```

If none are present, use a neutral configured default.

Do not remove `missing`, `uncertain`, or `rejected` evidence. Their relevance
and safety significance are independent from evidential quality.

## 12. Safety-Relevance Score

Detect safety and failure flags from relationship types and properties:

```text
missing_requirement
incompatibility
rejected_support
invalidated_effect
safety_requirement
uncertain_step
```

Calculate:

```text
safety_score = min(1.0, sum(configured boosts for detected flags))
```

This ensures that highly relevant negative evidence survives selection.

## 13. Final Score

Initial formula:

```text
final_score =
    0.35 * relation_score
  + 0.30 * text_score
  + 0.15 * distance_score
  + 0.10 * evidence_quality_score
  + 0.10 * safety_score
```

Store all score components:

```yaml
path_id: path_017
relation_score: 1.0
text_score: 0.85
distance_score: 1.0
evidence_quality_score: 0.5
safety_score: 0.9
final_score: 0.895
```

Deterministic tie-breaking should use:

1. Higher final score
2. Higher safety score
3. Lower typed traversal distance
4. Stable path ID

## 14. Connected Subgraph Selection

Create:

```text
experiments/query_driven_graph/src/subgraph_selector.py
```

Algorithm:

1. Sort candidate paths by deterministic score order.
2. Always retain candidates above a configured critical-safety threshold.
3. Add paths while respecting path, node, and edge budgets.
4. Include every intermediate node and edge on an accepted path.
5. Deduplicate identical nodes and edges.
6. Stop when all budgets are exhausted.

The selector should return:

```python
@dataclass(frozen=True)
class SelectedSubgraph:
    nodes: tuple[dict[str, Any], ...]
    edges: tuple[dict[str, Any], ...]
    selected_paths: tuple[ScoredPath, ...]
    rejected_path_count: int
```

## 15. Prompt Serialization

Create:

```text
experiments/query_driven_graph/src/evidence_serializer.py
```

Render compact, connected evidence:

```text
Current step: step_4 — Install front chassis pin

Selected graph evidence:
1. step_4 -[REQUIRES]-> aligned(front_chassis_pin, front_chassis)
   support_status: missing
   confidence: 1.0

2. step_4 -[HAS_CONSTRAINT]-> requires_alignment
   requires_alignment -[SUPPORTED_BY]-> observed_alignment_evidence
   support_status: observed
```

Do not send:

- Raw full IDs
- Full Cypher text unless required for a specific study
- Repeated node properties
- Candidate scores unless the study explicitly tests their effect
- Rejected candidate paths

Prompt text must remain in the experiment's `prompts.yaml`; the serializer
should produce evidence data inserted into those templates.

## 16. Retrieval Diagnostics

Write one structured diagnostic record per interaction:

```yaml
interaction: 4
case_id: case_002_possible_wrong_part
retrieval_strategy: heuristic_path_expansion
question_analysis:
  concepts:
    - component
  matched_terms:
    - part
candidate_path_count: 34
selected_path_count: 6
selected_node_count: 12
selected_edge_count: 11
selected_paths:
  - path_id: path_003
    relations:
      - HAS_ENTITY
      - HAS_PREDICATE
    final_score: 0.82
    score_components:
      relation: 0.9
      text: 0.8
      distance: 0.7
      evidence_quality: 1.0
      safety: 0.0
retrieval_duration_seconds: 0.034
```

Suggested output:

```text
outputs/retrieval_diagnostics_<strategy>_<timestamp>.jsonl
```

Communication logs should contain summary events but not entire prompt bodies.

## 17. Runner Integration

Suggested high-level runner flow:

```python
analysis = analyze_question(question, retrieval_config)
candidates = retrieve_candidate_paths(
    client=client,
    graph_name=graph_name,
    step_id=canonical_step_id,
    config=retrieval_config,
)
scored_paths = score_candidate_paths(analysis, candidates, retrieval_config)
subgraph = select_subgraph(scored_paths, retrieval_config)
evidence_text = serialize_selected_subgraph(subgraph)
prompt = build_answer_prompt(..., evidence_text=evidence_text)
response = ask_llm(...)
```

Keep LLM exception handling interaction-scoped, as in the current runner.

## 18. Preflight Validation

Extend preflight checks to validate:

- Retrieval configuration structure
- Scoring weights sum to `1.0`
- All configured relation types are approved
- Candidate query is read-only
- Current step exists
- Candidate retrieval stays within configured budgets
- Every test question can produce a diagnostic record

An empty selected subgraph should be handled explicitly rather than causing an
unexplained failure.

## 19. Testing Plan

### Unit tests

Test:

- Question normalization
- Concept detection
- Relation scoring
- Weighted lexical overlap
- Distance scoring
- Evidence-quality scoring
- Safety flag detection
- Final-score calculation
- Deterministic tie-breaking
- Node and edge budget enforcement
- Compact serialization

### Synthetic graph tests

Build small graphs where the expected best path is obvious:

```text
step_2 -[REQUIRES]-> alignment_missing
step_2 -[NEXT]-> step_3
step_2 -[HAS_ENTITY]-> unrelated_tool
```

Verify that an alignment question ranks `alignment_missing` first.

### Integration tests

Mock Neo4j results and verify:

- Full interaction processing
- Diagnostics written
- Selected evidence passed to the prompt builder
- Canonical IDs preserved in stored artifacts
- Compact IDs used in the LLM prompt
- A retrieval failure does not erase prior rows

## 20. Evaluation Plan

Run the same test cases under:

```text
template_pattern
heuristic_path_expansion
```

Measure:

### Retrieval quality

- Relevant evidence recall
- Relevant evidence precision
- Safety-critical evidence recall
- Number of selected nodes and edges
- Candidate-to-selected reduction ratio

### Prompt efficiency

- Prompt characters
- Estimated or measured input tokens
- Repeated identifier count

### Runtime

- Neo4j retrieval duration
- Ranking duration
- Total interaction duration

### Answer quality

- Expected answer element coverage
- Unsupported claims
- Correct refusal when evidence is missing
- Safety appropriateness
- Consistency across repeated runs

## 21. Suggested File Layout

```text
experiments/query_driven_graph/
├── configs/
│   ├── config_query_driven_graph.yaml
│   ├── prompts_query_driven_graph.yaml
│   ├── query_templates.yaml
│   └── retrieval_scoring.yaml
└── src/
    ├── question_analyzer.py
    ├── candidate_retriever.py
    ├── path_ranker.py
    ├── subgraph_selector.py
    ├── evidence_serializer.py
    ├── retrieval_diagnostics.py
    └── run_experiment_query_driven_graph.py

experiments/shared/configs/
└── graph_retrieval.yaml
```

## 22. Recommended Delivery Stages

### Stage 1: Independent question analysis

- Stop using `risk_type`
- Add configured concept extraction
- Keep the current Cypher templates

This isolates and measures the effect of removing evaluation leakage.

### Stage 2: Candidate expansion

- Add one-step sequence retrieval and two-level semantic-evidence retrieval
- Enforce expandable and terminal node-type rules
- Save candidate paths without changing the final prompt

This validates graph traversal and diagnostics.

### Stage 3: Heuristic ranking

- Add relation, lexical, distance, quality, and safety scores
- Compare ranking with manually expected evidence

### Stage 4: Connected selection and prompting

- Enforce graph budgets
- Serialize selected evidence
- Run LLM evaluations

### Stage 5: Optional semantic models

Only after evaluating the heuristic baseline:

- Add sentence-embedding similarity as an alternative `text_score`
- Compare heuristic and embedding text relevance
- Consider an LM relation selector under strict validation

GNN retrieval should be considered only if the graph and labeled training data
become large enough to justify it.

## 23. Initial Success Criteria

The first heuristic path-expansion version should:

- Use no `risk_type` information during retrieval
- Use independent `sequence_hops: 1` and `semantic_hops: 2` limits
- Expand semantic traversal only through approved node types
- Preserve all selected safety-critical evidence
- Produce deterministic rankings
- Reduce prompt evidence compared with unfiltered candidate retrieval
- Log every scoring decision
- Match or improve answer quality relative to the fixed-template baseline
