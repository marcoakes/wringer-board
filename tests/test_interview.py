"""S3 — the interview surface. SPEC_BOARD_V0 §5 ruling 20, and H-4's questions.

**The B5 test is byte equality**: drive the verb and the hand edit against the
same fixture and assert the resulting files are identical. That is why every
write here is a line edit rather than a YAML round-trip — a round-trip
reformats comments, key order and quoting, so it could not be byte-equal to
what a person would have typed, and the person's file is the artifact of
record.

The other half of this file is the set of things the surface must REFUSE.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from wringer_board import cards, interview, refusals
from wringer_board.__main__ import main
from wringer_board.read import Criterion

SPEC = """\
schema_version: wringer.spec.v1
approved: false
title: CSV export
intent: The reports page can export what it shows.
# A comment a person wrote. Nothing may reformat this file around it.
tasks:
  - id: build-export
    brief: Build the export endpoint
    objective: The reports page exports a CSV of what it shows.
criteria:
  - id: csv-downloads
    title: The export downloads a CSV
    required: true
  - id: copy-reads-well
    title: The copy reads the way our users speak
    required: true
    human: true
open_questions:
  - id: which-columns
    question: Which columns should the export contain?
    required: true
  - id: filename
    question: What should the file be called?
    required: false
"""

GATES = """\
schema_version: wringer.gatespec.v1
gates:
  - id: export
    run: "pytest -q tests/test_export.py"
    proves: csv-downloads
"""


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    (tmp_path / "wringer.spec.yaml").write_text(SPEC, encoding="utf-8")
    (tmp_path / "wringer.gates.yaml").write_text(GATES, encoding="utf-8")
    return tmp_path


# --- capability 1: the conversation ----------------------------------------


def test_the_button_and_the_hand_edit_produce_byte_identical_files(repo, tmp_path):
    """**THE B5 TEST.** Ruling 20's acceptance criterion, and the reason this
    surface writes line edits rather than round-tripping YAML."""
    interview.answer(repo, "which-columns", "The ones on screen, in that order.")

    by_hand = tmp_path / "hand"
    by_hand.mkdir()
    (by_hand / "wringer.spec.yaml").write_text(
        SPEC.replace(
            "  - id: which-columns\n"
            "    question: Which columns should the export contain?\n"
            "    required: true\n",
            "  - id: which-columns\n"
            "    question: Which columns should the export contain?\n"
            "    required: true\n"
            "    answer: The ones on screen, in that order.\n",
        ),
        encoding="utf-8",
    )

    assert (repo / "wringer.spec.yaml").read_bytes() == (
        by_hand / "wringer.spec.yaml"
    ).read_bytes()


def test_the_comment_and_everything_else_survive_untouched(repo):
    before = (repo / "wringer.spec.yaml").read_text(encoding="utf-8")
    interview.answer(repo, "filename", "export.csv")
    after = (repo / "wringer.spec.yaml").read_text(encoding="utf-8")

    assert "# A comment a person wrote." in after
    # Exactly one line added, and nothing else moved.
    assert after.count("\n") == before.count("\n") + 1
    for line in before.splitlines():
        assert line in after.splitlines(), line


def test_the_core_loader_reads_what_this_surface_wrote(repo):
    """The whole claim of capability 1: the answer lands in the shape the
    ENGINE's spec loader already reads. Checked against the real loader, not
    against this repository's idea of it."""
    spec = pytest.importorskip("wringer.spec")
    interview.answer(repo, "which-columns", "The ones on screen.")

    loaded = spec.load(repo / "wringer.spec.yaml")
    assert loaded.unanswered == (), [q.id for q in loaded.unanswered]
    answered = {q.id: q.answer for q in loaded.questions}
    assert answered["which-columns"] == "The ones on screen."


def test_an_empty_answer_is_refused(repo):
    with pytest.raises(interview.InterviewError, match="not an answer"):
        interview.answer(repo, "which-columns", "   ")


def test_it_refuses_to_overwrite_what_a_person_already_wrote(repo):
    interview.answer(repo, "which-columns", "The ones on screen.")
    with pytest.raises(interview.InterviewError, match="already answered"):
        interview.answer(repo, "which-columns", "Something else entirely.")
    assert "The ones on screen." in (repo / "wringer.spec.yaml").read_text()


def test_an_unknown_question_is_refused_and_names_the_known_ones(repo):
    with pytest.raises(interview.InterviewError, match="which-columns"):
        interview.answer(repo, "not-a-question", "x")


def test_an_answer_needing_quoting_round_trips(repo):
    """A colon in an answer is the first thing that breaks a naive line edit."""
    spec = pytest.importorskip("wringer.spec")
    text = "Order: the ones on screen, then # anything else"
    interview.answer(repo, "which-columns", text)
    loaded = spec.load(repo / "wringer.spec.yaml")
    assert {q.id: q.answer for q in loaded.questions}["which-columns"] == text


def test_a_task_id_is_never_mistaken_for_a_question_id(repo):
    """`tasks` and `open_questions` both have `- id:` entries. Writing an
    answer under a task would corrupt the spec silently."""
    with pytest.raises(interview.InterviewError, match="no open question"):
        interview.answer(repo, "build-export", "x")
    assert "answer:" not in (repo / "wringer.spec.yaml").read_text()


# --- capability 2: the plain-language plan ---------------------------------


def test_the_plan_says_what_will_be_built_and_how_each_piece_is_proved(repo):
    text = interview.plan(repo)
    assert "The reports page exports a CSV" in text
    # Bound: names the check, and says it must be seen to fail first.
    assert "`export`" in text and "seen to FAIL first" in text
    # Human: says a PERSON decides, and that no check will be written.
    assert "A PERSON decides this" in text
    # Still-open questions are shown, with the refusal they will cause.
    assert "which-columns" in text and "will refuse" in text
    # And the limit that stops a PM approving the wrong thing confidently.
    assert "never its wisdom" in text


def test_the_plan_says_out_loud_when_nothing_checks_a_criterion(repo):
    (repo / "wringer.gates.yaml").unlink()
    text = interview.plan(repo)
    assert "NOTHING CHECKS THIS YET" in text
    assert "will not be claimed as done" in text


# --- capability 3: approve --------------------------------------------------


def test_approve_writes_only_the_approved_line(repo):
    interview.answer(repo, "which-columns", "The ones on screen.")
    before = (repo / "wringer.spec.yaml").read_text(encoding="utf-8")

    interview.approve(repo, read_the_plan=True)

    after = (repo / "wringer.spec.yaml").read_text(encoding="utf-8")
    assert after == before.replace("approved: false", "approved: true", 1)


def test_approve_and_the_hand_edit_are_byte_identical(repo, tmp_path):
    interview.answer(repo, "which-columns", "The ones on screen.")
    hand = tmp_path / "hand.yaml"
    hand.write_text(
        (repo / "wringer.spec.yaml")
        .read_text(encoding="utf-8")
        .replace("approved: false", "approved: true", 1),
        encoding="utf-8",
    )
    interview.approve(repo, read_the_plan=True)
    assert (repo / "wringer.spec.yaml").read_bytes() == hand.read_bytes()


def test_approve_does_not_corrupt_a_hand_written_capital_False(repo):
    """**A LIVE DEFECT, found 2026-08-19 by the adversarial review of
    SPEC_PMPLAN_V0 — in shipped code, not in the spec under review.**

    `approved: False` is valid YAML and PyYAML reads it as the boolean false,
    so a person who wrote their own spec by hand can perfectly well have it.
    `APPROVED_LINE` matches case-insensitively and therefore accepts it — and
    the edit underneath was `partition("false")`, which is case-SENSITIVE. It
    found nothing, so `head` became the entire line and the write produced

        approved: Falsetrue

    a corrupted spec that the engine's own loader then refuses with
    "'approved' must be a boolean". The person's file is destroyed and the
    error blames them for it.

    This surface exists to edit files a person wrote (`_spec_path`'s own
    message: *"this surface edits a spec a person or `wring spec` already
    wrote"*), so "the engine only ever writes lowercase" is not a defence —
    it is exactly the seam the board's fixtures kept landing on the wrong
    side of.
    """
    path = repo / "wringer.spec.yaml"
    path.write_text(
        path.read_text(encoding="utf-8").replace("approved: false", "approved: False", 1),
        encoding="utf-8",
    )
    interview.answer(repo, "which-columns", "The ones on screen.")

    interview.approve(repo, read_the_plan=True)

    after = path.read_text(encoding="utf-8")
    assert "Falsetrue" not in after, f"the interlock line was corrupted: {after!r}"
    import yaml
    assert yaml.safe_load(after)["approved"] is True, (
        "the file no longer parses with approved: true"
    )


def test_approve_preserves_the_operators_own_capitalisation_and_comment(repo):
    """The line edit changes the WORD and nothing else — the same promise the
    lowercase path already keeps, on a line a person capitalised."""
    path = repo / "wringer.spec.yaml"
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            "approved: false", "approved:   False   # mine, and I capitalise", 1
        ),
        encoding="utf-8",
    )
    interview.answer(repo, "which-columns", "x")

    interview.approve(repo, read_the_plan=True)

    line = [
        ln for ln in path.read_text(encoding="utf-8").splitlines()
        if ln.startswith("approved:")
    ][0]
    assert line == "approved:   true   # mine, and I capitalise", line


def test_there_is_no_way_to_approve_without_the_plan_being_rendered(repo):
    """**Ruling 20's forbidden button.** A button that approves without showing
    the plan is not the act the approval step exists for."""
    interview.answer(repo, "which-columns", "x")
    with pytest.raises(interview.InterviewError, match="rendered first"):
        interview.approve(repo, read_the_plan=False)
    assert "approved: false" in (repo / "wringer.spec.yaml").read_text()


def test_approving_with_a_required_question_open_is_refused(repo):
    with pytest.raises(interview.InterviewError, match="still unanswered"):
        interview.approve(repo, read_the_plan=True)
    assert "approved: false" in (repo / "wringer.spec.yaml").read_text()


def test_the_cli_approve_path_prints_the_plan_before_it_writes(repo, capsys):
    interview.answer(repo, "which-columns", "The ones on screen.")
    assert main(["approve", str(repo)]) == 0
    out = capsys.readouterr().out
    assert "HOW EACH PIECE WILL BE PROVED" in out
    assert out.index("HOW EACH PIECE") < out.index("approved: true")
    assert "never the same action" in out
    assert "approved: true" in (repo / "wringer.spec.yaml").read_text()


def test_no_verb_writes_anything_but_the_spec_file(repo):
    """**The surface writes `wringer.spec.yaml` and nothing else** — §8
    non-goal 9. In particular it never writes a judgement: a surface that could
    answer a `human` criterion would be the thing this programme exists to
    answer."""
    import ast

    before = {p.name for p in repo.iterdir()}
    interview.answer(repo, "which-columns", "x")
    interview.approve(repo, read_the_plan=True)
    assert {p.name for p in repo.iterdir()} == before

    # Structural, with `ast`, for the reason the core's face-detector guard is:
    # the PROSE here names `wringer.judgements.yaml` on purpose, because a
    # comment that cannot spell the thing it explains is no use. Only string
    # literals in executable positions count.
    source = Path(interview.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr) and isinstance(
                body[0].value, ast.Constant
            ):
                docstrings.add(id(body[0].value))

    named = [
        f"{n.lineno}: {n.value!r}"
        for n in ast.walk(tree)
        if isinstance(n, ast.Constant)
        and isinstance(n.value, str)
        and id(n) not in docstrings
        and "judgement" in n.value.lower()
    ]
    assert named == [], (
        f"this surface names a judgements path in executable code: {named}. "
        "Nothing anywhere may write a person's answer for them"
    )

    written = [
        n.lineno
        for n in ast.walk(tree)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Attribute)
        and n.func.attr in ("write_text", "write_bytes", "mkdir", "unlink")
    ]
    assert written, "the module writes nothing at all — that is also wrong"
    # And every write is to the spec file: the only path builder is `_spec_path`.
    assert "GATES_FILENAME" in source, "the sidecar is READ, so it is named"
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in ("write_text", "write_bytes"):
                target = ast.get_source_segment(source, node.func.value) or ""
                assert target == "path", (
                    f"a write at line {node.lineno} targets {target!r}, not the "
                    "`path` that `_spec_path` returned"
                )


# --- H-4: the questions, rendered ------------------------------------------


def criterion(**kwargs) -> Criterion:
    base = dict(
        id="c", title="T", required=True, state="unevidenced", refuses=True,
        gate_id=None, command=None, reason="", receipt=None, witness=None,
    )
    return Criterion(**{**base, **kwargs})


def test_every_needs_you_card_carries_its_unblocking_question():
    """**H-4.** Ruling 16 has given every value a question since S2 and nothing
    rendered one — half the mapping was guarded, pinned against the engine, and
    read by nobody. A card that states a problem without saying what is needed
    is a report; the question is what makes it a conversation."""
    board = object()
    for cause in (
        "unbound", "witness-evidenced-nothing", "born-green",
        "pre-existence-unestablished", "arrived-with-the-work",
    ):
        card = cards.card_for(board, criterion(cause=cause, gate_id="unit"))
        assert card.state == cards.NEEDS_YOU
        assert card.question, cause
        assert card.question == refusals.say(
            refusals.UNEVIDENCED_CAUSE, cause
        ).question


def test_the_three_human_states_each_get_their_own_question():
    """The NEEDS YOU card's question is the PM product's whole point, and
    before v3 this card said one thing for all three human states."""
    board = object()
    asked = {}
    for cause in ("human-unanswered", "human-said-no", "human-judgement-stale"):
        card = cards.card_for(board, criterion(state="human", cause=cause))
        assert card.state == cards.NEEDS_YOU
        asked[cause] = card.question
    assert len(set(asked.values())) == 3, asked
    assert "Only you can answer it" in asked["human-unanswered"]
    assert "still hold" in asked["human-judgement-stale"]


def test_a_human_row_a_person_answered_met_asks_the_honest_question():
    """Not "is this met?" — they said so. The honest question is the one the
    record's own limit raises: nothing re-checks it."""
    card = cards.card_for(
        object(),
        criterion(
            state="human", refuses=False,
            judgement={"verdict": "met", "by": "Marc", "at": "x", "stale": False},
        ),
    )
    assert card.state == cards.NEEDS_YOU
    assert "Marc said this was met" in card.question
    assert "does it still hold?" in card.question


def test_the_question_reaches_the_rendered_page():
    """Guarded at the HTML, not only on the dataclass — a question carried and
    never rendered is exactly the gap H-4 closes."""
    from wringer_board import render

    html = render._card_html(
        cards.Card(
            id="c", title="T", state=cards.NEEDS_YOU,
            sentence="Nothing checks this yet.",
            question="Which check should decide this requirement?",
        )
    )
    assert 'class="ask"' in html
    assert "Which check should decide this requirement?" in html


# --- the fixture that is the ENGINE'S OWN OUTPUT ---------------------------
#
# **These are the tests that would have caught two live defects, and did not
# exist.** Every fixture above is hand-typed, i.e. written on the same side of
# the seam as the reader — the identical failure mode that let eleven mutations
# through this repository's absence guard, and the one this window had already
# written into a commit message hours before repeating it here.
#
# The refute review of SPEC_DRIVE_V0 found both by driving `spec.render()`
# through `interview`. What follows is that, as a test.


def engine_spec_file(directory: Path) -> Path:
    """A `wringer.spec.yaml` rendered by the ENGINE, not typed here."""
    spec = pytest.importorskip("wringer.spec")
    drafted = spec.Spec(
        approved=False,
        title="CSV export",
        intent="A manager can export the report as a CSV.",
        questions=(
            spec.Question(id="which-columns", question="Which columns?", required=True),
            spec.Question(id="filename", question="What filename?", required=False),
        ),
        criteria=(spec.Criterion(id="exports-csv", title="It exports a CSV", required=True),),
        gates=(),
        tasks=(spec.Task(id="build", brief="Build it", objective="It exports."),),
        path="wringer.spec.yaml",
    )
    path = directory / "wringer.spec.yaml"
    path.write_text(spec.render(drafted), encoding="utf-8")
    return path


def test_approve_accepts_the_spec_THIS_ENGINE_DRAFTS(tmp_path):
    """**The defect this catches shipped.**

    `wring spec` renders the interlock with a trailing comment:

        approved: false        # <- the interlock. `wring plan` refuses …

    and the first `APPROVED_LINE` ended `\\s*$`, so `approve` REFUSED every
    spec the engine itself drafts, with the message *"it does not invent
    structure"* — which reads as a caller bug and is not one.
    """
    engine_spec_file(tmp_path)
    interview.answer(tmp_path, "which-columns", "The ones on screen.")

    interview.approve(tmp_path, read_the_plan=True)

    text = (tmp_path / "wringer.spec.yaml").read_text(encoding="utf-8")
    assert "approved: true" in text
    # **The interlock's own comment survives**, because it is the sentence that
    # tells a person what the flag does. A surface that deleted the explanation
    # while flipping the flag would be removing the reason for the thing it did.
    line = next(l for l in text.splitlines() if l.startswith("approved:"))
    assert "#" in line and "interlock" in line, line
    # And the engine can read its own file back.
    spec = pytest.importorskip("wringer.spec")
    assert spec.load(tmp_path / "wringer.spec.yaml").approved is True


def test_answer_FILLS_the_empty_answer_the_engine_already_wrote(tmp_path):
    """**The second defect this catches shipped**, and it was invisible.

    `wring spec` renders `answer: ''` unconditionally, so appending produced a
    mapping with a DUPLICATE `answer:` key. PyYAML takes the last, so nothing
    errored and the byte-equality test stayed green — its fixture had no
    `answer:` line at all.
    """
    engine_spec_file(tmp_path)
    interview.answer(tmp_path, "which-columns", "The ones on screen.")

    text = (tmp_path / "wringer.spec.yaml").read_text(encoding="utf-8")
    block = text.split("open_questions:", 1)[1]
    first = block.split("- id: filename", 1)[0]
    assert first.count("answer:") == 1, (
        f"duplicate `answer:` key written into one mapping:\n{first}"
    )
    assert "answer: ''" not in first
    assert "The ones on screen." in first

    spec = pytest.importorskip("wringer.spec")
    loaded = spec.load(tmp_path / "wringer.spec.yaml")
    assert {q.id: q.answer for q in loaded.questions}["which-columns"] == (
        "The ones on screen."
    )
    assert loaded.unanswered == ()


def test_the_whole_S3_chain_runs_on_engine_output(tmp_path):
    """plan → answer → plan → approve, against bytes the engine wrote.

    The end-to-end version, so a future change that breaks any one link fails
    here rather than in whatever composes them later.
    """
    engine_spec_file(tmp_path)

    before = interview.plan(tmp_path)
    assert "which-columns" in before and "will refuse" in before

    interview.answer(tmp_path, "which-columns", "The ones on screen.")
    after = interview.plan(tmp_path)
    assert "STILL UNANSWERED" not in after, after

    interview.approve(tmp_path, read_the_plan=True)
    spec = pytest.importorskip("wringer.spec")
    assert spec.load(tmp_path / "wringer.spec.yaml").approved is True


def test_a_required_question_left_open_still_blocks_approval_on_engine_output(
    tmp_path,
):
    engine_spec_file(tmp_path)
    with pytest.raises(interview.InterviewError, match="still unanswered"):
        interview.approve(tmp_path, read_the_plan=True)
    spec = pytest.importorskip("wringer.spec")
    assert spec.load(tmp_path / "wringer.spec.yaml").approved is False


# --- multi-line answers, which a PM writes and which used to be lost -------


@pytest.mark.parametrize("text", [
    "one line",
    "line one\nline two",
    "First: the ones on screen.\nSecond: in that order.\nThird: no totals row.",
    "has: a colon",
    "has # a hash",
    'has "quotes" in it',
    "  leading and trailing  ",
    # **YAML's plain scalars are not decided by which characters are in them**,
    # which is what `_scalar` used to check. Every one of these round-tripped
    # as a bool, None, a float or a date — and `yes` is the likeliest answer
    # anybody will ever type into an interview. `wring plan` then refused the
    # PM's own spec with "'answer' must be a string".
    #
    # Found by driving a REAL drafted spec through `wringer-drive`, not by
    # reading this function.
    "yes",
    "no",
    "true",
    "off",
    "null",
    "~",
    "1.5",
    "12",
    "2026-08-17",
    "Yes",
    "NO",
])
def test_an_answer_round_trips_EXACTLY_through_the_engines_own_loader(tmp_path, text):
    """**`_scalar`'s docstring claimed this and it was false** (finding 15).

    A double-quoted YAML scalar containing a literal newline is FOLDED, so
    `"line one\\nline two"` reparses as `line one line two`. A PM answering in
    more than one sentence lost their line breaks with no error anywhere.

    Byte-equality could not catch it, which is the interesting part: both
    sides of that test go through `_scalar`, so it agreed with itself. This
    checks the round trip against the ENGINE's loader instead.
    """
    spec = pytest.importorskip("wringer.spec")
    engine_spec_file(tmp_path)
    interview.answer(tmp_path, "which-columns", text)

    loaded = spec.load(tmp_path / "wringer.spec.yaml")
    got = {q.id: q.answer for q in loaded.questions}["which-columns"]
    assert got == text, f"answer did not survive: {text!r} -> {got!r}"


def test_a_multi_line_answer_is_a_block_scalar_which_is_what_a_person_writes():
    """Byte-equality with a hand edit still holds, because `|-` is the form a
    person reaching for multi-line YAML would use."""
    rendered = interview._scalar("line one\nline two", "    ")
    assert rendered.startswith("|-\n")
    assert "      line one" in rendered
    assert "      line two" in rendered


def test_the_plan_reads_INSTALLED_bindings_not_only_proposed_ones(tmp_path):
    """**It said "NOTHING CHECKS THIS YET" about a criterion a gate binds.**

    `wringer.gates.yaml` holds gates a drafter PROPOSED; `.wringer.yaml` holds
    the ones a human INSTALLED, and only those run. `_bindings` read the
    sidecar alone, so a repository that had already bound a criterion was told
    nothing checked it — a false sentence, to the reader least able to check
    it, on the page they approve from.

    Found by driving DRIVE end to end against a repository with a binding.
    """
    (tmp_path / "wringer.spec.yaml").write_text(SPEC, encoding="utf-8")
    (tmp_path / ".wringer.yaml").write_text(
        'version: 1\ngates:\n  - id: export-works\n'
        '    run: "grep -q text/csv report.py"\n    proves: csv-downloads\n',
        encoding="utf-8",
    )
    text = interview.plan(tmp_path)
    assert "NOTHING CHECKS THIS" not in text.split("copy-reads-well")[0], text
    assert "`export-works`" in text
    assert "seen to FAIL first" in text
    assert "proposed, not installed" not in text


def test_a_PROPOSED_gate_says_so_rather_than_reading_as_installed(tmp_path):
    """The other direction, and it is the honest half: a proposal is not a
    check yet, and a plan that read one as installed would promise a proof
    nobody has agreed to run."""
    (tmp_path / "wringer.spec.yaml").write_text(SPEC, encoding="utf-8")
    (tmp_path / "wringer.gates.yaml").write_text(GATES, encoding="utf-8")

    text = interview.plan(tmp_path)
    assert "`export`" in text
    assert "proposed, not installed yet" in text


def test_an_installed_binding_wins_over_a_proposed_one(tmp_path):
    """The plan describes what WILL happen, and what happens is what
    `.wringer.yaml` says."""
    (tmp_path / "wringer.spec.yaml").write_text(SPEC, encoding="utf-8")
    (tmp_path / "wringer.gates.yaml").write_text(GATES, encoding="utf-8")
    (tmp_path / ".wringer.yaml").write_text(
        'version: 1\ngates:\n  - id: the-real-one\n    run: "true"\n'
        "    proves: csv-downloads\n",
        encoding="utf-8",
    )
    text = interview.plan(tmp_path)
    assert "`the-real-one`" in text
    assert "proposed, not installed" not in text
