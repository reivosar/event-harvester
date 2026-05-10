#!/usr/bin/env bash
# Stop hook: notify when Claude finishes a session

# macOS Notification Center
if command -v osascript &>/dev/null; then
  osascript -e 'display notification "Claude Code session complete" with title "Claude Code" sound name "Glass"' 2>/dev/null
fi

# Terminal bell fallback
echo -e "\a" 2>/dev/null

exit 0
