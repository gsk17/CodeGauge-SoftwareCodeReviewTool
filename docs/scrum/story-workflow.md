# How One User Story Gets Done

The sequence every member follows, nine times each. It exists so that the commit
history of each branch shows the test before the implementation, which is what the
Definition of Done means by "the failing test was written first and observed failing".

Replace `<username>` with your university username and `US01`/`classify-line` with your
story's ID and slug from [product-backlog.md](product-backlog.md).

## 1. Take the story at the daily scrum

Move the card to **In Progress** on the board and set its start date. Say at the
stand-up that you are starting it.

## 2. Branch from main

```bash
git checkout main
git pull origin main
git checkout -b feature/<username>-us01-classify-line
```

Link the branch to the issue in GitHub's **Development** sidebar.

## 3. Write the failing test first

Look up your story's exact signature and assertions in the implementation plan
(`docs/design/plans/2026-11-04-code-review-tool.md`). Write the test file in your
black-box technique package:

```bash
# <username>/test/blackbox/<technique>/test_classify_line.py
```

Open the file with a comment naming the technique and the function under test — the
rubric checks for that comment.

## 4. Watch it fail, and commit the failure

```bash
python -m pytest <username>/test/blackbox -v
```

Expect `ImportError` or `AttributeError`. **Commit the failing test on its own:**

```bash
git add <username>/test
git commit -m "test(US01): failing tests for classify_line"
```

This commit is the evidence. A branch whose first commit contains both the test and the
implementation cannot show that the test ever failed.

## 5. Implement the function

In the module the plan names, at the exact signature it gives. Docstring, and a comment
on each branch. Explicit multi-way branching rather than a dictionary lookup — that is a
deliberate project decision, because the marks reward complexity that can be drawn as a
symbolic execution tree.

## 6. Watch it pass

```bash
python -m pytest <username>/test -v
python -m pytest -q                  # the whole suite, to be sure nothing else broke
```

```bash
git add core/ <username>/test
git commit -m "feat(US01): classify a source line as blank, comment or code"
```

## 7. Add the white-box tests and the symbolic analysis

Still on the same branch:

- white-box test cases under `<username>/test/whitebox/<technique>/`;
- the symbolic execution tree, the path conditions and the concolic iteration table in
  `docs/symbolic/<username>-symbolic-execution.md`, following
  [../symbolic/WORKED-EXAMPLE.md](../symbolic/WORKED-EXAMPLE.md);
- the solved witnesses as test cases under the symbolic and concolic packages, each
  commented with the path condition it discharges.

```bash
python -m coverage run -m pytest <username>/test && python -m coverage report -m
```

Every branch of your function executed, or an infeasible path with the proof.

```bash
git add <username>/test docs/symbolic
git commit -m "test(US01): white-box, symbolic and concolic cases for classify_line"
```

## 8. Open a pull request and get it reviewed

```bash
git push -u origin feature/<username>-us01-classify-line
gh pr create --fill --base main
```

**Another member reviews it** against the Definition of Done and leaves a comment. Review
each other's work in a rotation — Gunjan → Kasam → Saaket → Harshita → Gunjan — so that
every member both gives and receives review, which is the PPQA evidence.

## 9. Merge, and keep the branch

```bash
gh pr merge --merge          # a merge commit, not a squash: it keeps the test-first order
```

**Do not delete the branch.** The brief requires branches as development evidence, so
decline GitHub's offer to delete it.

## 10. Close the story

- Log the hours you spent as a comment on the issue — this is the EVM actual cost.
- Set the issue's end date and close it.
- Move the card to **Done**.
- Report the new remaining-points total at the next stand-up:

```bash
bash scripts/daily_scrum.sh --sprint 1 --member <name> \
     --did "US01 merged" --next "US02" --blocked none --remaining 61
git add docs/scrum/daily-scrum-log.md docs/measurement/burndown-data.csv
git commit -m "docs(sprint-1): daily scrum $(date +%F)"
```

## The shape of a finished story's branch

```
* test(US01): failing tests for classify_line          <- observed failing
* feat(US01): classify a source line ...               <- made it pass
* test(US01): white-box, symbolic and concolic cases
```

Three commits, in that order, merged by a reviewed pull request, on real dates. That is
what the marker is looking for, and it is what makes the testing and research marks
defensible as your own work.
