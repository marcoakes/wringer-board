"""Rendered against bundles a REAL Wringer run wrote, not fixtures.

`conftest.py` says why this file is the load-bearing one: the fixtures there
are a second copy of the engine's output shape, which is the drift ruling 1
exists to refuse. This file holds bytes the engine actually produced, so if the
engine's shape moves, this fails and the fixtures do not get to disagree
quietly.
"""

from __future__ import annotations

import json
from pathlib import Path

from wringer_board import cards, read as read_module, render as render_module

# **A real `wringer.acceptance.v2` row**, copied verbatim from the bundle a
# corpus re-validation wrote on 2026-08-16. Two things in it would have been
# got wrong by a fixture written from the spec alone, and both are here for
# that reason:
#
#   1. the id key is `criterion`, not `id`;
#   2. `witness.result` is the STRING `"not_run"`, not null, and the witness
#      object carries no `covers` key at all.
REAL_V2 = {
    "schema_version": "wringer.acceptance.v2",
    "counts": {"evidenced": 0, "unevidenced": 1, "gate-failed": 0,
               "gate-did-not-run": 0, "human": 0},
    "criteria": [{
        "criterion": "issue",
        "title": "`fields.Constant` with `required=True` raised a warning",
        "required": True,
        "state": "unevidenced",
        "gate": None,
        "command": None,
        "receipt": None,
        "reason": (
            "no gate proves this criterion, and its witness evidences nothing "
            "(the runner could not collect it (exit 2), so its red says "
            "nothing about the criterion) — a human decides"
        ),
        "refuses": False,
        "witness": {
            "pinned_sha256": "3343c99acd3d",
            "proved_red": "collection_error",
            "result": "not_run",
            "discarded": "the runner could not collect it (exit 2)",
        },
    }],
    "limits": [
        "A witness proves the stated criterion could fail and was made to "
        "pass. It does not certify agreement with an unstated intended fix.",
    ],
}


def _repo(tmp_path: Path) -> Path:
    run = tmp_path / ".wringer" / "runs" / "20260816-055805-a77a"
    run.mkdir(parents=True)
    (run / "acceptance.json").write_text(json.dumps(REAL_V2), encoding="utf-8")
    (run / "manifest.json").write_text(
        json.dumps({"schema_version": "wringer.evidence.v1"}), encoding="utf-8"
    )
    return tmp_path


def test_a_real_v2_bundle_renders_without_a_fixture_in_sight(tmp_path):
    """The id key is `criterion` and not `id`. A reader that assumed `id`
    would render every card as `?` — and every fixture in this suite would
    still have passed."""
    board = read_module.read(_repo(tmp_path))
    assert board.acceptance_version == "wringer.acceptance.v2"
    assert [c.id for c in board.criteria] == ["issue"]

    page = render_module.render(board)
    assert "fields.Constant" in page


def test_the_witness_lanes_own_unevidenced_cause_renders_UNTRANSLATED(tmp_path):
    """**A FIFTH cause, found on real data, and rendering it honestly.**

    Ruling 15 enumerated four `unevidenced` causes from `accept.py` as it stood
    at `d23d7ca`. The witness lane added another: *no gate proves this
    criterion, and its witness evidences nothing*. It is not any of the four —
    it is not unbound-with-nothing-else, not born green, not an unestablished
    pre-existence, and not a check that arrived with the work.

    So it renders UNTRANSLATED with the engine's own words, which is exactly
    what ruling 17 prescribes for a reason the mapping does not cover: *a PM
    seeing an ugly string files a bug report; a PM seeing nothing has been lied
    to.* Giving it the generic born-green sentence would be rendering one cause
    as another, which ruling 15 exists to forbid.

    **Naming it a fifth cause with its own sentence is S2's job**, not S1's.
    Recorded here so the next slice starts from a measured fact.
    """
    board = read_module.read(_repo(tmp_path))
    card = cards.card_for(board, board.criteria[0])

    assert card.state == cards.UNTRANSLATED
    assert "could not collect it" in (card.engine_words or "")

    page = render_module.render(board)
    assert "never been recorded failing" not in page, (
        "a cause the mapping does not cover was rendered as the generic "
        "born-green sentence — one cause shown as another"
    )


def test_the_promise_is_WITHHELD_on_a_run_that_evidenced_nothing(tmp_path):
    board = read_module.read(_repo(tmp_path))
    page = render_module.render(board)
    assert "does not claim that every requirement" in page
    assert "It was red first." not in page


def test_the_real_bundles_limits_render_verbatim(tmp_path):
    board = read_module.read(_repo(tmp_path))
    page = render_module.render(board)
    assert "does not certify agreement with an unstated intended fix" in page
