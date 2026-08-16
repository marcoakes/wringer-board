"""One criterion → one card. SPEC_BOARD_V0 §3, rulings 4, 5 and 15.

Every state here is a function of bytes the engine wrote. The three computed
things are named in ruling 1 and two of them live in this file: the receipt
chain walk (ruling 5) and the discrimination of `unevidenced`'s four causes
(ruling 15). Nothing else is computed and nothing is scored.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from wringer_board.read import Board, Criterion

# The six card states. **REFUSED is not among them and that is ruling 4a**:
# `refuses` is true for any criterion that is required and covered and not
# evidenced, so a NOT YET card, a NOT REACHED card and a bound NEEDS YOU card
# are all simultaneously refusing rows. Six mutually exclusive states with no
# precedence rule would be a lie about the data. It is also the honest model:
# **it is the delivery that was refused, not the criterion.**
DONE = "DONE — AND PROVED"
NOT_YET = "NOT YET"
NOT_REACHED = "NOT REACHED"
NEEDS_YOU = "NEEDS YOU"
UNKNOWN = "UNKNOWN"
UNTRANSLATED = "UNTRANSLATED"

STATES = (DONE, NOT_YET, NOT_REACHED, NEEDS_YOU, UNKNOWN, UNTRANSLATED)

# Ruling 15's four causes of `unevidenced`, discriminated. **Only the first is
# structural** — `gate: null` — and the spec says so rather than pretending
# otherwise. The other three are told apart by matching the engine's own
# `reason` text, each pinned by a fixture test, so a wording change in
# `accept.py` fails loudly instead of silently re-labelling a card.
#
# A reason matching none of them renders UNTRANSLATED with the engine's words
# verbatim (ruling 17) — never the generic born-green sentence, which would be
# rendering one cause as another.
UNEVIDENCED_CAUSES: tuple[tuple[str, re.Pattern[str], str], ...] = (
    (
        "arrived-with-the-work",
        re.compile(r"arrived with the change|created by the same change|"
                   r"did not exist before", re.I),
        "A new check cannot vouch for the work that brought it. This check was "
        "created by the same change it judges.",
    ),
    (
        "never-recorded-failing",
        re.compile(r"never (been )?recorded failing|no record of (it|this gate) "
                   r"failing|born green|passed at its first", re.I),
        "The check passes, but it has never been recorded failing — so passing "
        "proves nothing yet.",
    ),
    (
        "pre-existence-unestablished",
        re.compile(r"could not (be )?establish|pre-change|sensitiv", re.I),
        "The check passes, but this run could not establish that the check "
        "existed before the change.",
    ),
)

UNBOUND = (
    "Nothing checks this yet, so nobody can prove it either way."
)


@dataclass
class Card:
    """What one criterion looks like on the board, and nothing more."""

    id: str
    title: str
    state: str
    sentence: str
    refused: bool = False
    # The check's OWN words, verbatim, in a visually distinct block attributed
    # to the check (ruling 7). Never paraphrased: the surface does not get to
    # improve a check's words, and this is the one place a machine's words earn
    # their seat on a PM's screen.
    check_said: str | None = None
    receipt: str | None = None
    engine_words: str | None = None
    cause: str | None = None


def _chain(board: Board, criterion: Criterion) -> tuple[bool, str | None, str | None]:
    """Walk the receipt to the failure it cites. Ruling 5.

    Returns `(resolved, what the card shows, the check's own words)`.

    **Two receipt kinds, resolving differently**, and the first draft of the
    probe handled only one — which would have rendered UNKNOWN for every
    criterion in any repository using `run.prove: true`, the mechanism the
    README's own objections block advertises.
    """
    receipt = criterion.receipt or {}
    kind = receipt.get("kind")
    cited = receipt.get("run") or receipt.get("bundle") or receipt.get("cites")
    if not kind:
        return False, None, None

    if kind == "failure":
        # The cited bundle's gate directory says `failed`, and its stderr is
        # what the check printed. That is the red, on the record.
        run = _cited_dir(board, receipt)
        if run is None:
            return False, None, None
        said = _gate_stderr(run, criterion.gate_id)
        return True, (
            "This check has been recorded failing — the run that failed it is "
            "in this repository's evidence."
        ), said

    if kind == "sensitive":
        # On the CHANGED tree the gate passed, so the gate directory's
        # `result.json` says `passed` and reading it would resolve nothing. The
        # failure is in the run's `vacuity/` — and the schema already carries
        # the citation line verbatim.
        cites = receipt.get("cites")
        if not cites:
            return False, None, None
        return True, (
            "This check failed on the code as it was BEFORE this change, and "
            "passes on it now."
        ), str(cites)

    return False, None, None


def _cited_dir(board: Board, receipt: dict[str, Any]) -> Path | None:
    for key in ("run", "bundle", "evidence_dir"):
        value = receipt.get(key)
        if not value:
            continue
        candidate = board.repo / str(value)
        if candidate.is_dir():
            return candidate
        candidate = board.repo / ".wringer" / "runs" / Path(str(value)).name
        if candidate.is_dir():
            return candidate
    return None


def _gate_stderr(run: Path, gate_id: str | None) -> str | None:
    """The message the check printed, verbatim, from the cited run."""
    if gate_id is None:
        return None
    for directory in sorted((run / "gates").glob(f"*_{gate_id}")):
        for name in ("stderr.log", "stdout.log"):
            path = directory / name
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="replace").strip()
            if text:
                return text[:600]
    return None


def _unevidenced(criterion: Criterion) -> tuple[str, str, str | None]:
    """Which of ruling 15's FOUR causes, and the sentence for it.

    Rendering the fourth as the second is false and backwards — the record
    *does* show the gate can fail; the objection is that the gate is new. It is
    also one of the three things the README advertises as breaking the
    circularity objection, so getting it wrong here contradicts the README two
    clicks away.
    """
    if criterion.gate_id is None and not (criterion.witness or {}).get("covers", True):
        return "unbound", UNBOUND, None
    if criterion.gate_id is None and criterion.witness is None:
        return "unbound", UNBOUND, None
    for name, pattern, sentence in UNEVIDENCED_CAUSES:
        if pattern.search(criterion.reason):
            return name, sentence, None
    # Ruling 17: never invisibly, never swallowed, never prettified. A PM
    # seeing an ugly string files a bug report; a PM seeing nothing has been
    # lied to.
    return "untranslated", "", criterion.reason


def card_for(board: Board, criterion: Criterion) -> Card:
    """One criterion, rendered — and never scored."""
    refused = criterion.refuses
    state = criterion.state

    if state == "evidenced":
        resolved, sentence, said = _chain(board, criterion)
        if not resolved:
            # **A row that CLAIMS evidenced and cannot resolve is UNKNOWN**, and
            # it vetoes the promise whatever it ends up rendering (ruling 5).
            # The probe's own implementation got this wrong: demoting the card
            # removed it from the set of greens and the promise then fired over
            # the survivors — a page reading "every green was red first" beside
            # a card that could not show its red.
            return Card(
                id=criterion.id, title=criterion.title, state=UNKNOWN,
                sentence=(
                    "This record says this requirement is proved, and the "
                    "proof it points at is not something this board could "
                    "follow. So it is showing nothing rather than something it "
                    "cannot stand behind."
                ),
                refused=refused,
            )
        return Card(
            id=criterion.id, title=criterion.title, state=DONE,
            sentence=sentence or "", refused=refused, receipt=sentence,
            check_said=said,
        )

    if state == "gate-failed":
        witness = criterion.witness or {}
        if witness.get("covers") or witness.get("proved_red") == "assertion":
            sentence = (
                "Not done yet — and the check that decides it was written "
                "BEFORE the work began, was recorded failing then, and is "
                "still failing now."
            )
        else:
            sentence = (
                "Not built yet — and the check that will decide it is written "
                "and failing right now."
            )
        return Card(
            id=criterion.id, title=criterion.title, state=NOT_YET,
            sentence=sentence, refused=refused,
            check_said=_gate_stderr(board.run_dir, criterion.gate_id)
            if board.run_dir else None,
        )

    if state == "gate-did-not-run":
        # **Ruling 4b: no cause this card cannot support.** The sentence is
        # `accept.py`'s own. A scoped run gets its own honest sentence, read
        # from the manifest rather than inferred.
        sentence = "Not checked in this run, so nothing here says anything about it."
        if board.scoped_out:
            sentence += (
                " This run was only asked to check some of the requirements."
            )
        return Card(
            id=criterion.id, title=criterion.title, state=NOT_REACHED,
            sentence=sentence, refused=refused,
        )

    if state == "human":
        return Card(
            id=criterion.id, title=criterion.title, state=NEEDS_YOU,
            sentence=(
                "A person has to decide this one. Nothing automatic can, and "
                "Wringer will not pretend otherwise."
            ),
            refused=refused,
        )

    if state == "unevidenced":
        cause, sentence, engine = _unevidenced(criterion)
        if cause == "untranslated":
            return Card(
                id=criterion.id, title=criterion.title, state=UNTRANSLATED,
                sentence="", refused=refused, engine_words=engine, cause=cause,
            )
        return Card(
            id=criterion.id, title=criterion.title, state=NEEDS_YOU,
            sentence=sentence, refused=refused, cause=cause,
        )

    return Card(
        id=criterion.id, title=criterion.title, state=UNKNOWN,
        sentence=(
            "This record says something this board does not understand, so it "
            "is showing nothing rather than something it cannot stand behind."
        ),
        refused=refused,
    )


def promise_earned(board: Board, cards: list[Card]) -> bool:
    """Whether "every green on this board was red first" may be rendered.

    **Computed over CLAIMS, not over survivors** (ruling 5). A row that claims
    `evidenced` and cannot resolve its receipt VETOES the promise, whatever the
    card ends up rendering. Demoting it to UNKNOWN and then firing the promise
    over what is left is the probe's own bug, and it produced a page reading
    "every green was red first" beside a card that could not show its red.
    """
    claimed = [c for c in board.criteria if c.state == "evidenced"]
    if not claimed:
        return False
    return all(_chain(board, criterion)[0] for criterion in claimed)
