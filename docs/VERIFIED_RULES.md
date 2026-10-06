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

## BG-SHEAR-PHI-001 — Shear Strength Reduction Factor φ and Factored One-Way Shear Check

Status: VERIFIED
Type: CODE_RULE
Source: Iranian National Building Regulations — Mabhas 9 (1399, 5th Edition)
PDF Page: 128, 130–131, 133, 140 (Design Excerpt PDF Pages: 16, 18–19, 21, 28)
Printed Page: 107, 109–110, 112, 119
Clause: 9-7-4-1, Table 9-7-2 (Row 2), 9-7-4-5, 9-8-1-4 Eq. (9-8-1-ب), 9-8-4-1-1, 9-8-4-1-2 Eq. (9-8-8), 9-11-3-3, 9-11-4-3

Formula / Requirement:

1. Strength reduction factor for one-way shear (Clause 9-7-4-1 and Table 9-7-2, Row 2):
   φ = 0.75

2. Nominal and factored one-way shear resistance check (Clauses 9-8-1-4, 9-8-4-1-1, 9-8-4-1-2, 9-11-4-3):
   Vn = Vc + Vs   [Eq. (9-8-8)]
   φ × Vn = φ × (Vc + Vs) ≥ Vu   [Eq. (9-8-1-ب)]

3. Minimum shear reinforcement trigger threshold in beams (Clause 9-11-5-2-1):
   - Standard beams not satisfying Table 9-11-2: minimum shear reinforcement Av,min is required where
     Vu > 0.08 × φ × λ × sqrt(f'c) × bw × d
   - Beams satisfying a Table 9-11-2 condition: minimum shear reinforcement Av,min is not required where
     Vu ≤ φ × Vc

Applicability:

Non-prestressed reinforced concrete beams under standard one-way shear design governed by Mabhas 9 Chapters 9-7, 9-8, and 9-11.

Inputs:

- vu_n: optional factored shear force demand Vu (N)
- vc_n: optional nominal concrete shear resistance Vc (N)
- vs_n: optional nominal transverse reinforcement shear resistance Vs (N)
- is_seismic_capacity_governed: boolean indicating whether Clause 9-7-4-5 seismic shear capacity design governs (default False)
- is_beam_column_joint_or_diagonal_coupling_beam: boolean indicating beam-column joint or diagonally reinforced coupling beam under Clause 9-7-4-5 (default False)

Units:

- φ: dimensionless
- vu_n, vc_n, vs_n, vn_n, phi_vn_n: N

Exceptions / Blocked Conditions:

- Seismic capacity-design shear provisions under Clause 9-7-4-5 (φ = 0.60 when nominal shear strength is less than the shear corresponding to development of nominal flexural strength in special seismic systems in high/very-high seismic zones, and φ = 0.85 for beam-column joints and diagonally reinforced coupling beams) depend on Chapter 9-20 seismic capacity-design shear demands (`Ve`) and return `UNVERIFIED_RULE_BLOCKED` when requested (`is_seismic_capacity_governed == True` or `is_beam_column_joint_or_diagonal_coupling_beam == True`).

Verification Method:

Actual source page review (Mabhas 9, 1399 Edition, Chapters 9-7, 9-8, and 9-11, Complete PDF Pages 128, 130–131, 133, 140, Printed Pages 107, 109–110, 112, 119, Table 9-7-2 and Clauses 9-7-4-1, 9-7-4-5, 9-8-1-4, and 9-8-4-1).

---

## BG-SHEAR-VC-001 — Concrete One-Way Shear Resistance Vc

Status: VERIFIED
Type: CODE_RULE
Source: Iranian National Building Regulations — Mabhas 9 (1399, 5th Edition)
PDF Page: 76–77, 140–142, 218–221 (Design Excerpt PDF Pages: 28–30)
Printed Page: 55–56, 119–121, 197–200
Clause: 9-8-4-4-1 through 9-8-4-4-5, Eq. (9-8-12-الف), Eq. (9-8-12-ب), Eq. (9-8-13), Eq. (9-8-14), 9-8-4-2-2, 9-3-2-2, Tables 9-3-1 & 9-3-2, 9-3-2-3, 9-3-3-3, 9-11-4-3

Formula / Requirement:

1. Concrete compressive strength square-root limit in one-way shear (Clause 9-8-4-2-2):
   - In general one-way shear: sqrt(f'c)_eff = min(sqrt(f'c), 8.3 MPa)
   - Exception (Clause 9-8-4-2-2): In concrete beams and joists reinforced with at least minimum web shear reinforcement per Clause 9-11-5-2 (Av ≥ Av,min), the 8.3 MPa limit is waived (sqrt(f'c)_eff = sqrt(f'c) for 20 MPa ≤ f'c ≤ 70 MPa).

2. Lightweight concrete modification factor λ (Clauses 9-3-2-2 & 9-3-2-3, Tables 9-3-1 & 9-3-2):
   - Normal-weight concrete (Clause 9-3-2-3): λ = 1.0
   - Lightweight concrete (Clause 9-3-2-2, Table 9-3-2): 0.75 ≤ λ ≤ 1.0 (0.75 for all-lightweight, 0.85 for sand-lightweight, or per Table 9-3-1 equilibrium density wc).

3. Size-effect modification factor λs (Clause 9-8-4-4-5, Eq. (9-8-14)):
   λs = min(sqrt(2 / (1 + d / 250)), 1.0) = min(sqrt(2 / (1 + 0.004 × d)), 1.0)   [Eq. (9-8-14)]
   where d is in mm.

4. Axial force stress modifier (Clauses 9-8-4-4-1 & 9-8-4-4-3):
   - Nu is positive for axial compression (Nu > 0) and negative for axial tension (Nu < 0).
   - For axial compression (Clause 9-8-4-4-3):
     Nu / (6 × Ag) ≤ 0.05 × f'c
   - Effective axial stress term:
     σN,eff = min(Nu / (6 × Ag), 0.05 × f'c)

5. Concrete shear resistance Vc for sections with at least minimum transverse reinforcement Av ≥ Av,min (Clause 9-8-4-4-1):
   - Simplified equation [Eq. (9-8-12-الف)]:
     Vc,raw = (0.17 × λ × sqrt(f'c)_eff + σN,eff) × bw × d
   - Detailed longitudinal reinforcement ratio equation [Eq. (9-8-12-ب)]:
     Vc,raw = (0.66 × λ × (ρw)^(1/3) × sqrt(f'c)_eff + σN,eff) × bw × d
     where ρw = As / (bw × d).

6. Concrete shear resistance Vc for sections with less than minimum transverse reinforcement Av < Av,min (Clause 9-8-4-4-2):
   - Size-effect equation [Eq. (9-8-13)]:
     Vc,raw = (0.66 × λs × λ × (ρw)^(1/3) × sqrt(f'c)_eff + σN,eff) × bw × d

7. Lower and upper bounds on Vc (Clauses 9-8-4-4-1 & 9-8-4-4-4):
   0 ≤ Vc ≤ 0.42 × λ × sqrt(f'c)_eff × bw × d
   Therefore:
   Vc = min(max(Vc,raw, 0.0), 0.42 × λ × sqrt(f'c)_eff × bw × d)

Applicability:

Non-prestressed reinforced concrete beam sections with 20 MPa ≤ f'c ≤ 70 MPa (Clause 9-3-3-3).

Inputs:

- bw_mm: web width bw (mm)
- h_mm: total section depth h (mm)
- d_effective_mm: effective depth d (mm), resolved via Phase 1 effective-depth precedence
- fc_prime_mpa: specified concrete compressive strength f'c (MPa)
- lambda_factor: concrete modification factor λ (dimensionless, default 1.0 for normal-weight concrete)
- has_minimum_shear_reinforcement: boolean indicating whether Av ≥ Av,min is provided (default True)
- use_detailed_rho_w_equation: boolean selecting Eq. (9-8-12-ب) when Av ≥ Av,min (default False, which selects Eq. (9-8-12-الف); when Av < Av,min, Eq. (9-8-13) is always used)
- rho_w: optional longitudinal tension reinforcement ratio As / (bw × d) (dimensionless; can also be derived from as_longitudinal_tension_mm2 or geometry.tension_rebar_groups)
- nu_n: optional factored axial force Nu (N, positive in compression, negative in tension, default 0.0 N)
- ag_mm2: optional gross cross-sectional area Ag (mm², defaults to bw × h for rectangular sections)

Units:

- bw_mm, h_mm, d_effective_mm: mm
- ag_mm2, as_longitudinal_tension_mm2: mm²
- fc_prime_mpa: MPa
- lambda_factor, λs, ρw: dimensionless
- nu_n, vc_n: N

Exceptions / Blocked Conditions:

- Members with web openings (Clause 9-8-4-1-4), unquantified restraint creep/shrinkage tension (Clause 9-8-4-1-5), variable-depth haunches with inclined flexural compression (Clause 9-8-4-1-6), circular sections (Clause 9-8-4-2-1), one-way joists (Clause 9-11-4-3-2 / Clause 9-11-7), and seismic special moment frame hinges where Vc = 0 (Clause 9-20-5-2-4-2) return `UNVERIFIED_RULE_BLOCKED` when flagged.

Verification Method:

Actual source page review (Mabhas 9, 1399 Edition, Chapters 9-3, 9-8, and 9-11, Complete PDF Pages 76–77, 140–142, 218–221, Printed Pages 55–56, 119–121, 197–200, Clauses 9-3-2-2, 9-8-4-2-2, and 9-8-4-4-1 through 9-8-4-4-5).

---

## BG-SHEAR-VS-001 — Transverse Reinforcement One-Way Shear Resistance Vs and Demand

Status: VERIFIED
Type: CODE_RULE
Source: Iranian National Building Regulations — Mabhas 9 (1399, 5th Edition)
PDF Page: 89–90, 140, 142–144 (Design Excerpt PDF Pages: 28, 30–32)
Printed Page: 68–69, 119, 121–123
Clause: 9-8-4-1-2 Eq. (9-8-8), 9-8-4-2-3, 9-4-8-5, Table 9-4-4, 9-8-4-5-1 Eq. (9-8-15), 9-8-4-5-3 Eq. (9-8-16), 9-8-4-5-4 Eq. (9-8-17)

Formula / Requirement:

1. Transverse shear reinforcement design yield strength limit (Clauses 9-8-4-2-3 & 9-4-8-5, Table 9-4-4):
   For non-seismic deformed stirrups, ties, and hoops in shear:
   fyt ≤ 420 MPa

2. Provided shear resistance of vertical transverse reinforcement perpendicular to member axis (Clause 9-8-4-5-3, Eq. (9-8-16), α = 90°):
   Vs = Av × fyt × d / s   [Eq. (9-8-16)]
   where Av = n_legs × (π × dbt² / 4) is the total cross-sectional area of all stirrup legs within spacing s.

3. Provided shear resistance of inclined stirrups at angle 45° ≤ α ≤ 90° to longitudinal tension reinforcement (Clause 9-8-4-5-4 الف, Eq. (9-8-17)):
   Vs = Av × fyt × (sin α + cos α) × d / s   [Eq. (9-8-17)]

4. Required transverse reinforcement shear resistance and area ratio (Clause 9-8-4-5-1, Eq. (9-8-15)):
   Vs,req = max(Vu / φ - Vc, 0.0)   [Eq. (9-8-15)]
   - Vertical stirrups (α = 90°):
     (Av / s)_req = Vs,req / (fyt × d)
   - Inclined stirrups (45° ≤ α ≤ 90°):
     (Av / s)_req = Vs,req / (fyt × (sin α + cos α) × d)

Applicability:

Non-prestressed reinforced concrete beams with vertical stirrups (α = 90°) or inclined stirrups (45° ≤ α ≤ 90°) and transverse reinforcement yield strength fyt ≤ 420 MPa (Table 9-4-4).

Inputs:

- d_effective_mm: effective depth d (mm), resolved via Phase 1 effective-depth precedence
- fyt_mpa: transverse reinforcement yield strength fyt (MPa, ≤ 420 MPa)
- stirrups: optional `StirrupLayout` (providing dbt, num_legs, s, Av, and Av/s)
- av_over_s_provided_mm2_per_mm: optional explicit provided Av/s (mm²/mm)
- stirrup_angle_deg: angle α of stirrups with longitudinal tension reinforcement (degrees, default 90.0°, valid range 45.0° ≤ α ≤ 90.0°)
- vu_n: optional factored shear force demand Vu (N)
- vc_n: optional concrete shear resistance Vc (N)
- phi_shear: shear strength reduction factor φ from `BG-SHEAR-PHI-001` (default 0.75)

Units:

- d_effective_mm, s: mm
- Av: mm²
- Av/s, (Av/s)_req: mm²/mm
- fyt_mpa: MPa
- stirrup_angle_deg: degrees
- Vs, Vs,req, Vu, Vc: N

Exceptions / Blocked Conditions:

- Transverse reinforcement yield strength fyt > 420 MPa is rejected as `INVALID_INPUT` for standard non-seismic beam stirrups per Table 9-4-4.
- Stirrup angles α < 45° or α > 90° violate Clause 9-8-4-5-4 and return `INVALID_INPUT`.
- Bent-up longitudinal bars (Clause 9-8-4-5-4 ب/پ, Eqs. (9-8-18-الف) and (9-8-18-ب)) and circular-section hoops/spirals (Clause 9-8-4-5-6) return `UNVERIFIED_RULE_BLOCKED` when requested.

Verification Method:

Actual source page review (Mabhas 9, 1399 Edition, Chapters 9-4 and 9-8, Complete PDF Pages 89–90, 140, 142–144, Printed Pages 68–69, 119, 121–123, Table 9-4-4 and Clauses 9-4-8-5, 9-8-4-2-3, and 9-8-4-5-1 through 9-8-4-5-4).

---

## BG-SHEAR-VS-MAX-001 — Maximum One-Way Shear / Web-Crushing Limit (Vs,max and Vu,max)

Status: VERIFIED
Type: CODE_RULE
Source: Iranian National Building Regulations — Mabhas 9 (1399, 5th Edition)
PDF Page: 140 (Design Excerpt PDF Page: 28)
Printed Page: 119
Clause: 9-8-4-1-3, Eq. (9-8-9) (with Eq. (9-8-1-ب), Eq. (9-8-8), and Clause 9-8-4-2-2)

Formula / Requirement:

1. Cross-sectional dimension adequacy limit on factored one-way shear Vu (Clause 9-8-4-1-3, Eq. (9-8-9)):
   Vu ≤ φ × (Vc + 0.66 × sqrt(f'c)_eff × bw × d)   [Eq. (9-8-9)]

2. Resulting maximum nominal shear resistance of transverse reinforcement Vs,max (combining Eq. (9-8-9) with φVn = φ(Vc + Vs) ≥ Vu from Eqs. (9-8-1-ب) and (9-8-8)):
   Vs ≤ Vs,max = 0.66 × sqrt(f'c)_eff × bw × d
   Vu,max = φ × (Vc + Vs,max) = φ × (Vc + 0.66 × sqrt(f'c)_eff × bw × d)

Applicability:

Non-prestressed reinforced concrete beam sections checked for one-way shear under Mabhas 9 Clause 9-8-4-1-3.

Inputs:

- bw_mm: web width bw (mm)
- h_mm: total section depth h (mm)
- d_effective_mm: effective depth d (mm), resolved via Phase 1 effective-depth precedence
- fc_prime_mpa: specified concrete compressive strength f'c (MPa)
- vs_n: optional nominal shear force carried by transverse reinforcement Vs (N)
- vu_n: optional factored shear demand Vu (N)
- vc_n: optional nominal concrete shear resistance Vc (N)
- phi_shear: shear strength reduction factor φ from `BG-SHEAR-PHI-001` (default 0.75)

Units:

- bw_mm, h_mm, d_effective_mm: mm
- fc_prime_mpa: MPa
- vs_n, vs_max_n, vu_n, vc_n, vu_max_n: N

Exceptions / Blocked Conditions:

- Sections exceeding `Vs,max = 0.66 × sqrt(f'c)_eff × bw × d` or `Vu,max = φ × (Vc + 0.66 × sqrt(f'c)_eff × bw × d)` fail cross-sectional adequacy (`FAIL`).
- Combined shear and torsion web-crushing interaction (Clause 9-8-6-3-1, Eq. (9-8-26)) is out of scope and returns `UNVERIFIED_RULE_BLOCKED` (`BG-TORSION-PENDING`) if torsion `tu_nmm > 0` is present.

Verification Method:

Actual source page review (Mabhas 9, 1399 Edition, Chapter 9-8, Complete PDF Page 140, Printed Page 119, Clause 9-8-4-1-3, Eq. (9-8-9)).

---

## BG-SHEAR-MIN-001 — Minimum Shear Reinforcement

Status: VERIFIED
Type: CODE_RULE
Source: Iranian National Building Regulations — Mabhas 9
PDF Page: 221
Printed Page: 200
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
Printed Page: 206
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

Production Implementation (Phase 2D):

Executable in `beamgenius.engine.detailing_mabhas9.evaluate_minimum_transverse_bar_diameter`
(registry `execution_allowed=True`; dispatched by `run_mabhas9_beam_check`). The
non-bundled interval 32 mm < db < 36 mm deterministically returns
`UNVERIFIED_RULE_BLOCKED` (UNSUPPORTED_CONFIGURATION) — no interpolation invented.

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

Production Implementation (Phase 2D):

Executable in `beamgenius.engine.detailing_mabhas9.evaluate_compression_reinforcement_lateral_support_spacing`
(registry `execution_allowed=True`; dispatched by `run_mabhas9_beam_check`). Requires
`has_compression_reinforcement=True` plus positive finite db/dbt/sc inputs; b_min is
auto-resolved as min(bw, h). Compression bar buckling behavior beyond this spacing rule
is intentionally NOT implemented.

---

## BG-DETAIL-LONG-SPACING-001 — Longitudinal Bar Minimum Clear Spacing in a Horizontal Layer

Status: VERIFIED
Type: CODE_RULE
Source: Iranian National Building Regulations — Mabhas 9 (1399, 5th ed.)
PDF Page: 441
Printed Page: 420
Clause: 9-21-2-1-1 (same page: scope exceptions Clauses 9-21-2-1-3 and 9-21-2-1-4)

### SOURCE VERIFIED (visually verified 2026-10-03; ATNasr Mabhas 9 1399 PDF capture, page footer ۴۲۰)

Formula / Requirement:

The clear distance between parallel longitudinal bars placed in one horizontal layer shall not be less than EACH of (Clause 9-21-2-1-1 items الف/ب/پ):

- 25 mm
- db,max (diameter of the largest bar in the layer)
- (4/3) × d_agg = 1.33 × nominal maximum aggregate size

  s_clear ≥ max(25 mm, db,max, (4/3) × d_agg)

(The Persian text renders the aggregate factor as `1/33`, i.e. 1.33 in Persian decimal notation, consistent with item (ب) of Clause 9-21-2-1-3 rendered `1/5` = 1.5 on the same page.)

Applicability:

Parallel longitudinal bars in one horizontal layer of (non-shotcrete) members, e.g. beam tension/compression layers.

Limitations / Exceptions / Blocked Conditions:

- Clause 9-21-2-1-3 (columns, pedestal columns, ties, wall boundary elements: ≥ max(40 mm, 1.5 × db,max, (4/3) × d_agg)) is NOT a beam rule and is never substituted for beams.
- Clause 9-21-2-1-4: the spacing values do not apply to shotcrete — shotcrete input returns NOT_APPLICABLE.
- Bundled bars: the Clause 9-21-5-6 equivalent diameter is VERIFIED and implemented as `BG-DETAIL-BUNDLE-006` (Phase 2F Stage B), but integrating it into this spacing rule is a separate pending stage — bundled input returns BLOCKED (`UNVERIFIED_RULE_BLOCKED` / `UNVERIFIED_BUNDLE_RULE`); no equivalent diameter is invented here. Bundled cases never PASS.
- Missing db,max or d_agg returns BLOCKED (`UNVERIFIED_RULE_BLOCKED` / `MISSING_GOVERNING_BAR_DIAMETER` or `MISSING_AGGREGATE_SIZE`) — clause items are never dropped; malformed (non-finite / non-positive) values return INVALID_INPUT.

Required Inputs:

- db,max: largest bar diameter in the layer (mm) — REQUIRED, never defaulted
- d_agg: nominal maximum aggregate size (mm) — REQUIRED, never defaulted
- provided clear spacing between bars in the layer (mm) — optional; when omitted the required minimum is computed (COMPUTED)

Units: mm.

Verification Method:

Actual source-page capture review (Mabhas 9, 1399 5th ed., PDF Page 441, Printed Page 420, Clause 9-21-2-1-1 in full; visually verified 2026-10-03).

### EXECUTABLE IMPLEMENTATION (Phase 2E Stage B)

Executable as `beamgenius.engine.detailing_spacing_mabhas9.evaluate_longitudinal_bar_clear_spacing`
(registry `execution_allowed=True`; dispatched by `run_mabhas9_beam_check` and
`run_mabhas9_beam_detailing_workflow` when the mandatory aggregate input is supplied).
The legacy `BG-DETAIL-SPACING-BLOCKED` sentinel and blocked stub remain untouched.

---

## BG-DETAIL-LAYER-SPACING-001 — Multi-Layer Longitudinal Bar Vertical Clear Spacing and Alignment

Status: VERIFIED
Type: CODE_RULE
Source: Iranian National Building Regulations — Mabhas 9 (1399, 5th ed.)
PDF Page: 441
Printed Page: 420
Clause: 9-21-2-1-2

### SOURCE VERIFIED (visually verified 2026-10-03; ATNasr Mabhas 9 1399 PDF capture, page footer ۴۲۰)

Formula / Requirement:

For parallel longitudinal bars placed in SEVERAL horizontal layers:

1. The bars of each upper layer shall be placed directly above the bars of the layer below (vertical alignment), AND
2. The clear distance between two successive layers shall not be less than 25 mm (independent of bar diameter and aggregate size).

Applicability:

Multiple horizontal reinforcement layers of non-shotcrete members (e.g. beam layers).

Limitations / Exceptions / Blocked Conditions:

- Single layer (layer_count = 1): NOT_APPLICABLE (no inter-layer requirement).
- Bundled bars: the Clause 9-21-5-6 equivalent diameter is VERIFIED and implemented as `BG-DETAIL-BUNDLE-006` (Phase 2F Stage B); integration into this layer-spacing rule is a separate pending stage — bundled input returns BLOCKED (`UNVERIFIED_BUNDLE_RULE`).
- Missing layer geometry (layer count or alignment) returns BLOCKED (`MISSING_LAYER_COUNT` / `MISSING_LAYER_ALIGNMENT`) — never silently assumed; malformed values return INVALID_INPUT; misaligned layers FAIL (`LAYERS_NOT_DIRECTLY_ALIGNED`).

Required Inputs:

- layer_count: number of reinforcement layers (integer ≥ 1; may be derived from rebar-group layer indices) — REQUIRED, never assumed
- layers_directly_aligned: typed vertical-alignment confirmation for multi-layer arrangements — REQUIRED when layer_count ≥ 2, never silently assumed
- provided clear inter-layer spacing (mm) — optional; when omitted the 25 mm requirement is computed (COMPUTED)

Units: mm.

Verification Method:

Actual source-page capture review (Mabhas 9, 1399 5th ed., PDF Page 441, Printed Page 420, Clause 9-21-2-1-2 in full; visually verified 2026-10-03).

### EXECUTABLE IMPLEMENTATION (Phase 2E Stage B)

Executable as `beamgenius.engine.detailing_spacing_mabhas9.evaluate_longitudinal_layer_spacing`
(registry `execution_allowed=True`; dispatched by `run_mabhas9_beam_check` and
`run_mabhas9_beam_detailing_workflow` when the layer count is supplied). The legacy
`BG-DETAIL-LAYER-SPACING-BLOCKED` sentinel and blocked stub remain untouched.

---

## BG-DETAIL-COVER-001 — Minimum Concrete Cover over Reinforcement (Normal Environment)

Status: VERIFIED
Type: CODE_RULE
Source: Iranian National Building Regulations — Mabhas 9 (1399, 5th ed.)
PDF Page: 92–93
Printed Page: 71–72
Clause: 9-4-9-4, 9-4-9-5, 9-4-9-5-1, 9-4-9-5-2, 9-4-9-5-3 + Table 9-4-6 (corrosive routing: Clause 9-4-9-6; coatings: Clause 9-4-9-7)

### SOURCE VERIFIED (visually verified 2026-10-03; ATNasr Mabhas 9 1399 PDF captures, page footers ۷۱ and ۷۲)

Formula / Requirement:

The concrete cover over ALL longitudinal and transverse reinforcement shall not be less than the values of Table 9-4-6 (Clause 9-4-9-5-1), for normal (non-corrosive) environmental conditions (Clauses 9-4-9-4/9-4-9-5):

1. Concrete cast against and permanently in contact with earth (all members, all bars): 75 mm
2. Concrete exposed to air/weather or in non-permanent contact with earth (all members):
   - bars/wires db ≤ 16 mm: 40 mm
   - bars db 18–58 mm: 50 mm
3. Concrete NOT in contact with air or earth:
   - slabs, joists, walls: db > 36 mm → 40 mm; db ≤ 34 mm → 20 mm
   - beams, columns, pedestals, tension members: 40 mm (longitudinal bars, stirrups, ties, spirals, hoops)
4. Bundled bar groups (Clause 9-4-9-5-2): cover ≥ min(equivalent group diameter, 75 mm permanent-earth / 50 mm otherwise) — blocked, see below
5. Headed shear reinforcement (Clause 9-4-9-5-3): cover over head/plate ≥ member cover (same minimum as computed)

Applicability:

Normal environment (non-corrosive) cover checks by typed member class; the exposure condition, member type, and reinforcement type are REQUIRED typed inputs and are never assumed.

Limitations / Exceptions / Blocked Conditions:

- Corrosive or unusual environments (Clauses 9-4-9-6/9-4-9-7): governed by Appendix 9-پ1 durability requirements, NOT visually verified — returns BLOCKED (`CORROSIVE_EXPOSURE_BLOCKED_APPENDIX_9P1`); Appendix 9-پ1 values are never computed here.
- Bundled groups (Clause 9-4-9-5-2 → equivalent diameter Clause 9-21-5-6): the equivalent diameter is VERIFIED and implemented as `BG-DETAIL-BUNDLE-006` (Phase 2F Stage B); integration into this cover rule is a separate pending stage — returns BLOCKED (`UNVERIFIED_BUNDLE_RULE`).
- Diameter classes: only db ≤ 16 mm and db 18–58 mm (weather, all members) and db ≤ 34 mm / db > 36 mm (unexposed slabs-joints-walls) are verified; the uncovered intervals (16, 18) mm, db > 58 mm, and (34, 36] mm return BLOCKED (`UNVERIFIED_COVER_DIAMETER_CLASS`) — never interpolated.
- Missing exposure/member/reinforcement type (or missing governing diameter for the diameter-classed rows) returns BLOCKED (`MISSING_COVER_EXPOSURE_CLASS` / `MISSING_COVER_MEMBER_CLASS` / `MISSING_COVER_REINFORCEMENT_TYPE` / `MISSING_COVER_BAR_DIAMETER`) — never silently assumed; an unknown member type returns INVALID_INPUT (`UNKNOWN_COVER_MEMBER_CLASS`); malformed numeric values return INVALID_INPUT.

Required Inputs:

- exposure: ConcreteCoverExposureClass (NOT_EXPOSED / WEATHER_OR_EARTH_CONTACT / PERMANENT_EARTH_CONTACT / CORROSIVE_ENVIRONMENT) — REQUIRED
- member_class: ConcreteCoverMemberClass (BEAM / COLUMN / PEDESTAL / TENSION_MEMBER / SLAB / JOIST / WALL) — REQUIRED
- reinforcement_type: CoverReinforcementType (LONGITUDINAL / TRANSVERSE i.e. stirrups-ties-spirals-hoops) — REQUIRED
- cover_bar_diameter_mm: governing bar diameter (mm) — REQUIRED for the diameter-classed rows (weather exposure; unexposed slabs/joists/walls); may fall back to tension-group diameters
- provided cover (mm) — optional (falls back to geometry.clear_cover_mm); when omitted the required minimum is computed (COMPUTED)

Units: mm.

Verification Method:

Actual source-page capture review (Mabhas 9, 1399 5th ed., PDF Pages 92–93, Printed Pages 71–72: Clauses 9-4-9-3..9-4-9-7 and the complete Table 9-4-6; visually verified 2026-10-03).

### EXECUTABLE IMPLEMENTATION (Phase 2E Stage B)

Executable as `beamgenius.engine.detailing_spacing_mabhas9.evaluate_beam_cover`
(registry `execution_allowed=True`; dispatched by `run_mabhas9_beam_check` and
`run_mabhas9_beam_detailing_workflow` when a typed cover input is supplied). The
legacy `BG-DETAIL-COVER-BLOCKED` sentinel and blocked stub remain untouched.

---

## BG-DETAIL-BUNDLE-001 — Bundled Bars: Maximum Number of Bars per Bundle

Status: VERIFIED
Type: CODE_RULE
Source: Iranian National Building Regulations — Mabhas 9 (1399, 5th ed.)
PDF Page: 462
Printed Page: 441
Clause: 9-21-5-1

### SOURCE VERIFIED (visually verified 2026-10-03, re-confirmed 2026-10-05; ATNasr Mabhas 9 1399 PDF capture, page footer ۴۴۱)

Formula / Requirement:

«تعداد میلگردها در هر گروه میلگرد که به صورت یک واحد کار می‌کنند، به چهار محدود می‌شود.» — The number of bars in a bar bundle (group of bars acting as one unit) is limited to four: n_bundle ≤ 4.

Applicability:

Any bar bundle acting as one unit (longitudinal bars of structural members). A single bar is not a bundle (NOT_APPLICABLE in every bundle rule).

Limitations / Exceptions / Blocked Conditions:

- A bundle of more than four bars is a verifiable code violation → FAIL (`BUNDLE_BAR_COUNT_EXCEEDS_MAXIMUM`).
- A missing bundle bar count is never assumed → BLOCKED (`MISSING_BUNDLE_BAR_COUNT`); malformed counts (bool / non-integer / < 1) → INVALID_INPUT (`INVALID_BUNDLE_BAR_COUNT`).
- The satellite bundle rules 002..008 defer prohibited bundle sizes (n > 4) to this rule and return NOT_APPLICABLE for n > 4.

Required Inputs:

- bundle_n_bars: integer ≥ 1 — REQUIRED, never assumed

Units: dimensionless (bar count).

Verification Method:

Actual source-page capture review (Mabhas 9, 1399 5th ed., PDF p. 462 / Printed p. 441; section heading «9-21-5 گروه میلگردها» and clause «9-21-5-1» visible; visually verified 2026-10-03, re-confirmed 2026-10-05).

### EXECUTABLE IMPLEMENTATION (Phase 2F Stage B)

Executable as `beamgenius.engine.detailing_bundle_mabhas9.evaluate_bundle_bar_count` (registry `execution_allowed=True`; dispatched by `run_mabhas9_beam_check`; appended by `run_mabhas9_beam_detailing_workflow` when `bundle_n_bars` is supplied).

---

## BG-DETAIL-BUNDLE-002 — Bundled Bars: Transverse Enclosure & Compressed-Bundle Tie Diameter

Status: VERIFIED
Type: CODE_RULE
Source: Iranian National Building Regulations — Mabhas 9 (1399, 5th ed.)
PDF Page: 463
Printed Page: 442
Clause: 9-21-5-2

### SOURCE VERIFIED (visually verified 2026-10-03, re-confirmed 2026-10-05; ATNasr Mabhas 9 1399 PDF capture, page footer ۴۴۲)

Formula / Requirement:

«گروه میلگرد باید توسط آرماتور عرضی محاط شود. آرماتورهای عرضی گروه میلگردهای تحت فشار باید به قطر حداقل 12 میلی‌متر باشند.» — A bar bundle must be enclosed by transverse reinforcement; the transverse bars of bundles under compression must be at least 12 mm in diameter (dbt ≥ 12 mm).

Applicability:

Bar bundles, including compressed bundles (e.g., columns, compressed beam bars).

Limitations / Exceptions / Blocked Conditions:

- Missing enclosure / compression state is never assumed → BLOCKED (`MISSING_TRANSVERSE_ENCLOSURE` / `MISSING_COMPRESSION_STATE`); malformed flags → INVALID_INPUT.
- For compressed bundles the transverse bar diameter is REQUIRED — missing → BLOCKED (`MISSING_TRANSVERSE_BAR_DIAMETER`); malformed → INVALID_INPUT.
- Unenclosed bundle → FAIL (`BUNDLE_TRANSVERSE_ENCLOSURE_MISSING`); compressed bundle with dbt < 12 mm → FAIL (`BUNDLE_COMPRESSED_TRANSVERSE_DIAMETER_BELOW_MINIMUM`); the 12 mm boundary is inclusive (dbt = 12 mm passes).
- The unresolved transverse-spacing detailing clauses of 9-21-6 remain outside this rule (no dependency is invented).

Required Inputs:

- bundle_n_bars — REQUIRED
- bundle_has_transverse_enclosure: bool — REQUIRED, never assumed
- bundle_is_compressed: bool — REQUIRED, never assumed
- transverse_bar_diameter_mm — REQUIRED when bundle_is_compressed; otherwise optional

Units: mm (diameter check); dimensionless flags.

Verification Method:

Actual source-page capture review (Mabhas 9, 1399 5th ed., PDF p. 463 / Printed p. 442; clause «9-21-5-2» visible; visually verified 2026-10-03, re-confirmed 2026-10-05).

### EXECUTABLE IMPLEMENTATION (Phase 2F Stage B)

Executable as `beamgenius.engine.detailing_bundle_mabhas9.evaluate_bundle_transverse_reinforcement` (registry `execution_allowed=True`; orchestrated with the bundle chain).

---

## BG-DETAIL-BUNDLE-003 — Bundled Bars: Beam Bundle Bar Diameter Prohibition

Status: VERIFIED
Type: CODE_RULE
Source: Iranian National Building Regulations — Mabhas 9 (1399, 5th ed.)
PDF Page: 463
Printed Page: 442
Clause: 9-21-5-3

### SOURCE VERIFIED (visually verified 2026-10-03, re-confirmed 2026-10-05; ATNasr Mabhas 9 1399 PDF capture, page footer ۴۴۲)

Formula / Requirement:

«در تیرها استفاده از میلگردهای با قطر بیش از 34 میلی‌متر به صورت گروه میلگرد مجاز نیست.» — In beams, bars with diameter larger than 34 mm are not permitted in bundles (beam-specific clause).

Applicability:

Beams only. Non-beam member classes → NOT_APPLICABLE.

Limitations / Exceptions / Blocked Conditions:

- Missing member class or governing diameter is never assumed → BLOCKED (`MISSING_MEMBER_CLASS` / `MISSING_GOVERNING_BAR_DIAMETER`); an unknown member class → INVALID_INPUT (`UNKNOWN_MEMBER_CLASS`); malformed diameter → INVALID_INPUT.
- A bundled beam bar with db > 34 mm → FAIL (`BUNDLE_BEAM_BAR_DIAMETER_EXCEEDS_MAXIMUM`); the 34 mm boundary is inclusive (db = 34 mm passes).

Required Inputs:

- bundle_n_bars — REQUIRED
- member_class (ConcreteCoverMemberClass) — REQUIRED, never assumed
- bundle_bar_diameter_mm — REQUIRED for beams, never assumed

Units: mm.

Verification Method:

Actual source-page capture review (Mabhas 9, 1399 5th ed., PDF p. 463 / Printed p. 442; clause «9-21-5-3» visible; visually verified 2026-10-03, re-confirmed 2026-10-05).

### EXECUTABLE IMPLEMENTATION (Phase 2F Stage B)

Executable as `beamgenius.engine.detailing_bundle_mabhas9.evaluate_bundle_beam_bar_diameter` (registry `execution_allowed=True`; orchestrated with the bundle chain).

---

## BG-DETAIL-BUNDLE-004 — Bundled Bars: Cutoff Point Staggering in Flexural Members

Status: VERIFIED
Type: CODE_RULE
Source: Iranian National Building Regulations — Mabhas 9 (1399, 5th ed.)
PDF Page: 463
Printed Page: 442
Clause: 9-21-5-4

### SOURCE VERIFIED (visually verified 2026-10-03, re-confirmed 2026-10-05; ATNasr Mabhas 9 1399 PDF capture, page footer ۴۴۲)

Formula / Requirement:

Along the span of flexural members, the cutoff point of each bar of a bundle must be at least 40 bar diameters from the cutoff points of the other bars of the bundle: min |xi − xj| ≥ 40·db (more than one bar of the bundle may not be cut at one point).

Applicability:

Flexural members with bundled bars being curtailed along the span.

Limitations / Exceptions / Blocked Conditions:

- The cutoff configuration is a REQUIRED typed input — missing → BLOCKED (`MISSING_CUTOFF_CONFIGURATION`); malformed → INVALID_INPUT. When no bundle bar is cut → NOT_APPLICABLE.
- With cutoffs: missing diameter → BLOCKED (`MISSING_GOVERNING_BAR_DIAMETER`); missing cutoff positions → BLOCKED (`MISSING_BUNDLE_CUTOFF_POSITIONS`); malformed values (including non-finite positions) → INVALID_INPUT.
- Fewer than two cut bars → NOT_APPLICABLE (no pair to stagger).
- Any pair of cutoff points closer than 40·db → FAIL (`BUNDLE_CUTOFF_STAGGER_BELOW_MINIMUM`); exactly 40·db passes.

Required Inputs:

- bundle_n_bars — REQUIRED
- bundle_has_cutoffs: bool — REQUIRED, never assumed
- bundle_bar_diameter_mm — REQUIRED when cutoffs exist
- bundle_cutoff_positions_mm: sequence of axial positions (mm) — REQUIRED when cutoffs exist

Units: mm.

Verification Method:

Actual source-page capture review (Mabhas 9, 1399 5th ed., PDF p. 463 / Printed p. 442; clause «9-21-5-4» visible; visually verified 2026-10-03, re-confirmed 2026-10-05).

### EXECUTABLE IMPLEMENTATION (Phase 2F Stage B)

Executable as `beamgenius.engine.detailing_bundle_mabhas9.evaluate_bundle_cutoff_stagger` (registry `execution_allowed=True`; orchestrated with the bundle chain).

---

## BG-DETAIL-BUNDLE-005 — Bundled Bars: Bar Plane Arrangement Limit

Status: VERIFIED
Type: CODE_RULE
Source: Iranian National Building Regulations — Mabhas 9 (1399, 5th ed.)
PDF Page: 463
Printed Page: 442
Clause: 9-21-5-5

### SOURCE VERIFIED (visually verified 2026-10-03, re-confirmed 2026-10-05; ATNasr Mabhas 9 1399 PDF capture, page footer ۴۴۲)

Formula / Requirement:

In bundles with more than two bars, not all bar axes may lie in one plane, and at most two bars may lie in one plane — except at splice locations.

Applicability:

Bar bundles with more than two bars (bundles of one or two bars → NOT_APPLICABLE); splice locations are exempted.

Limitations / Exceptions / Blocked Conditions:

- The plane arrangement and splice-location status are REQUIRED typed inputs — missing → BLOCKED (`MISSING_BUNDLE_PLANE_ARRANGEMENT` / `MISSING_SPLICE_LOCATION_STATUS`); malformed values (including a plane count above the bundle size) → INVALID_INPUT.
- More than two bars in one plane at a non-splice location → FAIL (`BUNDLE_BARS_PER_PLANE_EXCEEDED`); at a splice location the clause exception applies → PASS (noted in the trace message).

Required Inputs:

- bundle_n_bars — REQUIRED
- bundle_max_bars_in_single_plane: integer ≥ 1 — REQUIRED, never assumed
- bundle_is_splice_location: bool — REQUIRED, never assumed

Units: dimensionless.

Verification Method:

Actual source-page capture review (Mabhas 9, 1399 5th ed., PDF p. 463 / Printed p. 442; clause «9-21-5-5» visible; visually verified 2026-10-03, re-confirmed 2026-10-05).

### EXECUTABLE IMPLEMENTATION (Phase 2F Stage B)

Executable as `beamgenius.engine.detailing_bundle_mabhas9.evaluate_bundle_plane_arrangement` (registry `execution_allowed=True`; orchestrated with the bundle chain).

---

## BG-DETAIL-BUNDLE-006 — Bundled Bars: Equivalent Bar Diameter

Status: VERIFIED
Type: CODE_RULE
Source: Iranian National Building Regulations — Mabhas 9 (1399, 5th ed.)
PDF Page: 463
Printed Page: 442
Clause: 9-21-5-6

### SOURCE VERIFIED (visually verified 2026-10-03, re-confirmed 2026-10-05; ATNasr Mabhas 9 1399 PDF capture, page footer ۴۴۲)

Formula / Requirement:

For checks whose calculation is based on bar diameter — spacing limits, minimum cover, the confinement coefficient of Clause 9-21-3-2-1 and the coating factor of Clause 9-21-3-2-2 — a bundle is treated as one equivalent bar of equal total area whose centroid coincides with the bundle centroid. For n identical bars:

    d_eq = db · √n

(with equal-area identity n·π·db²/4 = π·d_eq²/4 enforced in the trace).

Applicability:

Identical-bar bundles for spacing-limit, minimum-cover, confinement-coefficient and coating-factor calculations (the clause scope). Development length is NOT derived from d_eq — Clause 9-21-5-7 provides its own multipliers (see `BG-DETAIL-BUNDLE-007`).

Limitations / Exceptions / Blocked Conditions:

- Only the identical-bar closed form is implemented. Mixed-diameter bundles return BLOCKED (`UNSUPPORTED_CONFIGURATION`) — the equal-area/coincident-centroid construction exists in the source but no verified closed-form diameter is applied here; BLOCKED never becomes PASS.
- Missing identical-flag or diameter → BLOCKED (`MISSING_BUNDLE_BARS_IDENTICAL` / `MISSING_GOVERNING_BAR_DIAMETER`); malformed values → INVALID_INPUT.
- Integrating d_eq into the Phase 2E spacing/cover rules (`BG-DETAIL-LONG-SPACING-001`, `BG-DETAIL-LAYER-SPACING-001`, `BG-DETAIL-COVER-001`) is a separate pending stage; those rules keep returning `UNVERIFIED_BUNDLE_RULE` for bundled inputs until that integration is implemented.

Required Inputs:

- bundle_n_bars — REQUIRED
- bundle_bar_diameter_mm — REQUIRED, never assumed
- bundle_bars_identical: bool — REQUIRED, never assumed

Units: mm (equivalent diameter).

Verification Method:

Actual source-page capture review (Mabhas 9, 1399 5th ed., PDF p. 463 / Printed p. 442; clause «9-21-5-6» visible, including spacing/cover/9-21-3-2-1/9-21-3-2-2 references; visually verified 2026-10-03, re-confirmed 2026-10-05).

### EXECUTABLE IMPLEMENTATION (Phase 2F Stage B)

Executable as `beamgenius.engine.detailing_bundle_mabhas9.evaluate_bundle_equivalent_diameter` (registry `execution_allowed=True`; outcome COMPUTED with the equal-area check recorded in trace intermediates).

---

## BG-DETAIL-BUNDLE-007 — Bundled Bars: Development Length Multiplier

Status: VERIFIED
Type: CODE_RULE
Source: Iranian National Building Regulations — Mabhas 9 (1399, 5th ed.)
PDF Page: 463
Printed Page: 442
Clause: 9-21-5-7

### SOURCE VERIFIED (visually verified 2026-10-03, re-confirmed 2026-10-05; ATNasr Mabhas 9 1399 PDF capture, page footer ۴۴۲)

Formula / Requirement:

The development length of bars in a bundle, in tension or compression, equals the single-bar development length for a 2-bar bundle, and is 20% and 33% greater for 3-bar and 4-bar bundles respectively:

    ld_bundle = factor · ld_single,  factor = 1.00 (2-bar) / 1.20 (3-bar) / 1.33 (4-bar)

Applicability:

Bar bundles in tension or compression — development-length scaling only.

Limitations / Exceptions / Blocked Conditions:

- This rule applies ONLY the verified bundle multipliers. The underlying single-bar development length of Clause 9-21-3 is NOT computed here (unverified dependency, `BG-DEV-LENGTH-PENDING`): a missing verified single-bar ld deterministically returns BLOCKED (`MISSING_SINGLE_BAR_DEVELOPMENT_LENGTH`) — the value is never invented; malformed ld → INVALID_INPUT.

Required Inputs:

- bundle_n_bars — REQUIRED
- single_bar_development_length_mm (verified ld of a single bar) — REQUIRED, never computed here

Units: mm.

Verification Method:

Actual source-page capture review (Mabhas 9, 1399 5th ed., PDF p. 463 / Printed p. 442; clause «9-21-5-7» visible; visually verified 2026-10-03, re-confirmed 2026-10-05).

### EXECUTABLE IMPLEMENTATION (Phase 2F Stage B)

Executable as `beamgenius.engine.detailing_bundle_mabhas9.evaluate_bundle_development_length` (registry `execution_allowed=True`; multiplier table exported as `BG_DETAIL_BUNDLE_007_LD_MULTIPLIERS = {2: 1.00, 3: 1.20, 4: 1.33}`).

---

## BG-DETAIL-BUNDLE-008 — Bundled Bars: Lap Splice Constraints & Multiplier

Status: VERIFIED
Type: CODE_RULE
Source: Iranian National Building Regulations — Mabhas 9 (1399, 5th ed.)
PDF Page: 463
Printed Page: 442
Clause: 9-21-5-8

### SOURCE VERIFIED (visually verified 2026-10-03, re-confirmed 2026-10-05; ATNasr Mabhas 9 1399 PDF capture, page footer ۴۴۲; clause text continuing onto the following page)

Formula / Requirement:

1. The lap splice length of each bar in a bundle is computed from the single-bar development length including the Clause 9-21-5-7 bundle increase (lap = ld_single · factor, factor = 1.00 / 1.20 / 1.33 for 2/3/4-bar bundles).
2. The laps of individual bars of a bundle must not overlap along the bars.
3. A lap splice of a whole bundle with another bundle is prohibited.

Applicability:

Bar bundles being lap-spliced (bundle-specific splice constraints).

Limitations / Exceptions / Blocked Conditions:

- Only these verified bundle-specific constraints are implemented. The underlying lap rules of Clause 9-21-4 and the single-bar ld of Clause 9-21-3 are NOT computed here (unverified dependencies): a missing verified single-bar ld deterministically returns BLOCKED (`MISSING_SINGLE_BAR_DEVELOPMENT_LENGTH`) — never an invented value; malformed ld → INVALID_INPUT.
- Missing lap type / overlap status → BLOCKED (`MISSING_BUNDLE_LAP_TYPE` / `MISSING_BUNDLE_LAP_OVERLAP_STATUS`); malformed flags → INVALID_INPUT.
- Bundle-to-bundle lap → FAIL (`BUNDLE_TO_BUNDLE_LAP_SPLICE_PROHIBITED`); overlapping individual laps → FAIL (`BUNDLE_INDIVIDUAL_LAPS_OVERLAP_PROHIBITED`); otherwise the per-bar lap length is COMPUTED.

Required Inputs:

- bundle_n_bars — REQUIRED
- single_bar_development_length_mm (verified ld of a single bar) — REQUIRED, never computed here
- bundle_is_bundle_to_bundle_lap: bool — REQUIRED, never assumed
- bundle_laps_overlap: bool — REQUIRED, never assumed

Units: mm (lap length).

Verification Method:

Actual source-page capture review (Mabhas 9, 1399 5th ed., PDF p. 463 / Printed p. 442; clause «9-21-5-8» visible with its continuation; visually verified 2026-10-03, re-confirmed 2026-10-05).

### EXECUTABLE IMPLEMENTATION (Phase 2F Stage B)

Executable as `beamgenius.engine.detailing_bundle_mabhas9.evaluate_bundle_lap_splice` (registry `execution_allowed=True`; uses the same verified multiplier table as `BG-DETAIL-BUNDLE-007`).


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

---

## BG-DEV-LENGTH-TENSION-001 — Development Length of Deformed Bars in Tension (General Relation, Clause 9-21-3-2-1 / Eq. 9-21-1)

Status: VERIFIED
Type: CODE_RULE
Source: Iranian National Building Regulations — Mabhas 9 (1399, 5th ed.)
PDF Page: 445 (clause spans PDF pp. 445-447; floors/reduction PDF pp. 446, 455-456)
Printed Page: 425 (clause spans Printed pp. 425-427; reduction Printed pp. 435-436)
Clause: 9-21-3-1-3..6, 9-21-3-2-1, Eq. (9-21-1), Eq. (9-21-2), Table 9-21-3, 9-21-3-9

### SOURCE VERIFIED (visually verified 2026-10-05; evidence scan `phase2f-source-442-472` @ commit df8067a; PDF page-445/446/447/455/456 JPGs; canonical offset PDF = printed + 20)

Formula / Requirement:

l_d = [ψ_t·ψ_e·ψ_s·ψ_g / (λ·((c_b + K_tr)/d_b))] · (0.9·f_y/√f′c) · d_b per Eq. (9-21-1), with c_b = min(distance from bar center to nearest concrete surface, half center-to-center bar spacing), K_tr = 40·A_tr/(s·n) per Eq. (9-21-2) (K_tr = 0 is permitted even when transverse reinforcement is present), confinement index (c_b+K_tr)/d_b capped at 2.5, minimum l_d = 300 mm (9-21-3-2-1-ب). No φ is applied (9-21-3-1-4); √f′c clamped at 8.3 MPa (9-21-3-1-5); λ = 1.0 (normal-weight) / 0.75 (lightweight) (9-21-3-1-6). Table 9-21-3 (9-21-3-2-2): ψ_g = 1.0 (S340/S350/S400/S420) / 1.15 (S500/S520); ψ_e = 1.5 (epoxy/dual-coated with cover < 3·d_b or clear spacing < 6·d_b) / 1.2 (other epoxy/dual-coated) / 1.0 (uncoated or galvanized); ψ_s = 0.8 (d_b < 20 mm) / 1.0; ψ_t = 1.3 (≥ 300 mm fresh concrete cast below) / 1.0; ψ_t·ψ_e ≤ 1.7. Excess-reinforcement reduction (9-21-3-9): permitted for this equation case by the ratio required/provided only when no 9-21-3-9-2 context applies; the 300 mm floor is preserved after reduction.

Applicability:

Tension development of single deformed bars or wires. Hooks, heads, mechanical anchorage, welded-wire mesh and compression have their own Stage C rules.

Limitations / Exceptions / Blocked Conditions:

- Reduction is deterministically BLOCKED in any 9-21-3-9-2 context (`PROHIBITED_EXCESS_REDUCTION_CONTEXT`): non-continuous supports, yield-development-required locations, continuity-required bars, intermediate/high-ductility seismic systems, anchored headed/hooked/mechanical bars, pile-head anchorage.
- A reduction ratio as_required > as_provided is INVALID_INPUT (not a reduction).
- Every required input missing → BLOCKED; malformed → INVALID_INPUT. BLOCKED never becomes PASS.

Required Inputs:

- steel_grade (SteelGradeClass), bar_diameter_mm, yield_stress_mpa, concrete_strength_mpa, concrete_weight_class (ConcreteWeightClass), coating_class (BarCoatingClass), top_bar_placement, concrete_cover_mm, clear_spacing_mm, apply_k_tr (with transverse_area_mm2, transverse_spacing_mm, developed_bar_count when True) — all REQUIRED typed inputs, never assumed. Reduction inputs required only when apply_excess_reinforcement_reduction is True.

Units: mm.

Verification Method:

Visual source-page verification of the committed evidence scan (git show df8067a:phase2f-source-442-472/page-445..447.jpg + page-455/456.jpg for 9-21-3-9), 2026-10-05; recorded in docs/PHASE2_SOURCE_VERIFICATION_MATRIX.md §4B/§4C.

### EXECUTABLE IMPLEMENTATION (Phase 2F Stage C)

Executable as `beamgenius.engine.development_length_mabhas9.evaluate_dev_length_tension` (registry `execution_allowed=True`).

---

## BG-DEV-LENGTH-TENSION-TABLE-001 — Simplified Development Length of Deformed Bars in Tension (Table 9-21-4, Clause 9-21-3-2-3)

Status: VERIFIED
Type: CODE_RULE
Source: Iranian National Building Regulations — Mabhas 9 (1399, 5th ed.)
PDF Page: 448
Printed Page: 428
Clause: 9-21-3-2-3, Table 9-21-4 (factors Table 9-21-3 Printed p. 427 / PDF p. 447; floor 9-21-3-2-1-ب Printed p. 426 / PDF p. 446)

### SOURCE VERIFIED (visually verified 2026-10-05; page-447/448 JPGs @ df8067a)

Formula / Requirement:

l_d = (ψ_t·ψ_e·ψ_g)·f_y/(D·λ·√f′c)·d_b with divisor D = 2.1 (confined row, d_b < 20) / 1.7 (confined, d_b ≥ 20) / 1.4 (other, d_b < 20) / 1.1 (other, d_b ≥ 20); confined row requires (clear spacing or splice ≥ d_b AND minimum code ties provided along l_d) OR (clear spacing or splice ≥ 2·d_b AND cover ≥ d_b). The 300 mm minimum of 9-21-3-2-1-ب governs in all cases. Factor verification and clamps identical to BG-DEV-LENGTH-TENSION-001; ψ_t·ψ_e ≤ 1.7. Reduction per 9-21-3-9 with the floor preserved.

Applicability:

Alternative simplified path for tension development length of deformed bars/wires, exactly as printed in Table 9-21-4; nothing is interpolated beyond the two printed rows × two diameter classes.

Limitations / Exceptions / Blocked Conditions:

- Same reduction prohibitions/gates as BG-DEV-LENGTH-TENSION-001.
- The row-selection inputs (clear spacing, cover, ties flag) are REQUIRED — the confined row is never assumed.

Required Inputs:

- As BG-DEV-LENGTH-TENSION-001 minus K_tr, plus min_code_ties_provided_along_ld (REQUIRED).

Units: mm.

Verification Method:

Visual source-page verification (page-448 JPG, Table 9-21-4 cells read at full resolution), 2026-10-05.

### EXECUTABLE IMPLEMENTATION (Phase 2F Stage C)

Executable as `beamgenius.engine.development_length_mabhas9.evaluate_dev_length_tension_table`.

---

## BG-DEV-LENGTH-HOOKED-001 — Development Length of Deformed Bars with Standard Hooks in Tension (Eq. 9-21-3, Clause 9-21-3-3)

Status: VERIFIED
Type: CODE_RULE
Source: Iranian National Building Regulations — Mabhas 9 (1399, 5th ed.)
PDF Page: 448 (table PDF p. 450; definitions PDF p. 449)
Printed Page: 428 (table Printed p. 430; definitions Printed p. 429)
Clause: 9-21-3-3-1/-2/-3/-4, Eq. (9-21-3), Table 9-21-5

### SOURCE VERIFIED (visually verified 2026-10-05; page-448/449/450 JPGs @ df8067a)

Formula / Requirement:

l_dh = [ψ_e·ψ_r·ψ_o·ψ_c / λ] · (0.043·f_y/√f′c) · d_b^1.5 per Eq. (9-21-3); minimum max(8·d_b, 150 mm) (3-3-1-ب). Table 9-21-5: ψ_e = 1.2 (epoxy/dual-coated) / 1.0 (uncoated, galvanized); ψ_r = 1.0 (d_b ≤ 34 mm AND A_th ≥ 0.40·A_hs AND anchored-bar spacing > 6·d_b), else 1.6; ψ_o = 1.0 (d_b ≤ 34 mm AND anchored in column core AND side cover normal to hook plane > 65 mm or > 6·d_b), else 1.25; ψ_c = f′c/105 + 0.6 (f′c < 42 MPa) / 1.0 (f′c ≥ 42). A_th per 9-21-3-3-3 (≥ 0.75·l_dh from hook bend; tie placement zones of 3-3-3-الف/ب and 3-3-4 are placement requirements recorded for traceability).

Applicability:

Tension anchorage with standard hooks. Hooks are never permitted to develop bars in compression (9-21-3-1-3).

Limitations / Exceptions / Blocked Conditions:

- Excess-reinforcement reduction is NOT permitted for hooked anchorage (9-21-3-9-2-ث) — not offered by the evaluator.
- The tie-placement geometry of 9-21-3-3-3/-4 is not computed by this length evaluator (documented dependency, not silently dropped).

Required Inputs:

- bar_diameter_mm, yield_stress_mpa, concrete_strength_mpa, concrete_weight_class, coating_class, a_th_mm2, a_hs_mm2, anchored_bar_clear_spacing_mm, anchored_in_column_core, side_cover_normal_to_hook_plane_mm — all REQUIRED, never assumed.

Units: mm.

Verification Method:

Visual source-page verification (page-448/449/450 JPGs; Table 9-21-5 factor cells), 2026-10-05.

### EXECUTABLE IMPLEMENTATION (Phase 2F Stage C)

Executable as `beamgenius.engine.development_length_mabhas9.evaluate_dev_length_hooked`.

---

## BG-DEV-LENGTH-HEADED-001 — Development Length of Headed Deformed Bars in Tension (Eq. 9-21-4, Clause 9-21-3-4)

Status: VERIFIED
Type: CODE_RULE
Source: Iranian National Building Regulations — Mabhas 9 (1399, 5th ed.)
PDF Page: 450 (equation PDF p. 451; table PDF p. 452)
Printed Page: 430 (equation Printed p. 431; table Printed p. 432)
Clause: 9-21-3-4-1/-2/-3/-4/-5, Eq. (9-21-4), Table 9-21-6

### SOURCE VERIFIED (visually verified 2026-10-05; page-450/451/452 JPGs @ df8067a)

Formula / Requirement:

l_dt = [ψ_e·ψ_c·ψ_p·ψ_o / λ] · (0.032·f_y/√f′c) · d_b^1.5 per Eq. (9-21-4); minimum max(8·d_b, 150 mm). Applicability limits (9-21-3-4-1): d_b ≤ 34 mm; head bearing section A_brg ≥ 4·A_b; normal-weight concrete only; cover ≥ 2·d_b; center-to-center spacing ≥ 3·d_b — each a verifiable FAIL when violated. Table 9-21-6: ψ_e = 1.2 / 1.0 (coating); ψ_p = 1.0 (d_b ≤ 34 AND (beam-column joint with A_tt ≥ 0.3·A_ts, A_tt per 9-21-3-4-4 within 8·d_b, OR connection with anchored-bar spacing > 6·d_b)), else 1.6; ψ_o = 1.0 / 1.25 (column-core side-cover condition as Table 9-21-5); ψ_c as Table 9-21-5.

Applicability:

Tension anchorage with headed bars meeting every 9-21-3-4-1 limit. Heads never develop bars in compression (9-21-3-1-3).

Limitations / Exceptions / Blocked Conditions:

- Reduction NOT permitted (9-21-3-9-2-ث) — not offered.
- A_tt/A_ts inputs are REQUIRED when connection_class = BEAM_COLUMN_JOINT (missing → BLOCKED); for ANY_OTHER connections the joint-area branch is not evaluated.

Required Inputs:

- bar_diameter_mm, yield_stress_mpa, concrete_strength_mpa, concrete_weight_class, coating_class, head_bearing_area_mm2, concrete_cover_mm, bar_spacing_cc_mm, anchored_in_column_core, side_cover_normal_to_head_plane_mm, connection_class, a_tt_mm2/a_ts_mm2 (beam-column joints), anchored_bar_clear_spacing_mm — all REQUIRED, never assumed.

Units: mm.

Verification Method:

Visual source-page verification (page-450/451/452 JPGs; Table 9-21-6 factor cells), 2026-10-05.

### EXECUTABLE IMPLEMENTATION (Phase 2F Stage C)

Executable as `beamgenius.engine.development_length_mabhas9.evaluate_dev_length_headed`.

---

## BG-DEV-MECH-ANCHOR-001 — Mechanical Anchorage of Deformed Bars in Tension (Clause 9-21-3-5)

Status: VERIFIED
Type: CODE_RULE
Source: Iranian National Building Regulations — Mabhas 9 (1399, 5th ed.)
PDF Page: 453
Printed Page: 433
Clause: 9-21-3-5-1

### SOURCE VERIFIED (visually verified 2026-10-05; page-453 JPG @ df8067a)

Formula / Requirement:

No length equation is given by the clause (and none is invented): any welded attachment or mechanical device capable of developing the bar yield f_y is permitted only with the design engineer's approval, and combined anchorage (mechanical anchor + development length between the critical section and the device) is permitted on the basis of approved test results. The evaluator enforces exactly this three-part gate.

Applicability:

Tension mechanical anchorage of deformed bars.

Limitations / Exceptions / Blocked Conditions:

- Any missing condition → BLOCKED; any false condition → FAIL (device supplies f_y, engineer approval, approved test results). Reduction is not applicable to mechanical anchorage (9-21-3-9-2-ث).

Required Inputs:

- device_supplies_yield_capacity, designer_engineer_approved, approved_test_results_present — all REQUIRED booleans, never assumed.

Units: dimensionless gate (unit "1").

Verification Method:

Visual source-page verification (page-453 JPG, clause 9-21-3-5-1 read at full resolution), 2026-10-05.

### EXECUTABLE IMPLEMENTATION (Phase 2F Stage C)

Executable as `beamgenius.engine.development_length_mabhas9.evaluate_dev_mech_anchorage`.

---

## BG-DEV-WIRE-DEFORMED-001 — Development Length of Welded Deformed-Wire Mesh in Tension (Eq. 9-21-5, Clause 9-21-3-6)

Status: VERIFIED
Type: CODE_RULE
Source: Iranian National Building Regulations — Mabhas 9 (1399, 5th ed.)
PDF Page: 453 (ψ_w equations PDF p. 454)
Printed Page: 433 (ψ_w equations Printed p. 434)
Clause: 9-21-3-6-1/-2/-3/-4, Eq. (9-21-5), Eqs. (9-21-6-الف/ب)

### SOURCE VERIFIED (visually verified 2026-10-05; page-453/454 JPGs @ df8067a)

Formula / Requirement:

l_d = [ψ_t·ψ_e·ψ_s·ψ_w / (λ·((c_b+K_tr)/d_b))] · (0.90·f_y/√f′c) · d_b per Eq. (9-21-5); floor 200 mm (3-6-1-ب). ψ_t/ψ_e/ψ_s per 9-21-3-2-2 (ψ_t·ψ_e ≤ 1.7); for epoxy-coated welded-wire mesh ψ_e may be taken 1.0 (3-6-1 explicit permission — typed option). c_b and K_tr per 9-21-3-2-1 (index ≤ 2.5). ψ_w per Eqs. (9-21-6-الف/ب): with a cross wire within l_d at ≥ 50 mm from the critical section, ψ_w = max(min((f_y−240)/f_y, 1.0), min(5·d_b/s, 1.0)); otherwise ψ_w = 1.0. Reduction permitted (9-21-3-9) with the 200 mm floor preserved.

Applicability:

Tension development of welded DEFORMED-wire mesh with d_b ≤ 16 mm, uncoated or epoxy-coated.

Limitations / Exceptions / Blocked Conditions:

- Plain wire (any diameter), deformed wire d_b > 16 mm, and galvanized mesh are routed to 9-21-3-7 (3-6-3/-4) → NOT_APPLICABLE (`BG-DEV-WIRE-PLAIN-001` governs).
- Supplying a cross-wire distance while declaring no cross wire is INVALID (INCONSISTENT_CROSS_WIRE_INPUTS).

Required Inputs:

- bar_diameter_mm, yield_stress_mpa, concrete_strength_mpa, concrete_weight_class, wire_surface_class (WireSurfaceClass), wire_is_deformed, epoxy_psi_e_unit_permission (epoxy only), top_bar_placement, concrete_cover_mm, clear_spacing_mm, cross_wire_in_development (with cross_wire_distance_from_critical_mm and anchored_wire_spacing_mm when True), apply_k_tr (+ transverse inputs when True) — all REQUIRED, never assumed.

Units: mm.

Verification Method:

Visual source-page verification (page-453/454 JPGs; Eqs. (9-21-6-الف/ب) read at full resolution), 2026-10-05.

### EXECUTABLE IMPLEMENTATION (Phase 2F Stage C)

Executable as `beamgenius.engine.development_length_mabhas9.evaluate_dev_wire_deformed`.

---

## BG-DEV-WIRE-PLAIN-001 — Development Length of Welded Plain-Wire Mesh in Tension (Eq. 9-21-7, Clause 9-21-3-7)

Status: VERIFIED
Type: CODE_RULE
Source: Iranian National Building Regulations — Mabhas 9 (1399, 5th ed.)
PDF Page: 454 (floors/mins PDF p. 455)
Printed Page: 434 (floors/mins Printed p. 435)
Clause: 9-21-3-7-1, Eq. (9-21-7)

### SOURCE VERIFIED (visually verified 2026-10-05; page-454/455 JPGs @ df8067a)

Formula / Requirement:

l_dt = (3.3·f_y / (λ·√f′c)) · (A_b/s) per Eq. (9-21-7), measured from the critical section to the OUTERMOST cross wire (s = spacing of the anchored wires; A_b = wire cross-section); minimum: the greater of 150 mm and s + 50 mm (3-7-1-ب); at least two cross wires must exist within l_dt in all cases — fewer is a verifiable FAIL. Reduction permitted (9-21-3-9) with both floors preserved.

Applicability:

Tension development of welded PLAIN-wire mesh; also governs deformed wires > 16 mm and galvanized mesh (9-21-3-6-3/-4 routing).

Limitations / Exceptions / Blocked Conditions:

- Fewer than two cross wires → FAIL (PLAIN_WIRE_FEWER_THAN_TWO_CROSS_WIRES).
- No ψ factors apply to this equation (none printed); none invented.

Required Inputs:

- bar_diameter_mm, anchored_wire_spacing_mm, yield_stress_mpa, concrete_strength_mpa, concrete_weight_class, cross_wires_in_development_length — all REQUIRED, never assumed.

Units: mm.

Verification Method:

Visual source-page verification (page-454/455 JPGs; Eq. (9-21-7) and floors), 2026-10-05.

### EXECUTABLE IMPLEMENTATION (Phase 2F Stage C)

Executable as `beamgenius.engine.development_length_mabhas9.evaluate_dev_wire_plain`.

---

## BG-DEV-LENGTH-COMPRESSION-001 — Development Length of Deformed Bars and Wires in Compression (Clause 9-21-3-8)

Status: VERIFIED
Type: CODE_RULE
Source: Iranian National Building Regulations — Mabhas 9 (1399, 5th ed.)
PDF Page: 455
Printed Page: 435
Clause: 9-21-3-8-1

### SOURCE VERIFIED (visually verified 2026-10-05; page-455 JPG @ df8067a)

Formula / Requirement:

l_dc = max{ (ψ_r·0.24·f_y/(λ·√f′c))·d_b , 0.043·f_y·ψ_r·d_b }, minimum 200 mm. ψ_r = 0.75 for confinement by a spiral, a continuous circular tie (diameter > 6 mm at spacing < 100 mm), a wire tie (diameter > 12 mm at spacing < 100 mm) [VERIFY_PENDING branch — see limitation], or a دوریگر/دورگیر per Clause 9-21-6-4 at spacing < 100 mm; ψ_r = 1.0 otherwise. Reduction permitted (9-21-3-9) with the 200 mm floor preserved.

Applicability:

Compression development of single deformed bars or wires. Hooks/heads never develop bars in compression (9-21-3-1-3).

Limitations / Exceptions / Blocked Conditions:

- The «تنگ سیمی» (wire tie > 12 mm @ < 100 mm) ψ_r branch keeps its recorded noun ambiguity (source-verification matrix §4B †1: the printed noun requires re-confirmation) — the branch is deterministically BLOCKED (`VERIFY_PENDING_CONFINEMENT_TIE_CLASS`) and never executed.
- Circular-tie/dورگیر classes require their diameter/spacing inputs; qualifications fully below the printed thresholds yield ψ_r = 1.0 (never assumed).

Required Inputs:

- bar_diameter_mm, yield_stress_mpa, concrete_strength_mpa, concrete_weight_class, confinement_tie_class (CompressionConfinementClass; +confinement_tie_diameter_mm for CIRCULAR_TIE, +confinement_tie_spacing_mm for CIRCULAR_TIE/DORGIR_9_21_6_4) — all REQUIRED, never assumed.

Units: mm.

Verification Method:

Visual source-page verification (page-455 JPG; ψ_r class list read at high zoom), 2026-10-05.

### EXECUTABLE IMPLEMENTATION (Phase 2F Stage C)

Executable as `beamgenius.engine.development_length_mabhas9.evaluate_dev_length_compression`.

---

# Lap & Bearing Splices (Phase 2F Stage E — Clause 9-21-4)

Promotion gate: only VERIFIED + CODE_RULE + MABHAS_9_COMPLIANCE + execution_allowed=True rules below were promoted. Every §9-21-4 value was visually re-verified 2026-10-06 from `phase2f-source-442-472` @ `df8067a` (footer-confirmed Printed pp. 436–441 / PDF pp. 456–461). Lap lengths consume the Stage C verified Clause 9-21-3 development length `l_d`/`l_dc` as a caller-provided value (never computed here; missing → BLOCKED). No NBC Chapter 9-4 / Chapter 10 / Mostofinejad dependency is imported or invented.

## BG-DEV-LAP-APPLIC-001 — Bar-Splice Methods and Lap Diameter Applicability (Clause 9-21-4-1-1 / 9-21-4-1-2)

Status: VERIFIED | Type: CODE_RULE | Source: Mabhas 9 (1399, 5th ed.) | PDF 456 | Printed 436

Formula / Requirement: splices permitted by one of four methods (lap / bearing / welded / mechanical) per 9-21-4-1-1; a lap splice is permitted in tension and compression for d_b ≤ 34 mm (9-21-4-1-2-الف); in compression a lap of a bar ≤ 42 mm to a bar ≤ 34 mm is permitted (length per 9-21-4-5-2) per 9-21-4-1-2-ب.

Applicability: all bar splices; the diameter limit is lap-specific (bearing/welded/mechanical → permitted method, specifics deferred to their own clauses).
Required Inputs: splice_method (SpliceMethod), bar_stress_action (BarStressAction), bar_diameter_mm, larger_bar_diameter_mm (optional, compression different-diameter case). Missing → BLOCKED; malformed → INVALID_INPUT; d_b > 34 mm in tension (or outside compression limits) → FAIL.
Units: mm. Executable as `beamgenius.engine.development_lap_splice_mabhas9.evaluate_lap_splice_applicability`.

## BG-DEV-LAP-SPACING-001 — Contact-Lap Transverse Centre-to-Centre Spacing (Clause 9-21-4-1-4)

Status: VERIFIED | Type: CODE_RULE | Source: Mabhas 9 (1399, 5th ed.) | PDF 457 | Printed 437

Formula / Requirement: for a contact lap splice in flexural members, the transverse centre-to-centre spacing of the spliced bars shall not exceed one fifth of the lap length and 150 mm: s ≤ min(lap/5, 150 mm).
Applicability: contact lap splices in flexural members. Required Inputs: lap_length_mm, transverse_center_to_center_spacing_mm. Missing → BLOCKED; malformed → INVALID_INPUT; above limit → FAIL.
Units: mm. Executable as `beamgenius.engine.development_lap_splice_mabhas9.evaluate_lap_splice_spacing`.

## BG-DEV-LAP-TENSION-001 — Tension Lap Splice Length (Clause 9-21-4-2-1)

Status: VERIFIED | Type: CODE_RULE | Source: Mabhas 9 (1399, 5th ed.) | PDF 457 | Printed 437

Formula / Requirement: l_st = 1.3·l_d (type B) general; l_st = 1.0·l_d (type A) only if provided ≥ 2× required AND ≤ ½ of provided is spliced within the lap length; l_st ≥ 300 mm; l_d per 9-21-4-2-1-1 (Clause 9-21-3-1).
Applicability: tension lap splices of bars with d_b ≤ 34 mm (9-21-4-1-2). The excess-reinforcement l_d reduction of 9-21-3-9 is NOT applied (9-21-4-1-5). Required Inputs: development_length_mm (verified l_d; missing → BLOCKED, never invented), tension_lap_class (TensionLapClass); as_provided_over_required_ratio and fraction_of_provided_bars_spliced required for type A (missing → BLOCKED). Type A with unmet conditions → FAIL.
Units: mm. Executable as `beamgenius.engine.development_lap_splice_mabhas9.evaluate_lap_splice_tension`.

## BG-DEV-LAP-TENSION-DIFFDIA-001 — Different-Diameter Tension Lap Splice Length (Clause 9-21-4-2)

Status: VERIFIED | Type: CODE_RULE | Source: Mabhas 9 (1399, 5th ed.) | PDF 458 | Printed 438

Formula / Requirement: l_s ≥ max(l_d for the larger bar, l_st for the smaller bar).
Applicability: tension lap splices of different-diameter bars (d_b ≤ 34 mm per 9-21-4-1-2, checked by BG-DEV-LAP-APPLIC-001). Both governing lengths are caller-provided verified values (missing → BLOCKED).
Required Inputs: development_length_larger_bar_mm, tension_lap_length_smaller_bar_mm.
Units: mm. Executable as `beamgenius.engine.development_lap_splice_mabhas9.evaluate_lap_splice_tension_diffdia`.

## BG-DEV-LAP-COMPRESSION-001 — Compression Lap Splice Length (Clause 9-21-4-5-1)

Status: VERIFIED | Type: CODE_RULE | Source: Mabhas 9 (1399, 5th ed.) | PDF 459 | Printed 439

Formula / Requirement: for d_b ≤ 34 mm — l_sc = 0.071·f_y·d_b (f_y ≤ 420 MPa); l_sc = (0.13·f_y − 24)·d_b (f_y > 420 MPa); l_sc ≥ 300 mm.
Applicability: compression lap splices of bars with d_b ≤ 34 mm; d_b > 34 mm → NOT_APPLICABLE (use BG-DEV-LAP-COMPRESSION-DIFFDIA-001 for the smaller bar).
Required Inputs: bar_diameter_mm, yield_stress_mpa. Missing → BLOCKED; malformed → INVALID_INPUT.
Units: mm. Executable as `beamgenius.engine.development_lap_splice_mabhas9.evaluate_lap_splice_compression`.

## BG-DEV-LAP-COMPRESSION-DIFFDIA-001 — Different-Diameter Compression Lap Splice Length (Clause 9-21-4-5-2)

Status: VERIFIED | Type: CODE_RULE | Source: Mabhas 9 (1399, 5th ed.) | PDF 460 | Printed 440

Formula / Requirement: l_s ≥ max(l_dc for the larger bar per 9-21-3-8, l_sc for the smaller bar per 9-21-4-5-1).
Applicability: compression lap splices of different-diameter bars. Both governing lengths are caller-provided verified values (missing → BLOCKED).
Required Inputs: compression_dev_length_larger_bar_mm, compression_lap_length_smaller_bar_mm.
Units: mm. Executable as `beamgenius.engine.development_lap_splice_mabhas9.evaluate_lap_splice_compression_diffdia`.

## BG-DEV-SPLICE-BEARING-001 — Bearing Splice of Compression-Only Bars (Clause 9-21-4-6)

Status: VERIFIED | Type: CODE_RULE | Source: Mabhas 9 (1399, 5th ed.) | PDF 460 | Printed 440

Formula / Requirement: bearing transfer permitted only for bars under compression alone, ends cut perpendicular to the bar axis, the two spliced bars coaxial (e.g. via a ring) (9-21-4-6-1); only in members with confinement (خاموت: tied / spiral / دورگیر) (9-21-4-6-2); end-face deviation ≤ 5° and axial misalignment ≤ 3° (9-21-4-6-3 — the 5° value refines an earlier 1.5° reading).
Applicability: bearing splices of compression-only bars; geometry/applicability check only (no force transfer). Required Inputs: bars_compression_only, ends_cut_perpendicular, bars_coaxial, member_has_confinement, end_face_deviation_deg, axial_misalignment_deg. Missing → BLOCKED; malformed → INVALID_INPUT; any unmet condition → FAIL.
Units: deg. Executable as `beamgenius.engine.development_lap_splice_mabhas9.evaluate_splice_bearing`.

### BLOCKED (not promoted) — §9-21-4-3 / §9-21-4-4 / §9-21-4-7

- `BG-DEV-LAP-WIRE-DEFORMED-PENDING` (9-21-4-3, PDF 458 / Printed 438): welded deformed-wire mesh lap. BLOCKED — §9-4-8 itself is now visually verified (Stage H.14); the residual dependency is conformity to INSO 11558 via §9-4-8-7 (Stage H.15, unresolved), and it branches to 9-21-4-4.
- `BG-DEV-LAP-WIRE-PLAIN-PENDING` (9-21-4-4, PDF 459 / Printed 439): welded plain-wire mesh lap. BLOCKED — the 9-21-4-4-1-ب «و یا» disjunct («…۵۰ میلی‌متر، و یا ۱۵۰ میلی‌متر») is unresolved (VERIFY_PENDING; recorded verbatim, never interpreted/executed) plus the Chapter 9-4 dependency.
- `BG-DEV-SPLICE-WELDED-MECH-PENDING` (9-21-4-7, PDF 460–461 / Printed 440–441): welded/mechanical splices. BLOCKED — 9-21-4-7-3 requires NBC Chapter 10 welding compliance (out of window, VERIFY_PENDING) and the mechanical-splice strength coefficient glyph was not independently re-confirmed.

All three are registered with `execution_allowed=False`, `status=VERIFY_PENDING`, and a `blocked_reason`; the Gatekeeper returns `UNVERIFIED_RULE_BLOCKED` for any attempted execution.

# Transverse Reinforcement / Confinement (Phase 2F Stage G — Clause 9-21-6)

Promotion gate: only VERIFIED + CODE_RULE + MABHAS_9_COMPLIANCE + execution_allowed=True rules below were promoted. Every §9-21-6 value was visually re-verified 2026-10-06 from `phase2f-source-442-472` @ `df8067a` (footer-confirmed Printed pp. 443–450 / PDF pp. 463–470; PDF = printed + 20). OCR `.txt` was navigation-only; tight digits were confirmed from enlarged `.jpg` crops. Only fully-verified clauses without unresolved dependency were promoted; every ambiguity/dependency stays BLOCKED. No NBC Chapter 9-4 / Chapter 10 / Mostofinejad dependency is imported or invented. This engine module does not import the reference package and reads no source file at runtime. Executable module: `beamgenius.engine.transverse_reinforcement_mabhas9`.

## BG-TRANS-TIE-SHEAR-EXTENT-001 — Confining Tie Extent When Used as Shear Reinforcement (Clause 9-21-6-1-1)

Status: VERIFIED | Type: CODE_RULE | Source: Mabhas 9 (1399, 5th ed.) | PDF 463 | Printed 443

Formula / Requirement: where a tie is used as shear reinforcement it must extend to the effective depth d measured from the compression face (extent ≥ d). Corrects the earlier Stage F note of "50% of d" — the printed clause is the full effective depth d.
Applicability: confining ties used as shear reinforcement; a tie not used as shear reinforcement → NOT_APPLICABLE for this extent check.
Required Inputs: used_as_shear_reinforcement (bool; missing → BLOCKED), tie_extent_from_compression_face_mm, effective_depth_mm (missing → BLOCKED; malformed → INVALID_INPUT). extent < d → FAIL.
Units: mm. Executable as `beamgenius.engine.transverse_reinforcement_mabhas9.evaluate_tie_shear_extent`.

## BG-TRANS-CLOSED-TIE-LAP-001 — Closed-Tie Two-Piece U-Leg Lap (Clause 9-21-6-1-8)

Status: VERIFIED | Type: CODE_RULE | Source: Mabhas 9 (1399, 5th ed.) | PDF 466 | Printed 446

Formula / Requirement: a closed tie may be built from two U-ties; the U-tie leg lap ≥ anchorage_length/3. In members with total depth ≥ 450 mm and force per leg (f_y × tie area) < 40 kN, a leg lap continuing across the full member depth is sufficient (governing requirement = min(anchorage/3, total depth) under the exception).
Applicability: two-piece closed ties (not torsion/integrity ties). Required Inputs: anchorage_length_mm (caller-provided verified value; missing → BLOCKED), total_depth_mm, force_per_leg_n, provided_leg_lap_mm (missing → BLOCKED; malformed → INVALID_INPUT). Insufficient lap → FAIL.
Units: mm / N. Executable as `beamgenius.engine.transverse_reinforcement_mabhas9.evaluate_closed_tie_lap`.

## BG-TRANS-TIE-SPACING-001 — Tie Spacing Limits (Clause 9-21-6-2-1)

Status: VERIFIED | Type: CODE_RULE | Source: Mabhas 9 (1399, 5th ed.) | PDF 466 | Printed 446

Formula / Requirement: (الف) clear spacing ≥ d_agg/3; (ب) centre-to-centre tie spacing ≤ min(16 × longitudinal bar d_b, 48 × transverse (tie) bar d_b, smallest member dimension). (OCR misread 16×/48× as 6×/8×; visual is authoritative.)
Applicability: closed deformed-bar tie spacing. Required Inputs: provided_clear_spacing_mm, provided_center_to_center_spacing_mm, aggregate_size_mm, longitudinal_bar_diameter_mm, transverse_bar_diameter_mm, smallest_member_dimension_mm (missing → BLOCKED; malformed → INVALID_INPUT). Either limit violated → FAIL.
Units: mm. Executable as `beamgenius.engine.transverse_reinforcement_mabhas9.evaluate_tie_spacing`.

## BG-TRANS-TIE-DIA-001 — Minimum Tie Diameter (Clause 9-21-6-2-2)

Status: VERIFIED | Type: CODE_RULE | Source: Mabhas 9 (1399, 5th ed.) | PDF 466 | Printed 446

Formula / Requirement: (الف) tie diameter ≥ 10 mm for longitudinal bars up to 32 mm; (ب) ≥ 12 mm for longitudinal bars 34 mm and larger, or longitudinal bar bundles. A non-bundled longitudinal bar with 32 < d_b < 34 mm (e.g. 33 mm) is in neither verified branch → deterministically BLOCKED (never interpolated).
Applicability: closed deformed-bar tie diameter. Required Inputs: longitudinal_bar_diameter_mm, is_bundled (bool), provided_tie_diameter_mm (missing → BLOCKED; malformed → INVALID_INPUT). Diameter below the branch minimum → FAIL; the 33 mm gap → BLOCKED.
Units: mm. Executable as `beamgenius.engine.transverse_reinforcement_mabhas9.evaluate_tie_diameter`.

## BG-TRANS-RECT-TIE-001 — Rectangular-Tie Unrestrained Longitudinal Bar Spacing (Clause 9-21-6-2-4-ب)

Status: VERIFIED | Type: CODE_RULE | Source: Mabhas 9 (1399, 5th ed.) | PDF 467 | Printed 447

Formula / Requirement: a longitudinal bar without lateral (tie-bend) restraint must not have clear spacing greater than 150 mm from a restrained longitudinal bar. (The other sub-parts of 9-21-6-2-4 — الف 135° bend restraint, پ standard-hook anchorage, ت headed-bar prohibition — are positional/hook requirements verified by inspection and are NOT computed here.)
Applicability: rectangular-tie longitudinal-bar restraint spacing. Required Inputs: unrestrained_bar_clear_spacing_mm (missing → BLOCKED; malformed → INVALID_INPUT). Above 150 mm → FAIL.
Units: mm. Executable as `beamgenius.engine.transverse_reinforcement_mabhas9.evaluate_rect_tie_unrestrained_spacing`.

## BG-TRANS-CIRC-TIE-001 — Circular-Tie End Overlap (Clause 9-21-6-2-5-الف)

Status: VERIFIED | Type: CODE_RULE | Source: Mabhas 9 (1399, 5th ed.) | PDF 467 | Printed 447

Formula / Requirement: where longitudinal bars have a circular arrangement, at each circular-tie end the bars must overlap by at least 150 mm. (The other sub-parts of 9-21-6-2-5 — ب standard-hook ends, پ non-coincident successive overlaps — are positional/hook requirements verified by inspection and are NOT computed here.)
Applicability: circular ties. Required Inputs: tie_end_overlap_mm (missing → BLOCKED; malformed → INVALID_INPUT). Below 150 mm → FAIL.
Units: mm. Executable as `beamgenius.engine.transverse_reinforcement_mabhas9.evaluate_circular_tie_overlap`.

## BG-TRANS-SPIRAL-SPACING-001 — Spiral Clear Spacing and Pitch Limits (Clause 9-21-6-3-1)

Status: VERIFIED | Type: CODE_RULE | Source: Mabhas 9 (1399, 5th ed.) | PDF 468 | Printed 448

Formula / Requirement: (الف) clear spacing ≥ max(d_agg/3, 25 mm); (ب) pitch ≤ 75 mm.
Applicability: spiral transverse reinforcement. Required Inputs: provided_clear_spacing_mm, provided_pitch_mm, aggregate_size_mm (missing → BLOCKED; malformed → INVALID_INPUT). Either limit violated → FAIL.
Units: mm. Executable as `beamgenius.engine.transverse_reinforcement_mabhas9.evaluate_spiral_spacing`.

## BG-TRANS-SPIRAL-DIA-001 — Minimum Spiral Diameter, Cast-in-Place (Clause 9-21-6-3-2)

Status: VERIFIED | Type: CODE_RULE | Source: Mabhas 9 (1399, 5th ed.) | PDF 468 | Printed 448

Formula / Requirement: spiral wire/bar diameter for cast-in-place concrete ≥ 10 mm.
Applicability: cast-in-place spirals. Required Inputs: provided_spiral_diameter_mm (missing → BLOCKED; malformed → INVALID_INPUT). Below 10 mm → FAIL.
Units: mm. Executable as `beamgenius.engine.transverse_reinforcement_mabhas9.evaluate_spiral_diameter`.

## BG-TRANS-SPIRAL-RATIO-001 — Spiral Volumetric Reinforcement Ratio, Eq. (9-21-8) (Clause 9-21-6-3-3)

Status: VERIFIED | Type: CODE_RULE | Source: Mabhas 9 (1399, 5th ed.) | PDF 468 | Printed 448

Formula / Requirement: ρ_s ≥ 0.45·(A_g/A_ch − 1)·f′c/f_yτ [Eq. (9-21-8)], with the spiral yield stress f_yτ not taken greater than 700 MPa.
Applicability: transverse reinforcement in deep foundations. Required Inputs: gross_area_mm2 (A_g), core_area_mm2 (A_ch), concrete_strength_mpa (f′c), spiral_yield_stress_mpa (f_yτ), provided_rho_s (missing → BLOCKED; malformed → INVALID_INPUT). f_yτ > 700 MPa → FAIL (not permitted for this equation); ρ_s below required → FAIL.
Units: ratio (dimensionless) / MPa / mm². Executable as `beamgenius.engine.transverse_reinforcement_mabhas9.evaluate_spiral_ratio`.

## BG-TRANS-SPIRAL-ANCHOR-001 — Spiral End Anchorage, Extra Turns (Clause 9-21-6-3-4)

Status: VERIFIED | Type: CODE_RULE | Source: Mabhas 9 (1399, 5th ed.) | PDF 468 | Printed 448

Formula / Requirement: spiral anchorage at each end is provided by 1½ extra turns of the spiral (extra turns ≥ 1.5 at each end).
Applicability: spiral end anchorage. Required Inputs: extra_turns_each_end (missing → BLOCKED; malformed → INVALID_INPUT). Below 1.5 → FAIL.
Units: turns. Executable as `beamgenius.engine.transverse_reinforcement_mabhas9.evaluate_spiral_anchor_turns`.

## BG-TRANS-SPIRAL-LAP-001 — Spiral Lap Splice Length, Table 9-21-7 (Clause 9-21-6-3-6)

Status: VERIFIED | Type: CODE_RULE | Source: Mabhas 9 (1399, 5th ed.) | PDF 469 | Printed 449

Formula / Requirement: lap = max(k·d_b, 300 mm), k = 48 or 72 per Table 9-21-7 (verified verbatim): deformed bar — uncoated/galvanized no hook → 48, epoxy/dual no hook → 72, epoxy/dual with standard transverse hook → 48; deformed wire — uncoated no hook → 48, epoxy no hook → 72, epoxy with hook → 48; plain bar — uncoated/galvanized no hook → 72, with hook → 48; plain wire — uncoated no hook → 72, with hook → 48. Any (type, coating, end-condition) combination not printed in Table 9-21-7 → deterministically BLOCKED (no interpretation about coating/hook).
Applicability: spiral lap splices. Required Inputs: splice_bar_type (SpiralSpliceBarType), coating_class (SpiralSpliceCoating), end_condition (SpiralSpliceEndCondition), bar_diameter_mm (missing → BLOCKED; malformed → INVALID_INPUT; unlisted combination → BLOCKED).
Units: mm. Executable as `beamgenius.engine.transverse_reinforcement_mabhas9.evaluate_spiral_lap_splice`.

## BG-TRANS-SEISMIC-HOOK-001 — Seismic Hook Geometry (Clause 9-21-2-2-4)

Status: VERIFIED | Type: CODE_RULE | Source: Mabhas 9 (1399, 5th ed.) | PDF 442 | Printed 442

Formula / Requirement: a seismic hook (قلاب لرزه‌ای) has a bend of at least 135° and a straight extension after the bend of at least 6·d_b **or** 75 mm; in circular دورگیر (دورگیرهای دایروی) the bend may be at least 90°. The geometry is stated inline in 9-21-2-2-4; the terminological phrase «مطابق تعریف فصل ۹-۲۰» is NOT a dependency on Chapter 9-20 and Chapter 9-20 is never imported.
Applicability: seismic-hook geometry anchor for the Clause 9-21-6-4 دورگیر and Clause 9-21-6-2-7-الف seismic-hook rules. Required Inputs: circular_dorgir (bool; selects the 90° vs 135° bend minimum), bend_angle_deg, straight_extension_mm, bar_diameter_mm (missing → BLOCKED; malformed / bend > 180° / non-bool circular → INVALID_INPUT). Dependencies: none.
Units: deg / mm. Executable as `beamgenius.engine.transverse_reinforcement_mabhas9.evaluate_seismic_hook`.

## BG-TRANS-DORGIR-001 — Confinement Tie دورگیر, Closed / Continuous / Multi-Part (Clauses 9-21-6-4-1, 9-21-6-4-2 & 9-21-6-4-3)

Status: VERIFIED | Type: CODE_RULE | Source: Mabhas 9 (1399, 5th ed.) | PDF 470 | Printed 450

Formula / Requirement: Clause 9-21-6-4-1 — دورگیر shall consist of closed ties or be wound continuously. Clause 9-21-6-4-2 — دورگیر may be made of several parts, each anchored at both ends by a seismic hook per Clause 9-21-2-2-4; Clause 9-21-6-4-3 — each part shall engage one longitudinal bar and interconnected headed bars are not permitted; each hook encloses one longitudinal bar; interconnected headed bars (میلگردهای سَر دار متصل به هم) are not permitted as دورگیر. The component hook geometry is delegated to BG-TRANS-SEISMIC-HOOK-001 (not duplicated); no geometry beyond these clauses is invented.
Applicability: دورگیر confinement ties. Required Inputs: dorgir_construction (DorgirConstruction), uses_interconnected_headed_bars (bool); for MULTI_PART also hook_bend_angle_deg, hook_straight_extension_mm, hook_bar_diameter_mm, hook_circular_dorgir, hook_encloses_longitudinal_bar (missing → BLOCKED; malformed / wrong type → INVALID_INPUT; headed bars → FAIL; bad delegated hook → FAIL). Dependencies: `BG-TRANS-SEISMIC-HOOK-001`.
Units: mm. Executable as `beamgenius.engine.transverse_reinforcement_mabhas9.evaluate_dorgir`.

## BG-TRANS-TWO-PIECE-TIE-001 — Two-Piece Torsion / Integrity Tie (Clause 9-21-6-1-7)

Status: VERIFIED | Type: CODE_RULE | Source: Mabhas 9 (1399, 5th ed.) | PDF 465 | Printed 445

Formula / Requirement: a tie for torsion/cracking may be made of two parts — a U-shaped tie with 135° bends, and a member (سنگراقی) whose 90° bend shall be adjacent to the member face where the concrete is not susceptible to deterioration from flange/slab confinement. Only these requirements are represented; no bend diameter, embedment length, or other geometry is invented.
Applicability: two-piece torsion/integrity ties. Required Inputs: u_tie_bend_angle_deg (≥ 135°), second_member_bend_angle_deg (= 90°), second_member_adjacent_nonspalling_face (bool) (missing → BLOCKED; malformed / wrong type → INVALID_INPUT). Dependencies: none.
Units: deg. Executable as `beamgenius.engine.transverse_reinforcement_mabhas9.evaluate_two_piece_tie`.

## BG-TRANS-TORSION-TIE-135HOOK-001 — Torsion / Integrity Tie 135° Hook, Clause 9-21-6-1-6-الف

Status: VERIFIED | Type: CODE_RULE | Source: Mabhas 9 (1399, 5th ed.) | PDF 464 | Printed 444

Formula / Requirement: both ends of the tie shall be terminated with a 135° hook around the longitudinal bar. Only the deterministic (الف) branch is implemented. Scope of this rule is unchanged by Stage H.7: the (ب) branch is still NOT executed here. (Stage H.7 M2 correction: the earlier text claimed the (ب) branch delegates to the still-blocked Clauses 9-21-6-1-3 **and** 9-21-6-1-4. Clause 9-21-6-1-4 is no longer blocked — it was promoted to the executable `BG-TRANS-TORSION-TIE-WIRE-ROUTE-001` — while Clause 9-21-6-1-3 remains blocked. This rule still implements only its already-implemented 135° torsion-hook branch and does NOT execute either (ب) route.)
Applicability: torsion/integrity tie 135°-hook anchorage. Required Inputs: hook_bend_angle_deg (≥ 135°), hook_engages_longitudinal_bar (bool) (missing → BLOCKED; malformed / wrong type / bend > 180° → INVALID_INPUT). Dependencies: none.
Units: deg. Executable as `beamgenius.engine.transverse_reinforcement_mabhas9.evaluate_torsion_tie_135hook`.

## BG-TRANS-TORSION-TIE-SEISMIC-HOOK-001 — Torsion Tie Seismic-Hook Branch, Clause 9-21-6-2-7-الف

Status: VERIFIED | Type: CODE_RULE | Source: Mabhas 9 (1399, 5th ed.) | PDF 467 | Printed 447

Formula / Requirement: both ends of a torsion tie shall be terminated with a seismic hook around the longitudinal bar, with the bend end anchored in the core concrete. Only the seismic-hook option of 9-21-6-2-7-الف is implemented here; the standard 135° hook option is implemented separately as BG-TRANS-TORSION-TIE-STANDARD-HOOK-001 (Stage H.5) and the (ب) branch routes through the still-blocked Clause 9-21-6-1-3 — neither is executed here. The seismic-hook geometry is delegated to BG-TRANS-SEISMIC-HOOK-001.
Applicability: torsion-tie seismic-hook anchorage. Required Inputs: hook_engages_longitudinal_bar (bool), bend_end_anchored_in_core_concrete (bool), and the seismic-hook geometry inputs (hook_bend_angle_deg, hook_straight_extension_mm, hook_bar_diameter_mm, hook_circular_dorgir) (missing → BLOCKED; malformed / wrong type → INVALID_INPUT). Dependencies: `BG-TRANS-SEISMIC-HOOK-001`.
Units: mm. Executable as `beamgenius.engine.transverse_reinforcement_mabhas9.evaluate_torsion_tie_seismic_hook`.

## BG-TRANS-STANDARD-HOOK-001 — Standard Transverse-Bar Hook Geometry (Clause 9-21-2-2-2 & Table 9-21-2)

Status: VERIFIED | Type: CODE_RULE | Source: Mabhas 9 (1399, 5th ed.) | PDF 442–443 | Printed 442–443

Formula / Requirement: Clause 9-21-2-2-2 — standard hooks for transverse bars shall comply with Table 9-21-2 and the hook shall enclose a longitudinal bar. Table 9-21-2 (verified verbatim, PDF 443): for BOTH the 90° and 135° standard hooks, d_b 10–16 mm → minimum inner bend diameter 4·d_b and straight extension max(6·d_b, 75 mm); d_b 18–25 mm → minimum inner bend diameter 6·d_b and straight extension 12·d_b. Implemented for the 90° and 135° hooks only. The 180° hook (also printed in Table 9-21-2 with the same geometry) is a distinct configuration not exercised by any §9-21-6 rule in this stage and is deterministically BLOCKED (deferred, trivially promotable later). Unsupported diameter ranges are BLOCKED and never interpolated: d_b < 10 mm and d_b > 25 mm are outside the table; d_b = 17 mm falls in the gap between the printed 10–16 mm and 18–25 mm rows.
Applicability: standard transverse-bar hook geometry (§9-21-2-2-2 / Table 9-21-2). Required Inputs: hook_angle_deg (90 or 135), bar_diameter_mm, inner_bend_diameter_mm, straight_extension_mm, encloses_longitudinal_bar (bool) (missing → BLOCKED; malformed / non-bool enclosure → INVALID_INPUT; unsupported angle/diameter → BLOCKED; non-enclosing / under-size bend / under-size extension → FAIL). Dependencies: none.
Units: mm. Executable as `beamgenius.engine.transverse_reinforcement_mabhas9.evaluate_standard_hook`.

## BG-TRANS-TORSION-TIE-STANDARD-HOOK-001 — Torsion Tie Standard 135° Hook Branch, Clause 9-21-6-2-7-الف

Status: VERIFIED | Type: CODE_RULE | Source: Mabhas 9 (1399, 5th ed.) | PDF 467 | Printed 447

Formula / Requirement: both ends of a torsion tie shall be terminated with a standard 135° hook OR a seismic hook around the longitudinal bar, with the bend end anchored in the core concrete. Only the standard 135° hook option is implemented here; the seismic-hook option is implemented by BG-TRANS-TORSION-TIE-SEISMIC-HOOK-001 (not duplicated). The standard-hook geometry is delegated to BG-TRANS-STANDARD-HOOK-001 (Clause 9-21-2-2-2 / Table 9-21-2, not re-implemented). The (ب) branch of Clause 9-21-6-2-7 is NOT included (it remains blocked under `BG-TRANS-TORSION-TIE-PENDING`).
Applicability: torsion-tie standard 135°-hook anchorage. Required Inputs: hook_bar_diameter_mm, hook_inner_bend_diameter_mm, hook_straight_extension_mm, hook_engages_longitudinal_bar (bool), bend_end_anchored_in_core_concrete (bool) (missing → BLOCKED; malformed / wrong type → INVALID_INPUT; not engaging / not core-anchored / bad delegated geometry → FAIL). Dependencies: `BG-TRANS-STANDARD-HOOK-001`.
Units: mm. Executable as `beamgenius.engine.transverse_reinforcement_mabhas9.evaluate_torsion_tie_standard_hook`.

## BG-TRANS-WIRE-TIE-UTIE-001 — Welded-Wire U-Tie Leg Anchorage, Clause 9-21-6-1-4

Status: VERIFIED | Type: CODE_RULE | Source: Mabhas 9 (1399, 5th ed.) | PDF 464 | Printed 444 (Figure 9-21-1, PDF 465)

Formula / Requirement: the anchorage of one leg of a welded-wire-mesh U-stirrup shall satisfy one of the following. (الف) two longitudinal wires at 50 mm spacing in the upper part of the U-stirrup. (ب) one longitudinal wire less than one-quarter of the effective depth from the compression face, and a second longitudinal wire closer to the compression face than the first and more than 50 mm from the first, where the second wire may be on the stirrup leg or on a hook with a minimum bend diameter of eight times the stirrup wire diameter. Only these numeric conditions are represented; no geometry is inferred from Figure 9-21-1 and no spacing/anchorage/bend requirement is invented. The caller selects which alternative (الف/ب) is relied upon. Clause 9-21-6-1-5 remains blocked (separate).
Applicability: welded-wire U-tie leg anchorage. Required Inputs: alternative (WireTieUtieAlternative); for الف wire_spacing_mm (= 50 mm) and wires_in_upper_part_of_utie (bool); for ب effective_depth_mm, wire1_dist_from_compression_mm, wire2_dist_from_compression_mm, wire1_to_wire2_spacing_mm, wire2_on_hook (bool) and (if on hook) bend_diameter_mm, tie_wire_diameter_mm (missing → BLOCKED; malformed / wrong type → INVALID_INPUT; spacing ≠ 50 mm / not in upper part / ≥ ¼·d / not closer / ≤ 50 mm / bend < 8× wire dia → FAIL). Dependencies: none.
Units: mm. Executable as `beamgenius.engine.transverse_reinforcement_mabhas9.evaluate_wire_tie_utie`.

## BG-TRANS-SPIRAL-SPLICE-LAP-SEL-001 — Spiral Lap-Splice Method Selection, Clause 9-21-6-3-5-ب

Status: VERIFIED | Type: CODE_RULE | Source: Mabhas 9 (1399, 5th ed.) | PDF 468–469 | Printed 448–449

Formula / Requirement: a spiral lap splice per Clause 9-21-6-3-6 is permitted for bars with yield stress f_y ≤ 420 MPa. This rule selects/validates the lap-splice route and delegates the actual lap length to BG-TRANS-SPIRAL-LAP-001 (max(k·d_b, 300 mm), k = 48 or 72 per Table 9-21-7); the length is NOT recomputed. f_y > 420 MPa is not covered by the lap route and is deterministically BLOCKED (the only other route, welded/mechanical splice per Clause 9-21-6-3-5-الف → 9-21-4-7, is BLOCKED via NBC Chapter 10). The welded/mechanical route of Clause 9-21-6-3-5-الف is NOT implemented.
Applicability: spiral lap-splice method selection. Required Inputs: yield_stress_mpa (≤ 420 MPa) plus the Table 9-21-7 selection inputs (splice_bar_type, coating_class, end_condition, bar_diameter_mm) (missing → BLOCKED; malformed / wrong type → INVALID_INPUT; f_y > 420 MPa → BLOCKED; delegated table combination not printed → BLOCKED). Dependencies: `BG-TRANS-SPIRAL-LAP-001`.
Units: mm. Executable as `beamgenius.engine.transverse_reinforcement_mabhas9.evaluate_spiral_splice_lap_sel`.

## BG-TRANS-TIE-ANCHOR-STD-HOOK-001 — Tie Deformed-Bar Anchorage, Standard-Hook Branch (Alef), Clause 9-21-6-1-3-Alef

Status: VERIFIED | Type: CODE_RULE | Source: Mabhas 9 (1399, 5th ed.) | PDF 463 | Printed 443

Formula / Requirement: Clause 9-21-6-1-3-Alef — the anchorage of a tie deformed bar (or wire) shall be made with a standard hook around the longitudinal bar, where the standard hook is the one of Clause 9-21-2-2-2 / Table 9-21-2. The clause has THREE branches and only (Alef) is implemented here: (Alef) bars/wires with d_b <= 16 mm (any f_y), OR bars with d_b 18-25 mm and f_y < 280 MPa -> standard hook; (Be) bars with d_b 18-25 mm and f_y > 280 MPa -> standard hook plus an embedment length plus a minimum outer bend diameter 0.17*f_y/(lambda*sqrt(f'c))*d_b (NOT implemented, lambda undefined in Section 9-21-6); (Pe) in joists, bars/wires with d_b <= 12 mm -> standard hook (implemented separately as `BG-TRANS-TIE-ANCHOR-JOIST-STD-HOOK-001`). Per the source-faithful reading confirmed 2026-10-06 (page-463 evidence JPG), the f_y < 280 MPa condition attaches to the 18-25 mm sub-condition ONLY — the d_b <= 16 mm sub-condition carries no f_y gate, so f_y >= 280 MPa with d_b <= 16 mm is still branch (Alef). The hook geometry is delegated to `BG-TRANS-STANDARD-HOOK-001` and is NOT re-implemented. The source names no unique hook angle, so the caller supplies `hook_angle_deg` and it is validated through the delegated evaluator. Genuine source gaps are deterministically BLOCKED and never interpolated: f_y = 280 MPa exactly (in neither (Alef) nor (Be)), d_b = 17 mm (between the printed <= 16 mm and 18-25 mm sub-conditions), d_b > 25 mm (assigned to neither branch), and the d_b 18-25 mm with f_y >= 280 MPa case that belongs to the unimplemented (Be).
Applicability: tie deformed-bar anchorage via a standard hook, branch (Alef) only. Required Inputs: yield_stress_mpa, bar_diameter_mm, hook_angle_deg, inner_bend_diameter_mm, straight_extension_mm, encloses_longitudinal_bar (bool) (missing -> BLOCKED; malformed / non-bool -> INVALID_INPUT; unsupported combination -> BLOCKED; not enclosing / under-size delegated geometry -> FAIL). Dependencies: `BG-TRANS-STANDARD-HOOK-001`.
Units: mm / MPa. Executable as `beamgenius.engine.transverse_reinforcement_mabhas9.evaluate_tie_anchor_std_hook`.

## BG-TRANS-TIE-ANCHOR-JOIST-STD-HOOK-001 — Tie Deformed-Bar Anchorage in Joists, Standard Hook, Clause 9-21-6-1-3-Pe

Status: VERIFIED | Type: CODE_RULE | Source: Mabhas 9 (1399, 5th ed.) | PDF 463 | Printed 443

Formula / Requirement: Clause 9-21-6-1-3-Pe, read verbatim from the page-463 evidence JPG on 2026-10-06: "(Pe) — in joists, for bars or wires with a diameter less than or equal to 12 mm, a standard hook shall be provided", where the standard hook is the one of Clause 9-21-2-2-2 / Table 9-21-2. The branch-marker glyph was cropped at >=14x magnification and its three sub-bowl dots counted (Be carries one, Pe carries three) before this branch was attributed to (Pe). Applicability is EXACTLY the printed condition and nothing more: (1) the member is a joist, AND (2) d_b <= 12 mm. The branch carries NO f_y condition, NO embedment length and NO outer bend-diameter formula, so `yield_stress_mpa` is deliberately NOT an input of this rule — no condition is invented. The source term "joist" is preserved because the source states it. The hook geometry is delegated to `BG-TRANS-STANDARD-HOOK-001` and is NOT re-implemented; the source names no unique hook angle, so the caller supplies `hook_angle_deg` and it is validated through the delegated evaluator. The rule is kept separate from `BG-TRANS-TIE-ANCHOR-STD-HOOK-001` (branch Alef) because its applicability differs (no f_y gate; 12 mm ceiling instead of 16 mm). d_b > 12 mm in a joist is deterministically BLOCKED — the joist provision is printed only up to 12 mm, and this rule never silently falls back to another branch or interpolates the limit.
Applicability: tie deformed-bar anchorage in a joist via a standard hook, branch (Pe) only. Required Inputs: in_joist (bool), bar_diameter_mm, hook_angle_deg, inner_bend_diameter_mm, straight_extension_mm, encloses_longitudinal_bar (bool) (missing -> BLOCKED; malformed / non-bool -> INVALID_INPUT; not a joist -> NOT_APPLICABLE, branch (Alef) or (Be) governs instead; d_b > 12 mm -> BLOCKED; not enclosing / under-size delegated geometry -> FAIL). Dependencies: `BG-TRANS-STANDARD-HOOK-001`.
Units: mm. Executable as `beamgenius.engine.transverse_reinforcement_mabhas9.evaluate_tie_anchor_joist_std_hook`.

## BG-TRANS-TORSION-TIE-WIRE-ROUTE-001 — Torsion / Integrity Tie Welded-Wire Route, Clause 9-21-6-1-4

Status: VERIFIED | Type: CODE_RULE | Source: Mabhas 9 (1399, 5th ed.) | PDF 464 | Printed 444

Formula / Requirement: the Clause 9-21-6-1-4 route referenced by Clause 9-21-6-1-6-Be and Clause 9-21-6-2-7-Be (both read: anchorage per Clause 9-21-6-1-3-Alef/-Be OR Clause 9-21-6-1-4, only where the concrete around the anchorage is not liable to deteriorate from a flange or a slab). Only the Clause 9-21-6-1-4 route of that OR is implemented here; the Clause 9-21-6-1-3 route stays blocked and the OR semantics are preserved. The U-tie geometry is delegated to `BG-TRANS-WIRE-TIE-UTIE-001` and is NOT re-implemented. This rule is a typed route/precondition evaluator that explicitly distinguishes three things: (1) the torsion-tie context precondition `concrete_around_anchorage_not_liable_to_spall` (False -> NOT_APPLICABLE, the (Be) route is unavailable); (2) that the welded-wire route was selected (`alternative`); (3) the underlying U-tie geometry result (delegated verbatim). Missing route-selection data -> BLOCKED; invalid underlying U-tie geometry -> FAIL per the delegate's own semantics.
Applicability: torsion/integrity-tie anchorage via the Clause 9-21-6-1-4 welded-wire U-tie route. Required Inputs: concrete_around_anchorage_not_liable_to_spall (bool), alternative (WireTieUtieAlternative) and the `BG-TRANS-WIRE-TIE-UTIE-001` geometry inputs (missing -> BLOCKED; malformed / non-bool -> INVALID_INPUT; violated U-tie condition -> FAIL; precondition False -> NOT_APPLICABLE). Dependencies: `BG-TRANS-WIRE-TIE-UTIE-001`.
Units: mm. Executable as `beamgenius.engine.transverse_reinforcement_mabhas9.evaluate_torsion_tie_wire_route`.

### BLOCKED (not promoted) — §9-21-6-1-3 / §9-21-6-1-5 / §9-21-6-1-6-ب / §9-21-6-2-7-ب / §9-21-6-2-3 / §9-21-6-3-5-الف

- `BG-TRANS-TIE-ANCHOR-PENDING` (9-21-6-1-3-Be only, PDF 463 / Printed 443): tie deformed-bar anchorage, remaining blocked branch only. BLOCKED — Stage H.7 narrowed this sentinel from the whole clause and Stage H.8 narrowed it again to branch (Be) only: branch (Alef) is now the executable `BG-TRANS-TIE-ANCHOR-STD-HOOK-001` and branch (Pe) is now the executable `BG-TRANS-TIE-ANCHOR-JOIST-STD-HOOK-001`. What remains here: branch (Be) (d_b 18-25 mm with f_y > 280 MPa: standard hook plus an embedment length plus a minimum outer bend diameter 0.17*f_y/(lambda*sqrt(f'c))*d_b, whose lambda is not defined anywhere in Section 9-21-6), plus the genuine source gaps f_y = 280 MPa exactly, d_b = 17 mm and d_b > 25 mm. (Stage H.7 M4 wording correction: the earlier text said "(Alef) covers d_b <= 16 mm and 8-25 mm"; Clause 9-21-6-1-3 prints only "d_b <= 16 mm" and "d_b 18-25 mm" — no 8 mm lower bound appears in this clause.) Boundaries are recorded verbatim, never interpolated/inferred.
- `BG-TRANS-WIRE-TIE-PENDING` (9-21-6-1-5, PDF 464 / Printed 444): single-leg welded-wire tie anchorage. BLOCKED — the 9-21-6-1-5-الف inner-wire distance wording is ambiguous and the 9-21-6-1-5-ب outer-wire condition carries no governing number. (Clause 9-21-6-1-4 was promoted in Stage H.5 to BG-TRANS-WIRE-TIE-UTIE-001 and is no longer covered here.)
- `BG-TRANS-TORSION-TIE-PENDING` ((Be) branches of 9-21-6-1-6 & 9-21-6-2-7, PDF 464-468 / Printed 444-448): BLOCKED — Section 9-21-6-1-6-Be delegates to Clauses 9-21-6-1-3 (still blocked) and 9-21-6-1-4; Section 9-21-6-2-7-Be delegates to Clause 9-21-6-1-3-Alef/-Be (blocked) OR Clause 9-21-6-1-4 (corrected in Stage H.5 — the JPG, PDF 468, shows 9-21-6-1-3-Alef/-Be or 9-21-6-1-4, NOT 9-21-6-4-1). Stage H.7 promoted the 9-21-6-1-4 route to the executable `BG-TRANS-TORSION-TIE-WIRE-ROUTE-001` (which delegates the U-tie geometry to `BG-TRANS-WIRE-TIE-UTIE-001`); that route is therefore NO LONGER blocked. The 9-21-6-1-3 route stays BLOCKED (its branch (Be) is unimplemented — lambda undefined and a positional embedment datum — and it carries the f_y = 280 MPa / d_b = 17 mm / d_b > 25 mm boundary gap), so this sentinel is retained for that route. Implementing one OR route does NOT make the whole (Be) clause executable, so neither Clause 9-21-6-1-6-Be nor Clause 9-21-6-2-7-Be is globally executable, and this rule must never be marked executable merely because one OR branch now is. The Section 9-21-6-2-7-Alef standard-hook option is no longer blocked here (promoted to BG-TRANS-TORSION-TIE-STANDARD-HOOK-001, geometry per Clause 9-21-2-2-2 / Table 9-21-2, PDF 443). Executable branches: BG-TRANS-TORSION-TIE-135HOOK-001, BG-TRANS-TWO-PIECE-TIE-001, BG-TRANS-TORSION-TIE-SEISMIC-HOOK-001, BG-TRANS-TORSION-TIE-STANDARD-HOOK-001, BG-TRANS-TORSION-TIE-WIRE-ROUTE-001, plus the separately-registered BG-TRANS-TIE-ANCHOR-STD-HOOK-001 and BG-TRANS-TIE-ANCHOR-JOIST-STD-HOOK-001 for the tie-anchorage route.
- `BG-TRANS-WIRE-SUBST-PENDING` (9-21-6-2-3, PDF 466 / Printed 446): deformed-wire or welded-wire-mesh substitute for a deformed tie. BLOCKED — §9-4-8 is visually verified (Stage H.14, printed pp. 66–69) and the **ISIRI 11558** standard required by **§9-4-8-7 was obtained and visually verified in Stage H.16** (`phase2f-source-11558/`, 19 pages, 1st edition). The dependency is nevertheless not deterministic: 11558 defines conformity only as third-party certification under ISO 10144:1991 or statistical acceptance of 15 (or 60) specimens from a ≤50 t consignment; it rates its product only at 500 MPa while Mabhas 9 Table 9-4-4 caps shear-tie design yield at 420 MPa; and it contains no welded-fabric requirement at all, so the Mabhas 9 mesh-vs-tie ambiguity remains open. See `docs/PHASE2F_STAGE_H16_ISIRI_11558_VERIFICATION.md`.
- `BG-TRANS-SPIRAL-SPLICE-SEL-PENDING` (9-21-6-3-5-الف, PDF 468 / Printed 448): welded/mechanical spiral-splice route. BLOCKED — depends on Clause 9-21-4-7 (registered dependency `BG-DEV-SPLICE-WELDED-MECH-PENDING`), itself blocked (transitive UNVERIFIED_RULE_BLOCKED). **Stage H.18 (audit-only, no status change)** traced the route edge-by-edge and corrected the blanket reason: the NBC Chapter 10 requirement (§9-21-4-7-3) binds the **welded** sub-branch only, so it is **not** a blocker of the mechanical sub-branch; the mechanical route is instead blocked by **§9-21-4-7-5** (cover obligation with no numeric threshold and no device-enlargement datum — `AMBIGUITY`, primary) and **§9-21-4-7-6** (1.25·f_y requirement on a proprietary device's capacity — `INPUT_MODEL_GAP`/`EXTERNAL_DEPENDENCY`, secondary). §9-21-4-7-4 carries no predicate; -7-7/-7-8 (750 mm staggering in tension members) are deterministic but not separable (the route is conjunctive — a partial rule would be a false PASS). See `docs/PHASE2F_STAGE_H18_MECHANICAL_SPLICE_ROUTE.md`. (The lap-splice route of Clause 9-21-6-3-5-ب was promoted in Stage H.5 to BG-TRANS-SPIRAL-SPLICE-LAP-SEL-001.)

All five are registered with `execution_allowed=False`, `status=VERIFY_PENDING`, and a `blocked_reason`; the Gatekeeper returns `UNVERIFIED_RULE_BLOCKED` for any attempted execution (the spiral-splice-selection rule additionally reports `TRANSITIVE_DEPENDENCY_BLOCKED` via `BG-DEV-SPLICE-WELDED-MECH-PENDING`). No Section 9-21-6 clause was executed through an unverified branch; Section 9-22 was not started. (Stage H.3 promoted `BG-TRANS-DORGIR-PENDING` to `BG-TRANS-DORGIR-001` and split the deterministic torsion-tie branches; Stage H.5 promoted BG-TRANS-STANDARD-HOOK-001, BG-TRANS-TORSION-TIE-STANDARD-HOOK-001, BG-TRANS-WIRE-TIE-UTIE-001 and BG-TRANS-SPIRAL-SPLICE-LAP-SEL-001, verified against Table 9-21-2 / PDF 443; Stage H.7 promoted BG-TRANS-TIE-ANCHOR-STD-HOOK-001 (Clause 9-21-6-1-3-Alef only) and BG-TRANS-TORSION-TIE-WIRE-ROUTE-001 (the Clause 9-21-6-1-4 route of the (Be) branches); Stage H.8 promoted BG-TRANS-TIE-ANCHOR-JOIST-STD-HOOK-001 (Clause 9-21-6-1-3-Pe only — in joists, d_b <= 12 mm, no f_y gate) and narrowed the two sentinels above again, leaving Section 9-21-6-1-3-Be, Section 9-21-6-1-5, Section 9-21-6-2-3 and Section 9-21-6-3-5-Alef BLOCKED. After H.8 the registry holds 121 rules: 63 executable (60 Mabhas 9 + 3 new Phase 2F rules), 48 blocked and 10 reference-executable.)
