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
