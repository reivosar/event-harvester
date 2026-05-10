---
name: commit
description: Create a well-formed git commit for staged changes using Conventional Commits format. Use this skill when the user asks to commit, says "commit this", "make a commit", or "save my changes." Also use it at the end of a task when changes are ready to be committed.
---

# Commit

Create a Conventional Commits message for what is staged and commit it.

## Setup

Read `.claude/rule-library/git-workflow.md` before proceeding.

## Step 1: Verify branch

```bash
git branch --show-current
```

If on `main` — stop. Do not commit to main directly. Tell the user to create a feature branch:

```bash
git checkout -b feat/<short-description>
```

## Step 2: Understand what's staged

```bash
git status
git diff --staged
```

Read the diff carefully. The commit message should reflect the *intent* of the change, not just list files modified.

## Step 3: Draft the message

**Format:**
```
<type>(<scope>): <summary>

[optional body]
```

**Type selection:**
- `feat` — new capability the user didn't have before
- `fix` — corrects incorrect behavior
- `docs` — documentation only, no logic change
- `refactor` — restructures code without changing behavior
- `test` — adds or updates tests
- `chore` — build config, dependencies, tooling
- `perf` — measurable performance improvement

**Summary line rules:**
- Imperative mood: "add", "fix", "remove" — not "added", "fixes", "removed"
- No period at the end
- Under 72 characters
- Specific enough that someone reading the log can understand the change without opening the diff

**Body** (include when the summary alone isn't enough):
- Explain *why* the change was made, not what it does (the diff shows what)
- Mention tradeoffs or alternatives considered if relevant

## Step 4: Propose and confirm

Show the proposed message to the user and wait for approval or edits before committing. Do not stage unstaged files unless explicitly asked.

## Step 5: Commit

```bash
git commit -m "$(cat <<'EOF'
<type>(<scope>): <summary>

<body if any>
EOF
)"
```
