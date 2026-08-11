#!/usr/bin/env bash
#
# Turn a verified handoff into a briefing for the successor.
#
# The point is to hand the successor the *structured* fields rather than only
# the prose summary. The structured fields are the ones Babel checked; the
# prose is the part that drifts.
#
#   ./read-handoff.sh .babel/handoff.json

set -euo pipefail

handoff=${1:-.babel/handoff.json}

if ! command -v jq >/dev/null 2>&1; then
    echo "read-handoff: needs jq" >&2
    exit 2
fi

printf 'You are taking over: %s\n' "$(jq -r '.task.title // .task.task_id' "$handoff")"
printf 'Predecessor: %s   Checkpoint: %s\n\n' \
    "$(jq -r '.producer.agent' "$handoff")" \
    "$(jq -r '.checkpoint.checkpoint_id' "$handoff")"

printf 'CONSTRAINTS YOU MUST NOT BREAK\n'
jq -r '(.retained_constraints // [])[] | select(.binding=="MUST")
       | "  - \(.statement)"' "$handoff"

if [ "$(jq -r '[(.retained_constraints // [])[] | select(.binding=="SHOULD")] | length' "$handoff")" != "0" ]; then
    printf '\nPREFERENCES\n'
    jq -r '(.retained_constraints // [])[] | select(.binding=="SHOULD")
           | "  - \(.statement)"' "$handoff"
fi

printf '\nALREADY DECIDED — do not reopen these\n'
jq -r '(.decisions // [])[] | "  - \(.choice)" +
       (if .rationale then "\n      (\(.rationale))" else "" end)' "$handoff"

printf '\nSTILL OPEN — this is your work\n'
open_count=$(jq -r '(.unresolved // []) | length' "$handoff")
if [ "$open_count" = "0" ]; then
    printf '  (nothing recorded as open)\n'
else
    jq -r '(.unresolved // [])[] |
           "  - \(.statement)" + (if .blocking then "  [BLOCKING]" else "" end)' \
        "$handoff"
fi

printf '\nESTABLISHED FACTS\n'
jq -r '(.objects // [])[] | "  - \(.object_id) = \(.value|tostring)" +
       (if .required then "  [required]" else "" end)' "$handoff"

printf '\nSUMMARY FROM THE PREDECESSOR\n'
jq -r '  "  " + (.summary.text // "(none)")' "$handoff"

printf '\nWhen you finish, write your own handoff and run:\n'
printf '  babelci diff %s YOUR_HANDOFF.json\n' "$handoff"
