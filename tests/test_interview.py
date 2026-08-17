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
