# BeamGenius — Design Rules



## Governing Code



- Iranian National Building Regulations

- Mabhas 9 — Design and Construction of Reinforced Concrete Buildings

- Governing edition: 1399 / v5.0



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

Status: CODE\_RULE

Source: Mabhas 9, file page 228, Clause 11-5-6-11-9



- db ≤ 32 mm → transverse reinforcement ≥ 10 mm

- db ≥ 36 mm → transverse reinforcement ≥ 12 mm

- Bundled longitudinal bars → transverse reinforcement ≥ 12 mm



The 32–36 mm interval is not inferred.



### Compression Reinforcement Lateral Support

Status: CODE\_RULE

Source: Mabhas 9, file page 229, Clause 12-5-6-11-9



sc ≤ min(

&#x20;   16 × db,

&#x20;   48 × dbt,

&#x20;   bmin

)



### Structural Integrity Reinforcement

Status: CODE\_RULE

Source: Mabhas 9, file pages 229–230



- Minimum 1/4 of maximum positive flexural reinforcement, but not less than 2 bars, continuous.

- Minimum 1/6 of negative flexural reinforcement at support, but not less than 2 bars, continuous.

- Structural-integrity reinforcement shall satisfy the applicable continuity and enclosure requirements.



### Continuity Through Column Region

Status: CODE\_RULE

Source: Mabhas 9, file page 230, Clause 11-6-6-3-9



Structural-integrity longitudinal reinforcement shall pass through the region enclosed by longitudinal column reinforcement.



### Non-Continuous Supports

Status: CODE\_RULE

Source: Mabhas 9, file page 230, Clause 11-6-6-4-9



Structural-integrity longitudinal reinforcement shall be fully anchored so that reinforcement at the face of support can develop yield stress.



### Flexural Bar Extension

Status: CODE\_RULE

Source: Mabhas 9, file page 224, Clause 4-2-6-11-9



Tension reinforcement that remains in the member shall extend at least development length Ld beyond the point where reinforcement is no longer required for flexure.



### Positive Reinforcement at Simple Supports

Status: CODE\_RULE

Source: Mabhas 9, file page 225, Clause 2-3-6-11-9



At least 1/4 of the maximum positive flexural reinforcement shall continue through the support and extend at least 150 mm into the support.



For beams forming part of the primary lateral-load-resisting system, the reinforcement shall be anchored to develop yield stress.



## Pending Verification



The following shall NOT be implemented as executable engineering rules until source verification is complete:



- Clause 5-2-6-11-9 cutoff conditions

- Clause 2-3-6-9 development-length equations

- Negative reinforcement extension equation

- Skin reinforcement spacing

- Bent-bar anchorage length

- Remaining torsion rules

- Table 2-11-99 exceptions

- Other OCR-corrupted numerical requirements



No unverified OCR value shall be used as an engineering calculation rule.

'@ | Set-Content "D:\\BeamGenius\\project\\docs\\DESIGN\_RULES.md" -Encoding UTF8



