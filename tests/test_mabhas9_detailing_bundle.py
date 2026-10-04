"""Tests for Mabhas 9 (1399) Phase 2F Stage B verified bundled-bar rules.

Covers the eight rules promoted from VERIFIED_SOURCE_ONLY (visually
verified 2026-10-03 from Mabhas 9, 1399 5th ed. source-page captures,
re-confirmed 2026-10-05; Printed pp. 441-442 / PDF pp. 462-463) with the
Phase 2F Stage B deterministic contract:

- ``BG-DETAIL-BUNDLE-001`` (Clause 9-21-5-1): n_bundle <= 4.
- ``BG-DETAIL-BUNDLE-002`` (Clause 9-21-5-2): transverse enclosure;
  compressed bundles dbt >= 12 mm.
- ``BG-DETAIL-BUNDLE-003`` (Clause 9-21-5-3): beam bundled db > 34 mm
  prohibited (beam-only clause; non-beam NOT_APPLICABLE).
- ``BG-DETAIL-BUNDLE-004`` (Clause 9-21-5-4): cutoff staggering >= 40*db.
- ``BG-DETAIL-BUNDLE-005`` (Clause 9-21-5-5): >2-bar bundles, max 2 bars
  per plane (splice exception).
- ``BG-DETAIL-BUNDLE-006`` (Clause 9-21-5-6): d_eq = db*sqrt(n) for n
  identical bars.
- ``BG-DETAIL-BUNDLE-007`` (Clause 9-21-5-7): ld multipliers
  2-bar 1.00 / 3-bar 1.20 / 4-bar 1.33 (tension and compression).
- ``BG-DETAIL-BUNDLE-008`` (Clause 9-21-5-8): per-bar lap = ld *
  multiplier; individual laps must not overlap; bundle-to-bundle lap
  prohibited.

Deterministic contract verified throughout: gatekeeper first; malformed
values -> INVALID_INPUT; MISSING required engineering inputs -> BLOCKED
(``UNVERIFIED_RULE_BLOCKED``), never assumed; the single-bar development
length of Clause 9-21-3 and lap rules of Clause 9-21-4 are NOT computed
(unverified dependencies -> typed BLOCKED, never invented); BLOCKED never
becomes PASS; jurisdiction isolation; workflow aggregation; registry
exact-set; engine-reference isolation.
"""

from __future__ import annotations

import ast
import math
from pathlib import Path
from typing import List

from beamgenius.domain import (
    BeamGeometry,
    ConcreteCoverMemberClass,
    DiagnosticSeverity,
    EvaluationOutcome,
    JurisdictionMode,
    OverallComplianceStatus,
    VerificationStatus,
)
from beamgenius.engine import (
    aggregate_compliance_report,
    run_mabhas9_beam_check,
    run_mabhas9_beam_detailing_workflow,
)
from beamgenius.engine.detailing_bundle_mabhas9 import (
    BG_DETAIL_BUNDLE_001_MAX_BARS,
    BG_DETAIL_BUNDLE_002_COMPRESSED_MIN_TRANSVERSE_DIAMETER_MM,
    BG_DETAIL_BUNDLE_003_BEAM_MAX_BUNDLED_DB_MM,
    BG_DETAIL_BUNDLE_004_CUTOFF_STAGGER_FACTOR,
    BG_DETAIL_BUNDLE_005_MAX_BARS_PER_PLANE,
    BG_DETAIL_BUNDLE_007_LD_MULTIPLIERS,
    evaluate_bundle_bar_count,
    evaluate_bundle_beam_bar_diameter,
    evaluate_bundle_cutoff_stagger,
    evaluate_bundle_development_length,
    evaluate_bundle_equivalent_diameter,
    evaluate_bundle_lap_splice,
    evaluate_bundle_plane_arrangement,
    evaluate_bundle_transverse_reinforcement,
)
from beamgenius.registry.catalog import (
    RULE_BG_DETAIL_BUNDLE_001,
    RULE_BG_DETAIL_BUNDLE_002,
    RULE_BG_DETAIL_BUNDLE_003,
    RULE_BG_DETAIL_BUNDLE_004,
    RULE_BG_DETAIL_BUNDLE_005,
    RULE_BG_DETAIL_BUNDLE_006,
    RULE_BG_DETAIL_BUNDLE_007,
    RULE_BG_DETAIL_BUNDLE_008,
)
from beamgenius.registry.gatekeeper import evaluate_rule_gate


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

BEAM = ConcreteCoverMemberClass.BEAM
COLUMN = ConcreteCoverMemberClass.COLUMN

ALL_BUNDLE_RULE_IDS: List[str] = [
    "BG-DETAIL-BUNDLE-001",
    "BG-DETAIL-BUNDLE-002",
    "BG-DETAIL-BUNDLE-003",
    "BG-DETAIL-BUNDLE-004",
    "BG-DETAIL-BUNDLE-005",
    "BG-DETAIL-BUNDLE-006",
    "BG-DETAIL-BUNDLE-007",
    "BG-DETAIL-BUNDLE-008",
]


def _geometry() -> BeamGeometry:
    return BeamGeometry(bw_mm=300.0, h_mm=600.0, d_effective_mm=550.0)


# ---------------------------------------------------------------------------
# Registry metadata — all eight bundle rules
# ---------------------------------------------------------------------------


def test_bundle_registry_metadata_verified() -> None:
    """All eight: VERIFIED CODE_RULE, execution_allowed=True, pages recorded."""
    rules = (
        RULE_BG_DETAIL_BUNDLE_001,
        RULE_BG_DETAIL_BUNDLE_002,
        RULE_BG_DETAIL_BUNDLE_003,
        RULE_BG_DETAIL_BUNDLE_004,
        RULE_BG_DETAIL_BUNDLE_005,
        RULE_BG_DETAIL_BUNDLE_006,
        RULE_BG_DETAIL_BUNDLE_007,
        RULE_BG_DETAIL_BUNDLE_008,
    )
    assert [r.rule_id for r in rules] == ALL_BUNDLE_RULE_IDS
    for rule in rules:
        assert rule.status == VerificationStatus.VERIFIED, rule.rule_id
        assert rule.category.value == "CODE_RULE", rule.rule_id
        assert rule.execution_allowed is True, rule.rule_id
        assert "9-21-5-" in rule.clause_or_equation, rule.rule_id
    assert RULE_BG_DETAIL_BUNDLE_001.pdf_page == 462
    assert RULE_BG_DETAIL_BUNDLE_001.printed_page == 441
    for rule in rules[1:]:
        assert rule.pdf_page == 463, rule.rule_id
        assert rule.printed_page == 442, rule.rule_id


def test_bundle_multiplier_table_constants() -> None:
    """Constants exactly match the visually verified source values."""
    assert BG_DETAIL_BUNDLE_001_MAX_BARS == 4
    assert BG_DETAIL_BUNDLE_002_COMPRESSED_MIN_TRANSVERSE_DIAMETER_MM == 12.0
    assert BG_DETAIL_BUNDLE_003_BEAM_MAX_BUNDLED_DB_MM == 34.0
    assert BG_DETAIL_BUNDLE_004_CUTOFF_STAGGER_FACTOR == 40
    assert BG_DETAIL_BUNDLE_005_MAX_BARS_PER_PLANE == 2
    assert BG_DETAIL_BUNDLE_007_LD_MULTIPLIERS == {2: 1.00, 3: 1.20, 4: 1.33}


def test_bundle_gatekeeper_allows_verified_rules() -> None:
    """Gatekeeper permits all eight bundle rules under Mabhas 9 compliance."""
    for rule_id in ALL_BUNDLE_RULE_IDS:
        decision = evaluate_rule_gate(rule_id)
        assert decision.allowed is True, rule_id


def test_bundle_jurisdiction_isolation() -> None:
    """Non-Mabhas jurisdiction mode deterministically blocks every rule."""
    for rule_id in ALL_BUNDLE_RULE_IDS:
        decision = evaluate_rule_gate(
            rule_id,
            active_jurisdiction=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
        )
        assert decision.allowed is False, rule_id


# ---------------------------------------------------------------------------
# BG-DETAIL-BUNDLE-001 — Clause 9-21-5-1 (maximum bundle size)
# ---------------------------------------------------------------------------


def test_bundle_count_within_limit_pass() -> None:
    """n in {2, 3, 4} -> PASS per Clause 9-21-5-1."""
    for n in (2, 3, 4):
        step = evaluate_bundle_bar_count(bundle_n_bars=n)
        assert step.outcome == EvaluationOutcome.PASS, n
        assert step.rule_id == "BG-DETAIL-BUNDLE-001"
        assert step.final_result == float(n)


def test_bundle_count_exceeds_maximum_fail() -> None:
    """n > 4 -> FAIL (BUNDLE_BAR_COUNT_EXCEEDS_MAXIMUM), never PASS."""
    for n in (5, 6, 20):
        step = evaluate_bundle_bar_count(bundle_n_bars=n)
        assert step.outcome == EvaluationOutcome.FAIL, n
        assert step.diagnostics[0].code == "BUNDLE_BAR_COUNT_EXCEEDS_MAXIMUM"
        assert step.diagnostics[0].severity == DiagnosticSeverity.ERROR


def test_bundle_count_single_bar_not_applicable() -> None:
    """A single bar is not a bundle -> NOT_APPLICABLE."""
    step = evaluate_bundle_bar_count(bundle_n_bars=1)
    assert step.outcome == EvaluationOutcome.NOT_APPLICABLE


def test_bundle_count_missing_blocked() -> None:
    """Missing bundle count -> BLOCKED (MISSING_BUNDLE_BAR_COUNT)."""
    step = evaluate_bundle_bar_count(bundle_n_bars=None)
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "MISSING_BUNDLE_BAR_COUNT"
    assert step.diagnostics[0].severity == DiagnosticSeverity.BLOCK


def test_bundle_count_malformed_invalid() -> None:
    """Malformed counts (bool / float / < 1) -> INVALID_INPUT."""
    for bad in (True, 2.5, 0, -3):
        step = evaluate_bundle_bar_count(bundle_n_bars=bad)  # type: ignore[arg-type]
        assert step.outcome == EvaluationOutcome.INVALID_INPUT, bad
        assert step.diagnostics[0].code == "INVALID_BUNDLE_BAR_COUNT"


def test_bundle_count_above_max_not_applicable_in_satellite_rules() -> None:
    """n > 4 is owned by 9-21-5-1; satellite bundle rules defer to it."""
    step = evaluate_bundle_plane_arrangement(
        bundle_n_bars=5,
        bundle_max_bars_in_single_plane=2,
        bundle_is_splice_location=False,
    )
    assert step.outcome == EvaluationOutcome.NOT_APPLICABLE


# ---------------------------------------------------------------------------
# BG-DETAIL-BUNDLE-002 — Clause 9-21-5-2 (transverse enclosure)
# ---------------------------------------------------------------------------


def test_transverse_enclosure_missing_fail() -> None:
    """Unenclosed bundle -> FAIL (BUNDLE_TRANSVERSE_ENCLOSURE_MISSING)."""
    step = evaluate_bundle_transverse_reinforcement(
        bundle_n_bars=3,
        bundle_has_transverse_enclosure=False,
        bundle_is_compressed=False,
    )
    assert step.outcome == EvaluationOutcome.FAIL
    assert step.diagnostics[0].code == "BUNDLE_TRANSVERSE_ENCLOSURE_MISSING"


def test_transverse_enclosed_not_compressed_pass() -> None:
    """Enclosed non-compressed bundle -> PASS."""
    step = evaluate_bundle_transverse_reinforcement(
        bundle_n_bars=2,
        bundle_has_transverse_enclosure=True,
        bundle_is_compressed=False,
    )
    assert step.outcome == EvaluationOutcome.PASS


def test_compressed_bundle_dbt_below_12_fail() -> None:
    """Compressed bundle with dbt < 12 mm -> FAIL."""
    step = evaluate_bundle_transverse_reinforcement(
        bundle_n_bars=4,
        bundle_has_transverse_enclosure=True,
        bundle_is_compressed=True,
        transverse_bar_diameter_mm=10.0,
    )
    assert step.outcome == EvaluationOutcome.FAIL
    assert (
        step.diagnostics[0].code
        == "BUNDLE_COMPRESSED_TRANSVERSE_DIAMETER_BELOW_MINIMUM"
    )


def test_compressed_bundle_dbt_at_and_above_12_pass() -> None:
    """Compressed bundle with dbt >= 12 mm -> PASS (boundary inclusive)."""
    for dbt in (12.0, 16.0):
        step = evaluate_bundle_transverse_reinforcement(
            bundle_n_bars=4,
            bundle_has_transverse_enclosure=True,
            bundle_is_compressed=True,
            transverse_bar_diameter_mm=dbt,
        )
        assert step.outcome == EvaluationOutcome.PASS, dbt


def test_transverse_missing_inputs_blocked() -> None:
    """Missing enclosure/compression/compressed-dbt -> BLOCKED, never assumed."""
    step = evaluate_bundle_transverse_reinforcement(
        bundle_n_bars=3, bundle_is_compressed=False
    )
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "MISSING_TRANSVERSE_ENCLOSURE"

    step = evaluate_bundle_transverse_reinforcement(
        bundle_n_bars=3, bundle_has_transverse_enclosure=True
    )
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "MISSING_COMPRESSION_STATE"

    step = evaluate_bundle_transverse_reinforcement(
        bundle_n_bars=3,
        bundle_has_transverse_enclosure=True,
        bundle_is_compressed=True,
    )
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "MISSING_TRANSVERSE_BAR_DIAMETER"


def test_transverse_malformed_inputs_invalid() -> None:
    """Malformed bool flags or non-positive dbt -> INVALID_INPUT."""
    step = evaluate_bundle_transverse_reinforcement(
        bundle_n_bars=3,
        bundle_has_transverse_enclosure="yes",  # type: ignore[arg-type]
        bundle_is_compressed=False,
    )
    assert step.outcome == EvaluationOutcome.INVALID_INPUT

    step = evaluate_bundle_transverse_reinforcement(
        bundle_n_bars=3,
        bundle_has_transverse_enclosure=True,
        bundle_is_compressed=True,
        transverse_bar_diameter_mm=-5.0,
    )
    assert step.outcome == EvaluationOutcome.INVALID_INPUT


# ---------------------------------------------------------------------------
# BG-DETAIL-BUNDLE-003 — Clause 9-21-5-3 (beam db > 34 mm prohibition)
# ---------------------------------------------------------------------------


def test_beam_bundle_db_above_34_fail() -> None:
    """Bundled beam bar db > 34 mm -> FAIL."""
    for db in (34.5, 36.0, 40.0):
        step = evaluate_bundle_beam_bar_diameter(
            bundle_n_bars=3, member_class=BEAM, bundle_bar_diameter_mm=db
        )
        assert step.outcome == EvaluationOutcome.FAIL, db
        assert step.diagnostics[0].code == "BUNDLE_BEAM_BAR_DIAMETER_EXCEEDS_MAXIMUM"


def test_beam_bundle_db_at_or_below_34_pass() -> None:
    """Bundled beam bar db <= 34 mm -> PASS (34 mm boundary inclusive)."""
    for db in (20.0, 34.0):
        step = evaluate_bundle_beam_bar_diameter(
            bundle_n_bars=3, member_class=BEAM, bundle_bar_diameter_mm=db
        )
        assert step.outcome == EvaluationOutcome.PASS, db


def test_non_beam_member_not_applicable() -> None:
    """Clause 9-21-5-3 is beam-specific; other members -> NOT_APPLICABLE."""
    step = evaluate_bundle_beam_bar_diameter(
        bundle_n_bars=3, member_class=COLUMN, bundle_bar_diameter_mm=40.0
    )
    assert step.outcome == EvaluationOutcome.NOT_APPLICABLE


def test_beam_bundle_member_or_db_missing_blocked() -> None:
    """Missing member class or diameter -> BLOCKED, never assumed."""
    step = evaluate_bundle_beam_bar_diameter(
        bundle_n_bars=3, bundle_bar_diameter_mm=40.0
    )
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "MISSING_MEMBER_CLASS"

    step = evaluate_bundle_beam_bar_diameter(
        bundle_n_bars=3, member_class=BEAM, bundle_bar_diameter_mm=None
    )
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "MISSING_GOVERNING_BAR_DIAMETER"


def test_beam_bundle_malformed_inputs_invalid() -> None:
    """Unknown member class / malformed diameter -> INVALID_INPUT."""
    step = evaluate_bundle_beam_bar_diameter(
        bundle_n_bars=3,
        member_class="beam",  # type: ignore[arg-type]
        bundle_bar_diameter_mm=20.0,
    )
    assert step.outcome == EvaluationOutcome.INVALID_INPUT
    assert step.diagnostics[0].code == "UNKNOWN_MEMBER_CLASS"

    step = evaluate_bundle_beam_bar_diameter(
        bundle_n_bars=3, member_class=BEAM, bundle_bar_diameter_mm=float("nan")
    )
    assert step.outcome == EvaluationOutcome.INVALID_INPUT


# ---------------------------------------------------------------------------
# BG-DETAIL-BUNDLE-004 — Clause 9-21-5-4 (40*db cutoff staggering)
# ---------------------------------------------------------------------------


def test_cutoff_stagger_40db_pass() -> None:
    """Cutoffs staggered by >= 40*db -> PASS."""
    step = evaluate_bundle_cutoff_stagger(
        bundle_n_bars=3,
        bundle_has_cutoffs=True,
        bundle_bar_diameter_mm=16.0,
        bundle_cutoff_positions_mm=[0.0, 640.0, 1320.0],
    )
    assert step.outcome == EvaluationOutcome.PASS
    assert step.intermediate_values["stagger_required_mm"] == 40.0 * 16.0


def test_cutoff_stagger_below_40db_fail() -> None:
    """Any pair closer than 40*db -> FAIL."""
    step = evaluate_bundle_cutoff_stagger(
        bundle_n_bars=3,
        bundle_has_cutoffs=True,
        bundle_bar_diameter_mm=16.0,
        bundle_cutoff_positions_mm=[0.0, 500.0],
    )
    assert step.outcome == EvaluationOutcome.FAIL
    assert step.diagnostics[0].code == "BUNDLE_CUTOFF_STAGGER_BELOW_MINIMUM"
    assert step.intermediate_values["min_cutoff_pair_distance_mm"] == 500.0


def test_cutoff_unsorted_positions_handled() -> None:
    """Unsorted cutoff positions are ordered deterministically."""
    step = evaluate_bundle_cutoff_stagger(
        bundle_n_bars=3,
        bundle_has_cutoffs=True,
        bundle_bar_diameter_mm=16.0,
        bundle_cutoff_positions_mm=[1320.0, 0.0, 640.0],
    )
    assert step.outcome == EvaluationOutcome.PASS


def test_no_cutoffs_not_applicable() -> None:
    """No bar of the bundle is cut off -> NOT_APPLICABLE."""
    step = evaluate_bundle_cutoff_stagger(
        bundle_n_bars=3, bundle_has_cutoffs=False
    )
    assert step.outcome == EvaluationOutcome.NOT_APPLICABLE


def test_single_cut_bar_not_applicable() -> None:
    """Fewer than two cut bars -> no pair to stagger -> NOT_APPLICABLE."""
    step = evaluate_bundle_cutoff_stagger(
        bundle_n_bars=3,
        bundle_has_cutoffs=True,
        bundle_bar_diameter_mm=16.0,
        bundle_cutoff_positions_mm=[400.0],
    )
    assert step.outcome == EvaluationOutcome.NOT_APPLICABLE


def test_cutoff_missing_inputs_blocked() -> None:
    """Missing cutoff flag / diameter / positions -> BLOCKED, never assumed."""
    step = evaluate_bundle_cutoff_stagger(bundle_n_bars=3)
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "MISSING_CUTOFF_CONFIGURATION"

    step = evaluate_bundle_cutoff_stagger(
        bundle_n_bars=3,
        bundle_has_cutoffs=True,
        bundle_cutoff_positions_mm=[0.0, 800.0],
    )
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "MISSING_GOVERNING_BAR_DIAMETER"

    step = evaluate_bundle_cutoff_stagger(
        bundle_n_bars=3, bundle_has_cutoffs=True, bundle_bar_diameter_mm=16.0
    )
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "MISSING_BUNDLE_CUTOFF_POSITIONS"


def test_cutoff_malformed_inputs_invalid() -> None:
    """Malformed flag / diameter / NaN position -> INVALID_INPUT."""
    step = evaluate_bundle_cutoff_stagger(
        bundle_n_bars=3, bundle_has_cutoffs="yes"  # type: ignore[arg-type]
    )
    assert step.outcome == EvaluationOutcome.INVALID_INPUT

    step = evaluate_bundle_cutoff_stagger(
        bundle_n_bars=3,
        bundle_has_cutoffs=True,
        bundle_bar_diameter_mm=0.0,
        bundle_cutoff_positions_mm=[0.0, 800.0],
    )
    assert step.outcome == EvaluationOutcome.INVALID_INPUT

    step = evaluate_bundle_cutoff_stagger(
        bundle_n_bars=3,
        bundle_has_cutoffs=True,
        bundle_bar_diameter_mm=16.0,
        bundle_cutoff_positions_mm=[0.0, float("nan")],
    )
    assert step.outcome == EvaluationOutcome.INVALID_INPUT
    assert step.diagnostics[0].code == "INVALID_BUNDLE_CUTOFF_POSITIONS"


# ---------------------------------------------------------------------------
# BG-DETAIL-BUNDLE-005 — Clause 9-21-5-5 (plane arrangement)
# ---------------------------------------------------------------------------


def test_plane_arrangement_within_limit_pass() -> None:
    """>2-bar bundle with at most 2 bars per plane -> PASS."""
    step = evaluate_bundle_plane_arrangement(
        bundle_n_bars=4,
        bundle_max_bars_in_single_plane=2,
        bundle_is_splice_location=False,
    )
    assert step.outcome == EvaluationOutcome.PASS


def test_plane_arrangement_all_in_one_plane_fail() -> None:
    """>2 bars in one plane outside a splice -> FAIL."""
    step = evaluate_bundle_plane_arrangement(
        bundle_n_bars=3,
        bundle_max_bars_in_single_plane=3,
        bundle_is_splice_location=False,
    )
    assert step.outcome == EvaluationOutcome.FAIL
    assert step.diagnostics[0].code == "BUNDLE_BARS_PER_PLANE_EXCEEDED"


def test_plane_arrangement_splice_exception_pass() -> None:
    """All bars coplanar AT a splice location -> PASS (clause exception)."""
    step = evaluate_bundle_plane_arrangement(
        bundle_n_bars=3,
        bundle_max_bars_in_single_plane=3,
        bundle_is_splice_location=True,
    )
    assert step.outcome == EvaluationOutcome.PASS
    assert "splice" in (step.message or "").lower()


def test_plane_arrangement_two_bar_bundle_not_applicable() -> None:
    """Bundles of two bars are outside Clause 9-21-5-5 -> NOT_APPLICABLE."""
    step = evaluate_bundle_plane_arrangement(
        bundle_n_bars=2,
        bundle_max_bars_in_single_plane=2,
        bundle_is_splice_location=False,
    )
    assert step.outcome == EvaluationOutcome.NOT_APPLICABLE


def test_plane_arrangement_missing_inputs_blocked() -> None:
    """Missing arrangement or splice status -> BLOCKED, never assumed."""
    step = evaluate_bundle_plane_arrangement(
        bundle_n_bars=3, bundle_is_splice_location=False
    )
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "MISSING_BUNDLE_PLANE_ARRANGEMENT"

    step = evaluate_bundle_plane_arrangement(
        bundle_n_bars=3, bundle_max_bars_in_single_plane=2
    )
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "MISSING_SPLICE_LOCATION_STATUS"


def test_plane_arrangement_malformed_inputs_invalid() -> None:
    """Impossible plane count / non-bool splice flag -> INVALID_INPUT."""
    step = evaluate_bundle_plane_arrangement(
        bundle_n_bars=3,
        bundle_max_bars_in_single_plane=5,  # more bars than the bundle
        bundle_is_splice_location=False,
    )
    assert step.outcome == EvaluationOutcome.INVALID_INPUT
    assert step.diagnostics[0].code == "INVALID_BUNDLE_PLANE_ARRANGEMENT"

    step = evaluate_bundle_plane_arrangement(
        bundle_n_bars=3,
        bundle_max_bars_in_single_plane=2,
        bundle_is_splice_location=1,  # type: ignore[arg-type]
    )
    assert step.outcome == EvaluationOutcome.INVALID_INPUT
    assert step.diagnostics[0].code == "INVALID_SPLICE_LOCATION_STATUS"


# ---------------------------------------------------------------------------
# BG-DETAIL-BUNDLE-006 — Clause 9-21-5-6 (equivalent diameter)
# ---------------------------------------------------------------------------


def test_equivalent_diameter_two_three_four_bars() -> None:
    """d_eq = db*sqrt(n) exactly for n in {2, 3, 4}; equal-area check holds."""
    db = 20.0
    for n in (2, 3, 4):
        step = evaluate_bundle_equivalent_diameter(
            bundle_n_bars=n, bundle_bar_diameter_mm=db, bundle_bars_identical=True
        )
        assert step.outcome == EvaluationOutcome.COMPUTED, n
        assert step.final_result == db * math.sqrt(n)
        total = step.intermediate_values["total_bundle_area_mm2"]
        equiv = step.intermediate_values["equivalent_bar_area_mm2"]
        assert math.isclose(total, equiv, rel_tol=1e-12), n


def test_equivalent_diameter_exact_boundaries() -> None:
    """Exact values: d_eq(2, 16) = 16*sqrt(2); d_eq(4, 25) = 50.0."""
    step = evaluate_bundle_equivalent_diameter(
        bundle_n_bars=4, bundle_bar_diameter_mm=25.0, bundle_bars_identical=True
    )
    assert step.final_result == 50.0
    step = evaluate_bundle_equivalent_diameter(
        bundle_n_bars=2, bundle_bar_diameter_mm=16.0, bundle_bars_identical=True
    )
    assert step.final_result == 16.0 * math.sqrt(2.0)


def test_equivalent_diameter_mixed_bars_blocked() -> None:
    """Mixed-diameter bundles -> BLOCKED (UNSUPPORTED_CONFIGURATION)."""
    step = evaluate_bundle_equivalent_diameter(
        bundle_n_bars=2, bundle_bar_diameter_mm=20.0, bundle_bars_identical=False
    )
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "UNSUPPORTED_CONFIGURATION"
    assert step.diagnostics[0].severity == DiagnosticSeverity.BLOCK


def test_equivalent_diameter_missing_inputs_blocked() -> None:
    """Missing identical flag or diameter -> BLOCKED, never assumed."""
    step = evaluate_bundle_equivalent_diameter(
        bundle_n_bars=3, bundle_bar_diameter_mm=20.0
    )
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "MISSING_BUNDLE_BARS_IDENTICAL"

    step = evaluate_bundle_equivalent_diameter(
        bundle_n_bars=3, bundle_bars_identical=True
    )
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "MISSING_GOVERNING_BAR_DIAMETER"


def test_equivalent_diameter_malformed_inputs_invalid() -> None:
    """Malformed identical flag / diameter -> INVALID_INPUT."""
    step = evaluate_bundle_equivalent_diameter(
        bundle_n_bars=3,
        bundle_bar_diameter_mm=20.0,
        bundle_bars_identical="yes",  # type: ignore[arg-type]
    )
    assert step.outcome == EvaluationOutcome.INVALID_INPUT

    step = evaluate_bundle_equivalent_diameter(
        bundle_n_bars=3,
        bundle_bar_diameter_mm=float("inf"),
        bundle_bars_identical=True,
    )
    assert step.outcome == EvaluationOutcome.INVALID_INPUT


# ---------------------------------------------------------------------------
# BG-DETAIL-BUNDLE-007 — Clause 9-21-5-7 (development length multiplier)
# ---------------------------------------------------------------------------


def test_development_multipliers_1_00_1_20_1_33() -> None:
    """ld_bundle = factor * ld_single with the verified multiplier table."""
    ld = 900.0
    expected = {2: 1.00 * ld, 3: 1.20 * ld, 4: 1.33 * ld}
    for n, want in expected.items():
        step = evaluate_bundle_development_length(
            bundle_n_bars=n, single_bar_development_length_mm=ld
        )
        assert step.outcome == EvaluationOutcome.COMPUTED, n
        assert step.final_result == want, n
        assert (
            step.intermediate_values["bundle_development_length_factor"]
            == BG_DETAIL_BUNDLE_007_LD_MULTIPLIERS[n]
        )


def test_development_missing_single_bar_ld_blocked() -> None:
    """Missing verified single-bar ld -> BLOCKED; Clause 9-21-3 never computed."""
    step = evaluate_bundle_development_length(bundle_n_bars=3)
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "MISSING_SINGLE_BAR_DEVELOPMENT_LENGTH"
    req = step.diagnostics[0].required_verification
    assert req is not None and "9-21-3" in req


def test_development_malformed_ld_invalid() -> None:
    """Non-finite or non-positive single-bar ld -> INVALID_INPUT."""
    for bad in (0.0, -100.0, float("nan")):
        step = evaluate_bundle_development_length(
            bundle_n_bars=3, single_bar_development_length_mm=bad
        )
        assert step.outcome == EvaluationOutcome.INVALID_INPUT, bad


# ---------------------------------------------------------------------------
# BG-DETAIL-BUNDLE-008 — Clause 9-21-5-8 (lap splice constraints)
# ---------------------------------------------------------------------------


def test_lap_splice_computed_per_bar_lap() -> None:
    """Per-bar lap = single-bar ld * 9-21-5-7 multiplier -> COMPUTED."""
    step = evaluate_bundle_lap_splice(
        bundle_n_bars=4,
        single_bar_development_length_mm=800.0,
        bundle_is_bundle_to_bundle_lap=False,
        bundle_laps_overlap=False,
    )
    assert step.outcome == EvaluationOutcome.COMPUTED
    assert step.final_result == 1.33 * 800.0
    assert step.intermediate_values["bundle_lap_splice_factor"] == 1.33

    step = evaluate_bundle_lap_splice(
        bundle_n_bars=2,
        single_bar_development_length_mm=800.0,
        bundle_is_bundle_to_bundle_lap=False,
        bundle_laps_overlap=False,
    )
    assert step.outcome == EvaluationOutcome.COMPUTED
    assert step.final_result == 800.0  # 2-bar multiplier 1.00


def test_bundle_to_bundle_lap_prohibited_fail() -> None:
    """Bundle-to-bundle lap splice -> FAIL (prohibited)."""
    step = evaluate_bundle_lap_splice(
        bundle_n_bars=3,
        single_bar_development_length_mm=800.0,
        bundle_is_bundle_to_bundle_lap=True,
        bundle_laps_overlap=False,
    )
    assert step.outcome == EvaluationOutcome.FAIL
    assert step.diagnostics[0].code == "BUNDLE_TO_BUNDLE_LAP_SPLICE_PROHIBITED"


def test_overlapping_individual_laps_fail() -> None:
    """Overlapping individual laps within a bundle -> FAIL."""
    step = evaluate_bundle_lap_splice(
        bundle_n_bars=3,
        single_bar_development_length_mm=800.0,
        bundle_is_bundle_to_bundle_lap=False,
        bundle_laps_overlap=True,
    )
    assert step.outcome == EvaluationOutcome.FAIL
    assert step.diagnostics[0].code == "BUNDLE_INDIVIDUAL_LAPS_OVERLAP_PROHIBITED"


def test_lap_splice_missing_dependencies_blocked() -> None:
    """Missing ld / lap type / overlap status -> BLOCKED, never invented."""
    step = evaluate_bundle_lap_splice(
        bundle_n_bars=3,
        bundle_is_bundle_to_bundle_lap=False,
        bundle_laps_overlap=False,
    )
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "MISSING_SINGLE_BAR_DEVELOPMENT_LENGTH"
    req = step.diagnostics[0].required_verification
    assert req is not None and "9-21-4" in req

    step = evaluate_bundle_lap_splice(
        bundle_n_bars=3,
        single_bar_development_length_mm=800.0,
        bundle_laps_overlap=False,
    )
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "MISSING_BUNDLE_LAP_TYPE"

    step = evaluate_bundle_lap_splice(
        bundle_n_bars=3,
        single_bar_development_length_mm=800.0,
        bundle_is_bundle_to_bundle_lap=False,
    )
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step.diagnostics[0].code == "MISSING_BUNDLE_LAP_OVERLAP_STATUS"


def test_lap_splice_malformed_inputs_invalid() -> None:
    """Malformed ld / bool flags -> INVALID_INPUT."""
    step = evaluate_bundle_lap_splice(
        bundle_n_bars=3,
        single_bar_development_length_mm=-5.0,
        bundle_is_bundle_to_bundle_lap=False,
        bundle_laps_overlap=False,
    )
    assert step.outcome == EvaluationOutcome.INVALID_INPUT

    step = evaluate_bundle_lap_splice(
        bundle_n_bars=3,
        single_bar_development_length_mm=800.0,
        bundle_is_bundle_to_bundle_lap="no",  # type: ignore[arg-type]
        bundle_laps_overlap=False,
    )
    assert step.outcome == EvaluationOutcome.INVALID_INPUT
    assert step.diagnostics[0].code == "INVALID_BUNDLE_LAP_TYPE"


def test_lap_splice_all_satellite_rules_single_bar_not_applicable() -> None:
    """n == 1 (single bar) -> NOT_APPLICABLE in every bundle rule."""
    outcomes = [
        evaluate_bundle_bar_count(bundle_n_bars=1),
        evaluate_bundle_transverse_reinforcement(
            bundle_n_bars=1,
            bundle_has_transverse_enclosure=True,
            bundle_is_compressed=False,
        ),
        evaluate_bundle_beam_bar_diameter(
            bundle_n_bars=1, member_class=BEAM, bundle_bar_diameter_mm=40.0
        ),
        evaluate_bundle_cutoff_stagger(bundle_n_bars=1, bundle_has_cutoffs=True),
        evaluate_bundle_plane_arrangement(
            bundle_n_bars=1,
            bundle_max_bars_in_single_plane=1,
            bundle_is_splice_location=False,
        ),
        evaluate_bundle_equivalent_diameter(
            bundle_n_bars=1, bundle_bar_diameter_mm=20.0, bundle_bars_identical=True
        ),
        evaluate_bundle_development_length(
            bundle_n_bars=1, single_bar_development_length_mm=800.0
        ),
        evaluate_bundle_lap_splice(
            bundle_n_bars=1,
            single_bar_development_length_mm=800.0,
            bundle_is_bundle_to_bundle_lap=False,
            bundle_laps_overlap=False,
        ),
    ]
    for step in outcomes:
        assert step.outcome == EvaluationOutcome.NOT_APPLICABLE, step.rule_id
        assert step.rule_id.startswith("BG-DETAIL-BUNDLE-00")


# ---------------------------------------------------------------------------
# Orchestrator & workflow wiring
# ---------------------------------------------------------------------------


def test_run_mabhas9_beam_check_dispatches_bundle_rules() -> None:
    """run_mabhas9_beam_check routes bundle rule ids to the verified evaluators."""
    geometry = _geometry()
    from beamgenius.domain import ConcreteMaterial, RebarMaterial

    concrete = ConcreteMaterial(fc_prime_mpa=30.0)
    rebar = RebarMaterial(fy_mpa=400.0)
    report = run_mabhas9_beam_check(
        geometry,
        concrete,
        rebar,
        bundle_n_bars=3,
        bundle_member_class=BEAM,
        bundle_bar_diameter_mm=20.0,
        bundle_has_transverse_enclosure=True,
        bundle_is_compressed=False,
        bundle_max_bars_in_single_plane=2,
        bundle_is_splice_location=False,
        bundle_has_cutoffs=False,
        bundle_bars_identical=True,
        single_bar_development_length_mm=900.0,
        bundle_is_bundle_to_bundle_lap=False,
        bundle_laps_overlap=False,
        requested_rule_ids=ALL_BUNDLE_RULE_IDS,
    )
    bundles = [
        s
        for s in report.trace_steps
        if s.rule_id.startswith("BG-DETAIL-BUNDLE-")
    ]
    assert len(bundles) == 8
    outcomes = {s.rule_id: s.outcome for s in bundles}
    assert outcomes["BG-DETAIL-BUNDLE-001"] == EvaluationOutcome.PASS
    assert outcomes["BG-DETAIL-BUNDLE-002"] == EvaluationOutcome.PASS
    assert outcomes["BG-DETAIL-BUNDLE-003"] == EvaluationOutcome.PASS
    assert outcomes["BG-DETAIL-BUNDLE-004"] == EvaluationOutcome.NOT_APPLICABLE
    assert outcomes["BG-DETAIL-BUNDLE-005"] == EvaluationOutcome.PASS
    assert outcomes["BG-DETAIL-BUNDLE-006"] == EvaluationOutcome.COMPUTED
    assert outcomes["BG-DETAIL-BUNDLE-007"] == EvaluationOutcome.COMPUTED
    assert outcomes["BG-DETAIL-BUNDLE-008"] == EvaluationOutcome.COMPUTED


def test_run_mabhas9_beam_check_bundle_fail_dominates() -> None:
    """A FAIL bundle rule propagates to the aggregated overall status."""
    from beamgenius.domain import ConcreteMaterial, RebarMaterial

    geometry = _geometry()
    concrete = ConcreteMaterial(fc_prime_mpa=30.0)
    rebar = RebarMaterial(fy_mpa=400.0)
    report = run_mabhas9_beam_check(
        geometry,
        concrete,
        rebar,
        bundle_n_bars=5,
        requested_rule_ids=["BG-DETAIL-BUNDLE-001"],
    )
    assert report.overall_status == OverallComplianceStatus.FAIL


def test_run_mabhas9_beam_check_bundle_blocked_never_pass() -> None:
    """Missing bundle inputs -> BLOCKED steps; overall status never PASS."""
    from beamgenius.domain import ConcreteMaterial, RebarMaterial

    geometry = _geometry()
    concrete = ConcreteMaterial(fc_prime_mpa=30.0)
    rebar = RebarMaterial(fy_mpa=400.0)
    report = run_mabhas9_beam_check(
        geometry,
        concrete,
        rebar,
        requested_rule_ids=["BG-DETAIL-BUNDLE-007"],
    )
    assert report.overall_status == OverallComplianceStatus.BLOCKED


def test_detailing_workflow_bundle_chain() -> None:
    """Workflow appends the eight bundle steps when bundle_n_bars is given."""
    geometry = _geometry()
    steps = run_mabhas9_beam_detailing_workflow(
        geometry,
        max_longitudinal_bar_diameter_mm=20.0,
        transverse_bar_diameter_mm=10.0,
        bundle_n_bars=3,
        bundle_member_class=BEAM,
        bundle_bar_diameter_mm=20.0,
        bundle_has_transverse_enclosure=True,
        bundle_is_compressed=False,
        bundle_max_bars_in_single_plane=2,
        bundle_is_splice_location=False,
        bundle_has_cutoffs=False,
        bundle_bars_identical=True,
        single_bar_development_length_mm=900.0,
        bundle_is_bundle_to_bundle_lap=False,
        bundle_laps_overlap=False,
    )
    bundle_steps = [s for s in steps if s.rule_id.startswith("BG-DETAIL-BUNDLE-")]
    assert [s.rule_id for s in bundle_steps] == ALL_BUNDLE_RULE_IDS
    report = aggregate_compliance_report(steps)
    assert report.overall_status == OverallComplianceStatus.PARTIAL


def test_detailing_workflow_without_bundle_inputs_unchanged() -> None:
    """No bundle inputs -> no bundle steps (Phase 2D/2E behavior preserved)."""
    geometry = _geometry()
    steps = run_mabhas9_beam_detailing_workflow(
        geometry,
        max_longitudinal_bar_diameter_mm=20.0,
        transverse_bar_diameter_mm=10.0,
    )
    assert all(
        not s.rule_id.startswith("BG-DETAIL-BUNDLE-") for s in steps
    )


# ---------------------------------------------------------------------------
# Engine-reference isolation: no imports from the isolated reference package
# ---------------------------------------------------------------------------


def test_phase2f_engine_modules_have_no_reference_imports() -> None:
    """The verified engine must stay isolated from the Mostofinejad reference."""
    engine_dir = (
        Path(__file__).resolve().parents[1] / "src" / "beamgenius" / "engine"
    )
    module_files = [
        engine_dir / "detailing_bundle_mabhas9.py",
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
