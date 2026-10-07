# Next Engineering Subsystem Readiness

**BeamGenius — Next Subsystem Selection & Implementation Readiness Audit**

**Stage H.23 · baseline `80fd01b` · `origin/main` `df8067a…` untouched**

**DECISION: `DOCUMENTATION ONLY — NOT IMPLEMENTATION READY`.** The selected subsystem
(flexural reinforcement **design**) is the correct next target and its implementation
contract is fully specified below, but **one precondition fails**: the governing source
pages for its substrate are **not present in the repository evidence package**, so a new
executable rule cannot be promoted from evidence actually available in this repository.
No rule was registered, no status changed, no count moved.

---

## 1. Baseline

| Item | Value |
| :-- | :-- |
| HEAD at stage start | **`80fd01b`** (boot showed the known stale-boot artifact at `f22ff45` with 5 dirty tracked files; recovered with `git fetch` → `git reset --mixed origin/arena/b9cd291a-beamgenius` → `git checkout HEAD -- .`; **no** `--hard`, **no** revert, **no** rewrite) |
| Branch | `arena/b9cd291a-beamgenius` |
| `origin/main` | **`df8067a750ffc7984c9dc5d80220ad9013503aa6`** — untouched |
| Working tree | clean |
| Chain (last 12) | `80fd01b` ← `ad1ecba` ← `36c387b` ← `67e3edd` ← `3df5091` ← `0598116` ← `22111f8` ← `cc79715` ← `940490d` ← `b4364d5` ← `8fc1dc9` ← `f7176f3` |
| `pytest` | **673 passed** |
| `mypy --strict` | **clean — 23 source files** |
| Registry | **121 total / 63 executable / 48 blocked / 10 reference** |
| Duplicate Rule IDs | **0** |
| §9-21-6 | **21 executable / 5 blocked** |

**No baseline discrepancy.**

---

## 2. Current Engineering Coverage

Verified against the actual code, registry, tests and governance docs (not filenames).

| # | Domain | Status | Evidence |
| :-- | :-- | :-- | :-- |
| 1 | **Flexural capacity (rectangular singly-reinforced)** | **IMPLEMENTED + EXECUTABLE** | `BG-FLEX-RECT-SINGLY-001` + `BG-FLEX-STRESS-BLOCK` + `BG-FLEX-PHI-FACTOR` + `BG-FLEX-STRAIN-LIMIT` + `BG-FLEX-MIN-001`; `flexure_mabhas9.py` |
| 1b | **Flexural *design* (required As from Mu)** | **NOT STARTED** | No inverse solve exists anywhere; `as_required_by_analysis_mm2` is a **caller-supplied input** to `evaluate_minimum_flexural_reinforcement` (`flexure_mabhas9.py:254`) |
| 1c | Doubly-reinforced & T/L flanged capacity | **BLOCKED** | `BG-FLEX-RECT-DOUBLY-001`, `BG-FLEX-TBEAM-CAP-001`, `BG-FLEX-LBEAM-CAP-001` |
| 2 | **Shear capacity (Vc, Vs, Vs,max, φVn ≥ Vu)** | **IMPLEMENTED + EXECUTABLE** | `BG-SHEAR-PHI-001`, `BG-SHEAR-VC-001`, `BG-SHEAR-VS-001`, `BG-SHEAR-VS-MAX-001`, `BG-SHEAR-MIN-001`, `BG-SHEAR-SPACING-001` |
| 3 | **Torsion** | **BLOCKED / NOT STARTED** | `BG-TORSION-PENDING` only; `evaluate_torsion(...)` returns a blocked trace |
| 4 | **Longitudinal reinforcement *selection*** | **NOT STARTED** | `rebar/catalog.py` is area math + deterministic enumeration only; `constructability_verified` is permanently `False` |
| 5 | **Transverse reinforcement / stirrup *design*** | **PARTIAL** — checks implemented, selection not | 21 executable §9-21-6 rules (spacing, diameters, ties, spirals, extent, closed-tie lap, dorgir) + 5 frozen blockers |
| 6 | **Development length** | **IMPLEMENTED + EXECUTABLE** | 8 rules (`BG-DEV-LENGTH-TENSION-001`, `…-TABLE-001`, `…-HOOKED-001`, `…-HEADED-001`, `BG-DEV-MECH-ANCHOR-001`, `…-WIRE-DEFORMED-001`, `…-WIRE-PLAIN-001`, `…-COMPRESSION-001`) |
| 7 | **Lap splices** | **IMPLEMENTED (bars) / BLOCKED (wire)** | `BG-DEV-LAP-APPLIC-001`, `…-SPACING-001`, `…-TENSION-001`, `…-TENSION-DIFFDIA-001`, `…-COMPRESSION-001`, `…-COMPRESSION-DIFFDIA-001`, `BG-DEV-SPLICE-BEARING-001`; wire laps blocked |
| 8 | Mechanical / welded splices | **BLOCKED** | `BG-DEV-SPLICE-WELDED-MECH-PENDING` (E's delegate) |
| 9 | **Detailing rules** | **IMPLEMENTED (broad)** | Bundle rules `BG-DETAIL-BUNDLE-001..008`, `BG-DETAIL-LONG-SPACING-001`, `BG-DETAIL-LAYER-SPACING-001`, `BG-DETAIL-COVER-001`, `BG-DETAIL-TRANS-DIA-001`, `BG-DETAIL-COMP-LAT-001` |
| 10 | Cover | **IMPLEMENTED (partial)** | `BG-DETAIL-COVER-001`; bundled branch + corrosive Appendix 9-پ1 branches blocked |
| 11 | Bar spacing | **IMPLEMENTED (partial)** | longitudinal clear spacing + layer spacing; **bundled branch blocked** |
| 12 | **Anchorage / hooks** | **IMPLEMENTED (mostly)** | standard hook, seismic hook, hooked/headed development, tie anchors (partial), `BG-TRANS-DORGIR-001`; `BG-BENT-ANCHOR-PENDING` blocked |
| 13 | Seismic detailing | **PARTIAL** | `BG-TRANS-SEISMIC-HOOK-001`, `BG-TRANS-TORSION-TIE-SEISMIC-HOOK-001`; Chapter 9-20 capacity design not verified |
| 14 | **Constructability verification** | **NOT STARTED** | every `RebarCatalogCandidate.constructability_verified is False` by construction |
| 15 | Load / design-condition handling | **PARTIAL** | `mu_nmm`, `vu_n`, `tu_nmm`, `nu_n` accepted as caller inputs; no load-combination module |
| 16 | **Section / material validation** | **IMPLEMENTED** | `domain/validation.py`; f′c ∈ [20, 70] MPa (Clause 9-3-3-3), fy ≤ 550 MPa (Table 9-4-4) |
| 17 | Governing code checks | **IMPLEMENTED** | central `Gatekeeper` + `JurisdictionMode` (Mabhas 9 / Mostofinejad-methodology-only) |
| 18 | **Rebar optimization / selection** | **NOT STARTED** | catalog is math-only by design |
| 19 | **Beam design orchestration (end-to-end)** | **PARTIAL** | `run_mabhas9_beam_check(...)` aggregates **checks** into `BeamComplianceReport`; there is no design→layout workflow |

**Structural observation (`NEW FINDING`).** The engine is a **verification** system: it can
decide whether a *given* layout complies. The chain
**Mu → As,req → bar candidate → constructability** is broken at its **first link** — the
engine cannot compute `As,req`. The existing rebar catalog already accepts a *target area*
(`enumerate_rebar_candidates(..., target_area_mm2=…)`), but **nothing in the codebase
produces that target area**, and `evaluate_minimum_flexural_reinforcement` likewise
requires `as_required_by_analysis_mm2` from the caller.

---

## 3. Frozen H.22 Blockers

Frozen. Not reopened, not re-audited, not depended upon by this document's selected
subsystem.

| | Rule | Status |
| :-- | :-- | :-- |
| A | `BG-TRANS-TIE-ANCHOR-PENDING` (§9-21-6-1-3-ب) | `VERIFY_PENDING`, `execution_allowed=False` |
| B | `BG-TRANS-WIRE-TIE-PENDING` (§9-21-6-1-5) | `VERIFY_PENDING`, `execution_allowed=False` |
| C | `BG-TRANS-TORSION-TIE-PENDING` (§9-21-6-1-6-ب & -2-7-ب) | `VERIFY_PENDING`, `execution_allowed=False` |
| D | `BG-TRANS-WIRE-SUBST-PENDING` (§9-21-6-2-3) | `VERIFY_PENDING`, `execution_allowed=False` |
| E | `BG-TRANS-SPIRAL-SPLICE-SEL-PENDING` (§9-21-6-3-5-الف) | `VERIFY_PENDING`, `execution_allowed=False` |

---

## 4. Candidate Next Subsystems

| # | Candidate | Value | Source readiness | Verdict |
| :-- | :-- | :-- | :-- | :-- |
| 1 | **Flexural reinforcement design** — required tension steel area from factored moment (rectangular singly-reinforced) | **Very high** — the gateway from *checking* to *designing*; produces the target area the existing rebar catalog already consumes | Substrate rules **VERIFIED & EXECUTABLE**; their evidence pages are **outside** the in-repo package (§8) | **SELECTED** — with a source-precondition caveat |
| 2 | Bundle integration into `BG-DETAIL-LONG-SPACING-001` / `-LAYER-SPACING-001` / `BG-DETAIL-COVER-001` | Medium — unblocks bundled configurations in three promoted rules | Linchpin §9-21-5-6 **visually re-verified this stage**; **parent-rule pages also outside the in-repo package** | **NEXT-BEST** (see §6) |
| 3 | Doubly-reinforced / T-L flanged flexural capacity | High for real beams | **Source pages not delivered** (Mabhas 9 printed 107–114 / 132) | Not ready |
| 4 | Torsion design | High | Depends on frozen **C** / `BG-TORSION-PENDING` | Excluded by Step 7 |
| 5 | Rebar constructability / selection layer | High | **Depends on Candidate 1 existing** (no target area ⇒ nothing to select) | Blocked *by dependency*, not by source |
| 6 | Seismic detailing (Chapter 9-20) | Medium | Chapter not in any evidence package | Not ready |
| 7 | §9-21-6-1-2 (each tie bend engages a longitudinal bar) | Low | Verified source-only; **positional/by-inspection, no deterministic scalar** (matrix §511) | Rejected — nothing deterministic to evaluate |

---

## 5. Selected Next Subsystem

> **Flexural Reinforcement Design — determination of the required tension reinforcement
> area `As,req` for a rectangular, singly-reinforced, tension-controlled beam section,
> as the minimum steel satisfying the *already-verified* Mabhas 9 flexural constraints.**

**Proposed rule ID: `BG-FLEX-RECT-REQ-AS-001` — PROPOSED, not registered.** It emits a
*required area* (`mm²`) that is consumed directly by the existing
`enumerate_rebar_candidates(..., target_area_mm2=…)`.

---

## 6. Why It Comes Next

**Selection criteria, in the mandated order:**

1. **Required for a professional beam-design workflow — decisive.** BeamGenius can verify a
   layout but cannot propose one. Design *cannot begin* without `As,req`; every downstream
   capability (candidate generation, constructability, layout selection, end-to-end design)
   is gated behind this single missing quantity.
2. **Sufficient verified source basis — yes.** All three constraints involved are already
   promoted and executable: the stress block (`BG-FLEX-STRESS-BLOCK`), φ
   (`BG-FLEX-PHI-FACTOR`), the tension-controlled ductility limit (`BG-FLEX-STRAIN-LIMIT`,
   εt ≥ εty + 0.003), the design-strength check φMn ≥ Mu (`BG-FLEX-RECT-SINGLY-001`), and
   minimum steel (`BG-FLEX-MIN-001`). **No new code requirement is introduced** — the
   subsystem *solves* verified relations rather than reading new ones.
3. **Deterministic without unsupported assumptions — yes, within a declared scope**
   (§11). The reduction is a closed-form quadratic in `As`; the scope restriction to the
   tension-controlled regime keeps φ constant at 0.90 and makes the solution unique. Cases
   outside that regime **BLOCK** rather than guess.
4. **Clear input/output contracts — yes** (§10).
5. **Unlocks the largest amount of downstream functionality — decisive.** It converts
   `BG-FLEX-MIN-001`'s caller-supplied `as_required_by_analysis_mm2` into an engine-computed
   value, and it supplies the missing `target_area_mm2` for `beamgenius.rebar`.
6. **Testable comprehensively — yes** (§13): round-trip against the existing capacity
   evaluator, boundary tests, and blocked-envelope tests.
7. **Independent of the five frozen blockers — verified in §11.** Flexure has no
   transverse-reinforcement dependency whatsoever.

**Why the next-best alternative should NOT be chosen first.** Bundle integration
(Candidate 2) is smaller, but (a) it **refines existing checks** rather than adding a
missing design capability, so it moves the product's headline goal far less; (b) its
**parent-rule sources** (`BG-DETAIL-LONG-SPACING-001` on printed 420, the bundled-cover
basis on printed 71–72) sit **outside** the repository evidence package too — it carries
the *same* source-precondition caveat as the selected candidate while unlocking far less;
and (c) it is a **sub-case of layout verification**, which is only reachable *after* a
target area exists. It is the correct **third** step, not the next one.

---

## 7. Source Evidence

| Purpose | Clause / equation | Printed | PDF | Status in repo package |
| :-- | :-- | :-- | :-- | :-- |
| Stress-block parameters α₀, β₁ | Clauses 9-8-2-2-6, 9-8-2-2-7; Eqs. (9-8-2), (9-8-3-الف), (9-8-3-ب), (9-8-4) | 113–114 | 22–23 | **Not in package** |
| φ / regime (tension-controlled φ = 0.90) | Clauses 9-7-4-1…-4-4; Table 9-7-2; Eqs. (9-7-10-الف/ب) | 107–109 | 16–18 | **Not in package** |
| Design strength φMn ≥ Mu | Clause 9-8-1-4, Eq. (9-8-1-الف) | 112 | 21 | **Not in package** |
| Tension-controlled / ductility limit | Clauses 9-8-2-2-2/-2-2-3, 9-11-2-3 | 107–109, 132 | 16–18, 41 | **Not in package** |
| Minimum flexural steel (+ 4/3 waiver) | Clauses 9-11-5-1-1…-1-3 | 199 | 220 | **Not in package** |
| Material bounds | Clause 9-3-3-3 (f′c 20–70 MPa); Table 9-4-4 (fy ≤ 550 MPa) | — | — | Recorded verified |
| **Equivalent diameter (Candidate 2 linchpin)** | Clause 9-21-5-6 | **442** | **462** | **In package — re-verified this stage** |

**`NEW FINDING` (citation defect).** Clause **9-21-5-6** is printed on **p. 442 / PDF p. 462**
— footers read directly this stage (`page-462.jpg` footer = «۴۴۲»). Both
`src/beamgenius/engine/detailing_bundle_mabhas9.py:1142` and `docs/VERIFIED_RULES.md:1209`
record it as **PDF p. 463**. The printed page and clause number are correct; the **PDF page
is off by one**, consistent with the superseded `+21` page-offset lineage that
`docs/PHASE2_SOURCE_VERIFICATION_MATRIX.md` §4B.5 already declares obsolete. **Not corrected
here** (this commit is documentation-only); recorded for a future metadata correction.

---

## 8. Source-Verification Status

| Layer | Status |
| :-- | :-- |
| The composing clauses (stress block, φ, ductility, capacity, As,min) | **VERIFIED** — promoted, executable, in the registry |
| The **evidence pages** for those clauses | **VERIFY_PENDING (not in repository)** — Mabhas 9 flexure pages (printed 107–114, 132, 199; PDF 16–23, 41, 220) exist in **no** committed evidence package. The repo packages are: `phase2f-source-442-472` (on `origin/main`), `phase2f-source-948` (printed 66–69), `phase2f-source-11558` |
| Mostofinejad Ch. 5 **design methodology** (the method for sizing reinforcement) | **VERIFIED_SOURCE_ONLY** per matrix (Eqs. 5-46…5-48 on printed 200 / PDF 211) — **also not in the repository** |
| The selected subsystem itself | **NOT STARTED** — no rule, no rule ID, no code |

**Governance consequence (Step 8 test).** For a **new executable rule** the standing rule is
*"Visual source verification is required before executable promotion."* Because the
substrate pages are absent from the repository, this stage **cannot** re-verify them, and
the design-inversion method is a **methodology** step (Mostofinejad's sanctioned role)
whose page is likewise absent. Two of the Step 8 conditions therefore **fail**:
*source is visually verified* and *rule references are complete* for a *new* rule.
→ **DO NOT IMPLEMENT.**

---

## 9. Proposed Rule IDs

| Rule ID | Kind | Status | Notes |
| :-- | :-- | :-- | :-- |
| `BG-FLEX-RECT-REQ-AS-001` | `CODE_RULE`, `MABHAS_9_COMPLIANCE` | **PROPOSED — do not register yet** | Required tension steel area `As,req` for rectangular singly-reinforced tension-controlled sections |
| (optional companion) `BG-FLEX-RECT-DESIGN-CHECK-001` | non-code orchestration | **PROPOSED** | Round-trip guard: `As,req` → capacity → PASS; pure composition of existing verified rules |
| Existing, unchanged | `BG-FLEX-MIN-001`, `BG-FLEX-RECT-SINGLY-001`, `BG-FLEX-STRESS-BLOCK`, `BG-FLEX-PHI-FACTOR`, `BG-FLEX-STRAIN-LIMIT` | VERIFIED | Only *consumed*, never modified |

**No registration, no status change, and no count change was performed in this stage.**

---

## 10. Input/Output Contract

**Inputs**

| Input | Unit | Required | Notes |
| :-- | :-- | :-- | :-- |
| `mu_nmm` | N·mm | **yes** | Factored design moment (caller-supplied; no load-combination module) |
| `bw_mm` | mm | **yes** | Web / rectangular width |
| `d_effective_mm` | mm | **yes** | Via existing `resolve_effective_depth` precedence (`EXPLICIT_D` → `ACTUAL_REBAR_GEOMETRY` → `UNRESOLVED`); **never** `h − 65`/`h − 90` |
| `fc_prime_mpa` | MPa | **yes** | Domain-validated 20 ≤ f′c ≤ 70 (Clause 9-3-3-3) |
| `fy_mpa` | MPa | **yes** | fy ≤ 550 MPa (Table 9-4-4) |
| `section_type` | enum | **yes** | Must be `RECTANGULAR`; T/L → BLOCKED |
| `has_compression_reinforcement` | bool | **yes** | Must be false; otherwise → BLOCKED (doubly is unverified) |

**Outputs**: `as_required_mm2` (governing), plus intermediates
`as_required_flexure_mm2`, `as_min_mm2`, `as_max_tension_controlled_mm2`, `phi`, `a_mm`,
`c_mm`, `epsilon_t`, and the governing-constraint label — as a `CalculationTraceStep`.

**Algorithm (deterministic, closed form, inside the verified tension-controlled regime)**

1. Gate: `MABHAS_9_COMPLIANCE` + registry gate.
2. Validate geometry/material (existing validators); missing input → **BLOCKED**;
   malformed → `INVALID_INPUT`.
3. α₀, β₁ ← verified stress-block rule; φ = 0.90 (tension-controlled).
4. Solve φ·As·fy·(d − a/2) = Mu with a = As·fy/(α₀·f′c·b) → quadratic in `As`:
   `As,flexure = [0.9·fy·d − √((0.9·fy·d)² − 4·(0.9·fy²/(2·α₀·f′c·b))·Mu)] / (2·(0.9·fy²/(2·α₀·f′c·b)))`
   (a standard algebraic inversion of the *verified* equilibrium; the physical root is the
   smaller one).
5. `As,min` ← verified `BG-FLEX-MIN-001`.
6. `As,max` ← verified tension-controlled limit already computed by the capacity evaluator
   (`as_max_tc_mm2`).
7. `As,req = max(As,flexure, As,min)`.
8. **If `As,req > As,max` → BLOCKED** (`SECTION_INADEQUATE_TENSION_CONTROLLED_DESIGN`),
   recommendation: enlarge section / use compression steel (a *designer* decision — never
   auto-selected by the engine).

**Consumption**: `As,req` feeds `enumerate_rebar_candidates(target_area_mm2=As,req)`.

---

## 11. Dependencies

| Dependency | Kind | State |
| :-- | :-- | :-- |
| `BG-FLEX-STRESS-BLOCK`, `BG-FLEX-PHI-FACTOR`, `BG-FLEX-STRAIN-LIMIT`, `BG-FLEX-RECT-SINGLY-001`, `BG-FLEX-MIN-001` | verified executable rules | available |
| Domain validators (`domain/validation.py`), `resolve_effective_depth`, trace/diagnostic layer, Gatekeeper | infrastructure | available |
| `beamgenius.rebar` catalog | consumer | available (unchanged) |
| **A / B / C / D / E (frozen)** | — | **NOT depended upon — verified in Step 7 below** |

**Step 7 blocker-discipline verification (explicit).** The selected subsystem reads only
flexural clauses (§9-8, §9-7-4, §9-11-2-3, §9-11-5-1). It touches **no** transverse
reinforcement, **no** tie, **no** wire, **no** spiral, and **no** splice clause. Therefore:

| Frozen blocker | Touched? |
| :-- | :-- |
| A `BG-TRANS-TIE-ANCHOR-PENDING` | **No** |
| B `BG-TRANS-WIRE-TIE-PENDING` | **No** |
| C `BG-TRANS-TORSION-TIE-PENDING` | **No** |
| D `BG-TRANS-WIRE-SUBST-PENDING` | **No** |
| E `BG-TRANS-SPIRAL-SPLICE-SEL-PENDING` | **No** |

No blocked rule is bypassed, and no partial implementation of any blocked rule is
proposed.

---

## 12. Blocking Conditions

| Condition | Outcome |
| :-- | :-- |
| `mu_nmm` missing / non-finite / ≤ 0 | BLOCKED (missing) / `INVALID_INPUT` (malformed) |
| `d_effective_mm` unresolvable | BLOCKED |
| `section_type` ∈ {T_SECTION, L_SECTION} | BLOCKED — flanged flexural capacity unverified (existing precedent) |
| Compression reinforcement present | BLOCKED — doubly-reinforced unverified |
| f′c outside [20, 70] MPa, fy > 550 MPa | `INVALID_INPUT` (existing bounds) |
| `As,req > As,max` (tension-controlled envelope exceeded) | BLOCKED — section inadequate; **never** silently designed as over-reinforced or transition-zone |
| Any frozen blocker invoked | not reachable (Step 7) |

**False-PASS guards.** the rule returns a *required area*, never a compliance verdict on a
layout; it never rounds up to a bar arrangement (selection is a separate, explicitly
policy-driven step); and it never substitutes Mostofinejad or a foreign code for a Mabhas 9
requirement.

---

## 13. Test Strategy

1. **Round-trip (primary invariant).** For a grid of (b, d, f′c, fy, n bars), compute
   `As,req` from `Mu = φMn(As,n)` and assert `evaluate_mabhas9_flexural_capacity(As=As,req)`
   yields φMn ≥ Mu; and that `As,req − ε` fails the same check.
2. **As,min governing.** Low-moment cases must return `As,min` (Clause 9-11-5-1-1 path) and
   label the governing constraint.
3. **Envelope boundary.** Construct the exact `As,max` case; assert the equality boundary is
   inclusive, and that `As,max + ε` → BLOCKED.
4. **Determinism.** Identical inputs ⇒ byte-identical trace and result across repeated calls.
5. **Blocked inputs.** T-section, L-section, compression steel, missing `mu_nmm`,
   unresolvable `d`, out-of-range materials → correct BLOCKED / `INVALID_INPUT` outcomes.
6. **No-frozen-blocker regression.** Assert the new rule's dependency closure contains no
   `*-PENDING` rule and that its evaluation never emits a `TRANSITIVE_DEPENDENCY_BLOCKED`
   diagnostic attributable to A–E.
7. **Registry/gatekeeper integration.** New rule registered as `VERIFIED` +
   `execution_allowed=True` with a gate test; all existing counts asserted at their exact
   new values (investigate any exact-set assertion before updating — never blind-update).
8. **Reference regressions.** Existing Mostofinejad example tests must remain green and
   `constructability_verified` must stay `False` until the *constructability* layer is
   separately authorized.

---

## 14. Implementation Readiness

| Step 8 condition | Result |
| :-- | :-- |
| Source is visually verified | **FAIL** — substrate pages are not in the repository evidence package (§8) |
| Governance permits execution | PASS — nothing blocked is touched; scope is verified substrate |
| Inputs are available | PASS — all inputs already exist as typed values |
| No unresolved ambiguity affects correctness | PASS — scope restricted to the tension-controlled regime; outside → BLOCKED |
| No unsupported assumption required | PASS — closed-form inversion of verified relations; no new code requirement |
| Rule references are complete | **FAIL** — `BG-FLEX-RECT-REQ-AS-001` does not exist; its methodology basis (Mostofinejad Ch. 5) is not in the repository |
| Deterministic implementation contract is clear | PASS — §10 |

**Two conditions fail ⇒ NOT IMPLEMENTATION READY.** Verdict:
**`VERIFIED SUBSTRATE, PENDING SOURCE EVIDENCE`** — contract-complete, evidence-incomplete.

---

## 15. Recommended Next Stage

> **Stage H.24 — Flexural Design Source Acquisition & Verification, then implementation.**
>
> 1. **Acquire/attach** the Mabhas 9 flexural pages (printed 107–114, 132, 199 / PDF
>    16–23, 41, 220) and the Mostofinejad Ch. 5 design-methodology pages (printed 200 /
>    PDF 211) into a committed evidence package, exactly as `phase2f-source-11558` and
>    `phase2f-source-948` were handled.
> 2. **Visually verify** the substrate clauses and the design-methodology basis; record
>    footers and page mapping (`PDF = printed + 20`).
> 3. **Run the 12-condition promotion gate** for `BG-FLEX-RECT-REQ-AS-001`.
> 4. **Only if the gate passes**, implement the rule + the round-trip guard, register it,
>    update `docs/VERIFIED_RULES.md` and the matrix, add the §13 tests, and run all gates.
> 5. **Then** proceed to the bundle-integration stage (Candidate 2), and only afterwards to
>    the constructability/selection layer (Candidate 5), which consumes `As,req`.
>
> **Do not** implement the flexural design rule before step 1–3 complete, and **do not**
> reopen any frozen H.22 blocker as part of this sequence.

---

## Appendix — Findings recorded this stage (no code affected)

| # | Finding | Class |
| :-- | :-- | :-- |
| F1 | The engine can **check** but cannot **design**: no `As,req` computation exists anywhere; the rebar catalog's `target_area_mm2` has no producer | `NEW FINDING` |
| F2 | `rebar/catalog.py`'s stated governance rationale ("…because bar spacing, cover, development, and detailing rules are not yet verified in `docs/VERIFIED_RULES.md`") is **factually stale** — those rules ARE verified (`BG-DETAIL-LONG-SPACING-001`, `BG-DETAIL-LAYER-SPACING-001`, `BG-DETAIL-COVER-001`, `BG-DEV-LENGTH-TENSION-001`). No behaviour is affected (`constructability_verified` stays `False`), but the docstring now misstates the reason | `NEW FINDING` — recommend a future metadata-only correction; **not** performed here |
| F3 | §9-21-5-6 recorded as PDF p. 463 in `detailing_bundle_mabhas9.py:1142` and `VERIFIED_RULES.md:1209`; visually re-verified this stage as **PDF p. 462 / printed p. 442** | `NEW FINDING` — off-by-one from the superseded `+21` lineage; recommend a future metadata-only correction |
| F4 | §9-21-5-6's scope text — «در کنترل محدودیتهای فاصله، حداقل پوشش، … بند ۹-۲۱-۳-۲-۱ و … بند ۹-۲۱-۳-۲-۲» — is the verified basis for the future bundle-integration stage | `VERIFIED` (visually re-read this stage) |
| F5 | Evidence packages present in the repository cover only printed 422–452 (Mabhas 9), printed 66–69 (Mabhas 9 §9-4-8) and ISIRI 11558 | `VERIFIED FACT` |

---

```
NEXT SUBSYSTEM:      Flexural Reinforcement Design — required tension steel area
                     As,req for rectangular singly-reinforced tension-controlled beams
                     (proposed rule BG-FLEX-RECT-REQ-AS-001; not registered)
DECISION:            NOT IMPLEMENTATION READY — documentation/readiness only. The correct
                     next target, with a complete implementation contract, whose source
                     evidence is not yet in the repository (substrate pages absent), so a
                     new executable rule cannot lawfully be promoted now.
CURRENT COVERAGE:    Verification-strong, design-weak. Flexure (check), shear, development
                     length, lap splices, detailing, cover/spacing, hooks, bundles, ties,
                     spirals all executable; torsion and doubly-reinforced/T-L capacity
                     blocked; selection, constructability and design orchestration not
                     started. The Mu -> As,req -> candidate chain is broken at As,req.
FROZEN H.22 BLOCKERS:A/B/C/D/E all VERIFY_PENDING, execution_allowed=False; untouched and
                     NOT depended upon by the selected subsystem.
SOURCE READINESS:    Substrate VERIFIED + EXECUTABLE; evidence pages NOT IN REPOSITORY
                     (VERIFY_PENDING for new-rule promotion). Methodological basis
                     (Mostofinejad Ch. 5) recorded VERIFIED_SOURCE_ONLY, also not in repo.
IMPLEMENTATION:      NOT PERFORMED.
REGISTRY:            121 / 63 executable / 48 blocked / 10 reference (unchanged);
                     §9-21-6: 21 executable / 5 blocked (unchanged); duplicate IDs 0.
PYTEST:              673 passed.
MYPY:                Success: no issues found in 23 source files.
DOCUMENT:            docs/NEXT_ENGINEERING_SUBSYSTEM_READINESS.md
COMMIT:              see commit below
ORIGIN/MAIN:         df8067a750ffc7984c9dc5d80220ad9013503aa6 — untouched
NEXT STEP:           Stage H.24 — acquire + visually verify the Mabhas 9 flexural pages and
                     the Mostofinejad Ch. 5 methodology pages, run the 12-condition gate,
                     then implement BG-FLEX-RECT-REQ-AS-001 with round-trip tests.
```
