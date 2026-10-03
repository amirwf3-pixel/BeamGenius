"""Tests for Mabhas 9 (1399) Phase 2E Stage B verified beam detailing rules.

Covers the three rules promoted from VERIFIED_SOURCE_ONLY (visually verified
2026-10-03 from source-page captures):

- ``BG-DETAIL-SPACING-001`` (Clause 9-21-2-1-1, PDF p. 441 / Printed p. 420):
  clear spacing of parallel bars in one horizontal layer
  ``s_clear >= max(25 mm, db_max, (4/3) * d_agg)``; shotcrete NOT_APPLICABLE
  (9-21-2-1-4); bundled bars BLOCKED (9-21-5-6 pending).
- ``BG-DETAIL-LAYER-SPACING-001`` (Clause 9-21-2-1-2, same source page):
  upper-layer bars directly above lower-layer bars (tracked by a REQUIRED
  typed alignment input) and clear inter-layer spacing >= 25 mm.
- ``BG-DETAIL-COVER-001`` (Clauses 9-4-9-4, 9-4-9-5-1..3 + Table 9-4-6,
  PDF pp. 92-93 / Printed pp. 71-72): minimum concrete cover for beams:
  40 mm not exposed / 50 mm (db 18-58) or 40 mm (db <= 16) exposed to air,
  weather or non-permanent earth contact / 75 mm permanent earth contact;
  corrosive exposure BLOCKED (Appendix 9-پ1); bundled groups BLOCKED
  (Clause 9-4-9-5-2 -> 9-21-5-6); uncovered diameter classes never
  interpolated.

Also covers workflow aggregation, orchestrator dispatch, gatekeeper
jurisdiction isolation, and preservation of the legacy BLOCKED sentinels.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List

from beamgenius.domain import (
    BeamGeometry,
    ConcreteCoverExposureClass,
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
    evaluate_concrete_cover as legacy_blocked_cover_stub,
    evaluate_layer_clear_spacing,
    evaluate_layer_spacing as legacy_blocked_layer_stub,
    evaluate_longitudinal_bar_clear_spacing as legacy_blocked_spacing_stub,
    evaluate_minimum_concrete_cover,
    run_mabhas9_beam_check,
    run_mabhas9_beam_detailing_workflow,
)
from beamgenius.engine.detailing_mabhas9 import (
    BG_DETAIL_COVER_001_BEAM_NOT_EXPOSED_MM,
    BG_DETAIL_COVER_001_PERMANENT_EARTH_MM,
    BG_DETAIL_COVER_001_WEATHER_DB_18_TO_58_MM,
    BG_DETAIL_COVER_001_WEATHER_DB_LE_16_MM,
    BG_DETAIL_LAYER_SPACING_001_MIN_CLEAR_MM,
    BG_DETAIL_SPACING_001_AGGREGATE_FACTOR,
    BG_DETAIL_SPACING_001_MIN_CLEAR_MM,
    evaluate_longitudinal_bar_clear_spacing,
)
from beamgenius.registry.catalog import (
    RULE_BG_DETAIL_COVER_001,
    RULE_BG_DETAIL_COVER_BLOCKED,
    RULE_BG_DETAIL_LAYER_SPACING_001,
    RULE_BG_DETAIL_LAYER_SPACING_BLOCKED,
    RULE_BG_DETAIL_SPACING_001,
    RULE_BG_DETAIL_SPACING_BLOCKED,
)
from beamgenius.registry.gatekeeper import evaluate_rule_gate

# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------


def _geometry(
    *,
    clear_cover_mm: float | None = None,
    layer_clear_spacing_mm: float | None = None,
    tension_rebar_groups: tuple[RebarGroup, ...] = (),
) -> BeamGeometry:
    return BeamGeometry(
        bw_mm=300.0,
        h_mm=600.0,
        clear_cover_mm=clear_cover_mm,
        layer_clear_spacing_mm=layer_clear_spacing_mm,
        tension_rebar_groups=tension_rebar_groups,
    )


# ---------------------------------------------------------------------------
# BG-DETAIL-SPACING-001 — Clause 9-21-2-1-1
# ---------------------------------------------------------------------------


def test_spacing_rule_registry_metadata_verified() -> None:
    """Rule promoted: VERIFIED, execution_allowed=True, verified pages recorded."""
    rule = RULE_BG_DETAIL_SPACING_001
    assert rule.rule_id == "BG-DETAIL-SPACING-001"
    assert rule.status == VerificationStatus.VERIFIED
    assert rule.execution_allowed is True
    assert rule.pdf_page == 441
    assert rule.printed_page == 420
    assert "9-21-2-1-1" in rule.clause_or_equation


def test_spacing_pass_when_aggregate_term_governs() -> None:
    """d_agg governs: max(25, 25, 4/3*20=26.667) = 26.667; provided 27 -> PASS."""
    geometry = _geometry()
    step = evaluate_longitudinal_bar_clear_spacing(
        geometry,
        max_bar_diameter_mm=25.0,
        aggregate_size_mm=20.0,
        provided_clear_spacing_mm=27.0,
    )
    assert step.outcome == EvaluationOutcome.PASS
    assert step.final_result is not None
    assert abs(step.final_result - (4.0 / 3.0) * 20.0) < 1e-9
    assert step.intermediate_values["required_clear_spacing_mm"] > 25.0


def test_spacing_pass_when_db_max_governs() -> None:
    """db governs: max(25, 32, 26.667) = 32; provided 32 -> PASS, 31 -> FAIL."""
    geometry = _geometry()
    passing = evaluate_longitudinal_bar_clear_spacing(
        geometry,
        max_bar_diameter_mm=32.0,
        aggregate_size_mm=20.0,
        provided_clear_spacing_mm=32.0,
    )
    assert passing.outcome == EvaluationOutcome.PASS
    failing = evaluate_longitudinal_bar_clear_spacing(
        geometry,
        max_bar_diameter_mm=32.0,
        aggregate_size_mm=20.0,
        provided_clear_spacing_mm=31.0,
    )
    assert failing.outcome == EvaluationOutcome.FAIL
    assert failing.diagnostics[0].code == "INSUFFICIENT_BAR_CLEAR_SPACING"
    assert failing.diagnostics[0].severity == DiagnosticSeverity.ERROR


def test_spacing_absolute_25mm_floor_governs_small_bars() -> None:
    """25 mm floor governs: max(25, 16, 16) = 25; provided 25 -> PASS."""
    geometry = _geometry()
    step = evaluate_longitudinal_bar_clear_spacing(
        geometry,
        max_bar_diameter_mm=16.0,
        aggregate_size_mm=12.0,
        provided_clear_spacing_mm=25.0,
    )
    assert step.outcome == EvaluationOutcome.PASS
    assert step.final_result == BG_DETAIL_SPACING_001_MIN_CLEAR_MM
    assert step.intermediate_values["limit_absolute_25_mm"] == 25.0


def test_spacing_fail_below_25mm_floor() -> None:
    """provided 24.9 mm < 25 mm floor -> FAIL."""
    geometry = _geometry()
    step = evaluate_longitudinal_bar_clear_spacing(
        geometry,
        max_bar_diameter_mm=16.0,
        aggregate_size_mm=12.0,
        provided_clear_spacing_mm=24.9,
    )
    assert step.outcome == EvaluationOutcome.FAIL


def test_spacing_computed_without_provided_value() -> None:
    """No provided clear spacing -> COMPUTED with required value."""
    geometry = _geometry()
    step = evaluate_longitudinal_bar_clear_spacing(
        geometry,
        max_bar_diameter_mm=25.0,
        aggregate_size_mm=20.0,
    )
    assert step.outcome == EvaluationOutcome.COMPUTED
    assert step.final_result is not None
    assert "required" in step.message.lower()


def test_spacing_db_resolved_from_tension_groups() -> None:
    """db_max falls back to the largest tension-group bar diameter."""
    geometry = _geometry(
        tension_rebar_groups=(
            RebarGroup(bar_diameter_mm=25.0, bar_count=2),
            RebarGroup(bar_diameter_mm=32.0, bar_count=1),
        )
    )
    step = evaluate_longitudinal_bar_clear_spacing(
        geometry,
        aggregate_size_mm=20.0,
        provided_clear_spacing_mm=31.0,
    )
    assert step.outcome == EvaluationOutcome.FAIL  # needs >= 32
    assert step.intermediate_values["db_governing_mm"] == 32.0


def test_spacing_missing_aggregate_size_invalid_never_defaulted() -> None:
    """Missing d_agg -> INVALID_INPUT (clause item (پ) is never dropped)."""
    geometry = _geometry()
    step = evaluate_longitudinal_bar_clear_spacing(
        geometry,
        max_bar_diameter_mm=25.0,
        provided_clear_spacing_mm=80.0,  # would pass if d_agg were dropped
    )
    assert step.outcome == EvaluationOutcome.INVALID_INPUT
    assert step.diagnostics[0].code == "MISSING_AGGREGATE_SIZE"
    assert step.final_result is None


def test_spacing_missing_db_invalid() -> None:
    """Missing db (no kwarg, no groups) -> INVALID_INPUT."""
    geometry = _geometry()
    step = evaluate_longitudinal_bar_clear_spacing(
        geometry,
        aggregate_size_mm=20.0,
    )
    assert step.outcome == EvaluationOutcome.INVALID_INPUT
    assert step.diagnostics[0].code == "MISSING_GOVERNING_BAR_DIAMETER"


def test_spacing_invalid_numeric_inputs() -> None:
    """Non-positive / non-finite inputs are deterministic INVALID_INPUT."""
    geometry = _geometry()
    invalid_cases: List[Dict[str, Any]] = [
        {"max_bar_diameter_mm": 0.0, "aggregate_size_mm": 20.0},
        {"max_bar_diameter_mm": math.nan, "aggregate_size_mm": 20.0},
        {"max_bar_diameter_mm": 25.0, "aggregate_size_mm": -5.0},
        {"max_bar_diameter_mm": 25.0, "aggregate_size_mm": math.inf},
        {
            "max_bar_diameter_mm": 25.0,
            "aggregate_size_mm": 20.0,
            "provided_clear_spacing_mm": 0.0,
        },
    ]
    for kwargs in invalid_cases:
        step = evaluate_longitudinal_bar_clear_spacing(geometry, **kwargs)
        assert step.outcome == EvaluationOutcome.INVALID_INPUT


def test_spacing_bundled_bars_blocked_pending_9_21_5_6() -> None:
    """is_bundled=True -> UNVERIFIED_RULE_BLOCKED; 9-21-5-6 not executed."""
    geometry = _geometry()
    step = evaluate_longitudinal_bar_clear_spacing(
        geometry,
        max_bar_diameter_mm=25.0,
        aggregate_size_mm=20.0,
        provided_clear_spacing_mm=100.0,
        is_bundled=True,
    )
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "UNVERIFIED_BUNDLED_BAR_SPACING"
    assert step.diagnostics[0].severity == DiagnosticSeverity.BLOCK
    req_spacing = step.diagnostics[0].required_verification
    assert req_spacing is not None and "9-21-5-6" in req_spacing
    assert step.final_result is None


def test_spacing_shotcrete_not_applicable() -> None:
    """Clause 9-21-2-1-4: shotcrete is out of scope -> NOT_APPLICABLE."""
    geometry = _geometry()
    step = evaluate_longitudinal_bar_clear_spacing(
        geometry,
        max_bar_diameter_mm=25.0,
        aggregate_size_mm=20.0,
        is_shotcrete=True,
    )
    assert step.outcome == EvaluationOutcome.NOT_APPLICABLE


def test_spacing_jurisdiction_blocked_in_reference_mode() -> None:
    """Mabhas rule is JURISDICTION_BLOCKED under MOSTOFINEJAD_METHODOLOGY_ONLY."""
    geometry = _geometry()
    step = evaluate_longitudinal_bar_clear_spacing(
        geometry,
        max_bar_diameter_mm=25.0,
        aggregate_size_mm=20.0,
        jurisdiction_mode=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    )
    assert step.outcome == EvaluationOutcome.JURISDICTION_BLOCKED


def test_spacing_legacy_blocked_sentinel_untouched() -> None:
    """The BG-DETAIL-SPACING-BLOCKED sentinel and its stub remain blocked."""
    rule = RULE_BG_DETAIL_SPACING_BLOCKED
    assert rule.execution_allowed is False
    assert rule.status == VerificationStatus.VERIFY_PENDING
    geometry = _geometry()
    step = legacy_blocked_spacing_stub(geometry)
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED


# ---------------------------------------------------------------------------
# BG-DETAIL-LAYER-SPACING-001 — Clause 9-21-2-1-2
# ---------------------------------------------------------------------------


def test_layer_rule_registry_metadata_verified() -> None:
    rule = RULE_BG_DETAIL_LAYER_SPACING_001
    assert rule.rule_id == "BG-DETAIL-LAYER-SPACING-001"
    assert rule.status == VerificationStatus.VERIFIED
    assert rule.execution_allowed is True
    assert rule.pdf_page == 441
    assert rule.printed_page == 420
    assert "9-21-2-1-2" in rule.clause_or_equation


def test_layer_pass_aligned_with_25mm_spacing() -> None:
    """Aligned layers + 25 mm clear (from geometry) -> PASS."""
    geometry = _geometry(layer_clear_spacing_mm=25.0)
    step = evaluate_layer_clear_spacing(
        geometry,
        layer_count=2,
        layers_directly_aligned=True,
    )
    assert step.outcome == EvaluationOutcome.PASS
    assert step.final_result == BG_DETAIL_LAYER_SPACING_001_MIN_CLEAR_MM


def test_layer_fail_below_25mm() -> None:
    """Aligned layers + 20 mm clear -> FAIL (independent of db/aggregate)."""
    geometry = _geometry(layer_clear_spacing_mm=20.0)
    step = evaluate_layer_clear_spacing(
        geometry,
        layer_count=2,
        layers_directly_aligned=True,
    )
    assert step.outcome == EvaluationOutcome.FAIL
    assert step.diagnostics[0].code == "INSUFFICIENT_LAYER_CLEAR_SPACING"


def test_layer_fail_when_not_directly_aligned() -> None:
    """Alignment violation -> FAIL even with generous spacing."""
    geometry = _geometry(layer_clear_spacing_mm=100.0)
    step = evaluate_layer_clear_spacing(
        geometry,
        layer_count=2,
        layers_directly_aligned=False,
    )
    assert step.outcome == EvaluationOutcome.FAIL
    assert step.diagnostics[0].code == "LAYERS_NOT_DIRECTLY_ALIGNED"


def test_layer_computed_without_provided_spacing() -> None:
    """Aligned multi-layer, no provided spacing -> COMPUTED (25 mm)."""
    geometry = _geometry()
    step = evaluate_layer_clear_spacing(
        geometry,
        layer_count=2,
        layers_directly_aligned=True,
    )
    assert step.outcome == EvaluationOutcome.COMPUTED
    assert step.final_result == 25.0


def test_layer_alignment_never_silently_assumed() -> None:
    """Missing typed alignment input (multi-layer) -> INVALID_INPUT."""
    geometry = _geometry(layer_clear_spacing_mm=30.0)
    step = evaluate_layer_clear_spacing(
        geometry,
        layer_count=2,
    )
    assert step.outcome == EvaluationOutcome.INVALID_INPUT
    assert step.diagnostics[0].code == "MISSING_LAYER_ALIGNMENT"
    assert step.final_result is None


def test_layer_single_layer_not_applicable() -> None:
    """layer_count == 1 -> NOT_APPLICABLE (no inter-layer requirement)."""
    geometry = _geometry()
    step = evaluate_layer_clear_spacing(
        geometry,
        layer_count=1,
    )
    assert step.outcome == EvaluationOutcome.NOT_APPLICABLE


def test_layer_missing_layer_count_invalid() -> None:
    """No layer_count and no groups -> INVALID_INPUT MISSING_LAYER_COUNT."""
    geometry = _geometry()
    step = evaluate_layer_clear_spacing(geometry)
    assert step.outcome == EvaluationOutcome.INVALID_INPUT
    assert step.diagnostics[0].code == "MISSING_LAYER_COUNT"


def test_layer_count_derived_from_rebar_groups() -> None:
    """Layer count derived from max layer_index of tension rebar groups."""
    geometry = _geometry(
        layer_clear_spacing_mm=25.0,
        tension_rebar_groups=(
            RebarGroup(bar_diameter_mm=25.0, bar_count=3, layer_index=1),
            RebarGroup(bar_diameter_mm=25.0, bar_count=2, layer_index=2),
        ),
    )
    step = evaluate_layer_clear_spacing(
        geometry,
        layers_directly_aligned=True,
    )
    assert step.outcome == EvaluationOutcome.PASS
    assert step.intermediate_values["layer_count"] == 2.0


def test_layer_invalid_layer_count_values() -> None:
    """layer_count must be an integer >= 1 (bool rejected deterministically)."""
    geometry = _geometry()
    for bad in (0, -1, 2.5, True):
        step = evaluate_layer_clear_spacing(
            geometry,
            layer_count=bad,  # type: ignore[arg-type]
        )
        assert step.outcome == EvaluationOutcome.INVALID_INPUT
        assert step.diagnostics[0].code == "INVALID_LAYER_COUNT"


def test_layer_bundled_bars_blocked_pending_9_21_5_6() -> None:
    geometry = _geometry(layer_clear_spacing_mm=100.0)
    step = evaluate_layer_clear_spacing(
        geometry,
        layer_count=2,
        layers_directly_aligned=True,
        is_bundled=True,
    )
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    req_layer = step.diagnostics[0].required_verification
    assert req_layer is not None and "9-21-5-6" in req_layer


def test_layer_jurisdiction_blocked_in_reference_mode() -> None:
    geometry = _geometry()
    step = evaluate_layer_clear_spacing(
        geometry,
        layer_count=2,
        layers_directly_aligned=True,
        jurisdiction_mode=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    )
    assert step.outcome == EvaluationOutcome.JURISDICTION_BLOCKED


def test_layer_legacy_blocked_sentinel_untouched() -> None:
    rule = RULE_BG_DETAIL_LAYER_SPACING_BLOCKED
    assert rule.execution_allowed is False
    assert rule.status == VerificationStatus.VERIFY_PENDING
    geometry = _geometry(layer_clear_spacing_mm=25.0)
    step = legacy_blocked_layer_stub(geometry)
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED


# ---------------------------------------------------------------------------
# BG-DETAIL-COVER-001 — Clauses 9-4-9-5-1..3 + Table 9-4-6
# ---------------------------------------------------------------------------


def test_cover_rule_registry_metadata_verified() -> None:
    rule = RULE_BG_DETAIL_COVER_001
    assert rule.rule_id == "BG-DETAIL-COVER-001"
    assert rule.status == VerificationStatus.VERIFIED
    assert rule.execution_allowed is True
    assert rule.pdf_page == 92
    assert rule.printed_page == 71
    assert "9-4-9-5" in rule.clause_or_equation
    assert "9-4-6" in rule.clause_or_equation


def test_cover_not_exposed_beam_40mm() -> None:
    """Interior beams: 40 mm (longitudinal + transverse bars, Table row iv)."""
    geometry = _geometry(clear_cover_mm=40.0)
    step = evaluate_minimum_concrete_cover(
        geometry,
        exposure=ConcreteCoverExposureClass.NOT_EXPOSED,
    )
    assert step.outcome == EvaluationOutcome.PASS
    assert step.final_result == BG_DETAIL_COVER_001_BEAM_NOT_EXPOSED_MM

    failing = evaluate_minimum_concrete_cover(
        _geometry(clear_cover_mm=35.0),
        exposure=ConcreteCoverExposureClass.NOT_EXPOSED,
    )
    assert failing.outcome == EvaluationOutcome.FAIL
    assert failing.diagnostics[0].code == "INSUFFICIENT_CONCRETE_COVER"


def test_cover_computed_without_provided_value() -> None:
    """No provided cover (neither kwarg nor geometry) -> COMPUTED."""
    geometry = _geometry()
    step = evaluate_minimum_concrete_cover(
        geometry,
        exposure=ConcreteCoverExposureClass.NOT_EXPOSED,
    )
    assert step.outcome == EvaluationOutcome.COMPUTED
    assert step.final_result == 40.0


def test_cover_permanent_earth_contact_75mm() -> None:
    """Permanent earth contact: 75 mm for all members and all bars (row i)."""
    geometry = _geometry(clear_cover_mm=74.0)
    step = evaluate_minimum_concrete_cover(
        geometry,
        exposure=ConcreteCoverExposureClass.PERMANENT_EARTH_CONTACT,
    )
    assert step.outcome == EvaluationOutcome.FAIL
    assert step.final_result == BG_DETAIL_COVER_001_PERMANENT_EARTH_MM

    passing = evaluate_minimum_concrete_cover(
        _geometry(clear_cover_mm=75.0),
        exposure=ConcreteCoverExposureClass.PERMANENT_EARTH_CONTACT,
    )
    assert passing.outcome == EvaluationOutcome.PASS


def test_cover_weather_diameter_classes() -> None:
    """Air/earth contact: db <= 16 -> 40 mm; 18 <= db <= 58 -> 50 mm."""
    for db, required in (
        (10.0, BG_DETAIL_COVER_001_WEATHER_DB_LE_16_MM),
        (16.0, BG_DETAIL_COVER_001_WEATHER_DB_LE_16_MM),
        (18.0, BG_DETAIL_COVER_001_WEATHER_DB_18_TO_58_MM),
        (25.0, BG_DETAIL_COVER_001_WEATHER_DB_18_TO_58_MM),
        (58.0, BG_DETAIL_COVER_001_WEATHER_DB_18_TO_58_MM),
    ):
        step = evaluate_minimum_concrete_cover(
            _geometry(clear_cover_mm=required),
            exposure=ConcreteCoverExposureClass.WEATHER_OR_EARTH_CONTACT,
            cover_bar_diameter_mm=db,
        )
        assert step.outcome == EvaluationOutcome.PASS, (db, required, step.message)
        assert step.final_result == required


def test_cover_weather_governing_diameter_from_groups() -> None:
    """Diameter resolved from tension groups for weather exposure (25 -> 50)."""
    geometry = _geometry(
        clear_cover_mm=50.0,
        tension_rebar_groups=(RebarGroup(bar_diameter_mm=25.0, bar_count=2),),
    )
    step = evaluate_minimum_concrete_cover(
        geometry,
        exposure=ConcreteCoverExposureClass.WEATHER_OR_EARTH_CONTACT,
    )
    assert step.outcome == EvaluationOutcome.PASS
    assert step.intermediate_values["db_governing_mm"] == 25.0


def test_cover_weather_missing_diameter_invalid() -> None:
    """Weather exposure without db -> INVALID_INPUT (never assumed)."""
    geometry = _geometry(clear_cover_mm=80.0)
    step = evaluate_minimum_concrete_cover(
        geometry,
        exposure=ConcreteCoverExposureClass.WEATHER_OR_EARTH_CONTACT,
    )
    assert step.outcome == EvaluationOutcome.INVALID_INPUT
    assert step.diagnostics[0].code == "MISSING_COVER_BAR_DIAMETER"


def test_cover_weather_uncovered_diameter_classes_blocked() -> None:
    """db in (16, 18) or db > 58: not in Table 9-4-6 -> blocked, never interpolated."""
    for db in (17.0, 17.5, 60.0):
        step = evaluate_minimum_concrete_cover(
            _geometry(clear_cover_mm=100.0),
            exposure=ConcreteCoverExposureClass.WEATHER_OR_EARTH_CONTACT,
            cover_bar_diameter_mm=db,
        )
        assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
        assert step.diagnostics[0].code == "UNVERIFIED_COVER_DIAMETER_CLASS"
        assert step.final_result is None


def test_cover_missing_exposure_invalid_never_assumed() -> None:
    """Missing exposure condition -> INVALID_INPUT (never silently assumed)."""
    geometry = _geometry(clear_cover_mm=75.0)
    step = evaluate_minimum_concrete_cover(geometry)
    assert step.outcome == EvaluationOutcome.INVALID_INPUT
    assert step.diagnostics[0].code == "MISSING_COVER_EXPOSURE_CLASS"


def test_cover_corrosive_environment_blocked_appendix() -> None:
    """Corrosive/unusual environment -> routed to Appendix 9-پ1, BLOCKED."""
    geometry = _geometry(clear_cover_mm=100.0)
    step = evaluate_minimum_concrete_cover(
        geometry,
        exposure=ConcreteCoverExposureClass.CORROSIVE_ENVIRONMENT,
    )
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "CORROSIVE_EXPOSURE_BLOCKED_APPENDIX_9P1"
    assert step.diagnostics[0].severity == DiagnosticSeverity.BLOCK
    req_corr = step.diagnostics[0].required_verification
    assert req_corr is not None and "9-پ1" in req_corr
    assert step.final_result is None


def test_cover_bundled_bars_blocked_pending_9_21_5_6() -> None:
    """Bundled groups (Clause 9-4-9-5-2 -> 9-21-5-6) stay BLOCKED."""
    geometry = _geometry(clear_cover_mm=100.0)
    step = evaluate_minimum_concrete_cover(
        geometry,
        exposure=ConcreteCoverExposureClass.NOT_EXPOSED,
        is_bundled=True,
    )
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "UNVERIFIED_BUNDLED_BAR_COVER"
    req_cover = step.diagnostics[0].required_verification
    assert req_cover is not None and "9-21-5-6" in req_cover


def test_cover_headed_shear_reinforcement_same_minimum() -> None:
    """Clause 9-4-9-5-3: headed shear bars use the same member minimum."""
    geometry = _geometry(clear_cover_mm=40.0)
    step = evaluate_minimum_concrete_cover(
        geometry,
        exposure=ConcreteCoverExposureClass.NOT_EXPOSED,
        has_headed_shear_reinforcement=True,
    )
    assert step.outcome == EvaluationOutcome.PASS
    assert step.intermediate_values["headed_shear_reinforcement_same_minimum"] == 40.0
    assert "9-4-9-5-3" in step.message


def test_cover_invalid_numeric_inputs() -> None:
    geometry = _geometry(clear_cover_mm=-5.0)
    step = evaluate_minimum_concrete_cover(
        geometry,
        exposure=ConcreteCoverExposureClass.NOT_EXPOSED,
    )
    assert step.outcome == EvaluationOutcome.INVALID_INPUT

    step_db = evaluate_minimum_concrete_cover(
        _geometry(),
        exposure=ConcreteCoverExposureClass.WEATHER_OR_EARTH_CONTACT,
        cover_bar_diameter_mm=math.nan,
    )
    assert step_db.outcome == EvaluationOutcome.INVALID_INPUT


def test_cover_jurisdiction_blocked_in_reference_mode() -> None:
    geometry = _geometry()
    step = evaluate_minimum_concrete_cover(
        geometry,
        exposure=ConcreteCoverExposureClass.NOT_EXPOSED,
        jurisdiction_mode=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    )
    assert step.outcome == EvaluationOutcome.JURISDICTION_BLOCKED


def test_cover_legacy_blocked_sentinel_untouched() -> None:
    rule = RULE_BG_DETAIL_COVER_BLOCKED
    assert rule.execution_allowed is False
    assert rule.status == VerificationStatus.VERIFY_PENDING
    geometry = _geometry(clear_cover_mm=40.0)
    step = legacy_blocked_cover_stub(geometry)
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED


# ---------------------------------------------------------------------------
# Gatekeeper: the three promoted rules execute only in MABHAS_9_COMPLIANCE
# ---------------------------------------------------------------------------


def test_phase2e_rules_allowed_only_in_mabhas9_mode() -> None:
    """Promoted rules: allowed in MABHAS_9_COMPLIANCE, JURISDICTION_BLOCKED otherwise."""
    for rule_id in (
        "BG-DETAIL-SPACING-001",
        "BG-DETAIL-LAYER-SPACING-001",
        "BG-DETAIL-COVER-001",
    ):
        decision = evaluate_rule_gate(
            rule_id,
            active_jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
        )
        assert decision.allowed
        assert decision.blocked_outcome is None

        decision_ref = evaluate_rule_gate(
            rule_id,
            active_jurisdiction=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
        )
        assert not decision_ref.allowed
        assert decision_ref.blocked_outcome == EvaluationOutcome.JURISDICTION_BLOCKED


# ---------------------------------------------------------------------------
# Workflow aggregation & orchestrator dispatch
# ---------------------------------------------------------------------------


def test_detailing_workflow_runs_phase2e_rules_on_input_presence() -> None:
    """New verified steps join the workflow only when their inputs are supplied."""
    geometry = _geometry(
        clear_cover_mm=40.0,
        layer_clear_spacing_mm=25.0,
        tension_rebar_groups=(RebarGroup(bar_diameter_mm=25.0, bar_count=3),),
    )
    steps = run_mabhas9_beam_detailing_workflow(
        geometry,
        max_longitudinal_bar_diameter_mm=25.0,
        transverse_bar_diameter_mm=10.0,
        aggregate_size_mm=20.0,
        horizontal_clear_spacing_mm=28.0,
        rebar_layer_count=2,
        layers_directly_aligned=True,
        cover_exposure=ConcreteCoverExposureClass.NOT_EXPOSED,
    )
    assert [step.rule_id for step in steps] == [
        "BG-DETAIL-TRANS-DIA-001",
        "BG-DETAIL-SPACING-001",
        "BG-DETAIL-LAYER-SPACING-001",
        "BG-DETAIL-COVER-001",
    ]
    report = aggregate_compliance_report(steps)
    assert report.overall_status == OverallComplianceStatus.PASS
    assert report.is_compliant


def test_detailing_workflow_without_new_kwargs_is_unchanged() -> None:
    """No Phase 2E inputs -> workflow emits only the original Phase 2D steps."""
    geometry = _geometry()
    steps = run_mabhas9_beam_detailing_workflow(
        geometry,
        max_longitudinal_bar_diameter_mm=25.0,
    )
    assert [step.rule_id for step in steps] == ["BG-DETAIL-TRANS-DIA-001"]


def test_detailing_workflow_bundled_blocks_never_pass() -> None:
    """Bundled input blocks the spacing/cover steps; aggregate is BLOCKED."""
    geometry = _geometry(clear_cover_mm=100.0)
    steps = run_mabhas9_beam_detailing_workflow(
        geometry,
        max_longitudinal_bar_diameter_mm=25.0,
        is_bundled=True,
        aggregate_size_mm=20.0,
        cover_exposure=ConcreteCoverExposureClass.NOT_EXPOSED,
    )
    blocked_outcomes = {step.rule_id: step.outcome for step in steps}
    assert (
        blocked_outcomes["BG-DETAIL-SPACING-001"]
        == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    )
    assert (
        blocked_outcomes["BG-DETAIL-COVER-001"]
        == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    )
    report = aggregate_compliance_report(steps)
    assert report.overall_status == OverallComplianceStatus.BLOCKED
    assert not report.is_compliant


def test_detailing_workflow_missing_aggregate_dominates_invalid() -> None:
    """Missing mandatory aggregate input -> INVALID_INPUT dominates the report."""
    geometry = _geometry(clear_cover_mm=40.0)
    steps = run_mabhas9_beam_detailing_workflow(
        geometry,
        aggregate_size_mm=0.0,
        cover_exposure=ConcreteCoverExposureClass.NOT_EXPOSED,
    )
    assert steps[1].outcome == EvaluationOutcome.INVALID_INPUT
    report = aggregate_compliance_report(steps)
    assert report.overall_status == OverallComplianceStatus.INVALID_INPUT


def test_phase2e_rules_dispatch_via_run_mabhas9_beam_check() -> None:
    """Orchestrator dispatches the three verified Phase 2E rules."""
    geometry = _geometry(
        clear_cover_mm=40.0,
        layer_clear_spacing_mm=25.0,
        tension_rebar_groups=(RebarGroup(bar_diameter_mm=25.0, bar_count=3),),
    )
    concrete = ConcreteMaterial(fc_prime_mpa=30.0)
    rebar = RebarMaterial(fy_mpa=420.0)
    report = run_mabhas9_beam_check(
        geometry,
        concrete,
        rebar,
        max_longitudinal_bar_diameter_mm=25.0,
        aggregate_size_mm=20.0,
        horizontal_clear_spacing_mm=28.0,
        rebar_layer_count=2,
        layers_directly_aligned=True,
        cover_exposure=ConcreteCoverExposureClass.NOT_EXPOSED,
        requested_rule_ids=[
            "BG-DETAIL-SPACING-001",
            "BG-DETAIL-LAYER-SPACING-001",
            "BG-DETAIL-COVER-001",
        ],
    )
    assert report.overall_status == OverallComplianceStatus.PASS
    assert report.outcomes_by_rule["BG-DETAIL-SPACING-001"] == (
        EvaluationOutcome.PASS
    )
    assert report.outcomes_by_rule["BG-DETAIL-LAYER-SPACING-001"] == (
        EvaluationOutcome.PASS
    )
    assert report.outcomes_by_rule["BG-DETAIL-COVER-001"] == (
        EvaluationOutcome.PASS
    )


def test_phase2e_corrosive_cover_blocks_orchestrator_report() -> None:
    """A corrosive-exposure request blocks the whole compliance report."""
    geometry = _geometry(clear_cover_mm=40.0)
    concrete = ConcreteMaterial(fc_prime_mpa=30.0)
    rebar = RebarMaterial(fy_mpa=420.0)
    report = run_mabhas9_beam_check(
        geometry,
        concrete,
        rebar,
        cover_exposure=ConcreteCoverExposureClass.CORROSIVE_ENVIRONMENT,
        requested_rule_ids=["BG-DETAIL-COVER-001"],
    )
    assert report.overall_status == OverallComplianceStatus.BLOCKED
    assert report.outcomes_by_rule["BG-DETAIL-COVER-001"] == (
        EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    )
