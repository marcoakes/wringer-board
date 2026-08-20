# The board, measured twice

`PROTOCOL.md` exists so that "the board is readable" stops being a matter of
taste. It was run on **2026-08-19** against the shipped board, and again on
**2026-08-20** after four structural fixes — **same protocol, same six role
prompts, fresh readers, a page regenerated from the same real run.** Changing
the prompts would have made the comparison worthless.

## The numbers

| | 2026-08-19 | 2026-08-20 |
|---|---|---|
| said the work was finished | **0 of 6** | **0 of 6** |
| verdict split | 3 partly / 3 not finished | 4 partly / 2 not finished |
| confidence | low to medium | **5 medium, 1 high** |
| things a reader could not understand | **85** | **68** |
| words they had to guess at | 104 | 91 |

## Nobody said "finished", and that is now the RIGHT answer

The headline number did not move, and reading it as a failure would be the
mistake. **The work genuinely is not finished**: the handover is being held,
one requirement in ten is proved, and one is waiting on a person. A reader who
said "finished" would be wrong.

`PROTOCOL.md`'s pass criterion is not "they say finished". It is:

> they can say whether the work is finished, **and they are right**.

On 2026-08-19 readers said "partly" for confused reasons — one of them
believing the page contradicted itself. On 2026-08-20 they said it for
accurate ones. That is the change, and it does not show up in the verdict
column.

The clearest example is the count line. Before:

> *"'1 done and proved · 1 holding up the handover' — this count quietly omits
> the other eight unproven requirements. Reading only the count line, I'd
> think 8 of 10 were fine."*

After, unprompted, from every reader: *1 of 10 proved, 1 waiting on me, 8 with
nothing checking them.* The line now accounts for every requirement.

The scoped promise was noticed too, by the reader whose job was to catch
overclaiming: *"the top banner explicitly says the one green item 'says
nothing about the rest of the page'."*

## What was fixed between the two runs

- **The verdict comes first.** The page opened with sixteen lines of the
  reader's own PRD before saying anything about the state of the work. The
  requirements document is now last, and collapsed.
- **The counts account for every requirement**, not just the interesting ones.
- **The promise is scoped** to the rows it covers, and says outright that it
  says nothing about the rest of the page.
- **The intent is rendered.** A literal `# ` and literal `*asterisks*` were on
  screen; every reader noticed and one called it "a leftover formatting
  character".

## What is still wrong

**The only evidence on the page is a failing log.** Every reader on both runs
hit this: the one requirement marked done shows `pass 0 / fail 8` and the
passing run is never shown. *"I am told it passes and shown it failing."*
That is the single largest remaining defect and it is not fixed.

**Ninety-one words still need guessing at.** Down from 104, nowhere near zero.

**Two fixes landed AFTER this measurement** and are therefore unmeasured: the
sentence resolving the check-versus-requirement contradiction, and the
blocking question now naming the file an answer goes into. Their effect is
unknown until a third run.

## The ceiling, unchanged

**These readers are models prompted as people, not people.** A lower bound on
the confusion, not a measurement of it. A human run is still owed.
