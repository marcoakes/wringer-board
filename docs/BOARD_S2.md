# S2 — refusal language: what landed, and what did NOT

*The capture for slice S2 of `SPEC_BOARD_V0.md`. The house does not claim
unfilmed work, so this file exists before the slice is called anything — and
this one is now called **LANDED**, having been **PART-LANDED** between
`31c28b8` and the commit that added this line. What was owed, who said so, and
what closed it are in the last section, quoted rather than deleted.*

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

## What the seven unrendered families needed, and how each one is read

**This section closes what the one below it recorded as owed.** Every value on
the page is a string the engine literally wrote in a file, and the file was
traced in the engine's source rather than guessed — which turned out to matter,
because two of the seven are in no file under `.wringer/` at all.

| family | the artifact, and the field | how the board gets there |
|---|---|---|
| loop endings | `.wringer/loops/<id>/manifest.json` → `result.reason` (`loop.py:300`) | the loop bundle the board already opens for ordering |
| vacuity verdicts | `<run bundle>/vacuity.json` → `verdict` (`evidence.py:95`) | already read; now translated instead of only counted |
| fleet outcomes | `.wringer/fleets/<id>/manifest.json` → `tasks[].status` (`fleet.py:36`) | the newest fleet bundle |
| health verdicts | **no file under `.wringer/`** — a derived view, printed by `wring health --json`, written only where `--output` names a path | `--health-report PATH` |
| signature · identity · integrity | **no file under `.wringer/`** — `sign.assess`'s three axes reach a consumer only through `wring audit --json` (`cli.py:3624`) | `--audit-report PATH` |

**The two "no file" rows are a finding, not a shortcut.** It is natural to
assume an `attestation.json` carries a signature verdict. It does not: its own
`signature` field is `null` in v0 by ruling, and `change.commit_signature.status`
is git's `%G?` letter — a different vocabulary from `sign.SIGNATURE_STATES`
entirely. The board therefore renders those three only from `wring audit`'s own
report, and **never assesses a signature itself**: concluding
`signature_missing` from a missing `.sig` would be this surface
re-implementing `sign.assess`, which ruling 1 forbids outright.

**Ruling 11 offered two mechanisms for health and one of them was refused.** It
allows either running `wring health --json` through the CLI-as-API, or
rendering nothing. The CLI-as-API branch is **not built**: this package has no
runtime dependency on the engine, and a renderer that shells out mid-render
makes the page a function of the machine rather than of bytes on disk. The
narrowing is real and is stated rather than smoothed — where nobody hands the
board a report, it says nothing about health, which is ruling 11's own other
branch.

### Absence is not a verdict, and that is the test that matters

Ruling 11 governed vacuity and health. It is widened here to all seven: **an
artifact that is not there produces no line at all.** No attestation report,
and the page says nothing about signature, identity or integrity — it does not
say "unsigned". No fleet manifest, and nothing about fleet outcomes.

*A missing artifact and a bad verdict are different facts, and rendering one as
the other is the exact defect class this project exists to catch.* The
temptation is one line of code away in every one of these families, and
`signature_missing` is the most tempting of all because its sentence is
reassuring and would therefore be believed.

So the guard is `test_a_missing_artifact_renders_NOTHING_about_its_family`,
which walks **every value of all seven families** and asserts its sentence is
absent from a page whose artifacts are absent — and its twin,
`test_an_artifact_appearing_LATER_starts_being_rendered`, without which
deleting the whole feature would pass. Both were watched to fail: the mutation
was a missing audit report defaulting to the ordinary local answer, which is
precisely the helpful line a future slice would add.

### An artifact present in an unknown version is not parsed, and is not silent

Ruling 6's rule, applied to the artifacts ruling 6 predates. A version off the
known list gets no best-effort parsing, because the board cannot know where a
later schema put the field. So the PM section stays silent — and the artifact
is named in the collapsed engineers' block, because **silence in both places
would make an unreadable artifact indistinguishable from an absent one**, which
is the distinction this whole slice is about.

Both loop-manifest versions are read: `wringer.loop.v1` froze `reason` as a
closed six-value enum and v2 opened it to a string, both put it at
`result.reason`, and **the real bundles on disk are v1** — a board that knew
only the version the current engine writes could not read the runs that exist.

### Ruling 17 has one implementation, not two

An unmapped value in the round section lands in the same UNTRANSLATED block a
card uses, from the same function, with the engine's word verbatim. That is not
tidiness: a second copy is how one of the two paths quietly stops being
verbatim, and `test_the_untranslated_block_is_ONE_mechanism_shared_with_the_cards`
fails if a second one appears.

**This is a shipped possibility rather than a hypothetical.**
`loop-manifest-v2`'s `reason` is deliberately an open string, so a stop reason
this table has never heard of costs no schema version and can arrive at any
time.

### The section says nothing of its own

Every sentence in it comes from `refusals.say` and nowhere else — the function
that renders it contains no wording but its heading. That is what keeps
`test_no_surface_string_claims_a_wrong_fix_was_caught` and
`test_no_rendered_string_uses_house_jargon` exhaustive over this surface: they
run over the mapping, and the mapping is all this section can say.
`test_this_section_says_NOTHING_that_is_not_in_the_mapping` pins it over the
rendered text rather than over the source, and reddens on a single friendly
sentence added to `render.py`.

## What did NOT land, and what has changed since

**Reversed in the open, because a reversed status stated quietly is the defect
this repository exists to catch.** Between `31c28b8` and this commit, this
section read:

> **The mapping is total; the RENDERING of seven of its ten families is not
> wired.** […] Loop endings, vacuity verdicts, health verdicts, signature,
> identity, integrity and fleet outcomes are **mapped and unrendered** — the
> sentences exist and are guarded, and no page yet shows them.
>
> So §9's capture column for S2 asks for *"one board per family showing a real
> refusal in PM language"* and **this slice does not produce it.** […] What the
> next slice owes: wiring the seven families into the page, and the per-family
> capture.

**Both debts are now paid.** All seven render, each from the artifact named in
the table above, and §9's capture column exists: seven pages under
`docs/captures/`, one per family plus one showing an unmapped value in the
UNTRANSLATED state, **and every value on them but one came from a real run** —
a real loop, a real pre-change comparison, a real health report, a real fleet,
a real audit, and a real tamper detected by `wring audit`. The one fixture is
the unmapped stop reason, labelled as a fixture on its own row, because no real
run has produced one.

**Still not done, and it still belongs to the engine rather than here:** twenty
of delivery's twenty-three refusals have no names. Checked at core `babc10b`
rather than assumed — `deliver.REFUSAL_REASONS` does not exist, and
`deliver.py` still raises `Refused` at 23 sites as prose with an exit code and
no enum. `SPEC_REFUSAL_V0.md` in the core repository specifies naming all
twenty-three and remains **authored, unreviewed and unbuilt**, so this table
does not invent the names it would create. Inventing them here would be the
surface deciding what the engine says, which ruling 1 forbids outright.

**And the delivery family reaches no page, which is a fact about the engine and
not a gap in this slice.** A refused delivery writes no manifest at all
(ruling 19, `BOARD_PROBE.md` gap 10), so there is no artifact for the board to
read — the three named delivery refusals are translatable and unreachable. Nine
of ten families now render; the tenth needs an engine change, not a surface
one.

**One thing this slice deliberately did not widen to.** Ruling 16 gives every
value a sentence *and* an unblocking question, and **nothing on this surface
renders the question** — not the new section, and not the criterion cards,
which have never rendered it. Half the mapping is written, guarded by the
totality test, and read by nobody. Wiring it changes the card layout as well as
this section, so it is recorded here rather than done quietly on the way past.
