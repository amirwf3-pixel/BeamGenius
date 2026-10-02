"""Tests for deterministic blocked engineering workflows and Anti-Misleading-PASS aggregation."""

from __future__ import annotations

import pytest

from beamgenius.domain import (
    BeamComplianceReport,
    BeamGeometry,
    ConcreteMaterial,
    EvaluationOutcome,
    JurisdictionMode,
    OverallComplianceStatus,
    RebarMaterial,
    StirrupLayout,
)
from beamgenius.engine import (
    aggregate_compliance_report,
    evaluate_bar_cutoff,
    evaluate_bent_bar_anchorage,
    evaluate_compression_rebar_lateral_support,
    evaluate_concrete_cover,
    evaluate_concrete_shear_capacity_vc,
    evaluate_continuity_through_column,
    evaluate_development_length,
    evaluate_flexural_bar_extension,
    evaluate_full_shear_capacity,
    evaluate_layer_spacing,
    evaluate_longitudinal_bar_clear_spacing,
    evaluate_mabhas9_flexural_capacity,
    evaluate_maximum_shear_steel_vs_max,
    evaluate_minimum_flexural_reinforcement,
    evaluate_minimum_transverse_bar_diameter,
    evaluate_negative_rebar_extension,
    evaluate_non_continuous_support_anchorage,
    evaluate_positive_rebar_simple_support,
    evaluate_required_shear_steel_demand_vs,
    evaluate_skin_reinforcement,
    evaluate_structural_integrity_reinforcement,
    evaluate_table_9_11_2_remaining_exceptions,
    evaluate_torsion,
    run_mabhas9_beam_check,
)
from beamgenius.reference import evaluate_mostofinejad_blocked_equation


def test_all_blocked_mabhas9_workflows_return_unverified_rule_blocked() -> None:
    geom = BeamGeometry(
        bw_mm=350.0,
        h_mm=600.0,
        d_effective_mm=535.0,
        clear_cover_mm=40.0,
        stirrup_diameter_mm=10.0,
        layer_clear_spacing_mm=25.0,
    )
    concrete = ConcreteMaterial(fc_prime_mpa=28.0)
    rebar = RebarMaterial(fy_mpa=400.0)

    blocked_steps = [
        evaluate_mabhas9_flexural_capacity(
            geom,
            concrete,
            rebar,
            as_provided_mm2=1800.0,
            as_compression_mm2=500.0,
            mu_nmm=250e6,
        ),
        evaluate_full_shear_capacity(geom, concrete, rebar, vu_n=180_000.0),
        evaluate_concrete_shear_capacity_vc(geom, concrete),
        evaluate_required_shear_steel_demand_vs(geom, concrete, vu_n=180_000.0),
        evaluate_maximum_shear_steel_vs_max(geom, concrete, vs_n=120_000.0),
        evaluate_longitudinal_bar_clear_spacing(geom),
        evaluate_layer_spacing(geom),
        evaluate_concrete_cover(geom),
        evaluate_minimum_transverse_bar_diameter(geom),
        evaluate_compression_rebar_lateral_support(geom),
        evaluate_development_length(geom, concrete, rebar),
        evaluate_bar_cutoff(geom),
        evaluate_flexural_bar_extension(geom),
        evaluate_negative_rebar_extension(geom),
        evaluate_positive_rebar_simple_support(geom),
        evaluate_structural_integrity_reinforcement(geom),
        evaluate_continuity_through_column(geom),
        evaluate_non_continuous_support_anchorage(geom),
        evaluate_bent_bar_anchorage(geom),
        evaluate_skin_reinforcement(geom),
        evaluate_torsion(geom, concrete, rebar, tu_nmm=30e6),
        evaluate_table_9_11_2_remaining_exceptions(geom),
    ]

    for step in blocked_steps:
        assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
        assert step.outcome not in (EvaluationOutcome.PASS, EvaluationOutcome.FAIL)
        assert step.final_result is None
        assert len(step.diagnostics) >= 1
        assert step.diagnostics[0].required_verification is not None


@pytest.mark.parametrize(
    "blocked_eq_id",
    [
        "BG-MOST-5-44",
        "BG-MOST-5-45",
        "BG-MOST-5-51",
        "BG-MOST-5-52",
        "BG-MOST-5-53",
        "BG-MOST-5-57",
        "BG-MOST-5-58",
        "BG-MOST-5-59",
        "BG-MOST-5-60",
        "BG-MOST-5-62",
    ],
)
def test_blocked_mostofinejad_equations_via_reference_api(blocked_eq_id: str) -> None:
    for mode in JurisdictionMode:
        step = evaluate_mostofinejad_blocked_equation(
            blocked_eq_id, jurisdiction_mode=mode
        )
        assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
        assert step.final_result is None
        assert len(step.diagnostics) >= 1


def test_beam_checker_anti_misleading_pass_policy() -> None:
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=440.0)
    concrete = ConcreteMaterial(fc_prime_mpa=25.0)
    rebar = RebarMaterial(fy_mpa=400.0, fyt_mpa=400.0)
    stirrups = StirrupLayout(
        bar_diameter_mm=10.0,
        num_legs=2,
        longitudinal_spacing_s_mm=200.0,
        transverse_leg_spacing_st_mm=250.0,
    )

    # 1. All 3 verified Mabhas 9 rules pass -> OverallComplianceStatus.PASS
    report_pass = run_mabhas9_beam_check(
        geom,
        concrete,
        rebar,
        stirrups=stirrups,
        as_provided_mm2=800.0,
        vs_n=100_000.0,
    )
    assert report_pass.overall_status == OverallComplianceStatus.PASS
    assert report_pass.is_compliant is True
    assert len(report_pass.trace_steps) == 3

    # 2. Requesting the 3 verified rules (which all PASS) PLUS Mabhas 9 flexural capacity
    # MUST NOT return PASS -> returns BLOCKED while preserving all 4 trace steps!
    report_blocked = run_mabhas9_beam_check(
        geom,
        concrete,
        rebar,
        stirrups=stirrups,
        as_provided_mm2=800.0,
        vs_n=100_000.0,
        mu_nmm=200e6,
        requested_rule_ids=(
            "BG-FLEX-MIN-001",
            "BG-SHEAR-MIN-001",
            "BG-SHEAR-SPACING-001",
            "BG-MABHAS9-FLEX-CAP-BLOCKED",
        ),
    )
    assert report_blocked.overall_status == OverallComplianceStatus.BLOCKED
    assert report_blocked.is_compliant is False
    assert len(report_blocked.trace_steps) == 4
    assert report_blocked.outcomes_by_rule["BG-FLEX-MIN-001"] == EvaluationOutcome.PASS
    assert report_blocked.outcomes_by_rule["BG-SHEAR-MIN-001"] == EvaluationOutcome.PASS
    assert report_blocked.outcomes_by_rule["BG-SHEAR-SPACING-001"] == EvaluationOutcome.PASS
    assert (
        report_blocked.outcomes_by_rule["BG-MABHAS9-FLEX-CAP-BLOCKED"]
        == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    )

    # 3. Any FAIL dominates BLOCKED -> OverallComplianceStatus.FAIL
    report_fail = run_mabhas9_beam_check(
        geom,
        concrete,
        rebar,
        stirrups=stirrups,
        as_provided_mm2=200.0,  # < As,min (462 mm^2) -> FAIL
        vs_n=100_000.0,
        requested_rule_ids=(
            "BG-FLEX-MIN-001",
            "BG-SHEAR-MIN-001",
            "BG-MABHAS9-FLEX-CAP-BLOCKED",
        ),
    )
    assert report_fail.overall_status == OverallComplianceStatus.FAIL
    assert report_fail.is_compliant is False

    # 4. Any INVALID_INPUT dominates FAIL and BLOCKED -> OverallComplianceStatus.INVALID_INPUT
    report_invalid = run_mabhas9_beam_check(
        geom,
        concrete,
        RebarMaterial(fy_mpa=600.0, fyt_mpa=400.0),  # fy > 550 MPa -> INVALID_INPUT
        stirrups=stirrups,
        as_provided_mm2=200.0,
        vs_n=100_000.0,
        requested_rule_ids=(
            "BG-FLEX-MIN-001",
            "BG-SHEAR-MIN-001",
            "BG-MABHAS9-FLEX-CAP-BLOCKED",
        ),
    )
    assert report_invalid.overall_status == OverallComplianceStatus.INVALID_INPUT
    assert report_invalid.is_compliant is False

    # 5. Pure COMPUTED step without pass/fail check -> OverallComplianceStatus.PARTIAL
    computed_step = evaluate_minimum_flexural_reinforcement(geom, concrete, rebar)
    assert computed_step.outcome == EvaluationOutcome.COMPUTED
    report_partial = aggregate_compliance_report((computed_step,))
    assert report_partial.overall_status == OverallComplianceStatus.PARTIAL
    assert report_partial.is_compliant is False


def test_aud_04_duplicate_rule_id_dominance_in_outcomes_by_rule() -> None:
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=440.0)
    concrete = ConcreteMaterial(fc_prime_mpa=25.0)
    rebar_valid = RebarMaterial(fy_mpa=400.0)
    rebar_invalid = RebarMaterial(fy_mpa=600.0)

    step_pass = evaluate_minimum_flexural_reinforcement(
        geom, concrete, rebar_valid, as_provided_mm2=800.0
    )
    step_fail = evaluate_minimum_flexural_reinforcement(
        geom, concrete, rebar_valid, as_provided_mm2=200.0
    )
    step_invalid = evaluate_minimum_flexural_reinforcement(
        geom, concrete, rebar_invalid, as_provided_mm2=800.0
    )
    step_blocked = evaluate_minimum_flexural_reinforcement(
        geom,
        concrete,
        rebar_valid,
        as_provided_mm2=800.0,
        jurisdiction_mode=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    )
    # Also create an UNVERIFIED_RULE_BLOCKED step for BG-FLEX-MIN-001 (T-section flange in tension)
    geom_t_tension = BeamGeometry(
        bw_mm=300.0,
        h_mm=500.0,
        d_effective_mm=440.0,
        bf_mm=700.0,
        tf_mm=120.0,
        section_type=geom.section_type.__class__.T_SECTION,
        flange_condition=geom.flange_condition.__class__.FLANGE_IN_TENSION,
    )
    step_unverified_blocked = evaluate_minimum_flexural_reinforcement(
        geom_t_tension, concrete, rebar_valid, as_provided_mm2=800.0
    )

    assert step_pass.outcome == EvaluationOutcome.PASS
    assert step_fail.outcome == EvaluationOutcome.FAIL
    assert step_invalid.outcome == EvaluationOutcome.INVALID_INPUT
    assert step_blocked.outcome == EvaluationOutcome.JURISDICTION_BLOCKED
    assert step_unverified_blocked.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED

    rule_id = "BG-FLEX-MIN-001"

    # 1. PASS followed by FAIL -> FAIL
    rep_pf = aggregate_compliance_report((step_pass, step_fail))
    assert rep_pf.outcomes_by_rule[rule_id] == EvaluationOutcome.FAIL
    direct_pf = BeamComplianceReport(
        overall_status=OverallComplianceStatus.FAIL,
        jurisdiction_mode=JurisdictionMode.MABHAS_9_COMPLIANCE,
        trace_steps=(step_pass, step_fail),
        diagnostics=(),
    )
    assert direct_pf.outcomes_by_rule[rule_id] == EvaluationOutcome.FAIL

    # 2. FAIL followed by PASS -> FAIL
    rep_fp = aggregate_compliance_report((step_fail, step_pass))
    assert rep_fp.outcomes_by_rule[rule_id] == EvaluationOutcome.FAIL
    direct_fp = BeamComplianceReport(
        overall_status=OverallComplianceStatus.FAIL,
        jurisdiction_mode=JurisdictionMode.MABHAS_9_COMPLIANCE,
        trace_steps=(step_fail, step_pass),
        diagnostics=(),
    )
    assert direct_fp.outcomes_by_rule[rule_id] == EvaluationOutcome.FAIL

    # 3. UNVERIFIED_RULE_BLOCKED followed by PASS -> UNVERIFIED_RULE_BLOCKED
    rep_bp = aggregate_compliance_report((step_unverified_blocked, step_pass))
    assert rep_bp.outcomes_by_rule[rule_id] == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    direct_bp = BeamComplianceReport(
        overall_status=OverallComplianceStatus.BLOCKED,
        jurisdiction_mode=JurisdictionMode.MABHAS_9_COMPLIANCE,
        trace_steps=(step_unverified_blocked, step_pass),
        diagnostics=(),
    )
    assert direct_bp.outcomes_by_rule[rule_id] == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED

    # 4. INVALID_INPUT followed by FAIL -> INVALID_INPUT
    rep_if = aggregate_compliance_report((step_invalid, step_fail))
    assert rep_if.outcomes_by_rule[rule_id] == EvaluationOutcome.INVALID_INPUT
    direct_if = BeamComplianceReport(
        overall_status=OverallComplianceStatus.INVALID_INPUT,
        jurisdiction_mode=JurisdictionMode.MABHAS_9_COMPLIANCE,
        trace_steps=(step_invalid, step_fail),
        diagnostics=(),
    )
    assert direct_if.outcomes_by_rule[rule_id] == EvaluationOutcome.INVALID_INPUT

