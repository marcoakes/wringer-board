"""Build the S2 capture set: one board per family, from real engine output.

**Run it, do not hand-edit the pages it writes.** Every `board-*.html` beside
this file came out of the shipped renderer — `wringer_board.__main__.main`, the
same entry point a user runs — over the artifacts in `inputs/`. Nothing was
styled, cropped, re-rendered from different data or assembled by hand.

## What is real and what is not, stated once and precisely

`inputs/` holds the artifacts the round section reads, **byte-for-byte as the
engine wrote them**, and every value on the pages except one came from a real
run:

| input | who wrote it, and when |
|---|---|
| `loop-manifest.json` | `wring run` on 2026-08-11 — a real repair loop, converged |
| `vacuity.json` | `wring verify --prove` in that same loop |
| `health.json` | `wring health --json --output` over those bundles, 2026-08-16 |
| `fleet-manifest.json` | `wring fleet tasks.jsonl`, 2026-08-16 |
| `audit.json` | `wring audit --json` over an attestation `wring attest` built from those bundles, 2026-08-16 |
| `audit-tampered.json` | the same command after a byte was appended to a file inside an attested bundle — a real detection, not a hand-written verdict |
| `loop-manifest-unmapped.json` | **THE ONE FIXTURE.** No real run has produced a stop reason this table does not know, so the UNTRANSLATED page needs an invented ending. It is labelled a fixture on the page's own README row and nowhere presented as a real run |

The criterion cards behind the round section come from a real evidence bundle
in the repository that produced it (`REPO` below), which is a different project
and is not vendored here — so this script needs those bundles on disk to run.
The seven values themselves do not depend on that: they are pinned as literals
in `tests/test_round.py`, which fails if the board stops rendering any of them.

## Why signature, identity and integrity share pages

They come from one artifact and one command. `wring audit --json` emits all
three axes in one object, and splitting it into three files would mean handing
the renderer an engine report that the engine never wrote. The two audit pages
show the two real outcomes instead: an intact unsigned local attestation, and
a tampered bundle.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
INPUTS = HERE / "inputs"
sys.path.insert(0, str(HERE.parents[1] / "src"))

# The repository whose real bundles supply the criterion cards. Its evidence
# belongs to that project and is read, never copied into this one.
REPO = Path("/Users/marc/Claude/first-contact/demo-rehearsal")
ACCEPTANCE_RUN = "20260811-183109-5a78"   # carries acceptance.json, 3 evidenced
CITED_RUN = "20260811-183109-8a36"        # the failure one receipt cites

DATE = "2026-08-16"


def base(dest: Path) -> Path:
    """The real board, with NONE of the seven families' artifacts present.

    `vacuity.json` is left out of the copied bundles deliberately: each page
    carries the one artifact it is about, so the round section shows that
    family alone and the others demonstrate the absence discipline in the same
    breath. Removing an artifact is a legitimate state of a repository; no
    value on any page was altered.
    """
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(REPO / "wringer.spec.yaml", dest / "wringer.spec.yaml")
    for run in (CITED_RUN, ACCEPTANCE_RUN):
        shutil.copytree(REPO / ".wringer" / "runs" / run,
                        dest / ".wringer" / "runs" / run, dirs_exist_ok=True)
        (dest / ".wringer" / "runs" / run / "vacuity.json").unlink(missing_ok=True)
    # The board describes the newest run by DIRECTORY mtime where no loop
    # ledger orders them (ruling 8 — never by id), so the run carrying the
    # acceptance record is made the newest explicitly rather than by luck.
    import os
    import time

    os.utime(dest / ".wringer" / "runs" / ACCEPTANCE_RUN, (time.time(), time.time()))
    return dest


def loop_manifest(repo: Path, source: Path) -> None:
    payload = json.loads(source.read_text(encoding="utf-8"))
    loop = repo / ".wringer" / "loops" / payload["loop_id"]
    loop.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, loop / "manifest.json")


def fleet_manifest(repo: Path, source: Path) -> None:
    payload = json.loads(source.read_text(encoding="utf-8"))
    fleet = repo / ".wringer" / "fleets" / payload["fleet_id"]
    fleet.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, fleet / "manifest.json")


def build(work: Path) -> list[str]:
    from wringer_board.__main__ import main

    written: list[str] = []

    def render(name: str, repo: Path, *flags: str) -> None:
        out = HERE / f"board-{name}-{DATE}.html"
        code = main(["render", str(repo), "-o", str(out), *flags])
        if code != 0:
            raise SystemExit(f"{name}: the renderer refused (exit {code})")
        written.append(out.name)

    # 1. Loop endings — real, `converged`.
    repo = base(work / "loop-ending")
    loop_manifest(repo, INPUTS / "loop-manifest.json")
    render("loop-ending", repo)

    # 2. Vacuity verdicts — real, `proven`.
    repo = base(work / "vacuity")
    shutil.copy2(INPUTS / "vacuity.json",
                 repo / ".wringer" / "runs" / ACCEPTANCE_RUN / "vacuity.json")
    render("vacuity", repo)

    # 3. Health verdicts — real: alive, untested and retired all present.
    repo = base(work / "health")
    render("health", repo, "--health-report", str(INPUTS / "health.json"))

    # 4-6. The three audit axes — real, and the ordinary local answer.
    repo = base(work / "audit")
    render("audit-axes", repo, "--audit-report", str(INPUTS / "audit.json"))

    # 4-6 again, the other real outcome: a bundle that was altered after it was
    # written. **`signature` is absent from this report** — the audit stopped at
    # integrity and never reached a signature verdict — so the page says
    # nothing about signature. That is the absence discipline, on real data.
    repo = base(work / "audit-tampered")
    render("integrity-broken", repo,
           "--audit-report", str(INPUTS / "audit-tampered.json"))

    # 7. Fleet outcomes — real, one task, `succeeded`.
    repo = base(work / "fleet")
    fleet_manifest(repo, INPUTS / "fleet-manifest.json")
    render("fleet", repo)

    # 8. Ruling 17 on this section. THE ONE FIXTURE on these pages.
    repo = base(work / "untranslated")
    loop_manifest(repo, INPUTS / "loop-manifest-unmapped.json")
    render("untranslated-ending", repo)

    return written


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        for name in build(Path(tmp)):
            print(name)
