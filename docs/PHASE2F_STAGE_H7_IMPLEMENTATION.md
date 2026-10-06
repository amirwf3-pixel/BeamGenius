# Phase 2F Stage H.7 — Implementation: §9-21-6-1-3(Alef) Split + Torsion Welded-Wire Route

**Date:** 2026-10-06
**Branch:** `arena/b9cd291a-beamgenius`
**Baseline HEAD:** `241a2fd` (parent `a66284b`) — *"feat(detiling): implement verified standard hook and spiral tie rules"*
**origin/main:** `df8067a` — untouched throughout (only the implementation branch is pushed)
**Source authority:** committed evidence scan `phase2f-source-442-472/` on `origin/main@df8067a`
**Evidence pages re-checked visually this stage:** PDF 463 (Printed 443), PDF 464 (Printed 444), PDF 443 (Printed 443), PDF 467–468 (Printed 447–448)

Stage H.7 follows Stage H.6 (`docs/PHASE2F_STAGE_H6_REMAINING_BLOCKER_AUDIT.md`, untracked audit-only deliverable), which audited the five remaining §9-21-6 blockers and found exactly **two implementation candidates** plus **four metadata corrections**. H.7 implements only those two candidates and applies only those four corrections. Nothing else is in scope.

---

## 1. What was implemented

Two new executable rules, both `VERIFIED` / `CODE_RULE` / `MABHAS_9_COMPLIANCE` / `execution_allowed=True`, both with a complete `RuleReference` (exact clause, PDF page, printed page, requirement, applicability, limitations, dependencies, execution status):

| New rule ID | Clause | PDF / Printed | Delegates to |
| :--- | :--- | :--- | :--- |
| `BG-TRANS-TIE-ANCHOR-STD-HOOK-001` | §9-21-6-1-3-**Alef** | 463 / 443 | `BG-TRANS-STANDARD-HOOK-001` |
| `BG-TRANS-TORSION-TIE-WIRE-ROUTE-001` | §9-21-6-1-4 (route of §9-21-6-1-6-Be & §9-21-6-2-7-Be) | 464 / 444 | `BG-TRANS-WIRE-TIE-UTIE-001` |

Engine functions: `beamgenius.engine.transverse_reinforcement_mabhas9.evaluate_tie_anchor_std_hook` and `.evaluate_torsion_tie_wire_route`.

---

## 2. Candidate #1 — `BG-TRANS-TIE-ANCHOR-STD-HOOK-001` (§9-21-6-1-3-Alef)

### 2.1 Source reading (PDF 463 / Printed 443), re-verified visually

§9-21-6-1-3 has **three** branches. The branch letters were read at high magnification (≥10× crop of the bare marker glyph): **Be** carries one dot below the bowl, **Pe** carries three. A downscaled crop makes **Pe** look like **Be** — this misread is what the H.6 audit fell into.

- **(Alef)** — anchorage of a deformed bar/wire in a tie shall be made with a **standard hook** around the longitudinal bar, for: bars/wires with **d_b ≤ 16 mm**, and bars with **d_b 18–25 mm and f_y < 280 MPa**.
- **(Be)** — bars with **d_b 18–25 mm and f_y > 280 MPa**: standard hook **plus** an embedment length (mid-depth of section to the end of the standard hook) **plus** a minimum outer bend diameter **0.17·f_y / (λ·√f′c) · d_b**.
- **(Pe)** — **in joists** (تیرچه), bars/wires with **d_b ≤ 12 mm** → standard hook.

### 2.2 The applicability decision (binding, source-faithful)

The literal task specification attached the `f_y < 280 MPa` condition to **both** sub-conditions of branch (Alef) (and additionally attached an embedment requirement to sub-condition 2, which belongs to branch (Be) only). The JPG does not read that way: the `f_y < 280 MPa` condition attaches **only to the 18–25 mm sub-condition**; the `d_b ≤ 16 mm` sub-condition carries **no f_y gate**.

The conflict was raised with the user, who ruled **source-faithful**:

> `(d_b ≤ 16 mm) OR (d_b 18–25 mm AND f_y < 280 MPa)`

Consequences encoded in the evaluator:

- `d_b ≤ 16 mm` with **any** f_y (including f_y ≥ 280 MPa) → branch (Alef) → **PASS** (when the delegated hook geometry is valid).
- `d_b 18–25 mm` with `f_y < 280 MPa` → branch (Alef) → **PASS**.
- `d_b 18–25 mm` with `f_y ≥ 280 MPa` → belongs to branch **(Be)** → **BLOCKED**.
- `f_y = 280 MPa` exactly with `d_b 18–25 mm` → in **neither** branch → **BLOCKED** (genuine gap).
- `f_y = 280 MPa` with `d_b ≤ 16 mm` → still branch (Alef) → **PASS** (the f_y gate does not apply to this sub-condition).

`yield_stress_mpa` remains a **required typed input** (missing → BLOCKED); it only disambiguates the 18–25 mm sub-condition.

### 2.3 What the rule does and does not do

- **Delegates** all hook geometry to `BG-TRANS-STANDARD-HOOK-001` (Clause 9-21-2-2-2 / Table 9-21-2). Inner bend diameter, straight extension, hook angle table and the longitudinal-bar enclosure requirement are **not duplicated**.
- The source names **no unique hook angle**, so the caller supplies `hook_angle_deg`; it is validated **through the delegated evaluator** (never assumed, never defaulted).
- Missing hook geometry → **BLOCKED**. Invalid delegated geometry → **FAIL** (with the delegate's own semantics, re-raised under this rule's ID).

### 2.4 Genuine source gaps — deterministically BLOCKED, never interpolated

| Case | Outcome | Reason |
| :--- | :--- | :--- |
| `f_y = 280 MPa` exactly (d_b 18–25 mm) | BLOCKED | in neither `f_y < 280` (Alef) nor `f_y > 280` (Be) |
| `d_b = 17 mm` | BLOCKED | gap between the printed `≤ 16 mm` and `18–25 mm` sub-conditions |
| `d_b > 25 mm` | BLOCKED | assigned to neither branch |
| `d_b < 10 mm` | BLOCKED | outside Table 9-21-2 (via the standard-hook dependency) |
| `d_b 18–25 mm`, `f_y ≥ 280 MPa` | BLOCKED | belongs to the unimplemented branch (Be) |

---

## 3. What was NOT implemented

### 3.1 Branch (Be) of §9-21-6-1-3

Branch (Be) requires a standard hook **plus an embedment length** **plus** a minimum outer bend diameter `0.17·f_y/(λ·√f′c)·d_b`. It is **not** implemented because:

- **λ is not defined anywhere in §9-21-6** — no governing value exists in the source;
- the **embedment datum wording is positional** (mid-depth of the section to the end of the standard hook), which was judged not sufficiently governed to encode without interpretation;
- H.6 classified it **blocked**; no interpolation and no outside-code substitution is permitted.

No separate rule was created for it. `BG-TRANS-TIE-ANCHOR-PENDING` is retained for branch (Be) and branch (Pe).

### 3.2 Branch (Pe) of §9-21-6-1-3

Branch (Pe) — in joists, bars/wires with `d_b ≤ 12 mm` → standard hook — is **deterministic** and is a legitimate further promotion candidate. It was **out of H.7 scope** (H.7 was scoped to branch Alef) and therefore remains under the sentinel. It is reported here as a **third promotion candidate** (the H.6 audit, working from the erroneous two-branch reading, reported only two).

### 3.3 Everything else explicitly out of scope

§9-21-6-1-5, §9-21-6-2-3 / §9-4-8, §9-21-6-3-5(Alef) welding/mechanical splice, NBC Chapter 10 welding, §9-22, any UI, and any unrelated refactoring. No new source extraction was performed beyond re-checking the authoritative pages.

---

## 4. Candidate #2 — `BG-TRANS-TORSION-TIE-WIRE-ROUTE-001` (§9-21-6-1-4 route)

### 4.1 The clause it serves

§9-21-6-1-6-Be (PDF 464 / Printed 444) and §9-21-6-2-7-Be (PDF 467–468 / Printed 447–448) both read:

> anchorage per **§9-21-6-1-3-Alef/-Be OR §9-21-6-1-4**, only where the concrete around the anchorage is not liable to spall from a flange (بال) or a slab (دال).

### 4.2 What the rule implements

**Only the §9-21-6-1-4 route** of that OR. It is a typed route/precondition evaluator that explicitly distinguishes three things:

1. **the torsion-tie context** — `concrete_around_anchorage_not_liable_to_spall` (bool). If `False`, the (Be) route is unavailable and the result is **NOT_APPLICABLE** (the tie must use the (Alef) routes instead);
2. **that the welded-wire route was selected** — `alternative` (`WireTieUtieAlternative.ALEF` / `.BE`). Missing route-selection data → **BLOCKED**;
3. **the underlying U-tie geometry result** — delegated verbatim to `BG-TRANS-WIRE-TIE-UTIE-001`. A violated U-tie condition is re-raised as **FAIL** with the delegate's own semantics; nothing is recomputed or duplicated.

Missing route data → BLOCKED. Malformed / non-bool inputs → INVALID_INPUT. Non-Mabhas-9 jurisdiction → JURISDICTION_BLOCKED.

### 4.3 The OR-semantics invariant (critical)

Promoting one branch of an OR does **not** promote the clause that contains the OR. Therefore:

- `BG-TRANS-TORSION-TIE-WIRE-ROUTE-001` being executable **does not** make `BG-TRANS-TORSION-TIE-PENDING` executable — the sentinel remains **BLOCKED** for the unresolved §9-21-6-1-3 route and for the unresolved overall clause semantics;
- §9-21-6-1-6-Be and §9-21-6-2-7-Be are **not** globally marked executable — their exact OR/dependency semantics are not fully represented by one executable route.

---

## 5. Sentinel narrowing

### 5.1 `BG-TRANS-TIE-ANCHOR-PENDING` (remains BLOCKED)

- **Before:** covered the whole §9-21-6-1-3 clause.
- **After:** clause citation narrowed to **§9-21-6-1-3-Be & §9-21-6-1-3-Pe**; retains branch (Be), branch (Pe) and the genuine gaps (`f_y = 280 MPa` exactly, `d_b = 17 mm`, `d_b > 25 mm`, and any other unsupported combination).
- The stale claim that branch (Alef) itself is entirely blocked is removed; branch (Alef) is now named as the promoted `BG-TRANS-TIE-ANCHOR-STD-HOOK-001`.
- The sentinel is **not deleted**.

### 5.2 `BG-TRANS-TORSION-TIE-PENDING` (remains BLOCKED)

- **Before:** implied §9-21-6-1-4 was still blocked.
- **After:** metadata narrowed to the remaining unresolved route — the **§9-21-6-1-3 route**. The description and `blocked_reason` explicitly distinguish the **executable §9-21-6-1-4 route** (promoted to `BG-TRANS-TORSION-TIE-WIRE-ROUTE-001`) from the **blocked §9-21-6-1-3 route**, and state that implementing one OR route does not make the whole (Be) clause executable.

### 5.3 Unchanged sentinels (all still BLOCKED)

`BG-TRANS-WIRE-TIE-PENDING` (§9-21-6-1-5), `BG-TRANS-WIRE-SUBST-PENDING` (§9-21-6-2-3 → §9-4-8), `BG-TRANS-SPIRAL-SPLICE-SEL-PENDING` (§9-21-6-3-5-Alef → §9-21-4-7 → NBC Ch. 10).

---

## 6. Metadata corrections M1–M4 (all four applied)

| ID | Rule | Correction |
| :--- | :--- | :--- |
| **M1** | `BG-TRANS-SPIRAL-SPLICE-SEL-PENDING` | `pdf_page`/`printed_page` **469/449 → 468/448** for §9-21-6-3-5-Alef; 469/449 retained where appropriate for the §9-21-6-3-5-Be / Table 9-21-7 material. The actual blocked dependency **§9-21-4-7 → NBC Chapter 10** is unchanged (not altered). |
| **M2** | `BG-TRANS-TORSION-TIE-135HOOK-001` | Stale descriptions claiming both §9-21-6-1-3 **and** §9-21-6-1-4 are still blocked are corrected (§9-21-6-1-4 is now executable). Applied to the **engine docstring**, the **catalog description**, and `docs/VERIFIED_RULES.md`. The rule's scope is unchanged — it still implements only its already-implemented 135° torsion-hook branch. The whole §9-21-6-2-7-Be route is **not** marked executable. |
| **M3** | `BG-TRANS-DORGIR-001` | Source coverage now includes **§9-21-6-4-1, -4-2 and -4-3** in the clause citation; the description adds the -4-3 hook-engagement / interconnected-headed-bar prohibition the rule already implements. Metadata/documentation only — behaviour unchanged (the source audit proved no behaviour was missing). |
| **M4** | `BG-TRANS-TIE-ANCHOR-PENDING` | Stale wording «(Alef) covers d_b ≤ 16 mm and 8–25 mm» corrected to «d_b ≤ 16 mm / d_b 18–25 mm». No "8–25" range is introduced. |

---

## 7. Correction to the H.6 audit

The H.6 audit concluded that §9-21-6-1-3 has **two** branches. Re-reading PDF p. 463 at ≥10× magnification on the bare branch-marker glyph shows **three** (Be = one dot below the bowl; Pe = three dots). Consequences:

- branch **(Pe)** (joists, d_b ≤ 12 mm → standard hook) is a real, deterministic, **third promotion candidate** that H.6 did not report;
- the H.6 "two branches" premise is superseded by this document; the existing `(Pe) joist bars d_b ≤ 12 mm` wording inside `BG-TRANS-TIE-ANCHOR-PENDING` was already correct and is preserved.

**Lesson recorded:** any Persian clause enumeration must be verified by cropping the bare branch-marker glyph at ≥10× and doing an A/B dot-count comparison, never from a downscaled crop.

---

## 8. Registry / dependency graph

### 8.1 Counts

| Metric | Before H.7 | After H.7 |
| :--- | :--- | :--- |
| Registry total | 118 | **120** |
| Executable (Mabhas 9) | 60 | **62** |
| Blocked | 48 | **48** (unchanged — two sentinels narrowed, none promoted) |
| Reference-executable | 10 | **10** |
| §9-21-6 executable | 20 | **22** |
| §9-21-6 blocked | 5 | **5** |
| `pytest` | 577 passed | **630 passed** |
| `mypy --strict` | clean, 23 files | clean, 23 files |

### 8.2 Dependency graph (new edges)

```
BG-TRANS-TIE-ANCHOR-STD-HOOK-001
    └── BG-TRANS-STANDARD-HOOK-001            (Table 9-21-2 geometry; not duplicated)

BG-TRANS-TORSION-TIE-WIRE-ROUTE-001
    └── BG-TRANS-WIRE-TIE-UTIE-001            (§9-21-6-1-4 U-tie geometry; not duplicated)
```

Both delegates are `VERIFIED` + `execution_allowed=True`, so the Gatekeeper's transitive-dependency check permits both new rules. No rule ID is duplicated. Neither new rule imports or duplicates reference-evaluator logic.

### 8.3 Blocked §9-21-6 clauses after H.7 (all still BLOCKED)

| Clause | Sentinel / state |
| :--- | :--- |
| §9-21-6-1-3-Be | `BG-TRANS-TIE-ANCHOR-PENDING` — BLOCKED (λ undefined; positional embedment datum) |
| §9-21-6-1-3-Pe | `BG-TRANS-TIE-ANCHOR-PENDING` — BLOCKED (not implemented in H.7; promotion candidate) |
| §9-21-6-1-5 | `BG-TRANS-WIRE-TIE-PENDING` — BLOCKED (ambiguous wording; no governing number) |
| §9-21-6-2-3 | `BG-TRANS-WIRE-SUBST-PENDING` — BLOCKED (§9-4-8 out of window) |
| §9-21-6-3-5-Alef | `BG-TRANS-SPIRAL-SPLICE-SEL-PENDING` — BLOCKED (§9-21-4-7 → NBC Ch. 10) |
| §9-21-6-1-6-Be / §9-21-6-2-7-Be (as a whole) | `BG-TRANS-TORSION-TIE-PENDING` — BLOCKED (only the §9-21-6-1-4 route promoted; OR semantics preserved) |

---

## 9. Tests

New focused suite `tests/test_mabhas9_tie_anchor_and_torsion_wire_route.py` (**53 tests**):

**Tie-anchor standard hook (§9-21-6-1-3-Alef)**
- `f_y < 280` + `d_b ≤ 16` + valid hook → PASS
- `f_y < 280` + `d_b 18–25` + valid hook → PASS (incl. `f_y` just below 280, `d_b = 25`)
- `d_b ≤ 16` with **high** `f_y` (500 MPa) → PASS (source-faithful: no f_y gate on this sub-condition)
- `d_b = 16` boundary → PASS
- `f_y = 280` → BLOCKED (`TIE_ANCHOR_FY_280_IN_GAP`); `f_y = 280` with `d_b ≤ 16` → PASS (guards against over-blocking)
- `f_y > 280` + `d_b 18–25` → BLOCKED (branch Be)
- `d_b = 17` → BLOCKED (`TIE_ANCHOR_DB_IN_GAP`); `d_b > 25` → BLOCKED (`TIE_ANCHOR_DB_ABOVE_TABLE`)
- `d_b < 10` → BLOCKED through the standard-hook dependency
- 180° hook / unsupported angle → BLOCKED through the standard-hook dependency
- missing `f_y` / `d_b` / `hook_angle_deg` / hook geometry / enclosure → BLOCKED
- non-enclosing / invalid delegated geometry → FAIL
- malformed `d_b < 0` / non-bool enclosure → INVALID_INPUT
- non-Mabhas-9 jurisdiction → JURISDICTION_BLOCKED
- **delegation agreement**: outcomes match `evaluate_standard_hook` on both PASS and FAIL paths (geometry not duplicated)

**Torsion wire route**
- valid Alef route → PASS; valid Be route → PASS
- **delegation agreement** with `evaluate_wire_tie_utie` on PASS and FAIL paths
- invalid U-tie geometry / not in upper part → FAIL
- missing `alternative` / route data / spall precondition → BLOCKED
- non-bool precondition → INVALID_INPUT
- precondition `False` → NOT_APPLICABLE
- non-Mabhas-9 jurisdiction → JURISDICTION_BLOCKED
- **OR semantics**: `BG-TRANS-TORSION-TIE-PENDING` stays blocked, the §9-21-6-1-3 route is retained there, §9-21-6-1-4 is no longer described as blocked, and the sentinel does not claim the whole clause is executable

**Sentinel / metadata / registry**
- `BG-TRANS-TIE-ANCHOR-PENDING` narrowed to Be & Pe; M4 "8–25" wording gone; promoted branch named; genuine gaps recorded
- M1: `BG-TRANS-SPIRAL-SPLICE-SEL-PENDING` pages 468/448; §9-21-4-7 dependency intact
- M2: `BG-TRANS-TORSION-TIE-135HOOK-001` no longer says §9-21-6-1-4 is still blocked; scope unchanged
- M3: `BG-TRANS-DORGIR-001` clause citation includes 9-21-6-4-3
- all five §9-21-6 sentinels remain blocked; `BG-TRANS-WIRE-TIE-PENDING` still scoped to §9-21-6-1-5 only
- registry: 120 total / 62 executable / 48 blocked, no duplicates, §9-21-6 = 22 + 5, both new dependencies executable

Existing suites updated (no test weakened): `tests/test_mabhas9_standard_hook_and_splits.py::test_executable_count_is_60` → `test_executable_count_is_62`, and the exact executable-rule set in `tests/test_registry_and_gatekeeper.py::test_mabhas9_executable_rules_exact_set` now lists both new rule IDs.

---

## 10. Files changed

| File | Change |
| :--- | :--- |
| `src/beamgenius/engine/transverse_reinforcement_mabhas9.py` | +2 catalog-rule imports, +5 `BG_TRANS_TIE_ANCHOR_*` constants, +2 evaluators (`evaluate_tie_anchor_std_hook`, `evaluate_torsion_tie_wire_route`), M2 docstring correction on `evaluate_torsion_tie_135hook` |
| `src/beamgenius/registry/catalog.py` | +2 `RuleReference`s (both added to `_ALL_RULES_TUPLE`); M1 on `BG-TRANS-SPIRAL-SPLICE-SEL-PENDING`; M2 on `BG-TRANS-TORSION-TIE-135HOOK-001`; M3 on `BG-TRANS-DORGIR-001`; M4 + narrowing on `BG-TRANS-TIE-ANCHOR-PENDING`; narrowing on `BG-TRANS-TORSION-TIE-PENDING` |
| `tests/test_mabhas9_tie_anchor_and_torsion_wire_route.py` | **new** — 53 focused H.7 tests |
| `tests/test_mabhas9_standard_hook_and_splits.py` | executable-count assertion 60 → 62 |
| `tests/test_registry_and_gatekeeper.py` | exact executable-rule set + 2 new IDs |
| `docs/VERIFIED_RULES.md` | +2 rule entries; M2 fix on the 135HOOK entry; M3 fix on the DORGIR entry; narrowed BLOCKED section; H.7 closing note and counts |
| `docs/PHASE2_SOURCE_VERIFICATION_MATRIX.md` | F.2 table rows for §9-21-6-1-3 / -1-4 / -1-6 / -2-7; F.3 note 2 (M4); G.4 sentinel rows; G.4b DORGIR row (M3); **new G.4d H.7 section**; G.5 registry + checks |
| `docs/PHASE2F_STAGE_H7_IMPLEMENTATION.md` | **new** — this document |

No source JPG/PDF/OCR artifact is committed; all evidence images live in the gitignored `working/h7/` scratch directory. The Stage H.6 audit document remains untracked and is **not** committed.

---

## 11. Governance / gate results

| Gate | Result |
| :--- | :--- |
| `pytest` | **630 passed** (577 before H.7 + 53 new) |
| `mypy --strict` | clean, 23 files |
| `git diff --check` | clean |
| Duplicate rule-ID check | no duplicates in the 120-rule registry |
| Registry integrity | 120 = 62 executable + 48 blocked + 10 reference-executable; `_ALL_RULES_TUPLE` contains both new IDs |
| New `RuleReference` metadata validation | both new rules carry exact clause, PDF page, printed page, requirement, applicability, limitations, dependencies and execution status; no invented page numbers |
| Engine AST reference-import check | no reference imports in the new evaluators; geometry delegated, never duplicated |
| `origin/main` | **still `df8067a`** — untouched |
| Unresolved branches | §9-21-6-1-3-Be, §9-21-6-1-3-Pe, §9-21-6-1-5, §9-21-6-2-3, §9-21-6-3-5-Alef and the (Be) clauses as a whole all remain **BLOCKED** |
