"""Tests for Mabhas 9 Maximum Stirrup Spacing (BG-SHEAR-SPACING-001)."""

from __future__ import annotations

import math

import pytest

from beamgenius.domain import (
    BeamGeometry,
    ConcreteMaterial,
    EvaluationOutcome,
    StirrupLayout,
)
from beamgenius.engine import evaluate_maximum_stirrup_spacing


def test_shear_spacing_exact_equality_at_threshold_uses_condition_1() -> None:
    # bw = 300 mm, d = 500 mm, f'c = 25 MPa -> sqrt(f'c) = 5.0
    # threshold = 0.33 * 5.0 * 300.0 * 500.0 = 247,500.0 N
    geom = BeamGeometry(bw_mm=300.0, h_mm=560.0, d_effective_mm=500.0)
    concrete = ConcreteMaterial(fc_prime_mpa=25.0)
    exact_threshold_n = 0.33 * math.sqrt(25.0) * 300.0 * 500.0
    assert exact_threshold_n == pytest.approx(247_500.0, rel=1e-12)

    # 1. Exact equality Vs == threshold MUST use Condition 1:
    # s_max = min(500 / 2, 600) = 250 mm
    # st_max = min(500, 600) = 500 mm (from VERIFIED_RULES.md, NOT 300 mm from DESIGN_RULES.md)
    step_eq = evaluate_maximum_stirrup_spacing(
        geom, concrete, vs_n=exact_threshold_n
    )
    assert step_eq.outcome == EvaluationOutcome.COMPUTED
    assert step_eq.intermediate_values["condition_branch"] == 1.0
    assert step_eq.intermediate_values["s_max_mm"] == pytest.approx(250.0, rel=1e-12)
    assert step_eq.intermediate_values["st_max_mm"] == pytest.approx(500.0, rel=1e-12)
    assert step_eq.final_result == pytest.approx(250.0, rel=1e-12)

    # 2. Strictly above threshold -> Condition 2:
    # s_max = min(500 / 4, 300) = 125 mm
    # st_max = min(500 / 2, 300) = 250 mm
    step_above = evaluate_maximum_stirrup_spacing(
        geom, concrete, vs_n=exact_threshold_n + 1e-6
    )
    assert step_above.outcome == EvaluationOutcome.COMPUTED
    assert step_above.intermediate_values["condition_branch"] == 2.0
    assert step_above.intermediate_values["s_max_mm"] == pytest.approx(125.0, rel=1e-12)
    assert step_above.intermediate_values["st_max_mm"] == pytest.approx(250.0, rel=1e-12)


def test_shear_spacing_cap_governed_for_deep_beam_and_verified_rules_precedence() -> None:
    # Deep beam: d = 1400 mm, h = 1500 mm, bw = 400 mm, f'c = 25 MPa
    geom_deep = BeamGeometry(bw_mm=400.0, h_mm=1500.0, d_effective_mm=1400.0)
    concrete = ConcreteMaterial(fc_prime_mpa=25.0)

    # Condition 1 (Vs = 0 N):
    # d/2 = 700 mm -> capped at 600 mm
    # d = 1400 mm -> capped at 600 mm (proving VERIFIED_RULES.md st <= min(d, 600 mm) is used)
    step_c1 = evaluate_maximum_stirrup_spacing(geom_deep, concrete, vs_n=0.0)
    assert step_c1.intermediate_values["condition_branch"] == 1.0
    assert step_c1.intermediate_values["s_max_mm"] == pytest.approx(600.0)
    assert step_c1.intermediate_values["st_max_mm"] == pytest.approx(600.0)

    # Condition 2 (Vs = 2,000,000 N > threshold):
    # d/4 = 350 mm -> capped at 300 mm
    # d/2 = 700 mm -> capped at 300 mm
    step_c2 = evaluate_maximum_stirrup_spacing(geom_deep, concrete, vs_n=2_000_000.0)
    assert step_c2.intermediate_values["condition_branch"] == 2.0
    assert step_c2.intermediate_values["s_max_mm"] == pytest.approx(300.0)
    assert step_c2.intermediate_values["st_max_mm"] == pytest.approx(300.0)


def test_shear_spacing_pass_and_fail_for_s_and_st() -> None:
    geom = BeamGeometry(bw_mm=300.0, h_mm=560.0, d_effective_mm=500.0)
    concrete = ConcreteMaterial(fc_prime_mpa=25.0)
    # Condition 1: s_max = 250 mm, st_max = 500 mm
    stirrups_ok = StirrupLayout(
        bar_diameter_mm=10.0,
        num_legs=2,
        longitudinal_spacing_s_mm=250.0,
        transverse_leg_spacing_st_mm=450.0,
    )
    step_ok = evaluate_maximum_stirrup_spacing(
        geom, concrete, vs_n=100_000.0, stirrups=stirrups_ok
    )
    assert step_ok.outcome == EvaluationOutcome.PASS

    # Fail longitudinal spacing s (260 > 250)
    stirrups_fail_s = StirrupLayout(
        bar_diameter_mm=10.0,
        num_legs=2,
        longitudinal_spacing_s_mm=260.0,
        transverse_leg_spacing_st_mm=450.0,
    )
    step_fail_s = evaluate_maximum_stirrup_spacing(
        geom, concrete, vs_n=100_000.0, stirrups=stirrups_fail_s
    )
    assert step_fail_s.outcome == EvaluationOutcome.FAIL
    assert any(
        d.code == "LONGITUDINAL_STIRRUP_SPACING_EXCEEDED"
        for d in step_fail_s.diagnostics
    )

    # Fail transverse leg spacing st (510 > 500)
    stirrups_fail_st = StirrupLayout(
        bar_diameter_mm=10.0,
        num_legs=2,
        longitudinal_spacing_s_mm=200.0,
        transverse_leg_spacing_st_mm=510.0,
    )
    step_fail_st = evaluate_maximum_stirrup_spacing(
        geom, concrete, vs_n=100_000.0, stirrups=stirrups_fail_st
    )
    assert step_fail_st.outcome == EvaluationOutcome.FAIL
    assert any(
        d.code == "TRANSVERSE_STIRRUP_SPACING_EXCEEDED"
        for d in step_fail_st.diagnostics
    )


def test_shear_spacing_vu_without_vs_is_unverified_rule_blocked() -> None:
    geom = BeamGeometry(bw_mm=300.0, h_mm=560.0, d_effective_mm=500.0)
    concrete = ConcreteMaterial(fc_prime_mpa=25.0)
    step = evaluate_maximum_stirrup_spacing(
        geom, concrete, vs_n=None, vu_n=180_000.0
    )
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.final_result is None
    assert any(
        d.code == "VS_DERIVATION_FROM_VU_UNVERIFIED_BLOCKED"
        for d in step.diagnostics
    )


def test_shear_spacing_invalid_inputs() -> None:
    geom = BeamGeometry(bw_mm=300.0, h_mm=560.0, d_effective_mm=500.0)
    concrete = ConcreteMaterial(fc_prime_mpa=25.0)

    # Negative Vs
    step_neg_vs = evaluate_maximum_stirrup_spacing(geom, concrete, vs_n=-10.0)
    assert step_neg_vs.outcome == EvaluationOutcome.INVALID_INPUT

    # Neither Vs nor Vu supplied
    step_none = evaluate_maximum_stirrup_spacing(geom, concrete, vs_n=None, vu_n=None)
    assert step_none.outcome == EvaluationOutcome.INVALID_INPUT


def test_aud_06_shear_spacing_exact_equality_on_transverse_spacing_st() -> None:
    # d = 400.0 mm, bw = 300.0 mm, f'c = 25.0 MPa -> threshold = 0.33 * 5 * 300 * 400 = 198,000 N
    geom = BeamGeometry(bw_mm=300.0, h_mm=460.0, d_effective_mm=400.0)
    concrete = ConcreteMaterial(fc_prime_mpa=25.0)

    # Condition 1 (Vs = 100,000 N <= 198,000 N): s_max = 200.0 mm, st_max = min(400.0, 600.0) = 400.0 mm
    step_c1_exact_st = evaluate_maximum_stirrup_spacing(
        geom,
        concrete,
        vs_n=100_000.0,
        s_provided_mm=200.0,
        st_provided_mm=400.0,
    )
    assert step_c1_exact_st.outcome == EvaluationOutcome.PASS
    assert step_c1_exact_st.intermediate_values["condition_branch"] == 1.0
    assert step_c1_exact_st.intermediate_values["st_max_mm"] == pytest.approx(400.0)

    # Condition 2 (Vs = 250,000 N > 198,000 N): s_max = 100.0 mm, st_max = min(400.0 / 2, 300.0) = 200.0 mm
    step_c2_exact_st = evaluate_maximum_stirrup_spacing(
        geom,
        concrete,
        vs_n=250_000.0,
        s_provided_mm=100.0,
        st_provided_mm=200.0,
    )
    assert step_c2_exact_st.outcome == EvaluationOutcome.PASS
    assert step_c2_exact_st.intermediate_values["condition_branch"] == 2.0
    assert step_c2_exact_st.intermediate_values["st_max_mm"] == pytest.approx(200.0)

