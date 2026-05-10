#!/usr/bin/env bash
HOOKS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$HOOKS_DIR/pre-write-check.py"
