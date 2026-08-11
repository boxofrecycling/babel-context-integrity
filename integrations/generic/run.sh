#!/usr/bin/env bash
#
# The whole handoff loop, end to end, offline.
#
#   1. predecessor writes a draft and seals it
#   2. babel verifies it against the repository's expectation
#   3. successor reads the structured briefing
#   4. successor writes its own handoff; babel diffs the two
#
# Nothing here needs a vendor API, a network connection, or a model.

set -euo pipefail

here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
root=$(cd "$here/../.." && pwd)
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

if [ -x "$root/.venv/bin/babelci" ]; then
    babelci="$root/.venv/bin/babelci"
else
    babelci=babelci
fi

say() { printf '\n\033[1m── %s\033[0m\n\n' "$1"; }

# ---------------------------------------------------------------------------
say "1. predecessor writes a handoff"

cat >"$work/draft.json" <<'JSON'
{
  "babel_handoff": "0.1",
  "handoff_id": "run-a",
  "task": { "task_id": "demo/rewrite-parser", "title": "Rewrite the config parser" },
  "producer": { "agent": "agent-a", "run_id": "run-0001" },
  "consumer": { "agent": "agent-b" },
  "checkpoint": { "checkpoint_id": "cp-01", "state_digest": "" },
  "objects": [
    { "object_id": "parser.format", "kind": "fact", "value": "toml",
      "required": true, "provenance": "scan/repo" },
    { "object_id": "tests.passing", "kind": "metric", "value": 87,
      "required": true, "provenance": "ci/run-1" }
  ],
  "retained_constraints": [
    { "constraint_id": "C1", "binding": "MUST",
      "statement": "The old YAML loader must keep working until v3 ships." },
    { "constraint_id": "C2", "binding": "SHOULD",
      "statement": "Prefer stdlib tomllib over a third-party parser." }
  ],
  "decisions": [
    { "decision_id": "D1", "choice": "Target TOML, not JSON5.",
      "rationale": "tomllib is in the stdlib from 3.11." }
  ],
  "unresolved": [
    { "issue_id": "U1", "statement": "Error message format is not agreed.",
      "blocking": false }
  ],
  "provenance": {
    "authority_root": "repo@deadbeef",
    "edges": [["scan/repo", "repo@deadbeef"], ["ci/run-1", "repo@deadbeef"]]
  },
  "summary": {
    "text": "Config parser now reads TOML via tomllib. The YAML loader is untouched and must stay that way until v3. 87 tests pass. Error message format still undecided.",
    "commitment": ""
  }
}
JSON

"$babelci" seal "$work/draft.json" >"$work/handoff-01.json"
echo "wrote $work/handoff-01.json"

cat >"$work/expect.json" <<'JSON'
{
  "babel_expectation": "0.1",
  "task_id": "demo/rewrite-parser",
  "authority_root": "repo@deadbeef",
  "required_constraints": [{ "constraint_id": "C1" }],
  "required_objects": ["parser.format", "tests.passing"],
  "required_unresolved": ["U1"]
}
JSON

# ---------------------------------------------------------------------------
say "2. babel verifies it"
"$babelci" verify "$work/handoff-01.json" --expect "$work/expect.json"

# ---------------------------------------------------------------------------
say "3. successor reads the structured briefing"
"$here/read-handoff.sh" "$work/handoff-01.json"

# ---------------------------------------------------------------------------
say "4a. successor does the work honestly, and babel diffs"

python3 - "$work/handoff-01.json" "$work/draft-02.json" <<'PY'
import json, sys
src, dst = sys.argv[1], sys.argv[2]
handoff = json.load(open(src))
handoff["handoff_id"] = "run-b"
handoff["producer"] = {"agent": "agent-b", "run_id": "run-0002"}
handoff["consumer"] = {"agent": "reviewer"}
handoff["checkpoint"] = {"checkpoint_id": "cp-02",
                         "parent_checkpoint_id": "cp-01", "state_digest": ""}
handoff["decisions"].append({
    "decision_id": "D2", "choice": "Error messages use the `file:line: msg` form.",
    "supersedes": "U1"})
handoff["unresolved"] = []
handoff["summary"]["text"] = handoff["summary"]["text"].replace(
    "Error message format still undecided.",
    "Error messages use the file:line: msg form.")
json.dump(handoff, open(dst, "w"), indent=2)
PY

"$babelci" seal "$work/draft-02.json" >"$work/handoff-02.json"
"$babelci" verify "$work/handoff-02.json" --expect "$work/expect.json"
echo
"$babelci" diff "$work/handoff-01.json" "$work/handoff-02.json"

# ---------------------------------------------------------------------------
say "4b. now the successor quietly reverses a decision"

python3 - "$work/handoff-02.json" "$work/draft-03.json" <<'PY'
import json, sys
src, dst = sys.argv[1], sys.argv[2]
handoff = json.load(open(src))
handoff["handoff_id"] = "run-c"
handoff["checkpoint"] = {"checkpoint_id": "cp-03",
                         "parent_checkpoint_id": "cp-02", "state_digest": ""}
for decision in handoff["decisions"]:
    if decision["decision_id"] == "D1":
        decision["choice"] = "Target JSON5 after all."
        decision["rationale"] = "Nicer for humans."
json.dump(handoff, open(dst, "w"), indent=2)
PY

"$babelci" seal "$work/draft-03.json" >"$work/handoff-03.json"

echo "verify says:"
"$babelci" verify "$work/handoff-03.json" --expect "$work/expect.json" || true
echo
echo "diff against the predecessor says:"
"$babelci" diff "$work/handoff-02.json" "$work/handoff-03.json" || true

say "done"
echo "A single artifact cannot show a reversal. Two artifacts can."
