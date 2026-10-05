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



### Shear Strength Reduction Factor φ and Factored One-Way Shear Check (BG-SHEAR-PHI-001)

Status: CODE\_RULE (VERIFIED in `docs/VERIFIED_RULES.md` as `BG-SHEAR-PHI-001`)

Source: Mabhas 9 (1399), PDF pages 128, 130–131, 133, 140 (design excerpt pp. 16, 18–19, 21, 28), printed pages 107, 109–110, 112, 119, Clauses 9-7-4-1, Table 9-7-2 (Row 2), 9-7-4-5, 9-8-1-4 Eq. (9-8-1-ب), 9-8-4-1-1, 9-8-4-1-2 Eq. (9-8-8)



- φ = 0.75 for standard one-way shear (Table 9-7-2, Row 2)

- Vn = Vc + Vs [Eq. (9-8-8)]

- φ × Vn = φ × (Vc + Vs) ≥ Vu [Eq. (9-8-1-ب)]

- Seismic capacity-design shear factor exceptions in Clause 9-7-4-5 (φ = 0.60 / φ = 0.85) remain blocked (`UNVERIFIED_RULE_BLOCKED`) when seismic capacity-design shear governs.



### Concrete One-Way Shear Resistance Vc (BG-SHEAR-VC-001)

Status: CODE\_RULE (VERIFIED in `docs/VERIFIED_RULES.md` as `BG-SHEAR-VC-001`)

Source: Mabhas 9 (1399), PDF pages 76–77, 140–142 (design excerpt pp. 28–30), printed pages 55–56, 119–121, Clauses 9-8-4-4-1 through 9-8-4-4-5, Eqs. (9-8-12-الف), (9-8-12-ب), (9-8-13), (9-8-14), 9-8-4-2-2, 9-3-2-2, Tables 9-3-1 & 9-3-2



- For Av ≥ Av,min (Clause 9-8-4-4-1):

  - Simplified [Eq. (9-8-12-الف)]: Vc = (0.17 × λ × √f'c + Nu / (6 × Ag)) × bw × d

  - Detailed [Eq. (9-8-12-ب)]: Vc = (0.66 × λ × (ρw)^(1/3) × √f'c + Nu / (6 × Ag)) × bw × d

- For Av < Av,min (Clause 9-8-4-4-2):

  - Size-effect [Eq. (9-8-13)]: Vc = (0.66 × λs × λ × (ρw)^(1/3) × √f'c + Nu / (6 × Ag)) × bw × d

- Size-effect factor [Eq. (9-8-14), Clause 9-8-4-4-5]: λs = min(√(2 / (1 + d / 250)), 1.0) = min(√(2 / (1 + 0.004 × d)), 1.0)

- Axial force modifier limit (Clause 9-8-4-4-3): Nu / (6 × Ag) ≤ 0.05 × f'c (Nu positive in compression, negative in tension)

- Bounds on Vc (Clause 9-8-4-4-4): 0 ≤ Vc ≤ 0.42 × λ × √f'c × bw × d

- √f'c ≤ 8.3 MPa in Vc unless beam/joist has at least minimum web shear reinforcement per Clause 9-11-5-2 (Clause 9-8-4-2-2).



### Transverse Reinforcement One-Way Shear Resistance Vs and Demand (BG-SHEAR-VS-001)

Status: CODE\_RULE (VERIFIED in `docs/VERIFIED_RULES.md` as `BG-SHEAR-VS-001`)

Source: Mabhas 9 (1399), PDF pages 89–90, 140, 142–144 (design excerpt pp. 28, 30–32), printed pages 68–69, 119, 121–123, Clauses 9-8-4-2-3, 9-4-8-5, Table 9-4-4, 9-8-4-5-1 Eq. (9-8-15), 9-8-4-5-3 Eq. (9-8-16), 9-8-4-5-4 Eq. (9-8-17)



- Required shear steel resistance [Eq. (9-8-15)]: Vs,req = max(Vu / φ - Vc, 0)

- Vertical stirrups (α = 90°) [Eq. (9-8-16)]: Vs = Av × fyt × d / s

- Inclined stirrups (45° ≤ α ≤ 90°) [Eq. (9-8-17)]: Vs = Av × fyt × (sin α + cos α) × d / s

- Constraint (Table 9-4-4): fyt ≤ 420 MPa for standard non-seismic shear stirrups/ties.



### Maximum One-Way Shear / Web-Crushing Limit (BG-SHEAR-VS-MAX-001)

Status: CODE\_RULE (VERIFIED in `docs/VERIFIED_RULES.md` as `BG-SHEAR-VS-MAX-001`)

Source: Mabhas 9 (1399), PDF page 140 (design excerpt p. 28), printed page 119, Clause 9-8-4-1-3, Eq. (9-8-9)



- Cross-section adequacy limit [Eq. (9-8-9)]: Vu ≤ φ × (Vc + 0.66 × √f'c × bw × d)

- Resulting upper bound on transverse reinforcement shear resistance: Vs,max = 0.66 × √f'c × bw × d



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



Implemented in Phase 2D: `beamgenius.engine.detailing_mabhas9.evaluate_minimum_transverse_bar_diameter` (registry `execution_allowed=True`); the non-bundled 32–36 mm interval returns `UNVERIFIED_RULE_BLOCKED` (`UNSUPPORTED_CONFIGURATION`).



### Compression Reinforcement Lateral Support

Status: CODE\_RULE (VERIFIED in `docs/VERIFIED_RULES.md` as `BG-DETAIL-COMP-LAT-001`)

Source: Mabhas 9, file page 229, Clause 9-11-6-5-12 (OCR token: 12-5-6-11-9)



sc ≤ min(

&#x20;   16 × db,

&#x20;   48 × dbt,

&#x20;   bmin

)



Implemented in Phase 2D: `beamgenius.engine.detailing_mabhas9.evaluate_compression_reinforcement_lateral_support_spacing` (registry `execution_allowed=True`); requires compression reinforcement and positive finite db/dbt/sc inputs, b_min = min(bw, h). No compression bar buckling behavior is modeled beyond this rule.



### Longitudinal Bar Minimum Clear Spacing in a Horizontal Layer

Status: CODE\_RULE (VERIFIED in `docs/VERIFIED_RULES.md` as `BG-DETAIL-LONG-SPACING-001`)

Source: Mabhas 9 (1399, 5th ed.), PDF page 441, printed page 420, Clause 9-21-2-1-1 (source-page capture visually verified 2026-10-03)



s_clear ≥ max(

    25 mm,

    db,max,

    (4/3) × d_agg

)



for parallel bars in one horizontal layer (clause items الف/ب/پ; the Persian `1/33` is decimal notation for 1.33). The column rule Clause 9-21-2-1-3 (40 mm / 1.5 × db,max) is never substituted; shotcrete is excluded (Clause 9-21-2-1-4 → NOT_APPLICABLE); bundled bars stay blocked in that rule (`UNVERIFIED_BUNDLE_RULE`): the Clause 9-21-5-6 equivalent diameter is VERIFIED and implemented as `BG-DETAIL-BUNDLE-006` (Phase 2F Stage B), but integrating it into the spacing rule is a separate pending stage.



Implemented in Phase 2E Stage B: `beamgenius.engine.detailing_spacing_mabhas9.evaluate_longitudinal_bar_clear_spacing` (registry `execution_allowed=True`); db,max and d_agg are REQUIRED inputs — missing inputs return `BLOCKED` (`MISSING_AGGREGATE_SIZE` / `MISSING_GOVERNING_BAR_DIAMETER`), malformed values `INVALID_INPUT`; bundled bars `BLOCKED` (`UNVERIFIED_BUNDLE_RULE`).



### Multi-Layer Vertical Clear Spacing and Alignment

Status: CODE\_RULE (VERIFIED in `docs/VERIFIED_RULES.md` as `BG-DETAIL-LAYER-SPACING-001`)

Source: Mabhas 9 (1399, 5th ed.), PDF page 441, printed page 420, Clause 9-21-2-1-2 (source-page capture visually verified 2026-10-03)



For parallel bars in several horizontal layers: (i) upper-layer bars shall be placed directly above lower-layer bars, and (ii) clear distance between two successive layers ≥ 25 mm (independent of db and aggregate size).



Implemented in Phase 2E Stage B: `beamgenius.engine.detailing_spacing_mabhas9.evaluate_longitudinal_layer_spacing` (registry `execution_allowed=True`); layer count and the typed vertical-alignment confirmation are REQUIRED inputs — missing layer geometry returns `BLOCKED` (`MISSING_LAYER_COUNT` / `MISSING_LAYER_ALIGNMENT`), never silently assumed; single layer → NOT_APPLICABLE; bundled bars → `UNVERIFIED_BUNDLE_RULE` (Clause 9-21-5-6 equivalent diameter VERIFIED as `BG-DETAIL-BUNDLE-006`; integration into this rule pending).



### Minimum Concrete Cover (Normal Environment)

Status: CODE\_RULE (VERIFIED in `docs/VERIFIED_RULES.md` as `BG-DETAIL-COVER-001`)

Source: Mabhas 9 (1399, 5th ed.), PDF pages 92–93, printed pages 71–72, Clauses 9-4-9-4, 9-4-9-5-1..3 + Table 9-4-6 (source-page captures visually verified 2026-10-03)



- No air/earth contact — beams (columns, pedestals, tension members): 40 mm over all longitudinal and transverse bars; slabs, joists, walls: db > 36 mm → 40 mm; db ≤ 34 mm → 20 mm.

- Air/weather or non-permanent earth contact (all members): db ≤ 16 mm → 40 mm; db 18–58 mm → 50 mm.

- Permanent earth contact (all members, all bars): 75 mm.

- Headed shear reinforcement (Clause 9-4-9-5-3): cover over head/plate ≥ member cover (same minimum).



Implemented in Phase 2E Stage B: `beamgenius.engine.detailing_spacing_mabhas9.evaluate_beam_cover` (registry `execution_allowed=True`); exposure condition, member type (BEAM/COLUMN/PEDESTAL/TENSION_MEMBER/SLAB/JOIST/WALL), and reinforcement type (LONGITUDINAL / TRANSVERSE) are REQUIRED typed inputs — missing inputs return `BLOCKED`, an unknown member type returns `INVALID_INPUT`; corrosive/unusual environments are routed to Appendix 9-پ1 (Clauses 9-4-9-6/9-4-9-7) and deterministically return `BLOCKED` (Appendix 9-پ1 values are never computed); the bundled-group rule (Clause 9-4-9-5-2, min(d_eq, 75|50 mm)) stays `BLOCKED` (`UNVERIFIED_BUNDLE_RULE`) pending integration of the Clause 9-21-5-6 equivalent diameter (VERIFIED as `BG-DETAIL-BUNDLE-006`) into this rule; uncovered diameter classes ((16, 18) mm, db > 58 mm, unexposed-slab (34, 36] mm) are blocked, never interpolated.



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



Structural-integrity longitudinal reinforcement shall be fully anchored so that reinforcement at the face of support can develop yield stress (a verified single-bar development/hook length is computable since Stage C via `BG-DEV-LENGTH-TENSION-001` / `BG-DEV-LENGTH-HOOKED-001`; integrating it into the integrity anchor-age check remains a separate, not yet implemented integration stage).



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


### Bundled Bars (گروه میلگردها) — Clauses 9-21-5-1..8

Status: CODE\_RULE (VERIFIED in `docs/VERIFIED_RULES.md` as `BG-DETAIL-BUNDLE-001` .. `BG-DETAIL-BUNDLE-008`)

Source: Mabhas 9 (1399, 5th ed.), PDF pages 462–463, printed pages 441–442, Clauses 9-21-5-1..8 (source-page captures visually verified 2026-10-03, re-confirmed 2026-10-05; page footers ۴۴۱ and ۴۴۲)



- `9-21-5-1` (`BG-DETAIL-BUNDLE-001`): at most 4 bars per bundle (n ≤ 4; n > 4 → FAIL).
- `9-21-5-2` (`BG-DETAIL-BUNDLE-002`): bundle enclosed by transverse reinforcement; compressed bundles require transverse bars dbt ≥ 12 mm.
- `9-21-5-3` (`BG-DETAIL-BUNDLE-003`): in beams, bundled bars with db > 34 mm prohibited (beam-specific clause; non-beam → NOT_APPLICABLE).
- `9-21-5-4` (`BG-DETAIL-BUNDLE-004`): in flexural members, cutoff points of bundle bars staggered by ≥ 40·db.
- `9-21-5-5` (`BG-DETAIL-BUNDLE-005`): bundles with > 2 bars — at most 2 bars in one plane (all-in-one-plane prohibited), except at splice locations.
- `9-21-5-6` (`BG-DETAIL-BUNDLE-006`): bundle as one equivalent bar of equal area / coincident centroid for spacing, cover, confinement-coefficient (9-21-3-2-1) and coating-factor (9-21-3-2-2) calculations; d_eq = db·√n for n identical bars (never for development length).
- `9-21-5-7` (`BG-DETAIL-BUNDLE-007`): bundle development length (tension or compression) = single-bar ld × {2-bar 1.00, 3-bar 1.20, 4-bar 1.33}.
- `9-21-5-8` (`BG-DETAIL-BUNDLE-008`): per-bar lap = single-bar ld with the 9-21-5-7 multiplier; individual laps must not overlap; bundle-to-bundle lap prohibited.



Implemented in Phase 2F Stage B: `beamgenius.engine.detailing_bundle_mabhas9` evaluators (registry `execution_allowed=True`; dispatched by `run_mabhas9_beam_check`; appended by `run_mabhas9_beam_detailing_workflow` when `bundle_n_bars` is supplied). Every physical fact is a REQUIRED typed input, never assumed (missing → `BLOCKED`; malformed → `INVALID_INPUT`); a single bar is `NOT_APPLICABLE`; n > 4 is owned by rule 001 (satellite rules defer → NOT_APPLICABLE). The single-bar development length of Clause 9-21-3 and the lap rules of Clause 9-21-4 are NOT computed (unverified dependencies): rules 007/008 apply only the verified bundle multipliers to a caller-provided verified ld and stay `BLOCKED` (`MISSING_SINGLE_BAR_DEVELOPMENT_LENGTH`) when it is missing. Mixed-diameter bundles stay `BLOCKED` (`UNSUPPORTED_CONFIGURATION`) under rule 006. Integrating the now-VERIFIED equivalent diameter into the bundled branches of the Phase 2E spacing/layer/cover rules is a separate pending stage (`UNVERIFIED_BUNDLE_RULE` unchanged there).



## Pending Verification



The following shall NOT be implemented as executable engineering rules until source verification is complete:



- Mabhas 9 doubly-reinforced beam flexural resistance (`BG-FLEX-RECT-DOUBLY-001`) and full T/L-beam neutral-axis-in-web flexural resistance (`BG-FLEX-TBEAM-CAP-001`, `BG-FLEX-LBEAM-CAP-001`)

- Mabhas 9 effective-width provision for T/L sections with flange in tension

- Mabhas 9 bent-up longitudinal bar shear resistance (`Eq. 9-8-18`), beams with web openings (`Clause 9-8-4-1-4`), variable-depth haunches (`Clause 9-8-4-1-6`), and seismic capacity-design shear provisions (`Clause 9-7-4-5` / `Chapter 9-20`)

- Integration of the VERIFIED bundled-bar equivalent diameter (Clause 9-21-5-6, implemented as `BG-DETAIL-BUNDLE-006` in Phase 2F Stage B) into the bundled branches of the clear-spacing (`BG-DETAIL-LONG-SPACING-001`), layer-spacing (`BG-DETAIL-LAYER-SPACING-001`) and cover (Clause 9-4-9-5-2, `BG-DETAIL-COVER-001`) rules (those branches keep returning `UNVERIFIED_BUNDLE_RULE` until this integration stage); corrosive/unusual-environment cover computations per Appendix 9-پ1 (Clauses 9-4-9-6/9-4-9-7; Tables 9-پ1-2..4 and 9-پ1-6 remain VERIFY_PENDING); cover diameter classes outside db ≤ 16 mm and db 18–58 mm (Table 9-4-6); the underlying single-bar development length (Clause 9-21-3 — **implemented 2026-10-05, Stage C**: `BG-DEV-LENGTH-TENSION-001` / `BG-DEV-LENGTH-COMPRESSION-001`), while lap rules (Clause 9-21-4, `VERIFIED_SOURCE_ONLY` — still NOT executable) consumed as typed inputs by `BG-DETAIL-BUNDLE-007/008` remain caller-supplied; bundle evaluators 007/008 themselves are unchanged

- Clause 9-11-6-6-2 non-perimeter beam structural integrity reinforcement

- Clause 9-11-6-2-4 (OCR 4-2-6-11-9) exact flexural bar extension equation

- Clause 9-11-6-2-5 (OCR 5-2-6-11-9) cutoff conditions

- Development-length and anchorage equations of Mabhas 9 Clause 9-21-3 (supersedes the former OCR token `Clause 2-3-6-9` placeholder): **PROMOTED & IMPLEMENTED 2026-10-05 (Phase 2F Stage C)** as `BG-DEV-LENGTH-TENSION-001` / `BG-DEV-LENGTH-TENSION-TABLE-001` / `BG-DEV-LENGTH-HOOKED-001` / `BG-DEV-LENGTH-HEADED-001` / `BG-DEV-MECH-ANCHOR-001` / `BG-DEV-WIRE-DEFORMED-001` / `BG-DEV-WIRE-PLAIN-001` / `BG-DEV-LENGTH-COMPRESSION-001` (registry `execution_allowed=True`; see `docs/VERIFIED_RULES.md` and matrix §4C; the compression wire-tie ψ_r branch stays `VERIFY_PENDING` by design). Still pending: lap-splice equations (Clause 9-21-4 — `VERIFIED_SOURCE_ONLY`, footer-verified PDF pp. 456–461 / printed pp. 436–441 in Phase 2F Stage D 2026-10-05 per matrix §4D; still **not executable**, `9-21-4-4-1-ب` disjunct semantics `VERIFY_PENDING`), negative bar extension, skin reinforcement, flexural bar extension (`9-11-6-2-4`) and cutoff (`9-11-6-2-5`)

- Transverse reinforcement / confinement detailing of Mabhas 9 Clause 9-21-6 (§9-21-6-1 خاموت‌ها, §9-21-6-2 تنگ‌ها, §9-21-6-3 دورپیچ‌ها, §9-21-6-4 دورگیر): **PROMOTED & IMPLEMENTED 2026-10-06 (Phase 2F Stage G)** for the fully-verified, dependency-free parts as `BG-TRANS-TIE-SHEAR-EXTENT-001` (9-21-6-1-1), `BG-TRANS-CLOSED-TIE-LAP-001` (9-21-6-1-8), `BG-TRANS-TIE-SPACING-001` (9-21-6-2-1), `BG-TRANS-TIE-DIA-001` (9-21-6-2-2), `BG-TRANS-RECT-TIE-001` (9-21-6-2-4-ب), `BG-TRANS-CIRC-TIE-001` (9-21-6-2-5-الف), `BG-TRANS-SPIRAL-SPACING-001` (9-21-6-3-1), `BG-TRANS-SPIRAL-DIA-001` (9-21-6-3-2), `BG-TRANS-SPIRAL-RATIO-001` (9-21-6-3-3 / Eq. 9-21-8), `BG-TRANS-SPIRAL-ANCHOR-001` (9-21-6-3-4), `BG-TRANS-SPIRAL-LAP-001` (9-21-6-3-6 / Table 9-21-7) — registry `execution_allowed=True`; see `docs/VERIFIED_RULES.md` and matrix §4G. Still BLOCKED (registered `execution_allowed=False`, `status=VERIFY_PENDING`): `BG-TRANS-TIE-ANCHOR-PENDING` (9-21-6-1-3 f_y 280 MPa / d_b boundary ambiguity), `BG-TRANS-WIRE-TIE-PENDING` (9-21-6-1-4/-1-5 welded-wire positioning), `BG-TRANS-TORSION-TIE-PENDING` (9-21-6-1-6/-1-7/-2-7 hook geometry), `BG-TRANS-WIRE-SUBST-PENDING` (9-21-6-2-3 → Clause 9-4-8, out of window), `BG-TRANS-SPIRAL-SPLICE-SEL-PENDING` (9-21-6-3-5 → Clause 9-21-4-7, blocked via NBC Chapter 10), `BG-TRANS-DORGIR-PENDING` (9-21-6-4 seismic hook). Note §9-21-6-2-2 (10 mm for db ≤ 32 mm / 12 mm for db ≥ 34 mm or bundles; 32 < db < 34 mm → BLOCKED) is distinct from the already-executable beam transverse-reinforcement-diameter rule `BG-DETAIL-TRANS-DIA-001` (Clause 9-11-6-5-11, 32/36 mm boundary)

- Negative reinforcement extension equation

- Skin reinforcement spacing

- Bent-bar anchorage length

- Remaining torsion rules

- Table 9-11-2 (OCR Table 2-11-99) remaining exceptions (one-way joists)

- Other OCR-corrupted numerical requirements



No unverified OCR value shall be used as an engineering calculation rule.

