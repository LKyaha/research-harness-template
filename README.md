# Research Harness Template

A reusable project template for long-running research, coding, and experimental work coordinated between ChatGPT and a local Harness/agent.

## Core idea

Chat history is not project state. Raw logs are not project state. The repository is the durable external working memory.

Canonical state flows as:

```text
raw evidence / code / logs / experiments
        ↓
structured findings
        ↓
HYPOTHESES + DECISIONS + FAILURES
        ↓
CONTEXT_LEDGER
        ↓
PROJECT_STATE
```

`PROJECT_STATE.md` is the shortest authoritative snapshot. `CONTEXT_LEDGER.md` preserves the reasoning structure behind it.

## Optional event-driven local execution

The template also includes an optional GitHub Actions + self-hosted runner transport:

```text
Planner / ChatGPT
      ↓
HARNESS_INBOX.md              human-readable task
.harness/task.json            machine READY trigger
      ↓
GitHub push event
      ↓
self-hosted GitHub runner
      ↓
harness/worker.py
      ↓
local Harness / Codex / OpenCode / custom agent
      ↓
HARNESS_OUTBOX.md + committed evidence
      ↓
GitHub
      ↓
Planner reviews and publishes a new task ID
```

The important invariant is **one task ID, at most one execution**. A Harness result or OUTBOX push cannot trigger the next round by itself.

The template defaults to conservative Level-2 autonomy. See `AUTONOMY_POLICY.md` before enabling automatic local execution.

## Start a new project

1. Create a repository from this template.
2. Replace all `[PROJECT ...]` / `[SET_ME]` placeholders.
3. Fill `PROJECT_STATE.md` and `RESEARCH_TASK.md`.
4. Review `AUTONOMY_POLICY.md` and define resource limits.
5. Give ChatGPT repository access and ask it to read `PROJECT_STATE.md`, `CONTEXT_LEDGER.md`, and `HARNESS_OUTBOX.md` before planning.
6. The next executable task goes into `HARNESS_INBOX.md`.
7. For manual Harness operation, execute that task directly.
8. For event-driven execution, configure a self-hosted runner and `HARNESS_COMMAND_JSON`, then publish the matching unique ID in `.harness/task.json` with `status: READY`.
9. The Harness executes, writes evidence, updates `HARNESS_OUTBOX.md`, and commits relevant work.
10. ChatGPT reviews the results and compresses durable conclusions back into canonical state before publishing a new task.

## Canonical files

- `PROJECT_STATE.md` — current authoritative project snapshot.
- `CONTEXT_LEDGER.md` — goal → evidence → exclusions → decisions → unknowns → next experiment.
- `RESEARCH_TASK.md` — staged research plan and gates.
- `HYPOTHESES.md` — falsifiable hypotheses and status.
- `DECISIONS.md` — important decisions and rationale.
- `UNRESOLVED.md` — open questions.
- `FAILURES.md` — failed or ruled-out paths so they are not repeated.
- `HARNESS_INBOX.md` — planner → local Harness task contract.
- `HARNESS_OUTBOX.md` — local Harness → planner structured result.
- `AUTONOMY_POLICY.md` — continuation, repair, human-review, and resource boundaries.
- `.harness/task.json` — machine-readable one-shot dispatch trigger.
- `.harness/completed.json` — consumed task-ID ledger.
- `harness/worker.py` — idempotent local dispatcher.
- `.github/workflows/harness-dispatch.yml` — optional self-hosted event transport.
- `docs/WORKFLOW.md` — operating protocol.
- `docs/CONTEXT_COMPRESSION.md` — rules for converting raw work into durable context.

## Safety properties of the dispatch design

- Only `.harness/task.json` changes trigger automatic local execution.
- OUTBOX/result commits do not trigger another run.
- A task ID is consumed after one execution attempt; retries need a new ID.
- `HUMAN_REVIEW_REQUIRED` never auto-dispatches.
- The local Harness is forbidden from publishing its own next task.
- The workflow does not run `git add -A`; arbitrary local files are not automatically staged.
- Resource/cost limits are project-defined and should be set before enabling automation.

## Prime directive

> Do not preserve everything. Preserve what remains decision-relevant.
