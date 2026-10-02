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



- Mabhas 9 flexural resistance equations, stress-block parameters, strain/ductility limits, and resistance factors φ

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

