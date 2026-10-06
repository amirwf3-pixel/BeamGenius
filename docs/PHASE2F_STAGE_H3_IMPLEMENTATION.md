# Phase 2F — Stage H.3 Implementation: Verified Seismic-Hook / دورگیر / Tie Rules

**Status:** IMPLEMENTED. Baseline `578c9c0` (Stage G) on `arena/b9cd291a-beamgenius`;
`origin/main` `df8067a`. Implements ONLY the H.2-approved, source-verified candidate
branches. No scope broadening.

Visual `.jpg` authority from the committed scan `phase2f-source-442-472` @ `df8067a`
(re-read in Stages H.1/H.2); OCR `.txt` navigation-only, never trusted for values.

## New executable rules (all `VERIFIED` / `CODE_RULE` / `MABHAS_9_COMPLIANCE` / `execution_allowed=True`)

| Rule ID | Clause | PDF / Printed | Depends on |
|---|---|---|---|
| `BG-TRANS-SEISMIC-HOOK-001` | §9-21-2-2-4 | 442 / 442 | — (geometry anchor) |
| `BG-TRANS-DORGIR-001` | §9-21-6-4-1 & -4-2 | 470 / 450 | `BG-TRANS-SEISMIC-HOOK-001` |
| `BG-TRANS-TWO-PIECE-TIE-001` | §9-21-6-1-7 | 465 / 445 | — |
| `BG-TRANS-TORSION-TIE-135HOOK-001` | §9-21-6-1-6-الف | 464 / 444 | — |
| `BG-TRANS-TORSION-TIE-SEISMIC-HOOK-001` | §9-21-6-2-7-الف (seismic option) | 467 / 447 | `BG-TRANS-SEISMIC-HOOK-001` |

- **Seismic hook (§9-21-2-2-4):** bend ≥ 135° (≥ 90° for circular دورگیر); straight
  extension ≥ 6·d_b **or** ≥ 75 mm. Geometry inline; the terminological
  «مطابق تعریف فصل ۹-۲۰» is NOT a Chapter 9-20 dependency and Chapter 9-20 is never
  imported. Inputs: `circular_dorgir`, `bend_angle_deg`, `straight_extension_mm`,
  `bar_diameter_mm` — all required (missing → BLOCKED; malformed / bend > 180° /
  non-bool → INVALID_INPUT).
- **DORGIR (§9-21-6-4-1/-4-2):** closed ties OR wound continuous (§9-21-6-4-1); or
  multi-part, each component a seismic hook at both ends enclosing one longitudinal
  bar; interconnected headed bars prohibited (§9-21-6-4-2). Component hook geometry is
  **delegated** to `evaluate_seismic_hook` (no duplicated formula). Inputs:
  `dorgir_construction`, `uses_interconnected_headed_bars`, and (multi-part) the hook
  geometry + `hook_encloses_longitudinal_bar`.
- **Two-piece tie (§9-21-6-1-7):** U-tie 135° bends + member 90° bend adjacent to the
  non-spalling face. Only source-stated requirements; no invented geometry.
- **Torsion tie 135° hook (§9-21-6-1-6-الف):** both ends terminate with a 135° hook
  around the longitudinal bar. (ب) NOT implemented.
- **Torsion tie seismic hook (§9-21-6-2-7-الف seismic):** both ends seismic hook around
  the longitudinal bar; bend end anchored in core concrete; geometry delegated to the
  seismic-hook rule. Standard-hook option and (ب) NOT implemented.

## Sentinel changes

- `BG-TRANS-DORGIR-PENDING` **removed** (fully replaced by `BG-TRANS-DORGIR-001`).
- `BG-TRANS-TORSION-TIE-PENDING` **narrowed** to the still-blocked branches
  (§9-21-6-1-6-ب, §9-21-6-2-7-ب, and the §9-21-6-2-7-الف standard-hook option); its
  obsolete «geometry lives in Clause 9-20-6» reason replaced with the corrected
  delegation reasons.
- Unchanged blocked sentinels: `BG-TRANS-TIE-ANCHOR-PENDING`, `BG-TRANS-WIRE-TIE-PENDING`,
  `BG-TRANS-WIRE-SUBST-PENDING`, `BG-TRANS-SPIRAL-SPLICE-SEL-PENDING`.

## Counts

§9-21-6 rules: 16 executable + 5 blocked (was 11 + 6). Registry total 114
(Mabhas 9 executable 56, blocked 48).

## Not implemented (still blocked / out of scope)

§9-21-6-1-3, §9-21-6-1-4/-1-5, §9-21-6-2-3 (§9-4-8), §9-21-6-3-5 (§9-21-4-7 → Ch. 10),
§9-21-6-1-6-ب, §9-21-6-2-7-ب, and the §9-21-6-2-7-الف standard-hook option
(Table 9-21-2-2 not yet verified). No welded-wire, no §9-4-8, no welding/mechanical
splice, no unrelated refactor, no UI work.

## Files changed

- `src/beamgenius/engine/transverse_reinforcement_mabhas9.py` — constants,
  `DorgirConstruction`, `evaluate_seismic_hook`, `evaluate_dorgir`,
  `evaluate_two_piece_tie`, `evaluate_torsion_tie_135hook`,
  `evaluate_torsion_tie_seismic_hook`.
- `src/beamgenius/registry/catalog.py` — 5 new `RuleReference`s, removed
  `BG-TRANS-DORGIR-PENDING`, narrowed `BG-TRANS-TORSION-TIE-PENDING`, updated
  `_ALL_RULES_TUPLE`.
- `tests/test_mabhas9_seismic_hook_and_ties.py` (new) — focused tests.
- `tests/test_mabhas9_transverse_reinforcement.py`, `tests/test_registry_and_gatekeeper.py`
  — updated tuples / exact-set / obsolete DORGIR-PENDING test.
- `docs/VERIFIED_RULES.md`, `docs/PHASE2_SOURCE_VERIFICATION_MATRIX.md` — documented.
