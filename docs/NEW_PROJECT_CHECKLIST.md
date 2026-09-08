# NEW PROJECT CHECKLIST

Use this after creating a repository from the template.

## Bootstrap

- [ ] Rename/project description updated.
- [ ] Replace `[PROJECT NAME]`, `[TASK-ID]`, `[SET_ME]`, and other placeholders.
- [ ] Replace/delete example entries in `provenance/sources.json` and `provenance/artifacts.json`.
- [ ] Fill `PROJECT_STATE.md` objective, current stage, and next action.
- [ ] Fill `RESEARCH_TASK.md` with stages and explicit gates.
- [ ] Create initial falsifiable hypotheses in `HYPOTHESES.md`.
- [ ] Record already-known exclusions/decisions.
- [ ] Register important external repositories/models/datasets/tools with immutable revisions when practical.
- [ ] Review `AUTONOMY_POLICY.md` and set compute/cost/failure limits.
- [ ] Choose default delivery policy; `PULL_REQUEST` is recommended for research/code work.
- [ ] Write first executable task to `HARNESS_INBOX.md`.
- [ ] Confirm the local Harness reads `AGENTS.md` or explicitly point it there.
- [ ] Run `python harness/validate_repository.py`.

## Optional event-driven execution

Only enable this if you intentionally want GitHub to start the local Harness when a planner publishes a task.

- [ ] Register a GitHub Actions self-hosted runner for the project/repository.
- [ ] Confirm the runner is on the intended trusted machine.
- [ ] Install/authenticate the local Harness using its normal secure mechanism.
- [ ] Set repository Actions variable `HARNESS_COMMAND_JSON` to a JSON argv array.
- [ ] Set repository Actions variable `HARNESS_TIMEOUT_SECONDS`.
- [ ] Confirm material resource limits are no longer `[SET_ME]`.
- [ ] Leave `.harness/task.json` at `status: IDLE` until intentional dispatch.
- [ ] Confirm `.harness/completed.json` contains no real project task IDs yet.
- [ ] Test with a harmless first task.
- [ ] Verify the claim is written to the base branch before local execution.
- [ ] Verify OUTBOX/PR/result pushes do **not** trigger another Harness run.
- [ ] Verify re-running the same task ID does **not** execute it again.
- [ ] If using PR delivery, verify `harness/<task_id>` is opened automatically as a PR.
- [ ] Record any decision to use Level-3 or Level-4 autonomy in `DECISIONS.md`.

## Publishing a task

1. Write/update `HARNESS_INBOX.md` with a unique task ID, bounded instructions, resource limits, and delivery mode.
2. Decide `AUTO_CONTINUE`, `AUTO_REPAIR`, or `HUMAN_REVIEW_REQUIRED`.
3. Choose `DIRECT` or `PULL_REQUEST`; prefer PR for code/instrumentation/experiments.
4. If automatic execution is authorized, update `.harness/task.json` with the same task ID, `status: READY`, autonomy, delivery mode, and base branch.
5. Commit/push both changes.
6. The path-filtered workflow should claim and dispatch the task once.

A repair/retry always uses a new task ID.

## First ChatGPT instruction

A useful first instruction is:

> Treat this repository as the project's durable external working memory and provenance graph. Restore state from `PROJECT_STATE.md` and `CONTEXT_LEDGER.md`, then inspect open Harness PRs/latest reviewed evidence before making decisions. Review evidence using `docs/REVIEW_PROTOCOL.md`, update canonical state only when warranted, and publish the next bounded task through `HARNESS_INBOX.md` + `.harness/task.json` under `AUTONOMY_POLICY.md`.

## First Harness instruction

A useful first instruction is:

> Read `AGENTS.md` and execute the current `HARNESS_INBOX.md`. Preserve exact reproducibility evidence, update `HARNESS_OUTBOX.md`, commit intended code/reports/provenance on the assigned work branch, and do not modify dispatch/consumption state, merge your own PR, invent the next task, or advance past the declared gate unless instructed.

## Template hygiene

Keep the file structure, task-ID semantics, provenance IDs, and status vocabulary stable when possible. Delete placeholder examples only after replacing them. The goal is that a future model can restore project state quickly and follow links to deeper evidence only when necessary.
