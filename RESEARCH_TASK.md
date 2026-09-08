# RESEARCH_TASK

**Project:** [PROJECT NAME]

## 1. Research Objective

[What are we trying to discover/build, and why?]

## 2. Non-Goals

- [What this project is explicitly not trying to do.]

## 3. Known Facts

- [Fact with evidence pointer.]

## 4. Research Questions

1. [Question]
2. [Question]

## 5. Stages

### Stage 0 — Ground Truth / Reproduction

**Goal:** [Establish exact baseline or reproduce key mechanism.]

**Tasks:**
- [ ] [Task]

**Artifacts:**
- [Expected files/results]

**Gate:**

```text
[STAGE0_PASS_TOKEN]
```

Do not advance unless the gate is satisfied or this document is explicitly revised.

---

### Stage 1 — Mechanism / Causal Analysis

**Goal:** [Understand why/how it works.]

**Tasks:**
- [ ] [Task]

**Gate:**

```text
[STAGE1_PASS_TOKEN]
```

---

### Stage 2 — Prototype

**Goal:** [Build smallest mechanism-valid prototype.]

**Tasks:**
- [ ] [Task]

**Gate:**

```text
[STAGE2_PASS_TOKEN]
```

---

### Stage 3 — Transfer / Scaling / Integration

**Goal:** [Cross-system transfer, scaling, or production integration.]

**Tasks:**
- [ ] [Task]

**Gate:**

```text
[STAGE3_PASS_TOKEN]
```

## 6. Experimental Discipline

Every meaningful experiment should state:
- question;
- hypothesis;
- independent variable;
- controls;
- metric;
- pass/fail interpretation;
- artifact location;
- environment/commit/config.

A failed experiment is still an artifact and must not be silently deleted.

## 7. Stop Conditions

Pause and revise the plan if:
- source/code reality contradicts the task assumptions;
- the current metric cannot distinguish competing hypotheses;
- resource cost grows before mechanism validity is established;
- repeated failures share an unexplained cause.
