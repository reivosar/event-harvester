#!/usr/bin/env bash
# Move files to the session trash instead of deleting permanently

SESSION_FILE="/tmp/claude-session-trash-dir"
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

if [ -f "$SESSION_FILE" ]; then
  TRASH_DIR="$(cat "$SESSION_FILE")"
else
  TIMESTAMP=$(python3 -c "from datetime import datetime; print(datetime.now().strftime('%Y-%m-%d_%H-%M-%S.') + f'{datetime.now().microsecond//1000:03d}')")
  TRASH_DIR="$PROJECT_ROOT/.trash/$TIMESTAMP"
  echo "$TRASH_DIR" > "$SESSION_FILE"
fi

mkdir -p "$TRASH_DIR"

for target in "$@"; do
  ABS_TARGET="$(cd "$(dirname "$target")" 2>/dev/null && pwd)/$(basename "$target")"
  if [[ "$ABS_TARGET" != "$PROJECT_ROOT/"* ]]; then
    echo "BLOCKED: $target is outside project root" >&2
    exit 2
  fi
  mv "$target" "$TRASH_DIR/"
done
