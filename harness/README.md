# Local Harness Dispatcher

This directory contains the optional bridge from a GitHub task publication to a local Harness process.

## What it does

`worker.py` consumes `.harness/task.json` only when:

- `status` is `READY`;
- autonomy is `AUTO_CONTINUE` or `AUTO_REPAIR`;
- the task ID is not already in `.harness/completed.json`.

It then invokes a local command configured by the operator.

It does **not** plan research, create the next task, or decide whether a failed hypothesis should be retried.

## Configure the self-hosted machine

1. Register a GitHub Actions self-hosted runner for the repository using GitHub's normal runner setup flow.
2. Install the local Harness you want to use (Codex, OpenCode, a custom CLI, etc.).
3. Authenticate that Harness locally using its normal secure mechanism. Do not commit credentials to this repository.
4. Create repository Actions variable `HARNESS_COMMAND_JSON`.
5. Optionally create repository Actions variable `HARNESS_TIMEOUT_SECONDS`.

Example `HARNESS_COMMAND_JSON`:

```json
["opencode", "run", "Read AGENTS.md and HARNESS_INBOX.md. Execute only task {task_id}. Update HARNESS_OUTBOX.md and commit intentional project changes. Do not edit .harness/task.json."]
```

The value is an argv array, not a shell string. Supported substitutions are:

- `{task_id}` — current task ID;
- `{inbox}` — inbox path from the machine task;
- `{repo}` — checked-out repository root.

## Dispatch a task

First write the full task to `HARNESS_INBOX.md`. Then publish the same unique ID in `.harness/task.json`:

```json
{
  "schema_version": 1,
  "task_id": "TASK-001",
  "status": "READY",
  "autonomy": "AUTO_CONTINUE",
  "depends_on": null,
  "issued_at": "2026-01-01T00:00:00Z",
  "failure_budget": 0,
  "inbox_path": "HARNESS_INBOX.md",
  "notes": "bounded first task"
}
```

Commit/push the task publication. The GitHub workflow watches `.harness/task.json` only.

## Why OUTBOX cannot loop

The workflow's path filter is:

```text
.harness/task.json
```

A Harness result normally changes:

```text
HARNESS_OUTBOX.md
.harness/completed.json
.harness/last_worker_run.json
project source/reports
```

Those changes do not match the trigger path, so result pushes do not start another Harness run.

The next execution requires a planner to publish a new task ID.

## Idempotency

After an execution attempt begins, the ID is recorded in `.harness/completed.json` when the worker finishes. The same ID will not execute again.

If an experiment or repair should be retried, publish a new task ID such as `TASK-001-R1`.

## Local test before enabling real work

Use a harmless command first, for example a small script/agent task that only:

1. reads `HARNESS_INBOX.md`;
2. writes the current task ID and `PASS` to `HARNESS_OUTBOX.md`;
3. exits successfully.

Then verify:

- the workflow ran once;
- the ID was added to `.harness/completed.json`;
- OUTBOX was pushed;
- the OUTBOX push did not start another run;
- a second workflow invocation with the same task ID is a no-op.

## Security notes

A self-hosted runner can execute code on your machine. Only enable this workflow in repositories and branches you trust. Define project resource limits in `AUTONOMY_POLICY.md`, keep credentials outside Git, and use `HUMAN_REVIEW_REQUIRED` for destructive, expensive, permission-sensitive, or legally sensitive actions.
