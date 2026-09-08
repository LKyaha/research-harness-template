# WORKFLOW

## Roles

### ChatGPT / project lead / reviewer

- Restores canonical state before planning.
- Converts goals into falsifiable tasks and stage gates.
- Reviews Harness evidence, code/config diffs, controls, provenance, and interpretation quality.
- Updates `PROJECT_STATE.md`, `CONTEXT_LEDGER.md`, `HYPOTHESES.md`, `DECISIONS.md`, `UNRESOLVED.md`, and `FAILURES.md` only when evidence warrants it.
- Writes the next executable contract to `HARNESS_INBOX.md`.
- Publishes the matching unique task ID to `.harness/task.json` only when execution is authorized.
- Chooses `AUTO_CONTINUE`, `AUTO_REPAIR`, or `HUMAN_REVIEW_REQUIRED` under `AUTONOMY_POLICY.md`.
- Chooses `DIRECT` or `PULL_REQUEST` delivery; prefer PR review for code/instrumentation/experiments and conclusion-changing evidence.

### Local Harness / research agent

- Reads the assigned task and referenced state.
- Executes code, tests, experiments, source inspection, and local environment work.
- Preserves failed runs and first mismatches.
- Reports reproducibility evidence in `HARNESS_OUTBOX.md`.
- Updates source/artifact provenance when needed.
- Does not silently redefine the project, promote guesses into canonical facts, merge its own review branch, publish the next task, or modify dispatch/consumption state.

### Human operator / PI

- Controls local hardware, accounts, credentials, budgets, and project priorities.
- Defines compute/cost/resource limits.
- May override decisions or redirect scope.
- Explicitly decides whether a project may use Level-3/4 autonomy or take high-impact/irreversible actions.

## Canonical reviewed loop

```text
1. Planner reads PROJECT_STATE + CONTEXT_LEDGER + latest reviewed evidence/open PRs
2. Planner reviews evidence and identifies the highest-value uncertainty
3. Canonical state is updated only for conclusions that survived review
4. Planner writes HARNESS_INBOX
5. Planner chooses autonomy + delivery mode
6. If authorized, planner publishes a new unique READY task_id
7. Dispatcher claims that task ID on the base branch before execution
8. For PULL_REQUEST delivery, dispatcher creates harness/<task_id>
9. Local Harness executes exactly that task once
10. Harness commits code/config/report/provenance evidence and updates HARNESS_OUTBOX
11. Workflow pushes the work branch and opens a PR when requested
12. Reviewer checks execution, controls, science, reproducibility, and provenance
13. Accepted evidence is merged; insufficient evidence gets REQUEST_CHANGES
14. Durable conclusions are compressed into canonical state
15. Only then may the planner publish another task ID
```

## Event-driven transport

Automatic local execution uses:

```text
.harness/task.json changed to READY on base branch
        ↓
GitHub Actions path-filtered push event
        ↓
self-hosted runner
        ↓
harness/worker.py
        ↓
claim task on latest base branch
        ↓
DIRECT: stay on base
PULL_REQUEST: create harness/<task_id>
        ↓
operator-configured HARNESS_COMMAND_JSON
```

Only `.harness/task.json` is the dispatch trigger path. `HARNESS_OUTBOX.md`, experiment reports, PR commits, canonical-state updates, claim commits, and worker-state commits do not launch another task.

## Task publication

`HARNESS_INBOX.md` and `.harness/task.json` must refer to the same new unique task ID and compatible delivery/autonomy settings.

Machine task fields include:

- `task_id` — globally unique within the project;
- `status` — `IDLE` or `READY`;
- `autonomy` — `AUTO_CONTINUE`, `AUTO_REPAIR`, or `HUMAN_REVIEW_REQUIRED`;
- `delivery_mode` — `DIRECT` or `PULL_REQUEST`;
- `base_branch` — required for PR delivery;
- `inbox_path` — normally `HARNESS_INBOX.md`.

## One-shot claim / idempotency

Before running the local Harness, `harness/worker.py`:

1. fetches the latest base branch;
2. verifies the task is still the latest READY intent;
3. checks the remote consumed-task ledger;
4. appends the task ID to `.harness/completed.json`;
5. commits and pushes that **claim** to the base branch;
6. only then begins local execution.

This makes a task one-shot even if an old GitHub Actions run is manually re-run. The claim push does not redispatch because the workflow is path-filtered to `.harness/task.json`.

A failed/timeout execution is still consumed. A retry requires a new task ID. This prevents silent infinite retries and makes failure history explicit.

## Pull-request delivery

For `PULL_REQUEST` tasks:

```text
claimed base
   ↓
harness/<task_id>
   ↓
Harness commits intentional changes/evidence
   ↓
harness/record_state.py commits communication state
   ↓
push work branch
   ↓
workflow opens PR automatically
```

The PR is the review queue. The reviewer should inspect:

- diff and implementation correctness;
- experiment definition and controls;
- `HARNESS_OUTBOX.md`;
- compact result files/reports;
- `provenance/sources.json` and `provenance/artifacts.json` changes;
- failures/contradictions;
- claimed impact on hypotheses/state.

See `docs/REVIEW_PROTOCOL.md`.

The Harness should fix normal review findings on the same PR. A **new task ID** is needed when the research question changes or a new execution is required after the original task attempt has been consumed.

## Harness command configuration

The self-hosted runner invokes an operator-provided JSON argv array through repository Actions variable `HARNESS_COMMAND_JSON`.

Example:

```json
["opencode", "run", "Read AGENTS.md and HARNESS_INBOX.md and execute task {task_id}. Do not modify .harness/task.json or .harness/completed.json."]
```

Supported placeholders:

```text
{task_id}
{inbox}
{repo}
```

Set `HARNESS_TIMEOUT_SECONDS` as another repository Actions variable. The worker defaults to 3600 seconds when absent.

Do not put credentials in command strings. Configure them on the self-hosted machine through each tool's normal secure mechanism.

## Commit behavior under the runner

The Harness must explicitly commit intentional project source/config/report/provenance changes before exit.

The workflow helper automatically stages only communication state:

```text
HARNESS_OUTBOX.md
.harness/last_worker_run.json
```

The consumed-task ledger is committed separately to the base branch **before** execution. The workflow deliberately never runs `git add -A`, reducing the chance of publishing model files, credentials, caches, datasets, or unrelated generated files.

## Provenance workflow

For important external dependencies:

```text
external repo/model/dataset/tool
→ provenance/sources.json (immutable revision when possible)
```

For large generated/downloaded artifacts:

```text
local/NAS/object store/model hub
→ provenance/artifacts.json (location + checksum + producer)
```

Git should contain enough compact evidence and generation instructions to interpret/recreate the result without becoming the storage backend for every raw byte.

See `docs/PROVENANCE.md` and `docs/RESEARCH_OBJECT_MODEL.md`.

## Startup protocol for a fresh ChatGPT thread

Read in this order:

1. `PROJECT_STATE.md`
2. `CONTEXT_LEDGER.md`
3. open Harness PRs / latest reviewed result
4. `HYPOTHESES.md`, `DECISIONS.md`, `FAILURES.md`, and `UNRESOLVED.md` when needed
5. raw reports/artifacts only when a claim requires verification

Do not reconstruct the project primarily from chat history if canonical repository state is available.

## Harness startup protocol

Read:

1. `HARNESS_INBOX.md`
2. `.harness/task.json` for task identity only; do not edit it
3. `PROJECT_STATE.md`
4. files explicitly referenced by the task
5. review/provenance docs when applicable

Do not scan the entire repository unless necessary.

## Stage gates

A stage gate prevents accidental progression based on superficial success. Prefer observable, binary gates where possible: exact reproduction, specified tests, causal controls, or a predeclared metric threshold.

A stage PASS does not automatically authorize the next experiment. The reviewer/planner must still accept the evidence and publish a new task ID.

## Human-review boundaries

Use `HUMAN_REVIEW_REQUIRED` for major scientific contradictions, research-direction changes, material cost/compute increases, destructive actions, licensing/legal/privacy issues, credentials/permissions issues, ambiguous high-impact findings, or repeated failure beyond budget.

See `AUTONOMY_POLICY.md`.

## Conflict resolution

Priority order:

```text
new direct evidence
> reviewed/merged evidence
> reviewed canonical state
> older reports
> tentative notes
> chat recollection
```

If evidence conflicts with canonical state, flag it; do not hide it or silently rewrite history.

## Commit discipline

Prefer commits that identify research transitions, for example:

- `stage0: reproduce baseline exactly`
- `experiment: add component ablation`
- `evidence: preserve first mismatch for EXP-012`
- `provenance: lock upstream source revision`
- `state: reject H3 after reviewed causal test`
- `harness: record TASK-004 result`

Keep large generated data outside Git when appropriate and record durable locations/checksums.
