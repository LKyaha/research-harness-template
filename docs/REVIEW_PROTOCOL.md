# REVIEW PROTOCOL

This repository treats review as a scientific gate, not only a code-style check.

## What a review evaluates

Review a Harness result in this order:

1. **Execution integrity** — did the code/experiment actually run what the task claimed?
2. **Instrumentation validity** — are hooks, baselines, controls, metrics, seeds, and failure handling correct?
3. **Scientific validity** — do the observations support the stated conclusion, and what alternative explanations remain?
4. **Reproducibility** — are commands, revisions, configs, environments, data references, and artifacts sufficient to repeat the result?
5. **Provenance** — are external sources and large artifacts identified by immutable revision/checksum where practical?
6. **State impact** — which hypotheses, decisions, exclusions, unknowns, and next actions should change?

A clean diff with weak evidence is not a successful research review.

## Delivery modes

### `DIRECT`
Use for bounded communication/state-only work where code review adds little value. The Harness may commit to the dispatch branch according to repository policy.

### `PULL_REQUEST`
Preferred for code, instrumentation, experiment design, reusable tools, or any result that may change canonical research conclusions.

A PR should contain one coherent evidence package:

- task ID and research question;
- code/config changes;
- exact test/experiment commands;
- `HARNESS_OUTBOX.md` result;
- reports or compact result files;
- provenance updates;
- pointers/checksums for large external artifacts;
- explicit hypothesis/state implications.

## Reviewer outcomes

### `APPROVE`
The evidence supports merging. Approval does **not** automatically mean every tentative interpretation becomes canonical truth. Canonical state is updated separately after review.

### `REQUEST_CHANGES`
Use when code, controls, instrumentation, reproducibility, or evidence is insufficient. The Harness should fix the same PR when the research question has not changed.

### `HUMAN_REVIEW_REQUIRED`
Use when the result changes project direction, requires material cost/compute, creates legal/license/privacy concerns, or leaves a high-impact ambiguity that should not be resolved automatically.

## Evidence vs. interpretation

Review comments should label claims as one of:

- **Observed** — directly measured or inspected.
- **Derived** — mechanically computed from observed data.
- **Interpreted** — plausible explanation that may have alternatives.
- **Decision** — chosen project direction after weighing evidence.

Do not merge these categories in prose.

## Merge discipline

Before merge, verify:

- declared gate result is supported;
- no silent scope expansion occurred;
- tests/controls cover the mechanism being claimed;
- failed or contradictory evidence was preserved;
- source revisions and artifact locations are recorded;
- large/generated files are not accidentally committed;
- no credentials, private data, model secrets, or machine-specific caches are included;
- the PR identifies what canonical state should be reconsidered after merge.

## Post-merge compression

After merge, the planner/reviewer should compress durable findings into, as appropriate:

`HYPOTHESES.md` → `DECISIONS.md` / `FAILURES.md` / `UNRESOLVED.md` → `CONTEXT_LEDGER.md` → `PROJECT_STATE.md`.

The PR and raw artifacts remain provenance; they are not themselves the current project state.
