# NEW PROJECT CHECKLIST

Use this after creating a repository from the template.

## Bootstrap

- [ ] Rename/project description updated.
- [ ] Replace `[PROJECT NAME]`, `[SET_ME]`, and other placeholders.
- [ ] Fill `PROJECT_STATE.md` objective, current stage, and next action.
- [ ] Fill `RESEARCH_TASK.md` with stages and explicit gates.
- [ ] Create initial falsifiable hypotheses in `HYPOTHESES.md`.
- [ ] Record any already-known exclusions/decisions.
- [ ] Review `AUTONOMY_POLICY.md` and set compute/cost/failure limits.
- [ ] Write first executable task to `HARNESS_INBOX.md`.
- [ ] Confirm local Harness reads `AGENTS.md` or explicitly point it there.

## Optional event-driven execution

Only enable this if you intentionally want GitHub to start the local Harness when a planner publishes a task.

- [ ] Register a GitHub Actions self-hosted runner for the project/repository.
- [ ] Confirm the runner is on the intended trusted machine.
- [ ] Install and authenticate the local Harness/agent on that machine using its normal secure mechanism.
- [ ] Set repository Actions variable `HARNESS_COMMAND_JSON` to a JSON argv array.
- [ ] Set repository Actions variable `HARNESS_TIMEOUT_SECONDS`.
- [ ] Confirm project resource limits are no longer `[SET_ME]` for any resource the Harness may materially consume.
- [ ] Leave `.harness/task.json` at `status: IDLE` until the first intentional dispatch.
- [ ] Confirm `.harness/completed.json` contains no project task IDs yet.
- [ ] Test with a harmless first task that only reads the repository and writes a small OUTBOX result.
- [ ] Verify that changing `HARNESS_OUTBOX.md` alone does **not** trigger another workflow.
- [ ] Verify that re-publishing the same task ID does **not** execute it again.
- [ ] Record any decision to use Level-3 or Level-4 autonomy in `DECISIONS.md`.

## Publishing a task

1. Write/update `HARNESS_INBOX.md` with a unique task ID and bounded instructions.
2. Decide `AUTO_CONTINUE`, `AUTO_REPAIR`, or `HUMAN_REVIEW_REQUIRED`.
3. If automatic execution is authorized, update `.harness/task.json` with the same task ID, `status: READY`, and the selected autonomy decision.
4. Commit/push both changes.
5. The path-filtered workflow should dispatch the task once on the self-hosted runner.

A repair/retry always uses a new task ID.

## First ChatGPT instruction

A useful first instruction is:

> Treat this repository as the project's durable external working memory. Read `PROJECT_STATE.md`, `CONTEXT_LEDGER.md`, and the latest `HARNESS_OUTBOX.md` before making project decisions. Review evidence, update canonical state when warranted, and place the next bounded executable task in `HARNESS_INBOX.md`. Follow `AUTONOMY_POLICY.md`; only publish `.harness/task.json` as `READY` when automatic execution is authorized.

## First Harness instruction

A useful first instruction is:

> Read `AGENTS.md` and execute the current `HARNESS_INBOX.md`. Preserve exact reproducibility evidence, update `HARNESS_OUTBOX.md`, and commit relevant artifacts. Do not modify `.harness/task.json`, invent the next task, or advance past the declared gate unless instructed.

## Template hygiene

Delete placeholder examples only after replacing them with project-specific content. Keep the file structure, task-ID semantics, and status vocabulary stable when possible so future agents can resume quickly.
