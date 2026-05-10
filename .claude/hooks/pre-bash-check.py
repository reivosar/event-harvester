#!/usr/bin/env python3
"""
Allow-list check for pre-bash.sh.
Exit 0 = allowed, Exit 2 = blocked.
"""
import sys
import json
import fnmatch
import os
import re


def read_command():
    try:
        data = json.load(sys.stdin)
        return data.get("tool_input", {}).get("command", "")
    except Exception:
        return None


def load_patterns(settings_path, key):
    with open(settings_path) as f:
        settings = json.load(f)
    entries = settings.get("permissions", {}).get(key, [])
    return [e[5:-1] for e in entries if e.startswith("Bash(") and e.endswith(")")]


def is_denied(command, patterns):
    return any(fnmatch.fnmatch(command, p) for p in patterns)


def is_whitelisted(command, patterns):
    return any(fnmatch.fnmatch(command, p) for p in patterns)


def block(reason):
    print(f"BLOCKED: {reason}", file=sys.stderr)
    sys.exit(2)


def check_stash_destructive(command):
    if re.search(r"git\s+stash\s+(drop|clear)", command):
        block("'git stash drop/clear' permanently deletes stashed work. "
              "Run 'git stash list' to review stashes before dropping.")


def check_checkout_discard(command):
    if re.search(r"git\s+checkout\s+--", command):
        block("'git checkout --' discards uncommitted changes permanently. "
              "Use 'git diff' to review changes first, or 'git stash' to save them.")


def check_branch_force_delete(command):
    if re.search(r"git\s+branch\s+-D\b", command):
        block("'git branch -D' force-deletes a branch. "
              "Use 'git branch -d' (safe delete) — it refuses to delete unmerged branches.")


def check_redirect_overwrite(command):
    match = re.search(r"(?<![>2])\s>(?![>&])\s*(\S+)", command)
    if match:
        target = os.path.expanduser(match.group(1))
        if os.path.exists(target):
            block(f"shell redirect '>' would overwrite existing file '{target}'. "
                  f"Use '>>' to append, or remove the file first if overwriting is intended.")


def run_blocklist_checks(command):
    check_stash_destructive(command)
    check_checkout_discard(command)
    check_branch_force_delete(command)
    check_redirect_overwrite(command)


def main():
    settings_path = sys.argv[1]

    command = read_command()
    if not command:
        sys.exit(0)

    try:
        allow_patterns = load_patterns(settings_path, "allow")
        deny_patterns = load_patterns(settings_path, "deny")
    except Exception as e:
        print(f"BLOCKED: could not read settings.json — {e}", file=sys.stderr)
        sys.exit(2)

    if is_denied(command, deny_patterns):
        print(f"BLOCKED: command matches deny list: {command[:300]}", file=sys.stderr)
        sys.exit(2)

    if not is_whitelisted(command, allow_patterns):
        print(f"BLOCKED: command not in allow list: {command[:300]}", file=sys.stderr)
        sys.exit(2)

    run_blocklist_checks(command)
    sys.exit(0)


if __name__ == "__main__":
    main()
