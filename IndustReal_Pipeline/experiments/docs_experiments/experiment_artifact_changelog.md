# Experiment Artifact Changelog

## 2026-07-05 - ADR-004 alignment-scope metadata patch

- Patch ids:
  - Response JSONLs and one-to-one prompt/query reports use `patched_<original response JSONL timestamp>`.
  - Combined human-judgement packets use `patched_20260704T130004+0200`, matching the original human packet timestamp.
- Scope: post-hoc correction of evaluation metadata wording for Q09 alignment-scope artifacts.
- Source copies: created patched copies of the latest `responses_*.jsonl` files under:
  - `experiments/llm_guidance_ablation/outputs/`
  - `experiments/query_driven_graph/outputs/`
- Regenerated/copied reports with the same patch id under:
  - `experiments/llm_guidance_ablation/outputs/prompt_reports/`
  - `experiments/query_driven_graph/outputs/query_reports/`
  - `experiments/docs_experiments/human_judgement/`
- Corrected stale wording from the earlier "base exception to all-component alignment" framing to the ADR-004 alignment-scope framing.
- Did not rerun LLM experiments. Actual operator questions, prompts sent to the LLM, retrieved evidence, and model responses were preserved.
- The maintained source question YAMLs had already been corrected; this patch brings generated response metadata and derived reports into alignment with that current wording.

## 2026-07-05 - Blind packet expected-answer elements

- Patch id: `patched_20260704T130004+0200` for the combined human-judgement packets.
- Added `expected_answer_elements` beside each question in patched blind human-judgement packets so judges can see the target answer elements inline with the item.
- Updated the blind-packet generator to include expected answer elements in future generated blind packets.
