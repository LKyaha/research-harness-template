# PROVENANCE

The repository is the durable index of research evidence, but it is not required to store every byte of evidence.

## Principle

Every result that may influence a scientific conclusion should be traceable to:

```text
question/task
→ source/code revision
→ command/config/environment
→ produced artifact/result
→ report/review
→ hypothesis/decision change
```

## External source registry

Use `provenance/sources.json` for important external dependencies such as:

- upstream Git repositories;
- model repositories/checkpoints;
- papers/specifications;
- datasets;
- external tools or binaries.

Prefer immutable identifiers:

- Git commit SHA instead of only branch name;
- model/dataset revision when available;
- exact version plus download URL;
- checksum for downloaded files where practical.

Do not vendor large third-party repositories or model weights solely for provenance. Record the exact source and revision instead.

## Artifact registry

Use `provenance/artifacts.json` for large or external artifacts that should not live in Git, for example:

- model weights;
- tensor dumps;
- large datasets;
- benchmark outputs;
- profiling traces;
- generated archives.

A useful artifact record includes:

- stable `artifact_id`;
- producing `task_id` / `experiment_id`;
- kind and short description;
- durable or local location;
- size;
- SHA-256 or other strong checksum when practical;
- producing command/script/config;
- source commit;
- retention notes.

A local path by itself is not durable provenance. If an artifact is intentionally local-only, say so explicitly and keep enough generation information to recreate it.

## Small evidence in Git

Prefer committing compact, reviewable evidence:

- JSON/CSV metrics;
- short logs containing first mismatch/error;
- experiment configs;
- plots when useful;
- reports;
- patches;
- scripts used to generate larger artifacts.

## Secrets and private data

Never put credentials, access tokens, private keys, authentication cookies, or unapproved private data into provenance manifests, logs, PRs, or artifacts. Record only non-secret identifiers needed for reproducibility.

## Evidence lifecycle

Raw evidence may be large and temporary. Durable conclusions should be compact.

```text
raw artifacts
→ structured result
→ reviewed evidence
→ hypothesis/decision update
→ compressed canonical state
```

Preserve enough provenance to revisit a conclusion without forcing future agents to preserve the entire original context window.
