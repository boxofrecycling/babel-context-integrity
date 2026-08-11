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
    echo "babel-verify: the producing agent is expected to write one." >&2
    echo "babel-verify: see integrations/ for how a predecessor writes one," >&2
    echo "babel-verify: or set the 'handoff' input to a different path." >&2
    exit 1
fi

verify_args=("verify" "$handoff")
[ -n "$expect" ] && verify_args+=("--expect" "$expect")

echo "── babelci verify $handoff"
"$babelci" "${verify_args[@]}"
verify_status=$?

# The machine-readable result drives the annotations, and optionally the
# report the caller asked for. Running the verifier twice is safe: it is
# deterministic, offline and takes milliseconds.
verify_json=$(mktemp)
trap 'rm -f "$verify_json" "${diff_json:-}"' EXIT
"$babelci" "${verify_args[@]}" --json >"$verify_json" 2>/dev/null || true

if [ -n "$report" ]; then
    mkdir -p "$(dirname "$report")"
    cp "$verify_json" "$report"
fi

# GitHub renders `::error` as an inline annotation on the pull request, which
# is where a developer actually looks. Without this the failure is buried in a
# log nobody expands.
annotate_verify() {
    python3 - "$verify_json" "$handoff" <<'PY'
import json, sys

path, handoff = sys.argv[1], sys.argv[2]
try:
    with open(path) as handle:
        result = json.load(handle)
except (OSError, ValueError):
    sys.exit(0)


def clean(text):
    # Annotation commands are newline-delimited; %0A keeps multi-line detail.
    return str(text).replace("%", "%25").replace("\r", "").replace("\n", "%0A")


for finding in result.get("findings", []):
    if finding.get("severity") != "fail":
        continue
    detail = clean(finding.get("detail", ""))
    if isinstance(finding.get("received"), list) and finding["received"]:
        detail += "%0A" + "%0A".join("- " + clean(x) for x in finding["received"])
    elif finding.get("expected") is not None:
        detail += "%0A" + clean(f"expected: {finding['expected']}")
        detail += "%0A" + clean(f"received: {finding.get('received')}")
    print(f"::error file={handoff},title=Babel: {finding['code']}::{detail}")

failed = [layer["layer"] for layer in result.get("layers", [])
          if layer.get("status") == "failed"]
if failed:
    print(f"::notice file={handoff},title=Babel: layers that failed::"
          + clean(", ".join(failed)))
PY
}

annotate_verify

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

    diff_json=$(mktemp)
    "$babelci" "diff" "$against" "$handoff" --json >"$diff_json" 2>/dev/null || true
    python3 - "$diff_json" "$handoff" <<'PY'
import json, sys

path, handoff = sys.argv[1], sys.argv[2]
try:
    with open(path) as handle:
        result = json.load(handle)
except (OSError, ValueError):
    sys.exit(0)

level = {"REFUSE": "error", "REVIEW": "warning"}
for change in result.get("changes", []):
    kind = level.get(change["verdict"])
    if not kind:
        continue
    detail = f"{change['subject']}: {change['headline']}"
    print(f"::{kind} file={handoff},title=Babel diff: {change['rule']}::"
          + detail.replace("%", "%25").replace("\n", "%0A"))
PY
fi

{
    echo "### Babel Context Integrity"
    echo
    if [ "$verify_status" -eq 0 ]; then
        echo "- **verify: PASS** — \`$handoff\`"
    else
        echo "- **verify: FAIL** — \`$handoff\`"
        python3 - "$verify_json" <<'PY'
import json, sys
try:
    with open(sys.argv[1]) as handle:
        result = json.load(handle)
except (OSError, ValueError):
    sys.exit(0)
for layer in result.get("layers", []):
    if layer.get("status") == "failed":
        print(f"  - `{layer['layer']}` failed")
for finding in result.get("findings", []):
    if finding.get("severity") == "fail":
        print(f"    - `{finding['code']}` — {finding['detail']}")
PY
    fi
    if [ -n "$diff_verdict" ]; then
        echo "- **diff vs \`$against\`: $diff_verdict**"
    fi
    echo
    echo "Reproduce locally:"
    echo
    echo '```'
    echo "babelci verify $handoff${expect:+ --expect $expect}"
    [ -n "$against" ] && echo "babelci diff $against $handoff"
    echo '```'
    echo
    echo "What each layer does and does not establish: \`babelci explain $handoff\`"
} | emit_summary

# Usage errors (2) are failures too; anything non-zero fails the check.
if [ "$verify_status" -ne 0 ]; then
    exit "$verify_status"
fi
if [ "$diff_status" -ne 0 ]; then
    exit "$diff_status"
fi
exit 0
