"""Focused tests for the Phase 2F Stage E Clause 9-21-4 lap-splice and
bearing-splice evaluators (Mabhas 9, 1399 5th ed.).

Every expected numeric value was hand-verified against the visually
re-verified source equations/factors (footer-confirmed Printed pp. 436-441 /
PDF pp. 456-461; evidence scan phase2f-source-442-472 @ df8067a, re-read
2026-10-06) before being recorded here.
"""

from __future__ import annotations

import math

import pytest

from beamgenius.domain.enums import EvaluationOutcome, JurisdictionMode
from beamgenius.engine.development_lap_splice_mabhas9 import (
    BarStressAction,
    SpliceMethod,
    TensionLapClass,
    evaluate_lap_splice_applicability,
    evaluate_lap_splice_compression,
    evaluate_lap_splice_compression_diffdia,
    evaluate_lap_splice_spacing,
    evaluate_lap_splice_tension,
    evaluate_lap_splice_tension_diffdia,
    evaluate_splice_bearing,
)
from beamgenius.registry.catalog import (
    RULE_BG_DEV_LAP_APPLIC_001,
    RULE_BG_DEV_LAP_COMPRESSION_001,
    RULE_BG_DEV_LAP_COMPRESSION_DIFFDIA_001,
    RULE_BG_DEV_LAP_SPACING_001,
    RULE_BG_DEV_LAP_TENSION_001,
    RULE_BG_DEV_LAP_TENSION_DIFFDIA_001,
    RULE_BG_DEV_LAP_WIRE_DEFORMED_PENDING,
    RULE_BG_DEV_LAP_WIRE_PLAIN_PENDING,
    RULE_BG_DEV_SPLICE_BEARING_001,
    RULE_BG_DEV_SPLICE_WELDED_MECH_PENDING,
    get_rule,
    list_blocked_rules,
    list_mabhas9_executable_rules,
)
from beamgenius.registry.gatekeeper import evaluate_rule_gate

MOST = JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY

EXECUTABLE_LAP_RULES = (
    RULE_BG_DEV_LAP_APPLIC_001,
    RULE_BG_DEV_LAP_SPACING_001,
    RULE_BG_DEV_LAP_TENSION_001,
    RULE_BG_DEV_LAP_TENSION_DIFFDIA_001,
    RULE_BG_DEV_LAP_COMPRESSION_001,
    RULE_BG_DEV_LAP_COMPRESSION_DIFFDIA_001,
    RULE_BG_DEV_SPLICE_BEARING_001,
)

BLOCKED_LAP_RULES = (
    RULE_BG_DEV_LAP_WIRE_DEFORMED_PENDING,
    RULE_BG_DEV_LAP_WIRE_PLAIN_PENDING,
    RULE_BG_DEV_SPLICE_WELDED_MECH_PENDING,
)


# ============================================================================
# Registry / gatekeeper integration
# ============================================================================

def test_all_seven_lap_rules_are_registered_executable() -> None:
    executable_ids = {r.rule_id for r in list_mabhas9_executable_rules()}
    for rule in EXECUTABLE_LAP_RULES:
        assert rule.rule_id in executable_ids
        assert rule.execution_allowed is True


def test_all_blocked_lap_rules_are_not_executable() -> None:
    executable_ids = {r.rule_id for r in list_mabhas9_executable_rules()}
    blocked_ids = {r.rule_id for r in list_blocked_rules()}
    for rule in BLOCKED_LAP_RULES:
        assert rule.execution_allowed is False
        assert rule.status.value == "VERIFY_PENDING"
        assert rule.rule_id not in executable_ids
        assert rule.rule_id in blocked_ids
        assert rule.blocked_reason is not None and len(rule.blocked_reason) > 0


@pytest.mark.parametrize("rule", EXECUTABLE_LAP_RULES, ids=lambda r: r.rule_id)
def test_executable_lap_rules_allowed_in_mabhas_blocked_in_mostofinejad(rule) -> None:
    dec_mabhas = evaluate_rule_gate(
        rule.rule_id, active_jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE
    )
    assert dec_mabhas.allowed
    assert dec_mabhas.blocked_outcome is None

    dec_most = evaluate_rule_gate(rule.rule_id, active_jurisdiction=MOST)
    assert not dec_most.allowed
    assert dec_most.blocked_outcome == EvaluationOutcome.JURISDICTION_BLOCKED


@pytest.mark.parametrize("rule", BLOCKED_LAP_RULES, ids=lambda r: r.rule_id)
def test_blocked_lap_rules_blocked_in_every_mode(rule) -> None:
    for mode in JurisdictionMode:
        decision = evaluate_rule_gate(rule.rule_id, active_jurisdiction=mode)
        assert not decision.allowed
        assert decision.blocked_outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
        step = decision.to_blocked_trace_step()
        assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
        assert step.diagnostics[0].required_verification is not None


def test_blocked_wire_plain_reason_records_disjunct() -> None:
    # 9-21-4-4-1-ب «و یا» disjunct must be recorded verbatim and never executed.
    reason = get_rule("BG-DEV-LAP-WIRE-PLAIN-PENDING").blocked_reason
    assert reason is not None
    assert "و یا" in reason


def test_engine_module_does_not_import_reference_package() -> None:
    # Reference PDF/OCR must NOT become a runtime dependency; the engine must
    # NOT import the reference package nor read source files at runtime.
    # Inspect the AST so docstring/comment mentions (e.g. the evidence-scan
    # name) do not trigger a false positive.
    import ast

    import beamgenius.engine.development_lap_splice_mabhas9 as mod

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
# BG-DEV-LAP-APPLIC-001 — Clause 9-21-4-1-1 / 9-21-4-1-2
# ============================================================================

def test_applic_tension_within_limit_passes() -> None:
    step = evaluate_lap_splice_applicability(
        splice_method=SpliceMethod.LAP,
        bar_stress_action=BarStressAction.TENSION,
        bar_diameter_mm=20.0,
    )
    assert step.outcome is EvaluationOutcome.PASS
    assert step.final_result == pytest.approx(20.0)


def test_applic_tension_boundary_34_passes_above_fails() -> None:
    assert (
        evaluate_lap_splice_applicability(
            splice_method=SpliceMethod.LAP,
            bar_stress_action=BarStressAction.TENSION,
            bar_diameter_mm=34.0,
        ).outcome
        is EvaluationOutcome.PASS
    )
    fail = evaluate_lap_splice_applicability(
        splice_method=SpliceMethod.LAP,
        bar_stress_action=BarStressAction.TENSION,
        bar_diameter_mm=36.0,
    )
    assert fail.outcome is EvaluationOutcome.FAIL
    assert fail.diagnostics[0].code == "LAP_NOT_PERMITTED_DIAMETER_EXCEEDS_LIMIT"


def test_applic_compression_single_and_diffdia() -> None:
    # single bar <= 34
    assert (
        evaluate_lap_splice_applicability(
            splice_method=SpliceMethod.LAP,
            bar_stress_action=BarStressAction.COMPRESSION,
            bar_diameter_mm=34.0,
        ).outcome
        is EvaluationOutcome.PASS
    )
    # compression different-diameter 42 -> 34 boundary permitted (9-21-4-1-2-ب)
    assert (
        evaluate_lap_splice_applicability(
            splice_method=SpliceMethod.LAP,
            bar_stress_action=BarStressAction.COMPRESSION,
            bar_diameter_mm=34.0,
            larger_bar_diameter_mm=42.0,
        ).outcome
        is EvaluationOutcome.PASS
    )
    # larger > 42 -> FAIL
    assert (
        evaluate_lap_splice_applicability(
            splice_method=SpliceMethod.LAP,
            bar_stress_action=BarStressAction.COMPRESSION,
            bar_diameter_mm=34.0,
            larger_bar_diameter_mm=43.0,
        ).outcome
        is EvaluationOutcome.FAIL
    )
    # smaller > 34 -> FAIL
    assert (
        evaluate_lap_splice_applicability(
            splice_method=SpliceMethod.LAP,
            bar_stress_action=BarStressAction.COMPRESSION,
            bar_diameter_mm=36.0,
            larger_bar_diameter_mm=42.0,
        ).outcome
        is EvaluationOutcome.FAIL
    )


@pytest.mark.parametrize(
    "method", [SpliceMethod.BEARING, SpliceMethod.WELDED, SpliceMethod.MECHANICAL]
)
def test_applic_non_lap_methods_not_applicable(method: SpliceMethod) -> None:
    step = evaluate_lap_splice_applicability(splice_method=method)
    assert step.outcome is EvaluationOutcome.NOT_APPLICABLE


def test_applic_missing_inputs_blocked() -> None:
    assert evaluate_lap_splice_applicability().outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    # lap method but no stress action
    assert (
        evaluate_lap_splice_applicability(splice_method=SpliceMethod.LAP).outcome
        is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    )
    # lap + action but no diameter
    assert (
        evaluate_lap_splice_applicability(
            splice_method=SpliceMethod.LAP, bar_stress_action=BarStressAction.TENSION
        ).outcome
        is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    )


def test_applic_malformed_inputs_invalid() -> None:
    assert (
        evaluate_lap_splice_applicability(
            splice_method="lap",  # type: ignore[arg-type]
            bar_stress_action=BarStressAction.TENSION,
            bar_diameter_mm=20.0,
        ).outcome
        is EvaluationOutcome.INVALID_INPUT
    )
    assert (
        evaluate_lap_splice_applicability(
            splice_method=SpliceMethod.LAP,
            bar_stress_action=BarStressAction.TENSION,
            bar_diameter_mm=0.0,
        ).outcome
        is EvaluationOutcome.INVALID_INPUT
    )


def test_applic_jurisdiction_blocked() -> None:
    step = evaluate_lap_splice_applicability(
        splice_method=SpliceMethod.LAP,
        bar_stress_action=BarStressAction.TENSION,
        bar_diameter_mm=20.0,
        jurisdiction_mode=MOST,
    )
    assert step.outcome is EvaluationOutcome.JURISDICTION_BLOCKED


# ============================================================================
# BG-DEV-LAP-SPACING-001 — Clause 9-21-4-1-4
# ============================================================================

def test_spacing_limit_is_min_of_lap_over_five_and_150() -> None:
    # lap/5 = 200 > 150 -> limit 150; spacing 200 -> FAIL
    step = evaluate_lap_splice_spacing(
        lap_length_mm=1000.0, transverse_center_to_center_spacing_mm=200.0
    )
    assert step.final_result == pytest.approx(150.0)
    assert step.outcome is EvaluationOutcome.FAIL
    # lap/5 = 100 < 150 -> limit 100
    step2 = evaluate_lap_splice_spacing(
        lap_length_mm=500.0, transverse_center_to_center_spacing_mm=100.0
    )
    assert step2.final_result == pytest.approx(100.0)
    assert step2.outcome is EvaluationOutcome.PASS


def test_spacing_boundary_passes_and_just_over_fails() -> None:
    assert (
        evaluate_lap_splice_spacing(
            lap_length_mm=1000.0, transverse_center_to_center_spacing_mm=150.0
        ).outcome
        is EvaluationOutcome.PASS
    )
    assert (
        evaluate_lap_splice_spacing(
            lap_length_mm=1000.0, transverse_center_to_center_spacing_mm=150.0001
        ).outcome
        is EvaluationOutcome.FAIL
    )


def test_spacing_missing_and_malformed() -> None:
    assert (
        evaluate_lap_splice_spacing(
            transverse_center_to_center_spacing_mm=100.0
        ).outcome
        is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    )
    assert (
        evaluate_lap_splice_spacing(
            lap_length_mm=1000.0, transverse_center_to_center_spacing_mm=-1.0
        ).outcome
        is EvaluationOutcome.INVALID_INPUT
    )


# ============================================================================
# BG-DEV-LAP-TENSION-001 — Clause 9-21-4-2-1
# ============================================================================

def test_tension_class_b_reference_value() -> None:
    # l_st = 1.3 * l_d = 1.3 * 400 = 520
    step = evaluate_lap_splice_tension(
        development_length_mm=400.0, tension_lap_class=TensionLapClass.B
    )
    assert step.outcome is EvaluationOutcome.COMPUTED
    assert step.final_result == pytest.approx(520.0)


def test_tension_min_300_floor() -> None:
    # 1.3 * 200 = 260 -> floored at 300
    step = evaluate_lap_splice_tension(
        development_length_mm=200.0, tension_lap_class=TensionLapClass.B
    )
    assert step.final_result == pytest.approx(300.0)


def test_tension_class_a_conditions_met() -> None:
    # 1.0 * 400 = 400 (>= 300 floor)
    step = evaluate_lap_splice_tension(
        development_length_mm=400.0,
        tension_lap_class=TensionLapClass.A,
        as_provided_over_required_ratio=2.0,
        fraction_of_provided_bars_spliced=0.5,
    )
    assert step.outcome is EvaluationOutcome.COMPUTED
    assert step.final_result == pytest.approx(400.0)


@pytest.mark.parametrize(
    "ratio,frac",
    [(1.99, 0.5), (2.0, 0.51), (1.5, 0.4)],
)
def test_tension_class_a_conditions_unmet_fails(ratio: float, frac: float) -> None:
    step = evaluate_lap_splice_tension(
        development_length_mm=400.0,
        tension_lap_class=TensionLapClass.A,
        as_provided_over_required_ratio=ratio,
        fraction_of_provided_bars_spliced=frac,
    )
    assert step.outcome is EvaluationOutcome.FAIL
    assert step.diagnostics[0].code == "CLASS_A_CONDITIONS_NOT_MET"


def test_tension_missing_development_length_blocked() -> None:
    step = evaluate_lap_splice_tension(tension_lap_class=TensionLapClass.B)
    assert step.outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "MISSING_DEVELOPMENT_LENGTH"


def test_tension_class_a_missing_conditions_blocked() -> None:
    step = evaluate_lap_splice_tension(
        development_length_mm=400.0, tension_lap_class=TensionLapClass.A
    )
    assert step.outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "MISSING_CLASS_A_CONDITIONS"


def test_tension_malformed_inputs_invalid() -> None:
    assert (
        evaluate_lap_splice_tension(
            development_length_mm=-5.0, tension_lap_class=TensionLapClass.B
        ).outcome
        is EvaluationOutcome.INVALID_INPUT
    )
    assert (
        evaluate_lap_splice_tension(
            development_length_mm=float("nan"), tension_lap_class=TensionLapClass.B
        ).outcome
        is EvaluationOutcome.INVALID_INPUT
    )


# ============================================================================
# BG-DEV-LAP-TENSION-DIFFDIA-001 — Clause 9-21-4-2 (mixed dia)
# ============================================================================

def test_tension_diffdia_takes_max() -> None:
    assert (
        evaluate_lap_splice_tension_diffdia(
            development_length_larger_bar_mm=600.0,
            tension_lap_length_smaller_bar_mm=500.0,
        ).final_result
        == pytest.approx(600.0)
    )
    assert (
        evaluate_lap_splice_tension_diffdia(
            development_length_larger_bar_mm=500.0,
            tension_lap_length_smaller_bar_mm=600.0,
        ).final_result
        == pytest.approx(600.0)
    )


def test_tension_diffdia_missing_blocked() -> None:
    assert (
        evaluate_lap_splice_tension_diffdia(
            tension_lap_length_smaller_bar_mm=500.0
        ).outcome
        is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    )


# ============================================================================
# BG-DEV-LAP-COMPRESSION-001 — Clause 9-21-4-5-1
# ============================================================================

def test_compression_low_fy_branch() -> None:
    # f_y = 400 <= 420: l_sc = 0.071 * 400 * 20 = 568
    step = evaluate_lap_splice_compression(
        bar_diameter_mm=20.0, yield_stress_mpa=400.0
    )
    assert step.outcome is EvaluationOutcome.COMPUTED
    assert step.final_result == pytest.approx(568.0)


def test_compression_high_fy_branch_and_boundary() -> None:
    # f_y = 420 boundary uses low branch: 0.071 * 420 * 20 = 596.4
    low = evaluate_lap_splice_compression(bar_diameter_mm=20.0, yield_stress_mpa=420.0)
    assert low.final_result == pytest.approx(596.4)
    # f_y = 500 > 420: (0.13*500 - 24) * 20 = 41 * 20 = 820
    high = evaluate_lap_splice_compression(bar_diameter_mm=20.0, yield_stress_mpa=500.0)
    assert high.final_result == pytest.approx(820.0)
    # just above threshold: (0.13*420.01 - 24) * 20
    above = evaluate_lap_splice_compression(
        bar_diameter_mm=20.0, yield_stress_mpa=420.01
    )
    assert above.final_result == pytest.approx((0.13 * 420.01 - 24.0) * 20.0)


def test_compression_min_300_floor() -> None:
    # 0.071 * 400 * 10 = 284 -> floored at 300
    step = evaluate_lap_splice_compression(
        bar_diameter_mm=10.0, yield_stress_mpa=400.0
    )
    assert step.final_result == pytest.approx(300.0)


def test_compression_diameter_above_34_not_applicable() -> None:
    assert (
        evaluate_lap_splice_compression(
            bar_diameter_mm=34.0, yield_stress_mpa=400.0
        ).outcome
        is EvaluationOutcome.COMPUTED
    )
    assert (
        evaluate_lap_splice_compression(
            bar_diameter_mm=40.0, yield_stress_mpa=400.0
        ).outcome
        is EvaluationOutcome.NOT_APPLICABLE
    )


def test_compression_missing_blocked_malformed_invalid() -> None:
    assert (
        evaluate_lap_splice_compression(bar_diameter_mm=20.0).outcome
        is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    )
    assert (
        evaluate_lap_splice_compression(
            bar_diameter_mm=20.0, yield_stress_mpa=0.0
        ).outcome
        is EvaluationOutcome.INVALID_INPUT
    )


# ============================================================================
# BG-DEV-LAP-COMPRESSION-DIFFDIA-001 — Clause 9-21-4-5-2
# ============================================================================

def test_compression_diffdia_takes_max() -> None:
    assert (
        evaluate_lap_splice_compression_diffdia(
            compression_dev_length_larger_bar_mm=700.0,
            compression_lap_length_smaller_bar_mm=568.0,
        ).final_result
        == pytest.approx(700.0)
    )
    assert (
        evaluate_lap_splice_compression_diffdia(
            compression_dev_length_larger_bar_mm=500.0,
            compression_lap_length_smaller_bar_mm=568.0,
        ).final_result
        == pytest.approx(568.0)
    )


def test_compression_diffdia_missing_blocked() -> None:
    assert (
        evaluate_lap_splice_compression_diffdia(
            compression_dev_length_larger_bar_mm=700.0
        ).outcome
        is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    )


# ============================================================================
# BG-DEV-SPLICE-BEARING-001 — Clause 9-21-4-6
# ============================================================================

def _bearing_ok(**overrides) -> dict:
    base = dict(
        bars_compression_only=True,
        ends_cut_perpendicular=True,
        bars_coaxial=True,
        member_has_confinement=True,
        end_face_deviation_deg=4.0,
        axial_misalignment_deg=2.0,
    )
    base.update(overrides)
    return base


def test_bearing_all_conditions_pass() -> None:
    step = evaluate_splice_bearing(**_bearing_ok())
    assert step.outcome is EvaluationOutcome.PASS


def test_bearing_angle_boundaries_pass() -> None:
    step = evaluate_splice_bearing(
        **_bearing_ok(end_face_deviation_deg=5.0, axial_misalignment_deg=3.0)
    )
    assert step.outcome is EvaluationOutcome.PASS


def test_bearing_angle_limits_enforced() -> None:
    dev = evaluate_splice_bearing(**_bearing_ok(end_face_deviation_deg=5.01))
    assert dev.outcome is EvaluationOutcome.FAIL
    assert dev.diagnostics[0].code == "BEARING_SPLICE_END_FACE_DEVIATION_EXCEEDED"
    mis = evaluate_splice_bearing(**_bearing_ok(axial_misalignment_deg=3.01))
    assert mis.outcome is EvaluationOutcome.FAIL
    assert mis.diagnostics[0].code == "BEARING_SPLICE_MISALIGNMENT_EXCEEDED"


@pytest.mark.parametrize(
    "override,code",
    [
        (dict(bars_compression_only=False), "BEARING_SPLICE_REQUIRES_COMPRESSION_ONLY"),
        (dict(ends_cut_perpendicular=False), "BEARING_SPLICE_ENDS_NOT_PERPENDICULAR"),
        (dict(bars_coaxial=False), "BEARING_SPLICE_NOT_COAXIAL"),
        (dict(member_has_confinement=False), "BEARING_SPLICE_NO_CONFINEMENT"),
    ],
)
def test_bearing_boolean_conditions_enforced(override: dict, code: str) -> None:
    step = evaluate_splice_bearing(**_bearing_ok(**override))
    assert step.outcome is EvaluationOutcome.FAIL
    assert step.diagnostics[0].code == code


def test_bearing_missing_blocked_and_malformed_invalid() -> None:
    assert evaluate_splice_bearing().outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert (
        evaluate_splice_bearing(**_bearing_ok(end_face_deviation_deg=-1.0)).outcome
        is EvaluationOutcome.INVALID_INPUT
    )
    assert (
        evaluate_splice_bearing(
            bars_compression_only="yes",  # type: ignore[arg-type]
            ends_cut_perpendicular=True,
            bars_coaxial=True,
            member_has_confinement=True,
            end_face_deviation_deg=4.0,
            axial_misalignment_deg=2.0,
        ).outcome
        is EvaluationOutcome.INVALID_INPUT
    )


def test_bearing_jurisdiction_blocked() -> None:
    step = evaluate_splice_bearing(**_bearing_ok(), jurisdiction_mode=MOST)
    assert step.outcome is EvaluationOutcome.JURISDICTION_BLOCKED
