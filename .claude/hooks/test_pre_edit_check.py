#!/usr/bin/env python3
"""Tests for pre-edit-check.py: TDD Red-phase enforcement, function extraction, test coverage."""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile

HOOK = os.path.join(os.path.dirname(__file__), "pre-edit-check.py")


def _load_module():
    spec = importlib.util.spec_from_file_location("pre_edit_check", HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def make_git_repo():
    tmpdir = tempfile.mkdtemp(prefix="hook_test_edit_")
    subprocess.run(["git", "init", tmpdir], check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmpdir, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmpdir, check=True, capture_output=True)
    init_path = os.path.join(tmpdir, "init.txt")
    with open(init_path, "w") as f:
        f.write("init\n")
    subprocess.run(["git", "add", "init.txt"], cwd=tmpdir, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=tmpdir, check=True, capture_output=True)
    return tmpdir


def stage_file(tmpdir, name, content):
    path = os.path.join(tmpdir, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    subprocess.run(["git", "add", name], cwd=tmpdir, check=True, capture_output=True)


def commit_file(tmpdir, name, content):
    stage_file(tmpdir, name, content)
    subprocess.run(["git", "commit", "-m", f"add {name}"], cwd=tmpdir, check=True, capture_output=True)


def run_hook(tmpdir, tool_name, file_path, code_key, code_value):
    payload = json.dumps({
        "tool_name": tool_name,
        "tool_input": {"file_path": file_path, code_key: code_value},
    })
    result = subprocess.run(
        ["python3", HOOK],
        input=payload, capture_output=True, text=True, cwd=tmpdir,
    )
    return result.returncode


def cleanup(tmpdir):
    shutil.rmtree(tmpdir, ignore_errors=True)


passed = failed = 0


def check(label, got, expected):
    global passed, failed
    ok = got == expected
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {label} → expected exit {expected}, got {got}")
    if ok:
        passed += 1
    else:
        failed += 1


mod = _load_module()

# Unit tests: is_impl_file
for path, expect in [
    ("src/app.py",              True),
    ("src/app.ts",              True),
    ("src/app.go",              True),
    ("src/app.java",            True),
    ("src/app.rb",              True),
    ("tests/test_app.py",       False),
    ("app.spec.ts",             False),
    ("__tests__/app.test.ts",   False),
    ("README.md",               False),
    ("config.json",             False),
    (".claude/hooks/foo.sh",    False),
    (".env",                    False),
]:
    ok = mod.is_impl_file(path) == expect
    print(f"[{'PASS' if ok else 'FAIL'}] is_impl_file({path!r}) == {expect}")
    if ok:
        passed += 1
    else:
        failed += 1

print()

# Unit tests: extract_func_names
for code, file_path, expect in [
    ("def calculate(x):\n    pass\n", "app.py", {"calculate"}),
    ("x = 1\n",                        "app.py", set()),
    ("function myFunc(a: string) {\n}", "app.ts", {"myFunc"}),
    ("const process = async (x) => {\n}", "app.ts", {"process"}),
    ("func (r *Repo) Save(x int) {\n}", "app.go", {"Save"}),
    ("func NewClient() {\n}",            "app.go", {"NewClient"}),
    # C: 'if' is a keyword — KEYWORD_SKIP removes it
    ("if (cond) {\n    x = 1;\n}\n",    "app.c",  set()),
]:
    got = mod.extract_func_names(code, file_path)
    ok = got == expect
    print(f"[{'PASS' if ok else 'FAIL'}] extract_func_names({file_path!r}) == {expect!r}")
    if ok:
        passed += 1
    else:
        failed += 1

print()

# Blackbox tests

# TC-ED-01: non-impl file (markdown) is skipped → exit 0
tmpdir = make_git_repo()
try:
    check("TC-ED-01 markdown skipped", run_hook(tmpdir, "Edit", "README.md", "old_string", "any"), 0)
finally:
    cleanup(tmpdir)

# TC-ED-02: test file itself is skipped → exit 0
tmpdir = make_git_repo()
try:
    check("TC-ED-02 test file itself skipped", run_hook(tmpdir, "Edit", "tests/test_app.py", "old_string", "def test_x():"), 0)
finally:
    cleanup(tmpdir)

# TC-ED-03: empty old_string → no code to analyse → exit 0
tmpdir = make_git_repo()
try:
    check("TC-ED-03 empty code skipped", run_hook(tmpdir, "Edit", "src/app.py", "old_string", ""), 0)
finally:
    cleanup(tmpdir)

# TC-ED-04: no test files anywhere → blocked
tmpdir = make_git_repo()
try:
    check("TC-ED-04 no tests blocked", run_hook(tmpdir, "Edit", "src/app.py", "old_string", "def calc():"), 2)
finally:
    cleanup(tmpdir)

# TC-ED-05: staged test references the modified function → allowed
tmpdir = make_git_repo()
try:
    stage_file(tmpdir, "tests/test_calc.py", "def test_calc():\n    calc()\n")
    check("TC-ED-05 staged test covers func", run_hook(tmpdir, "Edit", "src/app.py", "old_string", "def calc():"), 0)
finally:
    cleanup(tmpdir)

# TC-ED-06: staged test does not reference the modified function → blocked
tmpdir = make_git_repo()
try:
    stage_file(tmpdir, "tests/test_other.py", "def test_other():\n    other()\n")
    check("TC-ED-06 staged test missing func blocked", run_hook(tmpdir, "Edit", "src/app.py", "old_string", "def calc():"), 2)
finally:
    cleanup(tmpdir)

# TC-ED-07: test committed in last commit references the function (none staged) → allowed
tmpdir = make_git_repo()
try:
    commit_file(tmpdir, "tests/test_calc.py", "def test_calc():\n    calc()\n")
    check("TC-ED-07 last-commit test covers func", run_hook(tmpdir, "Edit", "src/app.py", "old_string", "def calc():"), 0)
finally:
    cleanup(tmpdir)

# TC-ED-08: no function names extracted, test file stem matches impl stem → allowed
tmpdir = make_git_repo()
try:
    stage_file(tmpdir, "tests/test_app.py", "# placeholder\n")
    # "x = 1" has no extractable function names in Python — falls back to stem match
    # stem of "src/app.py" is "app"; "test_app.py" contains "app" → match
    check("TC-ED-08 stem match fallback allowed", run_hook(tmpdir, "Edit", "src/app.py", "old_string", "x = 1\n"), 0)
finally:
    cleanup(tmpdir)

# TC-ED-09: no function names extracted, no stem match → blocked
tmpdir = make_git_repo()
try:
    stage_file(tmpdir, "tests/test_other.py", "# placeholder\n")
    # "test_other.py" does not contain stem "app" → no match → blocked
    check("TC-ED-09 no stem match blocked", run_hook(tmpdir, "Edit", "src/app.py", "old_string", "x = 1\n"), 2)
finally:
    cleanup(tmpdir)

# TC-ED-10: Write tool uses 'content' key (not 'old_string') → same coverage check applies
tmpdir = make_git_repo()
try:
    stage_file(tmpdir, "tests/test_calc.py", "def test_calc():\n    calc()\n")
    check("TC-ED-10 Write tool content key", run_hook(tmpdir, "Write", "src/app.py", "content", "def calc():\n    pass\n"), 0)
finally:
    cleanup(tmpdir)

print(f"\n{passed} passed, {failed} failed")
sys.exit(0 if failed == 0 else 1)
