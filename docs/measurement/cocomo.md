# COCOMO I and COCOMO II Cost Estimates

Project: CodeGauge - CO7095 project #17, Software Code Review Tool
Computed with [scripts/cocomo.py](scripts/cocomo.py) — run
`python docs/measurement/scripts/cocomo.py` to reproduce every number below.

## 1. Size measurement

Lines of code counted as **non-blank, non-comment lines**, measured with the counting
script in this directory.

| Component | LOC |
|---|---|
| `core/` (scanner, line metrics, complexity, rules, severity, scoring, history, storage) | 841 |
| `cli/` (menu, formatter) | 257 |
| `model/` (function record, issue, review report, thresholds) | 94 |
| `main.py` | 11 |
| **Production subtotal** | **1,203** |
| `tests/` | 837 |
| `samples/` | 43 |
| **Total delivered source** | **2,083** |

These figures were measured from the Sprint 0 throwaway prototype before it was
discarded. They are the empirical basis for the estimate rather than a claim about the
delivered product: measuring a prototype beats guessing KLOC for an unfamiliar product,
which is the largest single source of error in a cost estimate. **Re-measure against the
delivered code at the end of Sprint 3 and recompute** - the procedure is in
`scripts/cocomo.py`.

Two sizes are carried through the estimates:

- **KLOC = 2.083** — measured at the end of Sprint 3, all production code and the first
  round of tests, after the review fix pass.
- **KLOC = 2.600 (projected)** — the submitted size, once each function carries tests under
  every taught black-box technique, every taught white-box technique, and the symbolic and
  concolic packages. Those packages multiply the test code roughly 2.5-fold while leaving
  production code unchanged.

The projected figure is the one used for the headline estimates, because COCOMO estimates
the effort to *deliver* a product and the test packages are part of the deliverable.

## 2. COCOMO I — Basic

`E = a x KLOC^b` person-months, `D = c x E^d` months, `staff = E / D`.

### Mode selection

**Organic** is the correct mode. The three criteria are a small team (4), a familiar and
stable problem domain, and relaxed external constraints — all of which hold. The project is
not semi-detached: there is no mix of experienced and inexperienced staff working to
partially-known requirements, and there are no interface constraints with other systems. It
is certainly not embedded: there is no hardware coupling and no tight external regulation.
Semi-detached is computed below only to show the sensitivity of the model to that choice.

| Mode | a | b | c | d |
|---|---|---|---|---|
| Organic | 2.4 | 1.05 | 2.5 | 0.38 |
| Semi-detached | 3.0 | 1.12 | 2.5 | 0.35 |

### Results

| Size | Mode | Effort (PM) | Duration (months) | Staff | Productivity |
|---|---|---|---|---|---|
| 2.083 KLOC (measured) | organic | 5.19 | 4.67 | 1.11 | 401 LOC/PM |
| 2.600 KLOC (projected) | organic | **6.55** | **5.11** | **1.28** | 397 LOC/PM |
| 2.600 KLOC (projected) | semi-detached | 8.75 | 5.34 | 1.64 | 297 LOC/PM |

Worked, for organic at the projected size:

```
E = 2.4 x 2.600^1.05 = 2.4 x 2.727 = 6.545 person-months
D = 2.5 x 6.545^0.38 = 2.5 x 2.042 = 5.105 months
staff = 6.545 / 5.105 = 1.28 people
```

## 3. COCOMO I — Intermediate

`E = a x KLOC^b x EAF`, with `a = 3.2`, `b = 1.05` for organic mode, and the Effort
Adjustment Factor being the product of 15 cost drivers.

| Cost driver | Rating | Multiplier | Justification |
|---|---|---|---|
| RELY required software reliability | Low | 0.88 | A defect costs marks, not money or safety. |
| DATA database size | Low | 0.94 | One serialised text file; no database. |
| CPLX product complexity | High | 1.15 | The analysis functions are branch-heavy by design. |
| TIME execution time constraint | Nominal | 1.00 | No real-time requirement. |
| STOR main storage constraint | Nominal | 1.00 | None. |
| VIRT virtual machine volatility | Nominal | 1.00 | Fixed Python 3 and PyCharm throughout. |
| TURN computer turnaround time | Low | 0.87 | Interactive development; tests run in under a second. |
| ACAP analyst capability | Low | 1.19 | First group project of this kind for all four members. |
| AEXP applications experience | Low | 1.13 | No prior static-analysis experience. |
| PCAP programmer capability | Nominal | 1.00 | Competent MSc-level programmers. |
| VEXP virtual machine experience | High | 0.90 | All four use Python daily. |
| LEXP programming language experience | High | 0.95 | Python is the taught language. |
| MODP modern programming practices | High | 0.91 | TDD, code review on every merge, one branch per story. |
| TOOL use of software tools | High | 0.91 | PyCharm, pytest, coverage, GitHub Projects. |
| SCED required development schedule | Nominal | 1.00 | The published deadline, neither compressed nor stretched. |

```
EAF        = 0.88 x 0.94 x 1.15 x 1.00 x 1.00 x 1.00 x 0.87 x 1.19 x 1.13
             x 1.00 x 0.90 x 0.95 x 0.91 x 0.91 x 1.00
           = 0.7880
nominal E  = 3.2 x 2.600^1.05 = 8.727 person-months
adjusted E = 8.727 x 0.7880 = 6.877 person-months
D          = 2.5 x 6.877^0.38 = 5.202 months
staff      = 6.877 / 5.202 = 1.32 people
```

The EAF of 0.788 says the project is about 21% cheaper than a nominal project of the same
size: the team's inexperience (ACAP, AEXP) pushes the estimate up, but low reliability
requirements, fast turnaround, good tooling and modern practice more than cancel it out.

## 4. COCOMO II — Early Design model

`E = A x Size^E x prod(EM)` with `A = 2.94` and `E = B + 0.01 x sum(SF)`, `B = 0.91`.

### Scale factors

| Scale factor | Rating | Value | Justification |
|---|---|---|---|
| PREC precedentedness | Very Low | 6.20 | None of the four has built a static analyser before. |
| FLEX development flexibility | Nominal | 3.04 | The brief fixes the process and the tooling, but not the design. |
| RESL architecture / risk resolution | Nominal | 4.24 | A design document was written up front with the risks listed. |
| TEAM team cohesion | Very High | 1.10 | Four members, one agreed plan, one shared board, no competing stakeholders. |
| PMAT process maturity | Low | 6.24 | CMMI Level 2 is the target of this project, not an established record. |

```
sum(SF) = 6.20 + 3.04 + 4.24 + 1.10 + 6.24 = 20.82
E       = 0.91 + 0.01 x 20.82 = 1.1182
```

The exponent exceeding 1 means **diseconomy of scale**: doubling the size more than doubles
the effort. PREC and PMAT are what drive it, and both are inherent to a first-time student
project.

### Effort multipliers

| Multiplier | Rating | Value |
|---|---|---|
| RCPX product reliability and complexity | High | 1.33 |
| RUSE developed for reuse | Nominal | 1.00 |
| PDIF platform difficulty | Low | 0.87 |
| PERS personnel capability | Nominal | 1.00 |
| PREX personnel experience | Low | 1.22 |
| FCIL facilities | High | 0.87 |
| SCED required schedule | Nominal | 1.00 |

```
prod(EM) = 1.33 x 1.00 x 0.87 x 1.00 x 1.22 x 0.87 x 1.00 = 1.2281
E        = 2.94 x 2.600^1.1182 x 1.2281 = 2.94 x 2.911 x 1.2281 = 10.510 person-months
F        = 0.28 + 0.2 x (1.1182 - 0.91) = 0.3216
D        = 3.67 x 10.510^0.3216 = 7.821 months
staff    = 10.510 / 7.821 = 1.34 people
```

## 5. Comparison and critical discussion

| Model | Effort (PM) | Duration (months) | Staff |
|---|---|---|---|
| COCOMO I Basic, organic | 6.55 | 5.11 | 1.28 |
| COCOMO I Intermediate, organic | 6.88 | 5.20 | 1.32 |
| COCOMO II Early Design | 10.51 | 7.82 | 1.34 |

The three models agree on team size (about 1.3 full-time people) and disagree on effort by
a factor of 1.6. COCOMO II is the highest because its scale exponent of 1.1182 applies a
diseconomy of scale that COCOMO I Basic organic (b = 1.05) barely applies at all, and
because PREC = Very Low and PMAT = Low both load the exponent rather than a multiplier —
inexperience is modelled as something that gets *worse* with project size.

**Where all three models break down for this project.** COCOMO II's 10.51 person-months is
about 1,598 person-hours at 152 hours per person-month. The four members have roughly
**192 person-hours** between them across the project window at 8 hours each per week. The
models therefore over-estimate by a factor of about eight.

This is not an arithmetic error, it is a calibration mismatch, and three causes account for
it:

1. **COCOMO is calibrated on industrial projects** whose person-months include requirements
   negotiation with external stakeholders, formal configuration audits, independent V&V,
   release engineering and maintenance handover. A coursework project carries none of
   those, yet the regression constants were fitted with them included.
2. **COCOMO is known to be unreliable below about 2 KLOC.** Both Boehm's original data set
   and the COCOMO II recalibration are dominated by projects one to three orders of
   magnitude larger than 2.6 KLOC, and the models are not intended to extrapolate down this
   far. The organic estimate of 0.95 people for 1.647 KLOC — less than one person — is the
   model signalling its own floor.
3. **LOC is a poor size proxy for this particular product.** Over a third of the delivered
   code is test code, which is cheap per line to write once the function under test is
   fixed; and the production code was deliberately written with explicit multi-way branching
   rather than compact dispatch, which inflates LOC without inflating effort.

**What the estimate is still worth.** The *relative* picture is sound and was used: the
models agree that this is a one-to-one-and-a-half person job, which is why the 186 story
points were split four ways, at 46, 50, 45 and 45 points each, rather than concentrated, and they agree that
the scale exponent is driven by precedentedness and process maturity, which is exactly what
the CMMI Level 2 effort in this project is meant to improve. A function-point count would
be the better size measure for a product this small, and is the measure the team would use
if the project were re-estimated.
