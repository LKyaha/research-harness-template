# WORKFLOW

## Roles

### ChatGPT / project lead

- Reads canonical state before planning.
- Converts goals into falsifiable tasks and stage gates.
- Reviews Harness evidence.
- Updates `PROJECT_STATE.md`, `CONTEXT_LEDGER.md`, `HYPOTHESES.md`, `DECISIONS.md`, `UNRESOLVED.md`, and `FAILURES.md` as appropriate.
- Writes the next executable contract to `HARNESS_INBOX.md`.
- When execution is authorized, publishes the matching unique task ID to `.harness/task.json`.
- Decides whether the next step is `AUTO_CONTINUE`, `AUTO_REPAIR`, or `HUMAN_REVIEW_REQUIRED` under `AUTONOMY_POLICY.md`.

### Local Harness / agent

- Reads the assigned task and referenced state.
- Executes code, tests, experiments, source inspection, and local environment work.
- Preserves failed runs.
- Reports exact reproducibility evidence in `HARNESS_OUTBOX.md`.
- Does not silently redefine the project or promote guesses into canonical facts.
- Does not publish its own next task or modify `.harness/task.json`.

### Human operator

- Controls local hardware/accounts/secrets and project priorities.
- Defines compute/cost/resource limits.
- May override decisions or redirect scope.
- Explicitly decides whether a project may use Level-3/4 autonomy.

## Canonical research loop

```text
1. Planner reads PROJECT_STATE + CONTEXT_LEDGER + latest OUTBOX
2. Planner reviews evidence
3. Canonical state is updated
4. Planner writes HARNESS_INBOX
5. Planner decides AUTO_CONTINUE / AUTO_REPAIR / HUMAN_REVIEW_REQUIRED
6. If execution is authorized, planner publishes a new READY task_id
7. Local Harness executes exactly that task once
8. Harness commits evidence and updates HARNESS_OUTBOX
9. Repository receives result
10. Return to step 1
```

## Event-driven transport

Optional automatic local execution uses:

```text
.harness/task.json changed to READY
        ↓
GitHub Actions path-filtered push event
        ↓
self-hosted runner
        ↓
harness/worker.py
        ↓
operator-configured HARNESS_COMMAND_JSON
```

Only `.harness/task.json` is a trigger path. `HARNESS_OUTBOX.md`, experiment reports, code commits, and worker-state commits do not launch another task.

### Task publication

`HARNESS_INBOX.md` and `.harness/task.json` must refer to the same new unique task ID.

The machine task uses three autonomy decisions:

- `AUTO_CONTINUE` — execute a bounded, already-planned next step.
- `AUTO_REPAIR` — execute one bounded repair using a new task ID.
- `HUMAN_REVIEW_REQUIRED` — do not execute automatically.

### Idempotency

`.harness/completed.json` records consumed task IDs. `harness/worker.py` refuses to execute an already-consumed ID.

A task ID is consumed after one execution attempt, even when the local command fails or times out. A retry requires a new task ID. This prevents accidental infinite retries and makes failure history explicit.

The GitHub workflow also serializes runs with a repository-wide concurrency group.

### Harness command configuration

The self-hosted runner invokes an operator-provided JSON argv array through the repository Actions variable `HARNESS_COMMAND_JSON`.

Example value:

```json
["opencode", "run", "Read AGENTS.md and HARNESS_INBOX.md and execute task {task_id}. Do not modify .harness/task.json."]
```

Supported placeholders:

```text
{task_id}
{inbox}
{repo}
```

Set `HARNESS_TIMEOUT_SECONDS` as another repository Actions variable. The worker defaults to 3600 seconds when it is absent.

Do not put credentials in these command strings. Configure credentials on the self-hosted machine through the relevant tool's normal secure mechanism.

## Commit behavior under the runner

The Harness should commit intentional project source/report changes before it exits.

The workflow automatically stages only:

```text
HARNESS_OUTBOX.md
.harness/completed.json
.harness/last_worker_run.json
```

It deliberately does not run `git add -A`. This reduces the chance of accidentally committing local model files, credentials, caches, datasets, or unrelated generated files.

After recording communication state, the workflow pushes the current branch, including commits intentionally created by the Harness.

## Startup protocol for a fresh ChatGPT thread

Read in this order:

1. `PROJECT_STATE.md`
2. `CONTEXT_LEDGER.md`
3. `HARNESS_OUTBOX.md`
4. `HYPOTHESES.md` and `DECISIONS.md` when needed
5. raw reports/artifacts only when required to verify a claim

Do not reconstruct the project primarily from chat history if canonical repository state is available.

## Harness startup protocol

Read:

1. `HARNESS_INBOX.md`
2. `.harness/task.json` for task identity only; do not edit it
3. `PROJECT_STATE.md`
4. files explicitly referenced by the task

Do not scan the entire repository unless necessary.

## Stage gates

A stage gate prevents accidental progression based on superficial success. A gate should be observable and binary where possible, for example exact reproduction, a specified test suite, or a predeclared metric threshold.

A stage PASS does not automatically authorize the next experiment. The planner must still publish a new task ID.

## Human-review boundaries

Use `HUMAN_REVIEW_REQUIRED` when there is a major scientific contradiction, research-direction change, material cost/compute increase, destructive action, licensing/legal/privacy issue, credentials/permissions issue, or repeated failure beyond budget.

See `AUTONOMY_POLICY.md` for the full policy.

## Conflict resolution

Priority order:

```text
new direct evidence
> reviewed canonical state
> older reports
> tentative notes
> chat recollection
```

If evidence conflicts with canonical state, flag the conflict; do not hide it.

## Commit discipline

Prefer commits that describe research state transitions, for example:

- `stage0: reproduce baseline exactly`
- `experiment: add component ablation`
- `state: reject H3 after causal test`
- `harness: report TASK-004 results`

Keep large generated data outside Git when appropriate and record durable locations/checksums.
