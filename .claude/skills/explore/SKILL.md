---
name: explore
description: Investigate an unfamiliar codebase, module, or concept and produce a structured summary. Use this skill when the user is onboarding to a new project, wants to understand how something works, asks "how does X work?", "where is Y handled?", or "give me an overview of Z." Also use it proactively at the start of a session when the codebase is unfamiliar.
---

# Explore

Investigate and summarize without making any changes.

## Arguments

The target to explore is `$ARGUMENTS`. If omitted, give an overview of the whole project.

## What to investigate

Start broad, then drill into what's interesting or relevant to the user's work.

**Architecture**
- Overall directory structure and what each top-level area owns
- Key components, their responsibilities, and how they communicate
- Data flow: where data enters the system, how it's transformed, where it exits

**Implementation patterns**
- How features are typically structured (look at 2–3 existing examples)
- Error handling approach
- How configuration and environment variables are used
- Auth / session handling (if the user will be working near that area)

**Testing**
- Test framework and how to run tests (`npm test`, `pytest`, etc.)
- Patterns in existing tests: fixtures, factories, mocking style

**Build & dev environment**
- Commands to build, run, and test the project
- Required environment variables and where they're documented

## Output format

```
## Overview
<One sentence: what this project does and who it's for.>

## Key components
- `src/auth/` — handles JWT issuance and session management
- `src/api/` — REST handlers, one file per resource
(keep this list to the 5–8 most important areas)

## How to run
- Install: `npm install`
- Dev server: `npm run dev`
- Tests: `npm test`
- Build: `npm run build`

## Important patterns
<What a developer needs to know before adding a new feature. Reference specific files as examples.>

## Gotchas
<Non-obvious things that trip up newcomers: unusual conventions, known quirks, things not in the README.>
```

Keep the summary dense and actionable. Skip sections that don't apply.
