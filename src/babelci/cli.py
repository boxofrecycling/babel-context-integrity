"""``babelci`` command line.

Design rules, all of them testable:

* no network access, ever -- there is no HTTP client in this package;
* no model calls -- there is no model SDK in this package;
* deterministic -- the same inputs produce byte-identical output;
* no telemetry, no config file, no daemon, no cache directory;
* exit codes are documented and stable.

Exit codes
    0  everything checked passed
    1  a check failed (verify) or a REFUSE change was found (diff)
    2  usage or input error
    3  a REVIEW change was found (diff only)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from . import (__version__, authorities, carry as carry_module,
               diff as diff_module, render, seal as seal_module)
from .contract import (
    EXIT_FAIL, EXIT_OK, EXIT_REVIEW, EXIT_USAGE, LAYER_MEANING, REFUSE, REVIEW,
)
from .schema import schema_path
from .verify import verify

PROGRAM = "babelci"


def _load(path: str) -> Any:
    if path == "-":
        return json.loads(sys.stdin.read())
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as error:
        raise SystemExit(_usage_error(f"cannot read {path}: {error.strerror}"))
    try:
        return json.loads(text)
    except json.JSONDecodeError as error:
        raise SystemExit(_usage_error(f"{path} is not valid JSON: {error}"))


def _usage_error(message: str) -> int:
    print(f"{PROGRAM}: {message}", file=sys.stderr)
    return EXIT_USAGE


def _emit(result: dict[str, Any], human: str, as_json: bool) -> None:
    if as_json:
        print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    else:
        print(human)


# ---------------------------------------------------------------------------

def cmd_verify(args: argparse.Namespace) -> int:
    handoff = _load(args.handoff)
    expectation = _load(args.expect) if args.expect else None
    result = verify(handoff, expectation=expectation,
                    source=None if args.handoff == "-" else args.handoff)
    _emit(result, render.render_verify(result, verbose=args.verbose), args.json)
    return EXIT_OK if result["verdict"] == "PASS" else EXIT_FAIL


def cmd_explain(args: argparse.Namespace) -> int:
    handoff = _load(args.handoff)
    expectation = _load(args.expect) if args.expect else None
    result = verify(handoff, expectation=expectation,
                    source=None if args.handoff == "-" else args.handoff)
    _emit(result, render.render_explain(result, LAYER_MEANING), args.json)
    return EXIT_OK if result["verdict"] == "PASS" else EXIT_FAIL


def cmd_diff(args: argparse.Namespace) -> int:
    old, new = _load(args.old), _load(args.new)
    result = diff_module.diff(old, new, old_source=args.old, new_source=args.new)
    _emit(result, render.render_diff(result, verbose=args.verbose), args.json)
    if result["verdict"] == REFUSE:
        return EXIT_FAIL
    if result["verdict"] == REVIEW:
        return EXIT_REVIEW if args.strict else EXIT_OK
    return EXIT_OK


def cmd_seal(args: argparse.Namespace) -> int:
    draft = _load(args.handoff)
    try:
        sealed = seal_module.seal(draft, declare_authority=args.declare_authority)
    except (KeyError, TypeError, ValueError) as error:
        return _usage_error(f"cannot seal {args.handoff}: {error}")
    text = json.dumps(sealed, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.in_place:
        if args.handoff == "-":
            return _usage_error("--in-place needs a file, not stdin")
        Path(args.handoff).write_text(text, encoding="utf-8")
        print(f"sealed {args.handoff}")
    else:
        sys.stdout.write(text)
    return EXIT_OK


def cmd_carry(args: argparse.Namespace) -> int:
    predecessor = _load(args.handoff)
    try:
        successor = carry_module.carry(
            predecessor,
            checkpoint_id=args.checkpoint,
            handoff_id=args.handoff_id,
            producer=args.producer,
            consumer=args.consumer,
            summary=args.summary)
    except (KeyError, TypeError, ValueError) as error:
        return _usage_error(f"cannot carry {args.handoff}: {error}")
    sys.stdout.write(
        json.dumps(successor, indent=2, sort_keys=True, ensure_ascii=False)
        + "\n")
    return EXIT_OK


def cmd_schema(args: argparse.Namespace) -> int:
    path = schema_path()
    if args.path:
        print(path)
    else:
        sys.stdout.write(path.read_text(encoding="utf-8"))
    return EXIT_OK


def cmd_rules(args: argparse.Namespace) -> int:
    if args.json:
        print(json.dumps(diff_module.RULES, indent=2, sort_keys=True))
        return EXIT_OK
    import textwrap

    for verdict in (REFUSE, REVIEW, "SAFE"):
        print(verdict)
        rules = sorted(
            ((name, rule) for name, rule in diff_module.RULES.items()
             if rule["verdict"] == verdict),
            key=lambda entry: entry[1]["headline"])
        for name, rule in rules:
            print(f"  {rule['headline']}")
            for line in textwrap.wrap(rule["because"], width=70):
                print(f"      {line}")
            print(f"      [{name}]")
        print()
    return EXIT_OK


def cmd_lab(args: argparse.Namespace) -> int:
    from .lab import run as lab_run
    return lab_run.main(args)


def cmd_demo(args: argparse.Namespace) -> int:
    from .lab import demo
    return demo.main(args)


# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=PROGRAM,
        description="Verify what survives when one agent hands work to the next.",
        epilog="Exit codes: 0 pass, 1 fail/refuse, 2 usage, 3 review (diff --strict).",
    )
    parser.add_argument("--version", action="version",
                        version=f"{PROGRAM} {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_json(sub: argparse.ArgumentParser) -> None:
        sub.add_argument("--json", action="store_true",
                         help="emit the machine-readable result instead of prose")

    verify_parser = subparsers.add_parser(
        "verify", help="check one handoff artifact against the contract")
    verify_parser.add_argument("handoff", help="path to a handoff JSON file, or -")
    verify_parser.add_argument("--expect", metavar="FILE",
                               help="expectation file the handoff must satisfy")
    verify_parser.add_argument("-v", "--verbose", action="store_true")
    add_json(verify_parser)
    verify_parser.set_defaults(func=cmd_verify)

    explain_parser = subparsers.add_parser(
        "explain", help="say what each layer establishes and what it found")
    explain_parser.add_argument("handoff")
    explain_parser.add_argument("--expect", metavar="FILE")
    add_json(explain_parser)
    explain_parser.set_defaults(func=cmd_explain, verbose=True)

    diff_parser = subparsers.add_parser(
        "diff", help="report semantic drift between two handoffs")
    diff_parser.add_argument("old")
    diff_parser.add_argument("new")
    diff_parser.add_argument("-v", "--verbose", action="store_true")
    diff_parser.add_argument("--strict", action="store_true",
                             help="exit 3 on REVIEW instead of 0")
    add_json(diff_parser)
    diff_parser.set_defaults(func=cmd_diff)

    seal_parser = subparsers.add_parser(
        "seal", help="fill in the commitments a draft handoff is missing")
    seal_parser.add_argument("handoff")
    seal_parser.add_argument("--in-place", action="store_true")
    seal_parser.add_argument("--declare-authority", metavar="ID",
                             help="record this build's world commitment under ID")
    seal_parser.set_defaults(func=cmd_seal)

    carry_parser = subparsers.add_parser(
        "carry", help="draft the successor of a handoff, carrying it forward")
    carry_parser.add_argument("handoff")
    carry_parser.add_argument("--checkpoint", required=True, metavar="ID",
                              help="checkpoint id the successor declares")
    carry_parser.add_argument("--handoff-id", dest="handoff_id", metavar="ID",
                              help="successor handoff id (default: --checkpoint)")
    carry_parser.add_argument("--producer", metavar="AGENT",
                              help="successor's producer "
                                   "(default: the predecessor's consumer)")
    carry_parser.add_argument("--consumer", metavar="AGENT",
                              help="who the successor will hand to")
    carry_parser.add_argument("--summary", metavar="TEXT",
                              help="prose for the successor; the predecessor's "
                                   "is never carried")
    carry_parser.set_defaults(func=cmd_carry)

    schema_parser = subparsers.add_parser(
        "schema", help="print the normative JSON Schema")
    schema_parser.add_argument("--path", action="store_true",
                               help="print the file path instead of the contents")
    schema_parser.set_defaults(func=cmd_schema)

    rules_parser = subparsers.add_parser(
        "rules", help="print the diff verdict rules")
    add_json(rules_parser)
    rules_parser.set_defaults(func=cmd_rules)

    lab_parser = subparsers.add_parser(
        "lab", help="run the deterministic failure-class lab")
    lab_parser.add_argument("case", nargs="?",
                            help="run one case instead of all of them")
    lab_parser.add_argument("--list", action="store_true",
                            help="list the cases and exit")
    lab_parser.add_argument("--out", metavar="DIR",
                            help="write the generated fixtures to DIR")
    add_json(lab_parser)
    lab_parser.set_defaults(func=cmd_lab)

    demo_parser = subparsers.add_parser(
        "demo", help="the 60-second walkthrough")
    demo_parser.set_defaults(func=cmd_demo, json=False)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except SystemExit as error:  # _load raises SystemExit carrying an exit code
        code = error.code
        return code if isinstance(code, int) else EXIT_USAGE
    except BrokenPipeError:  # `babelci verify x --json | head`
        return EXIT_OK


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
