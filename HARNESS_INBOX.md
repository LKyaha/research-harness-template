# HARNESS_INBOX

**Task ID:** [TASK-ID]  
**Issued:** [YYYY-MM-DD]  
**Project stage:** [STAGE]

This file is the current executable contract from ChatGPT/project lead to the local harness.

## Objective

[One precise objective.]

## Why this task now

[Which uncertainty, hypothesis, or gate this task addresses.]

## Read first

1. `PROJECT_STATE.md`
2. `CONTEXT_LEDGER.md`
3. `RESEARCH_TASK.md`
4. Relevant source/code/report pointers listed below

## Scope

### Do

- [ ] [Action]

### Do not

- [ ] [Explicitly excluded work]

## Required implementation / experiment

[Detailed instructions, inputs, controls, metrics, expected files.]

## Required evidence

Return enough evidence that another agent can independently verify the conclusion:

- exact commands;
- git commit/revision;
- environment/version information;
- configs;
- raw or summarized metrics;
- artifact paths;
- first failure/mismatch details when applicable.

## Gate

The task is complete only if one of the following is reported:

```text
[PASS_TOKEN]
```

or

```text
FAIL
BLOCKED
```

with evidence and explanation.

## Output contract

Update `HARNESS_OUTBOX.md` using its schema and push all relevant code/artifacts.

Do not silently broaden the research direction. If repository/source reality contradicts this task, document the contradiction in `HARNESS_OUTBOX.md` and stop or make only the minimum safe adaptation needed to collect evidence.
