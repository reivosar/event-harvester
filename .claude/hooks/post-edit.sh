#!/usr/bin/env bash
# Post-tool-call hook: auto-format files after Write or Edit
# Receives JSON on stdin: {"tool_name": "...", "tool_input": {"file_path": "..."}}

INPUT=$(cat)
FILE=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))" 2>/dev/null)

if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
  exit 0
fi

EXT="${FILE##*.}"

case "$EXT" in
  js|jsx|ts|tsx|json|css|md)
    if command -v prettier &>/dev/null; then
      prettier --write "$FILE" --loglevel silent 2>/dev/null
    fi
    ;;
  py)
    if command -v black &>/dev/null; then
      black "$FILE" -q 2>/dev/null
    elif command -v autopep8 &>/dev/null; then
      autopep8 --in-place "$FILE" 2>/dev/null
    fi
    ;;
  go)
    if command -v gofmt &>/dev/null; then
      gofmt -w "$FILE" 2>/dev/null
    fi
    ;;
  rb)
    if command -v rubocop &>/dev/null; then
      rubocop -a "$FILE" --no-color -q 2>/dev/null
    fi
    ;;
  sh|bash)
    if command -v shfmt &>/dev/null; then
      shfmt -w "$FILE" 2>/dev/null
    fi
    ;;
esac

exit 0
