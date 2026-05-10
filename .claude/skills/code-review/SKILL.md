---
name: code-review
description: Review code changes on the current branch for bugs, security issues, code quality, and test coverage. Use this skill whenever the user asks to review, check, or audit code changes, a diff, a PR, or a branch — even if they just say "look over this" or "what do you think of these changes?"
---

# Code Review

Review the changes on the current branch and produce a structured report.

## Setup

Read the following rule files before proceeding:
- `.claude/rule-library/code-style.md`
- `.claude/rule-library/git-workflow.md`
- `.claude/rule-library/testing.md`
- `.claude/rule-library/security.md`

## Arguments

`$ARGUMENTS` is optional. If a PR number is passed (e.g. `42`), review that PR. Otherwise review the current branch.

## Gather the diff

**Current branch:**
```bash
git diff main...HEAD
git log main...HEAD --oneline
```

**PR number given:**
```bash
gh pr view $ARGUMENTS
gh pr diff $ARGUMENTS
```

Read each changed file to understand the intent behind the change, not just the mechanics.

## Review areas

### Bugs & Logic Errors
Look for incorrect behavior, not just syntax. Focus on:
- Logic that is wrong for edge cases (empty collections, null/undefined, concurrent access)
- Async code that lacks error handling or has race conditions
- Off-by-one errors, incorrect comparisons, missed negations

### Security
- OWASP Top 10: XSS, SQL injection, auth bypass, insecure deserialization, etc.
- Secrets or API keys hardcoded in source
- Missing validation on any data that crosses a trust boundary (user input, external APIs, env vars)

### Code Quality
Good code quality means the next developer can understand and modify the code safely. Check:
- Names that clearly convey intent (a name that requires a comment to understand is a red flag)
- Duplication that should be extracted
- Abstraction that obscures rather than clarifies
- Comments that describe *what* instead of *why* (the code already shows what; comments should explain non-obvious reasoning)

### Tests
- Tests added or updated proportional to the change
- Tests that verify real behavior, not just that mocks were called
- Edge cases covered (not just the happy path)

### Conventions
- Commit messages follow Conventional Commits (`feat:`, `fix:`, `docs:`, etc.)
- Code style matches the rules in `.claude/rule-library/code-style.md`

## Report format

Structure the report with one section per area above. Within each section, list specific file and line references for each finding. Omit sections that have no findings rather than writing "none found."

End with a verdict:
- **Approved** — ready to merge
- **Changes requested** — required fixes listed specifically (not vaguely)
- **Needs discussion** — design questions that need a decision before proceeding
