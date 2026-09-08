# CONTEXT COMPRESSION PROTOCOL

The repository is an external working memory, but dumping everything into Markdown is not memory management. Durable context must be compressed.

## Principle

> Preserve what remains decision-relevant, not everything that happened.

## Information ladder

```text
raw logs / source / data / chat
        ↓
experiment report or structured observation
        ↓
evidence item
        ↓
hypothesis / failure / decision update
        ↓
CONTEXT_LEDGER
        ↓
PROJECT_STATE
```

Each step should reduce volume while increasing decision relevance.

## What belongs in raw artifacts

- full stdout/stderr;
- large metric dumps;
- raw tensors/data;
- complete source snapshots;
- exhaustive benchmark outputs.

These should be referenced, not copied wholesale into canonical state.

## What belongs in reports

- experiment question;
- exact setup;
- controls;
- observations;
- uncertainty;
- pointers to raw evidence.

## What belongs in HYPOTHESES / DECISIONS / FAILURES

Only findings that change what we believe or what we will do.

Examples:

- a hypothesis gains or loses support;
- an approach is ruled out under defined conditions;
- a design decision is made and has a revisit condition.

## What belongs in CONTEXT_LEDGER

A compact causal map of the project:

1. Goal
2. Current model of the system
3. Strongest evidence
4. Active hypotheses
5. Ruled-out explanations
6. Decisions
7. Contradictions
8. Unknowns
9. Next discriminating action

## What belongs in PROJECT_STATE

Only what a new agent needs to resume correctly in a few minutes:

- objective;
- current best model;
- current stage;
- confirmed findings;
- ruled-out paths;
- blockers;
- single next action.

## Promotion rule

Do not promote an observation into canonical state merely because it occurred once. Before promotion ask:

- Is it reproducible or directly source-grounded?
- Does it change a hypothesis, decision, exclusion, blocker, or next action?
- Can another agent verify it from a pointer?
- Is uncertainty labeled correctly?

If not, keep it in a report/outbox.

## Contradiction rule

Do not append contradictory summaries forever. When evidence changes the model:

1. preserve the old hypothesis/decision history in its registry;
2. update the current model in `CONTEXT_LEDGER.md`;
3. update the short snapshot in `PROJECT_STATE.md`;
4. record why the old model changed.

## Failure retention

Failed work should be compressed, not erased. Preserve:

- what was tried;
- why it failed;
- evidence pointer;
- retry condition.

This prevents future agents from repeating dead ends.

## Context budget heuristic

Canonical state should remain small enough to reread frequently. If `PROJECT_STATE.md` starts becoming a history log, move details down the ladder. If `CONTEXT_LEDGER.md` becomes a raw experiment dump, move details into reports/artifacts.
