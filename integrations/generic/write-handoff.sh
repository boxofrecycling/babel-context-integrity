#!/usr/bin/env bash
#
# Build and seal a handoff from shell variables.
#
# For agents and scripts that would rather not hand-assemble JSON. Everything
# is optional except the task id and the authority root.
#
#   BABEL_TASK_ID=PR-4412/migrate-auth \
#   BABEL_AUTHORITY=repo@$(git rev-parse --short HEAD) \
#   BABEL_PRODUCER=my-agent \
#   BABEL_MUST="Do not drop the legacy session table yet.
#   Every new endpoint requires the oidc:read scope." \
#   BABEL_DECIDED="Use Okta as the OIDC provider." \
#   BABEL_OPEN="Rotation interval unagreed with security." \
#   BABEL_FACTS="auth.provider=okta-oidc
#   legacy.sessions=1843" \
#   BABEL_SUMMARY="Migrated auth behind a flag; legacy table untouched." \
#   ./write-handoff.sh > .babel/handoff.json
#
# Newline-separated values become one entry each. Facts are `key=value`.

set -euo pipefail

: "${BABEL_TASK_ID:?set BABEL_TASK_ID}"
: "${BABEL_AUTHORITY:?set BABEL_AUTHORITY (a commit, ticket or dataset id)}"

babelci=${BABELCI:-babelci}
command -v "$babelci" >/dev/null 2>&1 || {
    echo "write-handoff: babelci not found; pip install babel-context-integrity" >&2
    exit 2
}

python3 - <<'PY' | "$babelci" seal -
import json, os, sys

def lines(name):
    raw = os.environ.get(name, "")
    return [line.strip() for line in raw.splitlines() if line.strip()]

authority = os.environ["BABEL_AUTHORITY"]
producer = os.environ.get("BABEL_PRODUCER", "agent")
source = os.environ.get("BABEL_SOURCE", "agent-run")

objects = []
for index, entry in enumerate(lines("BABEL_FACTS")):
    key, _, value = entry.partition("=")
    key = key.strip() or f"fact.{index}"
    value = value.strip()
    # Numbers and booleans keep their type; everything else stays a string.
    try:
        parsed = json.loads(value)
    except (ValueError, TypeError):
        parsed = value
    objects.append({"object_id": key, "kind": "fact", "value": parsed,
                    "required": True, "provenance": source})

handoff = {
    "babel_handoff": "0.1",
    "handoff_id": os.environ.get("BABEL_HANDOFF_ID", f"{producer}-handoff"),
    "task": {"task_id": os.environ["BABEL_TASK_ID"]},
    "producer": {"agent": producer},
    "checkpoint": {"checkpoint_id": os.environ.get("BABEL_CHECKPOINT", "cp-01"),
                   "state_digest": ""},
    "objects": objects,
    "retained_constraints": (
        [{"constraint_id": f"C{i+1}", "binding": "MUST", "statement": text}
         for i, text in enumerate(lines("BABEL_MUST"))] +
        [{"constraint_id": f"S{i+1}", "binding": "SHOULD", "statement": text}
         for i, text in enumerate(lines("BABEL_SHOULD"))]),
    "decisions": [{"decision_id": f"D{i+1}", "choice": text}
                  for i, text in enumerate(lines("BABEL_DECIDED"))],
    "unresolved": [{"issue_id": f"U{i+1}", "statement": text}
                   for i, text in enumerate(lines("BABEL_OPEN"))],
    "provenance": {"authority_root": authority,
                   "edges": [[source, authority]]},
}

consumer = os.environ.get("BABEL_CONSUMER")
if consumer:
    handoff["consumer"] = {"agent": consumer}

parent = os.environ.get("BABEL_PARENT_CHECKPOINT")
if parent:
    handoff["checkpoint"]["parent_checkpoint_id"] = parent

summary = os.environ.get("BABEL_SUMMARY")
if summary:
    handoff["summary"] = {"text": summary, "commitment": ""}

json.dump(handoff, sys.stdout)
PY
