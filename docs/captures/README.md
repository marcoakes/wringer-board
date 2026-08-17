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

## S2 — one page per family, and what is real on each

The two pages above are S1's, and they show the *criterion* families. S2's
mapping covers ten families and, until the commit that added the pages below,
**seven of them reached no page at all.** These are that column of §9's slice
plan: one board per family, in PM language, plus one showing a value the
mapping does not cover.

Every page here was produced by `build_captures.py` beside this file, through
the shipped renderer, over the artifacts in `inputs/`. **`inputs/` holds the
engine's own reports byte-for-byte**, so "this came from a real run" is
checkable rather than asserted.

| file | family | the value on it, and where it came from |
|---|---|---|
| `board-loop-ending-2026-08-16.html` | loop endings | `converged` — **real.** `wring run`, 2026-08-11, a loop that reached green in two attempts |
| `board-vacuity-2026-08-16.html` | vacuity verdicts | `proven` — **real.** `wring verify --prove` in that same loop: three checks failed on the pre-change tree, so they measure the change |
| `board-health-2026-08-16.html` | health verdicts | `alive`, `untested`, `retired` — **real**, three of the four in one report. `wring health --json --output`, 2026-08-16, over those bundles |
| `board-audit-axes-2026-08-16.html` | signature · identity · integrity | `signature_missing`, `identity_unknown`, `integrity_valid` — **real.** `wring audit --json` over an attestation built from those bundles. The ordinary local answer: intact, unsigned, nobody named in advance |
| `board-integrity-broken-2026-08-16.html` | integrity (and the absence rule) | `integrity_invalid` — **real**, from a real tamper: one byte appended to a file inside an attested bundle. **Read the round section twice**: it says nothing at all about signature, because the audit stopped at integrity and never reached a signature verdict |
| `board-fleet-2026-08-16.html` | fleet outcomes | `succeeded` — **real.** `wring fleet tasks.jsonl`, 2026-08-16 |
| `board-untranslated-ending-2026-08-16.html` | ruling 17, on this section | `the_worker_declined_to_comment` — **THE ONE FIXTURE on any page here.** No real run has ended for a reason this table does not know, and `loop-manifest-v2`'s `reason` is an open string, so the possibility is real and the example had to be invented. It is a fixture and is not presented as anything else |

**The criterion cards behind every round section are real** — a real approved
spec and a real `acceptance.json` from the same repository, which is why the
three DONE — AND PROVED cards look identical on all seven pages. Each page
carries only the one artifact its family needs, so the other six families
render *nothing*, which is the discipline these pages exist to show: **a
missing artifact and a bad verdict are different facts.**

**Why three families share two pages.** `wring audit --json` emits signature,
identity and integrity in one object. Splitting it into three files would mean
handing the renderer a report the engine never wrote, so the two real outcomes
are shown instead.

**The two S1 pages have no round section**, and that is correct rather than
stale: the bundles they were rendered from carry none of these artifacts, and
the section does not render when there is nothing in it — not even a heading.

## The `.png` files, and what they are NOT

Each `.html` above has a `.png` beside it. **The HTML is the evidence; the PNG
is a convenience** — it exists so a reader who cannot open a local file still
sees the page, and so a README, which renders images and not HTML, can show
the surface at all.

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
