#!/usr/bin/env bash
#
# The whole action. It is a wrapper around the CLI on purpose: anything the
# action can do, you can do locally with the same command and get the same
# answer. `action/test-local.sh` runs this file directly.
#
# Environment (all set by action.yml, all optional except BABEL_HANDOFF):
#   BABEL_HANDOFF      path to the artifact to verify
#   BABEL_EXPECT       expectation file
#   BABEL_AGAINST      predecessor artifact to diff against
#   BABEL_STRICT       "true" to fail on a diff REVIEW
#   BABEL_JSON_REPORT  path to write machine-readable results
#   GITHUB_OUTPUT      set by Actions; ignored when unset
#   GITHUB_STEP_SUMMARY set by Actions; ignored when unset

set -uo pipefail

handoff=${BABEL_HANDOFF:-.babel/handoff.json}
expect=${BABEL_EXPECT:-}
against=${BABEL_AGAINST:-}
strict=${BABEL_STRICT:-false}
report=${BABEL_JSON_REPORT:-}

babelci=${BABELCI:-babelci}

emit_output() {
    [ -n "${GITHUB_OUTPUT:-}" ] && printf '%s=%s\n' "$1" "$2" >>"$GITHUB_OUTPUT"
    return 0
}

emit_summary() {
    [ -n "${GITHUB_STEP_SUMMARY:-}" ] && cat >>"$GITHUB_STEP_SUMMARY"
    return 0
}

if [ ! -f "$handoff" ]; then
    echo "babel-verify: no handoff artifact at '$handoff'" >&2
    echo "babel-verify: the producing agent is expected to write one; see" >&2
    echo "              https://github.com/babel-context-integrity/babel-context-integrity#integrations" >&2
    exit 1
fi

verify_args=("verify" "$handoff")
[ -n "$expect" ] && verify_args+=("--expect" "$expect")

echo "── babelci verify $handoff"
"$babelci" "${verify_args[@]}"
verify_status=$?

if [ -n "$report" ]; then
    mkdir -p "$(dirname "$report")"
    "$babelci" "${verify_args[@]}" --json >"$report"
fi

if [ "$verify_status" -eq 0 ]; then
    emit_output verdict PASS
else
    emit_output verdict FAIL
fi

diff_status=0
diff_verdict=""
if [ -n "$against" ]; then
    if [ ! -f "$against" ]; then
        echo "babel-verify: no predecessor artifact at '$against'" >&2
        exit 1
    fi
    echo
    echo "── babelci diff $against $handoff"
    diff_args=("diff" "$against" "$handoff")
    [ "$strict" = "true" ] && diff_args+=("--strict")
    "$babelci" "${diff_args[@]}"
    diff_status=$?
    case "$diff_status" in
        0) diff_verdict=SAFE ;;
        3) diff_verdict=REVIEW ;;
        1) diff_verdict=REFUSE ;;
        *) diff_verdict=ERROR ;;
    esac
    emit_output diff-verdict "$diff_verdict"
fi

{
    echo "### Babel Context Integrity"
    echo
    if [ "$verify_status" -eq 0 ]; then
        echo "- verify: **PASS** (\`$handoff\`)"
    else
        echo "- verify: **FAIL** (\`$handoff\`) — a required part of the handoff did not survive"
    fi
    [ -n "$diff_verdict" ] && echo "- diff vs \`$against\`: **$diff_verdict**"
    echo
    echo "Reproduce locally: \`babelci verify $handoff${expect:+ --expect $expect}\`"
} | emit_summary

# Usage errors (2) are failures too; anything non-zero fails the check.
if [ "$verify_status" -ne 0 ]; then
    exit "$verify_status"
fi
if [ "$diff_status" -ne 0 ]; then
    exit "$diff_status"
fi
exit 0
