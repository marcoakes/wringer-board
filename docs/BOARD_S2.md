# S2 — refusal language: what landed, and what did NOT

*The capture for slice S2 of `SPEC_BOARD_V0.md`. The house does not claim
unfilmed work, so this file exists before the slice is called anything — and
this one is called **PART-LANDED**, for the reason in the last section.*

## What landed

### The mapping is total, and totality is forced two ways

`src/wringer_board/refusals.py` holds one table: `(family, value) → (sentence,
question)`, over **ten families** — the eight of ruling 16, plus
`unevidenced`'s causes as a family of their own, plus the three delivery
refusals that are reachable from an artifact.

Totality is a chain of two links, and **neither link is allowed to be the only
one**:

| link | what it checks | when it runs |
|---|---|---|
| `test_the_mapping_covers_exactly_these_and_nothing_else` | the mapping against a written-down list of the engine's values, **set equality in both directions** | always |
| `test_these_are_the_engines_own_values` | that written-down list against the engine's own frozen schemas and public tuples, both directions | wherever `wringer` is importable — which is here |

A missing entry is a value a PM would meet as an untranslated string. **An
extra entry is dead text that reads as coverage**, which is why the assertion
is equality rather than a subset.

Five families are derived from **frozen schemas** — the strongest source in
this project, because `schema/frozen.json` byte-freezes them and a change
without a new version reddens the core's own suite. Three come from public
module symbols, which is what ruling 16 requires.

### The integrity exemption is discharged

Ruling 16 granted the two integrity values a hand-listed per-value exemption,
on the stated grounds that **"no collection and no schema enum exists"**. A
collection exists now — `sign.INTEGRITY_STATES`, landed at `ab884b5` — so they
are enumerated like their two siblings and **the exemption is removed rather
than left as a comment nobody re-reads.** The rationale expired; the exemption
went with it.

### The fifth cause is named, and the S1 assertion was flipped in the open

Ruling 15 enumerated **four** causes of `unevidenced` from `accept.py` at
`d23d7ca`. The witness lane added a fifth, and S1 met it **on real data** —
`test_real_bundles.py` rendered the corpus bundles, found a reason the mapping
did not cover, asserted it rendered UNTRANSLATED, and wrote in its own
docstring: *"Naming it a fifth cause with its own sentence is S2's job, not
S1's."*

S2 named it `witness-evidenced-nothing`, gave it a sentence, and **flipped that
S1 assertion in the same commit that did the naming**, citing the docstring as
the authority. The old expectation is quoted in the new test rather than
deleted. A pinned assertion is a record of a decision, and reversing one
silently is the defect this repository exists to catch.

One rename rode along: `never-recorded-failing` became `born-green`, the name
`accept.py` and ruling 15 both already used. Two names for one cause is how a
mapping stops being checkable.

**Order in the matcher is load-bearing and is commented as such.** The witness
cause is a `gate: null` row, so a structural unbound check placed first would
swallow it — which is precisely how a fifth cause hides inside a fourth.

### The two greps now run over the whole string table

S1's versions render one repository and grep the HTML, so they reach only the
strings that fixture happens to produce. S2's run over **every string this
surface can say**: every sentence and question in the mapping, plus every
string literal in `cards.py`.

Two categories are excluded, and the exclusion is **itself guarded** by
`test_the_excluded_strings_are_only_matchers_and_keys`: the `reason` regexes,
which must contain the engine's vocabulary in order to match it, and the cause
names, which are dictionary keys that `render.py` never writes. Forbidding the
word "witness" in a pattern that must match `accept.py`'s own sentence would
stop the board recognising the cause at all, while what the rule protects —
what a PM reads — is untouched.

Both greps were **watched to fail** before this was written: a jargon word
added to a rendered sentence, and a sentence claiming to guarantee
correctness. So were both totality links: a removed mapping entry, and a
written-down list edited to disagree with the engine.

### The claim ceiling, unchanged

*A witness proves the stated criterion could fail and was made to pass; it does
not certify agreement with an unstated intended fix, and where the criterion
under-describes the intent, the witness inherits that gap.* Nothing in the
mapping claims otherwise, and the grep over the whole table is what says so
rather than a reading.

## What did NOT land, and why this slice is PART-LANDED

**The mapping is total; the RENDERING of seven of its ten families is not
wired.** `render.py` writes criterion cards, so the criterion states, the five
`unevidenced` causes and the UNTRANSLATED path all reach a page today. Loop
endings, vacuity verdicts, health verdicts, signature, identity, integrity and
fleet outcomes are **mapped and unrendered** — the sentences exist and are
guarded, and no page yet shows them.

So §9's capture column for S2 asks for *"one board per family showing a real
refusal in PM language"* and **this slice does not produce it.** That is stated
here rather than quietly narrowed, because a mapping that is total over a
vocabulary nobody renders is exactly the shape that reads as finished and is
not.

What is genuinely finished and can be relied on by the next slice: the table,
its totality in both directions against the engine, the fifth cause, and the
two exhaustive greps. What the next slice owes: wiring the seven families into
the page, and the per-family capture.

**Also not done, and it belongs to the engine rather than here:** twenty of
delivery's twenty-three refusals still have no names, so they render
UNTRANSLATED with the engine's own words. `SPEC_REFUSAL_V0.md` in the core
repository specifies naming all twenty-three; as of 2026-08-16 it is
**authored, unreviewed and unbuilt**, and this table does not invent the names
it would create. Inventing them here would be the surface deciding what the
engine says, which ruling 1 forbids outright.
