#!/usr/bin/env bash
# Notification hook: send a desktop notification when Claude needs attention
# Receives JSON on stdin with a notification_type field

INPUT=$(cat)
TYPE=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('notification_type',''))" 2>/dev/null)

case "$TYPE" in
  permission_prompt)
    MESSAGE="Claude Code: approval required"
    ;;
  idle_prompt)
    MESSAGE="Claude Code: task complete"
    ;;
  auth_success)
    MESSAGE="Claude Code: authentication complete"
    ;;
  *)
    MESSAGE="Claude Code: attention needed"
    ;;
esac

# macOS Notification Center
if command -v osascript &>/dev/null; then
  osascript -e "display notification \"$MESSAGE\" with title \"Claude Code\" sound name \"Glass\"" 2>/dev/null
fi

# Linux (libnotify)
if command -v notify-send &>/dev/null; then
  notify-send "Claude Code" "$MESSAGE" 2>/dev/null
fi

exit 0
