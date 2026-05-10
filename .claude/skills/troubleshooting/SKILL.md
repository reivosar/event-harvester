---
name: troubleshooting
description: Investigate and resolve broken behavior. The defining condition is uncertainty about the cause — something is wrong but why is unknown. Use this skill when the user shares an error message, stack trace, failing test, or unexpected behavior, or says "this is broken", "it's not working", "help me debug this." Do NOT use the coding skill for this — diagnosis must come before any fix.
---

# Troubleshooting

Start from broken behavior with unknown cause. Diagnose first — do not write any fix until the root cause is stated. Change only what the root cause requires.

## Setup

Read the following rule files before proceeding:
- `.claude/rule-library/code-style.md`
- `.claude/rule-library/testing.md`
- `.claude/rule-library/security.md`

## Arguments

The problem description or error message is passed as `$ARGUMENTS`. If the user pasted it inline, use that. If they mentioned a file, read it first.

## Process

### 1. Investigate (read only)

Before touching anything, understand the system:

- Search for the error string or failing symbol: `grep -r "ErrorMessage" src/`
- Trace the call path from the entry point to where the error occurs
- Check git history to find when the behavior changed: `git log -p --all -S "symptom"` — this often reveals the commit that introduced the bug

Resist the urge to fix immediately. The first obvious explanation is often wrong.

### 2. Form a hypothesis

State the root cause in one sentence before writing any code. If there are multiple plausible causes, rank them and check the most likely one first.

### 3. Fix

- Change only what is necessary to fix the root cause
- Do not refactor, rename, or clean up adjacent code — that belongs in a separate commit
- If suppressing the error (try/catch, null check) is tempting, that's a sign the root cause is still wrong — fix the actual problem

### 4. Verify

- Run existing tests: if they pass before and fail after (or vice versa), you've confirmed the fix
- If no tests exist, write a minimal failing test first, then make it pass — this proves the fix actually works
- Grep for the same pattern elsewhere: `grep -rn "same_pattern" src/` — bugs often exist in multiple places

## Report

When done:
- **Root cause**: what was actually wrong and why
- **Fix**: what changed and the reasoning
- **Other occurrences**: whether the same bug pattern exists elsewhere, and if so, where
