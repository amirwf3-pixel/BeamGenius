"""Tests for Mabhas 9 (1399) Phase 2E Stage B verified spacing & cover rules.

Covers the three rules promoted from VERIFIED_SOURCE_ONLY (visually verified
2026-10-03 from Mabhas 9, 1399 5th ed. source-page captures) with the
Phase 2E Stage B deterministic contract:

- ``BG-DETAIL-LONG-SPACING-001`` (Clause 9-21-2-1-1, PDF p. 441 /
  Printed p. 420): s_clear >= max(25 mm, db_max, (4/3) * d_agg);
  shotcrete NOT_APPLICABLE (9-21-2-1-4); bundled BLOCKED
  (``UNVERIFIED_BUNDLE_RULE``; Clause 9-21-5-6 is VERIFIED as
  ``BG-DETAIL-BUNDLE-006`` — integration into these rules pending).
- ``BG-DETAIL-LAYER-SPACING-001`` (Clause 9-21-2-1-2, same source page):
  upper-layer bars directly above lower-layer bars (required typed alignment
  input) and clear inter-layer spacing >= 25 mm.
- ``BG-DETAIL-COVER-001`` (Clauses 9-4-9-4, 9-4-9-5-1..3 + Table 9-4-6,
  PDF pp. 92-93 / Printed pp. 71-72): minimum concrete cover: 40 mm
  unexposed beams/columns/pedestals/tension members, 20/40 mm unexposed
  slabs-joists-walls (db <= 34 / db > 36), 40/50 mm air-earth contact
  (db <= 16 / db 18-58), 75 mm permanent earth contact; corrosive BLOCKED
  (Appendix 9-پ1); bundled BLOCKED; uncovered diameter classes never
  interpolated.

Deterministic contract verified throughout: gatekeeper first; malformed
values -> INVALID_INPUT; MISSING required engineering inputs -> BLOCKED
(``UNVERIFIED_RULE_BLOCKED``), never assumed; BLOCKED never becomes PASS;
jurisdiction isolation; workflow aggregation; engine-reference isolation.
"""

from __future__ import annotations

import ast
import math
from pathlib import Path
from typing import Any, Dict, List

from beamgenius.domain import (
    BeamGeometry,
    ConcreteCoverExposureClass,
    ConcreteCoverMemberClass,
    ConcreteMaterial,
    CoverReinforcementType,
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
    evaluate_beam_cover,
    evaluate_concrete_cover as legacy_blocked_cover_stub,
    evaluate_layer_spacing as legacy_blocked_layer_stub,
    evaluate_longitudinal_bar_clear_spacing as legacy_blocked_spacing_stub,
    evaluate_longitudinal_layer_spacing,
    run_mabhas9_beam_check,
    run_mabhas9_beam_detailing_workflow,
)
from beamgenius.engine.detailing_spacing_mabhas9 import (
    BG_DETAIL_COVER_001_BEAM_NOT_EXPOSED_MM,
    BG_DETAIL_COVER_001_PERMANENT_EARTH_MM,
    BG_DETAIL_COVER_001_SLAB_NOT_EXPOSED_LARGE_DB_MM,
    BG_DETAIL_COVER_001_SLAB_NOT_EXPOSED_SMALL_DB_MM,
    BG_DETAIL_COVER_001_WEATHER_DB_18_TO_58_MM,
    BG_DETAIL_COVER_001_WEATHER_DB_LE_16_MM,
    BG_DETAIL_LAYER_SPACING_001_MIN_CLEAR_MM,
    BG_DETAIL_LONG_SPACING_001_AGGREGATE_FACTOR,
    BG_DETAIL_LONG_SPACING_001_MIN_CLEAR_MM,
    evaluate_longitudinal_bar_clear_spacing,
)
from beamgenius.registry.catalog import (
    RULE_BG_DETAIL_COVER_001,
    RULE_BG_DETAIL_COVER_BLOCKED,
    RULE_BG_DETAIL_LAYER_SPACING_001,
    RULE_BG_DETAIL_LAYER_SPACING_BLOCKED,
    RULE_BG_DETAIL_LONG_SPACING_001,
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


BEAM = ConcreteCoverMemberClass.BEAM
NO_EXPOSURE = ConcreteCoverExposureClass.NOT_EXPOSED
WEATHER = ConcreteCoverExposureClass.WEATHER_OR_EARTH_CONTACT
PERMANENT_EARTH = ConcreteCoverExposureClass.PERMANENT_EARTH_CONTACT
CORROSIVE = ConcreteCoverExposureClass.CORROSIVE_ENVIRONMENT
LONGITUDINAL = CoverReinforcementType.LONGITUDINAL
TRANSVERSE = CoverReinforcementType.TRANSVERSE


# ---------------------------------------------------------------------------
# BG-DETAIL-LONG-SPACING-001 — Clause 9-21-2-1-1 (clear spacing)
# ---------------------------------------------------------------------------


def test_long_spacing_registry_metadata_verified() -> None:
    """Final rule: VERIFIED CODE_RULE, execution_allowed=True, pages recorded."""
    rule = RULE_BG_DETAIL_LONG_SPACING_001
    assert rule.rule_id == "BG-DETAIL-LONG-SPACING-001"
    assert rule.status == VerificationStatus.VERIFIED
    assert rule.category.value == "CODE_RULE"
    assert rule.execution_allowed is True
    assert rule.pdf_page == 441
    assert rule.printed_page == 420
    assert "9-21-2-1-1" in rule.clause_or_equation


def test_clear_spacing_25mm_governing_case() -> None:
    """25 mm floor governs: max(25, 16, 4/3*12=16) = 25; exact 25 -> PASS."""
    geometry = _geometry()
    step = evaluate_longitudinal_bar_clear_spacing(
        geometry,
        max_bar_diameter_mm=16.0,
        aggregate_size_mm=12.0,
        provided_clear_spacing_mm=BG_DETAIL_LONG_SPACING_001_MIN_CLEAR_MM,
    )
    assert step.outcome == EvaluationOutcome.PASS
    assert step.final_result == 25.0
    assert step.intermediate_values["limit_absolute_25_mm"] == 25.0


def test_clear_spacing_db_governing_case() -> None:
    """db governs: max(25, 32, 26.667) = 32; provided 32 -> PASS, 31 -> FAIL."""
    geometry = _geometry()
    passing = evaluate_longitudinal_bar_clear_spacing(
        geometry,
        max_bar_diameter_mm=32.0,
        aggregate_size_mm=20.0,
        provided_clear_spacing_mm=32.0,
    )
    assert passing.outcome == EvaluationOutcome.PASS
    assert passing.final_result == 32.0
    failing = evaluate_longitudinal_bar_clear_spacing(
        geometry,
        max_bar_diameter_mm=32.0,
        aggregate_size_mm=20.0,
        provided_clear_spacing_mm=31.0,
    )
    assert failing.outcome == EvaluationOutcome.FAIL
    assert failing.diagnostics[0].code == "INSUFFICIENT_BAR_CLEAR_SPACING"


def test_clear_spacing_aggregate_governing_case() -> None:
    """d_agg governs: max(25, 25, 4/3*20=26.667) = 26.667; 26.667 -> PASS."""
    geometry = _geometry()
    required = BG_DETAIL_LONG_SPACING_001_AGGREGATE_FACTOR * 20.0
    passing = evaluate_longitudinal_bar_clear_spacing(
        geometry,
        max_bar_diameter_mm=25.0,
        aggregate_size_mm=20.0,
        provided_clear_spacing_mm=required,
    )
    assert passing.outcome == EvaluationOutcome.PASS
    assert passing.final_result == required
    failing = evaluate_longitudinal_bar_clear_spacing(
        geometry,
        max_bar_diameter_mm=25.0,
        aggregate_size_mm=20.0,
        provided_clear_spacing_mm=26.0,
    )
    assert failing.outcome == EvaluationOutcome.FAIL


def test_clear_spacing_below_limit_fail() -> None:
    """24.9 mm below the 25 mm floor -> FAIL, never PASS."""
    geometry = _geometry()
    step = evaluate_longitudinal_bar_clear_spacing(
        geometry,
        max_bar_diameter_mm=16.0,
        aggregate_size_mm=12.0,
        provided_clear_spacing_mm=24.9,
    )
    assert step.outcome == EvaluationOutcome.FAIL


def test_clear_spacing_computed_without_provided_value() -> None:
    """No provided clear spacing -> COMPUTED with required minimum."""
    geometry = _geometry()
    step = evaluate_longitudinal_bar_clear_spacing(
        geometry,
        max_bar_diameter_mm=25.0,
        aggregate_size_mm=20.0,
    )
    assert step.outcome == EvaluationOutcome.COMPUTED
    assert step.final_result == BG_DETAIL_LONG_SPACING_001_AGGREGATE_FACTOR * 20.0


def test_clear_spacing_missing_aggregate_blocked_never_pass() -> None:
    """Missing d_agg -> BLOCKED (clause item (پ) is never dropped)."""
    geometry = _geometry()
    step = evaluate_longitudinal_bar_clear_spacing(
        geometry,
        max_bar_diameter_mm=25.0,
        provided_clear_spacing_mm=500.0,  # would pass if d_agg were dropped
    )
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "MISSING_AGGREGATE_SIZE"
    assert step.diagnostics[0].severity == DiagnosticSeverity.BLOCK
    assert step.final_result is None


def test_clear_spacing_missing_db_blocked() -> None:
    """Missing db (no kwarg, no groups) -> BLOCKED."""
    geometry = _geometry()
    step = evaluate_longitudinal_bar_clear_spacing(
        geometry,
        aggregate_size_mm=20.0,
    )
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "MISSING_GOVERNING_BAR_DIAMETER"


def test_clear_spacing_invalid_diameter_invalid_input() -> None:
    """Malformed values (non-positive / non-finite) -> INVALID_INPUT."""
    geometry = _geometry()
    invalid_cases: List[Dict[str, Any]] = [
        {"max_bar_diameter_mm": 0.0, "aggregate_size_mm": 20.0},
        {"max_bar_diameter_mm": math.nan, "aggregate_size_mm": 20.0},
        {"max_bar_diameter_mm": -12.0, "aggregate_size_mm": 20.0},
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


def test_clear_spacing_malformed_dominates_bundled_blocked_in_aggregate() -> None:
    """Aggregate report precedence: INVALID_INPUT > FAIL > BLOCKED > PARTIAL > PASS."""
    geometry = _geometry()
    blocked_step = evaluate_longitudinal_bar_clear_spacing(
        geometry,
        max_bar_diameter_mm=25.0,
        provided_clear_spacing_mm=500.0,  # missing aggregate -> BLOCKED
    )
    invalid_step = evaluate_longitudinal_bar_clear_spacing(
        geometry,
        max_bar_diameter_mm=-1.0,
        aggregate_size_mm=20.0,
    )
    report = aggregate_compliance_report([blocked_step])
    assert report.overall_status == OverallComplianceStatus.BLOCKED
    report_invalid = aggregate_compliance_report([blocked_step, invalid_step])
    assert report_invalid.overall_status == OverallComplianceStatus.INVALID_INPUT


def test_clear_spacing_bundled_blocked_unverified_bundle_rule() -> None:
    """Bundled reinforcement branch -> BLOCKED UNVERIFIED_BUNDLE_RULE, never PASS."""
    geometry = _geometry()
    step = evaluate_longitudinal_bar_clear_spacing(
        geometry,
        max_bar_diameter_mm=25.0,
        aggregate_size_mm=20.0,
        provided_clear_spacing_mm=500.0,
        is_bundled=True,
    )
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "UNVERIFIED_BUNDLE_RULE"
    assert step.diagnostics[0].severity == DiagnosticSeverity.BLOCK
    req = step.diagnostics[0].required_verification
    assert req is not None and "9-21-5-6" in req
    assert step.final_result is None


def test_clear_spacing_shotcrete_not_applicable() -> None:
    """Clause 9-21-2-1-4: shotcrete is out of scope -> NOT_APPLICABLE."""
    geometry = _geometry()
    step = evaluate_longitudinal_bar_clear_spacing(
        geometry,
        max_bar_diameter_mm=25.0,
        aggregate_size_mm=20.0,
        is_shotcrete=True,
    )
    assert step.outcome == EvaluationOutcome.NOT_APPLICABLE


def test_clear_spacing_db_resolved_from_tension_groups() -> None:
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
    assert step.outcome == EvaluationOutcome.FAIL
    assert step.intermediate_values["db_governing_mm"] == 32.0


def test_clear_spacing_jurisdiction_blocked_in_reference_mode() -> None:
    """Mabhas rule is JURISDICTION_BLOCKED under MOSTOFINEJAD_METHODOLOGY_ONLY."""
    geometry = _geometry()
    step = evaluate_longitudinal_bar_clear_spacing(
        geometry,
        max_bar_diameter_mm=25.0,
        aggregate_size_mm=20.0,
        jurisdiction_mode=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    )
    assert step.outcome == EvaluationOutcome.JURISDICTION_BLOCKED


def test_long_spacing_legacy_blocked_sentinel_untouched() -> None:
    """The legacy BG-DETAIL-SPACING-BLOCKED sentinel and stub stay blocked."""
    rule = RULE_BG_DETAIL_SPACING_BLOCKED
    assert rule.execution_allowed is False
    assert rule.status == VerificationStatus.VERIFY_PENDING
    step = legacy_blocked_spacing_stub(_geometry())
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED


# ---------------------------------------------------------------------------
# BG-DETAIL-LAYER-SPACING-001 — Clause 9-21-2-1-2 (layer spacing)
# ---------------------------------------------------------------------------


def test_layer_spacing_registry_metadata_verified() -> None:
    rule = RULE_BG_DETAIL_LAYER_SPACING_001
    assert rule.rule_id == "BG-DETAIL-LAYER-SPACING-001"
    assert rule.status == VerificationStatus.VERIFIED
    assert rule.execution_allowed is True
    assert rule.pdf_page == 441
    assert rule.printed_page == 420
    assert "9-21-2-1-2" in rule.clause_or_equation


def test_layer_spacing_exact_25mm_pass() -> None:
    """Aligned layers + exactly 25 mm clear -> PASS."""
    geometry = _geometry(layer_clear_spacing_mm=25.0)
    step = evaluate_longitudinal_layer_spacing(
        geometry,
        layer_count=2,
        layers_directly_aligned=True,
    )
    assert step.outcome == EvaluationOutcome.PASS
    assert step.final_result == BG_DETAIL_LAYER_SPACING_001_MIN_CLEAR_MM


def test_layer_spacing_below_limit_fail() -> None:
    """Aligned layers + 24 mm clear -> FAIL (independent of db/aggregate)."""
    geometry = _geometry(layer_clear_spacing_mm=24.0)
    step = evaluate_longitudinal_layer_spacing(
        geometry,
        layer_count=2,
        layers_directly_aligned=True,
    )
    assert step.outcome == EvaluationOutcome.FAIL
    assert step.diagnostics[0].code == "INSUFFICIENT_LAYER_CLEAR_SPACING"


def test_layer_spacing_misalignment_fail() -> None:
    """Non-aligned layers -> FAIL even with generous spacing."""
    geometry = _geometry(layer_clear_spacing_mm=100.0)
    step = evaluate_longitudinal_layer_spacing(
        geometry,
        layer_count=2,
        layers_directly_aligned=False,
    )
    assert step.outcome == EvaluationOutcome.FAIL
    assert step.diagnostics[0].code == "LAYERS_NOT_DIRECTLY_ALIGNED"


def test_layer_spacing_missing_layer_geometry_blocked() -> None:
    """Missing layer count -> BLOCKED; alignment never silently assumed."""
    geometry = _geometry(layer_clear_spacing_mm=30.0)
    step = evaluate_longitudinal_layer_spacing(geometry)
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "MISSING_LAYER_COUNT"

    miss_align = evaluate_longitudinal_layer_spacing(
        geometry,
        layer_count=2,
    )
    assert miss_align.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert miss_align.diagnostics[0].code == "MISSING_LAYER_ALIGNMENT"
    assert miss_align.diagnostics[0].severity == DiagnosticSeverity.BLOCK
    assert miss_align.final_result is None


def test_layer_spacing_invalid_layer_count_invalid_input() -> None:
    """Malformed layer count (0 / non-integer / bool) -> INVALID_INPUT."""
    geometry = _geometry()
    for bad in (0, -1, 2.5, True):
        step = evaluate_longitudinal_layer_spacing(
            geometry,
            layer_count=bad,  # type: ignore[arg-type]
        )
        assert step.outcome == EvaluationOutcome.INVALID_INPUT
        assert step.diagnostics[0].code == "INVALID_LAYER_COUNT"


def test_layer_spacing_single_layer_not_applicable() -> None:
    """layer_count == 1 -> NOT_APPLICABLE (no inter-layer requirement)."""
    geometry = _geometry()
    step = evaluate_longitudinal_layer_spacing(geometry, layer_count=1)
    assert step.outcome == EvaluationOutcome.NOT_APPLICABLE


def test_layer_spacing_computed_without_provided_value() -> None:
    """Aligned multi-layer, no provided spacing -> COMPUTED (25 mm)."""
    geometry = _geometry()
    step = evaluate_longitudinal_layer_spacing(
        geometry,
        layer_count=2,
        layers_directly_aligned=True,
    )
    assert step.outcome == EvaluationOutcome.COMPUTED
    assert step.final_result == 25.0


def test_layer_spacing_count_derived_from_rebar_groups() -> None:
    """Layer count derived from max layer_index of tension rebar groups."""
    geometry = _geometry(
        layer_clear_spacing_mm=25.0,
        tension_rebar_groups=(
            RebarGroup(bar_diameter_mm=25.0, bar_count=3, layer_index=1),
            RebarGroup(bar_diameter_mm=25.0, bar_count=2, layer_index=2),
        ),
    )
    step = evaluate_longitudinal_layer_spacing(
        geometry,
        layers_directly_aligned=True,
    )
    assert step.outcome == EvaluationOutcome.PASS
    assert step.intermediate_values["layer_count"] == 2.0


def test_layer_spacing_bundled_blocked_unverified_bundle_rule() -> None:
    geometry = _geometry(layer_clear_spacing_mm=100.0)
    step = evaluate_longitudinal_layer_spacing(
        geometry,
        layer_count=2,
        layers_directly_aligned=True,
        is_bundled=True,
    )
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "UNVERIFIED_BUNDLE_RULE"
    req = step.diagnostics[0].required_verification
    assert req is not None and "9-21-5-6" in req


def test_layer_spacing_jurisdiction_blocked_in_reference_mode() -> None:
    geometry = _geometry()
    step = evaluate_longitudinal_layer_spacing(
        geometry,
        layer_count=2,
        layers_directly_aligned=True,
        jurisdiction_mode=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    )
    assert step.outcome == EvaluationOutcome.JURISDICTION_BLOCKED


def test_layer_spacing_legacy_blocked_sentinel_untouched() -> None:
    rule = RULE_BG_DETAIL_LAYER_SPACING_BLOCKED
    assert rule.execution_allowed is False
    assert rule.status == VerificationStatus.VERIFY_PENDING
    step = legacy_blocked_layer_stub(_geometry(layer_clear_spacing_mm=25.0))
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED


# ---------------------------------------------------------------------------
# BG-DETAIL-COVER-001 — Clauses 9-4-9-5-1..3 + Table 9-4-6 (concrete cover)
# ---------------------------------------------------------------------------


def test_cover_registry_metadata_verified() -> None:
    rule = RULE_BG_DETAIL_COVER_001
    assert rule.rule_id == "BG-DETAIL-COVER-001"
    assert rule.status == VerificationStatus.VERIFIED
    assert rule.execution_allowed is True
    assert rule.pdf_page == 92
    assert rule.printed_page == 71
    assert "9-4-9-5" in rule.clause_or_equation
    assert "9-4-6" in rule.clause_or_equation


def test_cover_beam_non_exposed_longitudinal_40mm() -> None:
    """Beam, no air/earth contact, longitudinal bars: 40 mm (Table row iv)."""
    geometry = _geometry(clear_cover_mm=40.0)
    step = evaluate_beam_cover(
        geometry,
        exposure=NO_EXPOSURE,
        member_class=BEAM,
        reinforcement_type=LONGITUDINAL,
    )
    assert step.outcome == EvaluationOutcome.PASS
    assert step.final_result == BG_DETAIL_COVER_001_BEAM_NOT_EXPOSED_MM

    failing = evaluate_beam_cover(
        _geometry(clear_cover_mm=35.0),
        exposure=NO_EXPOSURE,
        member_class=BEAM,
        reinforcement_type=LONGITUDINAL,
    )
    assert failing.outcome == EvaluationOutcome.FAIL
    assert failing.diagnostics[0].code == "INSUFFICIENT_CONCRETE_COVER"


def test_cover_beam_non_exposed_stirrups_40mm() -> None:
    """Beam, no air/earth contact, stirrups/ties (TRANSVERSE): 40 mm."""
    geometry = _geometry(clear_cover_mm=40.0)
    step = evaluate_beam_cover(
        geometry,
        exposure=NO_EXPOSURE,
        member_class=BEAM,
        reinforcement_type=TRANSVERSE,
    )
    assert step.outcome == EvaluationOutcome.PASS
    assert step.final_result == 40.0
    assert "stirrups" in step.message


def test_cover_column_non_exposed_40mm() -> None:
    """Columns/pedestals/tension members share the 40 mm row (iv)."""
    for member in (
        ConcreteCoverMemberClass.COLUMN,
        ConcreteCoverMemberClass.PEDESTAL,
        ConcreteCoverMemberClass.TENSION_MEMBER,
    ):
        step = evaluate_beam_cover(
            _geometry(clear_cover_mm=40.0),
            exposure=NO_EXPOSURE,
            member_class=member,
            reinforcement_type=LONGITUDINAL,
        )
        assert step.outcome == EvaluationOutcome.PASS, member
        assert step.final_result == 40.0


def test_cover_beam_soil_contact_permanent_75mm() -> None:
    """Permanent earth contact: 75 mm for all members and all bars."""
    step = evaluate_beam_cover(
        _geometry(clear_cover_mm=75.0),
        exposure=PERMANENT_EARTH,
        member_class=BEAM,
        reinforcement_type=LONGITUDINAL,
    )
    assert step.outcome == EvaluationOutcome.PASS
    assert step.final_result == BG_DETAIL_COVER_001_PERMANENT_EARTH_MM

    failing = evaluate_beam_cover(
        _geometry(clear_cover_mm=70.0),
        exposure=PERMANENT_EARTH,
        member_class=BEAM,
        reinforcement_type=LONGITUDINAL,
    )
    assert failing.outcome == EvaluationOutcome.FAIL


def test_cover_weather_diameter_classes() -> None:
    """Air/earth contact: db <= 16 -> 40 mm; 18 <= db <= 58 -> 50 mm."""
    cases = (
        (10.0, BG_DETAIL_COVER_001_WEATHER_DB_LE_16_MM),
        (16.0, BG_DETAIL_COVER_001_WEATHER_DB_LE_16_MM),
        (18.0, BG_DETAIL_COVER_001_WEATHER_DB_18_TO_58_MM),
        (25.0, BG_DETAIL_COVER_001_WEATHER_DB_18_TO_58_MM),
        (58.0, BG_DETAIL_COVER_001_WEATHER_DB_18_TO_58_MM),
    )
    for db, required in cases:
        step = evaluate_beam_cover(
            _geometry(clear_cover_mm=required),
            exposure=WEATHER,
            member_class=BEAM,
            reinforcement_type=LONGITUDINAL,
            cover_bar_diameter_mm=db,
        )
        assert step.outcome == EvaluationOutcome.PASS, (db, step.message)
        assert step.final_result == required


def test_cover_weather_stirrup_small_bar_40mm() -> None:
    """Weather exposure, stirrup (db=10, TRANSVERSE) -> 40 mm."""
    step = evaluate_beam_cover(
        _geometry(clear_cover_mm=40.0),
        exposure=WEATHER,
        member_class=BEAM,
        reinforcement_type=TRANSVERSE,
        cover_bar_diameter_mm=10.0,
    )
    assert step.outcome == EvaluationOutcome.PASS
    assert step.final_result == 40.0


def test_cover_weather_uncovered_diameter_classes_blocked() -> None:
    """db in (16, 18) or db > 58: not in Table 9-4-6 -> blocked, never interpolated."""
    for db in (17.0, 17.5, 60.0):
        step = evaluate_beam_cover(
            _geometry(clear_cover_mm=100.0),
            exposure=WEATHER,
            member_class=BEAM,
            reinforcement_type=LONGITUDINAL,
            cover_bar_diameter_mm=db,
        )
        assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
        assert step.diagnostics[0].code == "UNVERIFIED_COVER_DIAMETER_CLASS"
        assert step.final_result is None


def test_cover_slab_joist_wall_non_exposed_diameter_classes() -> None:
    """Unexposed slabs/joists/walls: db <= 34 -> 20 mm; db > 36 -> 40 mm."""
    for member in (
        ConcreteCoverMemberClass.SLAB,
        ConcreteCoverMemberClass.JOIST,
        ConcreteCoverMemberClass.WALL,
    ):
        small = evaluate_beam_cover(
            _geometry(clear_cover_mm=20.0),
            exposure=NO_EXPOSURE,
            member_class=member,
            reinforcement_type=LONGITUDINAL,
            cover_bar_diameter_mm=25.0,
        )
        assert small.outcome == EvaluationOutcome.PASS, member
        assert small.final_result == BG_DETAIL_COVER_001_SLAB_NOT_EXPOSED_SMALL_DB_MM

        large = evaluate_beam_cover(
            _geometry(clear_cover_mm=40.0),
            exposure=NO_EXPOSURE,
            member_class=member,
            reinforcement_type=LONGITUDINAL,
            cover_bar_diameter_mm=40.0,
        )
        assert large.outcome == EvaluationOutcome.PASS, member
        assert large.final_result == BG_DETAIL_COVER_001_SLAB_NOT_EXPOSED_LARGE_DB_MM


def test_cover_slab_uncovered_interval_blocked_never_interpolated() -> None:
    """Unexposed slab with db in (34, 36] -> BLOCKED, never interpolated."""
    step = evaluate_beam_cover(
        _geometry(clear_cover_mm=100.0),
        exposure=NO_EXPOSURE,
        member_class=ConcreteCoverMemberClass.SLAB,
        reinforcement_type=LONGITUDINAL,
        cover_bar_diameter_mm=36.0,
    )
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "UNVERIFIED_COVER_DIAMETER_CLASS"


def test_cover_missing_exposure_blocked_never_assumed() -> None:
    """Missing exposure -> BLOCKED (never silently assumed, never PASS)."""
    step = evaluate_beam_cover(
        _geometry(clear_cover_mm=75.0),
        member_class=BEAM,
        reinforcement_type=LONGITUDINAL,
    )
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "MISSING_COVER_EXPOSURE_CLASS"
    assert step.diagnostics[0].severity == DiagnosticSeverity.BLOCK
    assert step.final_result is None


def test_cover_missing_member_type_blocked() -> None:
    """Missing member type -> BLOCKED (never silently assumed)."""
    step = evaluate_beam_cover(
        _geometry(clear_cover_mm=40.0),
        exposure=NO_EXPOSURE,
        reinforcement_type=LONGITUDINAL,
    )
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "MISSING_COVER_MEMBER_CLASS"


def test_cover_unknown_member_type_invalid_input() -> None:
    """Unknown member type (non-enum value) -> INVALID_INPUT."""
    step = evaluate_beam_cover(
        _geometry(clear_cover_mm=40.0),
        exposure=NO_EXPOSURE,
        member_class="REINFORCED_CONCRETE_TUBE",  # type: ignore[arg-type]
        reinforcement_type=LONGITUDINAL,
    )
    assert step.outcome == EvaluationOutcome.INVALID_INPUT
    assert step.diagnostics[0].code == "UNKNOWN_COVER_MEMBER_CLASS"


def test_cover_missing_reinforcement_type_blocked() -> None:
    """Missing reinforcement type -> BLOCKED (never silently assumed)."""
    step = evaluate_beam_cover(
        _geometry(clear_cover_mm=40.0),
        exposure=NO_EXPOSURE,
        member_class=BEAM,
    )
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "MISSING_COVER_REINFORCEMENT_TYPE"


def test_cover_weather_missing_diameter_blocked() -> None:
    """Weather exposure without db -> BLOCKED (never assumed)."""
    step = evaluate_beam_cover(
        _geometry(clear_cover_mm=80.0),
        exposure=WEATHER,
        member_class=BEAM,
        reinforcement_type=LONGITUDINAL,
    )
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "MISSING_COVER_BAR_DIAMETER"


def test_cover_slab_missing_diameter_blocked() -> None:
    """Unexposed slab without db -> BLOCKED (never assumed)."""
    step = evaluate_beam_cover(
        _geometry(clear_cover_mm=80.0),
        exposure=NO_EXPOSURE,
        member_class=ConcreteCoverMemberClass.SLAB,
        reinforcement_type=LONGITUDINAL,
    )
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "MISSING_COVER_BAR_DIAMETER"


def test_cover_corrosive_blocked_with_reference_required() -> None:
    """Corrosive environment -> BLOCKED; Appendix 9-پ1 values never computed."""
    geometry = _geometry(clear_cover_mm=100.0)
    step = evaluate_beam_cover(
        geometry,
        exposure=CORROSIVE,
        member_class=BEAM,
        reinforcement_type=LONGITUDINAL,
    )
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "CORROSIVE_EXPOSURE_BLOCKED_APPENDIX_9P1"
    assert step.diagnostics[0].severity == DiagnosticSeverity.BLOCK
    req = step.diagnostics[0].required_verification
    assert req is not None and "9-پ1" in req
    assert step.final_result is None


def test_cover_bundled_blocked_unverified_bundle_rule() -> None:
    """Bundled reinforcement -> BLOCKED UNVERIFIED_BUNDLE_RULE, never PASS."""
    step = evaluate_beam_cover(
        _geometry(clear_cover_mm=100.0),
        exposure=NO_EXPOSURE,
        member_class=BEAM,
        reinforcement_type=LONGITUDINAL,
        is_bundled=True,
    )
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "UNVERIFIED_BUNDLE_RULE"
    req = step.diagnostics[0].required_verification
    assert req is not None and "9-21-5-6" in req


def test_cover_headed_shear_reinforcement_same_minimum() -> None:
    """Clause 9-4-9-5-3: headed shear bars use the same member minimum."""
    step = evaluate_beam_cover(
        _geometry(clear_cover_mm=40.0),
        exposure=NO_EXPOSURE,
        member_class=BEAM,
        reinforcement_type=TRANSVERSE,
        has_headed_shear_reinforcement=True,
    )
    assert step.outcome == EvaluationOutcome.PASS
    assert step.intermediate_values["headed_shear_reinforcement_same_minimum"] == 40.0
    assert "9-4-9-5-3" in step.message


def test_cover_computed_without_provided_value() -> None:
    """No provided cover -> COMPUTED with required minimum."""
    step = evaluate_beam_cover(
        _geometry(),
        exposure=NO_EXPOSURE,
        member_class=BEAM,
        reinforcement_type=LONGITUDINAL,
    )
    assert step.outcome == EvaluationOutcome.COMPUTED
    assert step.final_result == 40.0


def test_cover_diameter_resolved_from_tension_groups() -> None:
    """Governing diameter resolved from tension groups (weather, 25 -> 50)."""
    geometry = _geometry(
        clear_cover_mm=50.0,
        tension_rebar_groups=(RebarGroup(bar_diameter_mm=25.0, bar_count=2),),
    )
    step = evaluate_beam_cover(
        geometry,
        exposure=WEATHER,
        member_class=BEAM,
        reinforcement_type=LONGITUDINAL,
    )
    assert step.outcome == EvaluationOutcome.PASS
    assert step.intermediate_values["db_governing_mm"] == 25.0


def test_cover_malformed_values_invalid_input() -> None:
    neg_cover = evaluate_beam_cover(
        _geometry(clear_cover_mm=-5.0),
        exposure=NO_EXPOSURE,
        member_class=BEAM,
        reinforcement_type=LONGITUDINAL,
    )
    assert neg_cover.outcome == EvaluationOutcome.INVALID_INPUT

    nan_db = evaluate_beam_cover(
        _geometry(),
        exposure=WEATHER,
        member_class=BEAM,
        reinforcement_type=LONGITUDINAL,
        cover_bar_diameter_mm=math.nan,
    )
    assert nan_db.outcome == EvaluationOutcome.INVALID_INPUT


def test_cover_jurisdiction_blocked_in_reference_mode() -> None:
    step = evaluate_beam_cover(
        _geometry(),
        exposure=NO_EXPOSURE,
        member_class=BEAM,
        reinforcement_type=LONGITUDINAL,
        jurisdiction_mode=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    )
    assert step.outcome == EvaluationOutcome.JURISDICTION_BLOCKED


def test_cover_legacy_blocked_sentinel_untouched() -> None:
    rule = RULE_BG_DETAIL_COVER_BLOCKED
    assert rule.execution_allowed is False
    assert rule.status == VerificationStatus.VERIFY_PENDING
    step = legacy_blocked_cover_stub(_geometry(clear_cover_mm=40.0))
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED


# ---------------------------------------------------------------------------
# Gatekeeper: promoted rules execute only in MABHAS_9_COMPLIANCE
# ---------------------------------------------------------------------------


def test_phase2e_rules_allowed_only_in_mabhas9_mode() -> None:
    """Allowed in MABHAS_9_COMPLIANCE, JURISDICTION_BLOCKED in reference mode."""
    for rule_id in (
        "BG-DETAIL-LONG-SPACING-001",
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
        cover_exposure=NO_EXPOSURE,
        cover_member_class=BEAM,
        cover_reinforcement_type=LONGITUDINAL,
    )
    assert [step.rule_id for step in steps] == [
        "BG-DETAIL-TRANS-DIA-001",
        "BG-DETAIL-LONG-SPACING-001",
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
        cover_exposure=NO_EXPOSURE,
        cover_member_class=BEAM,
        cover_reinforcement_type=LONGITUDINAL,
    )
    outcomes = {step.rule_id: step.outcome for step in steps}
    assert (
        outcomes["BG-DETAIL-LONG-SPACING-001"]
        == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    )
    assert (
        outcomes["BG-DETAIL-COVER-001"]
        == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    )
    report = aggregate_compliance_report(steps)
    assert report.overall_status == OverallComplianceStatus.BLOCKED
    assert not report.is_compliant


def test_detailing_workflow_missing_aggregate_blocks_report() -> None:
    """Missing mandatory aggregate input -> BLOCKED step dominates the report."""
    geometry = _geometry(
        clear_cover_mm=40.0,
        tension_rebar_groups=(RebarGroup(bar_diameter_mm=25.0, bar_count=3),),
    )
    steps = run_mabhas9_beam_detailing_workflow(
        geometry,
        max_longitudinal_bar_diameter_mm=25.0,
        transverse_bar_diameter_mm=10.0,
        aggregate_size_mm=0.0,  # present but malformed -> INVALID_INPUT
        cover_exposure=NO_EXPOSURE,
        cover_member_class=BEAM,
        cover_reinforcement_type=LONGITUDINAL,
    )
    assert steps[1].rule_id == "BG-DETAIL-LONG-SPACING-001"
    assert steps[1].outcome == EvaluationOutcome.INVALID_INPUT

    flat_report = aggregate_compliance_report(steps)
    assert flat_report.overall_status == OverallComplianceStatus.INVALID_INPUT


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
        cover_exposure=NO_EXPOSURE,
        cover_member_class=BEAM,
        cover_reinforcement_type=LONGITUDINAL,
        requested_rule_ids=[
            "BG-DETAIL-LONG-SPACING-001",
            "BG-DETAIL-LAYER-SPACING-001",
            "BG-DETAIL-COVER-001",
        ],
    )
    assert report.overall_status == OverallComplianceStatus.PASS
    assert report.outcomes_by_rule["BG-DETAIL-LONG-SPACING-001"] == (
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
    geometry = _geometry(clear_cover_mm=100.0)
    concrete = ConcreteMaterial(fc_prime_mpa=30.0)
    rebar = RebarMaterial(fy_mpa=420.0)
    report = run_mabhas9_beam_check(
        geometry,
        concrete,
        rebar,
        cover_exposure=CORROSIVE,
        cover_member_class=BEAM,
        cover_reinforcement_type=LONGITUDINAL,
        requested_rule_ids=["BG-DETAIL-COVER-001"],
    )
    assert report.overall_status == OverallComplianceStatus.BLOCKED
    assert report.outcomes_by_rule["BG-DETAIL-COVER-001"] == (
        EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    )


def test_phase2e_missing_exposure_never_passes_orchestrator_report() -> None:
    """Requesting the cover rule without exposure -> BLOCKED, never PASS."""
    geometry = _geometry(clear_cover_mm=100.0)
    concrete = ConcreteMaterial(fc_prime_mpa=30.0)
    rebar = RebarMaterial(fy_mpa=420.0)
    report = run_mabhas9_beam_check(
        geometry,
        concrete,
        rebar,
        requested_rule_ids=["BG-DETAIL-COVER-001"],
    )
    assert report.overall_status == OverallComplianceStatus.BLOCKED
    assert report.outcomes_by_rule["BG-DETAIL-COVER-001"] == (
        EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    )


# ---------------------------------------------------------------------------
# Engine-reference isolation: no imports from the isolated reference package
# ---------------------------------------------------------------------------


def test_phase2e_engine_modules_have_no_reference_imports() -> None:
    """The verified engine must stay isolated from the Mostofinejad reference."""
    engine_dir = (
        Path(__file__).resolve().parents[1] / "src" / "beamgenius" / "engine"
    )
    module_files = [
        engine_dir / "detailing_spacing_mabhas9.py",
        engine_dir / "detailing_mabhas9.py",
        engine_dir / "beam_checker.py",
    ]
    for module_file in module_files:
        tree = ast.parse(module_file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert "reference" not in alias.name, module_file.name
            elif isinstance(node, ast.ImportFrom):
                module_name = node.module or ""
                assert "reference" not in module_name, module_file.name
