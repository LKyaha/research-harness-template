# NEW PROJECT CHECKLIST

Use this after creating a repository from the template.

## Bootstrap

- [ ] Rename/project description updated.
- [ ] Replace `[PROJECT NAME]` and other placeholders.
- [ ] Fill `PROJECT_STATE.md` objective, current stage, and next action.
- [ ] Fill `RESEARCH_TASK.md` with stages and explicit gates.
- [ ] Create initial falsifiable hypotheses in `HYPOTHESES.md`.
- [ ] Record any already-known exclusions/decisions.
- [ ] Write first executable task to `HARNESS_INBOX.md`.
- [ ] Confirm local harness reads `AGENTS.md` or explicitly point it there.

## First ChatGPT instruction

A useful first instruction is:

> Treat this repository as the project's durable external working memory. Read `PROJECT_STATE.md`, `CONTEXT_LEDGER.md`, and the latest `HARNESS_OUTBOX.md` before making project decisions. Review evidence, update canonical state when warranted, and place the next bounded executable task in `HARNESS_INBOX.md`.

## First Harness instruction

A useful first instruction is:

> Read `AGENTS.md` and execute the current `HARNESS_INBOX.md`. Preserve exact reproducibility evidence, update `HARNESS_OUTBOX.md`, commit relevant artifacts, and push. Do not advance past the declared gate unless instructed.

## Template hygiene

Delete placeholder examples only after replacing them with project-specific content. Keep the file structure and status vocabulary stable when possible so future agents can resume quickly.
