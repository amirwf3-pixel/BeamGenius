"""Tests for Mabhas 9 (1399) Phase 2D verified beam detailing rules.

Covers:
- ``BG-DETAIL-TRANS-DIA-001`` (Clause 9-11-6-5-11, PDF p. 228): minimum
  transverse reinforcement diameter — db <= 32 -> 10 mm, db >= 36 -> 12 mm,
  bundled -> 12 mm, blocked non-interpolated interval 32 < db < 36
- ``BG-DETAIL-COMP-LAT-001`` (Clause 9-11-6-5-12, PDF p. 229): compression
  reinforcement lateral support spacing sc <= min(16*db, 48*dbt, b_min)
- Verified workflow aggregation, orchestrator dispatch, gatekeeper
  (jurisdiction isolation), anti-misleading hierarchy, and isolation of the
  engine from any reference-package imports
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from beamgenius.domain import (
    BeamGeometry,
    ConcreteMaterial,
    DiagnosticSeverity,
    EvaluationOutcome,
    JurisdictionMode,
    OverallComplianceStatus,
    RebarGroup,
    RebarMaterial,
    VerificationStatus,
)
from beamgenius.engine import (
    aggregate_compliance_report,
    evaluate_compression_reinforcement_lateral_support_spacing,
    evaluate_minimum_transverse_bar_diameter as legacy_blocked_stub,
    run_mabhas9_beam_check,
    run_mabhas9_beam_detailing_workflow,
)
from beamgenius.engine.detailing_mabhas9 import (
    BG_DETAIL_COMP_LAT_001_DB_MULTIPLIER,
    BG_DETAIL_COMP_LAT_001_DBT_MULTIPLIER,
    BG_DETAIL_TRANS_DIA_001_DB_MAX_FOR_10MM,
    BG_DETAIL_TRANS_DIA_001_DB_MIN_FOR_12MM,
    BG_DETAIL_TRANS_DIA_001_DBT_FOR_LARGE_OR_BUNDLED_DB,
    BG_DETAIL_TRANS_DIA_001_DBT_FOR_SMALL_DB,
    evaluate_minimum_transverse_bar_diameter,
)

# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------


def _geometry(
    bw_mm: float = 300.0,
    h_mm: float = 600.0,
    stirrup_diameter_mm: float = 10.0,
) -> BeamGeometry:
    return BeamGeometry(
        bw_mm=bw_mm,
        h_mm=h_mm,
        stirrup_diameter_mm=stirrup_diameter_mm,
    )


def _geometry_with_bars(
    max_bar_diameter_mm: float,
    stirrup_diameter_mm: float = 10.0,
) -> BeamGeometry:
    return BeamGeometry(
        bw_mm=300.0,
        h_mm=600.0,
        d_effective_mm=540.0,
        tension_rebar_groups=(
            RebarGroup(bar_diameter_mm=max_bar_diameter_mm / 2.0, bar_count=2),
            RebarGroup(bar_diameter_mm=max_bar_diameter_mm, bar_count=2),
        ),
        stirrup_diameter_mm=stirrup_diameter_mm,
    )


# ---------------------------------------------------------------------------
# BG-DETAIL-TRANS-DIA-001 — Minimum Transverse Bar Diameter (Clause 9-11-6-5-11)
# Mandatory test (1): db = 32 mm -> dbt >= 10 mm accepted
# ---------------------------------------------------------------------------


def test_trans_dia_db_32_requires_10mm_accepted() -> None:
    """Mandatory (1): db = 32 exactly -> minimum dbt = 10 mm; 10 mm passes."""
    geometry = _geometry(stirrup_diameter_mm=10.0)
    step = evaluate_minimum_transverse_bar_diameter(
        geometry,
        max_longitudinal_bar_diameter_mm=32.0,
        transverse_bar_diameter_mm=10.0,
    )
    assert step.rule_id == "BG-DETAIL-TRANS-DIA-001"
    assert step.outcome == EvaluationOutcome.PASS
    assert step.final_result == pytest.approx(
        BG_DETAIL_TRANS_DIA_001_DBT_FOR_SMALL_DB
    )
    assert step.intermediate_values["db_governing_mm"] == pytest.approx(32.0)
    assert step.intermediate_values[
        "required_transverse_diameter_mm"
    ] == pytest.approx(10.0)
    assert step.verification_status == VerificationStatus.VERIFIED


# ---------------------------------------------------------------------------
# Mandatory test (2): db = 36 mm -> dbt >= 12 mm required
# ---------------------------------------------------------------------------


def test_trans_dia_db_36_requires_12mm() -> None:
    """Mandatory (2): db = 36 exactly -> minimum dbt = 12 mm required."""
    geometry = _geometry(stirrup_diameter_mm=10.0)
    # 10 mm provided -> FAIL against the 12 mm requirement.
    step_fail = evaluate_minimum_transverse_bar_diameter(
        geometry,
        max_longitudinal_bar_diameter_mm=36.0,
        transverse_bar_diameter_mm=10.0,
    )
    assert step_fail.outcome == EvaluationOutcome.FAIL
    assert step_fail.final_result == pytest.approx(
        BG_DETAIL_TRANS_DIA_001_DBT_FOR_LARGE_OR_BUNDLED_DB
    )
    assert any(
        d.code == "INSUFFICIENT_TRANSVERSE_BAR_DIAMETER"
        for d in step_fail.diagnostics
    )
    # 12 mm provided -> PASS.
    step_pass = evaluate_minimum_transverse_bar_diameter(
        geometry,
        max_longitudinal_bar_diameter_mm=36.0,
        transverse_bar_diameter_mm=12.0,
    )
    assert step_pass.outcome == EvaluationOutcome.PASS
    # No dbt resolvable -> COMPUTED with the 12 mm requirement.
    no_dbt = BeamGeometry(bw_mm=300.0, h_mm=600.0)
    step_computed = evaluate_minimum_transverse_bar_diameter(
        no_dbt,
        max_longitudinal_bar_diameter_mm=40.0,
    )
    assert step_computed.outcome == EvaluationOutcome.COMPUTED
    assert step_computed.final_result == pytest.approx(12.0)


# ---------------------------------------------------------------------------
# Mandatory test (3): bundled longitudinal bars -> dbt >= 12 mm required
# ---------------------------------------------------------------------------


def test_trans_dia_bundled_bars_require_12mm() -> None:
    """Mandatory (3): bundled bars (any db) -> minimum dbt = 12 mm."""
    geometry = _geometry(stirrup_diameter_mm=10.0)
    step_fail = evaluate_minimum_transverse_bar_diameter(
        geometry,
        max_longitudinal_bar_diameter_mm=25.0,
        is_bundled=True,
        transverse_bar_diameter_mm=10.0,
    )
    assert step_fail.outcome == EvaluationOutcome.FAIL
    assert step_fail.final_result == pytest.approx(12.0)

    step_pass = evaluate_minimum_transverse_bar_diameter(
        geometry,
        max_longitudinal_bar_diameter_mm=25.0,
        is_bundled=True,
        transverse_bar_diameter_mm=12.0,
    )
    assert step_pass.outcome == EvaluationOutcome.PASS


# ---------------------------------------------------------------------------
# Mandatory test (4): non-bundled db = 34 mm -> BLOCKED (no interpolation)
# ---------------------------------------------------------------------------


def test_trans_dia_db_34_unsupported_interval_blocked() -> None:
    """Mandatory (4): 32 < db < 36 -> UNVERIFIED_RULE_BLOCKED, never PASS."""
    geometry = _geometry(stirrup_diameter_mm=12.0)
    step = evaluate_minimum_transverse_bar_diameter(
        geometry,
        max_longitudinal_bar_diameter_mm=34.0,
        transverse_bar_diameter_mm=12.0,
    )
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.final_result is None
    assert len(step.diagnostics) == 1
    diag = step.diagnostics[0]
    assert diag.code == "UNSUPPORTED_LONGITUDINAL_DIAMETER_INTERVAL"
    assert diag.severity == DiagnosticSeverity.BLOCK
    assert diag.required_verification is not None
    assert "UNSUPPORTED_CONFIGURATION" in diag.message

    # Interval bounds are exact: 32 and 36 are NOT blocked.
    assert evaluate_minimum_transverse_bar_diameter(
        geometry, max_longitudinal_bar_diameter_mm=32.0
    ).outcome != EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert evaluate_minimum_transverse_bar_diameter(
        geometry, max_longitudinal_bar_diameter_mm=36.0
    ).outcome != EvaluationOutcome.UNVERIFIED_RULE_BLOCKED

    # Bundled bars in the interval are NOT blocked (they use the 12 mm rule).
    bundled = evaluate_minimum_transverse_bar_diameter(
        geometry, max_longitudinal_bar_diameter_mm=34.0, is_bundled=True
    )
    assert bundled.outcome == EvaluationOutcome.PASS
    assert bundled.final_result == pytest.approx(12.0)


# ---------------------------------------------------------------------------
# Mandatory test (5): invalid (non-finite / non-positive) diameter -> INVALID_INPUT
# ---------------------------------------------------------------------------


def test_trans_dia_invalid_diameters_invalid_input() -> None:
    """Mandatory (5): zero/negative/NaN/inf diameters -> INVALID_INPUT."""
    geometry = _geometry()
    for bad_db in (0.0, -10.0, float("nan"), float("inf")):
        step = evaluate_minimum_transverse_bar_diameter(
            geometry, max_longitudinal_bar_diameter_mm=bad_db
        )
        assert step.outcome == EvaluationOutcome.INVALID_INPUT
        assert any(
            d.code == "INVALID_BAR_DIAMETER_MAX_LONGITUDINAL_BAR_DIAMETER_MM"
            for d in step.diagnostics
        )

    for bad_dbt in (0.0, -5.0, float("nan")):
        step = evaluate_minimum_transverse_bar_diameter(
            geometry,
            max_longitudinal_bar_diameter_mm=25.0,
            transverse_bar_diameter_mm=bad_dbt,
        )
        assert step.outcome == EvaluationOutcome.INVALID_INPUT
        assert any(
            d.code == "INVALID_BAR_DIAMETER_TRANSVERSE_BAR_DIAMETER_MM"
            for d in step.diagnostics
        )

    # Missing db entirely (no kwarg, no rebar groups) -> INVALID_INPUT.
    no_bars = BeamGeometry(bw_mm=300.0, h_mm=600.0, stirrup_diameter_mm=10.0)
    step_missing = evaluate_minimum_transverse_bar_diameter(no_bars)
    assert step_missing.outcome == EvaluationOutcome.INVALID_INPUT
    assert any(
        d.code == "MISSING_LONGITUDINAL_BAR_DIAMETER"
        for d in step_missing.diagnostics
    )


def test_trans_dia_db_resolved_from_tension_rebar_groups() -> None:
    """db falls back to max bar diameter of geometry.tension_rebar_groups."""
    geometry = _geometry_with_bars(max_bar_diameter_mm=32.0)
    step = evaluate_minimum_transverse_bar_diameter(geometry)
    assert step.outcome == EvaluationOutcome.PASS
    assert step.intermediate_values["db_governing_mm"] == pytest.approx(32.0)


# ---------------------------------------------------------------------------
# BG-DETAIL-COMP-LAT-001 — Compression Lateral Support Spacing (Clause 9-11-6-5-12)
# Mandatory tests (6) & (7): exact limit PASS, limit + 1 mm FAIL
# ---------------------------------------------------------------------------


def test_comp_lat_spacing_exactly_at_limit_passes() -> None:
    """Mandatory (6): sc == sc_max -> PASS (b_min governs at 300 mm)."""
    geometry = _geometry(bw_mm=300.0, h_mm=600.0, stirrup_diameter_mm=10.0)
    # limits: 16*25 = 400, 48*10 = 480, b_min = 300 -> sc_max = 300
    step = evaluate_compression_reinforcement_lateral_support_spacing(
        geometry,
        has_compression_reinforcement=True,
        min_compression_bar_diameter_mm=25.0,
        compression_lateral_support_spacing_mm=300.0,
    )
    assert step.rule_id == "BG-DETAIL-COMP-LAT-001"
    assert step.outcome == EvaluationOutcome.PASS
    assert step.final_result == pytest.approx(300.0)
    assert step.intermediate_values["governing_limit_code"] == pytest.approx(
        3.0
    )
    assert step.verification_status == VerificationStatus.VERIFIED


def test_comp_lat_spacing_limit_plus_one_mm_fails() -> None:
    """Mandatory (7): sc == sc_max + 1 mm -> FAIL."""
    geometry = _geometry(bw_mm=300.0, h_mm=600.0, stirrup_diameter_mm=10.0)
    step = evaluate_compression_reinforcement_lateral_support_spacing(
        geometry,
        has_compression_reinforcement=True,
        min_compression_bar_diameter_mm=25.0,
        compression_lateral_support_spacing_mm=301.0,
    )
    assert step.outcome == EvaluationOutcome.FAIL
    assert any(
        d.code == "COMPRESSION_LATERAL_SUPPORT_SPACING_EXCEEDED"
        for d in step.diagnostics
    )
    assert any(
        d.field_name == "compression_lateral_support_spacing_mm"
        for d in step.diagnostics
    )


# ---------------------------------------------------------------------------
# Mandatory test (8): controlling limit switches among 16*db / 48*dbt / b_min
# ---------------------------------------------------------------------------


def test_comp_lat_governing_limit_switches() -> None:
    """Mandatory (8): min(16*db, 48*dbt, b_min) governing branch switches."""
    geometry = _geometry(bw_mm=500.0, h_mm=700.0, stirrup_diameter_mm=8.0)
    # limits: 16*20 = 320, 48*8 = 384, b_min = 500 -> 16*db governs.
    step_db = evaluate_compression_reinforcement_lateral_support_spacing(
        geometry,
        has_compression_reinforcement=True,
        min_compression_bar_diameter_mm=20.0,
    )
    assert step_db.outcome == EvaluationOutcome.COMPUTED
    assert step_db.final_result == pytest.approx(320.0)
    assert step_db.intermediate_values["governing_limit_code"] == pytest.approx(
        1.0
    )
    assert step_db.intermediate_values["limit_16db_mm"] == pytest.approx(
        BG_DETAIL_COMP_LAT_001_DB_MULTIPLIER * 20.0
    )

    # limits: 16*40 = 640, 48*8 = 384, b_min = 500 -> 48*dbt governs.
    step_dbt = evaluate_compression_reinforcement_lateral_support_spacing(
        geometry,
        has_compression_reinforcement=True,
        min_compression_bar_diameter_mm=40.0,
    )
    assert step_dbt.final_result == pytest.approx(384.0)
    assert step_dbt.intermediate_values[
        "governing_limit_code"
    ] == pytest.approx(2.0)
    assert step_dbt.intermediate_values["limit_48dbt_mm"] == pytest.approx(
        BG_DETAIL_COMP_LAT_001_DBT_MULTIPLIER * 8.0
    )

    # limits: 16*40 = 640, 48*8 = 384, b_min = 300 -> b_min governs.
    narrow = _geometry(bw_mm=300.0, h_mm=700.0, stirrup_diameter_mm=8.0)
    step_bmin = evaluate_compression_reinforcement_lateral_support_spacing(
        narrow,
        has_compression_reinforcement=True,
        min_compression_bar_diameter_mm=40.0,
    )
    assert step_bmin.final_result == pytest.approx(300.0)
    assert step_bmin.intermediate_values[
        "governing_limit_code"
    ] == pytest.approx(3.0)
    assert step_bmin.intermediate_values["b_min_mm"] == pytest.approx(300.0)


# ---------------------------------------------------------------------------
# Mandatory test (9): missing compression reinforcement / inputs -> invalid/block
# ---------------------------------------------------------------------------


def test_comp_lat_missing_compression_steel_invalid_input() -> None:
    """Mandatory (9): no compression reinforcement -> INVALID_INPUT."""
    geometry = _geometry()
    step = evaluate_compression_reinforcement_lateral_support_spacing(
        geometry,
        has_compression_reinforcement=False,
    )
    assert step.outcome == EvaluationOutcome.INVALID_INPUT
    assert any(
        d.code == "MISSING_COMPRESSION_REINFORCEMENT"
        for d in step.diagnostics
    )

    # Compression steel exists but its smallest bar diameter is missing.
    step_no_db = evaluate_compression_reinforcement_lateral_support_spacing(
        geometry,
        has_compression_reinforcement=True,
    )
    assert step_no_db.outcome == EvaluationOutcome.INVALID_INPUT
    assert any(
        d.code == "MISSING_COMPRESSION_BAR_DIAMETER"
        for d in step_no_db.diagnostics
    )

    # No transverse diameter resolvable at all.
    no_stirrups = BeamGeometry(bw_mm=300.0, h_mm=600.0)
    step_no_dbt = evaluate_compression_reinforcement_lateral_support_spacing(
        no_stirrups,
        has_compression_reinforcement=True,
        min_compression_bar_diameter_mm=25.0,
    )
    assert step_no_dbt.outcome == EvaluationOutcome.INVALID_INPUT
    assert any(
        d.code == "MISSING_TRANSVERSE_BAR_DIAMETER"
        for d in step_no_dbt.diagnostics
    )


# ---------------------------------------------------------------------------
# Mandatory test (10): zero dimensions -> INVALID_INPUT
# ---------------------------------------------------------------------------


def test_comp_lat_zero_dimensions_invalid_input() -> None:
    """Mandatory (10): zero / non-positive inputs -> INVALID_INPUT."""
    geometry = _geometry()
    # Zero provided spacing.
    step = evaluate_compression_reinforcement_lateral_support_spacing(
        geometry,
        has_compression_reinforcement=True,
        min_compression_bar_diameter_mm=25.0,
        compression_lateral_support_spacing_mm=0.0,
    )
    assert step.outcome == EvaluationOutcome.INVALID_INPUT
    assert any(
        d.code == "INVALID_COMPRESSION_LATERAL_SPACING"
        for d in step.diagnostics
    )

    # Zero compression bar diameter.
    step_db = evaluate_compression_reinforcement_lateral_support_spacing(
        geometry,
        has_compression_reinforcement=True,
        min_compression_bar_diameter_mm=0.0,
    )
    assert step_db.outcome == EvaluationOutcome.INVALID_INPUT
    assert any(
        d.code == "INVALID_BAR_DIAMETER_MIN_COMPRESSION_BAR_DIAMETER_MM"
        for d in step_db.diagnostics
    )

    # Zero transverse bar diameter.
    step_dbt = evaluate_compression_reinforcement_lateral_support_spacing(
        _geometry(stirrup_diameter_mm=0.0),
        has_compression_reinforcement=True,
        min_compression_bar_diameter_mm=25.0,
    )
    assert step_dbt.outcome == EvaluationOutcome.INVALID_INPUT
    assert any(
        d.code == "INVALID_BAR_DIAMETER_TRANSVERSE_BAR_DIAMETER_MM"
        for d in step_dbt.diagnostics
    )

    # Non-finite spacing.
    step_inf = evaluate_compression_reinforcement_lateral_support_spacing(
        geometry,
        has_compression_reinforcement=True,
        min_compression_bar_diameter_mm=25.0,
        compression_lateral_support_spacing_mm=float("inf"),
    )
    assert step_inf.outcome == EvaluationOutcome.INVALID_INPUT


# ---------------------------------------------------------------------------
# Gatekeeper & jurisdiction isolation
# ---------------------------------------------------------------------------


def test_detailing_rules_jurisdiction_isolation() -> None:
    """Verified detailing rules are JURISDICTION_BLOCKED outside Mabhas 9."""
    geometry = _geometry()
    step_trans = evaluate_minimum_transverse_bar_diameter(
        geometry,
        max_longitudinal_bar_diameter_mm=25.0,
        jurisdiction_mode=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    )
    assert step_trans.outcome == EvaluationOutcome.JURISDICTION_BLOCKED

    step_comp = evaluate_compression_reinforcement_lateral_support_spacing(
        geometry,
        has_compression_reinforcement=True,
        min_compression_bar_diameter_mm=25.0,
        jurisdiction_mode=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    )
    assert step_comp.outcome == EvaluationOutcome.JURISDICTION_BLOCKED


# ---------------------------------------------------------------------------
# Verified detailing workflow & aggregation
# ---------------------------------------------------------------------------


def test_detailing_workflow_and_aggregation_never_promotes_blocked() -> None:
    """Workflow returns ordered steps; aggregation keeps BLOCKED dominant."""
    geometry = _geometry_with_bars(max_bar_diameter_mm=25.0)  # type falls back
    steps = run_mabhas9_beam_detailing_workflow(
        geometry,
        has_compression_reinforcement=True,
        min_compression_bar_diameter_mm=25.0,
        compression_lateral_support_spacing_mm=200.0,
    )
    assert [s.rule_id for s in steps] == [
        "BG-DETAIL-TRANS-DIA-001",
        "BG-DETAIL-COMP-LAT-001",
    ]
    assert all(s.outcome == EvaluationOutcome.PASS for s in steps)
    report = aggregate_compliance_report(steps)
    assert report.overall_status == OverallComplianceStatus.PASS
    assert report.is_compliant

    # Without compression reinforcement, only the transverse rule runs.
    steps_single = run_mabhas9_beam_detailing_workflow(
        geometry, max_longitudinal_bar_diameter_mm=25.0
    )
    assert len(steps_single) == 1

    # A blocked branch (32 < db < 36) dominates the aggregate -> never PASS.
    blocked_steps = run_mabhas9_beam_detailing_workflow(
        geometry,
        max_longitudinal_bar_diameter_mm=34.0,
        has_compression_reinforcement=True,
        min_compression_bar_diameter_mm=25.0,
        compression_lateral_support_spacing_mm=200.0,
    )
    assert blocked_steps[0].outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    report_blocked = aggregate_compliance_report(blocked_steps)
    assert report_blocked.overall_status == OverallComplianceStatus.BLOCKED
    assert not report_blocked.is_compliant


def test_detailing_rules_dispatch_via_run_mabhas9_beam_check() -> None:
    """Orchestrator dispatches verified detailing rules and legacy stub stays blocked."""
    geometry = _geometry_with_bars(max_bar_diameter_mm=25.0)
    concrete = ConcreteMaterial(fc_prime_mpa=30.0)
    rebar = RebarMaterial(fy_mpa=420.0)
    report = run_mabhas9_beam_check(
        geometry,
        concrete,
        rebar,
        max_longitudinal_bar_diameter_mm=25.0,
        is_bundled=False,
        has_compression_reinforcement=True,
        min_compression_bar_diameter_mm=25.0,
        compression_lateral_support_spacing_mm=200.0,
        requested_rule_ids=[
            "BG-DETAIL-TRANS-DIA-001",
            "BG-DETAIL-COMP-LAT-001",
        ],
    )
    assert report.overall_status == OverallComplianceStatus.PASS
    assert report.outcomes_by_rule["BG-DETAIL-TRANS-DIA-001"] == (
        EvaluationOutcome.PASS
    )
    assert report.outcomes_by_rule["BG-DETAIL-COMP-LAT-001"] == (
        EvaluationOutcome.PASS
    )

    # The legacy blocked stub for the un-promoted PENDING sentinel is untouched.
    legacy = legacy_blocked_stub(geometry)
    assert legacy.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED


# ---------------------------------------------------------------------------
# Engine isolation: no imports from the isolated reference package
# ---------------------------------------------------------------------------


def test_detailing_engine_module_has_no_reference_imports() -> None:
    """The verified engine must stay isolated from the Mostofinejad reference."""
    engine_dir = (
        Path(__file__).resolve().parents[1]
        / "src"
        / "beamgenius"
        / "engine"
    )
    module_paths = sorted(engine_dir.glob("*.py"))
    assert module_paths, "engine package sources not found"
    for module_path in module_paths:
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert "reference" not in alias.name.split("."), (
                        f"{module_path.name} imports reference package"
                    )
            elif isinstance(node, ast.ImportFrom):
                assert node.module is not None
                assert "reference" not in node.module.split("."), (
                    f"{module_path.name} imports reference package"
                )
