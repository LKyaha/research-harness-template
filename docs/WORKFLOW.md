# WORKFLOW

## Roles

### ChatGPT / project lead

- Reads canonical state before planning.
- Converts goals into falsifiable tasks and stage gates.
- Reviews Harness evidence.
- Updates `PROJECT_STATE.md`, `CONTEXT_LEDGER.md`, `HYPOTHESES.md`, `DECISIONS.md`, `UNRESOLVED.md`, and `FAILURES.md` as appropriate.
- Writes the next executable contract to `HARNESS_INBOX.md`.

### Local Harness / agent

- Reads the assigned task and referenced state.
- Executes code, tests, experiments, source inspection, and local environment work.
- Preserves failed runs.
- Reports exact reproducibility evidence in `HARNESS_OUTBOX.md`.
- Does not silently redefine the project or promote guesses into canonical facts.

### Human operator

- Controls local hardware/accounts/secrets and project priorities.
- May override decisions or redirect scope.
- Connects the ChatGPT and Harness loops when automatic integration is unavailable.

## Normal loop

```text
1. ChatGPT reads PROJECT_STATE + CONTEXT_LEDGER + latest OUTBOX
2. ChatGPT reviews evidence
3. Canonical state is updated
4. ChatGPT writes HARNESS_INBOX
5. Harness pulls repository
6. Harness executes only current task
7. Harness commits artifacts and updates HARNESS_OUTBOX
8. Harness pushes
9. Repeat
```

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
2. `PROJECT_STATE.md`
3. files explicitly referenced by the task

Do not scan the entire repository unless necessary.

## Stage gates

A stage gate prevents accidental progression based on superficial success. A gate should be observable and binary where possible, for example exact reproduction, a specified test suite, or a predeclared metric threshold.

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
