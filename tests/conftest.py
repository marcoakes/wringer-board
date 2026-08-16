"""Fixtures that build a repository the way the ENGINE writes one.

Hand-built rather than produced by running Wringer, and the trade is stated
rather than hidden: these fixtures are a second copy of the engine's output
shape, which is exactly the drift ruling 1 exists to refuse — so the real
guard is not here. It is `test_real_bundles.py`, which renders the bundles a
REAL corpus run wrote and fails if this board cannot read them. These fixtures
exist to reach the shapes a real run does not conveniently produce on demand:
a broken receipt chain, an unknown schema version, a born-green criterion.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    (tmp_path / ".wringer" / "runs").mkdir(parents=True)
    (tmp_path / ".wringer" / "loops").mkdir(parents=True)
    (tmp_path / "wringer.spec.yaml").write_text(
        "schema_version: wringer.spec.v1\n"
        "approved: true\n"
        "title: Weekly reports go out on time\n"
        "intent: |\n"
        "  Finance needs the weekly figures as a file they can open in a\n"
        "  spreadsheet, without asking anyone.\n",
        encoding="utf-8",
    )
    return tmp_path


def write_run(
    repo: Path,
    run_id: str,
    criteria: list[dict],
    *,
    version: str = "wringer.acceptance.v1",
    limits: list[str] | None = None,
    gates: dict[str, tuple[str, str]] | None = None,
    scoped_out: list[str] | None = None,
) -> Path:
    """One verify bundle, in the shape `accept.write` produces."""
    run = repo / ".wringer" / "runs" / run_id
    run.mkdir(parents=True, exist_ok=True)
    (run / "acceptance.json").write_text(
        json.dumps({
            "schema_version": version,
            "criteria": criteria,
            "limits": limits or [
                "A gate passing says the gate passed. It does not say the "
                "criterion is met in every case the criterion could describe.",
            ],
        }, indent=2),
        encoding="utf-8",
    )
    (run / "manifest.json").write_text(
        json.dumps({"schema_version": "wringer.evidence.v1",
                    "scoped_out": scoped_out or []}),
        encoding="utf-8",
    )
    for index, (gate_id, (stream, text)) in enumerate(sorted((gates or {}).items())):
        directory = run / "gates" / f"{index:03d}_{gate_id}"
        directory.mkdir(parents=True, exist_ok=True)
        (directory / f"{stream}.log").write_text(text, encoding="utf-8")
        (directory / "result.json").write_text(
            json.dumps({"gate": gate_id, "status": "failed"}), encoding="utf-8"
        )
    return run


def write_loop(repo: Path, loop_id: str, run_ids: list[str]) -> Path:
    """A loop ledger whose `verify.finished` events order the runs.

    Ruling 8: the order comes from HERE and never from the ids, which are
    `<date>-<HHMMSS>-<4 hex>` and do not sort chronologically.
    """
    loop = repo / ".wringer" / "loops" / loop_id
    loop.mkdir(parents=True, exist_ok=True)
    lines = [
        json.dumps({
            "type": "verify.finished",
            "iteration": index + 1,
            "status": "failed",
            "evidence_dir": f".wringer/runs/{run_id}",
        })
        for index, run_id in enumerate(run_ids)
    ]
    (loop / "loop.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return loop


def criterion(
    cid: str,
    title: str,
    state: str,
    *,
    required: bool = True,
    refuses: bool = False,
    gate: str | None = "suite",
    reason: str = "",
    receipt: dict | None = None,
    witness: dict | None = None,
) -> dict:
    row = {
        "id": cid, "title": title, "required": required, "state": state,
        "gate": gate, "command": "pytest -q", "refuses": refuses,
        "reason": reason, "receipt": receipt,
    }
    if witness is not None:
        row["witness"] = witness
    return row
