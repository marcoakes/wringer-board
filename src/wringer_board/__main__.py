"""`wringer-board render <repo> -o board.html`.

**Not a `wring` subcommand, and never will be.** SPEC_BOARD_V0 §8 non-goal 5:
the core is at its 19-command ceiling and this is a separate layer consuming
the engine through what it already emits. B2.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from wringer_board import read as read_module
from wringer_board import render as render_module


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="wringer-board",
        description=(
            "Render a Wringer repository's requirements as one page a product "
            "manager can read without being taught anything first."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)
    rendered = sub.add_parser("render", help="write the board as one HTML file")
    rendered.add_argument("repo", nargs="?", default=".", help="the repository")
    rendered.add_argument(
        "-o", "--out", default="board.html", help="where to write the page"
    )
    # **Two artifacts the engine does not leave under `.wringer/`**, so the
    # only honest way to render them is to be handed the engine's own report.
    # Both optional, and absent means the page says nothing about them —
    # never that they were fine.
    rendered.add_argument(
        "--health-report",
        metavar="PATH",
        help="a health report the engine wrote: 'wring health --json --output "
             "PATH'. Without it the page says nothing about check health",
    )
    rendered.add_argument(
        "--audit-report",
        metavar="PATH",
        help="an audit report the engine wrote: 'wring audit --json ATTESTATION"
             " > PATH'. Without it the page says nothing about signature, "
             "identity or integrity",
    )

    args = parser.parse_args(argv)
    repo = Path(args.repo).resolve()
    out = Path(args.out)

    try:
        board = read_module.read(
            repo,
            health_report=Path(args.health_report) if args.health_report else None,
            audit_report=Path(args.audit_report) if args.audit_report else None,
        )
    except read_module.UnknownVersion as exc:
        # **Ruling 6, and the exit code says it too.** A version this board does
        # not know renders a banner and ZERO CARDS — never a partial page — and
        # exits non-zero so a script cannot mistake it for a render.
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            render_module.render_unknown_version(exc), encoding="utf-8"
        )
        print(f"wringer-board: {exc}", file=sys.stderr)
        print(f"wringer-board: wrote a refusal to {out}", file=sys.stderr)
        return 2

    render_module.write(board, out)
    print(f"wringer-board: {out}")
    return 0


if __name__ == "__main__":  # pragma: no cover - the entry point
    raise SystemExit(main())
