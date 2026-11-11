"""COCOMO I (Basic and Intermediate) and COCOMO II estimates for the project."""

KLOC_NOW = 2.083          # measured: production + test + sample code
KLOC_FINAL = 2.600        # projected once the per-technique test packages exist


def basic(kloc, a, b, c, d, label):
    effort = a * kloc ** b
    duration = c * effort ** d
    print("%-16s E = %.2f * %.3f^%.2f = %.3f PM" % (label, a, kloc, b, effort))
    print("%-16s D = %.1f * %.3f^%.2f = %.3f months" % ("", c, effort, d, duration))
    print("%-16s staff = E/D = %.3f people" % ("", effort / duration))
    print("%-16s productivity = %.0f LOC/PM\n" % ("", kloc * 1000 / effort))
    return effort, duration


print("=== COCOMO I Basic, organic mode, KLOC = %.3f ===" % KLOC_NOW)
basic(KLOC_NOW, 2.4, 1.05, 2.5, 0.38, "organic")
print("=== COCOMO I Basic, organic mode, projected KLOC = %.3f ===" % KLOC_FINAL)
e_org, d_org = basic(KLOC_FINAL, 2.4, 1.05, 2.5, 0.38, "organic")
print("=== COCOMO I Basic, semi-detached, projected KLOC = %.3f ===" % KLOC_FINAL)
basic(KLOC_FINAL, 3.0, 1.12, 2.5, 0.35, "semi-detached")

print("=== COCOMO I Intermediate, organic, KLOC = %.3f ===" % KLOC_FINAL)
DRIVERS = [
    ("RELY  required reliability", "Low", 0.88, "coursework; a defect costs marks, not money"),
    ("DATA  database size", "Low", 0.94, "one serialised text file"),
    ("CPLX  product complexity", "High", 1.15, "branch-heavy analysis code by design"),
    ("TIME  execution time constraint", "Nominal", 1.00, "no real-time constraint"),
    ("STOR  main storage constraint", "Nominal", 1.00, "none"),
    ("VIRT  virtual machine volatility", "Nominal", 1.00, "fixed Python 3 and PyCharm"),
    ("TURN  turnaround time", "Low", 0.87, "interactive development, instant feedback"),
    ("ACAP  analyst capability", "Low", 1.19, "first group project of this kind"),
    ("AEXP  applications experience", "Low", 1.13, "no prior static-analysis experience"),
    ("PCAP  programmer capability", "Nominal", 1.00, "competent MSc programmers"),
    ("VEXP  virtual machine experience", "High", 0.90, "all four use Python daily"),
    ("LEXP  language experience", "High", 0.95, "Python is the taught language"),
    ("MODP  modern programming practices", "High", 0.91, "TDD, code review, CI discipline"),
    ("TOOL  software tools", "High", 0.91, "PyCharm, pytest, coverage, GitHub"),
    ("SCED  schedule constraint", "Nominal", 1.00, "the published deadline"),
]
eaf = 1.0
for name, rating, value, why in DRIVERS:
    eaf *= value
    print("  %-34s %-8s %.2f   %s" % (name, rating, value, why))
nominal = 3.2 * KLOC_FINAL ** 1.05
print("\n  EAF = product of the 15 multipliers = %.4f" % eaf)
print("  nominal E = 3.2 * %.3f^1.05 = %.3f PM" % (KLOC_FINAL, nominal))
print("  adjusted E = %.3f * %.4f = %.3f PM" % (nominal, eaf, nominal * eaf))
dur = 2.5 * (nominal * eaf) ** 0.38
print("  D = 2.5 * %.3f^0.38 = %.3f months" % (nominal * eaf, dur))
print("  staff = %.3f people\n" % ((nominal * eaf) / dur))

print("=== COCOMO II, early design, projected KLOC = %.3f ===" % KLOC_FINAL)
SF = [
    ("PREC  precedentedness", "Very Low", 6.20, "nobody has built this before"),
    ("FLEX  development flexibility", "Nominal", 3.04, "the brief fixes much, but not the design"),
    ("RESL  architecture / risk resolution", "Nominal", 4.24, "design doc written up front, risks listed"),
    ("TEAM  team cohesion", "Very High", 1.10, "four members, one agreed plan, shared board"),
    ("PMAT  process maturity", "Low", 6.24, "CMMI Level 2 is the target, not yet the record"),
]
total_sf = 0.0
for name, rating, value, why in SF:
    total_sf += value
    print("  %-36s %-10s %.2f   %s" % (name, rating, value, why))
exponent = 0.91 + 0.01 * total_sf
print("\n  sum SF = %.2f, E exponent = 0.91 + 0.01 * %.2f = %.4f" % (total_sf, total_sf, exponent))

EM = [
    ("RCPX  product reliability and complexity", "High", 1.33),
    ("RUSE  developed for reuse", "Nominal", 1.00),
    ("PDIF  platform difficulty", "Low", 0.87),
    ("PERS  personnel capability", "Nominal", 1.00),
    ("PREX  personnel experience", "Low", 1.22),
    ("FCIL  facilities", "High", 0.87),
    ("SCED  required schedule", "Nominal", 1.00),
]
prod_em = 1.0
for name, rating, value in EM:
    prod_em *= value
    print("  %-40s %-8s %.2f" % (name, rating, value))
effort2 = 2.94 * KLOC_FINAL ** exponent * prod_em
print("\n  product of EM = %.4f" % prod_em)
print("  E = 2.94 * %.3f^%.4f * %.4f = %.3f PM" % (KLOC_FINAL, exponent, prod_em, effort2))
f = 0.28 + 0.2 * (exponent - 0.91)
dur2 = 3.67 * effort2 ** f
print("  F = 0.28 + 0.2 * (%.4f - 0.91) = %.4f" % (exponent, f))
print("  D = 3.67 * %.3f^%.4f = %.3f months" % (effort2, f, dur2))
print("  staff = %.3f people" % (effort2 / dur2))
print("\n  at 152 person-hours per person-month: %.0f person-hours" % (effort2 * 152))
print("  four members over 1.5 months at 8 h/week each: %.0f person-hours available"
      % (4 * 8 * 6))
