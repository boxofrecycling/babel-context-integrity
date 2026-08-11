"""``babelci demo`` -- the 60-second walkthrough.

Three acts, in this order, because the order is the argument:

1. a clean handoff passes;
2. a corrupted one fails, at a named layer, with expected/received;
3. a handoff that passes every internal check and is still wrong.

Act three is the point. Acts one and two are what people expect a verifier to
do; act three is what a verifier cannot do, stated by the tool itself rather
than buried in a limitations section.
"""

from __future__ import annotations

from ..contract import EXIT_OK
from ..render import render_verify
from ..verify import verify
from . import cases


def _act(number: int, title: str) -> None:
    print()
    print(f"── {number}. {title} " + "─" * max(0, 58 - len(title)))
    print()


def main(args=None) -> int:
    print()
    print("BABEL CONTEXT INTEGRITY — 60 second demo")
    print("Scenario: one coding agent hands an auth migration to the next.")

    expectation = cases.expectation()

    _act(1, "A clean handoff")
    clean = cases.build("clean")
    print("$ babelci verify examples/clean-handoff.json")
    print()
    print(render_verify(verify(clean, expectation=expectation,
                               source="examples/clean-handoff.json")))
    print()
    print("  Note the last line. Nothing outside the artifact was consulted,")
    print("  so the tool says so instead of calling it green.")

    _act(2, "One MUST constraint stops being carried")
    broken = cases.build("constraint-dropped")
    print("$ babelci verify examples/corrupted-handoff.json --expect .babel/expect.json")
    print()
    print(render_verify(verify(broken, expectation=expectation,
                               source="examples/corrupted-handoff.json")))
    print()
    print("  The prose summary still reads fine. The contract does not.")

    _act(3, "Every local check passes. Every fact is wrong.")
    common = cases.build("common-mode")
    print("$ babelci verify examples/common-mode-handoff.json")
    print()
    print(render_verify(verify(common, expectation=expectation,
                               source="examples/common-mode-handoff.json")))
    print()
    print("  Structure, identity, checkpoint, provenance, constraints and")
    print("  conflicts all accept this artifact. So do both of the verifier's")
    print("  independent encoders. It describes a branch nobody worked on.")
    print()
    print("  Why didn't the two encoders catch it? Because they agree about")
    print("  what the artifact SAYS, and they are both reading the same")
    print("  artifact. Agreement means it is unambiguous, not that it is true.")
    print()
    print("  The external receipt is different in kind: it was issued by")
    print("  something that looked at the repository instead of at the")
    print("  handoff. That is the only way a false-but-coherent world gets")
    print("  caught — and it moves your trust to whoever issued the receipt")
    print("  rather than removing it.")
    print()
    print("  Agreement is not truth.")
    print()
    print("Next:  babelci lab          all 15 cases")
    print("       babelci explain FILE what each layer establishes")
    print("       babelci rules        why diff says SAFE, REVIEW or REFUSE")
    print()
    return EXIT_OK


__all__ = ["main"]
