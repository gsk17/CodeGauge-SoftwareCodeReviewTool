"""Compute the PERT network for the CO7095 project: expected durations,
forward pass, backward pass, slack and the critical path."""

# id, name, optimistic, most likely, pessimistic, predecessors
ACTS = [
    ("A", "Requirements and user story backlog", 2, 3, 5, []),
    ("B", "Repository, PyCharm project, skeleton, tooling", 1, 1, 3, ["A"]),
    ("C", "Data model", 1, 2, 3, ["B"]),
    ("E", "M2 complexity metrics (US10-US18)", 3, 5, 8, ["C"]),
    ("D", "M1 scanner and line metrics (US01-US09)", 4, 6, 10, ["C", "E"]),
    ("F", "M3 rule engine and severity (US19-US27)", 3, 4, 7, ["C"]),
    ("G", "M4 scoring, history, persistence (US28-US36)", 4, 5, 9, ["C"]),
    ("H", "CLI, formatter, samples (integration)", 2, 3, 6, ["D", "E", "F", "G"]),
    ("I", "Test packages and coverage gate", 4, 6, 11, ["H"]),
    ("J", "Symbolic execution and concolic write-ups", 5, 8, 14, ["I"]),
    ("K", "Measurement artifacts (PERT, COCOMO, EVM, burndown)", 2, 4, 7, ["H"]),
    ("L", "CMMI Level 2 audit pack", 2, 3, 5, ["B"]),
    ("M", "Report", 3, 5, 9, ["J", "K", "L"]),
    ("N", "Video demonstration", 1, 2, 4, ["M"]),
    ("O", "Packaging and lab verification", 1, 2, 4, ["N"]),
]

exp = {}
var = {}
preds = {}
names = {}
order = []
for aid, name, o, m, p, pre in ACTS:
    exp[aid] = (o + 4 * m + p) / 6.0
    var[aid] = ((p - o) / 6.0) ** 2
    preds[aid] = pre
    names[aid] = (name, o, m, p)
    order.append(aid)

succs = {a: [] for a in order}
for a in order:
    for p in preds[a]:
        succs[p].append(a)

# forward pass (topological: ACTS is already listed in dependency order)
ES, EF = {}, {}
for a in order:
    ES[a] = max([EF[p] for p in preds[a]], default=0.0)
    EF[a] = ES[a] + exp[a]

project = max(EF.values())

# backward pass
LS, LF = {}, {}
for a in reversed(order):
    LF[a] = min([LS[s] for s in succs[a]], default=project)
    LS[a] = LF[a] - exp[a]

print("| Act | Activity | O | M | P | TE | Var | ES | EF | LS | LF | Slack | Critical |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for a in order:
    name, o, m, p = names[a]
    slack = LS[a] - ES[a]
    crit = "**yes**" if abs(slack) < 1e-9 else "no"
    print("| %s | %s | %d | %d | %d | %.2f | %.2f | %.2f | %.2f | %.2f | %.2f | %.2f | %s |"
          % (a, name, o, m, p, exp[a], var[a], ES[a], EF[a], LS[a], LF[a], slack, crit))

crit_path = [a for a in order if abs(LS[a] - ES[a]) < 1e-9]
print("\nProject duration: %.2f days" % project)
print("Critical path:", " -> ".join(crit_path))
cv = sum(var[a] for a in crit_path)
print("Critical path variance: %.4f, standard deviation: %.3f days" % (cv, cv ** 0.5))
print("Sum of TE over all activities: %.2f days" % sum(exp.values()))
