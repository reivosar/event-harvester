---
name: pull-request
description: Create a pull request from the current feature branch. Use this skill when the user says "create a PR", "open a pull request", "PR this", "ready to merge", or has finished a coding task and the next step is to get it reviewed.
---

# Pull Request

Create a pull request from the current branch to main.

## Setup

Read `.claude/rule-library/git-workflow.md` before proceeding.

## Step 1: Verify branch state

```bash
git branch --show-current
git status
git log main...HEAD --oneline
```

Guards:
- If on `main` — stop. Tell the user to create a feature branch first.
- If there are unstaged changes — run the `commit` skill first, then return here.
- If there are no commits ahead of `main` — stop. Nothing to PR.

## Step 2: Push the branch

```bash
git push -u origin HEAD
```

If the push fails due to diverged history, do not force push. Report the conflict to the user.

## Step 3: Draft the PR

**Title** — derive from the commit log:
- Single commit: use the commit subject line as-is
- Multiple commits: write a one-line summary of what the set of commits achieves as a whole

Title rules (same as commit summary):
- Imperative mood
- Under 72 characters
- No period at the end

**Body** — use this template:

```
## What

<1–3 bullets describing what changed>

## Why

<The motivation: what problem this solves or what requirement it fulfills>

## How to test

<Concrete steps a reviewer can follow to verify the change works>
```

## Step 4: Create the PR

```bash
gh pr create --title "<title>" --body "$(cat <<'EOF'
## What

<bullets>

## Why

<motivation>

## How to test

<steps>
EOF
)"
```

## Step 5: Report

Output the PR URL so the user can share or open it.
