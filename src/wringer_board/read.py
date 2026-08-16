"""Reading the engine's artifacts. **This layer renders; it never decides.**

SPEC_BOARD_V0 ruling 1: every card state is a function of bytes the engine
wrote. The surface computes exactly three things that are not reads, and all
three are named there — the receipt chain walk, the staleness comparison, and
the discrimination of `unevidenced`'s four causes. Everything else is a read.

*Why so absolute:* a hand-kept second copy of the engine's judgement is the
exact defect class Wringer exists to catch, and it would drift the week after
it shipped. So this module parses; it does not reimplement `accept.py`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# **The acceptance versions this board understands** (ruling 6, amended
# 2026-08-16). The spec named `wringer.acceptance.v1` alone, because v2 did not
# exist when it was written. It does now — a run carrying a witness lane writes
# v2, and the corpus re-test this board's first real render is built from is
# exactly such a run. Rendering only v1 would mean the board could not show the
# very artifact it was commissioned to show.
#
# v2 is a superset in the only two ways that matter here: a row gains an
# optional `witness` object, and `gate` may be null on a row that still
# `refuses`. Both are handled explicitly below. **The rule ruling 6 actually
# states is unchanged**: anything not on this list produces a banner naming the
# version and NO CARDS AT ALL — not best-effort parsing, not partial rendering.
KNOWN_ACCEPTANCE = ("wringer.acceptance.v1", "wringer.acceptance.v2")

ACCEPTANCE_FILENAME = "acceptance.json"
MANIFEST_FILENAME = "manifest.json"
VACUITY_FILENAME = "vacuity.json"
EVENTS_FILENAME = "loop.jsonl"
SPEC_FILENAME = "wringer.spec.yaml"


class UnknownVersion(Exception):
    """An artifact declares a schema version this board does not know.

    Raised rather than worked around. A reader that meets an unknown version
    and carries on is a reader that supplies the flattering answer, which is
    what every `limits` block in the engine warns about.
    """

    def __init__(self, artifact: str, version: str, known: tuple[str, ...]):
        self.artifact = artifact
        self.version = version
        self.known = known
        super().__init__(
            f"{artifact} declares {version!r}, which this board does not know "
            f"(it knows: {', '.join(known)})"
        )


@dataclass(frozen=True)
class Attempt:
    """One verification, in the order the LOOP ran it."""

    run_id: str
    directory: Path
    ordinal: int
    passed: bool | None = None
    failed_gate: str | None = None


@dataclass(frozen=True)
class Criterion:
    """One row of `acceptance.json`, plus the spec text a PM actually wrote."""

    id: str
    title: str
    required: bool
    state: str
    refuses: bool
    gate_id: str | None
    command: str | None
    reason: str
    receipt: dict[str, Any] | None
    witness: dict[str, Any] | None


@dataclass
class Board:
    """Everything one render needs, read and never recomputed."""

    repo: Path
    run_dir: Path | None = None
    loop_dir: Path | None = None
    acceptance_version: str | None = None
    criteria: list[Criterion] = field(default_factory=list)
    limits: list[str] = field(default_factory=list)
    attempts: list[Attempt] = field(default_factory=list)
    ordered: bool = False
    spec_title: str | None = None
    spec_intent: str | None = None
    scoped_out: list[str] = field(default_factory=list)
    vacuity: dict[str, Any] | None = None
    refusal: str | None = None


def _load(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def latest_run(repo: Path) -> Path | None:
    """The most recent verify bundle, by the LOOP's order where one exists.

    Falls back to the newest directory by mtime, never by id: run ids are
    `<date>-<HHMMSS>-<4 hex>` and do not sort chronologically. In the probe's
    capture four of five runs shared one second and lexical order was wrong
    (ruling 8).
    """
    runs = repo / ".wringer" / "runs"
    if not runs.is_dir():
        return None
    candidates = [p for p in runs.iterdir() if p.is_dir()]
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def latest_loop(repo: Path) -> Path | None:
    loops = repo / ".wringer" / "loops"
    if not loops.is_dir():
        return None
    candidates = [p for p in loops.iterdir() if p.is_dir()]
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def attempts_from_loop(repo: Path, loop_dir: Path | None) -> tuple[list[Attempt], bool]:
    """The verifications this loop ran, IN ORDER, or an unordered set.

    **Ruling 8.** The order comes from the loop's own `verify.finished` events,
    whose `evidence_dir` is required by `loop-event-v2.schema.json`. Sorting by
    id is forbidden and sorting by `started_at` alone is too: both tie at
    second precision, and in the probe's capture the truth and the lexical order
    disagreed.

    Returns `(attempts, ordered)`. When no loop bundle covers the runs, the
    caller must render them as a SET and use no "first"/"then"/"attempt N"
    language about them — which is what `ordered=False` says.
    """
    if loop_dir is None:
        return [], False
    ledger = loop_dir / EVENTS_FILENAME
    if not ledger.is_file():
        return [], False

    attempts: list[Attempt] = []
    for line in ledger.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") != "verify.finished":
            continue
        directory = event.get("evidence_dir")
        if not directory:
            continue
        path = repo / directory
        attempts.append(Attempt(
            run_id=Path(directory).name,
            directory=path,
            ordinal=len(attempts) + 1,
            passed=event.get("status") == "passed",
            failed_gate=event.get("failed_gate"),
        ))
    return attempts, bool(attempts)


def read_spec(repo: Path) -> tuple[str | None, str | None]:
    """The PM's own words — title and intent — out of `wringer.spec.yaml`.

    `acceptance.json` carries each criterion's id, title and `required`, but the
    spec's title and the intent live only here (probe gap 11). Parsed with a
    deliberately small reader rather than a YAML dependency: this layer reads
    two scalar fields and a block, and pulling a parser in to do it would be a
    second parser of a file the engine already owns.
    """
    path = repo / SPEC_FILENAME
    if not path.is_file():
        return None, None
    title = None
    intent_lines: list[str] = []
    in_intent = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if in_intent:
            if line.startswith((" ", "\t")) or not line.strip():
                intent_lines.append(line.strip())
                continue
            in_intent = False
        if line.startswith("title:"):
            title = line.split(":", 1)[1].strip()
        elif line.startswith("intent:"):
            in_intent = True
    intent = "\n".join(intent_lines).strip() or None
    return title, intent


def read(repo: Path) -> Board:
    """Everything one render needs. Raises `UnknownVersion` rather than guess."""
    repo = repo.resolve()
    board = Board(repo=repo)
    board.spec_title, board.spec_intent = read_spec(repo)
    board.loop_dir = latest_loop(repo)
    board.attempts, board.ordered = attempts_from_loop(repo, board.loop_dir)

    # The run the board describes: the LAST one the loop verified where a loop
    # exists, so the board and the loop agree about which run is "this run".
    board.run_dir = (
        board.attempts[-1].directory if board.attempts else latest_run(repo)
    )
    if board.run_dir is None or not board.run_dir.is_dir():
        board.refusal = (
            "There is no evidence here yet. Nothing has been verified in this "
            "repository, so there is nothing this board can honestly show."
        )
        return board

    accepted = _load(board.run_dir / ACCEPTANCE_FILENAME)
    if accepted is None:
        board.refusal = (
            "This run recorded no acceptance verdict, which means nobody has "
            "written down what the work is for. Wringer only judges criteria "
            "from an APPROVED spec; without one there is nothing to show per "
            "requirement."
        )
        return board

    version = accepted.get("schema_version")
    board.acceptance_version = version
    if version not in KNOWN_ACCEPTANCE:
        raise UnknownVersion(ACCEPTANCE_FILENAME, str(version), KNOWN_ACCEPTANCE)

    board.limits = list(accepted.get("limits") or [])
    for row in accepted.get("criteria") or []:
        board.criteria.append(Criterion(
            id=row.get("id") or row.get("criterion") or "?",
            title=row.get("title") or "",
            required=bool(row.get("required")),
            state=str(row.get("state") or ""),
            refuses=bool(row.get("refuses")),
            gate_id=row.get("gate"),
            command=row.get("command"),
            reason=str(row.get("reason") or ""),
            receipt=row.get("receipt"),
            # v1 has no such key, and `.get` returning None is exactly right:
            # "this run carried no witness lane" and "this criterion had no
            # witness" are the same fact from a card's point of view.
            witness=row.get("witness"),
        ))

    board.vacuity = _load(board.run_dir / VACUITY_FILENAME)

    # The gates this run was not asked to check. Read from the manifest rather
    # than inferred: a scoped run has its own honest sentence and ruling 4b
    # forbids inventing a cause for NOT REACHED.
    manifest = _load(board.run_dir / MANIFEST_FILENAME) or {}
    board.scoped_out = [
        gate for gate in (manifest.get("scoped_out") or []) if isinstance(gate, str)
    ]
    return board
