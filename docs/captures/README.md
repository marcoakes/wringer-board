# Captures — real pages, from real runs

**Not mock-ups.** Every file here was produced by `wringer-board render`
against bundles a real Wringer run wrote, and each is self-contained: open it
in a browser, no server and no network.

| file | what it shows |
|---|---|
| `board-corpus-2026-08-16.html` | **A winning row from the corpus re-test.** One requirement, DONE — AND PROVED, and the hero: *"It was red first. The repository had no check for this. Wringer wrote one before the work began, recorded it failing then, and the same check passes now."* The promise is EARNED and rendered |
| `board-uncovered-2026-08-16.html` | **The same board on a row where the witness evidenced nothing.** The criterion renders UNTRANSLATED with the engine's own words, and the promise is WITHHELD. This is the page a reader gets when the evidence is not there, and it is the more important of the two |

**Why the second file matters more.** A surface that only looks good on its
best day is a brochure. The withheld promise, the untranslated cause and the
absent hero box are what make the first page worth believing.

## What the winning page found in the board itself

The corpus bundles carry `receipt.kind: "witness"` — a **third** receipt kind.
`SPEC_BOARD_V0` ruling 5 enumerates `failure` and `sensitive`, because it was
written against `accept.py` at `d23d7ca` and `wringer.acceptance.v2` added the
third afterwards. Until that was fixed, the board met the strongest red-first
demonstration this programme has and rendered **UNKNOWN**, withholding the
promise. Honest, and wrong.

It now has its own sentence, because ruling 5's whole point is that different
facts get different words: a `failure` receipt says a repository's own check
has been recorded failing; a `sensitive` receipt says a check failed on the
code as it was; and this one says something neither can — **the check did not
exist until Wringer wrote it.**
