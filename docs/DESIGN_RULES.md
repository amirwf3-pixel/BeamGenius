# BeamGenius — Design Rules



## Source Hierarchy

### Primary Engineering Reference
**Davood Mostofinejad — Reinforced Concrete Structures, Vol. 1**

Use as the primary engineering source for:
- Design formulas
- Calculation logic and methodology
- Design procedures
- Worked examples
- Engineering interpretation of reinforced-concrete beam behavior

### Governing Code
**Iranian National Building Regulations — Mabhas 9**

Use for:
- Mandatory code requirements
- Limits and restrictions
- Detailing requirements
- Required checks and compliance conditions
- Code-specific applicability conditions

### Conflict Rule
If an engineering method or interpretation from the reference conflicts with an explicit requirement of Mabhas 9, **Mabhas 9 governs**.

### Source Integrity
- Every executable engineering rule must have a traceable source.
- OCR text is evidence for locating source material, not an authoritative engineering source by itself.
- No unverified OCR value may become an executable engineering rule.
- Numerical formulas and design logic must be verified against Mostofinejad Vol. 1 before implementation.
- Code limits and detailing requirements must be verified against Mabhas 9.

## Rule Status



- CODE\_RULE

- ENGINEERING\_REFERENCE

- PROJECT\_RULE

- TEMPORARY

- VERIFY\_PENDING

- NOT\_CHECKED

- REVIEW\_REQUIRED



## Beam Rules



### Minimum Flexural Reinforcement

Status: CODE\_RULE

Source: Mabhas 9, file page 220, printed page 199



As,min = max(

&#x20;   0.25 × √f'c × bw × d / fy,

&#x20;   1.4 × bw × d / fy

)



Constraint:

fy ≤ 550 MPa



### Equivalent Rectangular Stress-Block Parameters (BG-FLEX-STRESS-BLOCK)

Status: CODE\_RULE (VERIFIED in `docs/VERIFIED_RULES.md` as `BG-FLEX-STRESS-BLOCK`)

Source: Mabhas 9 (1399), PDF pages 22–23, printed pages 113–114, Clauses 9-8-2-2-6 & 9-8-2-2-7, Eqs. (9-8-2), (9-8-3-الف), (9-8-3-ب), (9-8-4)



- a = β1 × c

- For 20 MPa ≤ f'c ≤ 28 MPa: β1 = 0.85

- For f'c > 28 MPa: β1 = max(0.85 - 0.05 × (f'c - 28) / 7, 0.65)

- For f'c ≤ 55 MPa: α0 = 0.85

- For f'c > 55 MPa: α0 = max(0.85 - 0.004 × (f'c - 55), 0.75)



### Flexural Strain Compatibility and Beam Ductility Limit (BG-FLEX-STRAIN-LIMIT)

Status: CODE\_RULE (VERIFIED in `docs/VERIFIED_RULES.md` as `BG-FLEX-STRAIN-LIMIT`)

Source: Mabhas 9 (1399), PDF pages 16–18, 22, 41, printed pages 107–109, 113, 132, Clauses 9-8-2-2-2, 9-8-2-2-3, 9-7-4-2, 9-11-2-3



- εcu = 0.003

- εty = fy / Es (with Es = 200,000 MPa per Clause 9-4-8-4, fy ≤ 550 MPa per Table 9-4-4)

- εt = 0.003 × (dt - c) / c

- Non-prestressed beams with Pu < 0.10 × f'c × Ag must be tension-controlled at nominal strength: εt ≥ εty + 0.003 (equivalently c / dt ≤ 0.003 / (εty + 0.006)).



### Flexural Strength Reduction Factor φ (BG-FLEX-PHI-FACTOR)

Status: CODE\_RULE (VERIFIED in `docs/VERIFIED_RULES.md` as `BG-FLEX-PHI-FACTOR`)

Source: Mabhas 9 (1399), PDF pages 16–18, printed pages 107–109, Clauses 9-7-4-1 through 9-7-4-4, Table 9-7-2, Eqs. (9-7-10-الف) & (9-7-10-ب)



- Tension-controlled (εt ≥ εty + 0.003): φ = 0.90

- Compression-controlled (εt ≤ εty): φ = 0.75 (spiral) / φ = 0.65 (other)

- Transition zone (εty < εt < εty + 0.003):

  - Spiral: φ = 0.75 + 0.15 × (εt - εty) / 0.003

  - Other (tied beams): φ = 0.65 + 0.25 × (εt - εty) / 0.003



### Rectangular Singly-Reinforced Beam Flexural Resistance (BG-FLEX-RECT-SINGLY-001)

Status: CODE\_RULE (VERIFIED in `docs/VERIFIED_RULES.md` as `BG-FLEX-RECT-SINGLY-001`)

Source: Mabhas 9 (1399), PDF pages 16–18, 21–23, 41, printed pages 107–109, 112–114, 132, Clauses 9-8-1-4 Eq. (9-8-1-الف), 9-8-2-1-1, 9-8-2-2-1 through 9-8-2-2-8, 9-11-2-3



- a = (As × fy) / (α0 × f'c × bw), c = a / β1

- Mn = As × fy × (d - a / 2)

- φMn ≥ Mu with φ = 0.90 and εt ≥ εty + 0.003 required for non-prestressed beams (Pu < 0.10 × f'c × Ag).

- Doubly-reinforced sections (`BG-FLEX-RECT-DOUBLY-001`) and T/L flanged flexural capacity (`BG-FLEX-TBEAM-CAP-001`, `BG-FLEX-LBEAM-CAP-001`) remain `VERIFY_PENDING` and blocked.



### T-Beam and L-Beam Effective Compression Flange Width (BG-FLEX-TBEAM-B-EFF-001)

Status: CODE\_RULE (VERIFIED in `docs/VERIFIED_RULES.md` as `BG-FLEX-TBEAM-B-EFF-001`)

Source: Mabhas 9 (1399), PDF pages 12–13, 41, printed pages 103–104, 132, Clauses 9-6-3-3-1, Table 9-6-1, 9-6-3-3-2, 9-11-2-5



- T-beam (flange both sides of web): overhang on each side ≤ min(8 × hf, sw / 2, ln / 8); bf ≤ bw + 2 × min(8 × hf, sw / 2, ln / 8)

- L-beam (flange one side of web): overhang from web ≤ min(6 × hf, sw / 2, ln / 12); bf ≤ bw + min(6 × hf, sw / 2, ln / 12)

- Isolated T-beam (Clause 9-6-3-3-2): hf ≥ 0.5 × bw and bf ≤ 4 × bw



### Minimum Shear Reinforcement

Status: CODE\_RULE

Source: Mabhas 9, file page 221



Av/s ≥ 0.062 × √f'c × (bw/fyt)

Av/s ≥ 0.35 × (bw/fyt)



(Av/s)min = max(

&#x20;   0.062 × √f'c × (bw/fyt),

&#x20;   0.35 × (bw/fyt)

)



### Maximum Stirrup Spacing

Status: CODE\_RULE

Source: Mabhas 9, file page 227



If:

Vs ≤ 0.33 × √f'c × bw × d



Then:

s ≤ min(d/2, 600 mm)

s2 ≤ min(d, 300 mm)



If:

Vs > 0.33 × √f'c × bw × d



Then:

s ≤ min(d/4, 300 mm)

s2 ≤ min(d/2, 300 mm)



### Minimum Transverse Reinforcement Diameter

Status: CODE\_RULE (VERIFIED in `docs/VERIFIED_RULES.md` as `BG-DETAIL-TRANS-DIA-001`)

Source: Mabhas 9, file page 228, Clause 9-11-6-5-11 (OCR token: 11-5-6-11-9)



- db ≤ 32 mm → transverse reinforcement ≥ 10 mm

- db ≥ 36 mm → transverse reinforcement ≥ 12 mm

- Bundled longitudinal bars → transverse reinforcement ≥ 12 mm



The 32–36 mm interval is not inferred.



### Compression Reinforcement Lateral Support

Status: CODE\_RULE (VERIFIED in `docs/VERIFIED_RULES.md` as `BG-DETAIL-COMP-LAT-001`)

Source: Mabhas 9, file page 229, Clause 9-11-6-5-12 (OCR token: 12-5-6-11-9)



sc ≤ min(

&#x20;   16 × db,

&#x20;   48 × dbt,

&#x20;   bmin

)



### Structural Integrity Reinforcement (Perimeter Beams)

Status: CODE\_RULE (VERIFIED in `docs/VERIFIED_RULES.md` as `BG-INTEG-PERIMETER-001`)

Source: Mabhas 9, file pages 229–230, Clause 9-11-6-6-1



- Perimeter beams: minimum 1/4 of maximum positive flexural reinforcement, but not less than 2 bars, continuous.

- Perimeter beams: minimum 1/6 of negative flexural reinforcement at support, but not less than 2 bars, continuous.

- Enclosed by closed stirrups or closed ties over the clear span.

- Note: Clause 9-11-6-6-2 for non-perimeter beams remains `VERIFY_PENDING` and blocked.



### Continuity Through Column Region

Status: CODE\_RULE (VERIFIED in `docs/VERIFIED_RULES.md` as `BG-INTEG-COL-001`)

Source: Mabhas 9, file page 230, Clause 9-11-6-6-3 (OCR token: 11-6-6-3-9)



Structural-integrity longitudinal reinforcement shall pass through the region enclosed by longitudinal column reinforcement.



### Non-Continuous Supports

Status: CODE\_RULE (VERIFIED in `docs/VERIFIED_RULES.md` as `BG-INTEG-ANCHOR-001`)

Source: Mabhas 9, file page 230, Clause 9-11-6-6-4 (OCR token: 11-6-6-4-9)



Structural-integrity longitudinal reinforcement shall be fully anchored so that reinforcement at the face of support can develop yield stress (quantitative development/hook length equation remains `VERIFY_PENDING`).



### Flexural Bar Extension

Status: VERIFY\_PENDING

Source: Mabhas 9, file page 224, Clause 9-11-6-2-4 (OCR token: 4-2-6-11-9)



General concept: tension reinforcement that remains in the member extends beyond the point where reinforcement is no longer required for flexure; exact clause/equation (including comparison with effective depth d, 12db, and development length Ld) remains `VERIFY_PENDING` and blocked until source verification is complete.



### Positive Reinforcement at Simple and Interior Supports

Status: CODE\_RULE (VERIFIED in `docs/VERIFIED_RULES.md` as `BG-SUPPORT-POS-001`)

Source: Mabhas 9, file page 225, Clause 9-11-6-3-2 (OCR token: 2-3-6-11-9)



- Simple support: at least 1/3 of the maximum positive flexural reinforcement shall continue into the support and extend at least 150 mm into the support.

- Interior support: at least 1/4 of the maximum positive flexural reinforcement shall continue into the support and extend at least 150 mm into the support where applicable.

- For beams forming part of the primary lateral-load-resisting system, the reinforcement shall be anchored to develop yield stress fy at the face of the support.



## Pending Verification



The following shall NOT be implemented as executable engineering rules until source verification is complete:



- Mabhas 9 doubly-reinforced beam flexural resistance (`BG-FLEX-RECT-DOUBLY-001`) and full T/L-beam neutral-axis-in-web flexural resistance (`BG-FLEX-TBEAM-CAP-001`, `BG-FLEX-LBEAM-CAP-001`)

- Mabhas 9 effective-width provision for T/L sections with flange in tension

- Mabhas 9 concrete shear resistance Vc, shear reinforcement demand Vs, and maximum shear resistance Vs,max

- Mabhas 9 minimum concrete cover and longitudinal/layer bar clear spacing rules

- Clause 9-11-6-6-2 non-perimeter beam structural integrity reinforcement

- Clause 9-11-6-2-4 (OCR 4-2-6-11-9) exact flexural bar extension equation

- Clause 9-11-6-2-5 (OCR 5-2-6-11-9) cutoff conditions

- Clause 2-3-6-9 (OCR token) development-length equations

- Negative reinforcement extension equation

- Skin reinforcement spacing

- Bent-bar anchorage length

- Remaining torsion rules

- Table 9-11-2 (OCR Table 2-11-99) remaining exceptions (one-way joists)

- Other OCR-corrupted numerical requirements



No unverified OCR value shall be used as an engineering calculation rule.

