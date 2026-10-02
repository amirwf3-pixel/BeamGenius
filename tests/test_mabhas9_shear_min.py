"""Tests for Mabhas 9 Minimum Shear Reinforcement (BG-SHEAR-MIN-001)."""

from __future__ import annotations

import math

import pytest

from beamgenius.domain import (
    BeamGeometry,
    ConcreteMaterial,
    EvaluationOutcome,
    RebarMaterial,
    StirrupLayout,
)
from beamgenius.engine import evaluate_minimum_shear_reinforcement


def test_shear_min_exact_mathematical_transition() -> None:
    # Exact transition: 0.062 * sqrt(fc') = 0.35 => fc' = (0.35 / 0.062)^2
    fc_transition = (0.35 / 0.062) ** 2
    geom = BeamGeometry(bw_mm=350.0, h_mm=500.0, d_effective_mm=435.0)
    rebar = RebarMaterial(fy_mpa=400.0, fyt_mpa=400.0)

    # 1. Below transition: fc' = 25.0 MPa -> 0.35 * bw / fyt governs
    step_low = evaluate_minimum_shear_reinforcement(
        geom, ConcreteMaterial(fc_prime_mpa=25.0), rebar
    )
    assert step_low.outcome == EvaluationOutcome.COMPUTED
    assert (
        step_low.intermediate_values["av_over_s_term_2_mm2_per_mm"]
        > step_low.intermediate_values["av_over_s_term_1_mm2_per_mm"]
    )
    expected_low = 0.35 * 350.0 / 400.0
    assert step_low.final_result == pytest.approx(expected_low, rel=1e-12)

    # 2. At exact transition: fc' = (0.35 / 0.062)^2
    step_eq = evaluate_minimum_shear_reinforcement(
        geom, ConcreteMaterial(fc_prime_mpa=fc_transition), rebar
    )
    assert step_eq.outcome == EvaluationOutcome.COMPUTED
    assert step_eq.intermediate_values["av_over_s_term_1_mm2_per_mm"] == pytest.approx(
        step_eq.intermediate_values["av_over_s_term_2_mm2_per_mm"], rel=1e-12
    )
    assert step_eq.final_result == pytest.approx(expected_low, rel=1e-12)

    # 3. Above transition: fc' = 36.0 MPa -> 0.062 * 6.0 = 0.372 > 0.35
    step_high = evaluate_minimum_shear_reinforcement(
        geom, ConcreteMaterial(fc_prime_mpa=36.0), rebar
    )
    assert step_high.outcome == EvaluationOutcome.COMPUTED
    assert (
        step_high.intermediate_values["av_over_s_term_1_mm2_per_mm"]
        > step_high.intermediate_values["av_over_s_term_2_mm2_per_mm"]
    )
    expected_high = 0.062 * 6.0 * 350.0 / 400.0
    assert step_high.final_result == pytest.approx(expected_high, rel=1e-12)


def test_shear_min_pass_and_fail_with_stirrup_layout() -> None:
    geom = BeamGeometry(bw_mm=350.0, h_mm=500.0, d_effective_mm=435.0)
    concrete = ConcreteMaterial(fc_prime_mpa=25.0)
    rebar = RebarMaterial(fy_mpa=400.0, fyt_mpa=400.0)
    # (Av/s)min = 0.35 * 350 / 400 = 0.30625 mm^2/mm
    # 2 legs Φ10: Av = 2 * pi * 100 / 4 = 157.0796 mm^2
    # At s = 250 mm: Av/s = 0.6283 mm^2/mm >= 0.30625 -> PASS
    stirrups_pass = StirrupLayout(
        bar_diameter_mm=10.0, num_legs=2, longitudinal_spacing_s_mm=250.0
    )
    step_pass = evaluate_minimum_shear_reinforcement(
        geom, concrete, rebar, stirrups=stirrups_pass
    )
    assert step_pass.outcome == EvaluationOutcome.PASS
    assert step_pass.final_result == pytest.approx(0.30625)

    # At s = 600 mm: Av/s = 157.0796 / 600 = 0.2618 mm^2/mm < 0.30625 -> FAIL
    stirrups_fail = StirrupLayout(
        bar_diameter_mm=10.0, num_legs=2, longitudinal_spacing_s_mm=600.0
    )
    step_fail = evaluate_minimum_shear_reinforcement(
        geom, concrete, rebar, stirrups=stirrups_fail
    )
    assert step_fail.outcome == EvaluationOutcome.FAIL
    assert any(
        d.code == "INSUFFICIENT_MINIMUM_SHEAR_REINFORCEMENT"
        for d in step_fail.diagnostics
    )


def test_shear_min_table_9_11_2_exception_1_shallow_beam() -> None:
    concrete = ConcreteMaterial(fc_prime_mpa=25.0)
    rebar = RebarMaterial(fy_mpa=400.0)

    # h = 250.0 mm -> EXEMPT
    geom_250 = BeamGeometry(bw_mm=300.0, h_mm=250.0, d_effective_mm=200.0)
    step_exempt = evaluate_minimum_shear_reinforcement(geom_250, concrete, rebar)
    assert step_exempt.outcome == EvaluationOutcome.EXEMPT
    assert step_exempt.final_result == pytest.approx(0.35 * 300.0 / 400.0)
    assert any(
        d.code == "TABLE_9_11_2_EXCEPTION_1_SHALLOW_BEAM"
        for d in step_exempt.diagnostics
    )

    # h = 250.1 mm -> NOT EXEMPT
    geom_250_1 = BeamGeometry(bw_mm=300.0, h_mm=250.1, d_effective_mm=200.0)
    step_not_exempt = evaluate_minimum_shear_reinforcement(
        geom_250_1, concrete, rebar, av_over_s_provided_mm2_per_mm=0.10
    )
    assert step_not_exempt.outcome == EvaluationOutcome.FAIL


def test_shear_min_table_9_11_2_exception_2_integral_with_slab() -> None:
    concrete = ConcreteMaterial(fc_prime_mpa=28.0)
    rebar = RebarMaterial(fy_mpa=400.0)

    # Case A: 2.5 * tf = 2.5 * 160 = 400 mm, 0.5 * bw = 0.5 * 600 = 300 mm -> max = 400 mm
    # h = 400.0 mm <= 400 mm and <= 600 mm -> EXEMPT
    geom_ex2 = BeamGeometry(
        bw_mm=600.0,
        h_mm=400.0,
        d_effective_mm=340.0,
        tf_mm=160.0,
        is_integral_with_slab=True,
    )
    step_ex2 = evaluate_minimum_shear_reinforcement(geom_ex2, concrete, rebar)
    assert step_ex2.outcome == EvaluationOutcome.EXEMPT
    assert any(
        d.code == "TABLE_9_11_2_EXCEPTION_2_INTEGRAL_SLAB"
        for d in step_ex2.diagnostics
    )

    # Case B: 0.5 * bw = 0.5 * 1300 = 650 mm, h = 600.0 mm <= 650 mm and <= 600 mm -> EXEMPT
    geom_ex2_600 = BeamGeometry(
        bw_mm=1300.0,
        h_mm=600.0,
        d_effective_mm=535.0,
        tf_mm=150.0,
        is_integral_with_slab=True,
    )
    step_ex2_600 = evaluate_minimum_shear_reinforcement(geom_ex2_600, concrete, rebar)
    assert step_ex2_600.outcome == EvaluationOutcome.EXEMPT

    # Case C: h = 600.1 mm > 600 mm -> NOT EXEMPT even though 0.5 * bw = 650 mm
    geom_ex2_over_600 = BeamGeometry(
        bw_mm=1300.0,
        h_mm=600.1,
        d_effective_mm=535.0,
        tf_mm=150.0,
        is_integral_with_slab=True,
    )
    step_over_600 = evaluate_minimum_shear_reinforcement(
        geom_ex2_over_600,
        concrete,
        rebar,
        av_over_s_provided_mm2_per_mm=0.10,
    )
    assert step_over_600.outcome == EvaluationOutcome.FAIL


def test_shear_min_table_9_11_2_exception_3_steel_fiber_rc() -> None:
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=440.0)
    sfrc = ConcreteMaterial(fc_prime_mpa=36.0, is_steel_fiber_normal_rc=True)
    rebar = RebarMaterial(fy_mpa=400.0)

    # 1. Without explicit phi -> UNVERIFIED_RULE_BLOCKED
    step_no_phi = evaluate_minimum_shear_reinforcement(
        geom, sfrc, rebar, vu_n=50_000.0, phi_shear_explicit=None
    )
    assert step_no_phi.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert any(
        d.code == "SFRC_SHEAR_EXCEPTION_MISSING_EXPLICIT_PHI"
        for d in step_no_phi.diagnostics
    )

    # 2. With explicit phi = 0.75: limit = 0.75 * 0.17 * sqrt(36) * 300 * 440 = 100,980.0 N
    vu_limit = 0.75 * 0.17 * math.sqrt(36.0) * 300.0 * 440.0
    step_sfrc_exempt = evaluate_minimum_shear_reinforcement(
        geom, sfrc, rebar, vu_n=vu_limit, phi_shear_explicit=0.75
    )
    assert step_sfrc_exempt.outcome == EvaluationOutcome.EXEMPT
    assert any(
        d.code == "TABLE_9_11_2_EXCEPTION_3_STEEL_FIBER_RC"
        for d in step_sfrc_exempt.diagnostics
    )

    # 3. Vu exceeds limit -> NOT EXEMPT
    step_sfrc_exceed = evaluate_minimum_shear_reinforcement(
        geom,
        sfrc,
        rebar,
        vu_n=vu_limit + 1.0,
        phi_shear_explicit=0.75,
        av_over_s_provided_mm2_per_mm=0.10,
    )
    assert step_sfrc_exceed.outcome == EvaluationOutcome.FAIL

    # 4. f'c > 40 MPa -> NOT EXEMPT
    sfrc_high_fc = ConcreteMaterial(fc_prime_mpa=40.1, is_steel_fiber_normal_rc=True)
    step_sfrc_fc = evaluate_minimum_shear_reinforcement(
        geom,
        sfrc_high_fc,
        rebar,
        vu_n=10_000.0,
        phi_shear_explicit=0.75,
        av_over_s_provided_mm2_per_mm=0.10,
    )
    assert step_sfrc_fc.outcome == EvaluationOutcome.FAIL


def test_shear_min_table_9_11_2_exception_4_one_way_joist_blocked() -> None:
    geom_joist = BeamGeometry(
        bw_mm=150.0, h_mm=350.0, d_effective_mm=300.0, is_one_way_joist=True
    )
    step = evaluate_minimum_shear_reinforcement(
        geom_joist, ConcreteMaterial(fc_prime_mpa=28.0), RebarMaterial(fy_mpa=400.0)
    )
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert any(
        d.code == "ONE_WAY_JOIST_EXCEPTION_UNVERIFIED" for d in step.diagnostics
    )


def test_aud_05_exception_precedence_and_conditional_sfrc_demands() -> None:
    rebar = RebarMaterial(fy_mpa=400.0)

    # 1. Shallow beam (h = 250.0 mm) with is_one_way_joist=True -> EXEMPT under Exception 1
    geom_shallow_joist = BeamGeometry(
        bw_mm=150.0, h_mm=250.0, d_effective_mm=200.0, is_one_way_joist=True
    )
    step_shallow_joist = evaluate_minimum_shear_reinforcement(
        geom_shallow_joist, ConcreteMaterial(fc_prime_mpa=28.0), rebar
    )
    assert step_shallow_joist.outcome == EvaluationOutcome.EXEMPT
    assert any(
        d.code == "TABLE_9_11_2_EXCEPTION_1_SHALLOW_BEAM"
        for d in step_shallow_joist.diagnostics
    )

    # 2. Shallow beam (h = 250.0 mm) with SFRC and phi_shear_explicit=0.75 (without vu_n or d) -> EXEMPT
    geom_shallow_no_d = BeamGeometry(bw_mm=300.0, h_mm=250.0)
    sfrc_35 = ConcreteMaterial(fc_prime_mpa=35.0, is_steel_fiber_normal_rc=True)
    step_shallow_sfrc = evaluate_minimum_shear_reinforcement(
        geom_shallow_no_d,
        sfrc_35,
        rebar,
        vu_n=None,
        phi_shear_explicit=0.75,
    )
    assert step_shallow_sfrc.outcome == EvaluationOutcome.EXEMPT
    assert any(
        d.code == "TABLE_9_11_2_EXCEPTION_1_SHALLOW_BEAM"
        for d in step_shallow_sfrc.diagnostics
    )

    # 3. SFRC beam with phi_shear_explicit=None still returns UNVERIFIED_RULE_BLOCKED even when h = 250.0 mm
    step_shallow_sfrc_no_phi = evaluate_minimum_shear_reinforcement(
        geom_shallow_no_d,
        sfrc_35,
        rebar,
        vu_n=None,
        phi_shear_explicit=None,
    )
    assert step_shallow_sfrc_no_phi.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert any(
        d.code == "SFRC_SHEAR_EXCEPTION_MISSING_EXPLICIT_PHI"
        for d in step_shallow_sfrc_no_phi.diagnostics
    )

    # 4. SFRC beam with phi_shear_explicit=0.75 and fc_prime_mpa=45.0 (> 40 MPa) evaluates (Av/s)_min
    # without failing for missing vu_n or d_effective_mm
    geom_sfrc_45 = BeamGeometry(bw_mm=350.0, h_mm=500.0)
    sfrc_45 = ConcreteMaterial(fc_prime_mpa=45.0, is_steel_fiber_normal_rc=True)
    step_sfrc_45 = evaluate_minimum_shear_reinforcement(
        geom_sfrc_45,
        sfrc_45,
        rebar,
        vu_n=None,
        phi_shear_explicit=0.75,
    )
    assert step_sfrc_45.outcome == EvaluationOutcome.COMPUTED
    expected_av_s = max(0.062 * math.sqrt(45.0), 0.35) * 350.0 / 400.0
    assert step_sfrc_45.final_result == pytest.approx(expected_av_s, rel=1e-12)


def test_aud_06_shear_min_exact_boundaries() -> None:
    geom = BeamGeometry(bw_mm=350.0, h_mm=500.0, d_effective_mm=435.0)
    concrete = ConcreteMaterial(fc_prime_mpa=25.0)
    rebar = RebarMaterial(fy_mpa=400.0, fyt_mpa=400.0)

    # 1. Exact equality av_over_s_provided_mm2_per_mm == av_over_s_min -> PASS
    exact_av_over_s_min = 0.35 * 350.0 / 400.0
    step_exact_eq = evaluate_minimum_shear_reinforcement(
        geom,
        concrete,
        rebar,
        av_over_s_provided_mm2_per_mm=exact_av_over_s_min,
    )
    assert step_exact_eq.outcome == EvaluationOutcome.PASS
    assert step_exact_eq.final_result == pytest.approx(exact_av_over_s_min, rel=1e-12)

    # 2. Exception 2 when 0.5 * bw < 600 mm governs over 2.5 * tf:
    # bw = 800 mm -> 0.5 * bw = 400 mm; tf = 100 mm -> 2.5 * tf = 250 mm; limit = 400 mm
    geom_ex2_400 = BeamGeometry(
        bw_mm=800.0,
        h_mm=400.0,
        d_effective_mm=340.0,
        tf_mm=100.0,
        is_integral_with_slab=True,
    )
    step_ex2_400 = evaluate_minimum_shear_reinforcement(geom_ex2_400, concrete, rebar)
    assert step_ex2_400.outcome == EvaluationOutcome.EXEMPT
    assert step_ex2_400.intermediate_values["integral_slab_depth_limit_mm"] == pytest.approx(
        400.0
    )

    geom_ex2_400_1 = BeamGeometry(
        bw_mm=800.0,
        h_mm=400.1,
        d_effective_mm=340.0,
        tf_mm=100.0,
        is_integral_with_slab=True,
    )
    step_ex2_400_1 = evaluate_minimum_shear_reinforcement(
        geom_ex2_400_1,
        concrete,
        rebar,
        av_over_s_provided_mm2_per_mm=0.10,
    )
    assert step_ex2_400_1.outcome == EvaluationOutcome.FAIL

    # 3. Exception 3 exact boundaries at fc' = 40.0 vs 40.1 and h = 600.0 vs 600.1
    geom_600 = BeamGeometry(bw_mm=300.0, h_mm=600.0, d_effective_mm=535.0)
    sfrc_40 = ConcreteMaterial(fc_prime_mpa=40.0, is_steel_fiber_normal_rc=True)
    step_sfrc_40_600 = evaluate_minimum_shear_reinforcement(
        geom_600,
        sfrc_40,
        rebar,
        vu_n=50_000.0,
        phi_shear_explicit=0.75,
        av_over_s_provided_mm2_per_mm=0.10,
    )
    assert step_sfrc_40_600.outcome == EvaluationOutcome.EXEMPT

    sfrc_40_1 = ConcreteMaterial(fc_prime_mpa=40.1, is_steel_fiber_normal_rc=True)
    step_sfrc_40_1 = evaluate_minimum_shear_reinforcement(
        geom_600,
        sfrc_40_1,
        rebar,
        vu_n=50_000.0,
        phi_shear_explicit=0.75,
        av_over_s_provided_mm2_per_mm=0.10,
    )
    assert step_sfrc_40_1.outcome == EvaluationOutcome.FAIL

    geom_600_1 = BeamGeometry(bw_mm=300.0, h_mm=600.1, d_effective_mm=535.0)
    step_sfrc_600_1 = evaluate_minimum_shear_reinforcement(
        geom_600_1,
        sfrc_40,
        rebar,
        vu_n=50_000.0,
        phi_shear_explicit=0.75,
        av_over_s_provided_mm2_per_mm=0.10,
    )
    assert step_sfrc_600_1.outcome == EvaluationOutcome.FAIL

