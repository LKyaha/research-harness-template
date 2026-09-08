# Research Harness Template

A reusable project template for long-running research, coding, and experimental work coordinated between a human operator, ChatGPT/project planner-reviewer, and a local Harness/agent.

## Core idea

Chat history is not project state. Raw logs are not project state. The repository is the durable external working memory **and provenance graph**.

```text
raw evidence / code / logs / experiments
        ↓
structured evidence + provenance
        ↓
reviewable PR / report
        ↓
HYPOTHESES + DECISIONS + FAILURES + UNRESOLVED
        ↓
CONTEXT_LEDGER
        ↓
PROJECT_STATE
```

`PROJECT_STATE.md` is the shortest authoritative snapshot. `CONTEXT_LEDGER.md` preserves the decision-relevant reasoning structure behind it. Git history, PRs, experiment reports, source revisions, and artifact manifests let future agents drill back into evidence only when needed.

## Research-team model

A useful mental model is:

- **Human operator / PI** — priorities, resource limits, irreversible/high-impact decisions.
- **ChatGPT / planner-reviewer** — restores canonical context, evaluates evidence, reviews PRs, updates hypotheses/decisions/state, publishes the next bounded task.
- **Local Harness / research engineer** — inspects source, writes code, runs tests/experiments, preserves failures, and submits reproducible evidence.
- **GitHub** — durable working memory, source control, review queue, provenance index, and event transport.

## Event-driven reviewed loop

The recommended path for code and research experiments is `PULL_REQUEST` delivery:

```text
Planner / ChatGPT
      ↓
HARNESS_INBOX.md              human-readable task
.harness/task.json            one-shot READY trigger
      ↓
GitHub push event
      ↓
self-hosted runner
      ↓
harness/worker.py
      ↓
claim task ID on base branch
      ↓
create harness/<task_id>
      ↓
local Harness executes once
      ↓
code + configs + reports + provenance + HARNESS_OUTBOX
      ↓
workflow pushes work branch
      ↓
automatic Pull Request
      ↓
ChatGPT / human scientific review
      ↓
merge accepted evidence
      ↓
compress durable findings into canonical state
      ↓
publish a new task ID
```

The key invariant is **one task ID, at most one execution attempt**. A result, PR, OUTBOX update, or normal code commit cannot launch the next task by itself.

## Review is more than code review

`docs/REVIEW_PROTOCOL.md` requires reviewers to check:

1. execution integrity;
2. instrumentation and controls;
3. scientific validity;
4. reproducibility;
5. source/artifact provenance;
6. justified impact on hypotheses and canonical state.

A clean diff is not enough if the evidence does not support the claim.

## Provenance without turning Git into object storage

Use:

- `provenance/sources.json` for important external repositories, models, datasets, papers, tools, and immutable revisions;
- `provenance/artifacts.json` for model weights, tensor dumps, large benchmark outputs, datasets, traces, or other artifacts stored outside Git.

Keep compact evidence, configs, metrics, reports, and generation scripts in Git when practical. Keep huge blobs elsewhere and record durable location/checksum/reproduction information.

## Start a new project

1. Create a repository from this template.
2. Replace `[PROJECT ...]`, `[TASK-ID]`, example provenance entries, and `[SET_ME]` placeholders.
3. Fill `PROJECT_STATE.md` and `RESEARCH_TASK.md`.
4. Create initial falsifiable entries in `HYPOTHESES.md`.
5. Review `AUTONOMY_POLICY.md` and define resource/cost limits.
6. Configure important upstream sources in `provenance/sources.json`.
7. Give ChatGPT repository access and ask it to restore state from canonical files before planning.
8. Put the next executable task in `HARNESS_INBOX.md`.
9. For event-driven execution, configure a self-hosted runner and `HARNESS_COMMAND_JSON`, then publish the matching unique ID in `.harness/task.json` with `status: READY`.
10. Prefer `delivery_mode: PULL_REQUEST` for code, instrumentation, experiments, or evidence that may change conclusions.
11. Review/merge the evidence package, then compress durable findings back into canonical state before publishing another task.

## Core files

### Canonical state

- `PROJECT_STATE.md` — current authoritative snapshot.
- `CONTEXT_LEDGER.md` — goal → evidence → exclusions → decisions → unknowns → next experiment.
- `RESEARCH_TASK.md` — staged research plan and gates.
- `HYPOTHESES.md` — falsifiable hypotheses and status.
- `DECISIONS.md` — important decisions and rationale.
- `UNRESOLVED.md` — open questions.
- `FAILURES.md` — failed/invalid/ruled-out paths.

### Planner ↔ Harness

- `HARNESS_INBOX.md` — bounded executable contract.
- `HARNESS_OUTBOX.md` — structured evidence/result package.
- `AUTONOMY_POLICY.md` — continuation, repair, human-review, and resource boundaries.
- `.harness/task.json` — machine-readable one-shot dispatch trigger.
- `.harness/completed.json` — consumed task-ID ledger.

### Review / provenance

- `docs/REVIEW_PROTOCOL.md` — scientific/code review policy.
- `docs/PROVENANCE.md` — source and artifact traceability.
- `docs/RESEARCH_OBJECT_MODEL.md` — links hypotheses, tasks, experiments, artifacts, PRs, and decisions.
- `provenance/sources.json` — external source registry.
- `provenance/artifacts.json` — large/external artifact registry.
- `.github/pull_request_template.md` — evidence-oriented PR template.

### Automation

- `harness/worker.py` — one-shot claim + local dispatcher + optional PR work branch.
- `harness/record_state.py` — safely records/pushes communication state.
- `harness/validate_repository.py` — stdlib-only state/provenance contract validator.
- `.github/workflows/harness-dispatch.yml` — optional self-hosted execution and PR opening.
- `.github/workflows/research-state-check.yml` — validation on PRs and `main`.

## Safety properties

- Only `.harness/task.json` changes on the configured base branch trigger automatic local execution.
- A task is claimed on the base branch before local execution; workflow re-runs cannot silently replay it.
- OUTBOX/result/PR commits do not trigger another task.
- Retries require a new task ID.
- `HUMAN_REVIEW_REQUIRED` never auto-dispatches.
- The Harness cannot publish its own next task and protected trigger/ledger mutations are rejected/reverted.
- `PULL_REQUEST` delivery prevents normal research/code work from being silently pushed straight into canonical `main`.
- The workflow never runs `git add -A`; arbitrary local files are not automatically staged.
- Large artifacts belong in external storage with provenance, not blindly in Git.
- Resource/cost limits must be defined before high-cost autonomy is enabled.

## Prime directive

> Do not preserve everything. Preserve what remains decision-relevant — and preserve enough provenance to prove where it came from.
