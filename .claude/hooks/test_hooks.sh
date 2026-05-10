#!/usr/bin/env bash
# Run all hook test suites and report a pass/fail summary.
set -euo pipefail

HOOKS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOTAL_PASS=0
TOTAL_FAIL=0
FAILED_SUITES=()

for test_file in "$HOOKS_DIR"/test_*.py; do
    echo "=== $(basename "$test_file") ==="
    if python3 "$test_file"; then
        TOTAL_PASS=$((TOTAL_PASS + 1))
    else
        TOTAL_FAIL=$((TOTAL_FAIL + 1))
        FAILED_SUITES+=("$(basename "$test_file")")
    fi
    echo
done

echo "=== Summary: $TOTAL_PASS suites passed, $TOTAL_FAIL failed ==="
if [[ ${#FAILED_SUITES[@]} -gt 0 ]]; then
    printf "Failed suites: %s\n" "${FAILED_SUITES[*]}"
fi
exit $((TOTAL_FAIL > 0 ? 1 : 0))
