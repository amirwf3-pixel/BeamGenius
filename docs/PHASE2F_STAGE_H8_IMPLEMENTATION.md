# Phase 2F Stage H.8 — Implementation: §9-21-6-1-3(Pe) Joist Tie Standard Hook

**Date:** 2026-10-06
**Branch:** `arena/b9cd291a-beamgenius`
**Baseline HEAD:** `a59ec52` — *"phase2f: implement H7 tie anchor std hook and torsion wire route"*
**origin/main:** `df8067a` — untouched throughout (only the implementation branch is pushed)
**Source authority:** committed evidence scan `phase2f-source-442-472/` on `origin/main@df8067a`
**Evidence pages re-checked visually this stage:** PDF 463 (Printed 443) — clause text, branch marker, clause number, page footer, header

Stage H.8 follows Stage H.7 (`docs/PHASE2F_STAGE_H7_IMPLEMENTATION.md`), which implemented branch **(Alef)** of §9-21-6-1-3 and explicitly reported branch **(Pe)** — the joist case — as a **third promotion candidate**. H.8 implements **only** that one candidate. Nothing else is in scope.

---

## 1. What was implemented

One new executable rule: `VERIFIED` / `CODE_RULE` / `MABHAS_9_COMPLIANCE` / `execution_allowed=True`, with a complete `RuleReference` (exact clause, PDF page, printed page, requirement, applicability, limitations, dependencies, execution status).

| New rule ID | Clause | PDF / Printed | Delegates to |
| :--- | :--- | :--- | :--- |
| `BG-TRANS-TIE-ANCHOR-JOIST-STD-HOOK-001` | §9-21-6-1-3-**Pe** | 463 / 443 | `BG-TRANS-STANDARD-HOOK-001` |

Engine function: `beamgenius.engine.transverse_reinforcement_mabhas9.evaluate_tie_anchor_joist_std_hook`.

---

## 2. Source reading (PDF 463 / Printed 443), re-verified visually

§9-21-6-1-3 was re-read in full from the source image this stage; **all three branches** were read verbatim and nothing was inherited from a prior stage's transcription.

### 2.1 Page identification

| Item | Read | Method |
| :--- | :--- | :--- |
| PDF page | 463 | committed scan `phase2f-source-442-472/`, `page-463.jpg` (2480×3505) |
| Printed page footer | **443** | rightmost footer glyph cropped at **20×** and read as **۳** (three) by its double-lobe shape → `۴۴۳` = 443 |
| Header | «جزئیات آرماتورهای عرضی ۹-۲۱» | header strip crop — confirms the rule belongs to Chapter 9-21 |
| Clause number | **۹-۲۱-۶-۱-۳** | 11× crop of the clause-number region |

> **Correction recorded.** An early low-zoom read of an adjacent band misread the clause number as ۹-۲۱-۶-۱-۲. The 5× narrow crop proves **۹-۲۱-۶-۱-۳**; the real heading sits four ink-bands further down. **Never record a clause number without a ≥2× narrow crop.**

### 2.2 The branch marker — how «Pe» was established

The marker was isolated by computing the ink-column runs of the band and cropping the **rightmost** run (an earlier attempt cropped a guessed position near x≈2290–2450 and produced a blank image — the line actually starts at x=2152). At **14×** the marker shows **three dots below the bowl**, whereas **Be** carries one. Branch (Pe) is therefore correctly attributed.

### 2.3 The three branches, verbatim

- **Heading:** «مهار میلگرد و سیم آجدار در خاموت باید منطبق بر شرایط زیر باشد»
- **(Alef)** — «در میلگردها یا سیم‌های با قطر کوچکتر یا مساوی ۱۶ میلی‌متر، و برای میلگردهای با قطر ۱۸ تا ۲۵ میلی‌متر با تنش تسلیح کمتر از ۲۸۰ مگاپاسکال، وجوب قلاب استاندارد پیرامون میلگرد طولی»
- **(Be)** — «در میلگردهای به قطر ۱۸ تا ۲۵ میلی‌متر و تنش تسلیح بیش از ۲۸۰ مگاپاسکال، وجود قلاب استانبارد پیرامون میلگرد طولی به علاوه طول مدفون بین وسط ارتفاع مقطع و انتهای…» + «بیرونی قلاب بیشتر یا مساوی ۰.۱۷f_y/(λ√f_c)·d_b»
- **(Pe)** — «پ- در تیرچه‌ها، برای میلگردها یا سیم‌های با قطر کوچکتر یا مساوی ۱۲ میلی‌متر، وجوب قلاب استاندارد.»

i.e. **"(Pe) — In joists (تیرچه‌ها), for bars or wires with a diameter less than or equal to 12 mm, a standard hook shall be provided."**

### 2.4 The determinism ruling (why this branch is implementable)

Branch **(Pe)** states exactly **two** conditions and nothing else:

1. the member is a **joist** (تیرچه), and
2. the bar/wire diameter **d_b ≤ 12 mm**.

There is **no f_y gate**, **no λ**, **no embedment datum**, and **no bend-diameter formula** — unlike branch (Be). The source term تیرچه / joist is preserved **because the source states it**. The rule is therefore **fully deterministic** and was implemented. This satisfies the stage's precondition that implementation proceeds *only if* the actual source image proves determinism.

The **"standard hook"** itself is the hook of Clause 9-21-2-2-2 / Table 9-21-2, which is **delegated** to `BG-TRANS-STANDARD-HOOK-001`; its table is not duplicated. Clause 9-21-6-1-3(Pe) names **no unique hook angle**, so the angle is a caller-supplied typed input validated through the delegate — never assumed, never defaulted.

---

## 3. The applicability decision (binding, source-faithful)

Applicability is **exactly** the printed condition:

```
in_joist == True  AND  d_b <= 12 mm
```

`yield_stress_mpa` is **deliberately not an input** of this rule. The source states no f_y condition for branch (Pe), so none is invented — the rule works correctly with no f_y supplied at all, and a test asserts `yield_stress_mpa` is absent from the signature.

The rule is kept **separate** from `BG-TRANS-TIE-ANCHOR-STD-HOOK-001` (branch Alef) because its applicability differs: branch (Pe) has no f_y gate and a different diameter ceiling (12 mm vs 16 mm).

### 3.1 Outcome semantics

| Condition | Outcome | Diagnostic code |
| :--- | :--- | :--- |
| `in_joist` missing | **BLOCKED** | `MISSING_IN_JOIST` |
| `in_joist` non-bool | **INVALID_INPUT** | `INVALID_IN_JOIST` |
| `in_joist=False` | **NOT_APPLICABLE** | — |
| `in_joist=True`, `d_b > 12 mm` | **BLOCKED** | `TIE_ANCHOR_JOIST_DB_ABOVE_LIMIT` |
| `d_b`, angle or hook geometry missing | **BLOCKED** | `MISSING_BAR_DIAMETER`, `MISSING_HOOK_ANGLE`, … |
| `encloses_longitudinal_bar` missing / non-bool | **BLOCKED** / **INVALID_INPUT** | `MISSING_ENCLOSES_LONGITUDINAL_BAR` / `INVALID_ENCLOSES_LONGITUDINAL_BAR` |
| delegated geometry violated | **FAIL** | `TIE_ANCHOR_JOIST_STANDARD_HOOK_GEOMETRY_NOT_SATISFIED` |
| `encloses_longitudinal_bar=False` | **FAIL** | (via the delegate) |
| valid `d_b ≤ 12 mm` + valid hook | **PASS** | — |
| non-Mabhas-9 jurisdiction | **JURISDICTION_BLOCKED** | — |

- **`in_joist=False` → NOT_APPLICABLE** (not FAIL, not BLOCKED): branch (Pe) simply does not govern the member, whose tie anchorage follows branch (Alef) or (Be) instead. This is the same context-precedent pattern already used by `BG-TRANS-TORSION-TIE-WIRE-ROUTE-001`.
- **`d_b > 12 mm` in a joist → BLOCKED, never FAIL**: the joist provision is printed **only up to 12 mm**. This rule never silently falls back to another branch and never interpolates a limit. A joist with `d_b = 20 mm` is **not** routed into branch (Be) either.

### 3.2 Genuine source gaps — deterministically BLOCKED, never interpolated

| Case | Outcome | Reason |
| :--- | :--- | :--- |
| `in_joist=True`, `d_b = 12.5 mm` | BLOCKED | above the printed 12 mm joist limit |
| `in_joist=True`, `d_b = 16 / 20 / 25 / 30 mm` | BLOCKED | above the printed 12 mm joist limit |
| `in_joist=True`, `d_b < 10 mm` | BLOCKED | outside Table 9-21-2 (via the standard-hook delegate) |
| `d_b = 17 mm` (branch Alef) | BLOCKED | unchanged genuine gap |
| `f_y = 280 MPa` with `d_b 18–25 mm` | BLOCKED | unchanged genuine gap |
| `d_b > 25 mm` (branch Alef) | BLOCKED | unchanged genuine gap |

---

## 4. What was NOT implemented

### 4.1 Branch (Be) of §9-21-6-1-3 — remains BLOCKED

Branch (Be) requires a standard hook **plus an embedment length** **plus** a minimum outer bend diameter `0.17·f_y/(λ·√f′c)·d_b`. It stays blocked because:

- **λ is not defined anywhere in §9-21-6** — no governing value exists in the source;
- the **embedment datum wording is positional** (mid-depth of the section to the end of the standard hook), which is not sufficiently governed to encode without interpretation;
- H.6 classified it blocked; no interpolation and no outside-code substitution is permitted.

No separate rule was created for it. Its embedment branch was **not** promoted by this stage.

### 4.2 Branch (Alef) — unchanged

`BG-TRANS-TIE-ANCHOR-STD-HOOK-001` and `evaluate_tie_anchor_std_hook` are **untouched**. The source-faithful H.7 ruling stands: `(d_b ≤ 16 mm, any f_y) OR (d_b 18–25 mm AND f_y < 280 MPa)`. Regression tests in the new suite re-assert branch-(Alef) behaviour, including that `d_b ≤ 16 mm` with **high** `f_y` still PASSes (no f_y gate on that sub-condition).

### 4.3 Everything else explicitly out of scope

§9-21-6-1-5, §9-21-6-2-3 / §9-4-8, §9-21-6-3-5(Alef) welding/mechanical splice, NBC Chapter 10 welding, §9-22, any UI, and any unrelated refactoring. **No other sentinel was promoted.** No new source extraction beyond re-checking the authoritative page.

---

## 5. Sentinel narrowing

### 5.1 `BG-TRANS-TIE-ANCHOR-PENDING` (remains BLOCKED)

- **Before (H.7):** covered branches **Be & Pe** of §9-21-6-1-3.
- **After (H.8):** clause citation narrowed to **§9-21-6-1-3-Be only**. The `-Pe` reference is removed because branch (Pe) is now executable.
- The description and `blocked_reason` name **both** promoted branches (`BG-TRANS-TIE-ANCHOR-STD-HOOK-001` and `BG-TRANS-TIE-ANCHOR-JOIST-STD-HOOK-001`).
- The stale claim that branch (Pe) is a deterministic-but-unimplemented joist case is removed.
- Retains branch (Be) **and** the genuine gaps (`f_y = 280 MPa` exactly, `d_b = 17 mm`, `d_b > 25 mm`).
- The sentinel is **not deleted**.

### 5.2 `BG-TRANS-TORSION-TIE-PENDING` (remains BLOCKED)

- Description and `blocked_reason` updated so they no longer claim branch (Pe) is unimplemented; both promoted branches are named.
- The **OR-semantics invariant is preserved**: the §9-21-6-1-3 route remains blocked (branch Be plus the boundary gaps), and the metadata states explicitly that promoting one OR route does **not** make the whole (Be) clause executable.

### 5.3 Unchanged sentinels (all still BLOCKED)

`BG-TRANS-WIRE-TIE-PENDING` (§9-21-6-1-5), `BG-TRANS-WIRE-SUBST-PENDING` (§9-21-6-2-3 → §9-4-8), `BG-TRANS-SPIRAL-SPLICE-SEL-PENDING` (§9-21-6-3-5-Alef → §9-21-4-7 → NBC Ch. 10).

---

## 6. Registry / dependency graph

### 6.1 Counts

| Metric | Before H.8 | After H.8 |
| :--- | :--- | :--- |
| Registry total | 120 | **121** |
| Executable (Mabhas 9) | 62 | **63** |
| Blocked | 48 | **48** (unchanged — one sentinel narrowed, none promoted) |
| Reference-executable | 10 | **10** |
| §9-21-6 executable (governing clause) | 20 | **21** |
| §9-21-6 blocked | 5 | **5** |
| `pytest` | 630 passed | **673 passed** |
| `mypy --strict` | clean, 23 files | clean, 23 files |

> **Measurement note.** The H.7 doc quoted "§9-21-6 executable = 22" using a raw substring match on `clause_or_equation`. That match is noisy: two §9-21-3 rules cite `Table 9-21-6` and `Eq. (9-21-6-.../ب)` inside their clause strings and are counted wrongly. Matching on the governing clause prefix (`Clause 9-21-6` / `Clauses 9-21-6`) gives **21** executable and **5** blocked, which is the correct figure quoted above and asserted in the new suite.

### 6.2 Dependency graph (new edge)

```
BG-TRANS-TIE-ANCHOR-JOIST-STD-HOOK-001
    └── BG-TRANS-STANDARD-HOOK-001            (Table 9-21-2 geometry; not duplicated)
```

The delegate is `VERIFIED` + `execution_allowed=True`, so the Gatekeeper's transitive-dependency check permits the new rule. No rule ID is duplicated. The new evaluator imports no reference-package logic and performs no runtime PDF/OCR/file read.

### 6.3 Blocked §9-21-6 clauses after H.8 (all still BLOCKED)

| Clause | Sentinel / state |
| :--- | :--- |
| §9-21-6-1-3-Be | `BG-TRANS-TIE-ANCHOR-PENDING` — BLOCKED (λ undefined; positional embedment datum) |
| §9-21-6-1-5 | `BG-TRANS-WIRE-TIE-PENDING` — BLOCKED (ambiguous wording; no governing number) |
| §9-21-6-2-3 | `BG-TRANS-WIRE-SUBST-PENDING` — BLOCKED (§9-4-8 out of window) |
| §9-21-6-3-5-Alef | `BG-TRANS-SPIRAL-SPLICE-SEL-PENDING` — BLOCKED (§9-21-4-7 → NBC Ch. 10) |
| §9-21-6-1-6-Be / §9-21-6-2-7-Be (as a whole) | `BG-TRANS-TORSION-TIE-PENDING` — BLOCKED (only the §9-21-6-1-4 route promoted; OR semantics preserved) |

**§9-21-6-1-3-Pe is no longer blocked** — it is the one clause promoted by this stage.

---

## 7. Tests

New focused suite `tests/test_mabhas9_tie_anchor_joist_std_hook.py` (**43 tests**).

**Applicability / joist context**
- `d_b = 10` and `d_b = 12` (boundary, inclusive) with a valid 90° hook → **PASS**
- `d_b = 12.5`, `16`, `20`, `30 mm` → **BLOCKED** `TIE_ANCHOR_JOIST_DB_ABOVE_LIMIT` (never FAIL, never a silent fallback)
- `in_joist=False` → **NOT_APPLICABLE**; a joist with a large bar is **not** routed into branch (Be)
- `in_joist` missing → **BLOCKED** `MISSING_IN_JOIST`; non-bool → **INVALID_INPUT**

**Missing required inputs → BLOCKED**
- each of `bar_diameter_mm`, `hook_angle_deg`, `inner_bend_diameter_mm`, `straight_extension_mm` missing → BLOCKED (parametrised)
- `encloses_longitudinal_bar` missing → BLOCKED `MISSING_ENCLOSES_LONGITUDINAL_BAR`
- malformed `d_b < 0` and non-bool enclosure → **INVALID_INPUT**

**Delegation to `BG-TRANS-STANDARD-HOOK-001`**
- **outcome agreement** with `evaluate_standard_hook` on both PASS (three angle/diameter rows) and FAIL paths — geometry is not duplicated
- invalid delegated geometry → **FAIL** `TIE_ANCHOR_JOIST_STANDARD_HOOK_GEOMETRY_NOT_SATISFIED`
- `encloses_longitudinal_bar=False` → **FAIL**
- 180° hook → BLOCKED `STANDARD_HOOK_180_DEG_NOT_IMPLEMENTED`; unsupported 120° angle → BLOCKED `STANDARD_HOOK_ANGLE_NOT_IN_TABLE_9_21_2`; `d_b < 10 mm` → BLOCKED `STANDARD_HOOK_DB_BELOW_TABLE` (all through the delegate)
- **`yield_stress_mpa` is absent from the signature** (no f_y condition in the source) and the rule still PASSes with none supplied
- non-Mabhas-9 jurisdiction → **JURISDICTION_BLOCKED**

**Branch (Alef) regression — behaviour unchanged**
- `d_b ≤ 16 mm` with **high** `f_y` (500 MPa) → PASS (no f_y gate on this sub-condition)
- `d_b 18–25 mm` with `f_y < 280 MPa` → PASS
- `f_y = 280 MPa` → BLOCKED `TIE_ANCHOR_FY_280_IN_GAP`; `d_b = 17 mm` → BLOCKED `TIE_ANCHOR_DB_IN_GAP`; `d_b > 25 mm` → BLOCKED `TIE_ANCHOR_DB_ABOVE_TABLE`

**Branch (Be) remains blocked**
- `f_y = 281 / 300 / 500 MPa` with `d_b = 20 mm` → BLOCKED `TIE_ANCHOR_FY_ABOVE_280_B_BRANCH_NOT_IMPLEMENTED`
- a joist with a large bar never reaches branch (Be) either

**Sentinel / metadata / registry**
- `BG-TRANS-TIE-ANCHOR-PENDING` cites §9-21-6-1-3-**Be only**; `-Pe` absent; both promoted branches named; genuine gaps recorded; the stale "(Pe) unimplemented joist case" phrasing gone
- `BG-TRANS-TORSION-TIE-PENDING` no longer claims §9-21-6-1-4 or branch (Pe) is blocked, and still states that one OR route does not make the whole (Be) clause executable
- all five §9-21-6 sentinels remain blocked with a `blocked_reason`
- registry: **121 total / 63 executable / 48 blocked**, no duplicates; §9-21-6 = **21 executable + 5 blocked** with an exact blocked-ID set
- new rule metadata: VERIFIED, `execution_allowed`, `pdf_page=463`, `printed_page=443`, clause `9-21-6-1-3-پ`, deps `("BG-TRANS-STANDARD-HOOK-001",)`, dep executable, description/symbolic formula present, Applicability + Required Inputs documented, term "joist" preserved, no invented f_y input
- the new rule is **distinct** from the branch-(Alef) rule (different ID, different clause, and the Alef rule still requires f_y)

Existing suites updated (no test weakened):
- `tests/test_mabhas9_tie_anchor_and_torsion_wire_route.py` — `test_registry_counts_and_no_duplicates` 120/62 → **121/63**; `test_section_9216_counts` exe 22 → **23**; `test_tie_anchor_pending_narrowed_to_be_and_pe` → **`..._to_be_only`** with the `-Pe` assertions inverted and the new rule named
- `tests/test_mabhas9_standard_hook_and_splits.py` — `test_executable_count_is_62` → **`test_executable_count_is_63`**
- `tests/test_registry_and_gatekeeper.py` — exact executable-rule set gains `BG-TRANS-TIE-ANCHOR-JOIST-STD-HOOK-001` (appended last, matching `_ALL_RULES_TUPLE` order)

---

## 8. Files changed

| File | Change |
| :--- | :--- |
| `src/beamgenius/engine/transverse_reinforcement_mabhas9.py` | +1 catalog-rule import; constants comment block records the H.8 promotion; **new evaluator** `evaluate_tie_anchor_joist_std_hook` at EOF |
| `src/beamgenius/registry/catalog.py` | **new `RuleReference`** `RULE_BG_TRANS_TIE_ANCHOR_JOIST_STD_HOOK_001` added to `_ALL_RULES_TUPLE` under a Stage-H.8 comment; `RULE_BG_TRANS_TIE_ANCHOR_PENDING` narrowed to Be; `RULE_BG_TRANS_TORSION_TIE-PENDING` description + `blocked_reason` updated |
| `tests/test_mabhas9_tie_anchor_joist_std_hook.py` | **new** — 43 focused H.8 tests |
| `tests/test_mabhas9_tie_anchor_and_torsion_wire_route.py` | counts 120/62 → 121/63; §9-21-6 exe 22 → 23; sentinel test renamed and inverted |
| `tests/test_mabhas9_standard_hook_and_splits.py` | executable-count assertion 62 → 63 |
| `tests/test_registry_and_gatekeeper.py` | exact executable-rule set + 1 new ID |
| `docs/VERIFIED_RULES.md` | +1 rule entry; blocked section updated; H.8 closing note and counts |
| `docs/PHASE2_SOURCE_VERIFICATION_MATRIX.md` | §9-21-6-1-3 row; H.8 sentinel row; registry + checks |
| `docs/PHASE2F_STAGE_H8_IMPLEMENTATION.md` | **new** — this document |

No source JPG/PDF/OCR artifact is committed; all evidence images live in the gitignored `working/h8/` scratch directory. The Stage H.6 audit document remains untracked and is **not** committed.

---

## 9. Governance / gate results

| Gate | Result |
| :--- | :--- |
| `pytest` | **673 passed** (630 before H.8 + 43 new) |
| `mypy --strict` | clean, 23 files |
| `git diff --check` | clean (also checked on the new untracked test file) |
| Duplicate rule-ID check | no duplicates in the 121-rule registry |
| Registry integrity | 121 = 63 executable + 48 blocked + 10 reference-executable; `_ALL_RULES_TUPLE` contains the new ID |
| Baseline-vs-current registry diff | exactly **+1 rule, +1 executable**; blocked count, non-executable-dependency count and missing-page count are all **unchanged** (those are pre-existing properties of the wider registry, not regressions) |
| New `RuleReference` metadata validation | exact clause, PDF page, printed page, requirement, applicability, limitations, dependencies, execution status; no invented page numbers |
| Engine AST import governance | 10 engine files scanned — no reference-package / PDF / OCR / Pillow / numpy / OS / IO imports |
| Delegation check | hook geometry delegated to `BG-TRANS-STANDARD-HOOK-001`, never duplicated; delegate is executable |
| `origin/main` | **still `df8067a`** — untouched |
| Unresolved branches | §9-21-6-1-3-Be, §9-21-6-1-5, §9-21-6-2-3, §9-21-6-3-5-Alef and the (Be) clauses as a whole all remain **BLOCKED** |
