# Local Harness Dispatcher

This directory contains the optional bridge from a GitHub task publication to a local Harness process.

## What it does

`worker.py` consumes `.harness/task.json` only when:

- `status` is `READY`;
- autonomy is `AUTO_CONTINUE` or `AUTO_REPAIR`;
- the task ID has not already been consumed.

Before local execution, the worker fetches the latest base branch, verifies the task is still current, records the task ID in `.harness/completed.json`, commits/pushes that **claim**, and only then starts the local Harness.

For `PULL_REQUEST` delivery it creates:

```text
harness/<task_id>
```

and executes the Harness there. `record_state.py` pushes that work branch, and the workflow opens a PR automatically.

The dispatcher does **not** plan research, invent the next task, decide whether a hypothesis should be retried, or approve/merge results.

## Configure the self-hosted machine

1. Register a GitHub Actions self-hosted runner for the repository using GitHub's normal runner setup flow.
2. Install the local Harness you want to use (Codex, OpenCode, a custom CLI, etc.).
3. Authenticate that Harness locally using its normal secure mechanism. Do not commit credentials to the repository.
4. Create repository Actions variable `HARNESS_COMMAND_JSON`.
5. Optionally create repository Actions variable `HARNESS_TIMEOUT_SECONDS`.
6. Set project compute/cost boundaries in `AUTONOMY_POLICY.md` before expensive automatic execution.

Example `HARNESS_COMMAND_JSON`:

```json
["opencode", "run", "Read AGENTS.md and HARNESS_INBOX.md. Execute only task {task_id}. Update HARNESS_OUTBOX.md and commit intentional evidence. Do not edit .harness/task.json or .harness/completed.json."]
```

The value is an argv array, not a shell string. Supported substitutions are:

- `{task_id}` — current task ID;
- `{inbox}` — inbox path from the machine task;
- `{repo}` — checked-out repository root.

During execution the worker also exports:

- `HARNESS_TASK_ID`
- `HARNESS_INBOX_PATH`
- `HARNESS_AUTONOMY`
- `HARNESS_DELIVERY_MODE`
- `HARNESS_BASE_BRANCH`
- `HARNESS_WORK_BRANCH`

## Dispatch a task

First write the full task to `HARNESS_INBOX.md`. Then publish the same unique ID in `.harness/task.json`, for example:

```json
{
  "schema_version": 1,
  "task_id": "TASK-001",
  "status": "READY",
  "autonomy": "AUTO_CONTINUE",
  "delivery_mode": "PULL_REQUEST",
  "base_branch": "main",
  "depends_on": null,
  "issued_at": "2026-01-01T00:00:00Z",
  "failure_budget": 0,
  "inbox_path": "HARNESS_INBOX.md",
  "notes": "bounded first task"
}
```

Commit/push the task publication. The GitHub workflow watches `.harness/task.json` on the base branch.

## One-shot claim

The important order is:

```text
READY task
→ fetch latest base
→ verify intent still current
→ check remote completed ledger
→ commit/push task claim to base
→ execute locally
```

This prevents a manual re-run of an old GitHub Actions workflow from replaying the same task. An execution attempt remains consumed even when the local command fails or times out. A repair/retry uses a new ID such as `TASK-001-R1`.

## Why result pushes cannot loop

The workflow trigger path is only:

```text
.harness/task.json
```

Claims, OUTBOX changes, code/report commits, provenance changes, PR branches, and worker-state commits do not match that path, so they cannot launch the next task.

The next execution requires a planner to publish a **new** task ID.

## Pull-request delivery

`PULL_REQUEST` is recommended for code, instrumentation, experiments, and conclusion-changing evidence.

The Harness should:

1. stay on `HARNESS_WORK_BRANCH`;
2. commit intentional code/config/report/provenance changes;
3. update `HARNESS_OUTBOX.md`;
4. exit without merging or publishing another task.

The workflow then:

1. safely records communication state;
2. pushes the work branch;
3. opens a PR targeting `base_branch`;
4. creates it as draft when the Harness exits non-zero.

Review follows `docs/REVIEW_PROTOCOL.md`.

## Large data / provenance

Do not use Git as storage for large model weights, tensor dumps, datasets, traces, or arbitrary caches. Register important external sources in `provenance/sources.json` and large/external artifacts in `provenance/artifacts.json`, including immutable revision/checksum when practical.

## Local test before enabling real work

Use a harmless first task that only:

1. reads `HARNESS_INBOX.md`;
2. writes the current task ID and `PASS` to `HARNESS_OUTBOX.md`;
3. optionally commits one tiny test file;
4. exits successfully.

Prefer `PULL_REQUEST` delivery for this smoke test. Verify:

- the task claim was committed to the base branch before execution;
- the Harness ran once;
- a `harness/<task_id>` branch was pushed;
- a PR was opened automatically;
- the PR contains the OUTBOX/result;
- OUTBOX/PR pushes did not start another run;
- re-running the same workflow/task ID is a no-op or stale/consumed dispatch rather than a second execution;
- `python harness/validate_repository.py` passes.

## Security notes

A self-hosted runner can execute code on your machine. Only enable this workflow in repositories/branches you trust. Keep credentials outside Git, restrict runner permissions, set resource limits, and use `HUMAN_REVIEW_REQUIRED` for destructive, expensive, permission-sensitive, privacy-sensitive, or legally sensitive actions.
