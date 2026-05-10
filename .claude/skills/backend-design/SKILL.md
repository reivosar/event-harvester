---
name: backend-design
description: Design and implement backend features. Use this skill when the user wants to build or redesign APIs, services, database models, or backend logic — whether from scratch or modifying existing ones.
---

# Backend Design

## Setup

Read before proceeding:
- `.claude/rule-library/backend.md`
- `.claude/rule-library/coding.md`
- `.claude/rule-library/code-style.md`
- `.claude/rule-library/security.md`
- `.claude/rule-library/testing.md`
- `.claude/rule-library/database.md`
- `.claude/rule-library/errors.md`
- `.claude/rule-library/logging.md`
- `.claude/rule-library/monitoring.md`

## Steps

### 1. Investigate

Understand the existing codebase before touching anything:
- Identify the language, framework, and directory structure
- Find handlers, services, or models adjacent to the target area
- Note the API conventions, error handling patterns, and validation approach in use

### 2. Design

Decide the structure before writing code:
- API surface: endpoints, methods, request/response shapes, status codes
- Data model: tables/fields/relationships or document structure
- Service boundaries: what this layer is responsible for vs. what it delegates
- Failure modes: what can go wrong and how errors propagate to the caller

State the design in a short summary before implementing.

### 3. Implement

Write the code following the conventions from the rule files. Match the existing codebase style exactly — do not introduce new patterns without reason.

### 4. Verify

- Run existing tests; add an integration or unit test for the changed path if none exist
- Confirm auth, input validation, and error responses are correct
- Check for obvious security issues: injection, missing auth checks, data over-exposure
