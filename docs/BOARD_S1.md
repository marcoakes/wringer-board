# S1 — what was built, and what it is allowed to say

*The capture for slice S1 of `SPEC_BOARD_V0.md`. The house does not claim
unfilmed work, so this file exists before the slice is called done.*

## What it is

`wringer-board render <repo> -o board.html` reads the evidence Wringer already
wrote under `.wringer/` and produces one self-contained HTML file. No server,
no network, no account, no dependency beyond the standard library.

## What it renders, per §3

| ruling | what it means here |
|---|---|
| 1 | the surface RENDERS and never decides. Three computed things, all named in the spec: the receipt chain walk, the four causes of `unevidenced`, and the earned/withheld promise. `accept.py` is never re-implemented and nothing is scored |
| 4 | six card states, in the order the approved spec declares the criteria — **never sorted by state**, which would be the surface deciding which debts matter |
| 4a | **REFUSED is a badge, not a state.** `refuses` is true for any criterion that is required and covered and not evidenced, so a NOT YET card, a NOT REACHED card and a bound NEEDS YOU card are all simultaneously refusing rows. It is also the honest model: it is the delivery that was refused, not the criterion |
| 4b | NOT REACHED asserts no cause it cannot support. A scoped run gets its own sentence, read from the manifest rather than inferred |
| 5 | **both receipt kinds**, resolving differently and saying different sentences. A `failure` receipt says *this check has been recorded failing*; a `sensitive` receipt says *this check failed on the code as it was before this change*. The promise is computed over CLAIMS: a row that claims `evidenced` and cannot resolve VETOES it, whatever the card renders |
| 6 | an unknown schema version renders **zero cards** and exits non-zero |
| 7 | plain language, with two deliberate exceptions on the card: the message the check printed, verbatim in a block attributed to the check, and the attempt ordinal |
| 8 | order from the loop's `verify.finished` events. Never from run ids, which are `<date>-<HHMMSS>-<4 hex>` and do not sort chronologically |
| 9 | the limits render **verbatim**, in the engine's own voice |
| 15 | `unevidenced`'s four causes, never rendered as one another, each pinned by a fixture test |
| 17 | an unmapped reason renders inside a visible UNTRANSLATED state, with the engine's words |
| 18 | no dismiss, no snooze, no "proceed anyway", and no code path that catches a refusal and continues |

## The one amendment this slice makes, dated

**Ruling 6 named `wringer.acceptance.v1` alone**, because v2 did not exist when
the spec was written. A run carrying a witness lane writes
`wringer.acceptance.v2`, and the corpus re-test — the run this board's first
real render is built from — is exactly such a run. A board that knew only v1
could not render the artifact it was commissioned to show.

v2 is a superset in the only two ways that reach this layer: a row gains an
optional `witness` object, and `gate` may be null on a row that still
`refuses`. Both are handled explicitly. **The rule ruling 6 actually states is
unchanged**: anything off the known list produces a banner naming the version
and no cards at all.

## What it will not do (§8, binding)

No live preview, no hosting, no auth, no multi-user, no sync, no server. No
multi-repo. **No weakening of a refusal** in any form. No 20th `wring` command
— this is not a subcommand. No translation of `limits[]` into PM language: a
translated limit is a weakened limit unless the translation is guarded, and
that guard is a cycle. No PROVEN-RED card. No judge, score, ranking or quality
verdict. No writing into `.wringer/`. No editing a gate, a gate command or a
`proves:` binding — editing a command resets the criterion's discrimination
history, and a surface that could do it silently would destroy evidence by
clicking.

## The ceiling, and it is a test

`test_no_rendered_string_claims_a_wrong_fix_was_caught` greps the whole
rendered page. **Nothing here may claim the check catches wrong fixes.** A
witness proves the stated criterion could fail and was made to pass; it does
not certify agreement with an unstated intended fix, and where the criterion
under-describes the intent, the witness inherits that gap.

## What is NOT done in S1

- **Demo R** and the quickstart number belong to the launch cycle, not this
  window, and are not built.
- S2's total refusal-language mapping, S3's interview surface and S4's engine
  artifact slot are later slices.
- The **cold-read** — the page handed to someone with no Wringer context, and
  what they said — is a capture S1 owes and that only a person can produce.
