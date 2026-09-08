# AUTONOMY_POLICY

This file defines how far the research loop may continue without human review.

## Default level

**Level 2 — analyze, plan, and dispatch bounded tasks; do not run an unbounded autonomous loop.**

The planner may review evidence, update canonical state, prepare the next task, and publish a new `READY` task. The local Harness may execute each newly published task exactly once. A new task ID is required for every new execution.

For reviewable research/code work, the recommended delivery mode is `PULL_REQUEST`. Event-driven execution transport does not remove the review gate.

## Decision classes

### `AUTO_CONTINUE`
Use only when all of the following are true:

- the previous task reached its declared gate or produced an expected intermediate result;
- the next step is already inside the reviewed research plan;
- no major new contradiction changes the project model;
- the next task stays within declared compute, cost, data, and safety limits;
- no destructive or irreversible action is required.

### `AUTO_REPAIR`
Use for a bounded repair when:

- the failure is local and well diagnosed;
- the repair does not change the research question;
- the repair is cheap and reversible;
- retry count remains within the task's failure budget.

A repair still requires a **new task ID**. Never repeatedly retry the same task ID.

### `HUMAN_REVIEW_REQUIRED`
Stop and notify the human operator when any of the following occurs:

- evidence contradicts a major canonical assumption;
- the proposed next step changes the research direction or success criteria;
- large training, material cloud/API spend, or unusual hardware usage is required;
- credentials, account permissions, private data, publishing, licensing, or legal judgment is required;
- destructive actions, data deletion, force pushes, or irreversible migration are proposed;
- the same failure mode repeats beyond the declared failure budget;
- the Harness cannot distinguish a real result from an instrumentation/environment failure;
- a high-impact PR has unresolved evidence/reproducibility concerns;
- the planner is materially uncertain whether continuing is safe or scientifically meaningful.

## Delivery modes

### `DIRECT`
Use only for bounded work where a separate review branch adds little value and repository policy explicitly permits direct delivery.

### `PULL_REQUEST`
Recommended for:

- source-code changes;
- instrumentation and hooks;
- experiment definitions;
- reusable scripts/tools;
- provenance changes tied to conclusions;
- evidence likely to change hypotheses, exclusions, decisions, or canonical state.

`PULL_REQUEST` means execution may be automatic, but **acceptance is not**: the result must survive review before it becomes reviewed/merged evidence.

## Hard rules

1. **One task ID, at most one execution attempt.**
2. Only `.harness/task.json` with `status: READY` may trigger local execution.
3. A task is claimed in `.harness/completed.json` on the base branch before execution.
4. `HARNESS_OUTBOX.md`, reports, artifacts, PR commits, canonical-state updates, and normal commits must never trigger execution by themselves.
5. The Harness must not invent the next task. It may suggest one in `HARNESS_OUTBOX.md`, but a planner must publish a new task ID.
6. The Harness must not merge its own PR or silently promote tentative interpretations into canonical state.
7. A failed scientific hypothesis is not an infrastructure failure. Preserve the result; do not retry it until it becomes positive.
8. Raw evidence is never silently promoted into canonical state.
9. Significant external sources and large artifacts should be traceable through provenance records.

## Resource guardrails

Each project should replace these placeholders before enabling automatic execution:

- Maximum wall time per task: `[SET_ME]`
- Maximum GPU hours per task: `[SET_ME]`
- Maximum API/cloud spend per task: `[SET_ME]`
- Maximum automatic repair attempts: `[SET_ME]`
- Allowed machines/runners: `[SET_ME]`
- Allowed external services: `[SET_ME]`

If a limit is unset and a task would materially consume the corresponding resource, use `HUMAN_REVIEW_REQUIRED`.

## Autonomy levels

- **Level 0:** monitor only.
- **Level 1:** monitor + analyze + notify.
- **Level 2:** monitor + analyze + update state + publish the next bounded task.
- **Level 3:** Level 2 plus event-driven local execution of each published task; PR review remains available/encouraged.
- **Level 4:** long-running closed loop with human review only at explicitly declared boundaries.

This template defaults to the reasoning discipline of Level 2 while providing an optional Level-3 execution transport. Moving a project to Level 3 or 4 must be an explicit human decision recorded in `DECISIONS.md`.
