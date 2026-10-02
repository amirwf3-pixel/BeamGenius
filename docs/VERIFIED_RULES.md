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
