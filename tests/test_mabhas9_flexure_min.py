"""Tests for Mabhas 9 Minimum Flexural Reinforcement (BG-FLEX-MIN-001)."""

from __future__ import annotations

import math

import pytest

from beamgenius.domain import (
    BeamGeometry,
    ConcreteMaterial,
    EvaluationOutcome,
    FlangeCondition,
    JurisdictionMode,
    RebarGroup,
    RebarMaterial,
    SectionType,
    VerificationStatus,
)
from beamgenius.engine import evaluate_minimum_flexural_reinforcement


def test_flexure_min_exact_transition_fc_31_36_mpa() -> None:
    # Transition: 0.25 * sqrt(fc') = 1.4 => sqrt(fc') = 5.6 => fc' = 31.36 MPa
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=440.0)
    rebar = RebarMaterial(fy_mpa=400.0)

    # 1. Below transition: fc' = 25 MPa -> sqrt(fc') = 5.0 -> 0.25*5.0 = 1.25 < 1.4
    step_low = evaluate_minimum_flexural_reinforcement(
        geom, ConcreteMaterial(fc_prime_mpa=25.0), rebar
    )
    assert step_low.outcome == EvaluationOutcome.COMPUTED
    assert step_low.intermediate_values["as_min_term_2_mm2"] > step_low.intermediate_values["as_min_term_1_mm2"]
    expected_low = 1.4 * 300.0 * 440.0 / 400.0  # 462.0 mm^2
    assert step_low.final_result == pytest.approx(expected_low, rel=1e-12)

    # 2. Exactly at transition: fc' = 31.36 MPa -> 0.25 * 5.6 = 1.4
    step_eq = evaluate_minimum_flexural_reinforcement(
        geom, ConcreteMaterial(fc_prime_mpa=31.36), rebar
    )
    assert step_eq.outcome == EvaluationOutcome.COMPUTED
    assert step_eq.intermediate_values["as_min_term_1_mm2"] == pytest.approx(
        step_eq.intermediate_values["as_min_term_2_mm2"], rel=1e-12
    )
    assert step_eq.final_result == pytest.approx(expected_low, rel=1e-12)

    # 3. Above transition: fc' = 36 MPa -> sqrt(fc') = 6.0 -> 0.25 * 6.0 = 1.5 > 1.4
    step_high = evaluate_minimum_flexural_reinforcement(
        geom, ConcreteMaterial(fc_prime_mpa=36.0), rebar
    )
    assert step_high.outcome == EvaluationOutcome.COMPUTED
    assert step_high.intermediate_values["as_min_term_1_mm2"] > step_high.intermediate_values["as_min_term_2_mm2"]
    expected_high = 0.25 * 6.0 * 300.0 * 440.0 / 400.0  # 495.0 mm^2
    assert step_high.final_result == pytest.approx(expected_high, rel=1e-12)


def test_flexure_min_pass_fail_and_trace_metadata() -> None:
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=440.0)
    concrete = ConcreteMaterial(fc_prime_mpa=25.0)
    rebar = RebarMaterial(fy_mpa=400.0)
    expected_as_min = 462.0

    # Exact equality -> PASS
    step_pass = evaluate_minimum_flexural_reinforcement(
        geom, concrete, rebar, as_provided_mm2=expected_as_min
    )
    assert step_pass.outcome == EvaluationOutcome.PASS
    assert step_pass.final_result == pytest.approx(expected_as_min)
    assert step_pass.rule_id == "BG-FLEX-MIN-001"
    assert step_pass.pdf_page == 220
    assert step_pass.printed_page == 199
    assert step_pass.verification_status == VerificationStatus.VERIFIED
    assert step_pass.unit == "mm^2"

    # Below As,min -> FAIL
    step_fail = evaluate_minimum_flexural_reinforcement(
        geom, concrete, rebar, as_provided_mm2=461.99
    )
    assert step_fail.outcome == EvaluationOutcome.FAIL
    assert step_fail.final_result == pytest.approx(expected_as_min)
    assert any(
        d.code == "INSUFFICIENT_MINIMUM_FLEXURAL_REINFORCEMENT"
        for d in step_fail.diagnostics
    )


def test_flexure_min_fy_550_constraint() -> None:
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=440.0)
    concrete = ConcreteMaterial(fc_prime_mpa=28.0)

    # fy == 550 MPa is permitted
    step_550 = evaluate_minimum_flexural_reinforcement(
        geom,
        concrete,
        RebarMaterial(fy_mpa=550.0),
        as_provided_mm2=400.0,
    )
    assert step_550.outcome == EvaluationOutcome.PASS

    # fy > 550 MPa is rejected with INVALID_INPUT
    step_551 = evaluate_minimum_flexural_reinforcement(
        geom,
        concrete,
        RebarMaterial(fy_mpa=550.01),
        as_provided_mm2=400.0,
    )
    assert step_551.outcome == EvaluationOutcome.INVALID_INPUT
    assert step_551.final_result is None
    assert any(d.code == "FY_EXCEEDS_MABHAS9_FLEX_MIN_LIMIT" for d in step_551.diagnostics)


def test_flexure_min_clause_9_11_5_1_3_waiver_retains_as_min_in_trace() -> None:
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=440.0)
    concrete = ConcreteMaterial(fc_prime_mpa=25.0)
    rebar = RebarMaterial(fy_mpa=400.0)
    # As,min = 462.0 mm^2
    # Suppose As,required_by_analysis = 300.0 mm^2 -> 4/3 * 300 = 400.0 mm^2
    # And As,provided = 400.0 mm^2 (< 462.0 mm^2, but >= 4/3 * 300.0 mm^2)
    step_exempt = evaluate_minimum_flexural_reinforcement(
        geom,
        concrete,
        rebar,
        as_provided_mm2=400.0,
        as_required_by_analysis_mm2=300.0,
    )
    assert step_exempt.outcome == EvaluationOutcome.EXEMPT
    # IMPORTANT: As,min is still calculated and retained in final_result & intermediate_values
    assert step_exempt.final_result == pytest.approx(462.0)
    assert step_exempt.intermediate_values["as_min_mm2"] == pytest.approx(462.0)
    assert step_exempt.intermediate_values["waiver_threshold_4_3_as_req_mm2"] == pytest.approx(400.0)
    assert any(d.code == "CLAUSE_9_11_5_1_3_WAIVER_APPLIED" for d in step_exempt.diagnostics)

    # When As,provided = 399.9 mm^2 (< 400.0 mm^2 and < 462.0 mm^2) -> FAIL
    step_not_exempt = evaluate_minimum_flexural_reinforcement(
        geom,
        concrete,
        rebar,
        as_provided_mm2=399.9,
        as_required_by_analysis_mm2=300.0,
    )
    assert step_not_exempt.outcome == EvaluationOutcome.FAIL
    assert step_not_exempt.final_result == pytest.approx(462.0)


@pytest.mark.parametrize("sec_type", [SectionType.T_SECTION, SectionType.L_SECTION])
def test_flexure_min_flange_in_tension_blocked_and_compression_allowed(
    sec_type: SectionType,
) -> None:
    concrete = ConcreteMaterial(fc_prime_mpa=28.0)
    rebar = RebarMaterial(fy_mpa=400.0)

    # Flange in tension -> UNVERIFIED_RULE_BLOCKED
    geom_tension = BeamGeometry(
        bw_mm=300.0,
        h_mm=500.0,
        d_effective_mm=440.0,
        section_type=sec_type,
        flange_condition=FlangeCondition.FLANGE_IN_TENSION,
        bf_mm=700.0,
        tf_mm=120.0,
    )
    step_blocked = evaluate_minimum_flexural_reinforcement(
        geom_tension, concrete, rebar, as_provided_mm2=600.0
    )
    assert step_blocked.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step_blocked.final_result is None
    assert any(
        d.code == "FLANGE_IN_TENSION_EFFECTIVE_WIDTH_UNVERIFIED"
        for d in step_blocked.diagnostics
    )

    # Flange in compression -> uses bw_mm and passes
    geom_comp = BeamGeometry(
        bw_mm=300.0,
        h_mm=500.0,
        d_effective_mm=440.0,
        section_type=sec_type,
        flange_condition=FlangeCondition.FLANGE_IN_COMPRESSION,
        bf_mm=700.0,
        tf_mm=120.0,
    )
    step_comp = evaluate_minimum_flexural_reinforcement(
        geom_comp, concrete, rebar, as_provided_mm2=600.0
    )
    assert step_comp.outcome == EvaluationOutcome.PASS
    assert step_comp.final_result == pytest.approx(462.0)


def test_flexure_min_with_actual_rebar_geometry_and_jurisdiction_gate() -> None:
    # 3Φ20 in 1 layer with cover=40, stirrup=10 -> d = 500 - (40 + 10 + 10) = 440 mm
    # As_provided = 3 * pi * 20^2 / 4 = 942.4778 mm^2 > As_min (462 mm^2)
    geom = BeamGeometry(
        bw_mm=300.0,
        h_mm=500.0,
        clear_cover_mm=40.0,
        stirrup_diameter_mm=10.0,
        tension_rebar_groups=(RebarGroup(bar_diameter_mm=20.0, bar_count=3, layer_index=1),),
    )
    step = evaluate_minimum_flexural_reinforcement(
        geom, ConcreteMaterial(fc_prime_mpa=25.0), RebarMaterial(fy_mpa=400.0)
    )
    assert step.outcome == EvaluationOutcome.PASS
    assert step.normalized_inputs["d_effective_mm"] == pytest.approx(440.0)
    assert step.intermediate_values["as_provided_mm2"] == pytest.approx(300.0 * math.pi)

    # Calling in MOSTOFINEJAD_METHODOLOGY_ONLY returns JURISDICTION_BLOCKED
    step_jur = evaluate_minimum_flexural_reinforcement(
        geom,
        ConcreteMaterial(fc_prime_mpa=25.0),
        RebarMaterial(fy_mpa=400.0),
        jurisdiction_mode=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    )
    assert step_jur.outcome == EvaluationOutcome.JURISDICTION_BLOCKED
