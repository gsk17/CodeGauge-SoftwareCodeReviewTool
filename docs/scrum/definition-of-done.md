# Definition of Done

Agreed at Sprint 0 planning, 7 November 2026, by all four members. A story is
**Done** only when every line below is true. Nothing is "nearly done": a story that
fails any line stays in the sprint backlog and earns no points in that sprint's
velocity, which is the 0/100 rule the burndown and the EVM figures depend on.

This is the single most important agreement in the project, because the rubric marks
testing, coverage and the research component **individually**. A story that is merged
without its tests and its symbolic analysis costs its owner marks that no other member
can recover.

## Per story

- [ ] The story has a GitHub issue with an assignee, a story point value agreed in
      planning poker, a sprint iteration, and a start and end date.
- [ ] Work happened on its own branch, `feature/<username>-us<NN>-<slug>`, linked to
      the issue through the Development sidebar.
- [ ] The **failing test was written first and observed failing.** The commit order in
      the branch shows the test before the implementation.
- [ ] The function is implemented with a docstring, a comment on each branch, and the
      exact signature in the implementation plan.
- [ ] All tests pass: `python -m pytest -v`.
- [ ] Black-box test cases exist under `<username>/test/blackbox/<technique>/`, one
      directory per taught technique, each file commented with the technique and the
      function under test.
- [ ] White-box test cases exist under `<username>/test/whitebox/<technique>/`.
- [ ] The symbolic execution tree, the path conditions and the concolic iteration table
      are written up in `docs/symbolic/<username>-symbolic-execution.md`, and the solved
      witnesses are committed as test cases under `whitebox/<symbolic>/` and
      `whitebox/<concolic>/`.
- [ ] Statement coverage of the function is at least 85%, or every uncovered line has a
      recorded reason (an infeasible path, with the proof).
- [ ] A pull request was opened and **reviewed by another member**, who left a comment.
- [ ] The branch is merged into `main` and **not deleted** - the brief requires branches
      as development evidence.
- [ ] Hours spent are logged as a comment on the issue, feeding the EVM actual cost.
- [ ] The issue is closed and the board card moved to Done.

## Per sprint

- [ ] Every story in the sprint backlog is either Done or explicitly carried over, with
      the carry-over recorded in the retrospective.
- [ ] The full suite is green and project coverage is at least 85%.
- [ ] The daily scrum log has an entry for every working day of the sprint.
- [ ] The burndown data has a row for every working day.
- [ ] Velocity is recorded, and the EVM row (PV, EV, AC, CV, SV, CPI, SPI, EAC) computed.
- [ ] The increment is tagged `v0.<sprint>.0`.
- [ ] Sprint review and retrospective notes are written and committed.
- [ ] A board screenshot is saved to `docs/measurement/board-sprint<N>.png`.
- [ ] CMMI Level 2 evidence rows touched by the sprint are filled in.

## Per release (submission)

- [ ] All 36 stories Done, with roughly equal points per member.
- [ ] The zip uncompresses and opens in PyCharm on a Percy Gee lab machine with no error.
- [ ] Every test package runs from the README's commands with no error.
- [ ] Report under 5000 words, in the brief's structure, cover sheet signed by all four.
- [ ] Video covers every bullet in the brief's deliverable list.
- [ ] Turnitin similarity under 10%.
- [ ] Submission under 50MB, submitted by one member only.
- [ ] Tagged `v1.0.0`.
