#!/usr/bin/env python3
"""
TDD Red-phase enforcement hook for Write/Edit tools.
Verifies that staged (or recently committed) test files reference
the functions being modified before allowing implementation edits.
"""
import sys
import json
import re
import subprocess
import os

IMPL_EXTS = {
    '.ts', '.tsx', '.js', '.jsx', '.mts', '.mjs',
    '.py', '.go', '.java', '.rb', '.rs',
    '.kt', '.kts', '.swift', '.cs',
    '.cpp', '.cc', '.cxx', '.c', '.h', '.hpp', '.php',
}

SKIP_BASENAMES = {'Makefile', 'Dockerfile', 'Procfile', '.gitignore'}

SKIP_EXT = {'.md', '.json', '.yaml', '.yml', '.toml', '.ini', '.sh',
            '.txt', '.lock', '.sum', '.env', '.gitignore'}

TEST_NAME_RE = re.compile(r'(test|spec)(\.|_|-|$)', re.IGNORECASE)
TEST_DIR_RE = re.compile(r'(/__tests__/|/tests?/|/specs?/)', re.IGNORECASE)

FUNC_PATTERNS = {
    '.py':    [r'def\s+(\w+)\s*\('],
    '.go':    [r'func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)\s*\('],
    '.rb':    [r'def\s+(\w+)'],
    '.rs':    [r'fn\s+(\w+)\s*[\(<]'],
    '.kt':    [r'fun\s+(\w+)\s*[\(<]'],
    '.kts':   [r'fun\s+(\w+)\s*[\(<]'],
    '.swift': [r'func\s+(\w+)\s*[\(<]'],
}
_JS = [
    r'function\s+(\w+)\s*\(',
    r'(?:async\s+)?(?:export\s+)?(?:const|let)\s+(\w+)\s*=\s*(?:async\s*)?\(',
    r'(?:public|private|protected|static|async)(?:\s+\w+)*\s+(\w+)\s*\(',
]
for _e in ('.ts', '.tsx', '.js', '.jsx', '.mts', '.mjs'):
    FUNC_PATTERNS[_e] = _JS
_JAVA = [r'(?:public|private|protected|static|final|\s)+\w[\w<>\[\]]*\s+(\w+)\s*\(']
for _e in ('.java', '.cs'):
    FUNC_PATTERNS[_e] = _JAVA
_C = [r'\b(\w+)\s*\([^;]*\)\s*\{']
for _e in ('.c', '.h', '.cpp', '.cc', '.cxx', '.hpp'):
    FUNC_PATTERNS[_e] = _C

KEYWORD_SKIP = {'if', 'for', 'while', 'return', 'new', 'switch', 'catch', 'try',
                'else', 'do', 'case', 'break', 'continue', 'throw', 'import',
                'class', 'interface', 'enum', 'struct', 'type', 'const', 'let', 'var'}


def read_input():
    data = json.load(sys.stdin)
    return data.get('tool_name', ''), data.get('tool_input', {})


def is_impl_file(path):
    basename = os.path.basename(path)
    if basename in SKIP_BASENAMES:
        return False
    if path.startswith('.claude/') or path.startswith('CLAUDE'):
        return False
    _, ext = os.path.splitext(path)
    if ext.lower() in SKIP_EXT:
        return False
    if not ext or path.startswith('.env'):
        return False
    if is_test_file(path):
        return False
    return ext.lower() in IMPL_EXTS


def is_test_file(path):
    basename = os.path.basename(path)
    return bool(TEST_NAME_RE.search(basename) or TEST_DIR_RE.search(path))


def extract_func_names(code, file_path):
    _, ext = os.path.splitext(file_path)
    patterns = FUNC_PATTERNS.get(ext.lower(), [])
    names = set()
    for pattern in patterns:
        for m in re.finditer(pattern, code, re.MULTILINE):
            name = m.group(1)
            if name and len(name) > 1 and name not in KEYWORD_SKIP:
                names.add(name)
    return names


def git_files(cmd):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return [f for f in result.stdout.strip().split('\n') if f]
    except Exception:
        return []


def test_covers_funcs(test_paths, func_names):
    for path in test_paths:
        try:
            with open(path, encoding='utf-8', errors='ignore') as f:
                content = f.read()
            if any(name in content for name in func_names):
                return True
        except OSError:
            continue
    return False


def block(reason, file_path, func_names, staged_tests):
    print(f"BLOCKED: {reason}", file=sys.stderr)
    print(f"  File: {file_path}", file=sys.stderr)
    if func_names:
        print(f"  Functions being modified: {', '.join(sorted(func_names))}", file=sys.stderr)
    if staged_tests:
        print(f"  Staged tests: {', '.join(staged_tests)}", file=sys.stderr)
        print(f"  None reference the modified functions.", file=sys.stderr)
    else:
        print(f"  No test files staged or in the last commit.", file=sys.stderr)
    print(f"  Write a failing test for these functions first (Red phase).", file=sys.stderr)
    sys.exit(2)


def main():
    tool_name, tool_input = read_input()
    file_path = tool_input.get('file_path', '')

    if not file_path or not is_impl_file(file_path):
        sys.exit(0)

    code = (tool_input.get('old_string') or '') if tool_name == 'Edit' else tool_input.get('content', '')
    if not code:
        sys.exit(0)

    func_names = extract_func_names(code, file_path)

    staged_tests = [f for f in git_files(['git', 'diff', '--staged', '--name-only']) if is_test_file(f)]
    last_tests = [f for f in git_files(['git', 'log', '-1', '--name-only', '--pretty=format:']) if is_test_file(f)]
    all_tests = staged_tests + last_tests

    if not all_tests:
        block("No test files staged.", file_path, func_names, staged_tests)

    if func_names:
        if not test_covers_funcs(all_tests, func_names):
            block(
                "Staged tests do not reference the modified functions.",
                file_path, func_names, staged_tests,
            )
    else:
        # No function names extracted — fall back to file-stem match
        impl_stem = re.sub(r'\.\w+$', '', os.path.basename(file_path)).lower()
        matched = [t for t in all_tests if impl_stem in os.path.basename(t).lower()]
        if not matched:
            block(
                f"No test for '{os.path.basename(file_path)}' found.",
                file_path, func_names, staged_tests,
            )

    sys.exit(0)


if __name__ == '__main__':
    main()
