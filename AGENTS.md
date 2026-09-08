# AGENTS.md

This repository uses a persistent research-state protocol and an optional event-driven local Harness dispatcher.

## Before doing work

Read, in order:

1. `HARNESS_INBOX.md` — current human-readable executable task and scope.
2. `.harness/task.json` — machine dispatch identity/status; do **not** modify it.
3. `PROJECT_STATE.md` — current authoritative state.
4. Files explicitly referenced by the task.
5. `AUTONOMY_POLICY.md` when automatic continuation or repair is involved.

Read `CONTEXT_LEDGER.md` when broader reasoning context is necessary.

## Execution rules

- Work only on the current task unless a minimal adaptation is required by source/environment reality.
- Do not silently expand scope or skip stage gates.
- Prefer exact source/code inspection and reproducible experiments over assumptions.
- Preserve failed experiments and first mismatches/errors.
- Record exact commands, revisions, configs, environment, metrics, and artifact paths.
- Distinguish observed facts from interpretation.
- Do not rewrite project hypotheses or decisions as if tentative local interpretations were reviewed facts.
- Do not publish or invent the next task. Suggest next actions only in `HARNESS_OUTBOX.md`.
- **Never edit `.harness/task.json`.** The dispatcher reverts such changes, and task publication belongs to the planner.
- Do not retry the same task ID. Repairs require a new ID issued by the planner.
- Never place credentials, access tokens, private keys, large model weights, or sensitive local files into Git.

## When running under the self-hosted dispatcher

The workflow will only auto-stage communication state. Therefore:

- commit intentional source/report changes before the Harness exits;
- do not push secrets or large generated data;
- record external artifact locations/checksums when data should stay outside Git;
- the workflow will push committed work after execution.

## Before finishing

Update `HARNESS_OUTBOX.md` with:

- task ID;
- PASS / FAIL / BLOCKED / PARTIAL;
- gate token/result;
- exact commands;
- revisions/environment;
- results;
- artifacts;
- unexpected findings;
- failures/mismatches;
- facts vs tentative interpretations;
- suggested next action;
- whether human review is recommended.

## Authority order

When instructions conflict, use:

```text
current HARNESS_INBOX task
> PROJECT_STATE / reviewed canonical state
> RESEARCH_TASK stage plan
> older reports/outbox
> chat recollection or assumptions
```

If current source evidence contradicts canonical state, report the contradiction explicitly rather than forcing the old assumption.
