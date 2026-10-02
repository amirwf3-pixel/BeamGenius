"""Tests for Mabhas 9 Minimum Flexural Reinforcement (BG-FLEX-MIN-001)."""

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
    VerificationStatus,
)
from beamgenius.engine import (
    evaluate_mabhas9_flexural_capacity,
    evaluate_minimum_flexural_reinforcement,
    run_mabhas9_flexural_workflow,
)
from beamgenius.reference import (
    evaluate_mostofinejad_eq_5_49_alpha1,
    evaluate_mostofinejad_eq_5_54_a,
    evaluate_mostofinejad_eq_5_55_mr,
    evaluate_mostofinejad_eq_5_61_check,
)
from beamgenius.registry import evaluate_rule_gate, require_rule


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


def test_phase_2b_flexural_capacity_input_and_effective_depth_validation() -> None:
    valid_geom = BeamGeometry(bw_mm=350.0, h_mm=600.0, d_effective_mm=535.0)
    valid_conc = ConcreteMaterial(fc_prime_mpa=28.0)
    valid_rebar = RebarMaterial(fy_mpa=400.0)

    # 1. Invalid fc' -> INVALID_INPUT
    step_bad_fc = evaluate_mabhas9_flexural_capacity(
        valid_geom,
        ConcreteMaterial(fc_prime_mpa=0.0),
        valid_rebar,
        as_provided_mm2=1800.0,
        mu_nmm=240e6,
    )
    assert step_bad_fc.outcome == EvaluationOutcome.INVALID_INPUT
    assert any(d.code == "INVALID_CONCRETE_STRENGTH" for d in step_bad_fc.diagnostics)

    # 2. Invalid fy -> INVALID_INPUT
    step_bad_fy = evaluate_mabhas9_flexural_capacity(
        valid_geom,
        valid_conc,
        RebarMaterial(fy_mpa=-400.0),
        as_provided_mm2=1800.0,
        mu_nmm=240e6,
    )
    assert step_bad_fy.outcome == EvaluationOutcome.INVALID_INPUT
    assert any(d.code == "INVALID_REBAR_FY" for d in step_bad_fy.diagnostics)

    # 3. Invalid geometry -> INVALID_INPUT
    step_bad_geom = evaluate_mabhas9_flexural_capacity(
        BeamGeometry(bw_mm=0.0, h_mm=600.0, d_effective_mm=535.0),
        valid_conc,
        valid_rebar,
        as_provided_mm2=1800.0,
        mu_nmm=240e6,
    )
    assert step_bad_geom.outcome == EvaluationOutcome.INVALID_INPUT
    assert any(d.code == "INVALID_BEAM_WIDTH" for d in step_bad_geom.diagnostics)

    # 4. Invalid As -> INVALID_INPUT
    step_bad_as = evaluate_mabhas9_flexural_capacity(
        valid_geom,
        valid_conc,
        valid_rebar,
        as_provided_mm2=0.0,
        mu_nmm=240e6,
    )
    assert step_bad_as.outcome == EvaluationOutcome.INVALID_INPUT
    assert any(d.code == "INVALID_AS_PROVIDED" for d in step_bad_as.diagnostics)

    # 5. Invalid Mu -> INVALID_INPUT
    step_bad_mu = evaluate_mabhas9_flexural_capacity(
        valid_geom,
        valid_conc,
        valid_rebar,
        as_provided_mm2=1800.0,
        mu_nmm=-1.0,
    )
    assert step_bad_mu.outcome == EvaluationOutcome.INVALID_INPUT
    assert any(d.code == "INVALID_FACTORED_MOMENT_MU" for d in step_bad_mu.diagnostics)

    # 6. Unresolved d -> INVALID_INPUT (never guesses h - 65 or h - 90)
    step_no_d = evaluate_mabhas9_flexural_capacity(
        BeamGeometry(bw_mm=350.0, h_mm=600.0),
        valid_conc,
        valid_rebar,
        as_provided_mm2=1800.0,
        mu_nmm=240e6,
    )
    assert step_no_d.outcome == EvaluationOutcome.INVALID_INPUT
    assert any(d.code == "MISSING_EFFECTIVE_DEPTH" for d in step_no_d.diagnostics)

    # 7. Explicit d precedence preserved in trace normalized_inputs
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
    assert step_explicit_d.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step_explicit_d.normalized_inputs["d_effective_mm"] == pytest.approx(538.0)
    assert step_explicit_d.normalized_inputs["d_resolution_source"] == "EXPLICIT_D"


def test_phase_2b_blocked_flanged_and_doubly_reinforced_configurations() -> None:
    conc = ConcreteMaterial(fc_prime_mpa=28.0)
    rebar = RebarMaterial(fy_mpa=400.0)

    # 1. T-beam and L-beam never fall back to rectangular behavior
    for sec_type in (SectionType.T_SECTION, SectionType.L_SECTION):
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
        assert step_flanged.final_result is None
        assert any(
            d.code == "FLANGED_SECTION_FLEXURAL_RESISTANCE_UNVERIFIED"
            for d in step_flanged.diagnostics
        )

    # 2. Doubly reinforced beam never silently ignores compression steel As'
    geom_rect = BeamGeometry(bw_mm=350.0, h_mm=600.0, d_effective_mm=535.0)
    step_doubly = evaluate_mabhas9_flexural_capacity(
        geom_rect,
        conc,
        rebar,
        as_provided_mm2=2600.0,
        as_compression_mm2=600.0,
        mu_nmm=400e6,
    )
    assert step_doubly.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step_doubly.final_result is None
    assert any(
        d.code == "DOUBLY_REINFORCED_FLEXURAL_RESISTANCE_UNVERIFIED"
        for d in step_doubly.diagnostics
    )

    # 3. Jurisdiction gate on evaluate_mabhas9_flexural_capacity
    step_jur = evaluate_mabhas9_flexural_capacity(
        geom_rect,
        conc,
        rebar,
        as_provided_mm2=2600.0,
        mu_nmm=400e6,
        jurisdiction_mode=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    )
    assert step_jur.outcome == EvaluationOutcome.JURISDICTION_BLOCKED


def test_phase_2b_flexural_workflow_interaction_and_rule_references() -> None:
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=440.0)
    conc = ConcreteMaterial(fc_prime_mpa=25.0)
    rebar = RebarMaterial(fy_mpa=400.0)

    # 1. When As_provided >= As_min (462 mm^2), BG-FLEX-MIN-001 passes, but overall workflow
    # is BLOCKED (never a false PASS) because Mabhas 9 flexural resistance is VERIFY_PENDING.
    report_blocked = run_mabhas9_flexural_workflow(
        geom, conc, rebar, as_provided_mm2=900.0, mu_nmm=150e6
    )
    assert report_blocked.overall_status == OverallComplianceStatus.BLOCKED
    assert report_blocked.is_compliant is False
    assert report_blocked.outcomes_by_rule["BG-FLEX-MIN-001"] == EvaluationOutcome.PASS
    assert (
        report_blocked.outcomes_by_rule["BG-MABHAS9-FLEX-CAP-BLOCKED"]
        == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    )

    # 2. When As_provided < As_min (462 mm^2), BG-FLEX-MIN-001 fails, and FAIL dominates BLOCKED
    report_fail = run_mabhas9_flexural_workflow(
        geom, conc, rebar, as_provided_mm2=300.0, mu_nmm=150e6
    )
    assert report_fail.overall_status == OverallComplianceStatus.FAIL
    assert report_fail.is_compliant is False
    assert report_fail.outcomes_by_rule["BG-FLEX-MIN-001"] == EvaluationOutcome.FAIL

    # 3. Verify granular flexural pending RuleReferences in central registry
    for pending_id in (
        "BG-FLEX-STRESS-BLOCK-PENDING",
        "BG-FLEX-PHI-FACTOR-PENDING",
        "BG-FLEX-STRAIN-LIMIT-PENDING",
        "BG-FLEX-DOUBLY-REINF-PENDING",
        "BG-FLEX-FLANGE-WIDTH-PENDING",
        "BG-MABHAS9-FLEX-CAP-BLOCKED",
    ):
        rule = require_rule(pending_id)
        assert rule.status == VerificationStatus.VERIFY_PENDING
        assert rule.execution_allowed is False
        gate = evaluate_rule_gate(pending_id)
        assert gate.allowed is False
        assert gate.blocked_outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED


def test_phase_2b_mostofinejad_reference_capacity_boundaries_isolated_from_mabhas9() -> None:
    # Mostofinejad Example 5-5 section (b=400, h=500, d=435, fc'=35, fy=400, 3Φ28 -> As=1847.26 mm^2)
    # In isolated reference mode (CSA A23.3-14):
    ref_mode = JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY
    b_mm = 400.0
    d_mm = 435.0
    fc_mpa = 35.0
    fy_mpa = 400.0
    as_mm2 = 3.0 * math.pi * (28.0**2) / 4.0

    alpha_1 = evaluate_mostofinejad_eq_5_49_alpha1(fc_mpa, jurisdiction_mode=ref_mode).final_result
    assert alpha_1 is not None
    a_mm = evaluate_mostofinejad_eq_5_54_a(
        as_mm2=as_mm2,
        fy_mpa=fy_mpa,
        fc_prime_mpa=fc_mpa,
        b_mm=b_mm,
        alpha_1=alpha_1,
        phi_s=0.85,
        phi_c=0.65,
        jurisdiction_mode=ref_mode,
    ).final_result
    assert a_mm is not None
    mr_nmm = evaluate_mostofinejad_eq_5_55_mr(
        as_mm2=as_mm2,
        fy_mpa=fy_mpa,
        d_mm=d_mm,
        a_mm=a_mm,
        phi_s=0.85,
        jurisdiction_mode=ref_mode,
    ).final_result
    assert mr_nmm is not None

    # Exact equality Mf == Mr -> PASS in reference mode
    assert (
        evaluate_mostofinejad_eq_5_61_check(
            mf_nmm=mr_nmm, mr_nmm=mr_nmm, jurisdiction_mode=ref_mode
        ).outcome
        == EvaluationOutcome.PASS
    )
    # Just below capacity (Mf < Mr) -> PASS in reference mode
    assert (
        evaluate_mostofinejad_eq_5_61_check(
            mf_nmm=mr_nmm - 1.0, mr_nmm=mr_nmm, jurisdiction_mode=ref_mode
        ).outcome
        == EvaluationOutcome.PASS
    )
    # Just above capacity (Mf > Mr) -> FAIL in reference mode
    assert (
        evaluate_mostofinejad_eq_5_61_check(
            mf_nmm=mr_nmm + 1.0, mr_nmm=mr_nmm, jurisdiction_mode=ref_mode
        ).outcome
        == EvaluationOutcome.FAIL
    )

    # In Mabhas 9 compliance mode, the exact same section does NOT use CSA equations and
    # returns UNVERIFIED_RULE_BLOCKED until Mabhas 9 flexural resistance is verified.
    mabhas_step = evaluate_mabhas9_flexural_capacity(
        BeamGeometry(bw_mm=b_mm, h_mm=500.0, d_effective_mm=d_mm),
        ConcreteMaterial(fc_prime_mpa=fc_mpa),
        RebarMaterial(fy_mpa=fy_mpa),
        as_provided_mm2=as_mm2,
        mu_nmm=240.0e6,
        jurisdiction_mode=JurisdictionMode.MABHAS_9_COMPLIANCE,
    )
    assert mabhas_step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert mabhas_step.final_result is None


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


