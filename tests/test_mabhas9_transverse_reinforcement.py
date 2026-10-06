"""Focused tests for the Phase 2F Stage G Clause 9-21-6 transverse-reinforcement
evaluators (Mabhas 9, 1399 5th ed.).

Every expected numeric value was hand-verified against the visually
re-verified source equations/limits (footer-confirmed Printed pp. 443-450 /
PDF pp. 463-470; evidence scan phase2f-source-442-472 @ df8067a, re-read
2026-10-06) before being recorded here.
"""

from __future__ import annotations

import pytest

from beamgenius.domain.enums import EvaluationOutcome, JurisdictionMode
from beamgenius.engine.transverse_reinforcement_mabhas9 import (
    DorgirConstruction,
    SpiralSpliceBarType,
    SpiralSpliceCoating,
    SpiralSpliceEndCondition,
    evaluate_circular_tie_overlap,
    evaluate_closed_tie_lap,
    evaluate_dorgir,
    evaluate_rect_tie_unrestrained_spacing,
    evaluate_seismic_hook,
    evaluate_spiral_anchor_turns,
    evaluate_spiral_diameter,
    evaluate_spiral_lap_splice,
    evaluate_spiral_ratio,
    evaluate_spiral_spacing,
    evaluate_tie_diameter,
    evaluate_tie_spacing,
    evaluate_tie_shear_extent,
    evaluate_torsion_tie_135hook,
    evaluate_torsion_tie_seismic_hook,
    evaluate_two_piece_tie,
)
from beamgenius.registry.catalog import (
    RULE_BG_TRANS_CIRC_TIE_001,
    RULE_BG_TRANS_CLOSED_TIE_LAP_001,
    RULE_BG_TRANS_DORGIR_001,
    RULE_BG_TRANS_RECT_TIE_001,
    RULE_BG_TRANS_SEISMIC_HOOK_001,
    RULE_BG_TRANS_SPIRAL_ANCHOR_001,
    RULE_BG_TRANS_SPIRAL_DIA_001,
    RULE_BG_TRANS_SPIRAL_LAP_001,
    RULE_BG_TRANS_SPIRAL_RATIO_001,
    RULE_BG_TRANS_SPIRAL_SPACING_001,
    RULE_BG_TRANS_SPIRAL_SPLICE_SEL_PENDING,
    RULE_BG_TRANS_TIE_ANCHOR_PENDING,
    RULE_BG_TRANS_TIE_DIA_001,
    RULE_BG_TRANS_TIE_SHEAR_EXTENT_001,
    RULE_BG_TRANS_TIE_SPACING_001,
    RULE_BG_TRANS_TORSION_TIE_135HOOK_001,
    RULE_BG_TRANS_TORSION_TIE_PENDING,
    RULE_BG_TRANS_TORSION_TIE_SEISMIC_HOOK_001,
    RULE_BG_TRANS_TWO_PIECE_TIE_001,
    RULE_BG_TRANS_WIRE_SUBST_PENDING,
    RULE_BG_TRANS_WIRE_TIE_PENDING,
    get_rule,
    list_blocked_rules,
    list_mabhas9_executable_rules,
)
from beamgenius.registry.gatekeeper import evaluate_rule_gate

MOST = JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY

EXECUTABLE_TRANS_RULES = (
    RULE_BG_TRANS_TIE_SHEAR_EXTENT_001,
    RULE_BG_TRANS_CLOSED_TIE_LAP_001,
    RULE_BG_TRANS_TIE_SPACING_001,
    RULE_BG_TRANS_TIE_DIA_001,
    RULE_BG_TRANS_RECT_TIE_001,
    RULE_BG_TRANS_CIRC_TIE_001,
    RULE_BG_TRANS_SPIRAL_SPACING_001,
    RULE_BG_TRANS_SPIRAL_DIA_001,
    RULE_BG_TRANS_SPIRAL_RATIO_001,
    RULE_BG_TRANS_SPIRAL_ANCHOR_001,
    RULE_BG_TRANS_SPIRAL_LAP_001,
    RULE_BG_TRANS_SEISMIC_HOOK_001,
    RULE_BG_TRANS_DORGIR_001,
    RULE_BG_TRANS_TWO_PIECE_TIE_001,
    RULE_BG_TRANS_TORSION_TIE_135HOOK_001,
    RULE_BG_TRANS_TORSION_TIE_SEISMIC_HOOK_001,
)

BLOCKED_TRANS_RULES = (
    RULE_BG_TRANS_TIE_ANCHOR_PENDING,
    RULE_BG_TRANS_WIRE_TIE_PENDING,
    RULE_BG_TRANS_TORSION_TIE_PENDING,
    RULE_BG_TRANS_WIRE_SUBST_PENDING,
    RULE_BG_TRANS_SPIRAL_SPLICE_SEL_PENDING,
)


# ============================================================================
# Registry / gatekeeper integration
# ============================================================================

def test_all_sixteen_transverse_rules_registered_executable() -> None:
    executable_ids = {r.rule_id for r in list_mabhas9_executable_rules()}
    assert len(EXECUTABLE_TRANS_RULES) == 16
    for rule in EXECUTABLE_TRANS_RULES:
        assert rule.rule_id in executable_ids
        assert rule.execution_allowed is True
        assert rule.status.value == "VERIFIED"
        assert rule.category.value == "CODE_RULE"
        assert rule.jurisdiction is JurisdictionMode.MABHAS_9_COMPLIANCE
        # Every declared dependency must itself be registered + executable
        # (e.g. دورگیر / torsion-tie-seismic-hook depend on the seismic hook).
        for dep_id in rule.dependencies:
            dep = get_rule(dep_id)
            assert dep is not None
            assert dep.execution_allowed is True
            assert dep.rule_id in executable_ids


def test_all_blocked_transverse_rules_not_executable() -> None:
    executable_ids = {r.rule_id for r in list_mabhas9_executable_rules()}
    blocked_ids = {r.rule_id for r in list_blocked_rules()}
    for rule in BLOCKED_TRANS_RULES:
        assert rule.execution_allowed is False
        assert rule.status.value == "VERIFY_PENDING"
        assert rule.rule_id not in executable_ids
        assert rule.rule_id in blocked_ids
        assert rule.blocked_reason is not None and len(rule.blocked_reason) > 0


@pytest.mark.parametrize("rule", EXECUTABLE_TRANS_RULES, ids=lambda r: r.rule_id)
def test_executable_transverse_rules_allowed_in_mabhas_blocked_in_mostofinejad(rule) -> None:
    dec_mabhas = evaluate_rule_gate(
        rule.rule_id, active_jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE
    )
    assert dec_mabhas.allowed
    assert dec_mabhas.blocked_outcome is None

    dec_most = evaluate_rule_gate(rule.rule_id, active_jurisdiction=MOST)
    assert not dec_most.allowed
    assert dec_most.blocked_outcome == EvaluationOutcome.JURISDICTION_BLOCKED


@pytest.mark.parametrize("rule", BLOCKED_TRANS_RULES, ids=lambda r: r.rule_id)
def test_blocked_transverse_rules_blocked_in_every_mode(rule) -> None:
    for mode in JurisdictionMode:
        decision = evaluate_rule_gate(rule.rule_id, active_jurisdiction=mode)
        assert not decision.allowed
        assert decision.blocked_outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
        step = decision.to_blocked_trace_step()
        assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
        assert step.diagnostics[0].required_verification is not None


def test_spiral_splice_selection_blocked_via_transitive_welded_mech_dependency() -> None:
    # 9-21-6-3-5-الف depends on Clause 9-21-4-7 (BG-DEV-SPLICE-WELDED-MECH-PENDING),
    # itself blocked via NBC Chapter 10 -> transitive UNVERIFIED_RULE_BLOCKED.
    decision = evaluate_rule_gate(
        "BG-TRANS-SPIRAL-SPLICE-SEL-PENDING",
        active_jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    )
    assert not decision.allowed
    assert decision.blocked_outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert any(
        d.code == "TRANSITIVE_DEPENDENCY_BLOCKED" for d in decision.diagnostics
    )
    assert any(
        "BG-DEV-SPLICE-WELDED-MECH-PENDING" in d.message for d in decision.diagnostics
    )


def test_blocked_tie_anchor_reason_records_boundary_ambiguity() -> None:
    reason = get_rule("BG-TRANS-TIE-ANCHOR-PENDING").blocked_reason
    assert reason is not None
    assert "280" in reason  # f_y boundary recorded verbatim, never interpolated


def test_dorgir_rule_records_seismic_hook_dependency() -> None:
    # Stage H.3 promoted دورگیر: the seismic-hook geometry is now a VERIFIED
    # executable dependency (BG-TRANS-SEISMIC-HOOK-001), not a block reason.
    rule = get_rule("BG-TRANS-DORGIR-001")
    assert rule is not None
    assert rule.execution_allowed is True
    assert rule.dependencies == ("BG-TRANS-SEISMIC-HOOK-001",)
    assert "seismic" in rule.description.lower()


def test_engine_module_does_not_import_reference_package() -> None:
    # Reference PDF/OCR must NOT become a runtime dependency; the engine must
    # NOT import the reference package nor read source files at runtime.
    import ast

    import beamgenius.engine.transverse_reinforcement_mabhas9 as mod

    with open(mod.__file__) as handle:  # noqa: SIM115
        tree = ast.parse(handle.read())

    imported: list[str] = []
    opens_files = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "open":
                opens_files = True

    assert not any("reference" in name for name in imported)
    assert opens_files is False


# ============================================================================
# BG-TRANS-TIE-SHEAR-EXTENT-001 — Clause 9-21-6-1-1
# ============================================================================

def test_shear_extent_not_used_as_shear_not_applicable() -> None:
    step = evaluate_tie_shear_extent(used_as_shear_reinforcement=False)
    assert step.outcome is EvaluationOutcome.NOT_APPLICABLE


def test_shear_extent_pass_and_boundary_and_fail() -> None:
    # extent == d -> PASS (boundary)
    assert (
        evaluate_tie_shear_extent(
            used_as_shear_reinforcement=True,
            tie_extent_from_compression_face_mm=500.0,
            effective_depth_mm=500.0,
        ).outcome
        is EvaluationOutcome.PASS
    )
    assert (
        evaluate_tie_shear_extent(
            used_as_shear_reinforcement=True,
            tie_extent_from_compression_face_mm=520.0,
            effective_depth_mm=500.0,
        ).final_result
        == 500.0
    )
    fail = evaluate_tie_shear_extent(
        used_as_shear_reinforcement=True,
        tie_extent_from_compression_face_mm=400.0,
        effective_depth_mm=500.0,
    )
    assert fail.outcome is EvaluationOutcome.FAIL
    assert fail.diagnostics[0].code == "TIE_EXTENT_LESS_THAN_EFFECTIVE_DEPTH"


def test_shear_extent_missing_and_invalid() -> None:
    assert evaluate_tie_shear_extent().outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert (
        evaluate_tie_shear_extent(used_as_shear_reinforcement=True).outcome
        is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    )
    assert (
        evaluate_tie_shear_extent(
            used_as_shear_reinforcement=True,
            tie_extent_from_compression_face_mm=0.0,
            effective_depth_mm=500.0,
        ).outcome
        is EvaluationOutcome.INVALID_INPUT
    )


# ============================================================================
# BG-TRANS-CLOSED-TIE-LAP-001 — Clause 9-21-6-1-8
# ============================================================================

def test_closed_tie_lap_no_exception_third_of_anchorage() -> None:
    # shallow member (300 < 450) -> no exception; required = anchorage/3 = 300
    step = evaluate_closed_tie_lap(
        anchorage_length_mm=900.0,
        total_depth_mm=300.0,
        force_per_leg_n=50_000.0,
        provided_leg_lap_mm=300.0,
    )
    assert step.outcome is EvaluationOutcome.PASS
    assert step.final_result == pytest.approx(300.0)
    fail = evaluate_closed_tie_lap(
        anchorage_length_mm=900.0,
        total_depth_mm=300.0,
        force_per_leg_n=50_000.0,
        provided_leg_lap_mm=290.0,
    )
    assert fail.outcome is EvaluationOutcome.FAIL


def test_closed_tie_lap_full_depth_exception_relaxes_to_member_depth() -> None:
    # deep (600 >= 450) and low force (30 kN < 40 kN) -> exception:
    # required = min(anchorage/3 = 800, depth = 600) = 600
    step = evaluate_closed_tie_lap(
        anchorage_length_mm=2400.0,
        total_depth_mm=600.0,
        force_per_leg_n=30_000.0,
        provided_leg_lap_mm=600.0,
    )
    assert step.outcome is EvaluationOutcome.PASS
    assert step.final_result == pytest.approx(600.0)
    assert step.intermediate_values["full_depth_exception_applied"] == 1.0
    fail = evaluate_closed_tie_lap(
        anchorage_length_mm=2400.0,
        total_depth_mm=600.0,
        force_per_leg_n=30_000.0,
        provided_leg_lap_mm=590.0,
    )
    assert fail.outcome is EvaluationOutcome.FAIL


def test_closed_tie_lap_exception_not_triggered_by_high_force() -> None:
    # deep but force = 40 kN exactly -> NOT < 40 kN -> no exception -> required = anchorage/3
    step = evaluate_closed_tie_lap(
        anchorage_length_mm=900.0,
        total_depth_mm=600.0,
        force_per_leg_n=40_000.0,
        provided_leg_lap_mm=300.0,
    )
    assert step.outcome is EvaluationOutcome.PASS
    assert step.intermediate_values["full_depth_exception_applied"] == 0.0
    assert step.final_result == pytest.approx(300.0)


def test_closed_tie_lap_missing_blocked() -> None:
    assert evaluate_closed_tie_lap().outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED


# ============================================================================
# BG-TRANS-TIE-SPACING-001 — Clause 9-21-6-2-1
# ============================================================================

def test_tie_spacing_limits_are_min_of_16db_48db_and_member_dim() -> None:
    # 16*db_long = 320, 48*db_trans = 480, smallest dim = 300 -> limit 300
    step = evaluate_tie_spacing(
        provided_clear_spacing_mm=10.0,
        provided_center_to_center_spacing_mm=300.0,
        aggregate_size_mm=20.0,  # d_agg/3 = 6.667
        longitudinal_bar_diameter_mm=20.0,
        transverse_bar_diameter_mm=10.0,
        smallest_member_dimension_mm=300.0,
    )
    assert step.outcome is EvaluationOutcome.PASS
    assert step.final_result == pytest.approx(300.0)
    # c-c just over -> FAIL
    fail = evaluate_tie_spacing(
        provided_clear_spacing_mm=10.0,
        provided_center_to_center_spacing_mm=301.0,
        aggregate_size_mm=20.0,
        longitudinal_bar_diameter_mm=20.0,
        transverse_bar_diameter_mm=10.0,
        smallest_member_dimension_mm=300.0,
    )
    assert fail.outcome is EvaluationOutcome.FAIL
    assert fail.diagnostics[0].code == "TIE_SPACING_LIMIT_VIOLATED"


def test_tie_spacing_clear_below_aggregate_third_fails() -> None:
    step = evaluate_tie_spacing(
        provided_clear_spacing_mm=5.0,  # < d_agg/3 = 6.667
        provided_center_to_center_spacing_mm=200.0,
        aggregate_size_mm=20.0,
        longitudinal_bar_diameter_mm=20.0,
        transverse_bar_diameter_mm=10.0,
        smallest_member_dimension_mm=300.0,
    )
    assert step.outcome is EvaluationOutcome.FAIL


def test_tie_spacing_governed_by_16db() -> None:
    # smallest dim large; 16*db_long = 16*25 = 400 governs (< 48*10 = 480)
    step = evaluate_tie_spacing(
        provided_clear_spacing_mm=10.0,
        provided_center_to_center_spacing_mm=400.0,
        aggregate_size_mm=20.0,
        longitudinal_bar_diameter_mm=25.0,
        transverse_bar_diameter_mm=10.0,
        smallest_member_dimension_mm=1000.0,
    )
    assert step.final_result == pytest.approx(400.0)
    assert step.outcome is EvaluationOutcome.PASS


def test_tie_spacing_missing_blocked_malformed_invalid() -> None:
    assert evaluate_tie_spacing().outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert (
        evaluate_tie_spacing(
            provided_clear_spacing_mm=-1.0,
            provided_center_to_center_spacing_mm=200.0,
            aggregate_size_mm=20.0,
            longitudinal_bar_diameter_mm=20.0,
            transverse_bar_diameter_mm=10.0,
            smallest_member_dimension_mm=300.0,
        ).outcome
        is EvaluationOutcome.INVALID_INPUT
    )


# ============================================================================
# BG-TRANS-TIE-DIA-001 — Clause 9-21-6-2-2
# ============================================================================

def test_tie_dia_small_bar_requires_10mm() -> None:
    step = evaluate_tie_diameter(
        longitudinal_bar_diameter_mm=32.0, is_bundled=False, provided_tie_diameter_mm=10.0
    )
    assert step.outcome is EvaluationOutcome.PASS
    assert step.final_result == 10.0
    fail = evaluate_tie_diameter(
        longitudinal_bar_diameter_mm=32.0, is_bundled=False, provided_tie_diameter_mm=8.0
    )
    assert fail.outcome is EvaluationOutcome.FAIL
    assert fail.diagnostics[0].code == "TIE_DIAMETER_BELOW_MINIMUM"


def test_tie_dia_large_bar_requires_12mm() -> None:
    step = evaluate_tie_diameter(
        longitudinal_bar_diameter_mm=34.0, is_bundled=False, provided_tie_diameter_mm=12.0
    )
    assert step.outcome is EvaluationOutcome.PASS
    assert step.final_result == 12.0
    fail = evaluate_tie_diameter(
        longitudinal_bar_diameter_mm=40.0, is_bundled=False, provided_tie_diameter_mm=10.0
    )
    assert fail.outcome is EvaluationOutcome.FAIL


def test_tie_dia_bundled_requires_12mm_regardless_of_db() -> None:
    step = evaluate_tie_diameter(
        longitudinal_bar_diameter_mm=20.0, is_bundled=True, provided_tie_diameter_mm=12.0
    )
    assert step.outcome is EvaluationOutcome.PASS
    assert step.final_result == 12.0


def test_tie_dia_33mm_gap_is_blocked_never_interpolated() -> None:
    # 32 < d_b = 33 < 34, non-bundled -> no verified branch -> BLOCKED
    step = evaluate_tie_diameter(
        longitudinal_bar_diameter_mm=33.0, is_bundled=False, provided_tie_diameter_mm=12.0
    )
    assert step.outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "TIE_DIA_NO_VERIFIED_BRANCH"
    # 32.5 also in the gap
    step2 = evaluate_tie_diameter(
        longitudinal_bar_diameter_mm=32.5, is_bundled=False, provided_tie_diameter_mm=12.0
    )
    assert step2.outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED


def test_tie_dia_33mm_bundled_uses_12mm_branch() -> None:
    # bundled at 33 mm -> ب branch applies (bundles -> 12 mm), not blocked
    step = evaluate_tie_diameter(
        longitudinal_bar_diameter_mm=33.0, is_bundled=True, provided_tie_diameter_mm=12.0
    )
    assert step.outcome is EvaluationOutcome.PASS
    assert step.final_result == 12.0


def test_tie_dia_missing_blocked_invalid_enum() -> None:
    assert evaluate_tie_diameter().outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    # missing is_bundled
    assert (
        evaluate_tie_diameter(
            longitudinal_bar_diameter_mm=20.0, provided_tie_diameter_mm=10.0
        ).outcome
        is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    )
    # malformed diameter
    assert (
        evaluate_tie_diameter(
            longitudinal_bar_diameter_mm=0.0, is_bundled=False, provided_tie_diameter_mm=10.0
        ).outcome
        is EvaluationOutcome.INVALID_INPUT
    )


# ============================================================================
# BG-TRANS-RECT-TIE-001 — Clause 9-21-6-2-4-ب
# ============================================================================

def test_rect_tie_unrestrained_spacing_boundary() -> None:
    assert (
        evaluate_rect_tie_unrestrained_spacing(unrestrained_bar_clear_spacing_mm=150.0).outcome
        is EvaluationOutcome.PASS
    )
    fail = evaluate_rect_tie_unrestrained_spacing(unrestrained_bar_clear_spacing_mm=151.0)
    assert fail.outcome is EvaluationOutcome.FAIL
    assert fail.diagnostics[0].code == "RECT_TIE_UNRESTRAINED_SPACING_EXCEEDS_LIMIT"


def test_rect_tie_missing_blocked() -> None:
    assert (
        evaluate_rect_tie_unrestrained_spacing().outcome
        is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    )


# ============================================================================
# BG-TRANS-CIRC-TIE-001 — Clause 9-21-6-2-5-الف
# ============================================================================

def test_circular_tie_overlap_boundary() -> None:
    assert evaluate_circular_tie_overlap(tie_end_overlap_mm=150.0).outcome is EvaluationOutcome.PASS
    fail = evaluate_circular_tie_overlap(tie_end_overlap_mm=149.0)
    assert fail.outcome is EvaluationOutcome.FAIL
    assert fail.diagnostics[0].code == "CIRCULAR_TIE_OVERLAP_BELOW_MINIMUM"


def test_circular_tie_missing_blocked() -> None:
    assert evaluate_circular_tie_overlap().outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED


# ============================================================================
# BG-TRANS-SPIRAL-SPACING-001 — Clause 9-21-6-3-1
# ============================================================================

def test_spiral_spacing_clear_is_max_of_third_agg_and_25() -> None:
    # d_agg = 75 -> d_agg/3 = 25 -> min clear = max(25, 25) = 25; pitch 75 -> PASS
    step = evaluate_spiral_spacing(
        provided_clear_spacing_mm=25.0, provided_pitch_mm=75.0, aggregate_size_mm=75.0
    )
    assert step.outcome is EvaluationOutcome.PASS
    assert step.intermediate_values["min_clear_required_mm"] == pytest.approx(25.0)
    # pitch just over -> FAIL
    fail = evaluate_spiral_spacing(
        provided_clear_spacing_mm=25.0, provided_pitch_mm=76.0, aggregate_size_mm=75.0
    )
    assert fail.outcome is EvaluationOutcome.FAIL
    assert fail.diagnostics[0].code == "SPIRAL_SPACING_LIMIT_VIOLATED"


def test_spiral_spacing_clear_governed_by_third_aggregate_above_25() -> None:
    # d_agg = 90 -> d_agg/3 = 30 governs over the 25 mm floor
    step = evaluate_spiral_spacing(
        provided_clear_spacing_mm=30.0, provided_pitch_mm=60.0, aggregate_size_mm=90.0
    )
    assert step.outcome is EvaluationOutcome.PASS
    assert step.intermediate_values["min_clear_required_mm"] == pytest.approx(30.0)
    fail = evaluate_spiral_spacing(
        provided_clear_spacing_mm=29.0, provided_pitch_mm=60.0, aggregate_size_mm=90.0
    )
    assert fail.outcome is EvaluationOutcome.FAIL


def test_spiral_spacing_missing_blocked() -> None:
    assert evaluate_spiral_spacing().outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED


# ============================================================================
# BG-TRANS-SPIRAL-DIA-001 — Clause 9-21-6-3-2
# ============================================================================

def test_spiral_diameter_boundary() -> None:
    assert evaluate_spiral_diameter(provided_spiral_diameter_mm=10.0).outcome is EvaluationOutcome.PASS
    fail = evaluate_spiral_diameter(provided_spiral_diameter_mm=8.0)
    assert fail.outcome is EvaluationOutcome.FAIL
    assert fail.diagnostics[0].code == "SPIRAL_DIAMETER_BELOW_MINIMUM"


def test_spiral_diameter_missing_blocked() -> None:
    assert evaluate_spiral_diameter().outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED


# ============================================================================
# BG-TRANS-SPIRAL-RATIO-001 — Clause 9-21-6-3-3 & Eq. (9-21-8)
# ============================================================================

def test_spiral_ratio_eq_9_21_8_reference_value() -> None:
    # rho_req = 0.45*(200000/160000 - 1)*(30/400) = 0.45*0.25*0.075 = 0.0084375
    step = evaluate_spiral_ratio(
        gross_area_mm2=200_000.0,
        core_area_mm2=160_000.0,
        concrete_strength_mpa=30.0,
        spiral_yield_stress_mpa=400.0,
        provided_rho_s=0.0085,
    )
    assert step.outcome is EvaluationOutcome.PASS
    assert step.final_result == pytest.approx(0.0084375)
    fail = evaluate_spiral_ratio(
        gross_area_mm2=200_000.0,
        core_area_mm2=160_000.0,
        concrete_strength_mpa=30.0,
        spiral_yield_stress_mpa=400.0,
        provided_rho_s=0.0084,
    )
    assert fail.outcome is EvaluationOutcome.FAIL
    assert fail.diagnostics[0].code == "SPIRAL_RATIO_BELOW_REQUIRED"


def test_spiral_ratio_fyt_above_700_fails() -> None:
    step = evaluate_spiral_ratio(
        gross_area_mm2=200_000.0,
        core_area_mm2=160_000.0,
        concrete_strength_mpa=30.0,
        spiral_yield_stress_mpa=750.0,
        provided_rho_s=0.05,
    )
    assert step.outcome is EvaluationOutcome.FAIL
    assert step.diagnostics[0].code == "SPIRAL_FYT_EXCEEDS_700_LIMIT"


def test_spiral_ratio_fyt_exactly_700_allowed() -> None:
    step = evaluate_spiral_ratio(
        gross_area_mm2=200_000.0,
        core_area_mm2=160_000.0,
        concrete_strength_mpa=30.0,
        spiral_yield_stress_mpa=700.0,
        provided_rho_s=0.05,
    )
    assert step.outcome is EvaluationOutcome.PASS


def test_spiral_ratio_missing_blocked() -> None:
    assert evaluate_spiral_ratio().outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED


# ============================================================================
# BG-TRANS-SPIRAL-ANCHOR-001 — Clause 9-21-6-3-4
# ============================================================================

def test_spiral_anchor_turns_boundary() -> None:
    assert evaluate_spiral_anchor_turns(extra_turns_each_end=1.5).outcome is EvaluationOutcome.PASS
    fail = evaluate_spiral_anchor_turns(extra_turns_each_end=1.0)
    assert fail.outcome is EvaluationOutcome.FAIL
    assert fail.diagnostics[0].code == "SPIRAL_ANCHOR_TURNS_BELOW_MINIMUM"


def test_spiral_anchor_missing_blocked() -> None:
    assert evaluate_spiral_anchor_turns().outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED


# ============================================================================
# BG-TRANS-SPIRAL-LAP-001 — Clause 9-21-6-3-6 & Table 9-21-7
# ============================================================================

@pytest.mark.parametrize(
    "bar_type,coating,end,db,expected",
    [
        # deformed bar
        (SpiralSpliceBarType.DEFORMED_BAR, SpiralSpliceCoating.UNCOATED, SpiralSpliceEndCondition.NO_HOOK, 10.0, 480.0),
        (SpiralSpliceBarType.DEFORMED_BAR, SpiralSpliceCoating.GALVANIZED, SpiralSpliceEndCondition.NO_HOOK, 10.0, 480.0),
        (SpiralSpliceBarType.DEFORMED_BAR, SpiralSpliceCoating.EPOXY, SpiralSpliceEndCondition.NO_HOOK, 10.0, 720.0),
        (SpiralSpliceBarType.DEFORMED_BAR, SpiralSpliceCoating.DUAL_COATED, SpiralSpliceEndCondition.NO_HOOK, 10.0, 720.0),
        (SpiralSpliceBarType.DEFORMED_BAR, SpiralSpliceCoating.EPOXY, SpiralSpliceEndCondition.STANDARD_TRANSVERSE_HOOK, 10.0, 480.0),
        # deformed wire
        (SpiralSpliceBarType.DEFORMED_WIRE, SpiralSpliceCoating.UNCOATED, SpiralSpliceEndCondition.NO_HOOK, 10.0, 480.0),
        (SpiralSpliceBarType.DEFORMED_WIRE, SpiralSpliceCoating.EPOXY, SpiralSpliceEndCondition.NO_HOOK, 10.0, 720.0),
        (SpiralSpliceBarType.DEFORMED_WIRE, SpiralSpliceCoating.EPOXY, SpiralSpliceEndCondition.STANDARD_TRANSVERSE_HOOK, 10.0, 480.0),
        # plain bar
        (SpiralSpliceBarType.PLAIN_BAR, SpiralSpliceCoating.UNCOATED, SpiralSpliceEndCondition.NO_HOOK, 10.0, 720.0),
        (SpiralSpliceBarType.PLAIN_BAR, SpiralSpliceCoating.GALVANIZED, SpiralSpliceEndCondition.NO_HOOK, 10.0, 720.0),
        (SpiralSpliceBarType.PLAIN_BAR, SpiralSpliceCoating.GALVANIZED, SpiralSpliceEndCondition.STANDARD_TRANSVERSE_HOOK, 10.0, 480.0),
        # plain wire
        (SpiralSpliceBarType.PLAIN_WIRE, SpiralSpliceCoating.UNCOATED, SpiralSpliceEndCondition.NO_HOOK, 10.0, 720.0),
        (SpiralSpliceBarType.PLAIN_WIRE, SpiralSpliceCoating.UNCOATED, SpiralSpliceEndCondition.STANDARD_TRANSVERSE_HOOK, 20.0, 960.0),
    ],
)
def test_spiral_lap_table_rows(bar_type, coating, end, db, expected) -> None:
    step = evaluate_spiral_lap_splice(
        splice_bar_type=bar_type, coating_class=coating, end_condition=end, bar_diameter_mm=db
    )
    assert step.outcome is EvaluationOutcome.COMPUTED
    assert step.final_result == pytest.approx(expected)


def test_spiral_lap_300mm_floor_governs_small_bars() -> None:
    # 48*5 = 240 < 300 -> floored to 300
    step = evaluate_spiral_lap_splice(
        splice_bar_type=SpiralSpliceBarType.DEFORMED_WIRE,
        coating_class=SpiralSpliceCoating.EPOXY,
        end_condition=SpiralSpliceEndCondition.STANDARD_TRANSVERSE_HOOK,
        bar_diameter_mm=5.0,
    )
    assert step.outcome is EvaluationOutcome.COMPUTED
    assert step.final_result == 300.0
    assert step.intermediate_values["lap_before_floor_mm"] == pytest.approx(240.0)


@pytest.mark.parametrize(
    "bar_type,coating,end",
    [
        # not printed in Table 9-21-7 -> deterministically BLOCKED (no interpretation)
        (SpiralSpliceBarType.DEFORMED_WIRE, SpiralSpliceCoating.GALVANIZED, SpiralSpliceEndCondition.NO_HOOK),
        (SpiralSpliceBarType.DEFORMED_WIRE, SpiralSpliceCoating.DUAL_COATED, SpiralSpliceEndCondition.NO_HOOK),
        (SpiralSpliceBarType.PLAIN_WIRE, SpiralSpliceCoating.EPOXY, SpiralSpliceEndCondition.NO_HOOK),
        (SpiralSpliceBarType.PLAIN_WIRE, SpiralSpliceCoating.GALVANIZED, SpiralSpliceEndCondition.NO_HOOK),
        (SpiralSpliceBarType.PLAIN_BAR, SpiralSpliceCoating.EPOXY, SpiralSpliceEndCondition.NO_HOOK),
        (SpiralSpliceBarType.DEFORMED_BAR, SpiralSpliceCoating.UNCOATED, SpiralSpliceEndCondition.STANDARD_TRANSVERSE_HOOK),
    ],
)
def test_spiral_lap_unlisted_combination_blocked(bar_type, coating, end) -> None:
    step = evaluate_spiral_lap_splice(
        splice_bar_type=bar_type, coating_class=coating, end_condition=end, bar_diameter_mm=10.0
    )
    assert step.outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "SPIRAL_LAP_COMBINATION_NOT_IN_TABLE_9_21_7"


def test_spiral_lap_missing_and_invalid() -> None:
    assert evaluate_spiral_lap_splice().outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    # missing bar diameter
    assert (
        evaluate_spiral_lap_splice(
            splice_bar_type=SpiralSpliceBarType.PLAIN_BAR,
            coating_class=SpiralSpliceCoating.UNCOATED,
            end_condition=SpiralSpliceEndCondition.NO_HOOK,
        ).outcome
        is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    )
    # malformed diameter
    assert (
        evaluate_spiral_lap_splice(
            splice_bar_type=SpiralSpliceBarType.PLAIN_BAR,
            coating_class=SpiralSpliceCoating.UNCOATED,
            end_condition=SpiralSpliceEndCondition.NO_HOOK,
            bar_diameter_mm=-5.0,
        ).outcome
        is EvaluationOutcome.INVALID_INPUT
    )


def test_spiral_lap_jurisdiction_blocked() -> None:
    step = evaluate_spiral_lap_splice(
        splice_bar_type=SpiralSpliceBarType.PLAIN_BAR,
        coating_class=SpiralSpliceCoating.UNCOATED,
        end_condition=SpiralSpliceEndCondition.NO_HOOK,
        bar_diameter_mm=10.0,
        jurisdiction_mode=MOST,
    )
    assert step.outcome is EvaluationOutcome.JURISDICTION_BLOCKED


# ============================================================================
# Cross-cutting: trace metadata + jurisdiction for a representative check rule
# ============================================================================

def test_trace_step_carries_rule_reference_and_source() -> None:
    step = evaluate_spiral_diameter(provided_spiral_diameter_mm=12.0)
    assert step.rule_reference is RULE_BG_TRANS_SPIRAL_DIA_001
    assert step.clause_or_equation == RULE_BG_TRANS_SPIRAL_DIA_001.clause_or_equation
    assert step.source_document == RULE_BG_TRANS_SPIRAL_DIA_001.source_document
    assert step.pdf_page == 468
    assert step.printed_page == 448


def test_check_rule_jurisdiction_blocked_in_mostofinejad() -> None:
    step = evaluate_tie_spacing(
        provided_clear_spacing_mm=10.0,
        provided_center_to_center_spacing_mm=200.0,
        aggregate_size_mm=20.0,
        longitudinal_bar_diameter_mm=20.0,
        transverse_bar_diameter_mm=10.0,
        smallest_member_dimension_mm=300.0,
        jurisdiction_mode=MOST,
    )
    assert step.outcome is EvaluationOutcome.JURISDICTION_BLOCKED
