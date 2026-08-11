"""Generate docs/DIFF_RULES.md from the rule table so it cannot drift."""
from pathlib import Path
from babelci.diff import RULES
from babelci.contract import REFUSE, REVIEW, SAFE

HEADER = """# Diff verdict rules

Generated from `src/babelci/diff.py`. Do not edit by hand -- run
`python tools/gen_docs.py`. `tests/test_docs.py` fails if this file drifts.

`babelci diff` reports every change with a verdict, and every verdict comes
from exactly one rule below. Human output leads with the sentence; the rule id
is the machine handle and appears in `--json` and `-v`. There is no scoring and no heuristic. A change
with no matching rule is reported as `REVIEW` under `unclassified-change`,
which is itself a rule -- a human deciding beats a tool guessing.

The overall verdict is the worst individual verdict.

| Verdict | Exit code | Meaning |
|---|---|---|
| `SAFE` | 0 | the change is normal progress under the contract |
| `REVIEW` | 0 (3 with `--strict`) | a human should look; the contract does not forbid it |
| `REFUSE` | 1 | the contract forbids this change |
"""

lines = [HEADER]
for verdict in (REFUSE, REVIEW, SAFE):
    lines.append(f"\n## {verdict}\n")
    for name, rule in sorted(RULES.items()):
        if rule["verdict"] == verdict:
            lines.append(f"### {rule['headline']}\n")
            lines.append(f"Rule id `{name}`. {rule['because'].capitalize()}.\n")
Path("docs/DIFF_RULES.md").write_text("\n".join(lines).replace("\n\n\n", "\n\n"), encoding="utf-8")
print("wrote docs/DIFF_RULES.md")
