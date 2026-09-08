# AGENTS.md

This repository uses a persistent research-state protocol and an optional event-driven local Harness dispatcher.

## Before doing work

Read, in order:

1. `HARNESS_INBOX.md` — current human-readable executable task and scope.
2. `.harness/task.json` — machine dispatch identity/status; do **not** modify it.
3. `PROJECT_STATE.md` — current authoritative state.
4. Files explicitly referenced by the task.
5. `AUTONOMY_POLICY.md` when automatic continuation or repair is involved.
6. `docs/REVIEW_PROTOCOL.md` for `PULL_REQUEST` delivery.
7. `docs/PROVENANCE.md` when external sources or non-Git artifacts are involved.

Read `CONTEXT_LEDGER.md` when broader reasoning context is necessary.

## Execution rules

- Work only on the current task unless a minimal adaptation is required by source/environment reality.
- Do not silently expand scope or skip stage gates.
- Prefer exact source/code inspection and reproducible experiments over assumptions.
- Preserve failed experiments and first mismatches/errors.
- Record exact commands, revisions, configs, environment, metrics, and artifact paths.
- Distinguish **observed**, **derived**, and **interpreted** claims.
- Do not rewrite project hypotheses or decisions as if tentative local interpretations were reviewed facts.
- Do not publish or invent the next task. Suggest next actions only in `HARNESS_OUTBOX.md`.
- Never edit `.harness/task.json` or `.harness/completed.json`.
- Do not retry the same task ID. Repairs require a new ID issued by the planner.
- Never place credentials, access tokens, private keys, large model weights, or sensitive local files into Git.
- Register important upstream/model/dataset revisions in `provenance/sources.json`.
- Register important large/external artifacts in `provenance/artifacts.json` rather than committing them blindly.

## Delivery behavior

The dispatcher exports:

- `HARNESS_TASK_ID`
- `HARNESS_INBOX_PATH`
- `HARNESS_AUTONOMY`
- `HARNESS_DELIVERY_MODE`
- `HARNESS_BASE_BRANCH`
- `HARNESS_WORK_BRANCH`

### `PULL_REQUEST`

- remain on `HARNESS_WORK_BRANCH`;
- commit intentional source/config/report/provenance changes before exit;
- update `HARNESS_OUTBOX.md` with the evidence package;
- do not merge the branch;
- expect the workflow to push it and open a PR;
- address reviewer findings on that PR when asked.

### `DIRECT`

Use only when explicitly assigned. Commit only intended project changes plus structured communication state.

The workflow never runs `git add -A`, so uncommitted arbitrary files will not be published automatically.

## Before finishing

Update `HARNESS_OUTBOX.md` with:

- task ID and delivery mode;
- PASS / FAIL / BLOCKED / PARTIAL;
- gate token/result;
- exact commands;
- revisions/environment;
- results and controls;
- evidence paths and provenance IDs;
- unexpected findings;
- failures/mismatches;
- observed/derived facts vs tentative interpretations;
- hypothesis/state impact suggestions;
- review recommendation;
- suggested next action.

## Authority order

When instructions conflict, use:

```text
current HARNESS_INBOX task
> PROJECT_STATE / reviewed canonical state
> RESEARCH_TASK stage plan
> older reviewed reports/PRs
> older outbox/raw evidence
> chat recollection or assumptions
```

If current source evidence contradicts canonical state, report the contradiction explicitly rather than forcing the old assumption.
