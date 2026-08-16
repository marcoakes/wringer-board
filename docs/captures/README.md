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

## The `.png` files, and what they are NOT

Each `.html` above has a `.png` beside it. **The HTML is the evidence; the PNG
is a convenience** — it exists so a reader who cannot open a local file still
sees the page, and so this repository can show the surface before it is
published anywhere.

Each PNG was produced by loading the committed `.html` from disk in headless
Chrome at a 1200px viewport and screenshotting it. **Nothing was styled,
cropped to flatter, re-rendered from different data, or assembled by hand**,
and the only parameter chosen was a window height that fits the content
without a band of empty page underneath it. Anyone can reproduce one:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --hide-scrollbars \
  --window-size=1200,1330 --default-background-color=FFFFFFFF \
  --screenshot=board-corpus-2026-08-16.png \
  file://$PWD/board-corpus-2026-08-16.html
```

If a PNG and its HTML ever disagree, **the HTML is right** and the PNG is
stale. That direction is the whole reason both are kept.

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
