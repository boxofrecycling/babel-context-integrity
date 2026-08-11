#!/usr/bin/env bash
#
# Session-end handoff check.
#
# Deliberately advisory: it reports, it does not block. A hook that fails a
# session because a file is missing is a hook that gets deleted within a week.
# CI is where this becomes enforcing -- see ../../docs/CI.md.

set -uo pipefail

project=${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}
handoff="$project/.babel/handoff.json"
expect="$project/.babel/expect.json"

if [ ! -f "$handoff" ]; then
    cat <<EOF
[babel] No .babel/handoff.json was written this session.

The next session will inherit only the prose summary, which is where
constraints quietly stop existing. To write one:

    babelci seal .babel/draft.json > .babel/handoff.json
EOF
    exit 0
fi

if ! command -v babelci >/dev/null 2>&1; then
    echo "[babel] .babel/handoff.json exists but babelci is not installed."
    echo "[babel]   pip install babel-context-integrity"
    exit 0
fi

args=(verify "$handoff")
[ -f "$expect" ] && args+=(--expect "$expect")

echo "[babel] verifying the handoff this session is leaving behind"
babelci "${args[@]}"
status=$?

if [ "$status" -ne 0 ]; then
    cat <<EOF

[babel] The handoff does not satisfy the contract. The next session would
[babel] inherit a story that no longer matches what was required.
[babel] Fix .babel/handoff.json, or explain the change in .babel/expect.json.
EOF
fi

exit 0
