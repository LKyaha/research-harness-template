# HARNESS_INBOX

**Task ID:** [TASK-ID]  
**Issued:** [YYYY-MM-DD]  
**Project stage:** [STAGE]  
**Autonomy decision:** [AUTO_CONTINUE | AUTO_REPAIR | HUMAN_REVIEW_REQUIRED]

This file is the human-readable executable contract from ChatGPT/project lead to the local Harness.

## Machine dispatch contract

Automatic local execution is controlled separately by `.harness/task.json`.

For an intentionally dispatched task, the planner must publish the same unique task ID there with:

```json
{
  "task_id": "[TASK-ID]",
  "status": "READY",
  "autonomy": "AUTO_CONTINUE"
}
```

The exact schema contains additional fields; preserve them.

Rules:

- `HARNESS_INBOX.md` explains **what to do**.
- `.harness/task.json` decides **whether local execution should start**.
- A task ID may be consumed at most once.
- A retry or repair requires a new task ID.
- The Harness must never publish its own next task or modify `.harness/task.json`.
- If autonomy is `HUMAN_REVIEW_REQUIRED`, do not execute automatically.

## Objective

[One precise objective.]

## Why this task now

[Which uncertainty, hypothesis, or gate this task addresses.]

## Read first

1. `PROJECT_STATE.md`
2. `CONTEXT_LEDGER.md`
3. `RESEARCH_TASK.md`
4. `AUTONOMY_POLICY.md`
5. Relevant source/code/report pointers listed below

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
- artifact paths;
- first failure/mismatch details when applicable.

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

Update `HARNESS_OUTBOX.md` using its schema. Commit relevant project code/reports/artifacts before exiting when running under the self-hosted workflow. The workflow will commit only communication-state files and then push committed work.

Do not silently broaden the research direction. If repository/source reality contradicts this task, document the contradiction in `HARNESS_OUTBOX.md` and stop or make only the minimum safe adaptation needed to collect evidence.
