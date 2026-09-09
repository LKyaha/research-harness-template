## Task / question

- Task ID: `TASK-...`
- Stage: `[stage]`
- Research question: [what uncertainty this PR resolves]
- Declared gate: `[PASS_TOKEN / criterion]`

## What changed

- [code / config / instrumentation / experiment / report]

## Execution evidence

- Exact commands:

```text
[commands]
```

- Environment/revisions: [OS, runtime, source/model commits]
- Result status: `PASS / FAIL / BLOCKED / PARTIAL`
- Gate result: `[result]`

## Controls and validity

- Baseline/control: [description]
- Negative/positive controls: [if applicable]
- Known confounders: [list]
- First mismatch/failure preserved at: [path]

## Evidence package

- Harness outbox: `HARNESS_OUTBOX.md`
- Report(s): [paths]
- Compact result files: [paths]
- Source provenance IDs: [SRC-...]
- Artifact provenance IDs: [ART-...]

## Hypothesis / state impact

- Hypotheses supported: [H-... or none]
- Hypotheses contradicted: [H-... or none]
- Decisions/exclusions that may need review: [D-... / item]
- Unknowns remaining: [items]

## Large/external artifacts

[List location + checksum/provenance ID. Do not attach large raw data or secrets to the PR.]

## Harness self-check

- [ ] Scope stayed within `HARNESS_INBOX.md`.
- [ ] Exact commands/configs/revisions are recorded.
- [ ] Observed facts are separated from interpretation.
- [ ] Failed/contradictory evidence was preserved.
- [ ] Important external sources/artifacts have provenance records.
- [ ] No credentials/private data/cache/model blobs were accidentally committed.
- [ ] I did not silently change canonical project state or invent the next task.

## Reviewer checklist

- [ ] Execution and instrumentation match the claimed experiment.
- [ ] Controls support the causal/scientific claim.
- [ ] Evidence is reproducible enough for the importance of the conclusion.
- [ ] Provenance is sufficient to revisit the result later.
- [ ] State implications are justified by evidence, not just narrative.
- [ ] Merge / request changes / human review decision is explicit.
