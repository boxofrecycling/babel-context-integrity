#!/usr/bin/env bash
#
# Run the GitHub Action locally, without GitHub.
#
# The action is a wrapper over the CLI, so it can be exercised by setting the
# same environment variables Actions would set and calling entrypoint.sh
# directly. This script checks that it passes on a clean handoff, fails on a
# corrupted one, and reports the diff verdict -- which is the whole contract
# between the action and the workflow that uses it.
#
#   ./action/test-local.sh

set -uo pipefail

here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
root=$(dirname -- "$here")
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

if [ -x "$root/.venv/bin/babelci" ]; then
    export BABELCI="$root/.venv/bin/babelci"
elif command -v babelci >/dev/null 2>&1; then
    export BABELCI=babelci
else
    echo "test-local: babelci is not installed; run: pip install -e '.[dev]'" >&2
    exit 2
fi

"$BABELCI" lab --out "$work" >/dev/null || {
    echo "test-local: could not generate fixtures" >&2
    exit 2
}

pass=0
fail=0

check() {
    local name=$1 expected=$2 actual=$3
    if [ "$expected" = "$actual" ]; then
        printf 'ok    %-46s exit %s\n' "$name" "$actual"
        pass=$((pass + 1))
    else
        printf 'FAIL  %-46s exit %s, wanted %s\n' "$name" "$actual" "$expected"
        fail=$((fail + 1))
    fi
}

# The action reads its inputs from the environment, so each scenario exports
# them and then runs the entrypoint exactly as Actions would.
run() {
    export BABEL_HANDOFF=$1
    ( "$here/entrypoint.sh" >/dev/null 2>&1 )
    echo $?
}

export BABEL_EXPECT="$work/expect.json"
export BABEL_AGAINST=""
export BABEL_STRICT=false
export BABEL_JSON_REPORT=""

check "clean handoff passes"            0 "$(run "$work/clean.json")"
check "dropped MUST constraint fails"   1 "$(run "$work/constraint-dropped.json")"
check "rejected external receipt fails" 1 "$(run "$work/common-mode.json")"
check "missing artifact fails"          1 "$(run "$work/missing.json")"

# diff mode
export BABEL_AGAINST="$work/clean.json"
check "normal progress diffs SAFE"      0 "$(run "$work/restart-resume.json")"
check "silent reversal diffs REFUSE"    1 "$(run "$work/decision-reversed.json")"

# --strict turns a REVIEW into a failure
export BABEL_STRICT=true
check "strict mode still passes SAFE"   0 "$(run "$work/restart-resume.json")"
export BABEL_STRICT=false

# json report is written where asked
export BABEL_AGAINST=""
export BABEL_JSON_REPORT="$work/report/verify.json"
export BABEL_HANDOFF="$work/clean.json"
"$here/entrypoint.sh" >/dev/null 2>&1
if [ -s "$work/report/verify.json" ]; then
    printf 'ok    %-46s written\n' "json report"
    pass=$((pass + 1))
else
    printf 'FAIL  %-46s missing\n' "json report"
    fail=$((fail + 1))
fi

# Annotations: GitHub renders these inline on the pull request, so their
# absence is a silent UX failure rather than a loud one.
export BABEL_AGAINST="$work/clean.json"
export BABEL_JSON_REPORT=""
export BABEL_HANDOFF="$work/constraint-dropped.json"
annotations=$("$here/entrypoint.sh" 2>&1 | grep -c '^::error ' || true)
if [ "$annotations" -ge 2 ]; then
    printf 'ok    %-46s %s emitted\n' "error annotations" "$annotations"
    pass=$((pass + 1))
else
    printf 'FAIL  %-46s %s emitted, wanted >=2\n' "error annotations" "$annotations"
    fail=$((fail + 1))
fi

export BABEL_HANDOFF="$work/clean.json"
export BABEL_AGAINST=""
noise=$("$here/entrypoint.sh" 2>&1 | grep -c '^::error ' || true)
if [ "$noise" -eq 0 ]; then
    printf 'ok    %-46s none on success\n' "no spurious annotations"
    pass=$((pass + 1))
else
    printf 'FAIL  %-46s %s on a passing handoff\n' "no spurious annotations" "$noise"
    fail=$((fail + 1))
fi

# Step summary: the thing a reviewer reads at the top of the run.
summary="$work/summary.md"
export BABEL_HANDOFF="$work/constraint-dropped.json"
GITHUB_STEP_SUMMARY="$summary" "$here/entrypoint.sh" >/dev/null 2>&1
if grep -q "RETAINED_CONSTRAINT_MISSING" "$summary" 2>/dev/null; then
    printf 'ok    %-46s names the failure\n' "step summary"
    pass=$((pass + 1))
else
    printf 'FAIL  %-46s missing or vague\n' "step summary"
    fail=$((fail + 1))
fi

echo
echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ] || exit 1
