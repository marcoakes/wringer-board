---
title: wringer-board
---

# wringer-board

**One page that tells you what is actually done — and shows you the proof.**

Real pages sit beside this one, produced by `wringer-board render` against
bundles a real [Wringer](https://github.com/marcoakes/wringer) run wrote. None
is a mock-up. These two lead because they are the two that sell; **seven more,
[one per kind of refusal the engine can raise](captures/), landed with slice
S2** and every value on them but one came from a real run.

- **[A requirement that is done, and proved](captures/board-corpus-2026-08-16.html)**
  — from the corpus re-test of 2026-08-16. One card, DONE — AND PROVED, and the
  hero: *"It was red first. The repository had no check for this. Wringer wrote
  one before the work began, recorded it failing then, and the same check passes
  now."* The promise is earned, so it renders.

![A board page: one card reading DONE — AND PROVED, above it the earned promise that every requirement marked done on this page was demonstrated able to FAIL before it was made to pass, and inside the card a red-bordered box reading "It was red first."](captures/board-corpus-2026-08-16.png)

- **[The same board when the evidence is not there](captures/board-uncovered-2026-08-16.html)**
  — the promise **withheld**, the cause rendered in the engine's own words
  because this board has no plain-English wording for it yet, and no hero box.

![The same board with the evidence missing: a grey box saying the page does not claim that every requirement marked done was demonstrated able to fail first, a card badged UNTRANSLATED, and Wringer's own words quoted verbatim in a monospace block headed "Wringer said, and this board has no plain-English wording for it yet".](captures/board-uncovered-2026-08-16.png)

**The second page is the more important one.** A surface that only looks good on
its best day is a brochure. These two were published together, on a day the
programme's headline claim was
[withdrawn after losing its own pre-registered test](https://github.com/marcoakes/wringer/blob/main/docs/corpus-2026-08-16.md).

## What happened in the round, family by family

The two pages above are about *requirements*. A run also produces facts that
belong to no single requirement — how the loop ended, whether the checks were
shown to be capable of failing, what `wring audit` made of the signature. Slice
S2 gives each of those a sentence a PM can read, and these are one page per
family, so the wording can be judged rather than described:

- **[How the loop ended](captures/board-loop-ending-2026-08-16.html)**
- **[Whether the checks could have failed](captures/board-vacuity-2026-08-16.html)**
- **[Whether a check has stopped being able to fail](captures/board-health-2026-08-16.html)**
- **[Signature, identity and integrity](captures/board-audit-axes-2026-08-16.html)** — as `wring audit` reported them; this board does not assess them itself
- **[When the record has been altered](captures/board-integrity-broken-2026-08-16.html)**
- **[How a fleet of tasks came out](captures/board-fleet-2026-08-16.html)**
- **[A word this board has no wording for yet](captures/board-untranslated-ending-2026-08-16.html)** — shown in the engine's own words rather than hidden

**Absence is not on this list, and that is the point.** Where an artifact was
never written, the page says nothing about that family — it does not say
"unsigned", "unhealthy" or "not measured by us". A missing measurement and a
bad verdict are different facts, and rendering one as the other is the failure
this whole layer exists to avoid.

## The ceiling, said here rather than buried

A check that was demonstrated able to fail, and then made to pass, is real
evidence and much better than a check that has only ever been green. **It is not
a guarantee that the work is right.** Where a requirement was written vaguely,
the check inherits that vagueness — and the run these pages come from measured
exactly that, twice in each direction.
