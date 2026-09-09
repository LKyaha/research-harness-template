# RESEARCH OBJECT MODEL

The template treats a long-running research project as a graph of small, linked objects rather than one giant conversation.

## Core objects

### Project state
`PROJECT_STATE.md` — shortest authoritative snapshot of where the project is now.

### Context ledger
`CONTEXT_LEDGER.md` — compressed reasoning structure: goal, evidence, exclusions, decisions, unknowns, next experiment.

### Hypothesis
`HYPOTHESES.md` — falsifiable claim with status and supporting/contradicting evidence.

### Decision
`DECISIONS.md` — chosen direction plus rationale and evidence considered.

### Failure / exclusion
`FAILURES.md` — failed experiments, invalid methods, and ruled-out routes that should not be repeated accidentally.

### Task
`HARNESS_INBOX.md` + `.harness/task.json` — one bounded executable contract.

### Experiment
An experiment directory/report links a task to a question, controls, commands, result, and interpretation.

### Artifact
A generated object, local or remote, identified through `provenance/artifacts.json` when it should not live directly in Git.

### Source
An external dependency or evidence source identified through `provenance/sources.json`.

### Pull request
A reviewable evidence package that can include implementation, experiment definition, result summary, provenance changes, and state implications.

## Preferred links

Use stable IDs where possible:

```text
H-003                 hypothesis
TASK-012              task
EXP-012-A              experiment
ART-012-HIDDEN-DELTA   artifact
SRC-TRANSFORMERS       external source
D-007                  decision
```

A report should be able to say:

```text
TASK-012 tested H-003 using SRC-TRANSFORMERS@<sha>.
EXP-012-A produced ART-012-HIDDEN-DELTA.
PR #34 reviewed the implementation and evidence.
The result contradicted H-003 and caused D-007.
```

## Why this matters

This graph lets a future model restore the project from compact state and follow links to deeper evidence only when needed. The goal is not to make every file verbose; it is to make important claims traceable.

## Canonical-state rule

Neither an experiment, PR, Harness output, nor ChatGPT message automatically changes project truth. New evidence becomes durable project state only after review and compression into the canonical files.
