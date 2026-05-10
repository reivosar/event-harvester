#!/usr/bin/env bash
# PreToolUse hook for Bash — runs security/quality checks before `git commit`.
# Receives JSON on stdin: {"tool_name": "Bash", "tool_input": {"command": "..."}}
# Exits 2 to block the commit on failure.

set -euo pipefail

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin)['tool_input']['command'])" 2>/dev/null || true)

# Only run for git commit commands
if ! echo "$COMMAND" | grep -qE '^git commit'; then
  exit 0
fi

STAGED=$(git diff --cached --name-only 2>/dev/null || true)

if [[ -z "$STAGED" ]]; then
  exit 0
fi

ERRORS=()

# --- 1. Secret detection ---
# Look for common secret assignment patterns in staged content
SECRET_PATTERN='(password|passwd|api_key|apikey|secret|token|private_key)\s*[:=]\s*["'"'"'][^"'"'"']{4,}'
if git diff --cached -U0 | grep -iE "$SECRET_PATTERN" | grep -v '\.example' | grep -qE '^\+'; then
  ERRORS+=("Potential secret detected in staged changes. Remove it and use environment variables instead.")
fi

# --- 2. Branch name validation ---
BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null || echo "HEAD")
VALID_PREFIX='^(feat|fix|docs|chore|refactor|test|perf)/'
if [[ "$BRANCH" != "HEAD" ]] && [[ "$BRANCH" != "main" ]] && [[ "$BRANCH" != "master" ]] && ! echo "$BRANCH" | grep -qE "$VALID_PREFIX"; then
  ERRORS+=("Branch name '$BRANCH' does not follow the required prefix pattern (feat/|fix/|docs/|chore/|refactor/|test/|perf/).")
fi

# --- 3. Trailing whitespace ---
TRAILING=$(git diff --cached --check 2>&1 | grep 'trailing whitespace' | head -5 || true)
if [[ -n "$TRAILING" ]]; then
  ERRORS+=("Trailing whitespace found. Run: git diff --cached --check")
fi

# --- Report ---
if [[ ${#ERRORS[@]} -gt 0 ]]; then
  echo "BLOCKED: Pre-commit checks failed:" >&2
  for err in "${ERRORS[@]}"; do
    echo "  - $err" >&2
  done
  exit 2
fi

exit 0
