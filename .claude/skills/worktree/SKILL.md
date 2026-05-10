---
name: worktree
description: Create and manage git worktrees for parallel isolated work. Use this skill when the user wants to work on two things at once without losing progress, says "I need to switch context but don't want to stash", "can we work on this in parallel", or asks Claude to work on something in the background while they continue on the main branch.
---

# Worktree

Create an isolated git worktree so parallel work doesn't interfere with the main branch.

## Setup

Read `.claude/rule-library/git-workflow.md` before proceeding.

## Arguments

Worktree name is `$ARGUMENTS`. If omitted, Claude Code generates a random name automatically.

## Create via Claude Code

The cleanest way is to let Claude Code handle it:

```bash
claude --worktree $ARGUMENTS
```

This creates `.claude/worktrees/<name>/` on a new branch `worktree-<name>`, forked from the default remote branch (`origin/HEAD`).

## When to use worktrees

- **Bug fix during a feature**: you're mid-feature but a critical bug needs fixing now — open a worktree for the fix, keep the feature branch clean
- **Parallel review**: one session writes code, another reviews it with a fresh context (no anchoring bias from having written it)
- **Risky experiment**: try a big refactor in a worktree; discard it cleanly if it doesn't work out
- **Subagent isolation**: give subagents their own working copy so they don't step on each other (set `isolation: worktree` in agent frontmatter)

## Copy gitignored files

New worktrees are clean checkouts — `.env` and similar files won't be there. To copy them automatically, add a `.worktreeinclude` at the project root:

```
.env
.env.local
config/local.json
```

## Cleanup behavior

| Situation | Result |
|---|---|
| Worktree closed with no changes | Branch and directory deleted automatically |
| Worktree closed with changes | Prompt to keep or delete |
| Subagent worktree, no changes | Deleted automatically |

## Manual management

```bash
git worktree list
git worktree remove .claude/worktrees/<name>
```

Add `.claude/worktrees/` to `.gitignore` so worktree contents don't show as untracked files in the main repo.
