# DISPATCH INVARIANTS

This document states the safety/reproducibility properties the event-driven dispatcher is trying to preserve.

## 1. A task is an immutable execution intent

A task is defined by the Git commit that publishes:

- `.harness/task.json`;
- the referenced `HARNESS_INBOX.md` content;
- the repository/code state visible in that commit.

Before execution, the worker verifies that the base branch still points at the triggering `GITHUB_SHA`. If the base branch moved after publication, the task is considered stale and must be republished with a new task ID against the new state.

This prevents an experiment planned against one code revision from silently executing against another.

## 2. One task ID, at most one execution attempt

Before the local Harness is launched, the dispatcher appends the task ID to `.harness/completed.json`, commits the claim, and pushes it to the base branch.

A workflow re-run checks the remote ledger first. If the ID is already present, execution is a no-op.

Failures/timeouts after claim remain consumed. A new execution requires a new task ID.

## 3. Infrastructure preflight happens before claim

Invalid/missing `HARNESS_COMMAND_JSON`, invalid timeout configuration, unsafe task paths, and invalid task schema are rejected before claiming execution when possible.

The intent is to distinguish “runner is misconfigured” from “the scientific task attempted and failed.”

## 4. Task-controlled paths cannot escape the repository

`inbox_path` must be a relative path whose resolved target remains inside the repository root. Absolute paths and `..` escapes are rejected.

Base branch names are deliberately restricted to a conservative ASCII subset suitable for cross-platform automation.

## 5. Reviewable work does not go directly to canonical code state

For `PULL_REQUEST` delivery:

```text
base + task claim
→ harness/<task_id>
→ Harness work/evidence
→ push branch
→ PR review
→ merge only after review
```

The Harness does not merge its own PR.

## 6. Dispatcher state is protected from the Harness

The Harness is forbidden from changing:

- `.harness/task.json`;
- `.harness/completed.json`.

The worker restores these files after execution, and `record_state.py` stages the restored versions so even a mutation committed by the Harness cannot survive in the final PR diff.

## 7. Results cannot self-trigger the next task

The execution workflow listens only for changes to `.harness/task.json` on the configured base branch.

Changes to OUTBOX, reports, code, provenance, PR branches, claim commits, or worker state do not dispatch another task.

Only the planner can publish a new unique READY task.

## 8. Git is the provenance/index layer, not mandatory bulk storage

Large artifacts may live on local/NAS/object/model storage, but significant artifacts and external sources should be registered with stable identifiers, revisions, and checksums where practical.

## Current v0.2 operational constraints

### Base-branch claim write

The one-shot ledger is currently persisted by a small bot commit to the base branch before execution. Therefore the self-hosted workflow needs permission to push that claim commit.

If a project enforces a branch policy that forbids **all** direct automation writes to the base branch, either:

1. grant the research Harness workflow a narrowly scoped exception for claim-state commits; or
2. adapt the dispatcher to store claims on a dedicated state branch/external transactional store.

A dedicated state branch is a reasonable future template enhancement; v0.2 intentionally keeps the mechanism simple and auditable.

### Automatic PR creation

The workflow requires `pull-requests: write` and repository settings that allow GitHub Actions to create pull requests. If automatic PR creation is disabled by repository policy, the work branch can still be pushed and a human/planner can open the PR manually.

### Self-hosted runner trust

A self-hosted runner executes local commands with the runner account's OS permissions. Treat runner registration, repository write access, and local credentials as security boundaries. Do not enable automatic execution for repositories/branches you do not trust.
