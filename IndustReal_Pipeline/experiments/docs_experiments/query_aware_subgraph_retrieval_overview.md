# Query-Aware Subgraph Retrieval: High-Level Overview

## Purpose

The current `query_driven_graph` experiment chooses one predefined Cypher query
for each operator question. This is a useful baseline because it is predictable,
easy to inspect, and easy to debug.

The proposed next step is more flexible: instead of choosing one fixed query and
accepting everything it returns, the system explores a small area around the
current assembly step and selects the graph evidence that is most relevant to
the question.

The goal is not to replace the graph or let an LLM search it freely. The goal is
to retrieve a small, connected, explainable subgraph before asking the LLM to
write an answer.

## Current Approach

The current sequence is:

```text
Operator question
        │
        ▼
Choose one intent using fixed rules
        │
        ▼
Select one predefined Cypher template
        │
        ▼
Query the current step and specific neighboring evidence
        │
        ▼
Send all returned rows to the LLM
```

For example, an installation question selects the `installation_check`
template. That template always looks for relations such as `REQUIRES`,
`PRODUCES`, `DEPENDS_ON`, and `SUPPORTED_BY`.

This can be summarized as:

> “This looks like an installation question, so execute the installation
> query.”

## Proposed Approach

The proposed sequence is:

```text
Operator question
        │
        ▼
Identify the concepts mentioned in the question
        │
        ▼
Start from the known current step
        │
        ▼
Expand along two controlled dimensions:
sequence steps and semantic evidence
        │
        ▼
Score the candidate paths for relevance
        │
        ▼
Keep the best connected evidence
        │
        ▼
Send the compact subgraph to the LLM
```

This can be summarized as:

> “This question concerns installation and validation. Starting from the
> current step, follow graph links that can answer it and retain the strongest
> evidence.”

## End-to-End Sequence

### 1. Read the operator question

The system receives the question and the current step. The current step remains
the trusted starting point in the graph.

Example:

```text
Current step: step_4
Question: Can I continue if this pin may not be aligned correctly?
```

### 2. Identify question concepts

Simple, configured rules identify concepts such as:

- Sequence or continuation
- Installation
- Alignment or validation
- Removal or rework
- Tool use
- Confidence or evidence

The example question would likely activate:

```text
sequence
installation
validation
```

This first version does not require an LLM, embeddings, or a learned classifier.

### 3. Explore a bounded, typed graph neighborhood

The system starts at `step_4`, but it does not apply one generic hop limit to
every node and relationship. It uses two separate traversal budgets:

- `sequence_hops` controls movement between `Step` nodes through `NEXT`.
- `semantic_hops` controls movement from the original current step through
  evidence relationships.

With `sequence_hops: 1`, the sequence context is:

```text
previous step ← current step → next step
```

With `semantic_hops: 2`, the evidence expansion can be:

```text
step_4
  └── HAS_CONSTRAINT ──> alignment constraint    semantic hop 1
                              └── SUPPORTED_BY ──> observed evidence
                                                    semantic hop 2
```

Semantic expansion starts from the original current step, not automatically
from every previous or next step found by sequence traversal. Expansion is also
node-type-aware: constraints and predicates may be expanded further, while
neighboring steps, entities, rules, and sources are normally terminal.

The search is deliberately limited:

- Separate sequence and semantic hop limits
- Node-type-specific expansion rules
- Approved relation types only
- Maximum numbers of nodes, edges, and paths
- Read-only graph access

The numeric sequence and semantic limits are shared by all graph-using
experiments through:

```text
experiments/shared/configs/graph_retrieval.yaml
```

They should not be copied into individual experiment configs.

### 4. Create candidate evidence paths

The explored neighborhood is divided into understandable paths, such as:

```text
step_4 -[REQUIRES]-> aligned(front_chassis_pin, front_chassis)
```

or:

```text
step_4 -[HAS_CONSTRAINT]-> requires_alignment
       -[SUPPORTED_BY]-> observed_alignment_evidence
```

### 5. Estimate relevance

Each candidate receives an explainable score based on:

- Whether its relationships fit the question concepts
- Whether its labels and arguments match words in the question
- Its distance from the current step
- Its confidence and support status
- Whether it exposes a safety-relevant problem

This is heuristic semantic relevance. It means relevance is estimated using
explicit rules and graph properties instead of an opaque model.

### 6. Preserve important warnings

Missing, uncertain, rejected, incompatible, or invalidated evidence should not
be removed merely because its confidence is low. Such evidence can be the most
important part of a safety-oriented answer.

The ranking therefore distinguishes:

- How relevant evidence is
- How strongly supported evidence is
- Whether evidence signals a risk

### 7. Select a compact connected subgraph

The system keeps the best paths and all intermediate nodes needed to understand
them. It does not simply select unrelated high-scoring nodes.

The result may look like:

```text
Current: step_4 — Install front chassis pin

Relevant evidence:
1. step_4 REQUIRES aligned(front_chassis_pin, front_chassis)
   status: missing

2. step_4 HAS_CONSTRAINT requires_alignment
   requires_alignment SUPPORTED_BY observed_alignment_evidence
   status: observed
```

### 8. Ask the LLM to answer

The LLM receives:

- The operator question
- The compact current-step identity
- The selected graph evidence
- Only the procedural context that is still necessary

It does not receive every candidate, full internal identifiers, or irrelevant
graph properties.

### 9. Save retrieval diagnostics

The experiment records:

- Concepts detected in the question
- Candidate paths considered
- Scores assigned to each selected path
- Paths included in the final prompt
- Prompt size and retrieval time

This makes it possible to tell whether a bad answer came from poor retrieval or
from the LLM.

### 10. Compare with the current baseline

The existing fixed-template approach should remain available as the baseline.
Both methods should run on the same questions and graph.

Compare:

- Relevant evidence retrieved
- Irrelevant evidence included
- Safety warnings recovered
- Prompt size
- Retrieval latency
- Final answer quality and consistency

## Research Classification

The current implementation is primarily:

- Query-based subgraph pattern matching
- Traditional rule-based graph retrieval

The proposed implementation would be a hybrid of:

- Fixed-hop path-based expansion
- Query-aware or semantically relevant path filtering
- Traditional graph retrieval algorithms

It would still not be:

- Embedding-based retrieval
- An LM-based retriever
- A GNN-based retriever

Those methods can be considered later if the transparent heuristic baseline is
not sufficient.

## Recommended Development Order

1. Remove `risk_type` from retrieval decisions.
2. Add question-concept configuration.
3. Add bounded sequence and semantic-evidence expansion.
4. Convert candidate results into paths.
5. Implement transparent relevance scoring.
6. Select a connected evidence subgraph.
7. Serialize it compactly for the LLM.
8. Log complete retrieval diagnostics.
9. Evaluate it against the current fixed-template baseline.
10. Consider embeddings only after the baseline has been measured.
