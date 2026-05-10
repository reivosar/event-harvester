---
name: feedback
description: Capture a rule gap, skill gap, or new pattern discovered during project work and file it as a GitHub issue on the ai-developer-kit repository. Use this skill when you notice something missing from the kit's rules or skills, want to suggest an improvement, or the user says "this should be a rule", "add this to the kit", "file this as feedback", or "log this insight."
---

# Feedback

File an improvement insight as a GitHub issue on `reivosar/ai-developer-kit`.

## Arguments

`$ARGUMENTS` is the insight description. If empty, ask the user:
1. What was missing or should be improved?
2. In which project / what task did this come up?
3. What change would address it (optional)?

## Step 1: Determine category

Choose one label based on the insight:

| Label | When to use |
|---|---|
| `rule-gap` | A rule file lacks guidance that caused confusion or a mistake |
| `skill-gap` | A skill's process was incomplete or missing a step |
| `new-pattern` | A repeating pattern not yet captured as a rule or skill |
| `enhancement` | An existing rule or skill works but could be clearer or stronger |

## Step 2: Ensure labels exist

```bash
gh label create rule-gap --repo reivosar/ai-developer-kit --color 0075ca --description "Missing or incomplete rule coverage" --force
gh label create skill-gap --repo reivosar/ai-developer-kit --color e4e669 --description "Missing or incomplete skill coverage" --force
gh label create new-pattern --repo reivosar/ai-developer-kit --color d93f0b --description "Repeating pattern not yet in the kit" --force
gh label create enhancement --repo reivosar/ai-developer-kit --color a2eeef --description "Improvement to existing rule or skill" --force
```

## Step 3: Derive the issue title

- Imperative, under 72 characters
- Include the affected area: `rule(security):`, `skill(coding):`, `rule(logging):`, etc.
- Example: `rule(errors): add guidance for retrying non-idempotent operations`

## Step 4: Create the issue

```bash
gh issue create \
  --repo reivosar/ai-developer-kit \
  --title "<title>" \
  --label "<label>" \
  --body "$(cat <<'EOF'
## Insight

<What was missing or should be improved>

## Context

Project: <project name or path>
Task: <what was being worked on when this was noticed>

## Suggested change

<Which file to change and what to add or modify — leave blank if unknown>
EOF
)"
```

## Step 5: Report

Output the issue URL.
