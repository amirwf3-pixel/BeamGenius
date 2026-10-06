"""Focused tests for the Phase 2F Stage H.5 verified rules (Mabhas 9, 1399).

Rules under test (all Mabhas 9, 1399 5th ed.; visually re-verified 2026-10-06
from the committed evidence scan phase2f-source-442-472 @ df8067a):

- ``BG-TRANS-STANDARD-HOOK-001`` — Clause 9-21-2-2-2 & Table 9-21-2
  (PDF pp. 442-443 / Printed pp. 442-443)
- ``BG-TRANS-TORSION-TIE-STANDARD-HOOK-001`` — Clause 9-21-6-2-7-الف standard
  135-degree hook option (PDF p. 467 / Printed p. 447), geometry per Table 9-21-2
- ``BG-TRANS-WIRE-TIE-UTIE-001`` — Clause 9-21-6-1-4 (PDF p. 464 / Printed p. 444)
- ``BG-TRANS-SPIRAL-SPLICE-LAP-SEL-001`` — Clause 9-21-6-3-5-ب
  (PDF pp. 468-469 / Printed pp. 448-449), length delegated to
  BG-TRANS-SPIRAL-LAP-001

Every expected outcome was hand-checked against the visually verified source;
OCR was never used as authority. Unsupported configurations (d_b = 17 mm,
d_b > 25 mm, the 180-degree hook, f_y > 420 MPa) and the still-blocked
delegated branches (Clause 9-21-6-1-5, Clause 9-21-6-2-7-ب, the welded /
mechanical splice route) are asserted to remain BLOCKED — never a false PASS.
"""

from __future__ import annotations

import pytest

from beamgenius.domain.enums import EvaluationOutcome, JurisdictionMode
from beamgenius.engine.transverse_reinforcement_mabhas9 import (
    SpiralSpliceBarType,
    SpiralSpliceCoating,
    SpiralSpliceEndCondition,
    WireTieUtieAlternative,
    evaluate_spiral_lap_splice,
    evaluate_spiral_splice_lap_sel,
    evaluate_standard_hook,
    evaluate_torsion_tie_seismic_hook,
    evaluate_torsion_tie_standard_hook,
    evaluate_wire_tie_utie,
)
from beamgenius.registry.catalog import (
    RULE_BG_TRANS_SPIRAL_LAP_001,
    RULE_BG_TRANS_SPIRAL_SPLICE_LAP_SEL_001,
    RULE_BG_TRANS_SPIRAL_SPLICE_SEL_PENDING,
    RULE_BG_TRANS_STANDARD_HOOK_001,
    RULE_BG_TRANS_TIE_ANCHOR_PENDING,
    RULE_BG_TRANS_TORSION_TIE_PENDING,
    RULE_BG_TRANS_TORSION_TIE_SEISMIC_HOOK_001,
    RULE_BG_TRANS_TORSION_TIE_STANDARD_HOOK_001,
    RULE_BG_TRANS_WIRE_SUBST_PENDING,
    RULE_BG_TRANS_WIRE_TIE_PENDING,
    RULE_BG_TRANS_WIRE_TIE_UTIE_001,
    _ALL_RULES_TUPLE,
    list_blocked_rules,
    list_mabhas9_executable_rules,
)
from beamgenius.registry.gatekeeper import evaluate_rule_gate

MOST = JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY

H5_NEW_EXECUTABLE_RULES = (
    RULE_BG_TRANS_STANDARD_HOOK_001,
    RULE_BG_TRANS_TORSION_TIE_STANDARD_HOOK_001,
    RULE_BG_TRANS_WIRE_TIE_UTIE_001,
    RULE_BG_TRANS_SPIRAL_SPLICE_LAP_SEL_001,
)


# ============================================================================
# BG-TRANS-STANDARD-HOOK-001 — Clause 9-21-2-2-2 & Table 9-21-2
# ============================================================================

def test_standard_hook_90_db_10_16_valid() -> None:
    # d_b = 12 mm (10-16 row): inner bend >= 4*12 = 48, ext >= max(6*12, 75) = 75.
    step = evaluate_standard_hook(
        hook_angle_deg=90.0,
        bar_diameter_mm=12.0,
        inner_bend_diameter_mm=48.0,
        straight_extension_mm=75.0,
        encloses_longitudinal_bar=True,
    )
    assert step.outcome is EvaluationOutcome.PASS
    assert step.rule_id == "BG-TRANS-STANDARD-HOOK-001"


def test_standard_hook_90_db_10_16_invalid_bend_diameter() -> None:
    step = evaluate_standard_hook(
        hook_angle_deg=90.0,
        bar_diameter_mm=12.0,
        inner_bend_diameter_mm=47.0,  # < 4*12 = 48
        straight_extension_mm=75.0,
        encloses_longitudinal_bar=True,
    )
    assert step.outcome is EvaluationOutcome.FAIL
    assert step.diagnostics[0].code == "STANDARD_HOOK_INNER_BEND_BELOW_MINIMUM"


def test_standard_hook_90_db_10_16_invalid_extension() -> None:
    step = evaluate_standard_hook(
        hook_angle_deg=90.0,
        bar_diameter_mm=12.0,
        inner_bend_diameter_mm=48.0,
        straight_extension_mm=74.0,  # < max(6*12, 75) = 75
        encloses_longitudinal_bar=True,
    )
    assert step.outcome is EvaluationOutcome.FAIL
    assert step.diagnostics[0].code == "STANDARD_HOOK_EXTENSION_BELOW_MINIMUM"


def test_standard_hook_90_db_18_25_valid() -> None:
    # d_b = 20 mm (18-25 row): inner bend >= 6*20 = 120, ext >= 12*20 = 240.
    step = evaluate_standard_hook(
        hook_angle_deg=90.0,
        bar_diameter_mm=20.0,
        inner_bend_diameter_mm=120.0,
        straight_extension_mm=240.0,
        encloses_longitudinal_bar=True,
    )
    assert step.outcome is EvaluationOutcome.PASS


def test_standard_hook_90_db_18_25_invalid_extension() -> None:
    step = evaluate_standard_hook(
        hook_angle_deg=90.0,
        bar_diameter_mm=20.0,
        inner_bend_diameter_mm=120.0,
        straight_extension_mm=239.0,  # < 12*20 = 240
        encloses_longitudinal_bar=True,
    )
    assert step.outcome is EvaluationOutcome.FAIL
    assert step.diagnostics[0].code == "STANDARD_HOOK_EXTENSION_BELOW_MINIMUM"


def test_standard_hook_135_db_10_16_valid() -> None:
    # d_b = 14 mm (10-16 row): inner bend >= 4*14 = 56, ext >= max(6*14, 75) = 84.
    step = evaluate_standard_hook(
        hook_angle_deg=135.0,
        bar_diameter_mm=14.0,
        inner_bend_diameter_mm=56.0,
        straight_extension_mm=84.0,
        encloses_longitudinal_bar=True,
    )
    assert step.outcome is EvaluationOutcome.PASS


def test_standard_hook_135_db_10_16_invalid() -> None:
    step = evaluate_standard_hook(
        hook_angle_deg=135.0,
        bar_diameter_mm=14.0,
        inner_bend_diameter_mm=55.0,  # < 4*14 = 56
        straight_extension_mm=84.0,
        encloses_longitudinal_bar=True,
    )
    assert step.outcome is EvaluationOutcome.FAIL
    assert step.diagnostics[0].code == "STANDARD_HOOK_INNER_BEND_BELOW_MINIMUM"


def test_standard_hook_135_db_18_25_valid_source_provided() -> None:
    # Table 9-21-2 also prints the 135-degree hook for d_b 18-25 mm.
    # d_b = 22 mm: inner bend >= 6*22 = 132, ext >= 12*22 = 264.
    step = evaluate_standard_hook(
        hook_angle_deg=135.0,
        bar_diameter_mm=22.0,
        inner_bend_diameter_mm=132.0,
        straight_extension_mm=264.0,
        encloses_longitudinal_bar=True,
    )
    assert step.outcome is EvaluationOutcome.PASS


def test_standard_hook_db_17_gap_blocked() -> None:
    step = evaluate_standard_hook(
        hook_angle_deg=90.0,
        bar_diameter_mm=17.0,
        inner_bend_diameter_mm=68.0,
        straight_extension_mm=102.0,
        encloses_longitudinal_bar=True,
    )
    assert step.outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "STANDARD_HOOK_DB_IN_GAP"


def test_standard_hook_db_above_25_blocked() -> None:
    step = evaluate_standard_hook(
        hook_angle_deg=90.0,
        bar_diameter_mm=26.0,
        inner_bend_diameter_mm=156.0,
        straight_extension_mm=312.0,
        encloses_longitudinal_bar=True,
    )
    assert step.outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "STANDARD_HOOK_DB_ABOVE_TABLE"


def test_standard_hook_db_below_10_blocked() -> None:
    step = evaluate_standard_hook(
        hook_angle_deg=90.0,
        bar_diameter_mm=8.0,
        inner_bend_diameter_mm=32.0,
        straight_extension_mm=75.0,
        encloses_longitudinal_bar=True,
    )
    assert step.outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "STANDARD_HOOK_DB_BELOW_TABLE"


def test_standard_hook_180_deg_deferred_blocked() -> None:
    step = evaluate_standard_hook(
        hook_angle_deg=180.0,
        bar_diameter_mm=12.0,
        inner_bend_diameter_mm=48.0,
        straight_extension_mm=75.0,
        encloses_longitudinal_bar=True,
    )
    assert step.outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "STANDARD_HOOK_180_DEG_NOT_IMPLEMENTED"


def test_standard_hook_unsupported_angle_blocked() -> None:
    step = evaluate_standard_hook(
        hook_angle_deg=120.0,
        bar_diameter_mm=12.0,
        inner_bend_diameter_mm=48.0,
        straight_extension_mm=75.0,
        encloses_longitudinal_bar=True,
    )
    assert step.outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "STANDARD_HOOK_ANGLE_NOT_IN_TABLE_9_21_2"


def test_standard_hook_not_enclosing_longitudinal_bar_fails() -> None:
    step = evaluate_standard_hook(
        hook_angle_deg=90.0,
        bar_diameter_mm=12.0,
        inner_bend_diameter_mm=48.0,
        straight_extension_mm=75.0,
        encloses_longitudinal_bar=False,
    )
    assert step.outcome is EvaluationOutcome.FAIL
    assert (
        step.diagnostics[0].code
        == "STANDARD_HOOK_NOT_ENCLOSING_LONGITUDINAL_BAR"
    )


def test_standard_hook_missing_enclosure_blocked() -> None:
    step = evaluate_standard_hook(
        hook_angle_deg=90.0,
        bar_diameter_mm=12.0,
        inner_bend_diameter_mm=48.0,
        straight_extension_mm=75.0,
        encloses_longitudinal_bar=None,
    )
    assert step.outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "MISSING_ENCLOSES_LONGITUDINAL_BAR"


def test_standard_hook_missing_geometry_blocked() -> None:
    step = evaluate_standard_hook(
        hook_angle_deg=90.0,
        bar_diameter_mm=None,
        inner_bend_diameter_mm=48.0,
        straight_extension_mm=75.0,
        encloses_longitudinal_bar=True,
    )
    assert step.outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "MISSING_BAR_DIAMETER"


def test_standard_hook_invalid_input() -> None:
    step = evaluate_standard_hook(
        hook_angle_deg=90.0,
        bar_diameter_mm=-5.0,
        inner_bend_diameter_mm=48.0,
        straight_extension_mm=75.0,
        encloses_longitudinal_bar=True,
    )
    assert step.outcome is EvaluationOutcome.INVALID_INPUT


# ============================================================================
# BG-TRANS-TORSION-TIE-STANDARD-HOOK-001 — Clause 9-21-6-2-7-الف standard branch
# ============================================================================

def test_torsion_tie_standard_hook_valid() -> None:
    step = evaluate_torsion_tie_standard_hook(
        hook_bar_diameter_mm=12.0,
        hook_inner_bend_diameter_mm=48.0,
        hook_straight_extension_mm=75.0,
        hook_engages_longitudinal_bar=True,
        bend_end_anchored_in_core_concrete=True,
    )
    assert step.outcome is EvaluationOutcome.PASS
    assert step.rule_id == "BG-TRANS-TORSION-TIE-STANDARD-HOOK-001"


def test_torsion_tie_standard_hook_invalid_geometry_fails() -> None:
    step = evaluate_torsion_tie_standard_hook(
        hook_bar_diameter_mm=12.0,
        hook_inner_bend_diameter_mm=47.0,  # < 4*12 = 48
        hook_straight_extension_mm=75.0,
        hook_engages_longitudinal_bar=True,
        bend_end_anchored_in_core_concrete=True,
    )
    assert step.outcome is EvaluationOutcome.FAIL
    assert (
        step.diagnostics[0].code
        == "TORSION_TIE_STANDARD_HOOK_GEOMETRY_NOT_SATISFIED"
    )


def test_torsion_tie_standard_hook_not_engaging_fails() -> None:
    step = evaluate_torsion_tie_standard_hook(
        hook_bar_diameter_mm=12.0,
        hook_inner_bend_diameter_mm=48.0,
        hook_straight_extension_mm=75.0,
        hook_engages_longitudinal_bar=False,
        bend_end_anchored_in_core_concrete=True,
    )
    assert step.outcome is EvaluationOutcome.FAIL
    assert (
        step.diagnostics[0].code
        == "TORSION_TIE_STANDARD_HOOK_NOT_ENGAGING_LONGITUDINAL_BAR"
    )


def test_torsion_tie_standard_hook_missing_geometry_blocked() -> None:
    step = evaluate_torsion_tie_standard_hook(
        hook_bar_diameter_mm=None,
        hook_inner_bend_diameter_mm=48.0,
        hook_straight_extension_mm=75.0,
        hook_engages_longitudinal_bar=True,
        bend_end_anchored_in_core_concrete=True,
    )
    assert step.outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED


def test_torsion_tie_standard_hook_missing_engagement_blocked() -> None:
    step = evaluate_torsion_tie_standard_hook(
        hook_bar_diameter_mm=12.0,
        hook_inner_bend_diameter_mm=48.0,
        hook_straight_extension_mm=75.0,
        hook_engages_longitudinal_bar=None,
        bend_end_anchored_in_core_concrete=True,
    )
    assert step.outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "MISSING_HOOK_ENGAGES_LONGITUDINAL_BAR"


def test_torsion_tie_seismic_and_standard_branches_are_distinct() -> None:
    # The seismic-hook option is a separate executable rule; the standard
    # branch does not re-implement it.
    seismic = evaluate_torsion_tie_seismic_hook(
        hook_bend_angle_deg=135.0,
        hook_straight_extension_mm=120.0,
        hook_bar_diameter_mm=20.0,
        hook_circular_dorgir=False,
        hook_engages_longitudinal_bar=True,
        bend_end_anchored_in_core_concrete=True,
    )
    assert seismic.outcome is EvaluationOutcome.PASS
    assert seismic.rule_id == "BG-TRANS-TORSION-TIE-SEISMIC-HOOK-001"
    assert (
        RULE_BG_TRANS_TORSION_TIE_SEISMIC_HOOK_001.rule_id
        != RULE_BG_TRANS_TORSION_TIE_STANDARD_HOOK_001.rule_id
    )


def test_torsion_tie_be_branch_stays_blocked() -> None:
    assert RULE_BG_TRANS_TORSION_TIE_PENDING.execution_allowed is False
    for mode in JurisdictionMode:
        dec = evaluate_rule_gate(
            "BG-TRANS-TORSION-TIE-PENDING", active_jurisdiction=mode
        )
        assert not dec.allowed


# ============================================================================
# BG-TRANS-WIRE-TIE-UTIE-001 — Clause 9-21-6-1-4
# ============================================================================

def test_wire_tie_utie_alef_valid() -> None:
    step = evaluate_wire_tie_utie(
        alternative=WireTieUtieAlternative.ALEF,
        wire_spacing_mm=50.0,
        wires_in_upper_part_of_utie=True,
    )
    assert step.outcome is EvaluationOutcome.PASS
    assert step.rule_id == "BG-TRANS-WIRE-TIE-UTIE-001"


def test_wire_tie_utie_alef_invalid_50mm_spacing() -> None:
    step = evaluate_wire_tie_utie(
        alternative=WireTieUtieAlternative.ALEF,
        wire_spacing_mm=60.0,  # not 50 mm
        wires_in_upper_part_of_utie=True,
    )
    assert step.outcome is EvaluationOutcome.FAIL
    assert step.diagnostics[0].code == "WIRE_TIE_UTIE_ALEF_SPACING_NOT_50MM"


def test_wire_tie_utie_alef_not_in_upper_part_fails() -> None:
    step = evaluate_wire_tie_utie(
        alternative=WireTieUtieAlternative.ALEF,
        wire_spacing_mm=50.0,
        wires_in_upper_part_of_utie=False,
    )
    assert step.outcome is EvaluationOutcome.FAIL
    assert step.diagnostics[0].code == "WIRE_TIE_UTIE_ALEF_NOT_IN_UPPER_PART"


def test_wire_tie_utie_be_valid_on_leg() -> None:
    # effective_depth 400 -> quarter = 100; wire1 80 < 100; wire2 40 < 80;
    # spacing 60 > 50; wire2 on leg -> no bend-dia condition.
    step = evaluate_wire_tie_utie(
        alternative=WireTieUtieAlternative.BE,
        effective_depth_mm=400.0,
        wire1_dist_from_compression_mm=80.0,
        wire2_dist_from_compression_mm=40.0,
        wire1_to_wire2_spacing_mm=60.0,
        wire2_on_hook=False,
    )
    assert step.outcome is EvaluationOutcome.PASS


def test_wire_tie_utie_be_valid_on_hook() -> None:
    step = evaluate_wire_tie_utie(
        alternative=WireTieUtieAlternative.BE,
        effective_depth_mm=400.0,
        wire1_dist_from_compression_mm=80.0,
        wire2_dist_from_compression_mm=40.0,
        wire1_to_wire2_spacing_mm=60.0,
        wire2_on_hook=True,
        bend_diameter_mm=64.0,  # >= 8*8 = 64
        tie_wire_diameter_mm=8.0,
    )
    assert step.outcome is EvaluationOutcome.PASS


def test_wire_tie_utie_be_invalid_quarter_depth() -> None:
    step = evaluate_wire_tie_utie(
        alternative=WireTieUtieAlternative.BE,
        effective_depth_mm=400.0,
        wire1_dist_from_compression_mm=120.0,  # >= 0.25*400 = 100
        wire2_dist_from_compression_mm=40.0,
        wire1_to_wire2_spacing_mm=60.0,
        wire2_on_hook=False,
    )
    assert step.outcome is EvaluationOutcome.FAIL
    assert (
        step.diagnostics[0].code
        == "WIRE_TIE_UTIE_BE_WIRE1_NOT_WITHIN_QUARTER_DEPTH"
    )


def test_wire_tie_utie_be_wire2_not_closer_fails() -> None:
    step = evaluate_wire_tie_utie(
        alternative=WireTieUtieAlternative.BE,
        effective_depth_mm=400.0,
        wire1_dist_from_compression_mm=80.0,
        wire2_dist_from_compression_mm=90.0,  # not < 80
        wire1_to_wire2_spacing_mm=60.0,
        wire2_on_hook=False,
    )
    assert step.outcome is EvaluationOutcome.FAIL
    assert (
        step.diagnostics[0].code
        == "WIRE_TIE_UTIE_BE_WIRE2_NOT_CLOSER_TO_COMPRESSION"
    )


def test_wire_tie_utie_be_invalid_50mm_spacing() -> None:
    step = evaluate_wire_tie_utie(
        alternative=WireTieUtieAlternative.BE,
        effective_depth_mm=400.0,
        wire1_dist_from_compression_mm=80.0,
        wire2_dist_from_compression_mm=40.0,
        wire1_to_wire2_spacing_mm=40.0,  # not > 50
        wire2_on_hook=False,
    )
    assert step.outcome is EvaluationOutcome.FAIL
    assert step.diagnostics[0].code == "WIRE_TIE_UTIE_BE_SPACING_NOT_ABOVE_50MM"


def test_wire_tie_utie_be_invalid_bend_diameter_below_8x() -> None:
    step = evaluate_wire_tie_utie(
        alternative=WireTieUtieAlternative.BE,
        effective_depth_mm=400.0,
        wire1_dist_from_compression_mm=80.0,
        wire2_dist_from_compression_mm=40.0,
        wire1_to_wire2_spacing_mm=60.0,
        wire2_on_hook=True,
        bend_diameter_mm=30.0,  # < 8*8 = 64
        tie_wire_diameter_mm=8.0,
    )
    assert step.outcome is EvaluationOutcome.FAIL
    assert step.diagnostics[0].code == "WIRE_TIE_UTIE_BE_BEND_DIA_BELOW_8X"


def test_wire_tie_utie_missing_alternative_blocked() -> None:
    step = evaluate_wire_tie_utie(
        alternative=None,
        wire_spacing_mm=50.0,
        wires_in_upper_part_of_utie=True,
    )
    assert step.outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "MISSING_ALTERNATIVE"


def test_wire_tie_utie_missing_geometry_blocked() -> None:
    step = evaluate_wire_tie_utie(
        alternative=WireTieUtieAlternative.ALEF,
        wire_spacing_mm=None,
        wires_in_upper_part_of_utie=True,
    )
    assert step.outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "MISSING_WIRE_SPACING"


# ============================================================================
# BG-TRANS-SPIRAL-SPLICE-LAP-SEL-001 — Clause 9-21-6-3-5-ب
# ============================================================================

def test_spiral_splice_lap_sel_fy_leq_420_valid() -> None:
    step = evaluate_spiral_splice_lap_sel(
        yield_stress_mpa=400.0,
        splice_bar_type=SpiralSpliceBarType.DEFORMED_BAR,
        coating_class=SpiralSpliceCoating.UNCOATED,
        end_condition=SpiralSpliceEndCondition.NO_HOOK,
        bar_diameter_mm=20.0,
    )
    assert step.outcome is EvaluationOutcome.COMPUTED
    assert step.rule_id == "BG-TRANS-SPIRAL-SPLICE-LAP-SEL-001"
    # Delegated length: max(48*20, 300) = 960 mm.
    assert step.final_result == 960.0


def test_spiral_splice_lap_sel_fy_boundary_420_valid() -> None:
    step = evaluate_spiral_splice_lap_sel(
        yield_stress_mpa=420.0,  # exactly the limit -> permitted
        splice_bar_type=SpiralSpliceBarType.DEFORMED_BAR,
        coating_class=SpiralSpliceCoating.UNCOATED,
        end_condition=SpiralSpliceEndCondition.NO_HOOK,
        bar_diameter_mm=20.0,
    )
    assert step.outcome is EvaluationOutcome.COMPUTED


def test_spiral_splice_lap_sel_fy_above_420_blocked() -> None:
    step = evaluate_spiral_splice_lap_sel(
        yield_stress_mpa=500.0,
        splice_bar_type=SpiralSpliceBarType.DEFORMED_BAR,
        coating_class=SpiralSpliceCoating.UNCOATED,
        end_condition=SpiralSpliceEndCondition.NO_HOOK,
        bar_diameter_mm=20.0,
    )
    assert step.outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "SPIRAL_SPLICE_LAP_FY_ABOVE_420"


def test_spiral_splice_lap_sel_delegates_length_matches_spiral_lap() -> None:
    # The lap length is delegated to BG-TRANS-SPIRAL-LAP-001 and NOT recomputed.
    sel = evaluate_spiral_splice_lap_sel(
        yield_stress_mpa=400.0,
        splice_bar_type=SpiralSpliceBarType.DEFORMED_BAR,
        coating_class=SpiralSpliceCoating.EPOXY,
        end_condition=SpiralSpliceEndCondition.NO_HOOK,
        bar_diameter_mm=5.0,  # 72*5 = 360, but floor 300 -> 360
    )
    direct = evaluate_spiral_lap_splice(
        splice_bar_type=SpiralSpliceBarType.DEFORMED_BAR,
        coating_class=SpiralSpliceCoating.EPOXY,
        end_condition=SpiralSpliceEndCondition.NO_HOOK,
        bar_diameter_mm=5.0,
    )
    assert sel.outcome is EvaluationOutcome.COMPUTED
    assert direct.outcome is EvaluationOutcome.COMPUTED
    assert sel.final_result == direct.final_result


def test_spiral_splice_lap_sel_300mm_floor_not_duplicated() -> None:
    # The 300 mm floor lives in BG-TRANS-SPIRAL-LAP-001; delegation returns it.
    step = evaluate_spiral_splice_lap_sel(
        yield_stress_mpa=400.0,
        splice_bar_type=SpiralSpliceBarType.PLAIN_BAR,
        coating_class=SpiralSpliceCoating.UNCOATED,
        end_condition=SpiralSpliceEndCondition.NO_HOOK,
        bar_diameter_mm=2.0,  # 72*2 = 144 < 300 -> 300
    )
    assert step.outcome is EvaluationOutcome.COMPUTED
    assert step.final_result == 300.0


def test_spiral_splice_lap_sel_missing_fy_blocked() -> None:
    step = evaluate_spiral_splice_lap_sel(
        yield_stress_mpa=None,
        splice_bar_type=SpiralSpliceBarType.DEFORMED_BAR,
        coating_class=SpiralSpliceCoating.UNCOATED,
        end_condition=SpiralSpliceEndCondition.NO_HOOK,
        bar_diameter_mm=20.0,
    )
    assert step.outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "MISSING_YIELD_STRESS"


def test_spiral_splice_lap_sel_missing_table_input_blocked() -> None:
    step = evaluate_spiral_splice_lap_sel(
        yield_stress_mpa=400.0,
        splice_bar_type=None,
        coating_class=SpiralSpliceCoating.UNCOATED,
        end_condition=SpiralSpliceEndCondition.NO_HOOK,
        bar_diameter_mm=20.0,
    )
    assert step.outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED


def test_welded_mechanical_splice_route_stays_blocked() -> None:
    assert RULE_BG_TRANS_SPIRAL_SPLICE_SEL_PENDING.execution_allowed is False
    assert "9-21-6-3-5-الف" in (
        RULE_BG_TRANS_SPIRAL_SPLICE_SEL_PENDING.clause_or_equation or ""
    )


# ============================================================================
# Registry / governance integration
# ============================================================================

@pytest.mark.parametrize("rule", H5_NEW_EXECUTABLE_RULES, ids=lambda r: r.rule_id)
def test_h5_new_rules_are_verified_code_rules_allowed_in_mabhas(rule) -> None:
    assert rule.status.value == "VERIFIED"
    assert rule.category.value == "CODE_RULE"
    assert rule.jurisdiction is JurisdictionMode.MABHAS_9_COMPLIANCE
    assert rule.execution_allowed is True
    assert rule.pdf_page is not None and rule.printed_page is not None
    assert rule.blocked_reason is None

    dec = evaluate_rule_gate(
        rule.rule_id, active_jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE
    )
    assert dec.allowed
    dec_most = evaluate_rule_gate(rule.rule_id, active_jurisdiction=MOST)
    assert not dec_most.allowed
    assert dec_most.blocked_outcome == EvaluationOutcome.JURISDICTION_BLOCKED


def test_h5_declared_dependencies_are_executable() -> None:
    ex = {r.rule_id for r in list_mabhas9_executable_rules()}
    assert RULE_BG_TRANS_TORSION_TIE_STANDARD_HOOK_001.dependencies == (
        "BG-TRANS-STANDARD-HOOK-001",
    )
    assert RULE_BG_TRANS_SPIRAL_SPLICE_LAP_SEL_001.dependencies == (
        "BG-TRANS-SPIRAL-LAP-001",
    )
    assert RULE_BG_TRANS_WIRE_TIE_UTIE_001.dependencies == ()
    for rule in H5_NEW_EXECUTABLE_RULES:
        for dep_id in rule.dependencies:
            assert dep_id in ex


def test_superseded_sentinels_correctly_split() -> None:
    # WIRE-TIE-PENDING now keeps only Clause 9-21-6-1-5 (9-21-6-1-4 promoted).
    wire_desc = RULE_BG_TRANS_WIRE_TIE_PENDING.description or ""
    assert "9-21-6-1-5" in (RULE_BG_TRANS_WIRE_TIE_PENDING.clause_or_equation or "")
    assert "BG-TRANS-WIRE-TIE-UTIE-001" in wire_desc
    # SPIRAL-SPLICE-SEL-PENDING now keeps only Clause 9-21-6-3-5-الف.
    splice_desc = RULE_BG_TRANS_SPIRAL_SPLICE_SEL_PENDING.description or ""
    assert "BG-TRANS-SPIRAL-SPLICE-LAP-SEL-001" in splice_desc
    # The still-blocked sentinels remain blocked.
    for rule in (
        RULE_BG_TRANS_TIE_ANCHOR_PENDING,
        RULE_BG_TRANS_WIRE_TIE_PENDING,
        RULE_BG_TRANS_TORSION_TIE_PENDING,
        RULE_BG_TRANS_WIRE_SUBST_PENDING,
        RULE_BG_TRANS_SPIRAL_SPLICE_SEL_PENDING,
    ):
        assert rule.execution_allowed is False
        assert rule.rule_id in {r.rule_id for r in list_blocked_rules()}


def test_no_duplicate_rule_ids() -> None:
    ids = [r.rule_id for r in _ALL_RULES_TUPLE]
    assert len(ids) == len(set(ids))


def test_executable_count_is_63() -> None:
    """Stage H.5 delivered 60 executable rules; H.7 added 2 and H.8 added 1."""
    assert len(list_mabhas9_executable_rules()) == 63
