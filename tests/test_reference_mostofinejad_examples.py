"""Isolated textbook regression tests for Mostofinejad Vol. 1 Chapter 5."""

from __future__ import annotations

import pytest

from beamgenius.domain import (
    BeamGeometry,
    EvaluationOutcome,
    JurisdictionMode,
    RebarGroup,
)
from beamgenius.engine import evaluate_longitudinal_bar_clear_spacing
from beamgenius.rebar import evaluate_rebar_combination
from beamgenius.reference import (
    evaluate_mostofinejad_eq_5_46_kn,
    evaluate_mostofinejad_eq_5_47_bd2,
    evaluate_mostofinejad_eq_5_48a_d_estimate,
    evaluate_mostofinejad_eq_5_48b_d_estimate,
    evaluate_mostofinejad_eq_5_49_alpha1,
    evaluate_mostofinejad_eq_5_50_beta1,
    evaluate_mostofinejad_eq_5_54_a,
    evaluate_mostofinejad_eq_5_55_mr,
    evaluate_mostofinejad_eq_5_56_mr_rho,
    evaluate_mostofinejad_eq_5_61_check,
    solve_mostofinejad_flexural_steel_from_kn,
)


def test_mostofinejad_example_5_5_regression() -> None:
    """Mostofinejad Vol. 1 Example 5-5 (PDF pp. 212-213, Printed pp. 201-202).

    Given:
        b = 400 mm, h = 500 mm, Mu = 240 kN*m, f'c = 35 MPa, fy = 400 MPa, 1 layer.
    Expected textbook values:
        d = 435 mm (from Eq. 5-48-a)
        As ≈ 1636 mm^2
        2Φ25 + 1Φ30 ≈ 1689 mm^2
        3Φ28 ≈ 1847 mm^2
    """
    mode = JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY
    step_d = evaluate_mostofinejad_eq_5_48a_d_estimate(500.0, jurisdiction_mode=mode)
    assert step_d.outcome == EvaluationOutcome.COMPUTED
    assert step_d.final_result == pytest.approx(435.0, rel=1e-12)

    step_47, step_46 = solve_mostofinejad_flexural_steel_from_kn(
        b_mm=400.0,
        d_mm=435.0,
        mu_nmm=240.0e6,
        fc_prime_mpa=35.0,
        fy_mpa=400.0,
        phi=0.90,
        jurisdiction_mode=mode,
    )
    assert step_47.outcome == EvaluationOutcome.COMPUTED
    assert step_46.outcome == EvaluationOutcome.COMPUTED
    assert step_46.final_result is not None
    assert round(step_46.final_result) == 1636
    assert step_46.final_result == pytest.approx(1636.33, abs=0.5)

    # Candidate 1: 2Φ25 + 1Φ30 ≈ 1689 mm^2
    cand_1 = evaluate_rebar_combination(
        (
            RebarGroup(bar_diameter_mm=25.0, bar_count=2),
            RebarGroup(bar_diameter_mm=30.0, bar_count=1),
        ),
        target_area_mm2=step_46.final_result,
    )
    assert round(cand_1.total_area_mm2) == 1689
    assert cand_1.constructability_verified is False

    # Candidate 2: 3Φ28 ≈ 1847 mm^2
    cand_2 = evaluate_rebar_combination(
        (RebarGroup(bar_diameter_mm=28.0, bar_count=3),),
        target_area_mm2=step_46.final_result,
    )
    assert round(cand_2.total_area_mm2) == 1847
    assert cand_2.constructability_verified is False


def test_mostofinejad_example_5_6_main_and_alternative_regression() -> None:
    """Mostofinejad Vol. 1 Example 5-6 (PDF pp. 213-216, Printed pp. 202-205).

    Main case:
        b = 350 mm, h = 600 mm, d = 535 mm, M_max = 401.6 kN*m, f'c = 28 MPa, fy = 350 MPa.
        Reported As ≈ 2659 mm^2, selection 4Φ30 = 2827 mm^2.

    Alternative case:
        b = 300 mm, h = 550 mm, d = 485 mm.
        Reported As ≈ 3056 mm^2, 4Φ32 = 3217 mm^2, 3Φ36 = 3054 mm^2.
    """
    mode = JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY

    # Main case d estimate (600 - 65 = 535 mm)
    step_d_main = evaluate_mostofinejad_eq_5_48a_d_estimate(600.0, jurisdiction_mode=mode)
    assert step_d_main.final_result == pytest.approx(535.0)

    # Unrounded calculation and textbook-rounded rho = 0.0142 calculation
    _, step_main_unrounded = solve_mostofinejad_flexural_steel_from_kn(
        b_mm=350.0,
        d_mm=535.0,
        mu_nmm=401.6e6,
        fc_prime_mpa=28.0,
        fy_mpa=350.0,
        phi=0.90,
        jurisdiction_mode=mode,
    )
    assert step_main_unrounded.final_result == pytest.approx(2659.0, rel=0.002)

    _, step_main_textbook = solve_mostofinejad_flexural_steel_from_kn(
        b_mm=350.0,
        d_mm=535.0,
        mu_nmm=401.6e6,
        fc_prime_mpa=28.0,
        fy_mpa=350.0,
        phi=0.90,
        rho_override=0.0142,
        jurisdiction_mode=mode,
    )
    assert step_main_textbook.final_result is not None
    assert round(step_main_textbook.final_result) == 2659

    cand_4_30 = evaluate_rebar_combination(
        (RebarGroup(bar_diameter_mm=30.0, bar_count=4),),
        target_area_mm2=2659.0,
    )
    assert round(cand_4_30.total_area_mm2) == 2827
    assert cand_4_30.constructability_verified is False

    # Alternative case: b = 300 mm, h = 550 mm -> d = 550 - 65 = 485 mm
    step_d_alt = evaluate_mostofinejad_eq_5_48a_d_estimate(550.0, jurisdiction_mode=mode)
    assert step_d_alt.final_result == pytest.approx(485.0)

    _, step_alt_textbook = solve_mostofinejad_flexural_steel_from_kn(
        b_mm=300.0,
        d_mm=485.0,
        mu_nmm=395.8e6,
        fc_prime_mpa=28.0,
        fy_mpa=350.0,
        phi=0.90,
        rho_override=0.0210,
        jurisdiction_mode=mode,
    )
    assert step_alt_textbook.final_result is not None
    assert round(step_alt_textbook.final_result) == 3056

    cand_4_32 = evaluate_rebar_combination(
        (RebarGroup(bar_diameter_mm=32.0, bar_count=4),),
        target_area_mm2=3056.0,
    )
    assert round(cand_4_32.total_area_mm2) == 3217
    assert cand_4_32.constructability_verified is False

    cand_3_36 = evaluate_rebar_combination(
        (RebarGroup(bar_diameter_mm=36.0, bar_count=3),),
        target_area_mm2=3056.0,
    )
    assert round(cand_3_36.total_area_mm2) == 3054
    assert cand_3_36.constructability_verified is False

    # Confirm spacing constructability check is explicitly UNVERIFIED_RULE_BLOCKED
    spacing_step = evaluate_longitudinal_bar_clear_spacing(
        BeamGeometry(
            bw_mm=300.0,
            h_mm=550.0,
            d_effective_mm=485.0,
            tension_rebar_groups=cand_4_32.groups,
        )
    )
    assert spacing_step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED


def test_permitted_csa_reference_equations_consistency_and_jurisdiction_block() -> None:
    mode = JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY
    fc = 35.0
    fy = 400.0
    b = 400.0
    d = 435.0
    as_mm2 = 1800.0
    rho = as_mm2 / (b * d)
    phi_c = 0.65
    phi_s = 0.85

    step_a1 = evaluate_mostofinejad_eq_5_49_alpha1(fc, jurisdiction_mode=mode)
    step_b1 = evaluate_mostofinejad_eq_5_50_beta1(fc, jurisdiction_mode=mode)
    assert step_a1.outcome == EvaluationOutcome.COMPUTED
    assert step_b1.outcome == EvaluationOutcome.COMPUTED
    assert step_a1.final_result == pytest.approx(0.85 - 0.0015 * 35.0)
    assert step_b1.final_result == pytest.approx(0.97 - 0.0025 * 35.0)

    # Lower-bound clamp at 0.67 for high f'c
    assert evaluate_mostofinejad_eq_5_49_alpha1(150.0, jurisdiction_mode=mode).final_result == pytest.approx(0.67)
    assert evaluate_mostofinejad_eq_5_50_beta1(150.0, jurisdiction_mode=mode).final_result == pytest.approx(0.67)

    alpha_1 = step_a1.final_result
    assert alpha_1 is not None

    step_54 = evaluate_mostofinejad_eq_5_54_a(
        as_mm2=as_mm2,
        fy_mpa=fy,
        fc_prime_mpa=fc,
        b_mm=b,
        alpha_1=alpha_1,
        phi_s=phi_s,
        phi_c=phi_c,
        jurisdiction_mode=mode,
    )
    assert step_54.outcome == EvaluationOutcome.COMPUTED
    assert step_54.final_result is not None

    step_55 = evaluate_mostofinejad_eq_5_55_mr(
        as_mm2=as_mm2,
        fy_mpa=fy,
        d_mm=d,
        a_mm=step_54.final_result,
        phi_s=phi_s,
        jurisdiction_mode=mode,
    )
    step_56 = evaluate_mostofinejad_eq_5_56_mr_rho(
        rho=rho,
        fy_mpa=fy,
        fc_prime_mpa=fc,
        b_mm=b,
        d_mm=d,
        alpha_1=alpha_1,
        phi_s=phi_s,
        phi_c=phi_c,
        jurisdiction_mode=mode,
    )
    assert step_55.outcome == EvaluationOutcome.COMPUTED
    assert step_56.outcome == EvaluationOutcome.COMPUTED
    # Eq. (5-55) and Eq. (5-56) must yield identical Mr
    assert step_55.final_result == pytest.approx(step_56.final_result, rel=1e-12)

    assert step_55.final_result is not None
    step_61_pass = evaluate_mostofinejad_eq_5_61_check(
        mf_nmm=240.0e6, mr_nmm=step_55.final_result, jurisdiction_mode=mode
    )
    assert step_61_pass.outcome == EvaluationOutcome.PASS

    step_61_fail = evaluate_mostofinejad_eq_5_61_check(
        mf_nmm=300.0e6, mr_nmm=step_55.final_result, jurisdiction_mode=mode
    )
    assert step_61_fail.outcome == EvaluationOutcome.FAIL

    # Calling any reference equation in MABHAS_9_COMPLIANCE returns JURISDICTION_BLOCKED
    mabhas_mode = JurisdictionMode.MABHAS_9_COMPLIANCE
    assert (
        evaluate_mostofinejad_eq_5_46_kn(35.0, omega=0.1, jurisdiction_mode=mabhas_mode).outcome
        == EvaluationOutcome.JURISDICTION_BLOCKED
    )
    assert (
        evaluate_mostofinejad_eq_5_47_bd2(
            kn_mpa=3.5, mu_nmm=240e6, phi=0.9, jurisdiction_mode=mabhas_mode
        ).outcome
        == EvaluationOutcome.JURISDICTION_BLOCKED
    )
    assert (
        evaluate_mostofinejad_eq_5_48a_d_estimate(500.0, jurisdiction_mode=mabhas_mode).outcome
        == EvaluationOutcome.JURISDICTION_BLOCKED
    )
    assert (
        evaluate_mostofinejad_eq_5_48b_d_estimate(500.0, jurisdiction_mode=mabhas_mode).outcome
        == EvaluationOutcome.JURISDICTION_BLOCKED
    )
    assert (
        evaluate_mostofinejad_eq_5_49_alpha1(35.0, jurisdiction_mode=mabhas_mode).outcome
        == EvaluationOutcome.JURISDICTION_BLOCKED
    )
    assert (
        evaluate_mostofinejad_eq_5_50_beta1(35.0, jurisdiction_mode=mabhas_mode).outcome
        == EvaluationOutcome.JURISDICTION_BLOCKED
    )
    assert (
        evaluate_mostofinejad_eq_5_54_a(
            as_mm2=as_mm2,
            fy_mpa=fy,
            fc_prime_mpa=fc,
            b_mm=b,
            alpha_1=alpha_1,
            phi_s=phi_s,
            phi_c=phi_c,
            jurisdiction_mode=mabhas_mode,
        ).outcome
        == EvaluationOutcome.JURISDICTION_BLOCKED
    )
    assert (
        evaluate_mostofinejad_eq_5_55_mr(
            as_mm2=as_mm2,
            fy_mpa=fy,
            d_mm=d,
            a_mm=50.0,
            phi_s=phi_s,
            jurisdiction_mode=mabhas_mode,
        ).outcome
        == EvaluationOutcome.JURISDICTION_BLOCKED
    )
    assert (
        evaluate_mostofinejad_eq_5_56_mr_rho(
            rho=rho,
            fy_mpa=fy,
            fc_prime_mpa=fc,
            b_mm=b,
            d_mm=d,
            alpha_1=alpha_1,
            phi_s=phi_s,
            phi_c=phi_c,
            jurisdiction_mode=mabhas_mode,
        ).outcome
        == EvaluationOutcome.JURISDICTION_BLOCKED
    )
    assert (
        evaluate_mostofinejad_eq_5_61_check(
            mf_nmm=200e6, mr_nmm=240e6, jurisdiction_mode=mabhas_mode
        ).outcome
        == EvaluationOutcome.JURISDICTION_BLOCKED
    )


def test_aud_02_solve_mostofinejad_flexural_steel_from_kn_defensive_input_validation() -> None:
    mode = JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY
    base_kwargs = {
        "b_mm": 350.0,
        "d_mm": 535.0,
        "mu_nmm": 401.6e6,
        "fc_prime_mpa": 28.0,
        "fy_mpa": 350.0,
        "phi": 0.90,
        "jurisdiction_mode": mode,
    }

    invalid_cases = [
        {"b_mm": 0.0},
        {"d_mm": -10.0},
        {"mu_nmm": 0.0},
        {"fc_prime_mpa": 0.0},
        {"fy_mpa": 0.0},
        {"phi": 0.0},
        {"phi": 1.1},
        {"kn_override_mpa": 0.0},
        {"rho_override": -0.01},
        {"b_mm": float("nan")},
        {"d_mm": float("inf")},
    ]

    for override in invalid_cases:
        call_kwargs = {**base_kwargs, **override}
        step_47, step_46 = solve_mostofinejad_flexural_steel_from_kn(
            b_mm=float(call_kwargs["b_mm"]),  # type: ignore[arg-type]
            d_mm=float(call_kwargs["d_mm"]),  # type: ignore[arg-type]
            mu_nmm=float(call_kwargs["mu_nmm"]),  # type: ignore[arg-type]
            fc_prime_mpa=float(call_kwargs["fc_prime_mpa"]),  # type: ignore[arg-type]
            fy_mpa=float(call_kwargs["fy_mpa"]),  # type: ignore[arg-type]
            phi=float(call_kwargs["phi"]),  # type: ignore[arg-type]
            kn_override_mpa=call_kwargs.get("kn_override_mpa"),  # type: ignore[arg-type]
            rho_override=call_kwargs.get("rho_override"),  # type: ignore[arg-type]
            jurisdiction_mode=mode,
        )
        assert step_47.outcome == EvaluationOutcome.INVALID_INPUT
        assert step_46.outcome == EvaluationOutcome.INVALID_INPUT
        assert step_47.final_result is None
        assert step_46.final_result is None
        assert len(step_47.diagnostics) >= 1
        assert len(step_46.diagnostics) >= 1

