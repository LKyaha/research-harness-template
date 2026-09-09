# HARNESS_INBOX

**Task ID:** [TASK-ID]  
**Issued:** [YYYY-MM-DD]  
**Project stage:** [STAGE]  
**Autonomy decision:** [AUTO_CONTINUE | AUTO_REPAIR | HUMAN_REVIEW_REQUIRED]  
**Delivery mode:** [DIRECT | PULL_REQUEST]

This file is the human-readable executable contract from ChatGPT/project lead to the local Harness.

## Machine dispatch contract

Automatic local execution is controlled separately by `.harness/task.json`.

For an intentionally dispatched task, the planner must publish the same unique task ID and delivery mode there with `status: READY`.

Rules:

- `HARNESS_INBOX.md` explains **what to do**.
- `.harness/task.json` decides **whether local execution should start**.
- A task ID may be consumed at most once.
- A retry or repair requires a new task ID.
- The Harness must never publish its own next task or modify `.harness/task.json` / `.harness/completed.json`.
- If autonomy is `HUMAN_REVIEW_REQUIRED`, do not execute automatically.
- `PULL_REQUEST` is preferred for code, instrumentation, experiment design, reusable tools, or evidence that may change canonical conclusions.

## Objective

[One precise objective.]

## Why this task now

[Which uncertainty, hypothesis, or gate this task addresses.]

## Read first

1. `PROJECT_STATE.md`
2. `CONTEXT_LEDGER.md`
3. `RESEARCH_TASK.md`
4. `AUTONOMY_POLICY.md`
5. `docs/REVIEW_PROTOCOL.md` when delivery mode is `PULL_REQUEST`
6. `docs/PROVENANCE.md` when external sources or non-Git artifacts are involved
7. Relevant source/code/report pointers listed below

## Scope

### Do

- [ ] [Action]

### Do not

- [ ] [Explicitly excluded work]

## Resource limits

- Maximum wall time: [SET_ME]
- Maximum GPU hours: [SET_ME]
- Maximum external/API/cloud cost: [SET_ME]
- Automatic repair budget: [SET_ME]

Unset material resource limits require human review before expensive execution.

## Required implementation / experiment

[Detailed instructions, inputs, controls, metrics, expected files.]

## Required evidence

Return enough evidence that another agent can independently verify the conclusion:

- exact commands;
- git commit/revision;
- environment/version information;
- configs;
- raw or summarized metrics;
- compact evidence/report paths;
- first failure/mismatch details when applicable;
- `SRC-*` IDs for important external sources;
- `ART-*` IDs + checksum/location for important artifacts kept outside Git.

## Review / delivery contract

### `DIRECT`

Use only when the task explicitly permits direct delivery. Commit only intended project changes plus structured communication state.

### `PULL_REQUEST`

- work on the dispatcher-assigned branch from `HARNESS_WORK_BRANCH`;
- commit intentional code/config/report/provenance changes there;
- do not merge your own branch;
- prepare `HARNESS_OUTBOX.md` as part of the evidence package;
- expect the workflow to push the branch and open a PR;
- respond to review findings on the same PR unless the research question itself changes.

## Gate

The task is complete only if one of the following is reported:

```text
[PASS_TOKEN]
```

or

```text
FAIL
BLOCKED
PARTIAL
```

with evidence and explanation.

## Output contract

Update `HARNESS_OUTBOX.md` using its schema. Commit relevant project code, compact artifacts, reports, and provenance records before exiting when running under the self-hosted workflow. The workflow will commit only communication-state files and push the assigned work branch.

Do not silently broaden the research direction. If repository/source reality contradicts this task, document the contradiction in `HARNESS_OUTBOX.md` and stop or make only the minimum safe adaptation needed to collect evidence.
