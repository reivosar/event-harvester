#!/usr/bin/env bash
# PreToolUse hook for Write/Edit — enforces TDD Red phase.
HOOKS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECKER="$HOOKS_DIR/pre-edit-check.py"
[[ ! -f "$CHECKER" ]] && exit 0
exec python3 "$CHECKER"
