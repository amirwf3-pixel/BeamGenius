# BeamGenius — Verified Rule Registry

## Status Definitions

- VERIFIED — Directly verified against the source page/image.
- VERIFY_PENDING — Located but not yet verified against the source.
- REVIEW_REQUIRED — Evidence exists but requires reconciliation.
- NOT_CHECKED — Not yet reviewed.
- CODE_RULE — Governing requirement from Mabhas 9.
- ENGINEERING_REFERENCE — Engineering/design method from Mostofinejad.

---

# Flexure

## BG-FLEX-MIN-001 — Minimum Flexural Reinforcement

Status: VERIFIED
Type: CODE_RULE
Source: Iranian National Building Regulations — Mabhas 9
PDF Page: 220
Printed Page: 199
Clause: 9-11-5-1-1 / 9-11-5-1-2

Requirement:

Minimum flexural reinforcement shall be provided in all flexural member sections requiring tensile reinforcement.

The minimum flexural reinforcement shall be at least the greater of:

As,min = 0.25 × sqrt(f'c) × bw × d / fy

and

As,min = 1.4 × bw × d / fy

Constraint:

fy ≤ 550 MPa

Additional applicability:

For T- and L-sections with the flange in tension, the applicable effective-width provision of the code shall be applied.

Exception:

The minimum reinforcement requirement may be waived under the condition specified in Clause 9-11-5-1-3 when the provided tensile reinforcement is at least one-third greater than the reinforcement required by analysis.

Verification:

Source page visually verified.

---

## BG-FLEX-STRESS-BLOCK — Equivalent Rectangular Concrete Compression Stress-Block Parameters

Status: VERIFIED
Type: CODE_RULE
Source: Iranian National Building Regulations — Mabhas 9 (1399)
PDF Page: 22–23
Printed Page: 113–114
Clause: 9-8-2-2-6 / 9-8-2-2-7, Eq. (9-8-2), Eq. (9-8-3-الف), Eq. (9-8-3-ب), Eq. (9-8-4) (with f'c limits per Clause 9-3-3-3)

Formula / Requirement:

1. Equivalent rectangular compression stress block depth:
   a = β1 × c   [Eq. (9-8-2)]

2. Equivalent stress-block depth factor β1 (Clause 9-8-2-2-6):
   - For 20 MPa ≤ f'c ≤ 28 MPa:
     β1 = 0.85   [Eq. (9-8-3-الف)]
   - For f'c > 28 MPa:
     β1 = max(0.85 - 0.05 × (f'c - 28) / 7, 0.65)   [Eq. (9-8-3-ب)]

3. Equivalent uniform concrete compressive stress intensity α0 × f'c (Clauses 9-8-2-2-6 and 9-8-2-2-7):
   - For f'c ≤ 55 MPa:
     α0 = 0.85   [Clause 9-8-2-2-6]
   - For f'c > 55 MPa:
     α0 = max(0.85 - 0.004 × (f'c - 55), 0.75)   [Eq. (9-8-4)]

Applicability:

Non-prestressed reinforced concrete flexural members designed under Mabhas 9 Chapter 9-8 with specified concrete compressive strength 20 MPa ≤ f'c ≤ 70 MPa (Clause 9-3-3-3).

Inputs:

- fc_prime_mpa: specified concrete compressive strength f'c (MPa)
- c_mm: optional neutral-axis depth c measured from extreme compression fiber (mm)

Units:

- fc_prime_mpa: MPa
- c_mm, a_mm: mm
- α0, β1: dimensionless

Exceptions / Blocked Conditions:

- Concrete strengths outside the Mabhas 9 structural concrete range (f'c < 20 MPa or f'c > 70 MPa per Clause 9-3-3-3) are rejected as `INVALID_INPUT` when code bounds are enforced.
- CSA A23.3-14 stress-block equations (`BG-MOST-5-49`, `BG-MOST-5-50`) belong exclusively to `MOSTOFINEJAD_METHODOLOGY_ONLY` and must never be used in `MABHAS_9_COMPLIANCE`.

Verification Method:

Actual source page review (Mabhas 9, 1399 Edition, Chapter 9-8, PDF Pages 22–23, Printed Pages 113–114, Clauses 9-8-2-2-6 and 9-8-2-2-7).

---

## BG-FLEX-STRAIN-LIMIT — Flexural Strain Compatibility and Tension-Controlled Beam Ductility Limit

Status: VERIFIED
Type: CODE_RULE
Source: Iranian National Building Regulations — Mabhas 9 (1399)
PDF Page: 16–18, 22, 41
Printed Page: 107–109, 113, 132
Clause: 9-8-2-2-2 / 9-8-2-2-3 / 9-7-4-2 / 9-7-4-3 / 9-11-2-3 (with Es = 200,000 MPa per Clause 9-4-8-4 and fy ≤ 550 MPa per Table 9-4-4)

Formula / Requirement:

1. Maximum usable concrete compressive strain at extreme compression fiber (Clause 9-8-2-2-3):
   εcu = 0.003

2. Linear strain compatibility across section depth (Clause 9-8-2-2-2):
   εt = εcu × (dt - c) / c = 0.003 × (dt - c) / c

3. Reinforcement tension yield strain (Clause 9-2-2 / Clause 9-7-4-2 / Clause 9-4-8-4):
   εty = fy / Es, where Es = 200,000 MPa

4. Tension-controlled section limit and mandatory beam ductility requirement (Clause 9-7-4-2, Table 9-7-2, and Clause 9-11-2-3):
   For non-prestressed beams with factored axial load Pu < 0.10 × f'c × Ag, the section at nominal flexural strength shall be tension-controlled:
   εt ≥ εty + 0.003
   Equivalently in terms of neutral-axis ratio:
   c / dt ≤ 0.003 / (εty + 0.006)

Applicability:

Non-prestressed reinforced concrete beams with Pu < 0.10 × f'c × Ag and longitudinal flexural reinforcement yield strength fy ≤ 550 MPa (Table 9-4-4).

Inputs:

- c_mm: neutral-axis depth from extreme compression fiber (mm)
- dt_mm: distance from extreme compression fiber to extreme tension steel (mm)
- fy_mpa: specified longitudinal reinforcement yield strength fy (MPa)
- es_mpa: reinforcement modulus of elasticity Es (MPa, default 200,000 MPa)

Units:

- c_mm, dt_mm: mm
- fy_mpa, es_mpa: MPa
- εcu, εty, εt, c/dt: dimensionless

Exceptions / Blocked Conditions:

- Sections with εt < εty + 0.003 (i.e., transition-zone or compression-controlled sections) do not satisfy Clause 9-11-2-3 for non-prestressed beams with Pu < 0.10 × f'c × Ag and return `FAIL`.
- The older ACI/legacy approximation ρmax = 0.75 × ρb is NOT part of Mabhas 9 (1399) and must not be used.

Verification Method:

Actual source page review (Mabhas 9, 1399 Edition, Chapters 9-7, 9-8, and 9-11, PDF Pages 16–18, 22, 41, Printed Pages 107–109, 113, 132).

---

## BG-FLEX-PHI-FACTOR — Flexural Strength Reduction Factor φ

Status: VERIFIED
Type: CODE_RULE
Source: Iranian National Building Regulations — Mabhas 9 (1399)
PDF Page: 16–18
Printed Page: 107–109
Clause: 9-7-4-1 / 9-7-4-2 / 9-7-4-3 / 9-7-4-4, Table 9-7-2, Eq. (9-7-10-الف), Eq. (9-7-10-ب)

Formula / Requirement:

For members subject to moment, axial force, or combined moment and axial force (Table 9-7-2, Item 1):

1. Tension-controlled sections (Clause 9-7-4-2, εt ≥ εty + 0.003):
   φ = 0.90

2. Compression-controlled sections (Clause 9-7-4-3, εt ≤ εty):
   - Members with spiral reinforcement: φ = 0.75
   - Other members (tied beams/columns): φ = 0.65

3. Transition-zone sections (Clause 9-7-4-4, εty < εt < εty + 0.003):
   - Members with spiral reinforcement [Eq. (9-7-10-الف)]:
     φ = 0.75 + 0.15 × (εt - εty) / 0.003
   - Other members (tied beams) [Eq. (9-7-10-ب)]:
     φ = 0.65 + 0.25 × (εt - εty) / 0.003

Applicability:

Reinforced concrete sections under flexure or combined flexure and axial load governed by Mabhas 9 Chapter 9-7.

Inputs:

- epsilon_t: net tensile strain in extreme tension steel at nominal strength εt (dimensionless)
- fy_mpa: specified longitudinal reinforcement yield strength fy (MPa)
- es_mpa: reinforcement modulus of elasticity Es (MPa, default 200,000 MPa)
- is_spiral_transverse: boolean indicating spiral confinement (default False for tied beams)

Units:

- epsilon_t, εty, φ: dimensionless
- fy_mpa, es_mpa: MPa

Exceptions / Blocked Conditions:

- While Table 9-7-2 and Eqs. (9-7-10-الف)/(9-7-10-ب) define φ across all three strain regimes, Clause 9-11-2-3 requires non-prestressed beams with Pu < 0.10 × f'c × Ag to be tension-controlled (εt ≥ εty + 0.003, where φ = 0.90).

Verification Method:

Actual source page review (Mabhas 9, 1399 Edition, Chapter 9-7, PDF Pages 16–18, Printed Pages 107–109, Table 9-7-2 and Clauses 9-7-4-1 through 9-7-4-4).

---

## BG-FLEX-RECT-SINGLY-001 — Rectangular Singly-Reinforced Beam Flexural Resistance

Status: VERIFIED
Type: CODE_RULE
Source: Iranian National Building Regulations — Mabhas 9 (1399)
PDF Page: 16–18, 21–23, 41
Printed Page: 107–109, 112–114, 132
Clause: 9-8-1-4 Eq. (9-8-1-الف), 9-8-2-1-1, 9-8-2-2-1 through 9-8-2-2-8, 9-7-4-2, Table 9-7-2, 9-11-2-3, 9-3-3-3, 9-4-8-3 through 9-4-8-5, Table 9-4-4

Formula / Requirement:

For a rectangular singly-reinforced non-prestressed beam section of width b = bw and effective depth d with tensile reinforcement area As:

1. Stress-block parameters (`BG-FLEX-STRESS-BLOCK`):
   - α0 = 0.85 for f'c ≤ 55 MPa; α0 = max(0.85 - 0.004 × (f'c - 55), 0.75) for f'c > 55 MPa
   - β1 = 0.85 for f'c ≤ 28 MPa; β1 = max(0.85 - 0.05 × (f'c - 28) / 7, 0.65) for f'c > 28 MPa

2. Equilibrium and strain compatibility (`BG-FLEX-STRAIN-LIMIT`):
   - For yielding tension reinforcement (εt ≥ εty = fy / Es):
     a = (As × fy) / (α0 × f'c × bw)
     c = a / β1
     εt = 0.003 × (dt - c) / c
     fs = fy
   - Maximum tension-controlled reinforcement limit per Clause 9-11-2-3 (εt ≥ εty + 0.003):
     c_max,tc = (0.003 / (εty + 0.006)) × dt
     a_max,tc = β1 × c_max,tc
     As,max,tc = (α0 × f'c × bw × a_max,tc) / fy
     ρ_max,tc = As,max,tc / (bw × d)

3. Nominal and design flexural resistance (`BG-FLEX-PHI-FACTOR` and Clause 9-8-1-4):
   Mn = As × fs × (d - a / 2)
   φMn = φ × Mn ≥ Mu   [Eq. (9-8-1-الف)]
   with φ = 0.90 in the required tension-controlled regime (εt ≥ εty + 0.003).

Applicability:

Singly-reinforced rectangular non-prestressed concrete beams (Pu < 0.10 × f'c × Ag) with 20 MPa ≤ f'c ≤ 70 MPa and fy ≤ 550 MPa.

Inputs:

- bw_mm: rectangular beam width bw (mm)
- h_mm: total section depth h (mm)
- d_effective_mm: effective depth d from extreme compression fiber to centroid of tension reinforcement (mm), resolved via Phase 1 effective-depth precedence
- fc_prime_mpa: specified concrete compressive strength f'c (MPa)
- fy_mpa: specified longitudinal reinforcement yield strength fy (MPa)
- es_mpa: modulus of elasticity Es (MPa, default 200,000 MPa)
- as_provided_mm2: provided tensile reinforcement area As (mm²)
- mu_nmm: optional factored bending moment demand Mu (N·mm)

Units:

- bw_mm, h_mm, d_effective_mm, dt_mm, a_mm, c_mm: mm
- as_provided_mm2, as_max_tc_mm2: mm²
- fc_prime_mpa, fy_mpa, es_mpa, fs_mpa: MPa
- mn_nmm, phi_mn_nmm, mu_nmm: N·mm

Exceptions / Blocked Conditions:

- Doubly-reinforced sections with compression reinforcement (`as_compression_mm2 > 0`) are NOT covered by this rule and MUST return `UNVERIFIED_RULE_BLOCKED` (`BG-FLEX-RECT-DOUBLY-001`).
- T-beam and L-beam sections (`SectionType.T_SECTION`, `SectionType.L_SECTION`) MUST NOT silently fall back to rectangular flexural capacity and MUST return `UNVERIFIED_RULE_BLOCKED` (`BG-FLEX-TBEAM-CAP-001`, `BG-FLEX-LBEAM-CAP-001`).
- Never uses Mostofinejad initial depth estimates `d ≈ h - 65` or `d ≈ h - 90`.

Verification Method:

Actual source page review (Mabhas 9, 1399 Edition, Chapters 9-3, 9-4, 9-7, 9-8, and 9-11, PDF Pages 16–18, 21–23, 41, Printed Pages 107–109, 112–114, 132).

---

## BG-FLEX-TBEAM-B-EFF-001 — Non-Prestressed T-Beam and L-Beam Effective Compression Flange Width

Status: VERIFIED
Type: CODE_RULE
Source: Iranian National Building Regulations — Mabhas 9 (1399)
PDF Page: 12–13, 41
Printed Page: 103–104, 132
Clause: 9-6-3-3-1, Table 9-6-1, 9-6-3-3-2, and 9-11-2-5

Formula / Requirement:

1. Non-prestressed T-beams and L-beams integral with slab (Clause 9-6-3-3-1, Table 9-6-1, and Clause 9-11-2-5):
   - Flange on both sides of web (T-section, `SectionType.T_SECTION`):
     Effective overhanging flange width on each side of the web shall not exceed:
     b_overhang,each ≤ min(8 × hf, sw / 2, ln / 8)
     Total effective compression flange width:
     bf ≤ bw + 2 × min(8 × hf, sw / 2, ln / 8)
   - Flange on one side of web only (L-section, `SectionType.L_SECTION`):
     Effective overhanging flange width from the web face shall not exceed:
     b_overhang ≤ min(6 × hf, sw / 2, ln / 12)
     Total effective compression flange width:
     bf ≤ bw + min(6 × hf, sw / 2, ln / 12)

2. Isolated non-prestressed T-beams (Clause 9-6-3-3-2):
   Where an isolated T-beam shape is used to provide additional compression area:
   - Flange thickness: hf ≥ 0.5 × bw
   - Effective flange width: bf ≤ 4 × bw

Applicability:

Non-prestressed T-beams and L-beams with the flange in compression (`FlangeCondition.FLANGE_IN_COMPRESSION`).

Inputs:

- section_type: `T_SECTION` or `L_SECTION`
- flange_condition: `FLANGE_IN_COMPRESSION`
- bw_mm: web width bw (mm)
- h_mm: total beam depth h (mm)
- tf_mm: slab/flange thickness hf (mm, denoted h in Table 9-6-1)
- clear_web_spacing_sw_mm: clear distance between adjacent webs sw (mm, for slab-integral T/L beams)
- clear_span_ln_mm: clear beam span ln (mm, for slab-integral T/L beams)
- is_isolated_t_beam: boolean (True for isolated T-beams governed by Clause 9-6-3-3-2)
- bf_provided_mm: optional provided/assumed flange width bf (mm) checked against the code limit

Units:

- bw_mm, h_mm, tf_mm, clear_web_spacing_sw_mm, clear_span_ln_mm, bf_provided_mm, bf_limit_mm: mm

Exceptions / Blocked Conditions:

- T- and L-sections with the flange in tension (`FlangeCondition.FLANGE_IN_TENSION`) are NOT governed by Table 9-6-1 compression flange limits and remain `UNVERIFIED_RULE_BLOCKED`.
- Verification of effective compression flange width `bf` (`BG-FLEX-TBEAM-B-EFF-001`) does NOT unlock full T-beam or L-beam flexural capacity (`BG-FLEX-TBEAM-CAP-001`, `BG-FLEX-LBEAM-CAP-001`), which remain `VERIFY_PENDING` and `UNVERIFIED_RULE_BLOCKED`.

Verification Method:

Actual source page review (Mabhas 9, 1399 Edition, Chapters 9-6 and 9-11, PDF Pages 12–13 and 41, Printed Pages 103–104 and 132, Clauses 9-6-3-3-1, 9-6-3-3-2, Table 9-6-1, and Clause 9-11-2-5).

---

# Shear

## BG-SHEAR-MIN-001 — Minimum Shear Reinforcement

Status: VERIFIED
Type: CODE_RULE
Source: Iranian National Building Regulations — Mabhas 9
PDF Page: 221
Clause: 9-11-5-2

Requirement:

Where minimum shear reinforcement is required, the required shear reinforcement ratio shall satisfy:

Av/s ≥ 0.062 × sqrt(f'c) × bw / fyt

and

Av/s ≥ 0.35 × bw / fyt

Therefore:

(Av/s)min =
max(
0.062 × sqrt(f'c) × bw / fyt,
0.35 × bw / fyt
)

Important applicability:

Minimum shear reinforcement is not an unconditional requirement for every beam region. The code exceptions in Table 9-11-2 shall be evaluated before applying this requirement.

Verified exceptions include:

1. Shallow beam:
   h ≤ 250 mm

2. Beam integral with slab:
   h ≤ max(2.5 × tf, 0.5 × bw)
   and
   h ≤ 600 mm

3. Steel-fiber normal reinforced concrete:
   h ≤ 600 mm
   Vu ≤ φ × 0.17 × sqrt(f'c) × bw × d
   f'c ≤ 40 MPa

4. One-way joists subject to the applicable code provision.

Verification:

Source page/rule verified against Mabhas 9 source material.

---

## BG-SHEAR-SPACING-001 — Maximum Stirrup Spacing

Status: VERIFIED
Type: CODE_RULE
Source: Iranian National Building Regulations — Mabhas 9
PDF Page: 227
Clause: 9-11-6-5-3

Condition 1:

If:

Vs ≤ 0.33 × sqrt(f'c) × bw × d

then longitudinal stirrup spacing shall satisfy:

s ≤ min(d/2, 600 mm)

and transverse-leg spacing shall satisfy:

st ≤ min(d, 600 mm)

Condition 2:

If:

Vs > 0.33 × sqrt(f'c) × bw × d

then longitudinal stirrup spacing shall satisfy:

s ≤ min(d/4, 300 mm)

and transverse-leg spacing shall satisfy:

st ≤ min(d/2, 300 mm)

Verification:

Source page visually verified.

---

# Transverse Reinforcement & Detailing

## BG-DETAIL-TRANS-DIA-001 — Minimum Transverse Reinforcement Diameter

Status: VERIFIED
Type: CODE_RULE
Source: Iranian National Building Regulations — Mabhas 9
PDF Page: 228
Printed Page: Not recorded (PDF Page 228 verified)
Clause: 9-11-6-5-11 (OCR token in DESIGN_RULES.md: 11-5-6-11-9)

Formula / Requirement:

For transverse reinforcement (stirrups/ties) enclosing longitudinal bars in beams:

- If longitudinal bar diameter db ≤ 32 mm (non-bundled):
  dbt ≥ 10 mm
- If longitudinal bar diameter db ≥ 36 mm (non-bundled):
  dbt ≥ 12 mm
- If longitudinal bars are bundled:
  dbt ≥ 12 mm

Applicability:

Beams requiring transverse stirrups or ties enclosing longitudinal reinforcement.

Inputs:

- db: longitudinal bar diameter(s) enclosed by transverse reinforcement (mm)
- dbt: transverse bar diameter (mm)
- is_bundled: whether the longitudinal bars are bundled (boolean)

Units:

- db, dbt: mm

Exceptions / Blocked Conditions:

- The interval 32 mm < db < 36 mm for non-bundled bars MUST NOT be inferred and shall return an explicit blocked/unsupported status (`UNVERIFIED_RULE_BLOCKED` / `UNSUPPORTED_CONFIGURATION`).
- Welded wire reinforcement exceptions remain `VERIFY_PENDING` unless independently verified from Mabhas 9.

Verification Method:

Actual source page review (Mabhas 9, PDF Page 228, Clause 9-11-6-5-11).

---

## BG-DETAIL-COMP-LAT-001 — Compression Reinforcement Lateral Support Spacing

Status: VERIFIED
Type: CODE_RULE
Source: Iranian National Building Regulations — Mabhas 9
PDF Page: 229
Printed Page: Not recorded (PDF Page 229 verified)
Clause: 9-11-6-5-12 (OCR token in DESIGN_RULES.md: 12-5-6-11-9)

Formula / Requirement:

Longitudinal spacing of transverse reinforcement enclosing compression bars shall satisfy:

sc ≤ min(
16 × db,
48 × dbt,
bmin
)

Applicability:

Beam sections containing longitudinal compression reinforcement required by analysis or design.

Inputs:

- db: smallest diameter of longitudinal compression bars (mm)
- dbt: diameter of transverse stirrup/tie bar (mm)
- bmin: least dimension of the compression member/section (mm)
- sc: provided longitudinal center-to-center spacing of transverse ties supporting compression bars (mm)

Units:

- db, dbt, bmin, sc: mm

Exceptions / Blocked Conditions:

- Where no compression reinforcement is required, this check is `NOT_APPLICABLE`.

Verification Method:

Actual source page review (Mabhas 9, PDF Page 229, Clause 9-11-6-5-12).

---

# Continuity, Support Reinforcement & Structural Integrity

## BG-INTEG-PERIMETER-001 — Structural Integrity Reinforcement for Perimeter Beams

Status: VERIFIED
Type: CODE_RULE
Source: Iranian National Building Regulations — Mabhas 9
PDF Page: 229–230
Printed Page: Not recorded (PDF Pages 229–230 verified)
Clause: 9-11-6-6-1

Formula / Requirement:

For cast-in-place perimeter beams:

1. Continuous positive reinforcement:
   As,cont(+) ≥ (1/4) × As,max(+)
   and
   n_bars,cont(+) ≥ 2

2. Continuous negative reinforcement:
   As,cont(-) ≥ (1/6) × As,support(-)
   and
   n_bars,cont(-) ≥ 2

3. Transverse enclosure:
   Structural-integrity longitudinal reinforcement shall be enclosed by closed stirrups or closed ties along the clear span of the beam.

Applicability:

Cast-in-place perimeter beams governed by Clause 9-11-6-6-1.

Inputs:

- is_perimeter_beam: boolean (must be True for Clause 9-11-6-6-1)
- as_max_positive_mm2: maximum positive flexural reinforcement area in span (mm²)
- as_support_negative_mm2: negative flexural reinforcement area at support (mm²)
- as_continuous_positive_provided_mm2: provided continuous positive reinforcement area (mm²)
- continuous_positive_bar_count: number of continuous positive bars (integer)
- as_continuous_negative_provided_mm2: provided continuous negative reinforcement area (mm²)
- continuous_negative_bar_count: number of continuous negative bars (integer)
- is_enclosed_by_closed_stirrups_over_clear_span: boolean

Units:

- Reinforcement areas: mm²
- Bar counts: integer count

Exceptions / Blocked Conditions:

- Non-perimeter beams governed by Clause 9-11-6-6-2 are NOT fully verified and MUST remain `BLOCKED` (`VERIFY_PENDING`).
- Mechanical/welded/lap splice compliance of integrity reinforcement remains `VERIFY_PENDING` unless bars are continuous without splices or splice rules are separately verified in `docs/VERIFIED_RULES.md`.

Verification Method:

Actual source page review (Mabhas 9, PDF Pages 229–230, Clause 9-11-6-6-1).

---

## BG-INTEG-COL-001 — Structural Integrity Continuity Through Column Region

Status: VERIFIED
Type: CODE_RULE
Source: Iranian National Building Regulations — Mabhas 9
PDF Page: 230
Printed Page: Not recorded (PDF Page 230 verified)
Clause: 9-11-6-6-3 (OCR token in DESIGN_RULES.md: 11-6-6-3-9)

Formula / Requirement:

Structural-integrity longitudinal reinforcement shall pass through the region enclosed by the longitudinal reinforcement of the supporting column (`passes_through_column_core == True`).

Applicability:

Structural-integrity longitudinal reinforcement at continuous or interior column supports.

Inputs:

- passes_through_column_core: boolean indicating whether the continuous integrity bars pass inside the column longitudinal reinforcement cage.

Units:

- Boolean geometric detailing state.

Exceptions / Blocked Conditions:

- At non-continuous supports, anchorage is governed by Clause 9-11-6-6-4 (`BG-INTEG-ANCHOR-001`).

Verification Method:

Actual source page review (Mabhas 9, PDF Page 230, Clause 9-11-6-6-3).

---

## BG-INTEG-ANCHOR-001 — Structural Integrity Anchorage at Non-Continuous Supports

Status: VERIFIED
Type: CODE_RULE
Source: Iranian National Building Regulations — Mabhas 9
PDF Page: 230
Printed Page: Not recorded (PDF Page 230 verified)
Clause: 9-11-6-6-4 (OCR token in DESIGN_RULES.md: 11-6-6-4-9)

Formula / Requirement:

At non-continuous supports, structural-integrity longitudinal reinforcement shall be anchored into the support so that it can develop the specified yield stress fy at the face of the support.

Applicability:

Structural-integrity longitudinal reinforcement terminating at non-continuous supports.

Inputs:

- is_non_continuous_support: boolean
- develops_fy_at_support_face: boolean (when externally verified)

Units:

- Boolean / mm (when quantitative development length rules are verified).

Exceptions / Blocked Conditions:

- Quantitative calculation of required straight development length Ld (`BG-DEV-LENGTH-PENDING`) or standard hook development length ldh (`BG-BENT-ANCHOR-PENDING`) remains `BLOCKED` (`VERIFY_PENDING`) until the governing Mabhas 9 development/hook equations are visually verified and added to `docs/VERIFIED_RULES.md`.

Verification Method:

Actual source page review (Mabhas 9, PDF Page 230, Clause 9-11-6-6-4).

---

## BG-SUPPORT-POS-001 — Positive Flexural Reinforcement Continuation at Supports

Status: VERIFIED
Type: CODE_RULE
Source: Iranian National Building Regulations — Mabhas 9
PDF Page: 225
Printed Page: Not recorded (PDF Page 225 verified)
Clause: 9-11-6-3-2 (OCR token in DESIGN_RULES.md: 2-3-6-11-9)

Formula / Requirement:

1. Simple support:
   As,support(+) ≥ (1/3) × As,max(+)
   and
   l_embed,support ≥ 150 mm

2. Interior support:
   As,support(+) ≥ (1/4) × As,max(+)
   and
   l_embed,support ≥ 150 mm

3. Primary lateral-load-resisting system beams:
   Positive reinforcement continued into the support shall be anchored to develop the specified yield stress fy at the face of the support.

Applicability:

Positive flexural reinforcement continuation into simple and interior supports of beams.

Inputs:

- support_type: `SIMPLE` or `INTERIOR`
- as_max_positive_mm2: maximum positive flexural reinforcement area in the span (mm²)
- as_positive_into_support_mm2: positive flexural reinforcement area continued into the support (mm²)
- support_embedment_length_mm: embedment length of continued positive reinforcement into the support (mm)
- is_primary_lateral_load_resisting: boolean
- develops_fy_at_support_face: optional boolean (required when `is_primary_lateral_load_resisting == True`)

Units:

- Areas: mm²
- Lengths: mm

Exceptions / Blocked Conditions:

- Supersedes the older 1/4 simple-support transcription in `docs/DESIGN_RULES.md`; simple supports require at least 1/3 of maximum positive reinforcement.
- Quantitative calculation of the required yield development/hook length (Ld or ldh) for primary lateral-load-resisting beams remains `BLOCKED` (`VERIFY_PENDING`) until `BG-DEV-LENGTH-PENDING` and `BG-BENT-ANCHOR-PENDING` are verified in `docs/VERIFIED_RULES.md`.

Verification Method:

Actual source page review (Mabhas 9, PDF Page 225, Clause 9-11-6-3-2).

---

# Verification Policy

No rule shall become executable engineering logic solely from OCR.

For every VERIFIED rule, BeamGenius shall retain:

- source document
- exact clause
- PDF page
- verification status
- governing formula/requirement
- applicability conditions
- exceptions

If OCR conflicts with the source page, the source page governs.

If Mostofinejad and Mabhas 9 differ, Mabhas 9 governs mandatory code compliance while Mostofinejad remains the primary engineering reference for calculation methodology.
