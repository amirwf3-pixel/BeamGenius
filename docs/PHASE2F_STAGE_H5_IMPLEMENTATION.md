# Phase 2F — Stage H.5 Implementation: Verified Standard-Hook / Wire-Tie / Lap-Splice Rules

**Status:** IMPLEMENTED. Baseline `a66284b` (Stage H.3) on `arena/b9cd291a-beamgenius`;
`origin/main` `df8067a`. Implements ONLY the four H.4-approved candidates + the
§9-21-6-2-7-ب sentinel delegation correction. No scope broadening.

Visual `.jpg` authority from the committed scan `phase2f-source-442-472` @ `df8067a`
(re-read in Stage H.4 — Table 9-21-2 read in FULL, all rows/angles, PDF p.443);
OCR `.txt` navigation-only, never trusted for values. The correct table name is
**Table 9-21-2** (the earlier «Table 9-21-2-2» wording was a Stage H.1–H.3 error,
corrected here).

## New executable rules (all `VERIFIED` / `CODE_RULE` / `MABHAS_9_COMPLIANCE` / `execution_allowed=True`)

| Rule ID | Clause | PDF / Printed | Depends on |
|---|---|---|---|
| `BG-TRANS-STANDARD-HOOK-001` | §9-21-2-2-2 (Table 9-21-2) | 442–443 / 442–443 | — (geometry anchor) |
| `BG-TRANS-TORSION-TIE-STANDARD-HOOK-001` | §9-21-6-2-7-الف (standard option) | 467 / 447 | `BG-TRANS-STANDARD-HOOK-001` |
| `BG-TRANS-WIRE-TIE-UTIE-001` | §9-21-6-1-4 (Fig 9-21-1) | 464 / 444 (Fig 465) | — |
| `BG-TRANS-SPIRAL-SPLICE-LAP-SEL-001` | §9-21-6-3-5-ب (→ §9-21-6-3-6) | 468–469 / 448–449 | `BG-TRANS-SPIRAL-LAP-001` |

- **Standard hook (§9-21-2-2-2 / Table 9-21-2):** 90° and 135° hooks;
  d_b 10–16 mm → inner bend ≥ 4·d_b, straight extension ≥ max(6·d_b, 75 mm);
  d_b 18–25 mm → inner bend ≥ 6·d_b, straight extension ≥ 12·d_b; the hook shall
  enclose a longitudinal bar. Inputs: `hook_angle_deg`, `bar_diameter_mm`,
  `inner_bend_diameter_mm`, `straight_extension_mm`, `encloses_longitudinal_bar`
  (missing → BLOCKED; malformed / non-bool → INVALID_INPUT; non-enclosing /
  under-size bend / under-size extension → FAIL). **180° → BLOCKED** (printed in the
  table but a distinct configuration not exercised by any §9-21-6 rule this stage —
  deferred, trivially promotable). **d_b = 17 mm, d_b < 10 mm, d_b > 25 mm → BLOCKED**
  (genuine table gaps; never interpolated).
- **Torsion-tie standard hook (§9-21-6-2-7-الف standard option):** validates
  `hook_engages_longitudinal_bar` + `bend_end_anchored_in_core_concrete` itself, then
  **delegates** the geometry to `evaluate_standard_hook(hook_angle_deg=135.0, …)`
  (no duplicated formula, no re-implementation of the seismic branch). The seismic
  option remains `BG-TRANS-TORSION-TIE-SEISMIC-HOOK-001`; the (ب) branch stays BLOCKED.
- **Wire-tie U-tie (§9-21-6-1-4):** one-of alternatives via a
  `WireTieUtieAlternative` selector — **الف**: two longitudinal wires at 50 mm
  spacing in the upper part of the U-tie (`wire_spacing_mm == 50.0`,
  `wires_in_upper_part_of_utie`); **ب**: `wire1_dist_from_compression_mm` < ¼·effective
  depth, `wire2_dist_from_compression_mm` < wire1, `wire1_to_wire2_spacing_mm` > 50 mm,
  `wire2_on_hook` and (if on a hook) `bend_diameter_mm` ≥ 8×`tie_wire_diameter_mm`.
  The caller supplies the measured distances — no geometry is inferred from Figure
  9-21-1. §9-21-6-1-5 remains separate & BLOCKED.
- **Spiral-splice lap selection (§9-21-6-3-5-ب):** the lap route is permitted for
  f_y ≤ 420 MPa (`yield_stress_mpa`); f_y > 420 MPa → BLOCKED. The lap length is
  **delegated** to `evaluate_spiral_lap_splice` (`BG-TRANS-SPIRAL-LAP-001`) — no
  duplicated length computation. The welded/mechanical route §9-21-6-3-5-الف stays
  BLOCKED (NBC Chapter 10).

## Sentinel changes

- `BG-TRANS-TORSION-TIE-PENDING` **corrected & narrowed**: the §9-21-6-2-7-ب delegation
  dependency was the erroneous «§9-21-6-4-1»; the JPG (PDF 468) shows the authoritative
  «§9-21-6-1-3-الف/-ب OR §9-21-6-1-4». The standard-hook option of §9-21-6-2-7-الف is
  removed (promoted), and the «Table 9-21-2-2» wording is corrected to «Table 9-21-2».
  The (ب) branch is **not** auto-promoted even though the §9-21-6-1-4 route is now
  executable, because the §9-21-6-1-3 route stays blocked.
- `BG-TRANS-WIRE-TIE-PENDING` **narrowed** to §9-21-6-1-5 only (§9-21-6-1-4 promoted).
- `BG-TRANS-SPIRAL-SPLICE-SEL-PENDING` **narrowed** to §9-21-6-3-5-الف only
  (§9-21-6-3-5-ب promoted).
- Unchanged blocked sentinels: `BG-TRANS-TIE-ANCHOR-PENDING`, `BG-TRANS-WIRE-SUBST-PENDING`.

## Counts

§9-21-6 rules: 20 executable + 5 blocked (was 16 + 5). Registry total 118
(Mabhas 9 executable 60, blocked 48). No duplicate rule IDs.

## Not implemented (still blocked / out of scope)

§9-21-6-1-3 (boundary gap), §9-21-6-1-5, §9-21-6-2-3 (§9-4-8),
§9-21-6-3-5-الف welded/mechanical (§9-21-4-7 → NBC Ch. 10), §9-21-6-1-6-ب,
§9-21-6-2-7-ب, the 180° standard hook, and d_b = 17 mm / < 10 mm / > 25 mm.
No §9-4-8, no welding/mechanical splice, no unrelated refactor, no UI work,
no reference-package import, no reference PDF/OCR/JPG copied into the branch.

## Files changed

- `src/beamgenius/engine/transverse_reinforcement_mabhas9.py` — Table 9-21-2 /
  wire-tie / lap-sel constants, `WireTieUtieAlternative`, `evaluate_standard_hook`,
  `evaluate_torsion_tie_standard_hook`, `evaluate_wire_tie_utie` +
  `_evaluate_wire_tie_utie_alef` / `_evaluate_wire_tie_utie_be`,
  `evaluate_spiral_splice_lap_sel`.
- `src/beamgenius/registry/catalog.py` — 4 new `RuleReference`s, 3 sentinels
  corrected/narrowed, updated `_ALL_RULES_TUPLE`.
- `tests/test_mabhas9_standard_hook_and_splits.py` (new) — ~55 focused tests.
- `tests/test_mabhas9_seismic_hook_and_ties.py`,
  `tests/test_mabhas9_transverse_reinforcement.py`,
  `tests/test_registry_and_gatekeeper.py` — imports / tuples / exact-set updates.
- `docs/VERIFIED_RULES.md`, `docs/PHASE2_SOURCE_VERIFICATION_MATRIX.md` — documented.

## Verification

`pytest` **577 passed** (was 522; +55 focused cases). `mypy --strict` clean
(23 source files). No false PASS; missing input → BLOCKED, invalid → FAIL/INVALID,
source gaps → BLOCKED with a specific diagnostic code.
