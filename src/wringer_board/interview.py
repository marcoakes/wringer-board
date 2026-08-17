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
            out.append(f"{indent}answer: {_scalar(text)}\n")
            inserted = True
            inside = False
    if not inserted:
        raise InterviewError(
            f"could not find where to write the answer for {question_id!r} in "
            f"{SPEC_FILENAME}. Nothing was changed — edit it by hand"
        )
    path.write_text("".join(out), encoding="utf-8")
    return path


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


def _scalar(text: str) -> str:
    """A YAML scalar that round-trips to exactly `text`."""
    flat = " ".join(text.split())
    if flat != text or any(c in text for c in ":#\n\"'") or not text.strip():
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
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
    lines = [
        data.get("title") or "This build",
        "",
        (data.get("intent") or "").strip(),
        "",
        "WHAT I WILL BUILD",
        "",
    ]
    for task in data.get("tasks") or []:
        if isinstance(task, dict):
            lines.append(f"  - {task.get('objective') or task.get('brief') or task.get('id')}")
    lines += ["", "HOW EACH PIECE WILL BE PROVED", ""]
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
            how = f"the check `{bound[cid]}` — and it must be seen to FAIL first"
        else:
            how = (
                "NOTHING CHECKS THIS YET. It will be reported as unevidenced "
                "and it will not be claimed as done"
            )
        lines += [f"  {title}", f"    {need} — {how}", ""]

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


def _bindings(repo: Path) -> dict[str, str]:
    """`criterion id -> gate id`, from the sidecar if there is one."""
    import yaml

    path = repo / GATES_FILENAME
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


# --- capability 3: approve --------------------------------------------------


APPROVED_LINE = re.compile(r"^approved:\s*(true|false)\s*$", re.I)


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
        if APPROVED_LINE.match(line.rstrip("\n")):
            if line.rstrip("\n").split(":", 1)[1].strip().lower() == "true":
                raise InterviewError(
                    f"{SPEC_FILENAME} is already approved. Nothing was changed",
                    exit_code=0,
                )
            lines[index] = "approved: true\n"
            path.write_text("".join(lines), encoding="utf-8")
            return path
    raise InterviewError(
        f"{SPEC_FILENAME} has no top-level `approved:` line to set. This "
        "surface edits what is there; it does not invent structure"
    )
