#!/usr/bin/env bash
# Pre-tool-call hook: allow only commands listed in settings.json permissions.allow
# Receives JSON on stdin: {"tool_name": "Bash", "tool_input": {"command": "..."}}

HOOKS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SETTINGS="$HOOKS_DIR/../settings.json"

exec python3 "$HOOKS_DIR/pre-bash-check.py" "$SETTINGS"
