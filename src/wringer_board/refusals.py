"""Plain language for every named thing the engine can say. SPEC_BOARD_V0 §4.

**Ruling 16 — the mapping is total, keyed on `(family, value)`, and totality is
forced by a test.** Every named value the shipped engine can emit gets exactly
one PM sentence and exactly one unblocking question. The key is a pair and not
a bare value because `unevidenced` alone has five causes, and one sentence for
five facts is precisely the collapse ruling 15 exists to prevent.

**Ruling 17 — an unmapped value renders UNTRANSLATED**, with the engine's own
words, verbatim. Never invisibly, never swallowed, never best-effort
prettified: *a PM seeing an ugly string files a bug report; a PM seeing nothing
has been lied to.*

**Ruling 18 — this file translates and never negotiates.** There is no entry
here that softens a refusal, no "proceed anyway", and no value whose sentence
tells a reader the thing did not matter. A refusal rendered in plain language
is still a refusal.

**The unblocking question is one question.** Not a list, not a diagnosis, and
never a command to run — the board is read by someone who does not use a
terminal. Where the honest answer is that only an engineer can move it, the
question says so rather than inventing an action for the reader.

## Where these values come from, and the one honest weakness

Five families are enumerable from FROZEN SCHEMAS, which is the strongest source
this project has — a schema is a published contract and `schema/frozen.json`
byte-freezes it. Three are enumerable only from public module symbols
(`graph.LOOP_REASONS`, `sign.SIGNATURE_STATES`, `sign.IDENTITY_STATES`,
`sign.INTEGRITY_STATES`).

This package has **no runtime dependency on `wringer`** and will not gain one:
B1's structural test asserts the surface ships nothing it does not need, and a
renderer that cannot run without the engine installed is a worse product. So
the values are written down here, and `tests/test_refusals.py` cross-checks
every one of them against the engine's own symbols and schemas **whenever the
engine is importable** — which it is wherever this is developed or its CI runs.

The weakness, stated rather than hidden: on a machine with no `wringer`
installed, that cross-check cannot run, and this file is then a hand-kept list.
The test says so out loud instead of skipping quietly, because a guard that
goes silent is how the last three stale claims in this programme survived.

**`sign.INTEGRITY_STATES` is now a real tuple** (`ab884b5`), so the per-value
exemption ruling 16 granted the two integrity values — on the stated grounds
that no collection existed — is discharged. They are enumerated like their two
siblings and the exemption is gone rather than left as a comment.
"""

from __future__ import annotations

from dataclasses import dataclass

# --- families -------------------------------------------------------------

CRITERION_STATE = "criterion-state"
UNEVIDENCED_CAUSE = "unevidenced-cause"
LOOP_ENDING = "loop-ending"
VACUITY_VERDICT = "vacuity-verdict"
HEALTH_VERDICT = "health-verdict"
SIGNATURE = "signature"
IDENTITY = "identity"
INTEGRITY = "integrity"
FLEET_OUTCOME = "fleet-outcome"
DELIVERY_REFUSAL = "delivery-refusal"

FAMILIES = (
    CRITERION_STATE,
    UNEVIDENCED_CAUSE,
    LOOP_ENDING,
    VACUITY_VERDICT,
    HEALTH_VERDICT,
    SIGNATURE,
    IDENTITY,
    INTEGRITY,
    FLEET_OUTCOME,
    DELIVERY_REFUSAL,
)


@dataclass(frozen=True)
class Saying:
    """One sentence a PM reads, and the one question that unblocks it."""

    sentence: str
    question: str


# --- the mapping ----------------------------------------------------------
#
# Read it as a table, because that is what it is. Each row is the whole of what
# this board is permitted to say about that value.

MAPPING: dict[tuple[str, str], Saying] = {
    # Criterion states. `schema/acceptance.schema.json`'s enum, five values.
    (CRITERION_STATE, "evidenced"): Saying(
        "This is done, and the same check that passes now is on the record "
        "having failed before the work.",
        "Nothing is needed from you on this one.",
    ),
    (CRITERION_STATE, "gate-failed"): Saying(
        "Not done yet — the check that decides it is written and is failing "
        "right now.",
        "Nothing is needed from you yet; this is what work in progress looks "
        "like.",
    ),
    (CRITERION_STATE, "gate-did-not-run"): Saying(
        "This was not checked in this run, so nothing here says anything "
        "about it either way.",
        "Was this requirement meant to be part of this round of work?",
    ),
    (CRITERION_STATE, "human"): Saying(
        "A person has to decide this one. Nothing automatic can, and Wringer "
        "will not pretend otherwise.",
        "Is this requirement met? Only you can answer it.",
    ),
    (CRITERION_STATE, "unevidenced"): Saying(
        "Something is done or claimed here that cannot be proved from what is "
        "on record.",
        "See the specific reason on the card — the five reasons are not "
        "interchangeable.",
    ),
    # `unevidenced`'s causes. FIVE, not four. Ruling 15 enumerated four from
    # `accept.py` at `d23d7ca`; the witness lane added the second row below and
    # S1's real-bundle tests found it on real data rather than by reading.
    (UNEVIDENCED_CAUSE, "unbound"): Saying(
        "Nothing checks this yet, so nobody can prove it either way.",
        "Which check should decide this requirement?",
    ),
    (UNEVIDENCED_CAUSE, "witness-evidenced-nothing"): Saying(
        "Nothing in this repository checks this requirement, so Wringer wrote "
        "a check for it — and that check turned out to prove nothing, so it "
        "was thrown away rather than counted.",
        "Which check should decide this requirement?",
    ),
    (UNEVIDENCED_CAUSE, "born-green"): Saying(
        "The check passes, but it has never been recorded failing — so its "
        "passing proves nothing yet.",
        "Nothing is needed from you; this one needs a check that has been seen "
        "to fail.",
    ),
    (UNEVIDENCED_CAUSE, "pre-existence-unestablished"): Saying(
        "The check passes, but this run could not establish that the check "
        "existed before the change it is judging.",
        "Nothing is needed from you; an engineer has to make that provable.",
    ),
    (UNEVIDENCED_CAUSE, "arrived-with-the-work"): Saying(
        "A new check cannot vouch for the work that brought it. This check was "
        "created by the same change it judges.",
        "Nothing is needed from you; the check has to exist before the work "
        "that it judges.",
    ),
    # **The three HUMAN causes** — `wringer.acceptance.v3`. The engine's
    # `cause` is ONE closed enum of eight spanning `unevidenced` and `human`
    # rows, so they live in this family rather than a second one; a separate
    # vocabulary would mean the board could not render half of it.
    #
    # These are the cards the PM product exists for. Every other sentence here
    # tells a PM what a machine found; these three tell them the machine has
    # stopped and is waiting for THEM.
    (UNEVIDENCED_CAUSE, "human-unanswered"): Saying(
        "No check can decide this one — it needs a person to look and say. "
        "Nobody has yet.",
        "Is this requirement met? Only you can answer it.",
    ),
    (UNEVIDENCED_CAUSE, "human-said-no"): Saying(
        "A person looked at this and said it is not met. Nothing here can "
        "overrule that, and nothing tried to.",
        "What would have to change for you to call this met?",
    ),
    (UNEVIDENCED_CAUSE, "human-judgement-stale"): Saying(
        "Somebody answered this, but the requirement has been REWORDED since — "
        "so the answer was given to a different question.",
        "Does your earlier answer still hold for the requirement as it reads "
        "now?",
    ),
    # Loop endings. `graph.LOOP_REASONS`, NINE values.
    (LOOP_ENDING, "converged"): Saying(
        "The work finished: the checks it was asked to satisfy are passing.",
        "Nothing is needed from you on this one.",
    ),
    (LOOP_ENDING, "max_iterations"): Saying(
        "The work stopped because it had used up the number of attempts it "
        "was allowed, not because it was finished.",
        "Should this be given more attempts, or is something else wrong?",
    ),
    (LOOP_ENDING, "budget_exhausted"): Saying(
        "The work stopped because it reached the spending or time limit set "
        "for it, not because it was finished.",
        "Should this be given a larger budget, or is something else wrong?",
    ),
    (LOOP_ENDING, "no_progress"): Saying(
        "The work stopped because an attempt changed nothing at all. Running "
        "it again unchanged would not help.",
        "Nothing is needed from you; an engineer has to look at why it is "
        "stuck.",
    ),
    (LOOP_ENDING, "environment"): Saying(
        "The work never started: the very first check could not run at all, "
        "because the command it needs is not installed on the machine. No "
        "attempt was made and nothing was changed.",
        "Nothing is needed from you; the machine the work runs on has to be "
        "set up first.",
    ),
    (LOOP_ENDING, "oscillating"): Saying(
        "The work stopped because it kept hitting the same failure over and "
        "over, which means it is going round in circles rather than making "
        "progress.",
        "Nothing is needed from you; an engineer has to look at why it is "
        "stuck.",
    ),
    (LOOP_ENDING, "authority_moved"): Saying(
        "The work stopped because the requirements it was working from changed "
        "underneath it. It will not carry on against a question that moved.",
        "Did you mean to change the requirements while this was running?",
    ),
    (LOOP_ENDING, "flaky_gate"): Saying(
        "The work stopped because one of the checks gives different answers on "
        "the same code, so nothing it said could be trusted.",
        "Nothing is needed from you; a check that cannot make up its mind is "
        "an engineer's problem.",
    ),
    (LOOP_ENDING, "interrupted"): Saying(
        "The work was stopped part-way — by a person, or by the machine it was "
        "running on.",
        "Should this be started again?",
    ),
    # Vacuity verdicts. `schema/vacuity.schema.json`, four values.
    (VACUITY_VERDICT, "proven"): Saying(
        "The checks were tested against the code as it was before this change, "
        "and at least one of them noticed the difference. They are measuring "
        "something.",
        "Nothing is needed from you on this one.",
    ),
    (VACUITY_VERDICT, "gates_vacuous"): Saying(
        "Every check passed both before and after this change, so none of them "
        "noticed it. Passing here proves nothing about the work, and the "
        "handover is refused.",
        "Nothing is needed from you; this needs a check that can tell the "
        "difference.",
    ),
    (VACUITY_VERDICT, "not_applicable"): Saying(
        "There was nothing to compare against, so this question was not asked.",
        "Nothing is needed from you.",
    ),
    (VACUITY_VERDICT, "inconclusive"): Saying(
        "The comparison could not be completed, so this says nothing either "
        "way. It is not a pass.",
        "Nothing is needed from you; an engineer has to find out why it could "
        "not be run.",
    ),
    # Health verdicts. `schema/health-report.schema.json`, four values.
    (HEALTH_VERDICT, "alive"): Saying(
        "There is a record of this check failing at some point, so it is still "
        "capable of telling you something.",
        "Nothing is needed from you on this one.",
    ),
    (HEALTH_VERDICT, "zombie"): Saying(
        "This check has passed every time for a long run of attempts and there "
        "is no record of it ever failing. A check that never fails may have "
        "stopped testing anything.",
        "Nothing is needed from you; an engineer has to confirm this check can "
        "still fail.",
    ),
    (HEALTH_VERDICT, "untested"): Saying(
        "There is not enough history yet to say whether this check can fail.",
        "Nothing is needed from you.",
    ),
    (HEALTH_VERDICT, "retired"): Saying(
        "This check is no longer part of the set being run.",
        "Was this check meant to be switched off?",
    ),
    # Signature. `sign.SIGNATURE_STATES`, four values.
    (SIGNATURE, "signature_valid"): Saying(
        "This record carries a signature and it checks out.",
        "Nothing is needed from you on this one.",
    ),
    (SIGNATURE, "signature_invalid"): Saying(
        "This record carries a signature and it does NOT check out. Treat the "
        "record as unproven until somebody explains why.",
        "Nothing is needed from you; an engineer has to explain this one.",
    ),
    (SIGNATURE, "signature_missing"): Saying(
        "Nobody signed this record. That is the ordinary result for work done "
        "on somebody's own machine and it is not a failure.",
        "Nothing is needed from you.",
    ),
    (SIGNATURE, "signature_unverified"): Saying(
        "A signature is present and nothing checked it, so this says neither "
        "that it is good nor that it is bad.",
        "Nothing is needed from you.",
    ),
    # Identity. `sign.IDENTITY_STATES`, three values.
    (IDENTITY, "identity_trusted"): Saying(
        "The signature belongs to somebody this repository said in advance it "
        "would trust.",
        "Nothing is needed from you on this one.",
    ),
    (IDENTITY, "identity_untrusted"): Saying(
        "The signature belongs to somebody this repository did NOT say it "
        "would trust.",
        "Nothing is needed from you; an engineer has to explain this one.",
    ),
    (IDENTITY, "identity_unknown"): Saying(
        "This repository never wrote down whose signature it expects, so "
        "'signed by somebody' cannot become 'signed by the right somebody'.",
        "Nothing is needed from you.",
    ),
    # Integrity. `sign.INTEGRITY_STATES`, two values — and they are enumerated
    # now rather than exempted, because the tuple exists (`ab884b5`).
    (INTEGRITY, "integrity_valid"): Saying(
        "Every file behind this record is byte-for-byte what it was when it "
        "was written. Nothing has been altered since.",
        "Nothing is needed from you on this one.",
    ),
    (INTEGRITY, "integrity_invalid"): Saying(
        "At least one file behind this record has been altered since it was "
        "written. The evidence no longer matches what it claims.",
        "Nothing is needed from you; an engineer has to explain this one.",
    ),
    # Fleet task outcomes. `schema/fleet-manifest.schema.json`, three values.
    (FLEET_OUTCOME, "succeeded"): Saying(
        "This piece of work finished and its checks passed.",
        "Nothing is needed from you on this one.",
    ),
    (FLEET_OUTCOME, "failed"): Saying(
        "This piece of work ran and did not get its checks passing.",
        "Nothing is needed from you yet.",
    ),
    (FLEET_OUTCOME, "parked"): Saying(
        "This piece of work was set aside rather than finished or failed — it "
        "stopped needing something it did not have.",
        "Nothing is needed from you; an engineer has to look at what it was "
        "waiting for.",
    ),
    # Delivery refusals. **Only three of the engine's twenty-three are named
    # here, and that is the honest number, not an oversight.** `deliver.py`
    # raises its refusals as prose with an exit code and no reason enum, so
    # exactly three are reachable from an artifact this board can read
    # (SPEC_BOARD_V0 ruling 19). The other twenty render UNTRANSLATED with the
    # engine's own words, addressed to whoever runs the repository.
    #
    # `SPEC_REFUSAL_V0.md` (core repo) specifies naming all twenty-three. It is
    # UNREVIEWED and UNBUILT as of 2026-08-16, so this table does not pretend
    # its names exist yet — inventing them here would be this surface deciding
    # what the engine says, which ruling 1 forbids outright.
    (DELIVERY_REFUSAL, "acceptance"): Saying(
        "The handover is being held because at least one requirement cannot "
        "show its proof.",
        "See the cards above — each one that is holding this up says what it "
        "needs.",
    ),
    (DELIVERY_REFUSAL, "vacuity"): Saying(
        "The handover is being held because the checks did not notice this "
        "change at all, so their passing says nothing about it.",
        "Nothing is needed from you; this needs a check that can tell the "
        "difference.",
    ),
    (DELIVERY_REFUSAL, "staleness"): Saying(
        "The handover is being held because the requirements changed after "
        "this work was started, so it was judged against a different question "
        "from the one you are asking now.",
        "Did you mean to change the requirements while this was running?",
    ),
}


def say(family: str, value: str) -> Saying | None:
    """The sentence and question for a value, or None — never a guess.

    Returning None is what drives ruling 17's UNTRANSLATED state. There is
    deliberately no default, no nearest-match and no generic fallback sentence:
    a wrong plain-English sentence is worse than an ugly true one, because the
    reader cannot tell it is wrong.
    """
    return MAPPING.get((family, value))


def values_for(family: str) -> frozenset[str]:
    """Every value this board can translate in one family."""
    return frozenset(value for (f, value) in MAPPING if f == family)
