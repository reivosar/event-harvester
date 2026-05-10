---
name: documentation
description: Generate or update documentation. Use this skill when the user wants to write or update a README, create an Architecture Decision Record (ADR), generate an OpenAPI spec, or document an API — triggered by phrases like "document this", "write a README", "create an ADR", "generate API docs", "update the docs".
---

# Documentation

## Setup

Read before proceeding:
- `.claude/rule-library/documentation.md`
- `.claude/rule-library/code-style.md`

## Steps

### 1. Investigate

Before writing anything:
- Read what documentation already exists — do not duplicate or contradict it
- Read the actual source code for the area being documented; never invent behavior
- Identify the output type needed: README, ADR, OpenAPI spec, or inline comments

### 2. Write

Match the format required by `documentation.md`:

**README** — include: Overview, Setup, Usage, Architecture decisions. Keep commands copy-pasteable and tested.

**ADR** — file at `docs/adr/NNN-short-title.md`. Fill all four sections: Status, Context, Decision, Consequences.

**OpenAPI spec** — document every endpoint, all request/response schemas, and all error codes. Co-locate with the service it describes.

**Inline comments** — WHY only. If the comment restates what the code does, delete it.

### 3. Verify

- Every shell command in the docs runs successfully in the current environment
- Every claim about behavior matches what the code actually does — no aspirational docs
- ADR status is set correctly (Proposed, Accepted, etc.)
