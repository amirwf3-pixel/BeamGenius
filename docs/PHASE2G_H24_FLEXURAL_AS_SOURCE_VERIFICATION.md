# H.24 Flexural As,req Source Verification

**BeamGenius — Flexural `As,req` Source Acquisition + Visual Verification + Promotion Gate**

**Baseline `9cf67f4` · `origin/main` `df8067a…` untouched · documentation/verification only**

**DECISION: `BLOCKED — SOURCE PAGES NOT PRESENT IN THIS ENVIRONMENT`. 3 of 12 gates PASS.
NO IMPLEMENTATION.** The derivation is mathematically complete and recorded below as
`DERIVED`; the evidentiary root of its traceability cannot be verified here because **no
Mabhas 9 flexural page and no Mostofinejad page exists anywhere in this environment**.

---

## 1. Baseline

| Item | Value |
| :-- | :-- |
| HEAD at stage start | **`9cf67f4`** (boot showed the known stale-boot artifact at `f22ff45` + 5 dirty tracked files; recovered with `git fetch` → `git reset --mixed origin/arena/b9cd291a-beamgenius` → `git checkout HEAD -- .`; **no** `--hard`, **no** rewrite) |
| Branch | `arena/b9cd291a-beamgenius` |
| `origin/main` | **`df8067a750ffc7984c9dc5d80220ad9013503aa6`** — untouched |
| Working tree | clean |
| Log −12 | `9cf67f4` `80fd01b` `ad1ecba` `36c387b` `67e3edd` `3df5091` `0598116` `22111f8` `cc79715` `940490d` `b4364d5` `8fc1dc9` |
| `pytest` / `mypy` | **673 passed** / **clean (23 files)** |
| Registry | **121 / 63 executable / 48 blocked / 10 reference**; duplicate IDs **0**; §9-21-6 **21/5** |

---

## 2. Scope

Acquire and visually verify the exact source evidence required for the H.23-selected
subsystem `BG-FLEX-RECT-REQ-AS-001` (required tension steel area `As,req`, rectangular
singly-reinforced tension-controlled beams), run the 12-condition promotion gate, and
implement **only if all 12 pass**.

**Out of scope, and not touched:** the five frozen H.22 blockers; unrelated flexural rules;
UI/reports/DXF/mobile/cloud/AI; the §9-21-5-6 citation defect; the `rebar/catalog.py`
rationale defect; bundle integration; rebar selection; end-to-end orchestration.

---

## 3. Source Inventory

Exhaustive search of the repository, worktree, and filesystem.

| # | Artifact | Location | Coverage | State |
| :-- | :-- | :-- | :-- | :-- |
| 1 | `phase2f-source-442-472/` (31 JPG + 31 TXT) | **`origin/main` @ `df8067a` only** — *not* in this worktree, *not* tracked on our branch | Mabhas 9 **printed 422–452 / PDF 442–472** | available read-only via `git show` |
| 2 | `phase2f-source-948/` (4 PNG) | branch | Mabhas 9 **printed 66–69** (§9-4-8) | available |
| 3 | `phase2f-source-11558/` (PDF + notes) | branch | **ISIRI 11558**, 19 pp. | available |
| 4 | `docs/MOSTOFINEJAD_FORMULA_REGISTRY.md` | branch | **registry of equations only** — not source pages | available |
| 5 | `src/beamgenius/reference/mostofinejad_ch5.py` | branch | **implementation** of 5-46…5-62 | available |

**`VERIFIED FACT` — acquisition result.** A filesystem-wide search
(`find / -iname "*mabhas*" -o -iname "*mostofinejad*"`, plus every `*.pdf`/`*.jpg`/`*.png`
outside `.git`) returns **only** the three packages above. Therefore:

| Required for `BG-FLEX-RECT-REQ-AS-001` | Present? |
| :-- | :-- |
| Mabhas 9 flexural pages (printed 107–114, 132, 199) | **NO — absent** |
| Mostofinejad Vol. 1 Ch. 5 pages (printed 200, 201–205) | **NO — absent** |
| The repository's own source PDF (`references/mabhas9/source/…ATNasr…pdf`, a **Windows path** named in the matrix) | **NO — never committed; a different machine** |

The git-ignored directories that once held them (`references/`, `ocr/`, `extracted/`,
`verification/`, `working/`) **do not exist** in this environment.

**Governance consequence.** Per this stage's mandate — *"If the source pages are
unavailable, the correct result is VERIFY_PENDING + no implementation"* and *"Do not claim
source verification unless the actual source pages were visually inspected"* — **no H.24
visual verification is possible**. No evidence was manufactured, no source was fetched, and
no copyrighted material was acquired. Consistent with all prior packages (user-supplied
captures), acquisition requires the user to supply the pages.

---

## 4. Mabhas 9 Evidence

### 4.1 Recorded substrate (`EXISTING PRIOR FINDING` — recorded, **not** verified in H.24)

| Item | Clause / equation | Printed | PDF as recorded | H.24 status |
| :-- | :-- | :-- | :-- | :-- |
| A. Rectangular singly-reinforced assumptions | 9-8-2-1-1; 9-8-2-2-1…−2-2-8 | 112–114 | 21–23 | **not inspectable** |
| B. Tension-controlled / ductility condition | 9-8-2-2-2/-2-2-3; 9-7-4-2; 9-11-2-3 | 107–109, 132 | 16–18, 41 | **not inspectable** |
| C. Compression-block parameters | 9-8-2-2-6/-2-2-7; Eqs. (9-8-2), (9-8-3-الف/ب), (9-8-4) | 113–114 | 22–23 | **not inspectable** |
| D. Neutral-axis relationship | a = β₁·c; c from equilibrium | 113–114 | 22–23 | **not inspectable** |
| E. Steel strain/stress relationship | εcu = 0.003; εt = εcu(dt−c)/c; fs = Es·εt ≤ fy | 107–109 | 16–18 | **not inspectable** |
| F. Nominal moment Mn | Mn = As·fy·(d − a/2) | 112–114 | 21–23 | **not inspectable** |
| G. Design strength φMn | 9-8-1-4, Eq. (9-8-1-الف); Table 9-7-2 | 112, 107–109 | 21, 16–18 | **not inspectable** |
| H. Relationship to solve for As | **no design equation is printed** — the source gives the *resistance* model only | — | — | **absent by nature** |
| I. As,min | 9-11-5-1-1…−1-3 (+ 4/3 waiver) | 199 | 220 | **not inspectable** |
| J. Limits/boundaries | 9-3-3-3 (f′c 20–70); Table 9-4-4 (fy ≤ 550) | — | — | recorded only |
| K. Material parameters | f′c, fy, Es = 200 000 MPa (9-4-8-4) | — | — | recorded only |
| L. Section dimensions | b = bw, d (never h−65 / h−90) | — | — | recorded only |

### 4.2 `NEW FINDING` — the recorded PDF page attributions are mutually inconsistent

Computed offsets (PDF − printed) from `docs/PHASE2_SOURCE_VERIFICATION_MATRIX.md`:

| Set | Example | Offset |
| :-- | :-- | :-- |
| Flexure / T-beam (Phase 2B) | printed 107 ↔ PDF 16; 112 ↔ 21; 113 ↔ 22; 103 ↔ 12 | **−91** |
| Shear / min-steel (Phase 2C) | printed 107 ↔ PDF 128; 119 ↔ 140; 206 ↔ 227; 199 ↔ 220 | **+21** |
| §9-21 footer-verified evidence scan (2F) | printed 442 ↔ PDF 462 (30 consecutive footer pairs) | **+20** |

**Printed page 107 is attributed to PDF 16 *and* PDF 128 in the same matrix.** Both cannot
be correct for one continuous document. Therefore **no recorded PDF page number for the
flexural substrate can be trusted**, and any acquisition request must be issued by
**printed page** with the PDF↔printed mapping to be re-established by **footer inspection**
on the acquired document — exactly the procedure that produced the reliable `+20` lineage.

**Physical identity for acquisition (stable): printed pages 107–114, 132, 199, 200**
(and, for worked-example cross-checks, printed 201–205).

---

## 5. Mostofinejad Evidence

### 5.1 Recorded (`EXISTING PRIOR FINDING` — registry, not source pages)

| Eq. | Recorded content | Printed | PDF as recorded | Registry class |
| :-- | :-- | :-- | :-- | :-- |
| (5-46) | `kn = f′c·ω·(1 − 0.59ω)`, `ω = ρ·fy/f′c` | 200 | 211 | `VERIFIED_SOURCE` / `METHODOLOGY` |
| (5-47) | `b·d² = Mn/kn = Mu/(φ·kn)` | 200 | 211 | `VERIFIED_SOURCE` / `METHODOLOGY` |
| (5-48-a) | `d ≈ h − 65 mm` | 200 | 211 | `PRACTICAL_ESTIMATION` |
| (5-48-b) | `d ≈ h − 90 mm` | 200 | 211 | `PRACTICAL_ESTIMATION` |
| (5-49)…(5-61) | **CSA A23.3-14** stress block / capacity | 207–209 | 218–220 | `SOURCE_NOTE_REQUIRES_REVIEW` — **not Iranian code** |
| (5-44), (5-45) | referenced but not visible in the supplied pages | 200 | 211 | `UNRESOLVED` |

### 5.2 `NEW FINDING` — what the recorded methodology actually supports

**`(5-46)` + `(5-47)` are a SECTION-SIZING method, not an `As` formula.** `(5-47)` solves
for `b·d²` given a *pre-chosen* `ω`; `(5-46)` evaluates `kn` for that `ω`. The recorded
methodology answers *"what section do I need?"*, **not** *"how much steel does this fixed
section need?"*. Consequently **Mostofinejad does not supply the `As,req` equation for
fixed `b, d`** — that transformation is a **derivation**, and must be labelled `DERIVED`
(§7), never `SOURCE FORMULA`.

**Jurisdiction constraint (`VERIFIED FACT`).** `BG-MOST-5-46/-5-47/-5-48A/-5-48B` are
`execution_allowed=True` **only** in `JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY`, and
are `JURISDICTION_BLOCKED` in `MABHAS_9_COMPLIANCE`. They therefore **cannot carry a
`MABHAS_9_COMPLIANCE` code rule.**

### 5.3 `NEW FINDING` — an `As,req` solver already exists, but on a *different* model

`src/beamgenius/reference/mostofinejad_ch5.py` contains **`solve_required_as(...)`**
(≈ line 270): it computes `kn = Mu/(φ·b·d²)`, inverts `(5-46)` for `ω`, then
`ρ = ω·f′c/fy`, `As = ρ·b·d`. Its own docstring states it is *"used strictly for isolated
Mostofinejad textbook reference examples (Examples 5-5 & 5-6)"*.

**This corrects H.23's absolute claim.** H.23 recorded "no `As,req` producer exists
anywhere". Precisely: a producer exists, but (a) only in the Mostofinejad jurisdiction,
(b) built on Mostofinejad's `ω`-form model, (c) not registered as a Mabhas 9 rule, and
(d) not wired to the rebar catalog. **H.24 corrects the record accordingly.**

**Model-divergence measurement (`VERIFIED FACT`, computed this stage).** Equating
`Mn/(b·d²) = ω·f′c·(1 − ω/(2α₀))` (Mabhas 9) with `f′c·ω·(1 − 0.59ω)` (Mostofinejad):
Mostofinejad's `0.59` implies `α₀ = 1/(2×0.59) = 0.847458`, whereas Mabhas 9 uses
`α₀ = 0.85` → `0.588235` (a 0.3 % difference at f′c ≤ 55 MPa). **For f′c > 55 MPa the models
diverge materially**, because Mabhas 9 reduces `α₀` while Mostofinejad hard-codes `0.59`:

| f′c (MPa) | Mabhas 9 α₀ | Coefficient `1/(2α₀)` | Mostofinejad | Divergence |
| :-- | :-- | :-- | :-- | :-- |
| 55 | 0.850 | 0.588 | 0.59 | 0.3 % |
| 60 | 0.830 | 0.602 | 0.59 | 2.1 % |
| **70** | **0.790** | **0.633** | **0.59** | **~7 %** |

Since Mabhas 9's own concrete range is 20–70 MPa (Clause 9-3-3-3, enforced in code), the
window **55 < f′c ≤ 70 MPa** is a real divergence zone. Reusing the existing Mostofinejad
solver inside a `MABHAS_9_COMPLIANCE` rule would therefore be a **model substitution** —
prohibited — not a re-derivation.

---

## 6. Verified Resistance Model

**Status of this section: `EXISTING PRIOR FINDING` — reproduced from the registry and code.
H.24 did NOT visually verify it (the pages are absent), so it must not be cited as
H.24-verified.** It is recorded here only to define the model the derivation must invert.

```
Equilibrium / stress block:
    a = As·fy / (α0·f′c·b)                    [T = C, C = α0·f′c·b·a]
    α0 = 0.85                       (f′c ≤ 55 MPa)
    α0 = max(0.85 − 0.004(f′c − 55), 0.75)    (f′c > 55 MPa)
    β1 = 0.85                       (f′c ≤ 28 MPa)
    β1 = max(0.85 − 0.05(f′c − 28)/7, 0.65)   (f′c > 28 MPa)

Strain compatibility / ductility:
    εcu = 0.003 ;  εt = εcu·(dt − c)/c ;  εty = fy/Es ;  Es = 200 000 MPa
    Tension-controlled:  εt ≥ εty + 0.003  →  φ = 0.90

Nominal / design resistance:
    Mn = As·fy·(d − a/2)
    φ·Mn ≥ Mu                                 [Clause 9-8-1-4, Eq. (9-8-1-الف)]

Minimum steel:
    As,min = max(0.25·√f′c·bw·d/fy , 1.4·bw·d/fy)      [9-11-5-1-1/-1-2]
```

**No design equation (`As` from `Mu`) is printed in the source.** Item H of Step 4 is
therefore **absent by nature** — confirmed by §4.1 and §5.2.

---

## 7. As,req Derivation

**Classification: `DERIVED` (mathematically equivalent inversion of the verified resistance
model) — NOT a source formula.** Permitted only if mathematically equivalent; no
simplification is applied.

Setting the design strength to equality to obtain the **minimum** admissible steel:

```
φ·As·fy·(d − As·fy/(2·α0·f′c·b)) = Mu

Let  k = fy / (2·α0·f′c·b)          [units mm⁻¹]
  →  φ·fy·k·As² − φ·fy·d·As + Mu = 0
  →  As² − (d/k)·As + Mu/(φ·fy·k) = 0

Roots:  As = [ d/k ± sqrt( d²/k² − 4·Mu/(φ·fy·k) ) ] / 2

Governing root = the SMALLER one (smaller a, larger εt, tension-controlled branch):

    As,flexure = ( d/k − sqrt( d²/k² − 4·Mu/(φ·fy·k) ) ) / 2
```

**Solvability condition (exact, and identical to the physical `a ≤ d` limit).** The
discriminant is non-negative iff

```
Mu ≤ φ·fy·d²/(4k) = φ·α0·f′c·b·d²/2          (the moment at a = d)
```

giving a clean interpretation: **if `Mu` exceeds the moment a singly-reinforced section can
develop at `a = d`, no root exists** → BLOCKED (§9). In practice the binding limit is
stricter: the **tension-controlled** envelope `As,max` already computed by the verified
capacity evaluator (`as_max_tc_mm2`).

**Governing required area**

```
As,req = max( As,flexure , As,min )
```

**Traceability.** Every symbol (`α0`, `β1`, `φ`, `εcu`, `εty`, `Es`, `fy`, `f′c`, `b`, `d`,
`Mu`, `As,min`) originates in the recorded substrate of §6; the only operation applied is
algebraic rearrangement. **The mathematics is traceable; its evidentiary root is not
inspectable in this environment** (§3) — which is precisely why the gate fails.

**Explicitly rejected alternatives (no unsupported substitution):**
- reusing `mostofinejad_ch5.solve_required_as` inside a Mabhas 9 rule → **model
  substitution** (§5.3), rejected;
- importing a CSA/ACI form → prohibited;
- choosing the larger root → over-reinforced branch, outside the declared scope, rejected.

---

## 8. Applicability

| Applies when | Excluded (→ BLOCKED / INVALID) |
| :-- | :-- |
| `section_type == RECTANGULAR` | T_SECTION, L_SECTION (flanged capacity unverified) |
| `as_compression == 0` | any compression reinforcement (doubly unverified) |
| tension-controlled at the solution point (φ = 0.90) | transition/compression-controlled solutions |
| 20 ≤ f′c ≤ 70 MPa (Clause 9-3-3-3) | outside → `INVALID_INPUT` |
| fy ≤ 550 MPa (Table 9-4-4) | outside → `INVALID_INPUT` |
| non-prestressed, non-seismic scope | prestressed / seismic capacity-design extensions |

---

## 9. Boundary Conditions

| Case | Required behaviour |
| :-- | :-- |
| `Mu = 0` | `As,flexure = 0` → governing `As,req = As,min`. **Not** an error |
| `Mu < 0` | **`INVALID_INPUT`** — the model is unidirectional; negative moment is a different design case, not a reason to swap faces silently |
| `Mu` non-finite / missing | BLOCKED (missing) / `INVALID_INPUT` (malformed) |
| `bw ≤ 0`, `d ≤ 0`, `d ≥ h` | `INVALID_INPUT` |
| `f′c ∉ [20, 70]`, `fy > 550` | `INVALID_INPUT` |
| very small `Mu` | `As,flexure < As,min` → `As,min` governs |
| **`Mu` = the tension-controlled boundary** | inclusive: `As,req = As,max` is admissible (`εt = εty + 0.003`, φ = 0.90 exactly) |
| `Mu` just above that boundary | **BLOCKED** (`SECTION_INADEQUATE_TENSION_CONTROLLED_DESIGN`) — **never** silently solved as transition-zone, over-reinforced, or doubly-reinforced |
| very large `Mu` (discriminant < 0) | **BLOCKED** (no real root) |
| impossible singly-reinforced section | BLOCKED with an explicit diagnostic naming the four admissible remedies (enlarge section, raise f′c, raise fy, or **designer's** decision to use compression steel) — the engine never selects one |

**No clamping, no silent coercion, no automatic switch to doubly-reinforced design.**

---

## 10. Input Model Compatibility

`VERIFIED FACT` — all required inputs already exist; **read, not modified**.

| Input | Source in domain model | Status |
| :-- | :-- | :-- |
| `bw_mm` | `BeamGeometry.bw_mm` | exists |
| `h_mm` | `BeamGeometry.h_mm` | exists |
| `d_effective_mm` | `BeamGeometry.d_effective_mm` + `resolve_effective_depth` precedence (`EXPLICIT_D` → `ACTUAL_REBAR_GEOMETRY` → `UNRESOLVED`; **never** `h−65`/`h−90`) | exists |
| `section_type` | `BeamGeometry.section_type` (`SectionType`) | exists |
| `fc_prime_mpa` | `ConcreteMaterial.fc_prime_mpa` | exists |
| `fy_mpa` | `RebarMaterial.fy_mpa` | exists |
| `es_mpa` | `RebarMaterial.es_mpa` (default 200 000) | exists |
| `mu_nmm` | caller-supplied kwarg (same convention as `evaluate_mabhas9_flexural_capacity`) | exists |
| `as_provided_mm2` | `geometry.provided_tensile_area_mm2` or kwarg | exists |
| output `as_required_mm2` | → `enumerate_rebar_candidates(target_area_mm2=…)` | consumer exists |

**No new input type is required.** `d` is *never* defaulted; `Mu` is *never* invented.

---

## 11. Dependency Audit

Explicit Step-7/Step-9 verification — the proposed rule reads **only** flexural clauses.

| Frozen H.22 blocker | Touched? |
| :-- | :-- |
| A `BG-TRANS-TIE-ANCHOR-PENDING` | **No** |
| B `BG-TRANS-WIRE-TIE-PENDING` | **No** |
| C `BG-TRANS-TORSION-TIE-PENDING` | **No** |
| D `BG-TRANS-WIRE-SUBST-PENDING` | **No** |
| E `BG-TRANS-SPIRAL-SPLICE-SEL-PENDING` | **No** |
| Bundle substitution / wire substitution / spiral splice / wire tie / torsion tie / tie anchor | **No** |

**Dependency graph is clean.** The proposed rule's transitive closure would contain only
verified, executable flexure/validation infrastructure:
`BG-FLEX-STRESS-BLOCK`, `BG-FLEX-PHI-FACTOR`, `BG-FLEX-STRAIN-LIMIT`,
`BG-FLEX-RECT-SINGLY-001`, `BG-FLEX-MIN-001`, the Gatekeeper, and domain validation.
**No blocked rule is bypassed and no partial implementation of a blocked rule is proposed.**

---

## 12. 12-Condition Promotion Gate

| # | Condition | Result | Basis |
| :-- | :-- | :-- | :-- |
| 1 | Mabhas 9 source available | **FAIL** | flexural pages absent (§3) |
| 2 | Mabhas 9 visually verified | **FAIL** | not inspectable here (§3–§4) |
| 3 | Exact clauses/pages identified | **BLOCKED** | clauses identified exactly; **recorded PDF pages mutually inconsistent** — printed 107 recorded as both PDF 16 and PDF 128 (§4.2) |
| 4 | Resistance model verified | **FAIL** | recorded as verified on a prior lineage; **not verifiable in H.24** (§6) |
| 5 | Mostofinejad methodology available | **FAIL** | no Mostofinejad source in environment (§3, §5.1) |
| 6 | Mostofinejad methodology visually verified | **FAIL** | not inspectable here (§5) |
| 7 | Derivation traceable | **BLOCKED** | algebra fully traceable to §6; evidentiary root uninspectable (§7). **Also `NEW FINDING`:** Mostofinejad supplies a *sizing* method, not an `As` formula (§5.2) |
| 8 | Required inputs representable | **PASS** | all exist (§10) |
| 9 | Boundary conditions defined | **PASS** | fully specified, incl. inclusive tension-controlled boundary and explicit BLOCK cases (§9) |
| 10 | No unsupported assumption required | **FAIL** | two open items: (i) a **derived** (non-printed) equation as a `CODE_RULE` is an unadjudicated governance question; (ii) the existing `As` solver embodies a **different resistance model** (§5.3) and may not be reused |
| 11 | RuleReference can be completed | **BLOCKED** | a `VERIFIED` reference cannot be completed without source verification; its `pdf_page` is currently contradictory (§4.2) |
| 12 | Deterministic tests can be written | **PASS** | round-trip + boundary classes are fully specifiable (§13) |

**Result: 3 PASS · 6 FAIL · 3 BLOCKED ⇒ PROMOTION NOT ALLOWED.**

---

## 13. Test Design

Prepared for the future implementation stage. **Round-trip and boundary classes require no
external source** (they test internal consistency against the verified capacity evaluator);
**independently-valued vectors are BLOCKED** until the source pages are available
(`Do not invent expected numerical results without an independently verified derivation`).

| # | Test | Expected |
| :-- | :-- | :-- |
| T1 | **Round-trip**: `Mu ← φMn(As,n)` → solve → assert `φMn(As,req) ≥ Mu` and `φMn(As,req − ε) < Mu` | PASS at the boundary |
| T2 | `As,min` governs (small `Mu`) | `As,req == As,min`, governing-constraint label = `MINIMUM` |
| T3 | Tension-controlled boundary | `As,req == As,max_tc`; inclusive (no BLOCK at exact equality) |
| T4 | Just above the boundary | BLOCKED `SECTION_INADEQUATE_TENSION_CONTROLLED_DESIGN` |
| T5 | Discriminant < 0 (huge `Mu`) | BLOCKED, no real root |
| T6 | `Mu = 0` | `As,res = As,min` |
| T7 | `Mu < 0` | `INVALID_INPUT` |
| T8 | `bw ≤ 0`, `d ≤ 0`, `d ≥ h` | `INVALID_INPUT` |
| T9 | `f′c = 19.9 / 70.1`, `fy = 551` | `INVALID_INPUT` (bounds) |
| T10 | `section_type ∈ {T, L}` | BLOCKED (flanged unverified) |
| T11 | Compression steel present | BLOCKED (doubly unverified) |
| T12 | Determinism | byte-identical trace/result on repeated calls |
| T13 | **No-frozen-blocker regression** | dependency closure contains no `*-PENDING`; no `TRANSITIVE_DEPENDENCY_BLOCKED` from A–E |
| T14 | Materials across the whole 20–70 MPa range | `α0` follows Mabhas 9 (and **not** the fixed `0.59` form) — guards the §5.3 divergence |
| T15 | Registry/gatekeeper integration | exact count assertions (investigate before updating any exact-set assertion) |

---

## 14. RuleReference

**Prepared but NOT registerable — do not add to `catalog.py`.**

```python
rule_id          = "BG-FLEX-RECT-REQ-AS-001"          # PROPOSED
title            = "Flexural Required Tension Reinforcement Area (As,req)"
category         = RuleCategory.CODE_RULE            # ← open governance question (§12 #10)
jurisdiction     = JurisdictionMode.MABHAS_9_COMPLIANCE
source_document  = SOURCE_MABHAS_9
clause_or_equation = ("Clauses 9-8-2-1-1, 9-8-2-2-1..-2-2-8, 9-8-2-2-6/-2-2-7, "
                      "9-7-4-1..-4-4, 9-8-1-4, 9-11-2-3, 9-11-5-1-1..-1-3, 9-3-3-3")
printed_page     = "107-114, 132, 199"                # stable acquisition identity
pdf_page         = <UNRESOLVED>                       # recorded attributions contradictory (§4.2)
status           = VerificationStatus.VERIFY_PENDING  # unchanged
execution_allowed= False                              # unchanged
dependencies     = ()                                 # clean (§11)
```

**Open governance question requiring a decision (not resolvable by this stage):** may a
rule whose *equation* is **derived** (mathematically equivalent, but never printed as such)
carry `RuleCategory.CODE_RULE` / `VerificationStatus.VERIFIED`? The source prints the
resistance model only; the `As`-from-`Mu` form does not appear in Mabhas 9 or — for fixed
`b, d` — in the recorded Mostofinejad methodology. Until that precedent is set, the rule
cannot be honestly labelled.

---

## 15. Decision

**`BLOCKED — VERIFY_PENDING. NO IMPLEMENTATION.`**

- **`As,req` derivation: `DERIVED`** — mathematically complete, traceable to the recorded
  substrate, and recorded in §7 with its exact solvability condition.
- **Evidentiary status: `VERIFY_PENDING`** — the Mabhas 9 flexural pages and every
  Mostofinejad page are **absent from this environment**; no visual verification was
  performed; no claim of verification is made.
- **Implementation contract, boundary set, test design, dependency audit and a prepared
  RuleReference** are all complete — the subsystem is **specification-ready**, not
  evidence-ready.
- **Self-corrections recorded:** H.23's "no `As,req` producer exists" is imprecise (§5.3);
  the resistance-model divergence between the existing Mostofinejad solver and Mabhas 9 is
  quantified for the first time (§5.3).

Per the governing rule, **the correct result when source pages are unavailable is
`VERIFY_PENDING` + no implementation.**

---

## 16. Reopen / Next-Step Conditions

**Exact evidence required to reopen this blocker** (all by **printed** page; PDF↔printed
mapping to be re-established by **footer inspection** on the acquired document):

| # | Material | Printed pages | Purpose |
| :-- | :-- | :-- | :-- |
| 1 | Mabhas 9 (1399, 5th ed.) | **107–114** | φ / regime / strain compatibility / stress block / Mn / φMn |
| 2 | Mabhas 9 | **132** | Clause 9-11-2-3 ductility limit |
| 3 | Mabhas 9 | **199** | Clause 9-11-5-1-1…−1-3 minimum steel |
| 4 | Mostofinejad Vol. 1 | **200** | Eqs. (5-46), (5-47) — framing of the sizing methodology |
| 5 | Mostofinejad Vol. 1 | **201–205** | worked Examples 5-5 / 5-6 (independent cross-check values) |

**Then, in order:**
1. visually verify each clause; record footers, page mapping, provenance, checksum;
2. re-run the 12-condition gate (expect gates 1–7 to flip);
3. **adjudicate the `DERIVED`-vs-`CODE_RULE` governance question** (§14);
4. only then implement `BG-FLEX-RECT-REQ-AS-001` with §13's tests and a full gate run.

**Explicitly NOT part of this stage** (separate tasks): the §9-21-5-6 citation defect, the
`rebar/catalog.py` rationale defect, bundle integration, rebar selection, end-to-end
orchestration, and the five frozen H.22 blockers.

---

```
H.24 DECISION:        BLOCKED — source pages not present in this environment.
                      VERIFY_PENDING + NO IMPLEMENTATION (correct result per governance).
                      Derivation recorded as DERIVED; 3/12 gates PASS.

SOURCE ACQUISITION:   Exhaustive search (repo + branch + origin/main + full filesystem) found
                      ONLY three packages: Mabhas 9 printed 422-452 (origin/main), Mabhas 9
                      printed 66-69, ISIRI 11558. NO Mabhas 9 flexural page, NO Mostofinejad
                      page. The repo's own source PDF is a Windows path, never committed; the
                      git-ignored references//ocr//extracted//verification//working/ dirs do
                      not exist here. Nothing manufactured; nothing fetched.

MABHAS 9:             MISSING (pages printed 107-114, 132, 199 absent) -> not visually
                      verified in H.24. NEW FINDING: recorded PDF attributions are mutually
                      inconsistent (-91 flexure set vs +21 shear set vs +20 footer-verified);
                      printed 107 is recorded as BOTH PDF 16 and PDF 128.

MOSTOFINEJAD:         MISSING (printed 200, 201-205 absent) -> not visually verified.
                      NEW FINDINGS: (a) (5-46)+(5-47) is a SECTION-SIZING method (solve bd^2
                      given omega), NOT an As-for-fixed-b,d formula; (b) an As,req solver
                      ALREADY EXISTS (reference/mostofinejad_ch5.solve_required_as) but only
                      in MOSTOFINEJAD_METHODOLOGY_ONLY and on a DIFFERENT resistance model;
                      (c) quantified divergence: Mostofinejad's 0.59 implies alpha0=0.847 vs
                      Mabhas 9's 0.85, and for fc>55 MPa it diverges ~7% (fc=70: coefficient
                      should be 0.633, not 0.59). Reuse in a Mabhas 9 rule = model
                      substitution = prohibited.

As,req DERIVATION:    DERIVED (not a source formula). As^2 - (d/k)As + Mu/(phi*fy*k) = 0,
                      k = fy/(2*alpha0*fc*b); smaller root governs; solvability iff
                      Mu <= phi*alpha0*fc*b*d^2/2 (= moment at a=d); As,req = max(As,flexure,
                      As,min). Traceable to the recorded substrate; evidentiary root
                      uninspectable here.

12-GATE:              1 FAIL · 2 FAIL · 3 BLOCKED · 4 FAIL · 5 FAIL · 6 FAIL · 7 BLOCKED ·
                      8 PASS · 9 PASS · 10 FAIL · 11 BLOCKED · 12 PASS
                      => 3 PASS, 6 FAIL, 3 BLOCKED => PROMOTION NOT ALLOWED

IMPLEMENTATION:       NOT PERFORMED.

RULE:                 BG-FLEX-RECT-REQ-AS-001 — PROPOSED, NOT REGISTERED.
                      status VERIFY_PENDING / execution_allowed=False (no entry created).
                      RuleReference prepared but incomplete (pdf_page unresolvable).

EVIDENCE:             MISSING — required: Mabhas 9 printed 107-114, 132, 199; Mostofinejad
                      printed 200, 201-205 (acquire by printed page; re-establish PDF mapping
                      by footer inspection). Not added by H.24.

REGISTRY:             121 total / 63 executable / 48 blocked / 10 reference — unchanged
                      §9-21-6: 21 executable / 5 blocked — unchanged · duplicate IDs: 0

PYTEST:               673 passed

MYPY:                 Success: no issues found in 23 source files

DOCUMENT:             docs/PHASE2G_H24_FLEXURAL_AS_SOURCE_VERIFICATION.md

COMMIT:               see §16 backfill

ORIGIN/MAIN:          df8067a750ffc7984c9dc5d80220ad9013503aa6 — untouched

NEXT STEP:            User supplies the five page ranges above (printed 107-114, 132, 199
                      Mabhas 9; printed 200, 201-205 Mostofinejad); a follow-up stage then
                      performs visual verification, re-runs the 12-gate, adjudicates the
                      DERIVED-vs-CODE_RULE governance question, and only then implements.
```
