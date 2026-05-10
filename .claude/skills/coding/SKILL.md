---
name: coding
description: Coding skill for all implementation work — frontend, backend, CLI tools, scripts, full-stack, shared utilities, configuration, or anything else. Use this skill whenever the task is to write or modify code against a known design. Do NOT use for bug investigation — use troubleshooting instead.
---

# Coding

Implement code for any domain — frontend, backend, scripts, CLI, full-stack, or general utilities. The design or requirement is already known; this skill writes it.

## Setup

Always read (applies to every implementation):
- `.claude/rule-library/code-style.md`
- `.claude/rule-library/coding.md`
- `.claude/rule-library/testing.md`

Read when the task involves:
- Input validation, auth, or external data → `.claude/rule-library/security.md`
- Error handling or failure paths → `.claude/rule-library/errors.md`
- Log statements → `.claude/rule-library/logging.md`
- Frontend (UI, components, browser code) → `.claude/rule-library/frontend.md`
- Backend (APIs, services, DB, server-side) → `.claude/rule-library/backend.md`, `.claude/rule-library/database.md`, `.claude/rule-library/configuration.md`

## Arguments

The task description is passed as `$ARGUMENTS`. If files are mentioned, read them first.

## Process

Follow Red-Green-Refactor strictly. Tests come before implementation.

### 1. Understand the context

Before writing anything:

- Identify the language, toolchain, and conventions in use
- Locate the relevant entry point or file — search by symbol or filename, don't read speculatively
- Clarify ambiguous requirements before writing code

### 2. Plan the change

State in one sentence what you're going to build. Identify:
- What are the inputs and outputs?
- What are the failure modes?
- What test cases cover the happy path and each failure mode?

### 3. Red — write failing tests first

Write tests that describe the expected behavior before any implementation exists:
- One test per behavior (happy path, each error path, each edge case)
- Tests must fail at this point — if a test passes without implementation, it tests nothing
- Run the test suite and confirm the new tests fail

### 4. Green — implement to pass the tests

Write the minimum code required to make the failing tests pass:
- Match the existing code style and conventions
- Validate inputs at system boundaries
- Do not add logic not required by a currently failing test
- Run the test suite and confirm all tests pass

### 5. Refactor — clean up without changing behavior

With tests green, improve the implementation:
- Remove duplication
- Improve naming
- Extract if a function has grown beyond a single responsibility
- Run the test suite again — all tests must still pass after refactoring

## Report

When done:
- **What changed**: files/functions affected
- **Why**: the design decision behind the implementation
- **Caveats**: anything the caller should know about edge cases or follow-up work
