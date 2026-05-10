---
name: update-kit
description: Update this project's rule-library and skills from the latest version of reivosar/ai-developer-kit. Use this skill when the user says "update the kit", "pull the latest rules", "sync the kit", or "get the latest skills."
---

# Update Kit

Fetch the latest rule-library and skills from `reivosar/ai-developer-kit` and apply them to this project.

## What gets updated

- `.claude/rule-library/*.md` — all rule files (overwritten)
- `.claude/skills/*/SKILL.md` — each skill's definition (overwritten)

## What is never touched

- `CLAUDE.md` — project-specific behavior
- `.claude/settings.json` — project-specific permissions and hooks
- `.claude/hooks/` — project-specific hook scripts
- Any file not present in the kit (project-added files are preserved)

## Step 1: Check prerequisites

```bash
gh auth status
```

If not authenticated, stop and ask the user to run `gh auth login`.

## Step 2: Clone the kit to a temp directory

```bash
KITDIR=$(mktemp -d)
gh repo clone reivosar/ai-developer-kit "$KITDIR" -- --depth=1 --quiet
```

## Step 3: Update rule-library

```bash
cp "$KITDIR/.claude/rule-library/"*.md .claude/rule-library/
```

## Step 4: Update skills

For each skill directory in the kit, copy its SKILL.md into the project:

```bash
for skill_dir in "$KITDIR/.claude/skills"/*/; do
  skill_name=$(basename "$skill_dir")
  mkdir -p ".claude/skills/$skill_name"
  cp "$skill_dir/SKILL.md" ".claude/skills/$skill_name/SKILL.md"
done
```

## Step 5: Clean up

```bash
rm -rf "$KITDIR"
```

## Step 6: Report

Show what changed:

```bash
git diff --stat .claude/rule-library/ .claude/skills/
```

List any new files added (skills or rules not previously in the project):

```bash
git status --short .claude/rule-library/ .claude/skills/
```
