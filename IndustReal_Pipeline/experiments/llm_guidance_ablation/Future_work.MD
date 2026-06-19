# Future Work

## Graph-Only Prompting Condition

The current ablation should retain the generated procedural step list in the
`graph_grounded` condition. Although the graph embeds step information, keeping
the same step-list artifact across the existing conditions is methodologically
important:

- `steps_only` establishes the baseline.
- `symbolic_domain` adds symbolic evidence to that baseline.
- `graph_grounded` adds graph evidence to that baseline.

This design isolates the contribution of the additional evidence. Removing the
step list only from `graph_grounded` would change both the representation and
the available context in the following way:

- Representation: graph_grounded would receive graph relationships instead of the shared textual procedure.
- Available context: it would only see steps present in the extracted local subgraph, while other conditions receive the complete step list.

Which would make direct comparisons less controlled.

The shared step list does have costs. It increases prompt length, duplicates
sequence information already present in the graph, and may make the relevant
local evidence harder for the model to identify. The explicit local sequence
summary in the graph evidence helps reduce this ambiguity while preserving the
controlled comparison.

A future experiment should introduce a separate `graph_only` condition. The
resulting comparison would be:

1. `steps_only`
2. `symbolic_domain` (`steps + symbolic evidence`)
3. `graph_grounded` (`steps + graph evidence`)
4. `graph_only`

This additional condition would test whether the graph can replace the step
list, rather than only measuring the graph's incremental value when added to
it. Prompt length and context-budget usage should also be reported for each
condition so that improvements are not interpreted independently of their
context cost.
