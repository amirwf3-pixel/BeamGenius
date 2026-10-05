"""Focused tests for the Phase 2F Stage C Clause 9-21-3 development-length
evaluators (Mabhas 9, 1399 5th ed.).

Every expected numeric value was hand-verified against the visually verified
source equations/factors (Printed pp. 424-436 / PDF pp. 444-456; evidence
scan phase2f-source-442-472 @ df8067a) before being recorded here.
"""

from __future__ import annotations

import math

import pytest

from beamgenius.domain.enums import (
    AnchorConnectionClass,
    BarCoatingClass,
    CompressionConfinementClass,
    ConcreteWeightClass,
    EvaluationOutcome,
    JurisdictionMode,
    SteelGradeClass,
    WireSurfaceClass,
)
from beamgenius.engine.development_length_mabhas9 import (
    evaluate_dev_length_compression,
    evaluate_dev_length_headed,
    evaluate_dev_length_hooked,
    evaluate_dev_length_tension,
    evaluate_dev_length_tension_table,
    evaluate_dev_mech_anchorage,
    evaluate_dev_wire_deformed,
    evaluate_dev_wire_plain,
)
from beamgenius.registry.catalog import (
    RULE_BG_DEV_COMPRESSION_001,
    RULE_BG_DEV_LENGTH_HEADED_001,
    RULE_BG_DEV_LENGTH_HOOKED_001,
    RULE_BG_DEV_LENGTH_TENSION_001,
    RULE_BG_DEV_LENGTH_TENSION_TABLE_001,
    RULE_BG_DEV_MECH_ANCHOR_001,
    RULE_BG_DEV_WIRE_DEFORMED_001,
    RULE_BG_DEV_WIRE_PLAIN_001,
    list_mabhas9_executable_rules,
)

N = ConcreteWeightClass.NORMAL_WEIGHT
L = ConcreteWeightClass.LIGHTWEIGHT
UNCOATED = BarCoatingClass.UNCOATED_OR_GALVANIZED
EPOXY = BarCoatingClass.EPOXY_OR_DUAL_COATED

# No-reduction context bundle (all contexts explicitly absent)
NO_RED = dict(
    apply_excess_reinforcement_reduction=False,
)

NO_KTR = dict(apply_k_tr=False)



# ============================================================================
# BG-DEV-LENGTH-TENSION-001 — Eq. (9-21-1)
# ============================================================================

def _tension_base() -> dict:
    return dict(
        steel_grade=SteelGradeClass.S400,
        bar_diameter_mm=20.0,
        yield_stress_mpa=400.0,
        concrete_strength_mpa=25.0,
        concrete_weight_class=N,
        coating_class=UNCOATED,
        top_bar_placement=False,
        concrete_cover_mm=40.0,
        clear_spacing_mm=60.0,
        **NO_KTR,
        **NO_RED,
    )


def _reduction_case(as_required: float, as_provided: float) -> dict:
    """Tension equation base with a fully-populated permitted reduction."""
    case = _tension_base()
    case.update(
        apply_excess_reinforcement_reduction=True,
        as_required_mm2=as_required,
        as_provided_mm2=as_provided,
        at_non_continuous_support=False,
        yield_development_required=False,
        continuity_required=False,
        ductile_seismic_system=False,
        pile_head_anchorage=False,
    )
    return case


def test_tension_reference_value() -> None:
    # psi 1.0; c_b = min(50, 40) = 40; index = 40/20 = 2.0;
    # ld = (1/(1*2)) * (0.9*400/5) * 20 = 720
    step = evaluate_dev_length_tension(**_tension_base())
    assert step.outcome is EvaluationOutcome.COMPUTED
    assert step.final_result == pytest.approx(720.0)


def test_tension_top_epoxy_tight_psi_te_cap() -> None:
    # psi_t = 1.3, psi_e = 1.5 (cover 30 < 3*16) -> psi_te = 1.7; psi_s = 0.8
    # c_b = min(38, 58) = 38; index = 38/16 = 2.375
    step = evaluate_dev_length_tension(
        steel_grade=SteelGradeClass.S400, bar_diameter_mm=16.0,
        yield_stress_mpa=400.0, concrete_strength_mpa=25.0,
        concrete_weight_class=N, coating_class=EPOXY,
        top_bar_placement=True, concrete_cover_mm=30.0,
        clear_spacing_mm=100.0, **NO_KTR, **NO_RED)
    expected = min(1.3 * 1.5, 1.7) * 0.8 / (2.375) * (0.9 * 400 / 5.0) * 16.0
    assert step.outcome is EvaluationOutcome.COMPUTED
    assert step.final_result == pytest.approx(expected)
    assert step.intermediate_values["psi_te_capped"] == pytest.approx(1.7)


def test_tension_epoxy_other_case_psi_e_12() -> None:
    # cover 60 = 3*20 (NOT <) and clear 120 = 6*20 (NOT <) -> psi_e = 1.2
    step = evaluate_dev_length_tension(
        steel_grade=SteelGradeClass.S400, bar_diameter_mm=20.0,
        yield_stress_mpa=400.0, concrete_strength_mpa=25.0,
        concrete_weight_class=N, coating_class=EPOXY,
        top_bar_placement=False, concrete_cover_mm=60.0,
        clear_spacing_mm=120.0, **NO_KTR, **NO_RED)
    c_b = min(60.0 + 10.0, (120.0 + 20.0) / 2.0)
    index = min(c_b / 20.0, 2.5)  # confinement index capped at 2.5 (9-21-3-2-1)
    expected = (1.2 / index) * 72.0 * 20.0
    assert step.outcome is EvaluationOutcome.COMPUTED
    assert step.intermediate_values["psi_e"] == pytest.approx(1.2)
    assert step.final_result == pytest.approx(expected)


def test_tension_k_tr_used_and_index_capped_at_25() -> None:
    # Ktr = 40*100/(100*2) = 20 -> index = (40+20)/20 = 3.0 -> capped 2.5
    # ld = (1/2.5) * 72 * 20 = 576
    step = evaluate_dev_length_tension(
        steel_grade=SteelGradeClass.S400, bar_diameter_mm=20.0,
        yield_stress_mpa=400.0, concrete_strength_mpa=25.0,
        concrete_weight_class=N, coating_class=UNCOATED,
        top_bar_placement=False, concrete_cover_mm=40.0,
        clear_spacing_mm=60.0, apply_k_tr=True,
        transverse_area_mm2=100.0, transverse_spacing_mm=100.0,
        developed_bar_count=2, **NO_RED)
    assert step.outcome is EvaluationOutcome.COMPUTED
    assert step.final_result == pytest.approx(576.0)
    assert step.intermediate_values["confinement_index_capped"] == pytest.approx(2.5)


def test_tension_high_fc_clamped_and_lightweight_lambda() -> None:
    # fc = 100 -> sqrt(fc) clamped at 8.3; S500 -> psi_g 1.15; lambda 0.75
    # c_b = min(62.5, 50) = 50 -> index = 2.0
    step = evaluate_dev_length_tension(
        steel_grade=SteelGradeClass.S500, bar_diameter_mm=25.0,
        yield_stress_mpa=500.0, concrete_strength_mpa=100.0,
        concrete_weight_class=L, coating_class=UNCOATED,
        top_bar_placement=False, concrete_cover_mm=50.0,
        clear_spacing_mm=75.0, **NO_KTR, **NO_RED)
    expected = (1.15 / (0.75 * 2.0)) * (0.9 * 500 / 8.3) * 25.0
    assert step.outcome is EvaluationOutcome.COMPUTED
    assert step.intermediate_values["sqrt_fc_used"] == pytest.approx(8.3)
    assert step.final_result == pytest.approx(expected)


def test_tension_300mm_floor_active() -> None:
    step = evaluate_dev_length_tension(
        steel_grade=SteelGradeClass.S340, bar_diameter_mm=10.0,
        yield_stress_mpa=280.0, concrete_strength_mpa=60.0,
        concrete_weight_class=N, coating_class=UNCOATED,
        top_bar_placement=False, concrete_cover_mm=30.0,
        clear_spacing_mm=30.0, **NO_KTR, **NO_RED)
    assert step.outcome is EvaluationOutcome.COMPUTED
    assert step.final_result == pytest.approx(300.0)
    assert step.intermediate_values["ld_equation_mm"] < 300.0


def test_tension_excess_reduction_permitted() -> None:
    case = _reduction_case(3000.0, 4000.0)
    step = evaluate_dev_length_tension(**case)
    assert step.outcome is EvaluationOutcome.COMPUTED
    assert step.final_result == pytest.approx(720.0 * 0.75)


def test_tension_excess_reduction_floor_preserved() -> None:
    step = evaluate_dev_length_tension(**_reduction_case(800.0, 4000.0))
    assert step.outcome is EvaluationOutcome.COMPUTED
    assert step.final_result == pytest.approx(300.0)


@pytest.mark.parametrize(
    "field",
    ["at_non_continuous_support", "yield_development_required",
     "continuity_required", "ductile_seismic_system", "pile_head_anchorage"],
)
def test_tension_reduction_blocked_in_prohibited_contexts(field: str) -> None:
    case = _reduction_case(3000.0, 4000.0)
    case[field] = True
    step = evaluate_dev_length_tension(**case)
    assert step.outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "PROHIBITED_EXCESS_REDUCTION_CONTEXT"


def test_tension_reduction_ratio_above_one_is_invalid() -> None:
    step = evaluate_dev_length_tension(**_reduction_case(4000.0, 3000.0))
    assert step.outcome is EvaluationOutcome.INVALID_INPUT


def test_tension_missing_inputs_blocked() -> None:
    step = evaluate_dev_length_tension()
    assert step.outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    codes = {d.code for d in step.diagnostics}
    assert "MISSING_STEEL_GRADE" in codes
    assert "MISSING_BAR_DIAMETER_MM" in codes


def test_tension_malformed_inputs_invalid() -> None:
    base = _tension_base()
    for bad in (0.0, -20.0, float("nan"), float("inf")):
        case = dict(base)
        case["bar_diameter_mm"] = bad
        step = evaluate_dev_length_tension(**case)
        assert step.outcome is EvaluationOutcome.INVALID_INPUT


def test_tension_wrong_enum_type_invalid() -> None:
    base = _tension_base()
    case = dict(base)
    case["steel_grade"] = "S400"  # wrong type: typed enum required
    step = evaluate_dev_length_tension(**case)
    assert step.outcome is EvaluationOutcome.INVALID_INPUT


def test_tension_k_tr_missing_subinputs_blocked() -> None:
    base = _tension_base()
    case = dict(base)
    case["apply_k_tr"] = True
    step = evaluate_dev_length_tension(**case)
    assert step.outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    codes = {d.code for d in step.diagnostics}
    assert "MISSING_TRANSVERSE_AREA_MM2" in codes


def test_tension_jurisdiction_gate_mostofinejad_mode_blocked() -> None:
    step = evaluate_dev_length_tension(
        **_tension_base(),
        jurisdiction_mode=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY)
    assert step.outcome is EvaluationOutcome.JURISDICTION_BLOCKED


# ============================================================================
# BG-DEV-LENGTH-TENSION-TABLE-001 — Table 9-21-4
# ============================================================================

def _table_base() -> dict:
    return dict(
        steel_grade=SteelGradeClass.S400,
        bar_diameter_mm=16.0,
        yield_stress_mpa=400.0,
        concrete_strength_mpa=25.0,
        concrete_weight_class=N,
        coating_class=UNCOATED,
        top_bar_placement=False,
        concrete_cover_mm=40.0,
        clear_spacing_mm=60.0,
        min_code_ties_provided_along_ld=True,
        **NO_RED,
    )


def test_table_confined_small_db_divisor_21() -> None:
    # clear 60 >= db 16 AND ties -> confined; db<20 -> divisor 2.1
    # ld = 1*400/(2.1*5) * 16 = 609.52
    step = evaluate_dev_length_tension_table(**_table_base())
    assert step.outcome is EvaluationOutcome.COMPUTED
    assert step.intermediate_values["table_row_is_confined"] == 1.0
    assert step.final_result == pytest.approx(400.0 / (2.1 * 5.0) * 16.0)


def test_table_confined_large_db_divisor_17() -> None:
    case = dict(_table_base())
    case["bar_diameter_mm"] = 25.0
    case["clear_spacing_mm"] = 55.0  # >= 2*25 AND cover 40 >= 25 -> confined
    step = evaluate_dev_length_tension_table(**case)
    assert step.outcome is EvaluationOutcome.COMPUTED
    assert step.final_result == pytest.approx(400.0 / (1.7 * 5.0) * 25.0)


def test_table_other_row_divisor_11() -> None:
    case = dict(_table_base())
    case["bar_diameter_mm"] = 25.0
    case["clear_spacing_mm"] = 30.0  # < 2*db and ties required missing later
    case["min_code_ties_provided_along_ld"] = False
    step = evaluate_dev_length_tension_table(**case)
    assert step.outcome is EvaluationOutcome.COMPUTED
    assert step.intermediate_values["table_row_is_confined"] == 0.0
    assert step.intermediate_values["table_divisor"] == pytest.approx(1.1)
    assert step.final_result == pytest.approx(400.0 / (1.1 * 5.0) * 25.0)


def test_table_other_row_small_db_divisor_14() -> None:
    case = dict(_table_base())
    case["min_code_ties_provided_along_ld"] = False
    case["clear_spacing_mm"] = 18.0  # 18 >= db(16) but no ties, 18 < 2*16
    step = evaluate_dev_length_tension_table(**case)
    assert step.outcome is EvaluationOutcome.COMPUTED
    assert step.intermediate_values["table_divisor"] == pytest.approx(1.4)
    assert step.final_result == pytest.approx(400.0 / (1.4 * 5.0) * 16.0)


def test_table_s520_top_barFactors() -> None:
    step = evaluate_dev_length_tension_table(
        steel_grade=SteelGradeClass.S520, bar_diameter_mm=20.0,
        yield_stress_mpa=500.0, concrete_strength_mpa=30.0,
        concrete_weight_class=N, coating_class=UNCOATED,
        top_bar_placement=True, concrete_cover_mm=40.0,
        clear_spacing_mm=55.0, min_code_ties_provided_along_ld=True,
        **NO_RED)
    expected = (1.3 * 1.15) * 500.0 / (1.7 * math.sqrt(30.0)) * 20.0
    assert step.outcome is EvaluationOutcome.COMPUTED
    assert step.final_result == pytest.approx(expected)


def test_table_300mm_floor_and_reduction_floor() -> None:
    case = dict(_table_base())
    case["yield_stress_mpa"] = 190.0  # ld = 190/(2.1*5)*16 = 289.5 < 300
    step = evaluate_dev_length_tension_table(**case)
    assert step.outcome is EvaluationOutcome.COMPUTED
    assert step.final_result == pytest.approx(300.0)
    red = dict(case)
    red.update(apply_excess_reinforcement_reduction=True,
               as_required_mm2=100.0, as_provided_mm2=1000.0,
               at_non_continuous_support=False, yield_development_required=False,
               continuity_required=False, ductile_seismic_system=False,
               pile_head_anchorage=False)
    step2 = evaluate_dev_length_tension_table(**red)
    assert step2.final_result == pytest.approx(300.0)


# ============================================================================
# BG-DEV-LENGTH-HOOKED-001 — Eq. (9-21-3)
# ============================================================================

def _hooked_base() -> dict:
    return dict(
        bar_diameter_mm=20.0,
        yield_stress_mpa=400.0,
        concrete_strength_mpa=25.0,
        concrete_weight_class=N,
        coating_class=UNCOATED,
        a_th_mm2=100.0,
        a_hs_mm2=200.0,
        anchored_bar_clear_spacing_mm=140.0,  # > 6*20 = 120
        anchored_in_column_core=False,
        side_cover_normal_to_hook_plane_mm=70.0,
    )


def test_hooked_reference_value() -> None:
    # psi_r = 1.0 (db<=34, ath 100 >= 0.4*200, spacing > 6db), psi_o = 1.25
    # psi_c = 25/105+0.6 = 0.838095
    step = evaluate_dev_length_hooked(**_hooked_base())
    psi_c = 25.0 / 105.0 + 0.6
    expected = (1.25 * psi_c) * (0.043 * 400 / 5.0) * 20.0 ** 1.5
    assert step.outcome is EvaluationOutcome.COMPUTED
    assert step.final_result == pytest.approx(expected)
    assert step.intermediate_values["psi_r"] == pytest.approx(1.0)


def test_hooked_psi_r_16_when_not_confined() -> None:
    case = dict(_hooked_base())
    case["anchored_bar_clear_spacing_mm"] = 50.0  # < 6*20
    step = evaluate_dev_length_hooked(**case)
    psi_c = 25.0 / 105.0 + 0.6
    expected = 1.6 * 1.25 * psi_c * (0.043 * 400 / 5.0) * 20.0 ** 1.5
    assert step.outcome is EvaluationOutcome.COMPUTED
    assert step.intermediate_values["psi_r"] == pytest.approx(1.6)
    assert step.final_result == pytest.approx(expected)


def test_hooked_psi_o_10_column_core_qualification() -> None:
    case = dict(_hooked_base())
    case["anchored_in_column_core"] = True
    case["side_cover_normal_to_hook_plane_mm"] = 66.0  # > 65
    step = evaluate_dev_length_hooked(**case)
    assert step.intermediate_values["psi_o"] == pytest.approx(1.0)
    case2 = dict(_hooked_base())
    case2["anchored_in_column_core"] = True
    case2["side_cover_normal_to_hook_plane_mm"] = 64.0  # <= 65 and <= 6*20
    step2 = evaluate_dev_length_hooked(**case2)
    assert step2.intermediate_values["psi_o"] == pytest.approx(1.25)
    case3 = dict(_hooked_base())
    case3["anchored_in_column_core"] = True
    case3["side_cover_normal_to_hook_plane_mm"] = 121.0  # > 6*20 via ratio
    step3 = evaluate_dev_length_hooked(**case3)
    assert step3.intermediate_values["psi_o"] == pytest.approx(1.0)


def test_hooked_psi_c_factor_and_floor() -> None:
    case = dict(_hooked_base())
    case["bar_diameter_mm"] = 10.0
    case["yield_stress_mpa"] = 200.0
    step = evaluate_dev_length_hooked(**case)
    assert step.outcome is EvaluationOutcome.COMPUTED
    assert step.final_result == pytest.approx(150.0)
    assert step.intermediate_values["ld_floor_mm"] == pytest.approx(150.0)
    case_fc = dict(_hooked_base())
    case_fc["concrete_strength_mpa"] = 42.0  # psi_c = 1.0 at exactly 42
    step_fc = evaluate_dev_length_hooked(**case_fc)
    assert step_fc.intermediate_values["psi_c"] == pytest.approx(1.0)


def test_hooked_epoxy_psi_e_12() -> None:
    case = dict(_hooked_base())
    case["coating_class"] = EPOXY
    step = evaluate_dev_length_hooked(**case)
    assert step.intermediate_values["psi_e"] == pytest.approx(1.2)


def test_hooked_missing_and_malformed() -> None:
    step = evaluate_dev_length_hooked()
    assert step.outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    case = dict(_hooked_base())
    case["a_hs_mm2"] = float("nan")
    step2 = evaluate_dev_length_hooked(**case)
    assert step2.outcome is EvaluationOutcome.INVALID_INPUT


# ============================================================================
# BG-DEV-LENGTH-HEADED-001 — Eq. (9-21-4)
# ============================================================================

def _headed_base() -> dict:
    return dict(
        bar_diameter_mm=20.0,
        yield_stress_mpa=400.0,
        concrete_strength_mpa=25.0,
        concrete_weight_class=N,
        coating_class=UNCOATED,
        head_bearing_area_mm2=2000.0,  # >= 4 * pi*20^2/4 = 1256.6
        concrete_cover_mm=40.0,  # = 2*db (limit not exceeded)
        bar_spacing_cc_mm=80.0,  # >= 3*20 = 60
        anchored_in_column_core=True,
        side_cover_normal_to_head_plane_mm=70.0,
        connection_class=AnchorConnectionClass.BEAM_COLUMN_JOINT,
        a_tt_mm2=100.0,
        a_ts_mm2=200.0,  # 100 >= 0.3*200 -> qualified
        anchored_bar_clear_spacing_mm=30.0,
    )


def test_headed_reference_value() -> None:
    step = evaluate_dev_length_headed(**_headed_base())
    psi_c = 25.0 / 105.0 + 0.6
    expected = psi_c * (0.032 * 400 / 5.0) * 20.0 ** 1.5
    assert step.outcome is EvaluationOutcome.COMPUTED
    assert step.intermediate_values["psi_p"] == pytest.approx(1.0)
    assert step.intermediate_values["psi_o"] == pytest.approx(1.0)
    assert step.final_result == pytest.approx(expected)


def test_headed_psi_p_16_other_connection() -> None:
    case = dict(_headed_base())
    case["connection_class"] = AnchorConnectionClass.ANY_OTHER
    step = evaluate_dev_length_headed(**case)
    assert step.intermediate_values["psi_p"] == pytest.approx(1.6)
    psi_c = 25.0 / 105.0 + 0.6
    expected = 1.6 * psi_c * (0.032 * 400 / 5.0) * 20.0 ** 1.5
    assert step.final_result == pytest.approx(expected)


def test_headed_psi_p_spacing_alternative() -> None:
    case = dict(_headed_base())
    case["connection_class"] = AnchorConnectionClass.ANY_OTHER
    case["anchored_bar_clear_spacing_mm"] = 121.0  # > 6*20
    step = evaluate_dev_length_headed(**case)
    assert step.intermediate_values["psi_p"] == pytest.approx(1.0)


def test_headed_joint_area_inputs_required_when_beam_column() -> None:
    case = dict(_headed_base())
    case["a_ts_mm2"] = None
    step = evaluate_dev_length_headed(**case)
    assert step.outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    codes = {d.code for d in step.diagnostics}
    assert "MISSING_A_TS_MM2" in codes


@pytest.mark.parametrize(
    "override,fail_code",
    [
        ({"bar_diameter_mm": 34.1}, "HEADED_BAR_DIAMETER_EXCEEDS_LIMIT"),
        ({"concrete_weight_class": L, "side_cover_normal_to_head_plane_mm": 70.0,
          }, "HEADED_BAR_REQUIRES_NORMAL_WEIGHT_CONCRETE"),
        ({"head_bearing_area_mm2": 1000.0}, "HEADED_BEARING_AREA_BELOW_MINIMUM"),
        ({"concrete_cover_mm": 39.9}, "HEADED_COVER_BELOW_LIMIT"),
        ({"bar_spacing_cc_mm": 59.9}, "HEADED_SPACING_BELOW_LIMIT"),
    ],
)
def test_headed_applicability_limits_fail(override: dict, fail_code: str) -> None:
    case = dict(_headed_base())
    case.update(override)
    step = evaluate_dev_length_headed(**case)
    assert step.outcome is EvaluationOutcome.FAIL
    codes = {d.code for d in step.diagnostics}
    assert fail_code in codes


def test_headed_floor_and_weight_lambda_normal_only() -> None:
    case = dict(_headed_base())
    case["yield_stress_mpa"] = 200.0
    case["bar_diameter_mm"] = 10.0
    case["head_bearing_area_mm2"] = 400.0  # >= 4*pi*100/4 = 314.16
    case["concrete_cover_mm"] = 20.0
    case["bar_spacing_cc_mm"] = 30.0
    step = evaluate_dev_length_headed(**case)
    assert step.outcome is EvaluationOutcome.COMPUTED
    assert step.final_result == pytest.approx(max(80.0, 150.0))
    assert step.final_result == pytest.approx(150.0)


# ============================================================================
# BG-DEV-MECH-ANCHOR-001 — Clause 9-21-3-5 gate
# ============================================================================

def test_mech_anchor_all_true_passes() -> None:
    step = evaluate_dev_mech_anchorage(
        device_supplies_yield_capacity=True,
        designer_engineer_approved=True,
        approved_test_results_present=True)
    assert step.outcome is EvaluationOutcome.PASS


@pytest.mark.parametrize(
    "field,code",
    [
        ("device_supplies_yield_capacity", "MECH_ANCHOR_WITHOUT_YIELD_CAPACITY"),
        ("designer_engineer_approved", "MECH_ANCHOR_WITHOUT_ENGINEER_APPROVAL"),
        ("approved_test_results_present", "MECH_ANCHOR_WITHOUT_APPROVED_TESTS"),
    ],
)
def test_mech_anchor_single_false_fails(field: str, code: str) -> None:
    kwargs = dict(device_supplies_yield_capacity=True,
                  designer_engineer_approved=True,
                  approved_test_results_present=True)
    kwargs[field] = False
    step = evaluate_dev_mech_anchorage(**kwargs)
    assert step.outcome is EvaluationOutcome.FAIL
    assert step.diagnostics[0].code == code


def test_mech_anchor_missing_blocked() -> None:
    step = evaluate_dev_mech_anchorage()
    assert step.outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    codes = {d.code for d in step.diagnostics}
    assert "MISSING_DEVICE_SUPPLIES_YIELD_CAPACITY" in codes


# ============================================================================
# BG-DEV-WIRE-DEFORMED-001 — Eq. (9-21-5)
# ============================================================================

def _wire_def_base() -> dict:
    return dict(
        bar_diameter_mm=10.0,
        yield_stress_mpa=500.0,
        concrete_strength_mpa=25.0,
        concrete_weight_class=N,
        wire_surface_class=WireSurfaceClass.UNCOATED,
        wire_is_deformed=True,
        top_bar_placement=False,
        concrete_cover_mm=30.0,
        clear_spacing_mm=50.0,
        cross_wire_in_development=True,
        cross_wire_distance_from_critical_mm=60.0,
        anchored_wire_spacing_mm=150.0,
        **NO_KTR,
        **NO_RED,
    )


def test_wire_def_psi_w_greater_of_two_refs() -> None:
    # psi_w = max(min((500-240)/500, 1), min(50/150, 1)) = max(0.52, 0.333) = 0.52
    # c_b = min(35, 30) = 30 -> index 3.0 capped 2.5; psi_s = 0.8
    # ld = (0.8*0.52)/(2.5) * (0.9*500/5)*10 = 149.76 -> floor 200
    step = evaluate_dev_wire_deformed(**_wire_def_base())
    assert step.intermediate_values["psi_w"] == pytest.approx(0.52)
    assert step.outcome is EvaluationOutcome.COMPUTED
    assert step.final_result == pytest.approx(200.0)


def test_wire_def_psi_w_5db_over_s_governs() -> None:
    case = dict(_wire_def_base())
    case["yield_stress_mpa"] = 300.0  # (300-240)/300 = 0.20 < 5*10/150 = 0.3333
    step = evaluate_dev_wire_deformed(**case)
    assert step.intermediate_values["psi_w"] == pytest.approx(1.0 / 3.0)


def test_wire_def_no_cross_wire_psi_w_1() -> None:
    case = dict(_wire_def_base())
    case["cross_wire_in_development"] = False
    case["cross_wire_distance_from_critical_mm"] = None
    case["anchored_wire_spacing_mm"] = None
    step = evaluate_dev_wire_deformed(**case)
    assert step.intermediate_values["psi_w"] == pytest.approx(1.0)
    expected = (0.8 * 1.0 / 2.5) * (0.9 * 500 / 5.0) * 10.0
    assert step.final_result == pytest.approx(expected)


def test_wire_def_cross_wire_below_50mm_psi_w_1() -> None:
    case = dict(_wire_def_base())
    case["cross_wire_distance_from_critical_mm"] = 30.0
    case["anchored_wire_spacing_mm"] = None
    step = evaluate_dev_wire_deformed(**case)
    assert step.intermediate_values["psi_w"] == pytest.approx(1.0)


def test_wire_def_inconsistent_cross_wire_inputs_invalid() -> None:
    case = dict(_wire_def_base())
    case["cross_wire_in_development"] = False
    step = evaluate_dev_wire_deformed(**case)
    assert step.outcome is EvaluationOutcome.INVALID_INPUT
    assert step.diagnostics[0].code == "INCONSISTENT_CROSS_WIRE_INPUTS"


@pytest.mark.parametrize(
    "override",
    [
        {"bar_diameter_mm": 16.01},
        {"wire_is_deformed": False},
        {"wire_surface_class": WireSurfaceClass.GALVANIZED},
    ],
)
def test_wire_def_route_to_3_7_not_applicable(override: dict) -> None:
    case = dict(_wire_def_base())
    case.update(override)
    step = evaluate_dev_wire_deformed(**case)
    assert step.outcome is EvaluationOutcome.NOT_APPLICABLE
    assert "9-21-3-7" in step.message


def test_wire_def_epoxy_permission_and_table_default() -> None:
    case = dict(_wire_def_base())
    case["wire_surface_class"] = WireSurfaceClass.EPOXY
    step = evaluate_dev_wire_deformed(**case)
    assert step.outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED  # permission flag missing
    case["epoxy_psi_e_unit_permission"] = True
    step = evaluate_dev_wire_deformed(**case)
    assert step.intermediate_values["psi_e"] == pytest.approx(1.0)
    case["epoxy_psi_e_unit_permission"] = False
    case["concrete_cover_mm"] = 20.0  # < 3*10 -> psi_e = 1.5 branch
    step = evaluate_dev_wire_deformed(**case)
    assert step.intermediate_values["psi_e"] == pytest.approx(1.5)


def test_wire_def_db16_boundary_applicable() -> None:
    case = dict(_wire_def_base())
    case["bar_diameter_mm"] = 16.0
    case["anchored_wire_spacing_mm"] = 150.0
    step = evaluate_dev_wire_deformed(**case)
    assert step.outcome is EvaluationOutcome.COMPUTED


# ============================================================================
# BG-DEV-WIRE-PLAIN-001 — Eq. (9-21-7)
# ============================================================================

def test_wire_plain_reference_floors_govern() -> None:
    # ld = 3.3*400/5 * (pi*8^2/4 / 100) = 264 * 0.50265 = 132.7 -> max(150, 150)
    step = evaluate_dev_wire_plain(
        bar_diameter_mm=8.0, anchored_wire_spacing_mm=100.0,
        yield_stress_mpa=400.0, concrete_strength_mpa=25.0,
        concrete_weight_class=N, cross_wires_in_development_length=2,
        **NO_RED)
    assert step.outcome is EvaluationOutcome.COMPUTED
    assert step.final_result == pytest.approx(150.0)


def test_wire_plain_s_plus_50_floor() -> None:
    step = evaluate_dev_wire_plain(
        bar_diameter_mm=8.0, anchored_wire_spacing_mm=200.0,
        yield_stress_mpa=400.0, concrete_strength_mpa=25.0,
        concrete_weight_class=N, cross_wires_in_development_length=2,
        **NO_RED)
    assert step.outcome is EvaluationOutcome.COMPUTED
    assert step.final_result == pytest.approx(250.0)
    assert step.intermediate_values["ld_floor_mm"] == pytest.approx(250.0)


def test_wire_plain_equation_governs_and_lambda_lightweight() -> None:
    step = evaluate_dev_wire_plain(
        bar_diameter_mm=6.0, anchored_wire_spacing_mm=25.0,
        yield_stress_mpa=400.0, concrete_strength_mpa=25.0,
        concrete_weight_class=L, cross_wires_in_development_length=2,
        **NO_RED)
    a_b = math.pi * 36.0 / 4.0
    expected = (3.3 * 400 / (0.75 * 5.0)) * (a_b / 25.0)
    assert step.outcome is EvaluationOutcome.COMPUTED
    assert step.final_result == pytest.approx(expected)
    assert expected > 150.0


def test_wire_plain_fewer_than_two_cross_wires_fails() -> None:
    step = evaluate_dev_wire_plain(
        bar_diameter_mm=8.0, anchored_wire_spacing_mm=100.0,
        yield_stress_mpa=400.0, concrete_strength_mpa=25.0,
        concrete_weight_class=N, cross_wires_in_development_length=1,
        **NO_RED)
    assert step.outcome is EvaluationOutcome.FAIL
    assert step.diagnostics[0].code == "PLAIN_WIRE_FEWER_THAN_TWO_CROSS_WIRES"


def test_wire_plain_reduction_preserves_both_floors() -> None:
    step = evaluate_dev_wire_plain(
        bar_diameter_mm=6.0, anchored_wire_spacing_mm=25.0,
        yield_stress_mpa=400.0, concrete_strength_mpa=25.0,
        concrete_weight_class=N, cross_wires_in_development_length=2,
        apply_excess_reinforcement_reduction=True,
        as_required_mm2=100.0, as_provided_mm2=1000.0,
        at_non_continuous_support=False, yield_development_required=False,
        continuity_required=False, ductile_seismic_system=False,
        pile_head_anchorage=False)
    assert step.outcome is EvaluationOutcome.COMPUTED
    assert step.final_result == pytest.approx(max(150.0, 75.0))


# ============================================================================
# BG-DEV-LENGTH-COMPRESSION-001 — Clause 9-21-3-8
# ============================================================================

def _comp_base() -> dict:
    return dict(
        bar_diameter_mm=20.0,
        yield_stress_mpa=400.0,
        concrete_strength_mpa=25.0,
        concrete_weight_class=N,
        confinement_tie_class=CompressionConfinementClass.NONE,
        **NO_RED,
    )


def test_compression_reference_max_of_two_terms() -> None:
    # term a = 1.0*0.24*400/5*20 = 384; term b = 0.043*400*20 = 344 -> 384
    step = evaluate_dev_length_compression(**_comp_base())
    assert step.outcome is EvaluationOutcome.COMPUTED
    assert step.final_result == pytest.approx(384.0)
    assert step.intermediate_values["psi_r"] == pytest.approx(1.0)


def test_compression_spiral_psi_r_075() -> None:
    case = dict(_comp_base())
    case["confinement_tie_class"] = CompressionConfinementClass.SPIRAL
    step = evaluate_dev_length_compression(**case)
    assert step.intermediate_values["psi_r"] == pytest.approx(0.75)
    assert step.final_result == pytest.approx(0.75 * 384.0)


@pytest.mark.parametrize(
    "diameter,spacing,psi_r",
    [
        (8.0, 80.0, 0.75),   # > 6 mm @ < 100 mm qualifies
        (6.0, 80.0, 1.0),    # diameter not > 6 mm
        (8.0, 100.0, 1.0),   # spacing not < 100 mm
    ],
)
def test_compression_circular_tie_boundaries(diameter: float, spacing: float,
                                             psi_r: float) -> None:
    step = evaluate_dev_length_compression(
        bar_diameter_mm=20.0, yield_stress_mpa=400.0,
        concrete_strength_mpa=25.0, concrete_weight_class=N,
        confinement_tie_class=CompressionConfinementClass.CIRCULAR_TIE,
        confinement_tie_diameter_mm=diameter,
        confinement_tie_spacing_mm=spacing, **NO_RED)
    assert step.intermediate_values["psi_r"] == pytest.approx(psi_r)


def test_compression_dorgir_qualified() -> None:
    step = evaluate_dev_length_compression(
        bar_diameter_mm=20.0, yield_stress_mpa=400.0,
        concrete_strength_mpa=25.0, concrete_weight_class=N,
        confinement_tie_class=CompressionConfinementClass.DORGIR_9_21_6_4,
        confinement_tie_spacing_mm=99.0, **NO_RED)
    assert step.intermediate_values["psi_r"] == pytest.approx(0.75)
    step2 = evaluate_dev_length_compression(
        bar_diameter_mm=20.0, yield_stress_mpa=400.0,
        concrete_strength_mpa=25.0, concrete_weight_class=N,
        confinement_tie_class=CompressionConfinementClass.DORGIR_9_21_6_4,
        confinement_tie_spacing_mm=100.0, **NO_RED)
    assert step2.intermediate_values["psi_r"] == pytest.approx(1.0)


def test_compression_wire_tie_branch_verify_pending_blocked() -> None:
    step = evaluate_dev_length_compression(
        bar_diameter_mm=20.0, yield_stress_mpa=400.0,
        concrete_strength_mpa=25.0, concrete_weight_class=N,
        confinement_tie_class=CompressionConfinementClass.WIRE_TIE,
        confinement_tie_diameter_mm=14.0, confinement_tie_spacing_mm=80.0,
        **NO_RED)
    assert step.outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "VERIFY_PENDING_CONFINEMENT_TIE_CLASS"


def test_compression_200mm_floor() -> None:
    step = evaluate_dev_length_compression(
        bar_diameter_mm=10.0, yield_stress_mpa=400.0,
        concrete_strength_mpa=25.0, concrete_weight_class=N,
        confinement_tie_class=CompressionConfinementClass.SPIRAL, **NO_RED)
    # term a = 0.75*0.24*400/5*10 = 144 < 200
    assert step.final_result == pytest.approx(200.0)


def test_compression_reduction_applied_and_floor_preserved() -> None:
    step = evaluate_dev_length_compression(
        bar_diameter_mm=20.0, yield_stress_mpa=400.0,
        concrete_strength_mpa=25.0, concrete_weight_class=N,
        confinement_tie_class=CompressionConfinementClass.NONE,
        apply_excess_reinforcement_reduction=True,
        as_required_mm2=640.0, as_provided_mm2=800.0,
        at_non_continuous_support=False, yield_development_required=False,
        continuity_required=False, ductile_seismic_system=False,
        pile_head_anchorage=False)
    assert step.final_result == pytest.approx(384.0 * 0.8)
    step2 = evaluate_dev_length_compression(
        bar_diameter_mm=20.0, yield_stress_mpa=400.0,
        concrete_strength_mpa=25.0, concrete_weight_class=N,
        confinement_tie_class=CompressionConfinementClass.NONE,
        apply_excess_reinforcement_reduction=True,
        as_required_mm2=100.0, as_provided_mm2=800.0,
        at_non_continuous_support=False, yield_development_required=False,
        continuity_required=False, ductile_seismic_system=False,
        pile_head_anchorage=False)
    assert step2.final_result == pytest.approx(200.0)


def test_compression_missing_confinement_inputs_blocked() -> None:
    step = evaluate_dev_length_compression(**_comp_base())
    assert step.outcome is EvaluationOutcome.COMPUTED
    case = dict(_comp_base())
    case["confinement_tie_class"] = CompressionConfinementClass.CIRCULAR_TIE
    step2 = evaluate_dev_length_compression(**case)
    assert step2.outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    codes = {d.code for d in step2.diagnostics}
    assert "MISSING_CONFINEMENT_TIE_SPACING_MM" in codes


# ============================================================================
# Registry & traceability invariants for all Stage C rules
# ============================================================================

def test_all_stage_c_rules_registered_executable_and_metadata() -> None:
    stage_c = (
        RULE_BG_DEV_LENGTH_TENSION_001,
        RULE_BG_DEV_LENGTH_TENSION_TABLE_001,
        RULE_BG_DEV_LENGTH_HOOKED_001,
        RULE_BG_DEV_LENGTH_HEADED_001,
        RULE_BG_DEV_MECH_ANCHOR_001,
        RULE_BG_DEV_WIRE_DEFORMED_001,
        RULE_BG_DEV_WIRE_PLAIN_001,
        RULE_BG_DEV_COMPRESSION_001,
    )
    executable_ids = {r.rule_id for r in list_mabhas9_executable_rules()}
    for rule in stage_c:
        assert rule.rule_id in executable_ids
        assert rule.status.value == "VERIFIED"
        assert rule.category.value == "CODE_RULE"
        assert rule.jurisdiction.value == "MABHAS_9_COMPLIANCE"
        assert rule.execution_allowed is True
        assert isinstance(rule.pdf_page, int)
        assert isinstance(rule.printed_page, int)
        # Canonical Stage C window: Printed 424-436 / PDF 444-456 (+20 offset)
        assert 424 <= rule.printed_page <= 436
        assert rule.pdf_page - rule.printed_page == 20
        assert "9-21-3" in rule.clause_or_equation


def test_trace_carries_rule_reference_and_pages() -> None:
    step = evaluate_dev_length_tension(**_tension_base())
    assert step.rule_reference is RULE_BG_DEV_LENGTH_TENSION_001
    assert step.pdf_page == 445
    assert step.printed_page == 425
    assert step.clause_or_equation.startswith("Clause 9-21-3")
    assert step.unit == "mm"
    assert step.rule_reference.description


def test_blocked_never_passes_gate_example() -> None:
    # Missing inputs -> BLOCKED; BLOCKED outcome can never be PASS.
    step = evaluate_dev_length_compression()
    assert step.outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.final_result is None
