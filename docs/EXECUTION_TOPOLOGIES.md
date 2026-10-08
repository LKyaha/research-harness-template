# Optional Execution Topologies (Design Proposal)

**Status:** PROPOSED — documentation only; no runtime or schema changes in this PR.
**Baseline:** v0.2 on `main`; `.harness/task.json` schema version 1.
**Compatibility rule:** Single-Harness execution stays the default, fully supported path.

## Purpose

The template's invariant is **Task → Evidence → Review → Merge → State**. Recursive or multi-agent execution may be useful for independent, bounded work, but must be an *optional layer* over that invariant, not a replacement for the existing reviewed single-Harness loop.

A user who never enables this extension must see no new setup steps, workers, files, scheduling obligations, or behavioral changes. Complexity is paid only when the task warrants it.

## Topology vocabulary

| Topology | Meaning | Availability |
| --- | --- | --- |
| `DIRECT` | One bounded task executed by one Harness; the existing default. | Implemented in v0.2 (execution model; not a new machine field). |
| `PARALLEL` | Independent child tasks, with an explicit integration gate. | Proposed. |
| `HIERARCHICAL` | A parent delegates to bounded child workers and reviews/synthesizes their outputs. | Proposed. |
| `RECURSIVE` | Authorized child planners may create their own bounded descendants. | Proposed. |

These describe **execution organization**, not the existing `delivery_mode` (`DIRECT` versus `PULL_REQUEST`). A topology named `DIRECT` does **not** imply direct delivery to `main`: `PULL_REQUEST` remains the recommended delivery mode for reviewable code and research.

## Current transport constraint (do not pretend it is solved)

v0.2 has **one active READY slot** in `.harness/task.json`, **one consumed-ID ledger** in `.harness/completed.json`, and a single self-hosted dispatch job. Adding `parent_id` or `max_children` to that JSON does **not** create safe concurrent scheduling. In particular:

- The path-filtered push trigger is not a child-task queue.
- A single task claim cannot atomically reserve several child tasks.
- Multiple workers sharing a base branch can race on claims, branches, or protected state.
- A queued or offline self-hosted runner must not be mistaken for a successful execution.
- A parent PR cannot be considered scientifically accepted just because child PRs merged.

**Phase 1 is design only.** Do not add a `READY` task, modify the dispatcher, or claim parallelism is implemented until a separate reviewed scheduler/claim protocol and tests exist.

## Proposed optional task-tree contract

Keep `.harness/task.json` v1 unchanged for ordinary tasks. A future opt-in extension may maintain a separate, validated manifest (provisional path: `.harness/task_tree.json`) describing the *plan*, while dispatch continues to use existing one-shot semantics until an explicitly reviewed scheduler is implemented.

Illustrative (non-executable) manifest:

```json
{
  "schema_version": 1,
  "enabled": true,
  "root_task_id": "TASK-031",
  "topology": "PARALLEL",
  "limits": {
    "max_depth": 1,
    "max_children_per_parent": 3,
    "max_active_workers": 2,
    "max_total_tasks": 4,
    "max_wall_seconds": 7200,
    "max_gpu_hours": 0,
    "max_external_cost_usd": 0
  },
  "tasks": [
    {
      "task_id": "TASK-031",
      "parent_id": null,
      "depth": 0,
      "depends_on": [],
      "owner": "planner",
      "review_authority": "human-or-designated-reviewer",
      "merge_target": "main"
    },
    {
      "task_id": "TASK-031-A",
      "parent_id": "TASK-031",
      "depth": 1,
      "depends_on": [],
      "owner": "worker-a",
      "review_authority": "parent-reviewer",
      "merge_target": "integration/TASK-031"
    }
  ]
}
```

All names, paths, and fields in this example are **proposals**, not accepted machine API. `max_children_per_parent` limits direct fan-out; `max_total_tasks` and `max_active_workers` limit aggregate growth. Every resource limit is enforced against the *whole subtree*, not reset for each child. Unset material budgets mean no automatic spawning.

A future validated contract should require:

- Unique task IDs, exactly one root, existing parent references, acyclic `depends_on`, and `child.depth = parent.depth + 1`.
- Bounded depth, fan-out, active workers, total tasks, wall time, and cost/compute; no implicit unlimited defaults.
- Explicit task ownership and disjoint write scopes, or an integration owner for overlapping paths.
- A stable base revision and integration target for every child; stale-base detection before acceptance.
- An unambiguous review authority and no self-approval or self-merge.
- No secret material or raw private data in the manifest.

## Authority, lifecycle, and evidence

**Planning:** A parent may *propose* children, but may only *publish* a child task if its own authorization explicitly delegates that scope and the cumulative budget allows it. `HUMAN_REVIEW_REQUIRED` is never inherited as permission to execute. A child may not grant itself broader authority than its parent.

**Claim:** Each child needs its own globally unique, one-shot claim. Failure or timeout consumes the attempt; repair requires a new ID and an auditable parent link. A lease may prevent duplicate ownership but cannot replace the durable consumed-ID rule. Future scheduling must prove atomicity under concurrent claims and retries.

**Execution:** Each child returns code/config diffs, environment/revisions, commands, controls, compact results, provenance IDs, mismatches, and a clear PASS/FAIL/BLOCKED/PARTIAL gate. Child workers cannot alter protected dispatch state or publish siblings without authority.

**Review:** Local reviewers inspect child evidence and changes. A parent reviewer synthesizes *accepted* child evidence, records contradictions and integration failures, and prepares a parent-level PR/report. Acceptance requires its own integration tests and scientific validity check; passing child gates is not sufficient.

**Merge:** Children should ordinarily target an integration branch or staged PRs, not independently race to merge to `main`. Only the designated reviewer/integrator can approve parent-level promotion to canonical state. Conflicts and overlapping writes are escalated rather than auto-resolved by whichever worker finishes first.

**State:** Only reviewed, merged evidence changes `PROJECT_STATE.md`, `CONTEXT_LEDGER.md`, and related canonical files. Summaries must link back to exact child task IDs, PRs, commits, artifacts, and negative results; evidence compression must not erase contradictions.

## Failure and stop conditions

- Child FAIL/BLOCKED/PARTIAL: preserve evidence; the parent either reduces scope, requests a bounded repair with a new ID, or escalates.
- Budget exhausted, repeated failure, contradictory findings, unowned write conflicts, unknown provenance, or stale integration base: stop affected subtree and require review.
- Destructive operations, credential/permission changes, licensing/privacy/legal concerns, materially higher cost/compute, or changes to the scientific question: `HUMAN_REVIEW_REQUIRED`.
- A child cannot create an unbounded loop by recursively publishing its own descendants.

## Proposed incremental delivery

1. **Design review (this document):** Agree on vocabulary, invariants, boundaries, and backward-compatibility requirements. No execution behavior changes.
2. **Optional schema + validation:** Add a non-triggering manifest and stdlib validator tests. Existing v1 task files and default behavior must continue to pass unchanged.
3. **Single-process simulation:** Test DAG validation, budget aggregation, ownership conflicts, cancellation, failure propagation, and review/merge authority without dispatching extra agents.
4. **Bounded parallel scheduler:** Implement atomic child claims, task-specific workspaces/branches, crash recovery, and observability; prove race safety with integration tests.
5. **Hierarchical/recursive delegation:** Only after parallel scheduling is validated, enable explicit depth-limited delegation and evidence synthesis, behind opt-in policy.

## Acceptance criteria for any implementation PR

- No change to default single-Harness task publication, one-shot execution, or PR review semantics.
- Existing `.harness/task.json` v1 and tests remain valid.
- Opt-in topology is disabled by default and has deterministic rejection of invalid/budget-exceeding trees.
- No silent child auto-merge or automatic canonical-state promotion.
- Concurrency, stale dispatch, retry, crash recovery, and cost ceilings are tested before a real multi-worker dispatch is enabled.
- Offline runner is reported as a transport blocker, not a task result.

This proposal is intentionally smaller than a swarm implementation: it establishes a reviewable contract before adding concurrency.
