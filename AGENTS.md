# AGENTS.md

This repository uses a persistent research-state protocol.

## Before doing work

Read, in order:

1. `HARNESS_INBOX.md` — current executable task and scope.
2. `PROJECT_STATE.md` — current authoritative state.
3. Files explicitly referenced by the task.

Read `CONTEXT_LEDGER.md` when broader reasoning context is necessary.

## Execution rules

- Work only on the current task unless a minimal adaptation is required by source/environment reality.
- Do not silently expand scope or skip stage gates.
- Prefer exact source/code inspection and reproducible experiments over assumptions.
- Preserve failed experiments and first mismatches/errors.
- Record exact commands, revisions, configs, environment, metrics, and artifact paths.
- Distinguish observed facts from interpretation.
- Do not rewrite project hypotheses or decisions as if tentative local interpretations were reviewed facts.

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
- suggested next action.

Commit/push relevant code and artifacts according to repository policy.

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
