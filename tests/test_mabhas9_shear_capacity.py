"""Tests for Mabhas 9 (1399) Phase 2C verified one-way shear capacity rules.

Covers:
- ``BG-SHEAR-PHI-001``: φ = 0.75, φVn >= Vu, seismic branch blocking
- ``BG-SHEAR-VC-001``: Eqs. (9-8-12-الف), (9-8-12-ب), (9-8-13), (9-8-14),
  λ / λs boundaries, axial compression/tension branches, Nu/(6Ag) cap,
  Vc bounds (0 <= Vc <= 0.42·λ·√f'c·bw·d), √f'c <= 8.3 MPa waiver
- ``BG-SHEAR-VS-001``: Eqs. (9-8-15), (9-8-16), (9-8-17),
  fyt <= 420 MPa ceiling, vertical vs inclined stirrups
- ``BG-SHEAR-VS-MAX-001``: Eq. (9-8-9), Vs,max boundary, Vu,max boundary
- Anti-misleading hierarchy and blocked unresolved branches
"""

from __future__ import annotations

import math

import pytest

from beamgenius.domain import (
    BeamGeometry,
    ConcreteMaterial,
    EvaluationOutcome,
    OverallComplianceStatus,
    RebarMaterial,
    StirrupLayout,
)
from beamgenius.engine import (
    aggregate_compliance_report,
    evaluate_mabhas9_concrete_shear_resistance_vc,
    evaluate_mabhas9_shear_phi_factor,
    evaluate_mabhas9_shear_web_crushing_limit,
    evaluate_mabhas9_transverse_shear_resistance_vs,
    run_mabhas9_beam_check,
    run_mabhas9_shear_workflow,
)


# ---------------------------------------------------------------------------
# BG-SHEAR-PHI-001 — Shear Strength Reduction Factor φ
# ---------------------------------------------------------------------------


def test_shear_phi_standard_factor_is_075() -> None:
    step = evaluate_mabhas9_shear_phi_factor()
    assert step.outcome == EvaluationOutcome.COMPUTED
    assert step.final_result == pytest.approx(0.75)
    assert step.intermediate_values["phi_shear"] == pytest.approx(0.75)
    assert step.rule_id == "BG-SHEAR-PHI-001"
    assert step.verification_status.value == "VERIFIED"


def test_shear_phi_factored_check_pass_and_fail() -> None:
    # Vc = 120 kN, Vs = 100 kN -> phi*Vn = 0.75 * 220 = 165 kN
    step_pass = evaluate_mabhas9_shear_phi_factor(
        vu_n=165_000.0, vc_n=120_000.0, vs_n=100_000.0
    )
    assert step_pass.outcome == EvaluationOutcome.PASS
    assert step_pass.intermediate_values["phi_vn_n"] == pytest.approx(165_000.0)

    # Exact equality boundary: Vu == phi*Vn -> PASS (>= check)
    step_eq = evaluate_mabhas9_shear_phi_factor(
        vu_n=165_000.0, vc_n=120_000.0, vs_n=100_000.0
    )
    assert step_eq.outcome == EvaluationOutcome.PASS

    step_fail = evaluate_mabhas9_shear_phi_factor(
        vu_n=165_001.0, vc_n=120_000.0, vs_n=100_000.0
    )
    assert step_fail.outcome == EvaluationOutcome.FAIL
    assert any(
        d.code == "INSUFFICIENT_FACTORED_SHEAR_RESISTANCE"
        for d in step_fail.diagnostics
    )


def test_shear_phi_incomplete_check_inputs_is_invalid() -> None:
    # vu_n present, vc_n/vs_n missing -> INVALID_INPUT (anti-misleading)
    step = evaluate_mabhas9_shear_phi_factor(vu_n=100_000.0)
    assert step.outcome == EvaluationOutcome.INVALID_INPUT
    assert any(
        d.code == "INCOMPLETE_FACTORED_SHEAR_CHECK_INPUTS"
        for d in step.diagnostics
    )

    step_2 = evaluate_mabhas9_shear_phi_factor(vc_n=100_000.0, vs_n=50_000.0)
    assert step_2.outcome == EvaluationOutcome.INVALID_INPUT


def test_shear_phi_seismic_branches_blocked() -> None:
    step_cap = evaluate_mabhas9_shear_phi_factor(is_seismic_capacity_governed=True)
    assert step_cap.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert any(
        d.code == "SEISMIC_SHEAR_PHI_UNVERIFIED_BLOCKED"
        for d in step_cap.diagnostics
    )

    step_joint = evaluate_mabhas9_shear_phi_factor(
        is_beam_column_joint_or_diagonal_coupling_beam=True
    )
    assert step_joint.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED


def test_shear_phi_invalid_inputs() -> None:
    step = evaluate_mabhas9_shear_phi_factor(
        vu_n=-1.0, vc_n=50_000.0, vs_n=50_000.0
    )
    assert step.outcome == EvaluationOutcome.INVALID_INPUT


# ---------------------------------------------------------------------------
# BG-SHEAR-VC-001 — Concrete One-Way Shear Resistance Vc
# ---------------------------------------------------------------------------


def test_vc_simplified_eq_9_8_12_a_no_axial() -> None:
    # bw=300, h=500, d=440, fc=25, lambda=1, Nu=0, Av>=Av,min (simplified)
    # Vc = (0.17 * 1 * sqrt(25) + 0) * 300 * 440 = 0.85 * 132000 = 112,200 N
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=440.0)
    step = evaluate_mabhas9_concrete_shear_resistance_vc(
        geom, ConcreteMaterial(fc_prime_mpa=25.0)
    )
    assert step.outcome == EvaluationOutcome.COMPUTED
    expected = 0.17 * 1.0 * 5.0 * 300.0 * 440.0
    assert step.final_result == pytest.approx(expected, rel=1e-12)
    assert step.intermediate_values["selected_equation_branch"] == 1.0
    assert step.intermediate_values["sqrt_fc_effective_mpa"] == pytest.approx(5.0)


def test_vc_detailed_eq_9_8_12_b_with_rho_w() -> None:
    # rho_w = 0.01 -> cbrt = 0.01^(1/3) = 0.215443...
    # Vc = (0.66 * 1 * 0.215443 * sqrt(25)) * 300 * 440 = ...
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=440.0)
    rho_w = 0.01
    step = evaluate_mabhas9_concrete_shear_resistance_vc(
        geom,
        ConcreteMaterial(fc_prime_mpa=25.0),
        use_detailed_rho_w_equation=True,
        rho_w=rho_w,
    )
    assert step.outcome == EvaluationOutcome.COMPUTED
    expected = (
        0.66 * 1.0 * (rho_w ** (1.0 / 3.0)) * math.sqrt(25.0) * 300.0 * 440.0
    )
    assert step.final_result == pytest.approx(expected, rel=1e-9)
    assert step.intermediate_values["selected_equation_branch"] == 2.0


def test_vc_axial_compression_branch_and_nu_6ag_cap() -> None:
    # bw=300,h=500 -> Ag = 150,000 mm2 (default); fc=25; fc cap: 0.05*25 = 1.25 MPa
    # Nu = +600 kN compression -> Nu/(6*Ag) = 600000/(6*150000) = 0.6666... MPa
    # sigma_eff = min(0.6667, 1.25) = 0.6667
    # Vc = (0.17*5 + 0.66667) * 300 * 440 = (0.85+0.66667)*132000 = 200,200 N
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=440.0)
    step_comp = evaluate_mabhas9_concrete_shear_resistance_vc(
        geom, ConcreteMaterial(fc_prime_mpa=25.0), nu_n=600_000.0
    )
    assert step_comp.outcome == EvaluationOutcome.COMPUTED
    expected = (0.17 * 5.0 + 600_000.0 / (6.0 * 150_000.0)) * 300.0 * 440.0
    assert step_comp.final_result == pytest.approx(expected, rel=1e-9)
    assert step_comp.intermediate_values["sigma_n_effective_mpa"] == pytest.approx(
        600_000.0 / (6.0 * 150_000.0), rel=1e-9
    )

    # Very large compression -> Nu/(6Ag) capped at 0.05*fc = 1.25 MPa
    # Nu = 2,000,000 N -> Nu/(6*Ag) = 2.222 MPa > 1.25 -> capped
    step_capped = evaluate_mabhas9_concrete_shear_resistance_vc(
        geom, ConcreteMaterial(fc_prime_mpa=25.0), nu_n=2_000_000.0
    )
    assert step_capped.outcome == EvaluationOutcome.COMPUTED
    assert step_capped.intermediate_values["sigma_n_effective_mpa"] == pytest.approx(
        0.05 * 25.0, rel=1e-12
    )
    expected_capped = (0.17 * 5.0 + 0.05 * 25.0) * 300.0 * 440.0
    assert step_capped.final_result == pytest.approx(expected_capped, rel=1e-9)


def test_vc_axial_tension_branch_negative_nu() -> None:
    # Nu = -300 kN tension -> Nu/(6*Ag) = -300000/900000 = -0.33333 MPa
    # sigma_eff = min(-0.3333, 1.25) = -0.3333
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=440.0)
    step = evaluate_mabhas9_concrete_shear_resistance_vc(
        geom, ConcreteMaterial(fc_prime_mpa=25.0), nu_n=-300_000.0
    )
    assert step.outcome == EvaluationOutcome.COMPUTED
    expected = (
        0.17 * 5.0 - 300_000.0 / (6.0 * 150_000.0)
    ) * 300.0 * 440.0
    assert step.final_result == pytest.approx(expected, rel=1e-9)

    # Large tension -> Vc_raw pushed negative -> floored at 0
    step_floor = evaluate_mabhas9_concrete_shear_resistance_vc(
        geom, ConcreteMaterial(fc_prime_mpa=25.0), nu_n=-5_000_000.0
    )
    assert step_floor.outcome == EvaluationOutcome.COMPUTED
    assert step_floor.intermediate_values["vc_raw_n"] < 0.0
    assert step_floor.final_result == 0.0


def test_vc_upper_bound_042_ceiling() -> None:
    # Construct case where Vc_raw exceeds 0.42*lambda*sqrt(fc)*bw*d:
    # bw=300,h=500,d=440,fc=100 (structural max 70; but waiver keeps full sqrt
    # when Av>=Av,min per Clause 9-8-4-2-2 exception). Use fc=70, huge Ag so
    # Nu/(6*Ag) hits cap 0.05*70 = 3.5 MPa.
    # Vc_raw stress = 0.17*sqrt(70)+3.5 = 1.4224+3.5 = 4.9224 MPa
    # cap = 0.42*sqrt(70) = 3.5129 MPa -> Vc forced to cap stress.
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=440.0)
    step = evaluate_mabhas9_concrete_shear_resistance_vc(
        geom,
        ConcreteMaterial(fc_prime_mpa=70.0),
        nu_n=2_000_000.0,
        ag_mm2=100_000.0,  # Nu/(6*Ag) = 2000000/600000 = 3.333 <= 3.5 cap
    )
    assert step.outcome == EvaluationOutcome.COMPUTED
    vc_max = 0.42 * math.sqrt(70.0) * 300.0 * 440.0
    assert step.intermediate_values["vc_raw_n"] > vc_max
    assert step.final_result == pytest.approx(vc_max, rel=1e-9)


def test_vc_lightweight_lambda_branch() -> None:
    # lambda = 0.75 (all-lightweight)
    # Vc = (0.17 * 0.75 * 5.0 + 0) * 300 * 440 = 0.6375 * 132000 = 84,150 N
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=440.0)
    step = evaluate_mabhas9_concrete_shear_resistance_vc(
        geom, ConcreteMaterial(fc_prime_mpa=25.0, lambda_factor=0.75)
    )
    assert step.outcome == EvaluationOutcome.COMPUTED
    expected = 0.17 * 0.75 * 5.0 * 300.0 * 440.0
    assert step.final_result == pytest.approx(expected, rel=1e-12)

    # Invalid lambda outside [0.75, 1.0] -> INVALID_INPUT
    step_bad = evaluate_mabhas9_concrete_shear_resistance_vc(
        geom, ConcreteMaterial(fc_prime_mpa=25.0, lambda_factor=0.70)
    )
    assert step_bad.outcome == EvaluationOutcome.INVALID_INPUT


def test_vc_size_effect_lambda_s_branch_av_lt_min() -> None:
    # Av < Av,min -> Eq. (9-8-13) with lambda_s
    # d = 750 mm -> lambda_s = sqrt(2/(1+750/250)) = sqrt(2/4) = 0.70710...
    # rho_w = 0.01; Vc = (0.66*lambda_s*1*cbrt(0.01)*sqrt(25)) * bw*d
    geom = BeamGeometry(bw_mm=300.0, h_mm=850.0, d_effective_mm=750.0)
    rho_w = 0.01
    step = evaluate_mabhas9_concrete_shear_resistance_vc(
        geom,
        ConcreteMaterial(fc_prime_mpa=25.0),
        has_minimum_shear_reinforcement=False,
        rho_w=rho_w,
    )
    assert step.outcome == EvaluationOutcome.COMPUTED
    lambda_s_expected = math.sqrt(2.0 / (1.0 + 750.0 / 250.0))
    assert step.intermediate_values["lambda_s"] == pytest.approx(
        lambda_s_expected, rel=1e-9
    )
    expected = (
        0.66
        * lambda_s_expected
        * 1.0
        * (rho_w ** (1.0 / 3.0))
        * math.sqrt(25.0)
        * 300.0
        * 750.0
    )
    assert step.final_result == pytest.approx(expected, rel=1e-9)
    assert step.intermediate_values["selected_equation_branch"] == 3.0


def test_vc_lambda_s_exact_boundary_d_250() -> None:
    # d = 250 mm -> lambda_s = sqrt(2/(1+1)) = sqrt(1) = 1.0 -> capped at 1.0
    geom = BeamGeometry(bw_mm=300.0, h_mm=310.0, d_effective_mm=250.0)
    step = evaluate_mabhas9_concrete_shear_resistance_vc(
        geom,
        ConcreteMaterial(fc_prime_mpa=25.0),
        has_minimum_shear_reinforcement=False,
        rho_w=0.01,
    )
    assert step.outcome == EvaluationOutcome.COMPUTED
    assert step.intermediate_values["lambda_s"] == pytest.approx(1.0, rel=1e-12)

    # d = 250.1 mm -> lambda_s = sqrt(2/(1+1.0004)) = sqrt(0.999800...) < 1.0
    geom_2 = BeamGeometry(bw_mm=300.0, h_mm=310.0, d_effective_mm=250.1)
    step_2 = evaluate_mabhas9_concrete_shear_resistance_vc(
        geom_2,
        ConcreteMaterial(fc_prime_mpa=25.0),
        has_minimum_shear_reinforcement=False,
        rho_w=0.01,
    )
    assert step_2.outcome == EvaluationOutcome.COMPUTED
    assert step_2.intermediate_values["lambda_s"] < 1.0


def test_vc_eq_9_8_13_not_applicable_when_rho_w_zero() -> None:
    # Av < Av,min AND rho_w = 0 -> Eq. (9-8-13) not applicable -> BLOCKED
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=440.0)
    step = evaluate_mabhas9_concrete_shear_resistance_vc(
        geom,
        ConcreteMaterial(fc_prime_mpa=25.0),
        has_minimum_shear_reinforcement=False,
        rho_w=0.0,
    )
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert any(
        d.code == "VC_EQ_9_8_13_NOT_APPLICABLE_ZERO_RHO_W"
        for d in step.diagnostics
    )


def test_vc_detailed_requires_rho_w() -> None:
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=440.0)
    step = evaluate_mabhas9_concrete_shear_resistance_vc(
        geom,
        ConcreteMaterial(fc_prime_mpa=25.0),
        use_detailed_rho_w_equation=True,
        rho_w=None,
    )
    assert step.outcome == EvaluationOutcome.INVALID_INPUT
    assert any(
        d.code == "MISSING_RHO_W_FOR_DETAILED_VC" for d in step.diagnostics
    )


def test_vc_rho_w_from_as_longitudinal_and_geometry() -> None:
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=440.0)
    # As provided directly: rho_w = 1320 / (300*440) = 0.01
    step = evaluate_mabhas9_concrete_shear_resistance_vc(
        geom,
        ConcreteMaterial(fc_prime_mpa=25.0),
        use_detailed_rho_w_equation=True,
        as_longitudinal_tension_mm2=1320.0,
    )
    assert step.outcome == EvaluationOutcome.COMPUTED
    assert step.intermediate_values["rho_w"] == pytest.approx(0.01, rel=1e-12)


def test_vc_material_and_geometry_limits() -> None:
    # Invalid geometry -> INVALID_INPUT
    bad_geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=500.0)
    step_d = evaluate_mabhas9_concrete_shear_resistance_vc(
        bad_geom, ConcreteMaterial(fc_prime_mpa=25.0)
    )
    assert step_d.outcome == EvaluationOutcome.INVALID_INPUT

    # No effective depth resolvable -> INVALID_INPUT
    geom_no_d = BeamGeometry(bw_mm=300.0, h_mm=500.0)
    step_no_d = evaluate_mabhas9_concrete_shear_resistance_vc(
        geom_no_d, ConcreteMaterial(fc_prime_mpa=25.0)
    )
    assert step_no_d.outcome == EvaluationOutcome.INVALID_INPUT

    # Invalid concrete strength -> INVALID_INPUT
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=440.0)
    step_fc = evaluate_mabhas9_concrete_shear_resistance_vc(
        geom, ConcreteMaterial(fc_prime_mpa=0.0)
    )
    assert step_fc.outcome == EvaluationOutcome.INVALID_INPUT


def test_vc_special_condition_blocked_branches() -> None:
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=440.0)
    concrete = ConcreteMaterial(fc_prime_mpa=25.0)
    for kwargs in (
        {"has_web_openings": True},
        {"is_variable_depth_member": True},
        {"is_circular_section": True},
        {"is_one_way_joist_member": True},
        {"is_seismic_frame_hinge_region": True},
    ):
        step = evaluate_mabhas9_concrete_shear_resistance_vc(
            geom, concrete, **kwargs  # type: ignore[arg-type]
        )
        assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
        assert any(
            d.code == "VC_SPECIAL_CONDITION_UNVERIFIED_BLOCKED"
            for d in step.diagnostics
        )


def test_vc_sqrt_fc_83_cap_when_av_below_min() -> None:
    # Av < Av,min -> general cap sqrt(fc) <= 8.3 (Clause 9-8-4-2-2)
    # fc = 100 MPa would be sqrt=10, capped to 8.3. (fc=70 structural max stays
    # below anyway; use cap logic check via has_minimum_shear_reinforcement=False
    # with simplified-like path? Simplified only applies when Av>=Av,min, so
    # with Av<Av,min Eq. 9-8-13 applies with lambda_s & rho_w.)
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=440.0)
    rho_w = 0.02
    step_capped = evaluate_mabhas9_concrete_shear_resistance_vc(
        geom,
        ConcreteMaterial(fc_prime_mpa=70.0),
        has_minimum_shear_reinforcement=False,
        rho_w=rho_w,
    )
    # sqrt(70) = 8.3666 > 8.3 -> capped at 8.3
    assert step_capped.intermediate_values["sqrt_fc_effective_mpa"] == pytest.approx(
        8.3, rel=1e-12
    )

    # Av >= Av,min -> waiver -> full sqrt(fc)
    step_waived = evaluate_mabhas9_concrete_shear_resistance_vc(
        geom, ConcreteMaterial(fc_prime_mpa=70.0)
    )
    assert step_waived.intermediate_values["sqrt_fc_effective_mpa"] == pytest.approx(
        math.sqrt(70.0), rel=1e-12
    )


# ---------------------------------------------------------------------------
# BG-SHEAR-VS-001 — Transverse Shear Resistance Vs and Demand
# ---------------------------------------------------------------------------


def test_vs_vertical_stirrups_eq_9_8_16() -> None:
    # 2-leg dia10 @ 200 mm, d = 440 mm, fyt = 400 MPa
    # Av = 2*pi*100/4 = 157.0796 mm2; Av/s = 0.785398 mm2/mm
    # Vs = 0.785398 * 400 * 440 = 138,230 N
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=440.0)
    rebar = RebarMaterial(fy_mpa=400.0, fyt_mpa=400.0)
    stirrups = StirrupLayout(
        bar_diameter_mm=10.0, num_legs=2, longitudinal_spacing_s_mm=200.0
    )
    step = evaluate_mabhas9_transverse_shear_resistance_vs(
        geom, ConcreteMaterial(fc_prime_mpa=25.0), rebar, stirrups=stirrups
    )
    assert step.outcome == EvaluationOutcome.COMPUTED
    av_s = 2.0 * math.pi * 100.0 / 4.0 / 200.0
    expected = av_s * 400.0 * 440.0
    assert step.final_result == pytest.approx(expected, rel=1e-9)
    assert step.intermediate_values["sin_plus_cos_alpha"] == pytest.approx(1.0)


def test_vs_inclined_stirrups_eq_9_8_17() -> None:
    # alpha = 45 deg -> sin+cos = sqrt(2) = 1.414213...
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=440.0)
    rebar = RebarMaterial(fy_mpa=400.0, fyt_mpa=400.0)
    stirrups = StirrupLayout(
        bar_diameter_mm=10.0, num_legs=2, longitudinal_spacing_s_mm=200.0
    )
    step = evaluate_mabhas9_transverse_shear_resistance_vs(
        geom,
        ConcreteMaterial(fc_prime_mpa=25.0),
        rebar,
        stirrups=stirrups,
        stirrup_angle_deg=45.0,
    )
    assert step.outcome == EvaluationOutcome.COMPUTED
    av_s = 2.0 * math.pi * 100.0 / 4.0 / 200.0
    expected = av_s * 400.0 * math.sqrt(2.0) * 440.0
    assert step.final_result == pytest.approx(expected, rel=1e-9)
    assert step.intermediate_values["sin_plus_cos_alpha"] == pytest.approx(
        math.sqrt(2.0), rel=1e-12
    )

    # alpha = 60 deg -> sin60+cos60 = 0.866+0.5 = 1.3660...
    step60 = evaluate_mabhas9_transverse_shear_resistance_vs(
        geom,
        ConcreteMaterial(fc_prime_mpa=25.0),
        rebar,
        stirrups=stirrups,
        stirrup_angle_deg=60.0,
    )
    assert step60.intermediate_values["sin_plus_cos_alpha"] == pytest.approx(
        math.sin(math.radians(60.0)) + math.cos(math.radians(60.0)), rel=1e-12
    )

    # Exact boundary alpha = 45.0 allowed; alpha = 44.9 -> INVALID_INPUT
    step_invalid = evaluate_mabhas9_transverse_shear_resistance_vs(
        geom,
        ConcreteMaterial(fc_prime_mpa=25.0),
        rebar,
        stirrups=stirrups,
        stirrup_angle_deg=44.9,
    )
    assert step_invalid.outcome == EvaluationOutcome.INVALID_INPUT
    assert any(
        d.code == "INVALID_STIRRUP_ANGLE" for d in step_invalid.diagnostics
    )


def test_vs_fyt_ceiling_420_mpa() -> None:
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=440.0)
    # fyt = 420 -> OK
    step_ok = evaluate_mabhas9_transverse_shear_resistance_vs(
        geom,
        ConcreteMaterial(fc_prime_mpa=25.0),
        RebarMaterial(fy_mpa=420.0, fyt_mpa=420.0),
        av_over_s_provided_mm2_per_mm=0.5,
    )
    assert step_ok.outcome == EvaluationOutcome.COMPUTED

    # fyt > 420 -> INVALID_INPUT
    step_bad = evaluate_mabhas9_transverse_shear_resistance_vs(
        geom,
        ConcreteMaterial(fc_prime_mpa=25.0),
        RebarMaterial(fy_mpa=500.0, fyt_mpa=500.0),
        av_over_s_provided_mm2_per_mm=0.5,
    )
    assert step_bad.outcome == EvaluationOutcome.INVALID_INPUT
    assert any(
        d.code == "FYT_EXCEEDS_MABHAS9_SHEAR_LIMIT" for d in step_bad.diagnostics
    )


def test_vs_demand_eq_9_8_15_and_required_av_over_s() -> None:
    # Vu = 180 kN, Vc = 100 kN, phi = 0.75
    # Vs,req = max(180000/0.75 - 100000, 0) = 140,000 N
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=440.0)
    step = evaluate_mabhas9_transverse_shear_resistance_vs(
        geom,
        ConcreteMaterial(fc_prime_mpa=25.0),
        RebarMaterial(fy_mpa=400.0, fyt_mpa=400.0),
        vu_n=180_000.0,
        vc_n=100_000.0,
    )
    assert step.outcome == EvaluationOutcome.COMPUTED
    assert step.final_result == pytest.approx(140_000.0, rel=1e-9)
    expected_av_s = 140_000.0 / (400.0 * 1.0 * 440.0)
    assert step.intermediate_values[
        "av_over_s_required_mm2_per_mm"
    ] == pytest.approx(expected_av_s, rel=1e-9)

    # Vu/phi < Vc -> Vs,req floored at 0
    step_zero = evaluate_mabhas9_transverse_shear_resistance_vs(
        geom,
        ConcreteMaterial(fc_prime_mpa=25.0),
        RebarMaterial(fy_mpa=400.0),
        vu_n=50_000.0,
        vc_n=100_000.0,
    )
    assert step_zero.outcome == EvaluationOutcome.COMPUTED
    assert step_zero.intermediate_values["vs_required_n"] == 0.0


def test_vs_pass_and_fail_against_demand() -> None:
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=440.0)
    rebar = RebarMaterial(fy_mpa=400.0, fyt_mpa=400.0)
    stirrups = StirrupLayout(
        bar_diameter_mm=10.0, num_legs=2, longitudinal_spacing_s_mm=100.0
    )
    # Av/s = 157.0796/100 = 1.5708; Vs_prov = 1.5708*400*440 = 276,460 N
    # VS req (Vu=300k, Vc=100k): 300000/0.75 - 100000 = 300,000 N -> FAIL
    step_fail = evaluate_mabhas9_transverse_shear_resistance_vs(
        geom,
        ConcreteMaterial(fc_prime_mpa=25.0),
        rebar,
        stirrups=stirrups,
        vu_n=300_000.0,
        vc_n=100_000.0,
    )
    assert step_fail.outcome == EvaluationOutcome.FAIL
    assert any(
        d.code == "INSUFFICIENT_TRANSVERSE_SHEAR_RESISTANCE"
        for d in step_fail.diagnostics
    )

    # Vu = 250k -> Vs,req = 250000/0.75-100000 = 233,333 < 276,460 -> PASS
    step_pass = evaluate_mabhas9_transverse_shear_resistance_vs(
        geom,
        ConcreteMaterial(fc_prime_mpa=25.0),
        rebar,
        stirrups=stirrups,
        vu_n=250_000.0,
        vc_n=100_000.0,
    )
    assert step_pass.outcome == EvaluationOutcome.PASS


def test_vs_blocked_bent_up_bars_and_spirals() -> None:
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=440.0)
    step1 = evaluate_mabhas9_transverse_shear_resistance_vs(
        geom,
        ConcreteMaterial(fc_prime_mpa=25.0),
        RebarMaterial(fy_mpa=400.0),
        uses_bent_up_longitudinal_bars=True,
        vu_n=100_000.0,
        vc_n=60_000.0,
    )
    assert step1.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert any(
        d.code == "VS_SPECIAL_REINFORCEMENT_UNVERIFIED_BLOCKED"
        for d in step1.diagnostics
    )

    step2 = evaluate_mabhas9_transverse_shear_resistance_vs(
        geom,
        ConcreteMaterial(fc_prime_mpa=25.0),
        RebarMaterial(fy_mpa=400.0),
        uses_circular_hoops_or_spirals=True,
    )
    assert step2.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED


def test_vs_invalid_and_incomplete_inputs() -> None:
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=440.0)
    # Only vu_n (no vc_n) -> INVALID_INPUT
    step_partial = evaluate_mabhas9_transverse_shear_resistance_vs(
        geom,
        ConcreteMaterial(fc_prime_mpa=25.0),
        RebarMaterial(fy_mpa=400.0),
        vu_n=100_000.0,
    )
    assert step_partial.outcome == EvaluationOutcome.INVALID_INPUT
    assert any(
        d.code == "INCOMPLETE_SHEAR_DEMAND_INPUTS" for d in step_partial.diagnostics
    )

    # Nothing provided at all -> INVALID_INPUT
    step_none = evaluate_mabhas9_transverse_shear_resistance_vs(
        geom,
        ConcreteMaterial(fc_prime_mpa=25.0),
        RebarMaterial(fy_mpa=400.0),
    )
    assert step_none.outcome == EvaluationOutcome.INVALID_INPUT


# ---------------------------------------------------------------------------
# BG-SHEAR-VS-MAX-001 — Web-Crushing Limit
# ---------------------------------------------------------------------------


def test_vs_max_compute_and_boundary_eq_9_8_9() -> None:
    # bw=300, d=440, fc=25, Av>=Av,min -> sqrt fc full
    # Vs,max = 0.66 * 5 * 300 * 440 = 435,600 N
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=440.0)
    concrete = ConcreteMaterial(fc_prime_mpa=25.0)
    step = evaluate_mabhas9_shear_web_crushing_limit(geom, concrete)
    assert step.outcome == EvaluationOutcome.COMPUTED
    expected = 0.66 * 5.0 * 300.0 * 440.0
    assert step.final_result == pytest.approx(expected, rel=1e-12)

    # Exact equality Vs == Vs,max -> PASS
    step_eq = evaluate_mabhas9_shear_web_crushing_limit(
        geom, concrete, vs_n=expected
    )
    assert step_eq.outcome == EvaluationOutcome.PASS

    # Vs slightly above -> FAIL
    step_above = evaluate_mabhas9_shear_web_crushing_limit(
        geom, concrete, vs_n=expected + 1.0
    )
    assert step_above.outcome == EvaluationOutcome.FAIL
    assert any(
        d.code == "VS_EXCEEDS_WEB_CRUSHING_LIMIT" for d in step_above.diagnostics
    )


def test_vu_max_check_with_vc() -> None:
    # Vs,max = 435,600 N; Vc = 120,000 N; phi=0.75
    # Vu,max = 0.75*(120000+435600) = 416,700 N
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=440.0)
    concrete = ConcreteMaterial(fc_prime_mpa=25.0)
    step_pass = evaluate_mabhas9_shear_web_crushing_limit(
        geom, concrete, vu_n=416_700.0, vc_n=120_000.0
    )
    assert step_pass.outcome == EvaluationOutcome.PASS
    assert step_pass.intermediate_values["vu_max_n"] == pytest.approx(
        0.75 * (120_000.0 + 435_600.0), rel=1e-9
    )

    step_fail = evaluate_mabhas9_shear_web_crushing_limit(
        geom, concrete, vu_n=416_701.0, vc_n=120_000.0
    )
    assert step_fail.outcome == EvaluationOutcome.FAIL
    assert any(
        d.code == "VU_EXCEEDS_SECTION_DIMENSION_LIMIT"
        for d in step_fail.diagnostics
    )

    # vu_n without vc_n -> INVALID_INPUT (anti-misleading)
    step_missing = evaluate_mabhas9_shear_web_crushing_limit(
        geom, concrete, vu_n=100_000.0
    )
    assert step_missing.outcome == EvaluationOutcome.INVALID_INPUT


def test_vs_max_torsion_interaction_blocked() -> None:
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=440.0)
    step = evaluate_mabhas9_shear_web_crushing_limit(
        geom,
        ConcreteMaterial(fc_prime_mpa=25.0),
        vs_n=100_000.0,
        tu_nmm=5e6,
    )
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert any(
        d.code == "SHEAR_TORSION_INTERACTION_UNVERIFIED_BLOCKED"
        for d in step.diagnostics
    )


def test_vs_max_invalid_inputs() -> None:
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=440.0)
    step = evaluate_mabhas9_shear_web_crushing_limit(
        geom, ConcreteMaterial(fc_prime_mpa=25.0), vs_n=-1.0
    )
    assert step.outcome == EvaluationOutcome.INVALID_INPUT

    geom_no_d = BeamGeometry(bw_mm=300.0, h_mm=500.0)
    step_no_d = evaluate_mabhas9_shear_web_crushing_limit(
        geom_no_d, ConcreteMaterial(fc_prime_mpa=25.0)
    )
    assert step_no_d.outcome == EvaluationOutcome.INVALID_INPUT


# ---------------------------------------------------------------------------
# Orchestration & anti-misleading integration
# ---------------------------------------------------------------------------


def test_run_mabhas9_shear_workflow_end_to_end_pass() -> None:
    # Consistent fully passing setup:
    # bw=300, h=500, d=440, fc=25, Nu=0, lambda=1
    # Vc (simplified) = 112,200 N
    # stirrups 2Φ10@100: Av/s = 1.5708 -> Vs = 276,460 N
    # Vs,max = 435,600 N > 276,460 -> OK
    # Vu = 200,000 N:
    #   Vs,req = 200000/0.75 - 112200 = 154,467 < 276,460 -> PASS
    #   Vu,max = 0.75*(112200+435600) = 410,850 > 200,000 -> PASS
    #   phiVn = 0.75*(112200+276460) = 291,495 > 200,000 -> PASS
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=440.0)
    concrete = ConcreteMaterial(fc_prime_mpa=25.0)
    rebar = RebarMaterial(fy_mpa=400.0, fyt_mpa=400.0)
    stirrups = StirrupLayout(
        bar_diameter_mm=10.0, num_legs=2, longitudinal_spacing_s_mm=100.0
    )
    steps = run_mabhas9_shear_workflow(
        geom,
        concrete,
        rebar,
        stirrups=stirrups,
        vu_n=200_000.0,
    )
    outcomes = [s.outcome for s in steps]
    assert EvaluationOutcome.INVALID_INPUT not in outcomes
    assert EvaluationOutcome.UNVERIFIED_RULE_BLOCKED not in outcomes
    assert EvaluationOutcome.FAIL not in outcomes

    # Workflow includes Vc, phi, Vs, Vs,max and final phi-check steps
    rule_ids = [s.rule_id for s in steps]
    assert rule_ids[0] == "BG-SHEAR-VC-001"
    assert rule_ids[3] == "BG-SHEAR-VS-MAX-001"
    assert rule_ids[-1] == "BG-SHEAR-PHI-001"
    assert steps[-1].outcome == EvaluationOutcome.PASS

    # Anti-misleading aggregation: Vc and phi-only steps are COMPUTED
    # (capacity/factor computations), so the workflow is PARTIAL (no FAIL /
    # BLOCKED / INVALID_INPUT and all demand-check steps PASS).
    report = aggregate_compliance_report(steps)
    assert report.overall_status == OverallComplianceStatus.PARTIAL
    assert report.outcomes_by_rule["BG-SHEAR-VS-001"] == EvaluationOutcome.PASS
    assert report.outcomes_by_rule["BG-SHEAR-VS-MAX-001"] == EvaluationOutcome.PASS
    # Duplicate BG-SHEAR-PHI-001 steps merge by documented dominance:
    # COMPUTED (phi constant) dominates PASS for the per-rule outcome,
    # while the final full phi-check step itself is PASS.
    assert report.outcomes_by_rule["BG-SHEAR-PHI-001"] == EvaluationOutcome.COMPUTED


def test_run_mabhas9_beam_check_with_verified_shear_rules() -> None:
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=440.0)
    concrete = ConcreteMaterial(fc_prime_mpa=25.0)
    rebar = RebarMaterial(fy_mpa=400.0, fyt_mpa=400.0)
    stirrups = StirrupLayout(
        bar_diameter_mm=10.0, num_legs=2, longitudinal_spacing_s_mm=100.0
    )
    # Full demand chain supplied (Vc = 0.17*sqrt(25)*300*440 = 112,200 N)
    report = run_mabhas9_beam_check(
        geom,
        concrete,
        rebar,
        stirrups=stirrups,
        vu_n=200_000.0,
        vc_n=112_200.0,
        requested_rule_ids=(
            "BG-SHEAR-VC-001",
            "BG-SHEAR-VS-001",
            "BG-SHEAR-VS-MAX-001",
        ),
    )
    assert report.outcomes_by_rule["BG-SHEAR-VC-001"] == EvaluationOutcome.COMPUTED
    assert report.outcomes_by_rule["BG-SHEAR-VS-001"] == EvaluationOutcome.PASS
    assert report.outcomes_by_rule["BG-SHEAR-VS-MAX-001"] == EvaluationOutcome.PASS
    assert report.overall_status == OverallComplianceStatus.PARTIAL

    # vu_n without vc_n -> demand evaluation inputs incomplete -> INVALID_INPUT
    report_incomplete = run_mabhas9_beam_check(
        geom,
        concrete,
        rebar,
        stirrups=stirrups,
        vu_n=200_000.0,
        requested_rule_ids=("BG-SHEAR-VS-001",),
    )
    assert report_incomplete.overall_status == OverallComplianceStatus.INVALID_INPUT


def test_phase2b_flexural_rules_unchanged_regression() -> None:
    # Anti-misleading: BLOCKED dominates PASS/COMPUTED; a blocked legacy rule
    # keeps the report BLOCKED even when verified shear rules succeed.
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=440.0)
    concrete = ConcreteMaterial(fc_prime_mpa=25.0)
    rebar = RebarMaterial(fy_mpa=400.0)
    report = run_mabhas9_beam_check(
        geom,
        concrete,
        rebar,
        stirrups=StirrupLayout(
            bar_diameter_mm=10.0, num_legs=2, longitudinal_spacing_s_mm=100.0
        ),
        vu_n=200_000.0,
        requested_rule_ids=(
            "BG-SHEAR-VC-001",
            "BG-FLEX-TBEAM-CAP-001",
        ),
    )
    assert report.overall_status == OverallComplianceStatus.BLOCKED
    assert (
        report.outcomes_by_rule["BG-FLEX-TBEAM-CAP-001"]
        == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    )
    assert report.outcomes_by_rule["BG-SHEAR-VC-001"] == EvaluationOutcome.COMPUTED
