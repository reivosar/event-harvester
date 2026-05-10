#!/usr/bin/env python3
"""
Pre-tool-call hook for the Write tool.
Blocks Write when the target file already exists — use Edit instead.
"""
import sys
import json
import os


def read_file_path():
    try:
        data = json.load(sys.stdin)
        return data.get("tool_input", {}).get("file_path", "")
    except Exception:
        return None


def check_file_exists(file_path):
    if os.path.exists(file_path):
        print(
            f"BLOCKED: '{file_path}' already exists. Use Edit to modify existing files.",
            file=sys.stderr,
        )
        sys.exit(2)


def main():
    file_path = read_file_path()
    if not file_path:
        sys.exit(0)
    check_file_exists(file_path)
    sys.exit(0)


if __name__ == "__main__":
    main()
