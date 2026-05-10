---
name: plan
description: Explore the codebase and produce a detailed implementation plan before writing any code. Use this skill when the user wants to implement a feature, refactor something across multiple files, or asks "how should I approach this?" or "what would need to change?" — especially when the scope is unclear or the change touches unfamiliar code. When in doubt, plan first.
---

# Plan

Produce a concrete implementation plan without modifying any files.

## Setup

Read the following rule files before proceeding:
- `.claude/rule-library/code-style.md`
- `.claude/rule-library/testing.md`
- `.claude/rule-library/security.md`

## Arguments

The task or feature to plan is `$ARGUMENTS`.

## Phase 1: Explore

Read before reasoning. Do not modify anything.

- Identify which files and modules are likely involved
- Find existing utilities, abstractions, and patterns that could be reused — building on existing code is almost always better than adding new layers
- Understand the interfaces at the boundaries: what data flows in, what flows out, what invariants are assumed
- Check the test setup: how are similar things tested, and what fixtures or helpers already exist

When exploring a large codebase, use subagents in parallel to cover more ground faster. Assign each subagent a specific area (e.g., one reads the auth module, another reads the test patterns).

## Phase 2: Write the plan

Produce the plan in this format:

```
## Implementation Plan: <task name>

### Context
Why this change is being made and what outcome it achieves.

### Files to change
- `path/to/file.ts` — what changes and why (one line each)

### Files to create
- `path/to/new.ts` — purpose

### Existing code to reuse
- `path/to/util.ts` → `functionName()` — explain how it's used

### Implementation steps
1. ...
2. ...
(ordered so each step is independently testable if possible)

### Edge cases to handle
- ...

### Verification
- Command to run: `npm test -- --grep "auth"`
- Behavior to confirm: ...

### Open questions
- Decisions that need input before implementation can proceed
```

## Present and wait

Share the plan and explicitly ask whether to proceed. Do not begin implementation until the user approves.

Once approved, switch out of Plan Mode and implement step by step, verifying after each step.
