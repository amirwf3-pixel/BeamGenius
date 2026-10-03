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
- Bundled bars: Clause 9-21-5-6 (equivalent diameter) is text-located but NOT visually verified — bundled input returns BLOCKED (`UNVERIFIED_RULE_BLOCKED` / `UNVERIFIED_BUNDLE_RULE`); no equivalent diameter is invented. Bundled cases never PASS.
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
- Bundled bars: Clause 9-21-5-6 is not visually verified — bundled input returns BLOCKED (`UNVERIFIED_BUNDLE_RULE`).
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
- Bundled groups (Clause 9-4-9-5-2 → equivalent diameter Clause 9-21-5-6): NOT visually verified — returns BLOCKED (`UNVERIFIED_BUNDLE_RULE`).
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
