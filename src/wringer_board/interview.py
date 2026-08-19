"""The interview surface — SPEC_BOARD_V0 §5 ruling 20 (S3).

**A pen, not a new channel.** Three capabilities, each writing exactly what a
hand-edit writes today, into `wringer.spec.yaml` and nothing else:

1. **The conversation over `open_questions`** — an answer lands as an `answer:`
   under its question, in the shape the core's spec loader already reads
   (`spec.Spec.unanswered`). `wring plan` reports what is still unanswered and
   REFUSES; that refusal is rendered, never pre-empted.
2. **The plain-language plan** — *here is what I will build, and here is how I
   will prove each piece* — rendered from the approved spec's criteria and the
   gate sidecar's `proves:` bindings.
3. **The approve action**, which writes `approved: true` and nothing else.

**Three refusals, all structural.**

- **There is no `--yes` equivalent and this surface does not become one.** The
  whole point of the approval step is that a person read what is about to be
  built. A button clicked after reading a rendered plan is that same act; a
  button that approves WITHOUT rendering the plan is not, and `approve`
  therefore prints the plan and requires the reader to name what they read.
- **Approving and answering a question are never the same action.** Two verbs,
  two files' worth of edit, and neither reaches the other.
- **This module never writes `.wringer/`, never writes a judgement, and never
  touches a gate.** `wringer.judgements.yaml` in particular is a person's own
  file with no writer anywhere in either repository — see the core's
  `test_no_flag_no_env_var_and_no_command_can_write_a_judgement`. A surface
  that could answer a `human` criterion would be the thing this programme
  exists to answer.

**Byte equality is the test** (B5): drive the verb and the hand edit against
the same fixture and the resulting files are identical. That is why the writes
here are line edits to the existing text rather than a YAML round-trip — a
round-trip reformats comments, key order and quoting, so it could not be
byte-equal to what a person would have typed, and the person's file is the
artifact of record.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

SPEC_FILENAME = "wringer.spec.yaml"
GATES_FILENAME = "wringer.gates.yaml"


class InterviewError(Exception):
    """A refusal. Carries the exit code the CLI should use."""

    def __init__(self, message: str, exit_code: int = 2) -> None:
        super().__init__(message)
        self.exit_code = exit_code


@dataclass(frozen=True)
class Question:
    id: str
    question: str
    required: bool
    answer: str

    @property
    def answered(self) -> bool:
        return bool(self.answer.strip())


def _spec_path(repo: Path) -> Path:
    path = repo / SPEC_FILENAME
    if not path.is_file():
        raise InterviewError(
            f"there is no {SPEC_FILENAME} in {repo}. This surface edits a spec "
            "a person or `wring spec` already wrote; it does not draft one"
        )
    return path


def _load(repo: Path) -> dict:
    import yaml

    try:
        data = yaml.safe_load(_spec_path(repo).read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - yaml's own message is best
        raise InterviewError(f"{SPEC_FILENAME} could not be read: {exc}") from exc
    if not isinstance(data, dict):
        raise InterviewError(f"{SPEC_FILENAME} is not a mapping")
    return data


def questions(repo: Path) -> list[Question]:
    data = _load(repo)
    found = []
    for entry in data.get("open_questions") or []:
        if not isinstance(entry, dict):
            continue
        found.append(
            Question(
                id=str(entry.get("id", "")),
                question=str(entry.get("question", "")),
                required=bool(entry.get("required", True)),
                answer=str(entry.get("answer") or ""),
            )
        )
    return found


def unanswered(repo: Path) -> list[Question]:
    """Exactly what the core's `Spec.unanswered` means: required and empty."""
    return [q for q in questions(repo) if q.required and not q.answered]


# --- capability 1: the conversation ----------------------------------------


def answer(repo: Path, question_id: str, text: str) -> Path:
    """Write one `answer:` under one question. A line edit, not a round-trip.

    **It refuses to overwrite an existing answer.** A surface that silently
    replaces what a person already wrote is a surface that can lose it, and the
    remedy — edit the file — is the same act this verb performs.
    """
    if not text.strip():
        raise InterviewError(
            "an empty answer is not an answer. A question is answered when "
            "somebody writes something under it; leaving it blank is the state "
            "it is already in"
        )
    found = {q.id: q for q in questions(repo)}
    if question_id not in found:
        known = ", ".join(sorted(found)) or "none"
        raise InterviewError(
            f"no open question {question_id!r} in {SPEC_FILENAME}. Known: {known}"
        )
    if found[question_id].answered:
        raise InterviewError(
            f"{question_id!r} is already answered: "
            f"{found[question_id].answer.strip()!r}. This surface does not "
            f"overwrite what a person wrote — edit {SPEC_FILENAME} by hand"
        )

    path = _spec_path(repo)
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)

    # **`wring spec` renders `answer: ''` UNCONDITIONALLY**, so an unanswered
    # question already has an `answer:` key on disk. Appending a second one
    # produced a mapping with a duplicate key — PyYAML happens to take the
    # last, so nothing errored and the round-trip test passed, but a strict
    # loader rejects it and the file is malformed. Same cause as the interlock
    # bug above: the fixture was hand-typed and had no `answer:` line at all.
    #
    # So: fill an existing empty one in place, and only append when there is
    # none. Both paths stay byte-identical to what a person would have typed.
    filled = _fill_existing(lines, question_id, text)
    if filled is not None:
        path.write_text("".join(filled), encoding="utf-8")
        return path

    out, inserted = [], False
    target = re.compile(r"^(\s*)-?\s*id:\s*['\"]?" + re.escape(question_id) + r"['\"]?\s*$")
    inside = False
    indent = ""
    for index, line in enumerate(lines):
        out.append(line)
        if not inside:
            match = target.match(line.rstrip("\n"))
            if match and _within_open_questions(lines, index):
                inside = True
                indent = _sibling_indent(line)
            continue
        # Inside the matched question: append after its last key line.
        nxt = lines[index + 1] if index + 1 < len(lines) else ""
        if _ends_block(nxt, indent):
            out.append(f"{indent}answer: {_scalar(text, indent)}\n")
            inserted = True
            inside = False
    if not inserted:
        raise InterviewError(
            f"could not find where to write the answer for {question_id!r} in "
            f"{SPEC_FILENAME}. Nothing was changed — edit it by hand"
        )
    path.write_text("".join(out), encoding="utf-8")
    return path


def _fill_existing(
    lines: list[str], question_id: str, text: str
) -> list[str] | None:
    """Replace this question's EMPTY `answer:` in place, or None if it has none."""
    target = re.compile(
        r"^(\s*)-?\s*id:\s*['\"]?" + re.escape(question_id) + r"['\"]?\s*$"
    )
    inside = False
    indent = ""
    for index, line in enumerate(lines):
        if not inside:
            if target.match(line.rstrip("\n")) and _within_open_questions(lines, index):
                inside = True
                indent = _sibling_indent(line)
            continue
        if _ends_block(line, indent) and not line.strip().startswith("answer:"):
            return None                      # left the block without finding one
        if line.strip().startswith("answer:"):
            existing = line.split(":", 1)[1].strip().strip("'\"")
            if existing:
                return None                  # a real answer; the caller refuses
            copy = list(lines)
            copy[index] = f"{indent}answer: {_scalar(text, indent)}\n"
            return copy
    return None



def _within_open_questions(lines: list[str], index: int) -> bool:
    """Whether this `id:` belongs to `open_questions` rather than to a task."""
    for line in reversed(lines[:index]):
        stripped = line.rstrip("\n")
        if not stripped.strip() or stripped.startswith((" ", "\t", "-")):
            continue
        return stripped.split(":", 1)[0].strip() == "open_questions"
    return False


def _sibling_indent(line: str) -> str:
    """The column a sibling key of this `id:` sits at."""
    body = line.rstrip("\n")
    stripped = body.lstrip()
    lead = body[: len(body) - len(stripped)]
    return lead + "  " if stripped.startswith("-") else lead


def _ends_block(nxt: str, indent: str) -> bool:
    """Whether the next line leaves this question's block."""
    if not nxt.strip():
        return True
    lead = len(nxt) - len(nxt.lstrip())
    return lead < len(indent) or nxt.lstrip().startswith("-")


def _scalar(text: str, indent: str = "    ") -> str:
    """A YAML scalar that round-trips to exactly `text`.

    **It did not, and the docstring said it did.** A double-quoted scalar
    containing a literal newline is FOLDED by YAML — `"line one\nline two"`
    reparses as `line one line two` — so a PM answering a question in more
    than one sentence silently lost their line breaks, with no error anywhere.
    Found by the refute review of SPEC_DRIVE_V0 (finding 15).

    Byte-equality could not catch it, and that is the interesting part: both
    sides of that test go through this function, so it agreed with itself.

    Multi-line text is now a **literal block scalar** (`|-`), which is the one
    YAML form that preserves newlines exactly and is also the form a person
    would write by hand — so byte-equality still holds against a hand edit.
    """
    if "\n" in text:
        body = "\n".join(f"{indent}  {line}" if line else "" for line in
                          text.rstrip("\n").split("\n"))
        return "|-\n" + body
    flat = " ".join(text.split())
    quoted = '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    if flat != text or any(c in text for c in ":#\"'") or not text.strip():
        return quoted

    # **And now ASK THE READER, rather than reasoning about it.** The rule
    # above is a list of characters, and YAML's plain scalars are not decided
    # by characters: `yes`, `no`, `true`, `off`, `null`, `~`, `1.5` and
    # `2026-08-17` all reparse as a bool, None, a float or a date. A PM
    # answering a drafter's question with "yes" — the likeliest answer anyone
    # will ever type here — silently wrote a boolean, and `wring plan` then
    # refused their own spec with "'answer' must be a string".
    #
    # Found by driving a real drafted spec through this writer and back
    # through the ENGINE's loader, which is the only side that decides. Same
    # class as the newline folding above: a rule about the text, where the
    # question was what the reader does with it.
    try:
        import yaml

        if yaml.safe_load(f"v: {text}")["v"] != text:
            return quoted
    except Exception:                                    # noqa: BLE001
        # Unparseable bare is exactly the case quoting exists for.
        return quoted
    return text


# --- capability 2: the plain-language plan ----------------------------------


def plan(repo: Path) -> str:
    """*Here is what I will build, and here is how I will prove each piece.*

    Read from the approved spec's criteria and the gate sidecar's `proves:`
    bindings. **It states which criteria have no check and which are a
    person's**, because a plan that hides either is the one a PM would approve
    by mistake.
    """
    data = _load(repo)
    bound = _bindings(repo)
    assumptions, outcomes = _decisions(repo)
    answered = {
        str(q.id): q.answer for q in questions(repo) if q.answered
    }
    lines = [
        data.get("title") or "This build",
        "",
        (data.get("intent") or "").strip(),
        "",
    ]

    if assumptions:
        # **Board SCAFFOLDING, like `WHAT I WILL BUILD` beneath it.** Ruling 1
        # governs the board re-describing an ENGINE FACT; a section heading is
        # not one. What sits under it is the drafter's own field, verbatim —
        # and it must stay that way, because per-roll variance in the wording
        # of a consent surface is the defect this block exists to answer, not
        # a fix for it.
        lines += [
            "DECIDED WITHOUT ASKING YOU",
            "",
            "  These were decided for you. Approving this plan approves them.",
            "  Each one says the question it replaced, so you can ask it after all.",
            "",
        ]
        for assumption in assumptions:
            aid = str(assumption.get("id", ""))
            lines.append(f"  {aid}")
            if aid in answered:
                # SUPERSEDED: the person came back and answered the displaced
                # question, so this is no longer a decision anybody is being
                # asked to approve. Rendering it as one — or rendering "you
                # were not asked" — would be a false sentence on the page they
                # approve from.
                lines += [
                    f"    NO LONGER DECIDED FOR YOU — you answered this: "
                    f"{answered[aid].strip()}",
                    f"    (it had been: {assumption.get('decision', '')})",
                    "",
                ]
                continue
            lines += [
                f"    {assumption.get('decision', '')}",
                f"    Why: {assumption.get('why', '')}",
                f"    You were not asked: {assumption.get('instead_of_asking', '')}",
                "",
            ]

    lines += ["WHAT I WILL BUILD", ""]
    for task in data.get("tasks") or []:
        if not isinstance(task, dict):
            continue
        tid = str(task.get("id", ""))
        objective = task.get("objective") or task.get("brief") or tid
        # **Two registers, prominence to the person's.** The outcome is what
        # they will be able to DO; the objective is instructions for whoever
        # builds it, and is labelled as such rather than left to look like a
        # promise made to the reader.
        if tid in outcomes:
            lines += [
                f"  {outcomes[tid]}",
                f"    For the engineer: {objective}",
                "",
            ]
        else:
            lines += [
                "  (no plain-language outcome was written for this task)",
                f"    For the engineer: {objective}",
                "",
            ]
    lines += ["HOW EACH PIECE WILL BE PROVED", ""]
    for criterion in data.get("criteria") or []:
        if not isinstance(criterion, dict):
            continue
        cid = str(criterion.get("id", ""))
        title = criterion.get("title") or cid
        need = "must" if criterion.get("required", True) else "optional —"
        if criterion.get("human"):
            how = (
                "A PERSON decides this. No check can, and none will be written "
                "for it — you record the answer yourself"
            )
        elif cid in bound:
            gate, installed = bound[cid]
            how = f"the check `{gate}` — and it must be seen to FAIL first"
            if not installed:
                # A PROPOSED gate is not a check yet. Saying so is the
                # difference between a plan and a promise.
                how += (
                    " (proposed, not installed yet — somebody has to accept it "
                    "before it runs)"
                )
        else:
            how = (
                "NOTHING CHECKS THIS YET. It will be reported as unevidenced "
                "and it will not be claimed as done"
            )
        lines += [f"  {title}", f"    {need} — {how}", ""]

    lines += _ending_block(data, bound)

    still = unanswered(repo)
    if still:
        lines += [
            "STILL UNANSWERED — `wring plan` will refuse while these are open",
            "",
        ]
        lines += [f"  {q.id}: {q.question}" for q in still]
        lines.append("")
    lines += [
        "WHAT THIS PLAN DOES NOT SAY",
        "",
        "  That the criteria are the right ones. Wringer checks a binding's",
        "  consequences, never its wisdom — if a requirement is worded wrongly,",
        "  a green check against it proves the wrong thing perfectly.",
        "",
    ]
    return "\n".join(lines).rstrip() + "\n"


DECISIONS_FILENAME = "wringer.decisions.yaml"


def _decisions(repo: Path) -> tuple[list[dict], dict[str, str]]:
    """The plain-language sidecar: assumptions, and outcomes by task id.

    Absent or unreadable is not an error — this file is optional, an offline
    repository may never have one, and a plan that refused without it would
    make the whole surface depend on a channel that only `--send` fills.
    """
    import yaml

    path = repo / DECISIONS_FILENAME
    if not path.is_file():
        return [], {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:                                    # noqa: BLE001
        return [], {}
    if not isinstance(data, dict):
        return [], {}
    assumptions = [
        entry for entry in (data.get("assumptions") or [])
        if isinstance(entry, dict)
    ]
    outcomes = {
        str(row["task"]): str(row["outcome"])
        for row in (data.get("outcomes") or [])
        if isinstance(row, dict) and row.get("task") and row.get("outcome")
    }
    return assumptions, outcomes


def _ending_block(data: dict, bound: dict) -> list[str]:
    """What the run will do with each class of requirement.

    **Counts only, and the omission is deliberate** (SPEC_PMPLAN_V0 ruling 9,
    after review C2). Three sentences a reader would want here — that an
    unbound criterion cannot hold the handover, that a bound one can, that an
    unanswered `human` one will — are statements about ENGINE BEHAVIOUR, and
    board ruling 1 says this layer renders engine facts rather than authoring
    prose about them. `refusals.py` maps refusals that HAPPENED and has no
    saying for one that will not, and the delivery saying does not fit either:
    its second half is *"See the cards above"*, and at approval time there are
    no cards. So the counts render — they are a reading of data this module
    already holds — and the sentences wait for a saying added engine-side.

    **The three classes come from the INSTALLED flag, not from boundness.**
    `_bindings()` merges proposed gates (`wringer.gates.yaml`) with installed
    ones (`.wringer.yaml`); acceptance joins on the installed ones alone
    (`accept.assess` builds its map from `cfg.gates`). Counting a proposed
    gate as a bound check would make this block contradict the criteria block
    a few lines above it, which already says "proposed, not installed yet".
    """
    checked = human = nothing = 0
    for criterion in data.get("criteria") or []:
        if not isinstance(criterion, dict):
            continue
        cid = str(criterion.get("id", ""))
        if criterion.get("human"):
            human += 1
        elif cid in bound and bound[cid][1]:
            checked += 1
        else:
            nothing += 1
    total = checked + human + nothing
    if not total or not (human or nothing):
        # Everything is installed-bound: there is no surprise to warn about,
        # and a block predicting an ending that will not happen is noise.
        return []

    lines = ["WHAT WILL HAPPEN AT THE END", ""]
    lines.append(f"  {checked} of {total} have a check bound to them.")
    if human:
        lines.append(
            f"  {human} {'is' if human == 1 else 'are'} yours to decide — no "
            "check can, and you record the answer yourself."
        )
    if nothing:
        lines.append(f"  {nothing} have nothing checking them yet.")
    lines += [
        "",
        "  Approving this plan accepts that the ones with nothing checking",
        "  them will not be proved.",
        "",
    ]
    return lines


CONFIG_FILENAME = ".wringer.yaml"


def _bindings(repo: Path) -> dict[str, tuple[str, bool]]:
    """`criterion id -> (gate id, installed?)`.

    **Read from BOTH files, and the difference is not cosmetic.**
    `wringer.gates.yaml` holds gates a drafter PROPOSED; `.wringer.yaml` holds
    the ones a human INSTALLED, and only those actually run.

    This read the sidecar alone until 2026-08-17, so a repository whose
    `.wringer.yaml` already bound a criterion was told *"NOTHING CHECKS THIS
    YET"* on its plan — a false sentence, to the one reader least able to
    check it, on the page they approve from. Found by driving DRIVE end to end
    against a repository that had a binding.

    The installed one wins where both name a criterion: the plan describes what
    will happen, and what happens is what `.wringer.yaml` says.
    """
    import yaml

    def read(path: Path) -> dict[str, str]:
        if not path.is_file():
            return {}
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
        found = {}
        for gate in (data or {}).get("gates") or []:
            if isinstance(gate, dict) and gate.get("proves"):
                found[str(gate["proves"])] = str(gate.get("id", "?"))
        return found

    bindings: dict[str, tuple[str, bool]] = {
        criterion: (gate, False) for criterion, gate in read(repo / GATES_FILENAME).items()
    }
    for criterion, gate in read(repo / CONFIG_FILENAME).items():
        bindings[criterion] = (gate, True)
    return bindings


# --- capability 3: approve --------------------------------------------------


# **The trailing comment is part of the line, and both halves of that matter.**
# `wring spec` renders the interlock as:
#
#     approved: false        # <- the interlock. `wring plan` refuses while this is false.
#
# (`wringer/src/wringer/spec.py`). The first version of this pattern ended
# `\s*$`, so it matched a hand-written `approved: false` and REFUSED every spec
# the engine itself drafts — with the message "it does not invent structure",
# which reads as a caller bug and is not one. It was never caught because this
# package's fixture was hand-typed, i.e. written on the same side of the seam
# as the reader. That is the identical failure mode that let eleven mutations
# through this repository's absence guard, and it is why the fixture in
# `test_interview.py` is now `spec.render()`'s real output.
#
# The comment is CAPTURED and written back verbatim: it is the sentence that
# tells a person what the flag does, and a surface that silently deleted it
# while flipping the flag would be removing the explanation of the thing it
# just did.
# **Every YAML 1.1 boolean the ENGINE accepts, and the engine is what decides.**
# `false`, `no` and `off` all read as the boolean false in PyYAML, and
# `spec.load` on `approved: no` returns a perfectly valid unapproved spec. The
# pattern matched only `true|false`, so `approve` fell out of its loop on the
# others and told the person their file *"has no top-level `approved:` line to
# set"* — about a line sitting in front of them.
#
# That is the SECOND time this exact sentence has been wrong, for the same
# underlying reason, and the note below records the first. Both times the
# fixtures were written on the same side of the seam as the reader.
#
# `y`/`n` are deliberately absent: PyYAML reads them as the strings "y"/"n",
# so the engine refuses such a spec first with "'approved' must be a boolean".
# This surface must accept exactly what the engine does — no more, since a
# spelling the engine rejects is not an interlock at all, and no less.
_YAML_TRUE = frozenset({"true", "yes", "on"})
APPROVED_LINE = re.compile(
    r"^approved:\s*(?P<value>true|false|yes|no|on|off)\s*(?P<comment>#.*)?$", re.I
)


def approve(repo: Path, *, read_the_plan: bool) -> Path:
    """Write `approved: true`, and nothing else, into `wringer.spec.yaml`.

    **`read_the_plan` is not a `--yes`.** It is the caller's assertion that the
    plan was rendered to a person first, and the CLI sets it by RENDERING the
    plan — there is no flag that sets it without printing. `cli.py:2717-2726`
    in the core says the whole point of this step is that a person read what is
    about to be built; a button that approves without showing the plan is not
    that act, and is forbidden by ruling 20.
    """
    if not read_the_plan:
        raise InterviewError(
            "approval requires the plan to have been rendered first. That is "
            "the whole point of the step: a person approves what they have "
            "read. There is no flag that skips it"
        )
    still = unanswered(repo)
    if still:
        names = ", ".join(q.id for q in still)
        raise InterviewError(
            f"{len(still)} required question(s) are still unanswered: {names}. "
            "Answer them first — approving a spec with open questions approves "
            "a guess",
            exit_code=1,
        )

    path = _spec_path(repo)
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    for index, line in enumerate(lines):
        match = APPROVED_LINE.match(line.rstrip("\n"))
        if match is None:
            continue
        if match.group("value").lower() in _YAML_TRUE:
            raise InterviewError(
                f"{SPEC_FILENAME} is already approved. Nothing was changed",
                exit_code=0,
            )
        # Preserve the operator's own spacing and the interlock's comment. The
        # only thing that changes is the word.
        #
        # **Spliced on the MATCH's own span, and the previous version was a
        # live corruption bug** (found 2026-08-19 by the adversarial review of
        # SPEC_PMPLAN_V0, in this shipped code rather than in the spec it was
        # reviewing). It was `partition("false")` — case-SENSITIVE — under a
        # regex that matches case-INSENSITIVELY. A person's hand-written
        # `approved: False` therefore matched, found no lowercase `false` to
        # partition on, kept the whole line as `head`, and was written back as
        #
        #     approved: Falsetrue
        #
        # which the engine's loader then refuses with "'approved' must be a
        # boolean" — the person's file destroyed and the error pointed at them.
        # `False` is valid YAML for false, and this surface's entire purpose is
        # editing files people wrote by hand, so nothing about it was exotic.
        #
        # Using `span("value")` means the replaced bytes are exactly the ones
        # the pattern identified as the value, whatever its spelling, and every
        # other byte on the line — indentation, spacing, the interlock's
        # explanatory comment — is carried through untouched.
        body = line.rstrip("\n")
        start, end = match.span("value")
        lines[index] = f"{body[:start]}true{body[end:]}\n"
        path.write_text("".join(lines), encoding="utf-8")
        return path
    raise InterviewError(
        f"{SPEC_FILENAME} has no top-level `approved:` line to set. This "
        "surface edits what is there; it does not invent structure"
    )
