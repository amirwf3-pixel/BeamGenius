"""Tests for Mabhas 9 Flexural Reinforcement and Resistance (Phase 2B Continuation).

Covers:
- BG-FLEX-MIN-001: Minimum Flexural Reinforcement
- BG-FLEX-STRESS-BLOCK: Equivalent Rectangular Compression Stress-Block Parameters
- BG-FLEX-STRAIN-LIMIT: Flexural Strain Compatibility and Tension-Controlled Beam Ductility Limit
- BG-FLEX-PHI-FACTOR: Flexural Strength Reduction Factor phi
- BG-FLEX-RECT-SINGLY-001: Rectangular Singly-Reinforced Beam Flexural Resistance
- BG-FLEX-TBEAM-B-EFF-001: Non-Prestressed T-Beam and L-Beam Effective Compression Flange Width
- Blocked doubly-reinforced (BG-FLEX-RECT-DOUBLY-001) and flanged (BG-FLEX-TBEAM-CAP-001, BG-FLEX-LBEAM-CAP-001) paths
- Anti-misleading PASS workflow and report aggregation
"""

from __future__ import annotations

import ast
import math
from pathlib import Path

import pytest

from beamgenius.domain import (
    BeamGeometry,
    ConcreteMaterial,
    EvaluationOutcome,
    FlangeCondition,
    JurisdictionMode,
    OverallComplianceStatus,
    RebarGroup,
    RebarMaterial,
    SectionType,
    StirrupLayout,
    VerificationStatus,
)
from beamgenius.engine import (
    evaluate_mabhas9_effective_flange_width,
    evaluate_mabhas9_flexural_capacity,
    evaluate_mabhas9_phi_factor,
    evaluate_mabhas9_strain_and_ductility_limit,
    evaluate_mabhas9_stress_block_parameters,
    evaluate_minimum_flexural_reinforcement,
    run_mabhas9_beam_check,
    run_mabhas9_flexural_workflow,
)
from beamgenius.reference import (
    evaluate_mostofinejad_eq_5_49_alpha1,
    evaluate_mostofinejad_eq_5_54_a,
    evaluate_mostofinejad_eq_5_55_mr,
    evaluate_mostofinejad_eq_5_61_check,
)
from beamgenius.registry import evaluate_rule_gate, require_rule


# ============================================================================
# 1. BG-FLEX-MIN-001 TESTS (PRESERVED UNCHANGED)
# ============================================================================


def test_flexure_min_exact_transition_fc_31_36_mpa() -> None:
    # Transition: 0.25 * sqrt(fc') = 1.4 => sqrt(fc') = 5.6 => fc' = 31.36 MPa
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=440.0)
    rebar = RebarMaterial(fy_mpa=400.0)

    # 1. Below transition: fc' = 25 MPa -> sqrt(fc') = 5.0 -> 0.25*5.0 = 1.25 < 1.4
    step_low = evaluate_minimum_flexural_reinforcement(
        geom, ConcreteMaterial(fc_prime_mpa=25.0), rebar
    )
    assert step_low.outcome == EvaluationOutcome.COMPUTED
    assert (
        step_low.intermediate_values["as_min_term_2_mm2"]
        > step_low.intermediate_values["as_min_term_1_mm2"]
    )
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
    assert (
        step_high.intermediate_values["as_min_term_1_mm2"]
        > step_high.intermediate_values["as_min_term_2_mm2"]
    )
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
    assert any(
        d.code == "FY_EXCEEDS_MABHAS9_FLEX_MIN_LIMIT" for d in step_551.diagnostics
    )


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
    assert step_exempt.final_result == pytest.approx(462.0)
    assert step_exempt.intermediate_values["as_min_mm2"] == pytest.approx(462.0)
    assert step_exempt.intermediate_values[
        "waiver_threshold_4_3_as_req_mm2"
    ] == pytest.approx(400.0)
    assert any(
        d.code == "CLAUSE_9_11_5_1_3_WAIVER_APPLIED" for d in step_exempt.diagnostics
    )

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
    geom = BeamGeometry(
        bw_mm=300.0,
        h_mm=500.0,
        clear_cover_mm=40.0,
        stirrup_diameter_mm=10.0,
        tension_rebar_groups=(
            RebarGroup(bar_diameter_mm=20.0, bar_count=3, layer_index=1),
        ),
    )
    step = evaluate_minimum_flexural_reinforcement(
        geom, ConcreteMaterial(fc_prime_mpa=25.0), RebarMaterial(fy_mpa=400.0)
    )
    assert step.outcome == EvaluationOutcome.PASS
    assert step.normalized_inputs["d_effective_mm"] == pytest.approx(440.0)
    assert step.intermediate_values["as_provided_mm2"] == pytest.approx(
        300.0 * math.pi
    )

    step_jur = evaluate_minimum_flexural_reinforcement(
        geom,
        ConcreteMaterial(fc_prime_mpa=25.0),
        RebarMaterial(fy_mpa=400.0),
        jurisdiction_mode=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    )
    assert step_jur.outcome == EvaluationOutcome.JURISDICTION_BLOCKED


# ============================================================================
# 2. TASK 10.1 — STRESS-BLOCK BOUNDARY TESTS (BG-FLEX-STRESS-BLOCK)
# ============================================================================


def test_mabhas9_stress_block_boundaries_beta1_and_alpha0() -> None:
    # 1. Below threshold: f'c = 20 MPa & 25 MPa -> alpha_0 = 0.85, beta_1 = 0.85
    for fc_low in (20.0, 25.0):
        step_low = evaluate_mabhas9_stress_block_parameters(
            ConcreteMaterial(fc_prime_mpa=fc_low), c_mm=100.0
        )
        assert step_low.outcome == EvaluationOutcome.COMPUTED
        assert step_low.rule_id == "BG-FLEX-STRESS-BLOCK"
        assert step_low.pdf_page == 22
        assert step_low.printed_page == 113
        assert step_low.intermediate_values["alpha_0"] == pytest.approx(0.85, rel=1e-12)
        assert step_low.intermediate_values["beta_1"] == pytest.approx(0.85, rel=1e-12)
        assert step_low.intermediate_values["a_mm"] == pytest.approx(85.0, rel=1e-12)
        assert step_low.final_result == pytest.approx(0.85, rel=1e-12)

    # 2. Exact beta_1 threshold: f'c = 28 MPa -> alpha_0 = 0.85, beta_1 = 0.85
    step_28 = evaluate_mabhas9_stress_block_parameters(
        ConcreteMaterial(fc_prime_mpa=28.0)
    )
    assert step_28.outcome == EvaluationOutcome.COMPUTED
    assert step_28.intermediate_values["alpha_0"] == pytest.approx(0.85, rel=1e-12)
    assert step_28.intermediate_values["beta_1"] == pytest.approx(0.85, rel=1e-12)

    # 3. Above beta_1 threshold: f'c = 35 MPa -> beta_1 = 0.85 - 0.05*(35-28)/7 = 0.80
    step_35 = evaluate_mabhas9_stress_block_parameters(
        ConcreteMaterial(fc_prime_mpa=35.0)
    )
    assert step_35.outcome == EvaluationOutcome.COMPUTED
    assert step_35.intermediate_values["alpha_0"] == pytest.approx(0.85, rel=1e-12)
    assert step_35.intermediate_values["beta_1"] == pytest.approx(0.80, rel=1e-12)

    # 4. Exact alpha_0 threshold: f'c = 55 MPa -> alpha_0 = 0.85, beta_1 = 0.85 - 0.05*27/7
    step_55 = evaluate_mabhas9_stress_block_parameters(
        ConcreteMaterial(fc_prime_mpa=55.0)
    )
    assert step_55.outcome == EvaluationOutcome.COMPUTED
    assert step_55.intermediate_values["alpha_0"] == pytest.approx(0.85, rel=1e-12)
    assert step_55.intermediate_values["beta_1"] == pytest.approx(
        0.85 - 0.05 * 27.0 / 7.0, rel=1e-12
    )

    # 5. Exact beta_1 lower cutoff: f'c = 56 MPa -> beta_1 = 0.65, alpha_0 = 0.85 - 0.004*(1) = 0.846
    step_56 = evaluate_mabhas9_stress_block_parameters(
        ConcreteMaterial(fc_prime_mpa=56.0)
    )
    assert step_56.outcome == EvaluationOutcome.COMPUTED
    assert step_56.intermediate_values["beta_1"] == pytest.approx(0.65, rel=1e-12)
    assert step_56.intermediate_values["alpha_0"] == pytest.approx(0.846, rel=1e-12)

    # 6. Upper structural limit f'c = 70 MPa -> beta_1 = 0.65, alpha_0 = 0.85 - 0.004*(15) = 0.79
    step_70 = evaluate_mabhas9_stress_block_parameters(
        ConcreteMaterial(fc_prime_mpa=70.0)
    )
    assert step_70.outcome == EvaluationOutcome.COMPUTED
    assert step_70.intermediate_values["beta_1"] == pytest.approx(0.65, rel=1e-12)
    assert step_70.intermediate_values["alpha_0"] == pytest.approx(0.79, rel=1e-12)

    # 7. Lower cutoff of alpha_0 = 0.75 at f'c >= 80 MPa (when code f'c bounds are disabled)
    step_85 = evaluate_mabhas9_stress_block_parameters(
        ConcreteMaterial(fc_prime_mpa=85.0),
        enforce_code_fc_bounds=False,
    )
    assert step_85.outcome == EvaluationOutcome.COMPUTED
    assert step_85.intermediate_values["beta_1"] == pytest.approx(0.65, rel=1e-12)
    assert step_85.intermediate_values["alpha_0"] == pytest.approx(0.75, rel=1e-12)

    # 8. Clause 9-3-3-3 concrete bounds enforced by default
    step_below_20 = evaluate_mabhas9_stress_block_parameters(
        ConcreteMaterial(fc_prime_mpa=19.99)
    )
    assert step_below_20.outcome == EvaluationOutcome.INVALID_INPUT
    assert any(d.code == "FC_BELOW_MABHAS9_MINIMUM" for d in step_below_20.diagnostics)

    step_above_70 = evaluate_mabhas9_stress_block_parameters(
        ConcreteMaterial(fc_prime_mpa=70.01)
    )
    assert step_above_70.outcome == EvaluationOutcome.INVALID_INPUT
    assert any(d.code == "FC_EXCEEDS_MABHAS9_MAXIMUM" for d in step_above_70.diagnostics)


# ============================================================================
# 3. TASK 10.2 — STRAIN & PHI BOUNDARY TESTS (BG-FLEX-PHI-FACTOR & BG-FLEX-STRAIN-LIMIT)
# ============================================================================


def test_mabhas9_phi_factor_and_strain_limit_boundaries() -> None:
    rebar = RebarMaterial(fy_mpa=400.0, es_mpa=200_000.0)
    # epsilon_ty = 400 / 200000 = 0.002
    # epsilon_t_tc = 0.002 + 0.003 = 0.005

    # 1. Compression-controlled below boundary (epsilon_t = 0.001 < 0.002)
    phi_cc_other = evaluate_mabhas9_phi_factor(0.001, rebar, is_spiral_transverse=False)
    assert phi_cc_other.outcome == EvaluationOutcome.COMPUTED
    assert phi_cc_other.final_result == pytest.approx(0.65, rel=1e-12)
    assert phi_cc_other.normalized_inputs["strain_regime"] == "COMPRESSION_CONTROLLED"

    phi_cc_spiral = evaluate_mabhas9_phi_factor(0.001, rebar, is_spiral_transverse=True)
    assert phi_cc_spiral.final_result == pytest.approx(0.75, rel=1e-12)

    # 2. Exact compression-controlled boundary (epsilon_t == epsilon_ty == 0.002)
    phi_eq_cc_other = evaluate_mabhas9_phi_factor(
        0.002, rebar, is_spiral_transverse=False
    )
    assert phi_eq_cc_other.final_result == pytest.approx(0.65, rel=1e-12)
    assert phi_eq_cc_other.normalized_inputs["strain_regime"] == "COMPRESSION_CONTROLLED"

    phi_eq_cc_spiral = evaluate_mabhas9_phi_factor(
        0.002, rebar, is_spiral_transverse=True
    )
    assert phi_eq_cc_spiral.final_result == pytest.approx(0.75, rel=1e-12)

    # 3. Transition region midpoint (epsilon_t = 0.0035 -> (0.0035 - 0.002)/0.003 = 0.5)
    # Eq. (9-7-10-ب): phi = 0.65 + 0.25 * 0.5 = 0.775
    # Eq. (9-7-10-الف): phi = 0.75 + 0.15 * 0.5 = 0.825
    phi_trans_other = evaluate_mabhas9_phi_factor(
        0.0035, rebar, is_spiral_transverse=False
    )
    assert phi_trans_other.final_result == pytest.approx(0.775, rel=1e-12)
    assert phi_trans_other.normalized_inputs["strain_regime"] == "TRANSITION_ZONE"

    phi_trans_spiral = evaluate_mabhas9_phi_factor(
        0.0035, rebar, is_spiral_transverse=True
    )
    assert phi_trans_spiral.final_result == pytest.approx(0.825, rel=1e-12)
    assert phi_trans_spiral.normalized_inputs["strain_regime"] == "TRANSITION_ZONE"

    # 4. Exact tension-controlled boundary (epsilon_t == epsilon_ty + 0.003 == 0.005)
    phi_eq_tc_other = evaluate_mabhas9_phi_factor(
        0.005, rebar, is_spiral_transverse=False
    )
    assert phi_eq_tc_other.final_result == pytest.approx(0.90, rel=1e-12)
    assert phi_eq_tc_other.normalized_inputs["strain_regime"] == "TENSION_CONTROLLED"

    phi_eq_tc_spiral = evaluate_mabhas9_phi_factor(
        0.005, rebar, is_spiral_transverse=True
    )
    assert phi_eq_tc_spiral.final_result == pytest.approx(0.90, rel=1e-12)

    # 5. Tension-controlled region above boundary (epsilon_t = 0.008 > 0.005)
    phi_tc = evaluate_mabhas9_phi_factor(0.008, rebar)
    assert phi_tc.final_result == pytest.approx(0.90, rel=1e-12)
    assert phi_tc.normalized_inputs["strain_regime"] == "TENSION_CONTROLLED"

    # 6. BG-FLEX-STRAIN-LIMIT exact c/dt boundary:
    # For fy = 400 MPa, epsilon_ty = 0.002 -> (c/dt)_max,tc = 0.003 / 0.008 = 0.375
    # With dt = 400 mm -> c_max,tc = 150.0 mm
    strain_exact = evaluate_mabhas9_strain_and_ductility_limit(
        c_mm=150.0, dt_mm=400.0, rebar=rebar
    )
    assert strain_exact.outcome == EvaluationOutcome.PASS
    assert strain_exact.final_result == pytest.approx(0.005, rel=1e-12)
    assert strain_exact.intermediate_values["c_over_dt_max_tc"] == pytest.approx(
        0.375, rel=1e-12
    )

    strain_below_c = evaluate_mabhas9_strain_and_ductility_limit(
        c_mm=149.9, dt_mm=400.0, rebar=rebar
    )
    assert strain_below_c.outcome == EvaluationOutcome.PASS
    assert strain_below_c.final_result is not None and strain_below_c.final_result > 0.005

    strain_above_c = evaluate_mabhas9_strain_and_ductility_limit(
        c_mm=150.1, dt_mm=400.0, rebar=rebar
    )
    assert strain_above_c.outcome == EvaluationOutcome.FAIL
    assert any(
        d.code == "SECTION_NOT_TENSION_CONTROLLED_PER_9_11_2_3"
        for d in strain_above_c.diagnostics
    )


# ============================================================================
# 4. TASK 10.3 — MAXIMUM REINFORCEMENT / DUCTILITY BOUNDARY TESTS (BG-FLEX-RECT-SINGLY-001)
# ============================================================================


def test_mabhas9_rectangular_singly_reinforced_max_reinforcement_boundary() -> None:
    # Section: bw = 300 mm, h = 500 mm, d = 440 mm, f'c = 28 MPa, fy = 400 MPa, Es = 200,000 MPa
    # alpha_0 = 0.85, beta_1 = 0.85
    # epsilon_ty = 0.002 -> (c/dt)_max,tc = 0.003 / (0.002 + 0.006) = 3/8 = 0.375
    # c_max,tc = 0.375 * 440 = 165.0 mm
    # a_max,tc = 0.85 * 165.0 = 140.25 mm
    # As,max,tc = (0.85 * 28 * 300 * 140.25) / 400 = 2503.4625 mm^2
    # rho_max,tc = 2503.4625 / (300 * 440) = 0.018965625
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=440.0)
    conc = ConcreteMaterial(fc_prime_mpa=28.0)
    rebar = RebarMaterial(fy_mpa=400.0, es_mpa=200_000.0)
    as_max_tc = 2503.4625
    expected_mn_at_max = as_max_tc * 400.0 * (440.0 - 140.25 / 2.0)
    expected_phi_mn_at_max = 0.90 * expected_mn_at_max

    # 1. Just below As,max,tc -> PASS
    step_below = evaluate_mabhas9_flexural_capacity(
        geom,
        conc,
        rebar,
        as_provided_mm2=as_max_tc - 1.0,
        mu_nmm=300.0e6,
    )
    assert step_below.outcome == EvaluationOutcome.PASS
    assert step_below.rule_id == "BG-FLEX-RECT-SINGLY-001"
    assert step_below.intermediate_values["as_max_tc_mm2"] == pytest.approx(
        as_max_tc, rel=1e-12
    )
    assert step_below.intermediate_values["epsilon_t"] > 0.005

    # 2. Exact As,max,tc -> PASS (epsilon_t == 0.005, phi == 0.90)
    step_exact = evaluate_mabhas9_flexural_capacity(
        geom,
        conc,
        rebar,
        as_provided_mm2=as_max_tc,
        mu_nmm=expected_phi_mn_at_max,
    )
    assert step_exact.outcome == EvaluationOutcome.PASS
    assert step_exact.intermediate_values["epsilon_t"] == pytest.approx(0.005, rel=1e-12)
    assert step_exact.intermediate_values["phi"] == pytest.approx(0.90, rel=1e-12)
    assert step_exact.final_result == pytest.approx(expected_phi_mn_at_max, rel=1e-12)

    # 3. Just above As,max,tc -> FAIL (violates Clause 9-11-2-3 tension-controlled requirement)
    step_above = evaluate_mabhas9_flexural_capacity(
        geom,
        conc,
        rebar,
        as_provided_mm2=as_max_tc + 1.0,
        mu_nmm=200.0e6,
    )
    assert step_above.outcome == EvaluationOutcome.FAIL
    assert step_above.intermediate_values["epsilon_t"] < 0.005
    assert any(
        d.code == "MAX_REINFORCEMENT_DUCTILITY_LIMIT_EXCEEDED"
        for d in step_above.diagnostics
    )

    # 4. Proof that Mabhas 9 (1399) uses epsilon_t >= epsilon_ty + 0.003 and NOT 0.75 * rho_b:
    # 0.75 * rho_b = 0.75 * (0.85 * 28 / 400) * 0.85 * (0.003 / 0.005) = 0.02275875
    # Choose rho = 0.020 (As = 2640 mm^2), which is < 0.75*rho_b (3004.155 mm^2) but > As,max,tc (2503.4625 mm^2).
    step_legacy_rho = evaluate_mabhas9_flexural_capacity(
        geom,
        conc,
        rebar,
        as_provided_mm2=2640.0,
        mu_nmm=200.0e6,
    )
    assert step_legacy_rho.outcome == EvaluationOutcome.FAIL
    assert any(
        d.code == "MAX_REINFORCEMENT_DUCTILITY_LIMIT_EXCEEDED"
        for d in step_legacy_rho.diagnostics
    )

    # 5. Compression-controlled over-reinforced section (As = 5000 mm^2 -> epsilon_t < epsilon_ty)
    step_over = evaluate_mabhas9_flexural_capacity(
        geom,
        conc,
        rebar,
        as_provided_mm2=5000.0,
        mu_nmm=200.0e6,
    )
    assert step_over.outcome == EvaluationOutcome.FAIL
    assert step_over.intermediate_values["epsilon_t"] < 0.002
    assert step_over.intermediate_values["fs_mpa"] < 400.0
    assert step_over.intermediate_values["phi"] == pytest.approx(0.65, rel=1e-12)
    assert any(
        d.code == "MAX_REINFORCEMENT_DUCTILITY_LIMIT_EXCEEDED"
        for d in step_over.diagnostics
    )


# ============================================================================
# 5. TASK 10.4 — T-BEAM & L-BEAM EFFECTIVE FLANGE WIDTH TESTS (BG-FLEX-TBEAM-B-EFF-001)
# ============================================================================


def test_mabhas9_tbeam_and_lbeam_effective_flange_width_limits() -> None:
    # 1. T-beam governed by 8*hf on each side:
    # bw = 300, hf = 80 -> 8*hf = 640 mm; sw = 2000 -> sw/2 = 1000 mm; ln = 8000 -> ln/8 = 1000 mm
    # bf_limit = 300 + 2 * 640 = 1580 mm
    geom_t_hf = BeamGeometry(
        bw_mm=300.0,
        h_mm=600.0,
        tf_mm=80.0,
        section_type=SectionType.T_SECTION,
        flange_condition=FlangeCondition.FLANGE_IN_COMPRESSION,
        clear_web_spacing_sw_mm=2000.0,
        clear_span_ln_mm=8000.0,
    )
    step_t_hf = evaluate_mabhas9_effective_flange_width(geom_t_hf)
    assert step_t_hf.outcome == EvaluationOutcome.COMPUTED
    assert step_t_hf.rule_id == "BG-FLEX-TBEAM-B-EFF-001"
    assert step_t_hf.normalized_inputs["governing_criterion"] == "FLANGE_THICKNESS_HF"
    assert step_t_hf.final_result == pytest.approx(1580.0, rel=1e-12)

    # 2. T-beam governed by sw / 2 on each side:
    # bw = 300, hf = 120 -> 8*hf = 960 mm; sw = 1000 -> sw/2 = 500 mm; ln = 8000 -> ln/8 = 1000 mm
    # bf_limit = 300 + 2 * 500 = 1300 mm
    geom_t_sw = BeamGeometry(
        bw_mm=300.0,
        h_mm=600.0,
        tf_mm=120.0,
        section_type=SectionType.T_SECTION,
        flange_condition=FlangeCondition.FLANGE_IN_COMPRESSION,
        clear_web_spacing_sw_mm=1000.0,
        clear_span_ln_mm=8000.0,
    )
    step_t_sw = evaluate_mabhas9_effective_flange_width(geom_t_sw)
    assert step_t_sw.outcome == EvaluationOutcome.COMPUTED
    assert step_t_sw.normalized_inputs["governing_criterion"] == "WEB_CLEAR_SPACING_SW"
    assert step_t_sw.final_result == pytest.approx(1300.0, rel=1e-12)

    # 3. T-beam governed by ln / 8 on each side:
    # bw = 300, hf = 120 -> 8*hf = 960 mm; sw = 2000 -> sw/2 = 1000 mm; ln = 3200 -> ln/8 = 400 mm
    # bf_limit = 300 + 2 * 400 = 1100 mm
    geom_t_ln = BeamGeometry(
        bw_mm=300.0,
        h_mm=600.0,
        tf_mm=120.0,
        section_type=SectionType.T_SECTION,
        flange_condition=FlangeCondition.FLANGE_IN_COMPRESSION,
        clear_web_spacing_sw_mm=2000.0,
        clear_span_ln_mm=3200.0,
    )
    step_t_ln = evaluate_mabhas9_effective_flange_width(geom_t_ln)
    assert step_t_ln.outcome == EvaluationOutcome.COMPUTED
    assert step_t_ln.normalized_inputs["governing_criterion"] == "CLEAR_SPAN_LN"
    assert step_t_ln.final_result == pytest.approx(1100.0, rel=1e-12)

    # Provided bf check on T-beam: exact limit (1100 mm) -> PASS, above limit (1101 mm) -> FAIL
    step_t_pass = evaluate_mabhas9_effective_flange_width(
        geom_t_ln, bf_provided_mm=1100.0
    )
    assert step_t_pass.outcome == EvaluationOutcome.PASS
    step_t_fail = evaluate_mabhas9_effective_flange_width(
        geom_t_ln, bf_provided_mm=1101.0
    )
    assert step_t_fail.outcome == EvaluationOutcome.FAIL
    assert any(
        d.code == "EFFECTIVE_FLANGE_WIDTH_EXCEEDS_TABLE_9_6_1_LIMIT"
        for d in step_t_fail.diagnostics
    )

    # 4. L-beam governed by 6*hf:
    # bw = 300, hf = 80 -> 6*hf = 480 mm; sw = 1600 -> sw/2 = 800 mm; ln = 7200 -> ln/12 = 600 mm
    # bf_limit = 300 + 480 = 780 mm
    geom_l_hf = BeamGeometry(
        bw_mm=300.0,
        h_mm=600.0,
        tf_mm=80.0,
        section_type=SectionType.L_SECTION,
        flange_condition=FlangeCondition.FLANGE_IN_COMPRESSION,
        clear_web_spacing_sw_mm=1600.0,
        clear_span_ln_mm=7200.0,
    )
    step_l_hf = evaluate_mabhas9_effective_flange_width(geom_l_hf)
    assert step_l_hf.outcome == EvaluationOutcome.COMPUTED
    assert step_l_hf.normalized_inputs["governing_criterion"] == "FLANGE_THICKNESS_HF"
    assert step_l_hf.final_result == pytest.approx(780.0, rel=1e-12)

    # 5. L-beam governed by sw / 2:
    # bw = 300, hf = 120 -> 6*hf = 720 mm; sw = 800 -> sw/2 = 400 mm; ln = 7200 -> ln/12 = 600 mm
    # bf_limit = 300 + 400 = 700 mm
    geom_l_sw = BeamGeometry(
        bw_mm=300.0,
        h_mm=600.0,
        tf_mm=120.0,
        section_type=SectionType.L_SECTION,
        flange_condition=FlangeCondition.FLANGE_IN_COMPRESSION,
        clear_web_spacing_sw_mm=800.0,
        clear_span_ln_mm=7200.0,
    )
    step_l_sw = evaluate_mabhas9_effective_flange_width(geom_l_sw)
    assert step_l_sw.outcome == EvaluationOutcome.COMPUTED
    assert step_l_sw.normalized_inputs["governing_criterion"] == "WEB_CLEAR_SPACING_SW"
    assert step_l_sw.final_result == pytest.approx(700.0, rel=1e-12)

    # 6. L-beam governed by ln / 12:
    # bw = 300, hf = 120 -> 6*hf = 720 mm; sw = 1600 -> sw/2 = 800 mm; ln = 3600 -> ln/12 = 300 mm
    # bf_limit = 300 + 300 = 600 mm
    geom_l_ln = BeamGeometry(
        bw_mm=300.0,
        h_mm=600.0,
        tf_mm=120.0,
        section_type=SectionType.L_SECTION,
        flange_condition=FlangeCondition.FLANGE_IN_COMPRESSION,
        clear_web_spacing_sw_mm=1600.0,
        clear_span_ln_mm=3600.0,
    )
    step_l_ln = evaluate_mabhas9_effective_flange_width(geom_l_ln)
    assert step_l_ln.outcome == EvaluationOutcome.COMPUTED
    assert step_l_ln.normalized_inputs["governing_criterion"] == "CLEAR_SPAN_LN"
    assert step_l_ln.final_result == pytest.approx(600.0, rel=1e-12)

    # 7. Isolated T-beam (Clause 9-6-3-3-2): hf >= 0.5*bw and bf <= 4*bw
    geom_iso_ok = BeamGeometry(
        bw_mm=300.0,
        h_mm=600.0,
        tf_mm=150.0,  # == 0.5 * 300
        bf_mm=1200.0,  # == 4 * 300
        section_type=SectionType.T_SECTION,
        flange_condition=FlangeCondition.FLANGE_IN_COMPRESSION,
        is_isolated_t_beam=True,
    )
    step_iso_ok = evaluate_mabhas9_effective_flange_width(geom_iso_ok)
    assert step_iso_ok.outcome == EvaluationOutcome.PASS
    assert step_iso_ok.final_result == pytest.approx(1200.0, rel=1e-12)

    geom_iso_thin = BeamGeometry(
        bw_mm=300.0,
        h_mm=600.0,
        tf_mm=149.0,  # < 0.5 * 300
        bf_mm=1000.0,
        section_type=SectionType.T_SECTION,
        flange_condition=FlangeCondition.FLANGE_IN_COMPRESSION,
        is_isolated_t_beam=True,
    )
    step_iso_thin = evaluate_mabhas9_effective_flange_width(geom_iso_thin)
    assert step_iso_thin.outcome == EvaluationOutcome.FAIL
    assert any(
        d.code == "ISOLATED_T_BEAM_FLANGE_THICKNESS_TOO_SMALL"
        for d in step_iso_thin.diagnostics
    )

    geom_iso_wide = BeamGeometry(
        bw_mm=300.0,
        h_mm=600.0,
        tf_mm=160.0,
        bf_mm=1201.0,  # > 4 * 300
        section_type=SectionType.T_SECTION,
        flange_condition=FlangeCondition.FLANGE_IN_COMPRESSION,
        is_isolated_t_beam=True,
    )
    step_iso_wide = evaluate_mabhas9_effective_flange_width(geom_iso_wide)
    assert step_iso_wide.outcome == EvaluationOutcome.FAIL
    assert any(
        d.code == "ISOLATED_T_BEAM_FLANGE_WIDTH_EXCEEDED"
        for d in step_iso_wide.diagnostics
    )


# ============================================================================
# 6. TASK 10.5 — INVALID GEOMETRY / MATERIALS & EFFECTIVE DEPTH PRECEDENCE
# ============================================================================


def test_phase_2b_flexural_capacity_input_and_effective_depth_validation() -> None:
    valid_geom = BeamGeometry(bw_mm=350.0, h_mm=600.0, d_effective_mm=535.0)
    valid_conc = ConcreteMaterial(fc_prime_mpa=28.0)
    valid_rebar = RebarMaterial(fy_mpa=400.0)

    # 1. Invalid fc' <= 0 -> INVALID_INPUT
    step_bad_fc = evaluate_mabhas9_flexural_capacity(
        valid_geom,
        ConcreteMaterial(fc_prime_mpa=0.0),
        valid_rebar,
        as_provided_mm2=1800.0,
        mu_nmm=240e6,
    )
    assert step_bad_fc.outcome == EvaluationOutcome.INVALID_INPUT
    assert any(d.code == "INVALID_CONCRETE_STRENGTH" for d in step_bad_fc.diagnostics)

    # 2. fc' below Mabhas 9 Clause 9-3-3-3 minimum (20 MPa) -> INVALID_INPUT
    step_low_fc = evaluate_mabhas9_flexural_capacity(
        valid_geom,
        ConcreteMaterial(fc_prime_mpa=18.0),
        valid_rebar,
        as_provided_mm2=1800.0,
        mu_nmm=240e6,
    )
    assert step_low_fc.outcome == EvaluationOutcome.INVALID_INPUT
    assert any(d.code == "FC_BELOW_MABHAS9_MINIMUM" for d in step_low_fc.diagnostics)

    # 3. Invalid fy <= 0 and fy > 550 MPa -> INVALID_INPUT
    step_bad_fy = evaluate_mabhas9_flexural_capacity(
        valid_geom,
        valid_conc,
        RebarMaterial(fy_mpa=-400.0),
        as_provided_mm2=1800.0,
        mu_nmm=240e6,
    )
    assert step_bad_fy.outcome == EvaluationOutcome.INVALID_INPUT
    assert any(d.code == "INVALID_REBAR_FY" for d in step_bad_fy.diagnostics)

    step_high_fy = evaluate_mabhas9_flexural_capacity(
        valid_geom,
        valid_conc,
        RebarMaterial(fy_mpa=560.0),
        as_provided_mm2=1800.0,
        mu_nmm=240e6,
    )
    assert step_high_fy.outcome == EvaluationOutcome.INVALID_INPUT
    assert any(
        d.code == "FY_EXCEEDS_MABHAS9_FLEX_MIN_LIMIT" for d in step_high_fy.diagnostics
    )

    # 4. Invalid geometry (bw <= 0, d <= 0, d >= h) -> INVALID_INPUT
    step_bad_geom = evaluate_mabhas9_flexural_capacity(
        BeamGeometry(bw_mm=0.0, h_mm=600.0, d_effective_mm=535.0),
        valid_conc,
        valid_rebar,
        as_provided_mm2=1800.0,
        mu_nmm=240e6,
    )
    assert step_bad_geom.outcome == EvaluationOutcome.INVALID_INPUT
    assert any(d.code == "INVALID_BEAM_WIDTH" for d in step_bad_geom.diagnostics)

    step_d_zero = evaluate_mabhas9_flexural_capacity(
        BeamGeometry(bw_mm=350.0, h_mm=600.0, d_effective_mm=0.0),
        valid_conc,
        valid_rebar,
        as_provided_mm2=1800.0,
        mu_nmm=240e6,
    )
    assert step_d_zero.outcome == EvaluationOutcome.INVALID_INPUT
    assert any(d.code == "INVALID_EFFECTIVE_DEPTH" for d in step_d_zero.diagnostics)

    step_d_ge_h = evaluate_mabhas9_flexural_capacity(
        BeamGeometry(bw_mm=350.0, h_mm=600.0, d_effective_mm=600.0),
        valid_conc,
        valid_rebar,
        as_provided_mm2=1800.0,
        mu_nmm=240e6,
    )
    assert step_d_ge_h.outcome == EvaluationOutcome.INVALID_INPUT
    assert any(
        d.code == "IMPOSSIBLE_EFFECTIVE_DEPTH_GE_HEIGHT"
        for d in step_d_ge_h.diagnostics
    )

    # 5. Invalid As <= 0 -> INVALID_INPUT
    step_bad_as = evaluate_mabhas9_flexural_capacity(
        valid_geom,
        valid_conc,
        valid_rebar,
        as_provided_mm2=0.0,
        mu_nmm=240e6,
    )
    assert step_bad_as.outcome == EvaluationOutcome.INVALID_INPUT
    assert any(d.code == "INVALID_AS_PROVIDED" for d in step_bad_as.diagnostics)

    # 6. Invalid Mu < 0 -> INVALID_INPUT
    step_bad_mu = evaluate_mabhas9_flexural_capacity(
        valid_geom,
        valid_conc,
        valid_rebar,
        as_provided_mm2=1800.0,
        mu_nmm=-1.0,
    )
    assert step_bad_mu.outcome == EvaluationOutcome.INVALID_INPUT
    assert any(d.code == "INVALID_FACTORED_MOMENT_MU" for d in step_bad_mu.diagnostics)

    # 7. Unresolved d -> INVALID_INPUT (never guesses h - 65 or h - 90)
    step_no_d = evaluate_mabhas9_flexural_capacity(
        BeamGeometry(bw_mm=350.0, h_mm=600.0),
        valid_conc,
        valid_rebar,
        as_provided_mm2=1800.0,
        mu_nmm=240e6,
    )
    assert step_no_d.outcome == EvaluationOutcome.INVALID_INPUT
    assert any(d.code == "MISSING_EFFECTIVE_DEPTH" for d in step_no_d.diagnostics)

    # 8. Explicit d precedence preserved in trace normalized_inputs and executes BG-FLEX-RECT-SINGLY-001
    geom_explicit_with_partial_cover = BeamGeometry(
        bw_mm=350.0,
        h_mm=600.0,
        d_effective_mm=538.0,
        clear_cover_mm=40.0,
    )
    step_explicit_d = evaluate_mabhas9_flexural_capacity(
        geom_explicit_with_partial_cover,
        valid_conc,
        valid_rebar,
        as_provided_mm2=1800.0,
        mu_nmm=240e6,
    )
    assert step_explicit_d.outcome == EvaluationOutcome.PASS
    assert step_explicit_d.rule_id == "BG-FLEX-RECT-SINGLY-001"
    assert step_explicit_d.normalized_inputs["d_effective_mm"] == pytest.approx(538.0)
    assert step_explicit_d.normalized_inputs["d_resolution_source"] == "EXPLICIT_D"


# ============================================================================
# 7. TASKS 10.6 & 10.7 — SINGLY VS DOUBLY REINFORCED ROUTING & BLOCKED T/L CAPACITY
# ============================================================================


def test_phase_2b_singly_vs_doubly_and_flanged_routing() -> None:
    conc = ConcreteMaterial(fc_prime_mpa=28.0)
    rebar = RebarMaterial(fy_mpa=400.0)
    geom_rect = BeamGeometry(bw_mm=350.0, h_mm=600.0, d_effective_mm=535.0)

    # 1. Singly reinforced rectangular beam (as_compression_mm2 is None or 0.0) -> BG-FLEX-RECT-SINGLY-001
    # As = 1800 mm^2 -> a = 1800*400 / (0.85*28*350) = 720000 / 8330 = 86.43457382953181 mm
    # Mn = 1800*400*(535 - a/2) = 354,083,553.42136854 N*mm -> phi*Mn = 318,675,198.0792317 N*mm
    expected_a = (1800.0 * 400.0) / (0.85 * 28.0 * 350.0)
    expected_phi_mn = 0.90 * 1800.0 * 400.0 * (535.0 - expected_a / 2.0)
    step_singly = evaluate_mabhas9_flexural_capacity(
        geom_rect,
        conc,
        rebar,
        as_provided_mm2=1800.0,
        as_compression_mm2=0.0,
        mu_nmm=300.0e6,
    )
    assert step_singly.outcome == EvaluationOutcome.PASS
    assert step_singly.rule_id == "BG-FLEX-RECT-SINGLY-001"
    assert step_singly.final_result == pytest.approx(expected_phi_mn, rel=1e-12)

    # Demand exceeds phi*Mn -> FAIL (INSUFFICIENT_FLEXURAL_CAPACITY)
    step_singly_fail = evaluate_mabhas9_flexural_capacity(
        geom_rect,
        conc,
        rebar,
        as_provided_mm2=1800.0,
        mu_nmm=320.0e6,
    )
    assert step_singly_fail.outcome == EvaluationOutcome.FAIL
    assert any(
        d.code == "INSUFFICIENT_FLEXURAL_CAPACITY"
        for d in step_singly_fail.diagnostics
    )

    # 2. Doubly reinforced beam (as_compression_mm2 > 0) -> BG-FLEX-RECT-DOUBLY-001 (UNVERIFIED_RULE_BLOCKED)
    step_doubly = evaluate_mabhas9_flexural_capacity(
        geom_rect,
        conc,
        rebar,
        as_provided_mm2=2600.0,
        as_compression_mm2=600.0,
        mu_nmm=400e6,
    )
    assert step_doubly.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step_doubly.rule_id == "BG-FLEX-RECT-DOUBLY-001"
    assert step_doubly.final_result is None
    assert any(
        d.code == "DOUBLY_REINFORCED_FLEXURAL_RESISTANCE_UNVERIFIED"
        for d in step_doubly.diagnostics
    )

    # 3. T-beam and L-beam never fall back to rectangular behavior -> UNVERIFIED_RULE_BLOCKED
    for sec_type, expected_rule_id in (
        (SectionType.T_SECTION, "BG-FLEX-TBEAM-CAP-001"),
        (SectionType.L_SECTION, "BG-FLEX-LBEAM-CAP-001"),
    ):
        geom_flanged = BeamGeometry(
            bw_mm=300.0,
            h_mm=550.0,
            d_effective_mm=485.0,
            section_type=sec_type,
            flange_condition=FlangeCondition.FLANGE_IN_COMPRESSION,
            bf_mm=750.0,
            tf_mm=120.0,
        )
        step_flanged = evaluate_mabhas9_flexural_capacity(
            geom_flanged, conc, rebar, as_provided_mm2=2000.0, mu_nmm=250e6
        )
        assert step_flanged.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
        assert step_flanged.rule_id == expected_rule_id
        assert step_flanged.final_result is None
        assert any(
            d.code == "FLANGED_SECTION_FLEXURAL_RESISTANCE_UNVERIFIED"
            for d in step_flanged.diagnostics
        )

    # 4. Jurisdiction gate on evaluate_mabhas9_flexural_capacity
    step_jur = evaluate_mabhas9_flexural_capacity(
        geom_rect,
        conc,
        rebar,
        as_provided_mm2=1800.0,
        mu_nmm=250e6,
        jurisdiction_mode=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    )
    assert step_jur.outcome == EvaluationOutcome.JURISDICTION_BLOCKED


# ============================================================================
# 8. TASK 10.8 — ANTI-MISLEADING PASS WORKFLOW & AGGREGATION TESTS
# ============================================================================


def test_phase_2b_flexural_workflow_and_anti_misleading_pass_policy() -> None:
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=440.0)
    conc = ConcreteMaterial(fc_prime_mpa=25.0)
    rebar = RebarMaterial(fy_mpa=400.0)

    # 1. Rectangular singly-reinforced beam where BOTH BG-FLEX-MIN-001 (As,min = 462 mm^2)
    # and BG-FLEX-RECT-SINGLY-001 (phi*Mn >= Mu, tension-controlled) pass -> OverallComplianceStatus.PASS
    report_pass = run_mabhas9_flexural_workflow(
        geom, conc, rebar, as_provided_mm2=1200.0, mu_nmm=150.0e6
    )
    assert report_pass.overall_status == OverallComplianceStatus.PASS
    assert report_pass.is_compliant is True
    assert report_pass.outcomes_by_rule["BG-FLEX-MIN-001"] == EvaluationOutcome.PASS
    assert (
        report_pass.outcomes_by_rule["BG-FLEX-RECT-SINGLY-001"]
        == EvaluationOutcome.PASS
    )

    # 2. Rectangular singly-reinforced beam where BG-FLEX-MIN-001 passes (As = 600 >= 462 mm^2)
    # but Mu exceeds phi*Mn -> OverallComplianceStatus.FAIL
    report_cap_fail = run_mabhas9_flexural_workflow(
        geom, conc, rebar, as_provided_mm2=600.0, mu_nmm=150.0e6
    )
    assert report_cap_fail.overall_status == OverallComplianceStatus.FAIL
    assert report_cap_fail.is_compliant is False
    assert report_cap_fail.outcomes_by_rule["BG-FLEX-MIN-001"] == EvaluationOutcome.PASS
    assert (
        report_cap_fail.outcomes_by_rule["BG-FLEX-RECT-SINGLY-001"]
        == EvaluationOutcome.FAIL
    )

    # 3. Rectangular singly-reinforced beam where phi*Mn >= Mu (Mu = 40 kN*m)
    # but As_provided (300 mm^2) < As,min (462 mm^2) -> OverallComplianceStatus.FAIL
    report_min_fail = run_mabhas9_flexural_workflow(
        geom, conc, rebar, as_provided_mm2=300.0, mu_nmm=40.0e6
    )
    assert report_min_fail.overall_status == OverallComplianceStatus.FAIL
    assert report_min_fail.is_compliant is False
    assert report_min_fail.outcomes_by_rule["BG-FLEX-MIN-001"] == EvaluationOutcome.FAIL
    assert (
        report_min_fail.outcomes_by_rule["BG-FLEX-RECT-SINGLY-001"]
        == EvaluationOutcome.PASS
    )

    # 4. Doubly-reinforced beam in run_mabhas9_flexural_workflow -> OverallComplianceStatus.BLOCKED
    report_doubly_blocked = run_mabhas9_flexural_workflow(
        geom,
        conc,
        rebar,
        as_provided_mm2=1200.0,
        as_compression_mm2=400.0,
        mu_nmm=150.0e6,
    )
    assert report_doubly_blocked.overall_status == OverallComplianceStatus.BLOCKED
    assert report_doubly_blocked.is_compliant is False
    assert (
        report_doubly_blocked.outcomes_by_rule["BG-FLEX-MIN-001"]
        == EvaluationOutcome.PASS
    )
    assert (
        report_doubly_blocked.outcomes_by_rule["BG-FLEX-RECT-DOUBLY-001"]
        == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    )

    # 5. T-beam in run_mabhas9_flexural_workflow -> OverallComplianceStatus.BLOCKED
    geom_t = BeamGeometry(
        bw_mm=300.0,
        h_mm=500.0,
        d_effective_mm=440.0,
        section_type=SectionType.T_SECTION,
        flange_condition=FlangeCondition.FLANGE_IN_COMPRESSION,
        bf_mm=800.0,
        tf_mm=100.0,
    )
    report_t_blocked = run_mabhas9_flexural_workflow(
        geom_t, conc, rebar, as_provided_mm2=1200.0, mu_nmm=150.0e6
    )
    assert report_t_blocked.overall_status == OverallComplianceStatus.BLOCKED
    assert report_t_blocked.is_compliant is False
    assert (
        report_t_blocked.outcomes_by_rule["BG-FLEX-TBEAM-CAP-001"]
        == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    )

    # 6. Full beam check with BG-FLEX-MIN-001 + BG-FLEX-RECT-SINGLY-001 + BG-SHEAR-MIN-001 + BG-SHEAR-SPACING-001
    stirrups = StirrupLayout(
        bar_diameter_mm=10.0,
        num_legs=2,
        longitudinal_spacing_s_mm=200.0,
        transverse_leg_spacing_st_mm=250.0,
    )
    report_beam_pass = run_mabhas9_beam_check(
        geom,
        conc,
        rebar,
        stirrups=stirrups,
        as_provided_mm2=1200.0,
        mu_nmm=150.0e6,
        vs_n=100_000.0,
        requested_rule_ids=(
            "BG-FLEX-MIN-001",
            "BG-FLEX-RECT-SINGLY-001",
            "BG-SHEAR-MIN-001",
            "BG-SHEAR-SPACING-001",
        ),
    )
    assert report_beam_pass.overall_status == OverallComplianceStatus.PASS
    assert report_beam_pass.is_compliant is True

    # Adding an unverified rule (e.g. BG-SHEAR-CAP-BLOCKED or BG-DETAIL-COVER-BLOCKED)
    # prevents a false PASS and yields BLOCKED!
    report_beam_blocked = run_mabhas9_beam_check(
        geom,
        conc,
        rebar,
        stirrups=stirrups,
        as_provided_mm2=1200.0,
        mu_nmm=150.0e6,
        vs_n=100_000.0,
        requested_rule_ids=(
            "BG-FLEX-MIN-001",
            "BG-FLEX-RECT-SINGLY-001",
            "BG-SHEAR-MIN-001",
            "BG-SHEAR-SPACING-001",
            "BG-SHEAR-CAP-BLOCKED",
        ),
    )
    assert report_beam_blocked.overall_status == OverallComplianceStatus.BLOCKED
    assert report_beam_blocked.is_compliant is False


# ============================================================================
# 9. MOSTOFINEJAD VS MABHAS 9 SEPARATION & ARCHITECTURAL ISOLATION
# ============================================================================


def test_phase_2b_mostofinejad_reference_capacity_boundaries_isolated_from_mabhas9() -> None:
    # Mostofinejad Example 5-5 section (b=400, h=500, d=435, fc'=35, fy=400, 3Φ28 -> As=1847.26 mm^2)
    ref_mode = JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY
    b_mm = 400.0
    d_mm = 435.0
    fc_mpa = 35.0
    fy_mpa = 400.0
    as_mm2 = 3.0 * math.pi * (28.0**2) / 4.0

    # 1. In isolated reference mode (CSA A23.3-14):
    # alpha_1 = 0.85 - 0.0015*35 = 0.7975, phi_s = 0.85, phi_c = 0.65
    alpha_1 = evaluate_mostofinejad_eq_5_49_alpha1(
        fc_mpa, jurisdiction_mode=ref_mode
    ).final_result
    assert alpha_1 is not None
    assert alpha_1 == pytest.approx(0.7975, rel=1e-12)
    a_csa_mm = evaluate_mostofinejad_eq_5_54_a(
        as_mm2=as_mm2,
        fy_mpa=fy_mpa,
        fc_prime_mpa=fc_mpa,
        b_mm=b_mm,
        alpha_1=alpha_1,
        phi_s=0.85,
        phi_c=0.65,
        jurisdiction_mode=ref_mode,
    ).final_result
    assert a_csa_mm is not None
    mr_csa_nmm = evaluate_mostofinejad_eq_5_55_mr(
        as_mm2=as_mm2,
        fy_mpa=fy_mpa,
        d_mm=d_mm,
        a_mm=a_csa_mm,
        phi_s=0.85,
        jurisdiction_mode=ref_mode,
    ).final_result
    assert mr_csa_nmm is not None

    assert (
        evaluate_mostofinejad_eq_5_61_check(
            mf_nmm=mr_csa_nmm, mr_nmm=mr_csa_nmm, jurisdiction_mode=ref_mode
        ).outcome
        == EvaluationOutcome.PASS
    )

    # 2. In Mabhas 9 compliance mode, the exact same section uses Mabhas 9 (1399)
    # stress-block (alpha_0 = 0.85, beta_1 = 0.80) and strength reduction factor (phi = 0.90),
    # producing a distinct Iranian code capacity phi*Mn != CSA Mr!
    mabhas_step = evaluate_mabhas9_flexural_capacity(
        BeamGeometry(bw_mm=b_mm, h_mm=500.0, d_effective_mm=d_mm),
        ConcreteMaterial(fc_prime_mpa=fc_mpa),
        RebarMaterial(fy_mpa=fy_mpa),
        as_provided_mm2=as_mm2,
        mu_nmm=240.0e6,
        jurisdiction_mode=JurisdictionMode.MABHAS_9_COMPLIANCE,
    )
    assert mabhas_step.outcome == EvaluationOutcome.PASS
    assert mabhas_step.rule_id == "BG-FLEX-RECT-SINGLY-001"
    assert mabhas_step.intermediate_values["alpha_0"] == pytest.approx(0.85, rel=1e-12)
    assert mabhas_step.intermediate_values["beta_1"] == pytest.approx(0.80, rel=1e-12)
    assert mabhas_step.intermediate_values["phi"] == pytest.approx(0.90, rel=1e-12)
    assert mabhas_step.final_result is not None
    assert mabhas_step.final_result != pytest.approx(mr_csa_nmm, rel=1e-3)


def test_phase_2b_engine_never_imports_reference_module() -> None:
    engine_dir = Path(__file__).resolve().parents[1] / "src" / "beamgenius" / "engine"
    py_files = sorted(engine_dir.glob("*.py"))
    assert len(py_files) >= 3
    for py_file in py_files:
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith("beamgenius.reference"), (
                        f"{py_file.name} imports {alias.name}"
                    )
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                assert not mod.startswith("beamgenius.reference"), (
                    f"{py_file.name} imports from {mod}"
                )
