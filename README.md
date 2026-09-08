# Research Harness Template

A reusable project template for long-running research, coding, and experimental work coordinated between ChatGPT and a local harness/agent.

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

## Start a new project

1. Create a repository from this template.
2. Replace all `[PROJECT ...]` placeholders.
3. Fill `PROJECT_STATE.md` and `RESEARCH_TASK.md`.
4. Give ChatGPT repository access and ask it to read `PROJECT_STATE.md`, `CONTEXT_LEDGER.md`, and `HARNESS_OUTBOX.md` before planning.
5. The next executable task goes into `HARNESS_INBOX.md`.
6. The local harness executes it, writes artifacts, updates `HARNESS_OUTBOX.md`, and pushes.
7. ChatGPT reviews the results and compresses durable conclusions back into canonical state.

## Canonical files

- `PROJECT_STATE.md` — current authoritative project snapshot.
- `CONTEXT_LEDGER.md` — goal → evidence → exclusions → decisions → unknowns → next experiment.
- `RESEARCH_TASK.md` — staged research plan and gates.
- `HYPOTHESES.md` — falsifiable hypotheses and status.
- `DECISIONS.md` — important decisions and rationale.
- `UNRESOLVED.md` — open questions.
- `FAILURES.md` — failed or ruled-out paths so they are not repeated.
- `HARNESS_INBOX.md` — ChatGPT → local harness task contract.
- `HARNESS_OUTBOX.md` — local harness → ChatGPT structured result.
- `docs/WORKFLOW.md` — operating protocol.
- `docs/CONTEXT_COMPRESSION.md` — rules for converting raw work into durable context.

## Prime directive

> Do not preserve everything. Preserve what remains decision-relevant.
