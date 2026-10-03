"""Mabhas 9 (1399) verified beam detailing evaluators (Phase 2D & Phase 2E).

Verified production rules (Phase 2D):
- ``BG-DETAIL-TRANS-DIA-001``: minimum transverse reinforcement diameter
  enclosing longitudinal bars (Mabhas 9 Clause 9-11-6-5-11, PDF p. 228)
- ``BG-DETAIL-COMP-LAT-001``: compression reinforcement lateral support
  spacing (Mabhas 9 Clause 9-11-6-5-12, PDF p. 229)

Verified production rules (Phase 2E Stage B, visually verified 2026-10-03):
- ``BG-DETAIL-SPACING-001``: minimum clear spacing of parallel longitudinal
  bars in one horizontal layer (Mabhas 9 Clause 9-21-2-1-1, PDF p. 441 /
  Printed p. 420)
- ``BG-DETAIL-LAYER-SPACING-001``: vertical alignment and minimum clear
  spacing between reinforcement layers (Mabhas 9 Clause 9-21-2-1-2, PDF
  p. 441 / Printed p. 420)
- ``BG-DETAIL-COVER-001``: minimum concrete cover over beam reinforcement
  under normal (non-corrosive) conditions (Mabhas 9 Clauses 9-4-9-4,
  9-4-9-5-1..3 + Table 9-4-6, PDF pp. 92-93 / Printed pp. 71-72)

Access note: ``evaluate_minimum_transverse_bar_diameter`` /
``evaluate_longitudinal_bar_clear_spacing`` are the verified production
implementations. The legacy blocked-workflow stubs of the same names for the
un-promoted ``BG-DETAIL-TRANS-DIA-PENDING`` / ``BG-DETAIL-*-BLOCKED``
sentinels remain in ``beamgenius.engine.beam_checker``; import the verified
functions explicitly from this module, e.g.::

    from beamgenius.engine.detailing_mabhas9 import (
        evaluate_minimum_transverse_bar_diameter,
    )

All evaluators deterministically return ``UNVERIFIED_RULE_BLOCKED`` for any
input configuration whose Mabhas 9 requirement is not source-verified (e.g.
the non-interpolated ``32 < db < 36 mm`` interval, bundled-bar equivalent
diameters (Clause 9-21-5-6 pending), or corrosive exposure routed to
Appendix 9-پ1), deterministically return ``INVALID_INPUT`` for missing or
malformed required inputs (never a silent default), and never invent values.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional

from beamgenius.domain.enums import (
    ConcreteCoverExposureClass,
    DiagnosticSeverity,
    EvaluationOutcome,
    JurisdictionMode,
)
from beamgenius.domain.models import BeamGeometry
from beamgenius.domain.trace import (
    CalculationTraceStep,
    EngineeringDiagnostic,
    ScalarInputValue,
)
from beamgenius.domain.validation import (
    validate_beam_geometry,
)
from beamgenius.registry.catalog import (
    RULE_BG_DETAIL_COMP_LAT_001,
    RULE_BG_DETAIL_COVER_001,
    RULE_BG_DETAIL_LAYER_SPACING_001,
    RULE_BG_DETAIL_SPACING_001,
    RULE_BG_DETAIL_TRANS_DIA_001,
)
from beamgenius.registry.gatekeeper import evaluate_rule_gate

# Constants tied to BG-DETAIL-TRANS-DIA-001 (Mabhas 9 Clause 9-11-6-5-11)
BG_DETAIL_TRANS_DIA_001_DB_MAX_FOR_10MM: float = 32.0
BG_DETAIL_TRANS_DIA_001_DB_MIN_FOR_12MM: float = 36.0
BG_DETAIL_TRANS_DIA_001_DBT_FOR_SMALL_DB: float = 10.0
BG_DETAIL_TRANS_DIA_001_DBT_FOR_LARGE_OR_BUNDLED_DB: float = 12.0

# Constants tied to BG-DETAIL-COMP-LAT-001 (Mabhas 9 Clause 9-11-6-5-12)
BG_DETAIL_COMP_LAT_001_DB_MULTIPLIER: float = 16.0
BG_DETAIL_COMP_LAT_001_DBT_MULTIPLIER: float = 48.0

# Constants tied to BG-DETAIL-SPACING-001 (Mabhas 9 Clause 9-21-2-1-1,
# PDF p. 441 / Printed p. 420)
BG_DETAIL_SPACING_001_MIN_CLEAR_MM: float = 25.0
BG_DETAIL_SPACING_001_AGGREGATE_FACTOR: float = 4.0 / 3.0

# Constants tied to BG-DETAIL-LAYER-SPACING-001 (Mabhas 9 Clause 9-21-2-1-2,
# PDF p. 441 / Printed p. 420)
BG_DETAIL_LAYER_SPACING_001_MIN_CLEAR_MM: float = 25.0

# Constants tied to BG-DETAIL-COVER-001 (Mabhas 9 Clauses 9-4-9-5-1..3 +
# Table 9-4-6, PDF pp. 92-93 / Printed pp. 71-72)
BG_DETAIL_COVER_001_PERMANENT_EARTH_MM: float = 75.0
BG_DETAIL_COVER_001_WEATHER_DB_18_TO_58_MM: float = 50.0
BG_DETAIL_COVER_001_WEATHER_DB_LE_16_MM: float = 40.0
BG_DETAIL_COVER_001_BEAM_NOT_EXPOSED_MM: float = 40.0
BG_DETAIL_COVER_001_WEATHER_MAX_SMALL_DB_MM: float = 16.0
BG_DETAIL_COVER_001_WEATHER_MIN_LARGE_DB_MM: float = 18.0
BG_DETAIL_COVER_001_WEATHER_MAX_LARGE_DB_MM: float = 58.0


def _validate_diameter(
    value_mm: float,
    *,
    field_name: str,
    rule_id: str,
) -> EngineeringDiagnostic:
    """Return an ERROR diagnostic for a non-finite or non-positive diameter."""
    return EngineeringDiagnostic(
        code=(
            "INVALID_BAR_DIAMETER_"
            + field_name.upper().replace(" ", "_")
        ),
        severity=DiagnosticSeverity.ERROR,
        message=(
            f"{field_name} must be finite and > 0 mm, got {value_mm} mm."
        ),
        rule_id=rule_id,
        field_name=field_name,
    )


def _validate_positive_finite(
    value: float,
    *,
    field_name: str,
    rule_id: str,
) -> EngineeringDiagnostic:
    """Return an ERROR diagnostic for a non-finite or non-positive scalar (mm)."""
    return EngineeringDiagnostic(
        code="INVALID_" + field_name.upper().replace(" ", "_"),
        severity=DiagnosticSeverity.ERROR,
        message=(
            f"{field_name} must be finite and > 0 mm, got {value} mm."
        ),
        rule_id=rule_id,
        field_name=field_name,
    )


def evaluate_minimum_transverse_bar_diameter(
    geometry: BeamGeometry,
    *,
    max_longitudinal_bar_diameter_mm: Optional[float] = None,
    is_bundled: bool = False,
    transverse_bar_diameter_mm: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate Mabhas 9 minimum transverse bar diameter (BG-DETAIL-TRANS-DIA-001).

    Verified source: Mabhas 9 (1399), Clause 9-11-6-5-11, PDF p. 228:
    - Longitudinal bar ``db <= 32 mm`` (non-bundled): ``dbt >= 10 mm``
    - Longitudinal bar ``db >= 36 mm`` (non-bundled): ``dbt >= 12 mm``
    - Bundled longitudinal bars (any diameter): ``dbt >= 12 mm``

    The non-bundled interval ``32 < db < 36 mm`` has NO verified interpolation
    and returns ``UNVERIFIED_RULE_BLOCKED`` (UNSUPPORTED_CONFIGURATION).

    db is the governing (largest) longitudinal bar diameter enclosed by the
    transverse reinforcement: supplied explicitly via
    ``max_longitudinal_bar_diameter_mm`` or resolved from
    ``geometry.tension_rebar_groups``.
    """
    rule_id = RULE_BG_DETAIL_TRANS_DIA_001.rule_id

    resolved_db: Optional[float] = max_longitudinal_bar_diameter_mm
    if resolved_db is None and geometry.tension_rebar_groups:
        resolved_db = max(
            group.bar_diameter_mm for group in geometry.tension_rebar_groups
        )

    resolved_dbt: Optional[float] = transverse_bar_diameter_mm
    if resolved_dbt is None:
        resolved_dbt = geometry.stirrup_diameter_mm

    raw_inputs: Dict[str, ScalarInputValue] = {
        "bw_mm": geometry.bw_mm,
        "h_mm": geometry.h_mm,
        "max_longitudinal_bar_diameter_mm": resolved_db,
        "is_bundled": is_bundled,
        "transverse_bar_diameter_mm": resolved_dbt,
    }

    # 1. Central Gatekeeper check
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(
            normalized_inputs=raw_inputs, unit="mm"
        )

    # 2. Deterministic input validation
    diagnostics: List[EngineeringDiagnostic] = []
    diagnostics.extend(
        validate_beam_geometry(
            geometry, require_effective_depth=False, rule_id=rule_id
        )
    )

    if resolved_db is None:
        diagnostics.append(
            EngineeringDiagnostic(
                code="MISSING_LONGITUDINAL_BAR_DIAMETER",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    "Longitudinal bar diameter db is required: supply "
                    "max_longitudinal_bar_diameter_mm or "
                    "geometry.tension_rebar_groups."
                ),
                rule_id=rule_id,
                field_name="max_longitudinal_bar_diameter_mm",
            )
        )
    elif not math.isfinite(resolved_db) or resolved_db <= 0.0:
        diagnostics.append(
            _validate_diameter(
                resolved_db,
                field_name="max_longitudinal_bar_diameter_mm",
                rule_id=rule_id,
            )
        )

    if resolved_dbt is not None and (
        not math.isfinite(resolved_dbt) or resolved_dbt <= 0.0
    ):
        diagnostics.append(
            _validate_diameter(
                resolved_dbt,
                field_name="transverse_bar_diameter_mm",
                rule_id=rule_id,
            )
        )

    if diagnostics:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="mm",
            outcome=EvaluationOutcome.INVALID_INPUT,
            diagnostics=diagnostics,
            message=diagnostics[0].message,
        )

    assert resolved_db is not None  # for type checkers

    # 3. Unsupported interval: 32 < db < 36 for non-bundled bars is blocked
    if not is_bundled and (
        resolved_db > BG_DETAIL_TRANS_DIA_001_DB_MAX_FOR_10MM
        and resolved_db < BG_DETAIL_TRANS_DIA_001_DB_MIN_FOR_12MM
    ):
        interval_diag = EngineeringDiagnostic(
            code="UNSUPPORTED_LONGITUDINAL_DIAMETER_INTERVAL",
            severity=DiagnosticSeverity.BLOCK,
            message=(
                f"Rule '{rule_id}' is blocked: non-bundled longitudinal bar "
                f"diameter db = {resolved_db} mm lies in the interval "
                "(32, 36) mm, for which Mabhas 9 Clause 9-11-6-5-11 has no "
                "verified transverse diameter interpolation. "
                "UNVERIFIED_RULE_BLOCKED (UNSUPPORTED_CONFIGURATION)."
            ),
            rule_id=rule_id,
            field_name="max_longitudinal_bar_diameter_mm",
            required_verification=(
                "Visually verify Mabhas 9 Clause 9-11-6-5-11 guidance for the "
                "32 < db < 36 mm interval before executing."
            ),
        )
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="mm",
            outcome=EvaluationOutcome.UNVERIFIED_RULE_BLOCKED,
            diagnostics=(interval_diag,),
            message=interval_diag.message,
        )

    # 4. Required minimum transverse diameter
    if is_bundled or resolved_db >= BG_DETAIL_TRANS_DIA_001_DB_MIN_FOR_12MM:
        required_dbt_mm = BG_DETAIL_TRANS_DIA_001_DBT_FOR_LARGE_OR_BUNDLED_DB
        governing_basis = "bundled" if is_bundled else "db>=36"
    else:
        required_dbt_mm = BG_DETAIL_TRANS_DIA_001_DBT_FOR_SMALL_DB
        governing_basis = "db<=32"

    intermediates: Dict[str, float] = {
        "db_governing_mm": resolved_db,
        "required_transverse_diameter_mm": required_dbt_mm,
    }

    # 5. Verify provided stirrup diameter when available
    if resolved_dbt is None:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=required_dbt_mm,
            unit="mm",
            outcome=EvaluationOutcome.COMPUTED,
            diagnostics=(),
            message=(
                f"Computed required minimum transverse diameter dbt >= "
                f"{required_dbt_mm} mm ({governing_basis})."
            ),
        )

    intermediates["provided_transverse_diameter_mm"] = resolved_dbt
    if resolved_dbt >= required_dbt_mm:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=required_dbt_mm,
            unit="mm",
            outcome=EvaluationOutcome.PASS,
            diagnostics=(),
            message=(
                f"PASS: provided transverse diameter ({resolved_dbt} mm) >= "
                f"required minimum ({required_dbt_mm} mm) ({governing_basis})."
            ),
        )

    fail_diag = EngineeringDiagnostic(
        code="INSUFFICIENT_TRANSVERSE_BAR_DIAMETER",
        severity=DiagnosticSeverity.ERROR,
        message=(
            f"FAIL: provided transverse diameter ({resolved_dbt} mm) < "
            f"required minimum ({required_dbt_mm} mm) per Clause "
            f"9-11-6-5-11 ({governing_basis})."
        ),
        rule_id=rule_id,
        field_name="transverse_bar_diameter_mm",
    )
    return CalculationTraceStep.from_rule(
        gate.rule,
        normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=required_dbt_mm,
        unit="mm",
        outcome=EvaluationOutcome.FAIL,
        diagnostics=(fail_diag,),
        message=fail_diag.message,
    )


def evaluate_compression_reinforcement_lateral_support_spacing(
    geometry: BeamGeometry,
    *,
    has_compression_reinforcement: bool = False,
    min_compression_bar_diameter_mm: Optional[float] = None,
    transverse_bar_diameter_mm: Optional[float] = None,
    compression_lateral_support_spacing_mm: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate Mabhas 9 compression bar lateral support spacing (BG-DETAIL-COMP-LAT-001).

    Verified source: Mabhas 9 (1399), Clause 9-11-6-5-12, PDF p. 229:

        sc <= min(16 * db, 48 * dbt, b_min)

    where ``db`` is the smallest diameter of longitudinal compression bars,
    ``dbt`` the transverse reinforcement diameter (explicit kwarg or
    ``geometry.stirrup_diameter_mm``), and ``b_min = min(bw, h)`` the least
    section dimension (auto-resolved from ``geometry``).

    When ``has_compression_reinforcement`` is False, or the smallest
    compression bar diameter is unavailable, the rule returns
    ``INVALID_INPUT`` (compression & transverse reinforcement inputs are
    required to execute this verified check). Do NOT model compression bar
    buckling beyond this spacing rule.
    """
    rule_id = RULE_BG_DETAIL_COMP_LAT_001.rule_id

    resolved_dbt: Optional[float] = transverse_bar_diameter_mm
    if resolved_dbt is None:
        resolved_dbt = geometry.stirrup_diameter_mm

    raw_inputs: Dict[str, ScalarInputValue] = {
        "bw_mm": geometry.bw_mm,
        "h_mm": geometry.h_mm,
        "has_compression_reinforcement": has_compression_reinforcement,
        "min_compression_bar_diameter_mm": min_compression_bar_diameter_mm,
        "transverse_bar_diameter_mm": resolved_dbt,
        "compression_lateral_support_spacing_mm": (
            compression_lateral_support_spacing_mm
        ),
    }

    # 1. Central Gatekeeper check
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(
            normalized_inputs=raw_inputs, unit="mm"
        )

    # 2. Deterministic input validation
    diagnostics: List[EngineeringDiagnostic] = []
    diagnostics.extend(
        validate_beam_geometry(
            geometry, require_effective_depth=False, rule_id=rule_id
        )
    )

    if not has_compression_reinforcement:
        diagnostics.append(
            EngineeringDiagnostic(
                code="MISSING_COMPRESSION_REINFORCEMENT",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    f"Rule '{rule_id}' requires compression reinforcement: "
                    "set has_compression_reinforcement=True and supply "
                    "min_compression_bar_diameter_mm (smallest compression "
                    "bar diameter). For members without compression "
                    "reinforcement this check is not applicable and must not "
                    "be requested."
                ),
                rule_id=rule_id,
                field_name="has_compression_reinforcement",
            )
        )
    elif min_compression_bar_diameter_mm is None:
        diagnostics.append(
            EngineeringDiagnostic(
                code="MISSING_COMPRESSION_BAR_DIAMETER",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    "Smallest compression bar diameter db is required when "
                    "has_compression_reinforcement=True."
                ),
                rule_id=rule_id,
                field_name="min_compression_bar_diameter_mm",
            )
        )
    elif (
        not math.isfinite(min_compression_bar_diameter_mm)
        or min_compression_bar_diameter_mm <= 0.0
    ):
        diagnostics.append(
            _validate_diameter(
                min_compression_bar_diameter_mm,
                field_name="min_compression_bar_diameter_mm",
                rule_id=rule_id,
            )
        )

    if resolved_dbt is None:
        diagnostics.append(
            EngineeringDiagnostic(
                code="MISSING_TRANSVERSE_BAR_DIAMETER",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    "Transverse reinforcement diameter dbt is required: supply "
                    "transverse_bar_diameter_mm or geometry.stirrup_diameter_mm."
                ),
                rule_id=rule_id,
                field_name="transverse_bar_diameter_mm",
            )
        )
    elif not math.isfinite(resolved_dbt) or resolved_dbt <= 0.0:
        diagnostics.append(
            _validate_diameter(
                resolved_dbt,
                field_name="transverse_bar_diameter_mm",
                rule_id=rule_id,
            )
        )

    if compression_lateral_support_spacing_mm is not None and (
        not math.isfinite(compression_lateral_support_spacing_mm)
        or compression_lateral_support_spacing_mm <= 0.0
    ):
        diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_COMPRESSION_LATERAL_SPACING",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    "compression_lateral_support_spacing_mm must be finite "
                    f"and > 0 mm, got {compression_lateral_support_spacing_mm}."
                ),
                rule_id=rule_id,
                field_name="compression_lateral_support_spacing_mm",
            )
        )

    if diagnostics:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="mm",
            outcome=EvaluationOutcome.INVALID_INPUT,
            diagnostics=diagnostics,
            message=diagnostics[0].message,
        )

    assert min_compression_bar_diameter_mm is not None
    assert resolved_dbt is not None

    # 3. Maximum permitted lateral support spacing
    b_min_mm = min(geometry.bw_mm, geometry.h_mm)
    limit_from_db = BG_DETAIL_COMP_LAT_001_DB_MULTIPLIER * (
        min_compression_bar_diameter_mm
    )
    limit_from_dbt = BG_DETAIL_COMP_LAT_001_DBT_MULTIPLIER * resolved_dbt
    sc_max_mm = min(limit_from_db, limit_from_dbt, b_min_mm)

    if sc_max_mm == limit_from_db:
        governing = "16*db"
    elif sc_max_mm == limit_from_dbt:
        governing = "48*dbt"
    else:
        governing = "b_min"

    intermediates: Dict[str, float] = {
        "db_compression_min_mm": min_compression_bar_diameter_mm,
        "dbt_transverse_mm": resolved_dbt,
        "b_min_mm": b_min_mm,
        "limit_16db_mm": limit_from_db,
        "limit_48dbt_mm": limit_from_dbt,
        "sc_max_mm": sc_max_mm,
        "governing_limit_code": {
            "16*db": 1.0,
            "48*dbt": 2.0,
            "b_min": 3.0,
        }[governing],
    }

    # 4. Verify provided spacing when available
    if compression_lateral_support_spacing_mm is None:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=sc_max_mm,
            unit="mm",
            outcome=EvaluationOutcome.COMPUTED,
            diagnostics=(),
            message=(
                f"Computed maximum compression lateral support spacing sc_max "
                f"= {sc_max_mm} mm (governed by {governing})."
            ),
        )

    intermediates["sc_provided_mm"] = compression_lateral_support_spacing_mm
    if compression_lateral_support_spacing_mm <= sc_max_mm:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=sc_max_mm,
            unit="mm",
            outcome=EvaluationOutcome.PASS,
            diagnostics=(),
            message=(
                f"PASS: sc ({compression_lateral_support_spacing_mm} mm) <= "
                f"sc_max ({sc_max_mm} mm) per Clause 9-11-6-5-12 "
                f"({governing})."
            ),
        )

    fail_diag = EngineeringDiagnostic(
        code="COMPRESSION_LATERAL_SUPPORT_SPACING_EXCEEDED",
        severity=DiagnosticSeverity.ERROR,
        message=(
            f"FAIL: sc ({compression_lateral_support_spacing_mm} mm) > "
            f"sc_max ({sc_max_mm} mm) per Clause 9-11-6-5-12 ({governing})."
        ),
        rule_id=rule_id,
        field_name="compression_lateral_support_spacing_mm",
    )
    return CalculationTraceStep.from_rule(
        gate.rule,
        normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=sc_max_mm,
        unit="mm",
        outcome=EvaluationOutcome.FAIL,
        diagnostics=(fail_diag,),
        message=fail_diag.message,
    )


def evaluate_longitudinal_bar_clear_spacing(
    geometry: BeamGeometry,
    *,
    max_bar_diameter_mm: Optional[float] = None,
    aggregate_size_mm: Optional[float] = None,
    provided_clear_spacing_mm: Optional[float] = None,
    is_bundled: bool = False,
    is_shotcrete: bool = False,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate Mabhas 9 minimum clear bar spacing in a layer (BG-DETAIL-SPACING-001).

    Verified source: Mabhas 9 (1399), Clause 9-21-2-1-1, PDF p. 441 /
    Printed p. 420:

        s_clear >= max(25 mm, db_max, (4/3) * d_agg)

    for the clear distance between parallel longitudinal bars in ONE
    horizontal layer (clause items الف/ب/پ; `1/33` in the Persian text is
    Persian decimal notation for 1.33 = 4/3).

    Scope handling (same source page):
    - Clause 9-21-2-1-3 (columns, pedestal columns, ties, wall boundary
      elements: 40 mm / 1.5*db_max) is NOT a beam rule and is never
      substituted here.
    - Clause 9-21-2-1-4: not applicable to shotcrete -> ``is_shotcrete=True``
      deterministically returns ``NOT_APPLICABLE``.
    - Bundled bars: the equivalent-diameter treatment (Clause 9-21-5-6) is
      text-located but not visually verified -> ``is_bundled=True``
      deterministically returns ``UNVERIFIED_RULE_BLOCKED``.

    Required inputs (never defaulted): largest bar diameter ``db_max``
    (explicit kwarg or resolved from ``geometry.tension_rebar_groups``) and
    nominal maximum aggregate size ``d_agg`` (missing aggregate input returns
    ``INVALID_INPUT`` — item (پ) of the clause is never dropped). The
    provided clear spacing may be omitted, in which case the required minimum
    is computed (``COMPUTED``).
    """
    rule_id = RULE_BG_DETAIL_SPACING_001.rule_id

    resolved_db: Optional[float] = max_bar_diameter_mm
    if resolved_db is None and geometry.tension_rebar_groups:
        resolved_db = max(
            group.bar_diameter_mm for group in geometry.tension_rebar_groups
        )

    raw_inputs: Dict[str, ScalarInputValue] = {
        "bw_mm": geometry.bw_mm,
        "h_mm": geometry.h_mm,
        "max_bar_diameter_mm": resolved_db,
        "aggregate_size_mm": aggregate_size_mm,
        "provided_clear_spacing_mm": provided_clear_spacing_mm,
        "is_bundled": is_bundled,
        "is_shotcrete": is_shotcrete,
    }

    # 1. Central Gatekeeper check
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(
            normalized_inputs=raw_inputs, unit="mm"
        )

    # 2. Shotcrete exclusion (Clause 9-21-2-1-4)
    if is_shotcrete:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="mm",
            outcome=EvaluationOutcome.NOT_APPLICABLE,
            diagnostics=(),
            message=(
                "NOT_APPLICABLE: Clause 9-21-2-1-1 minimum clear bar spacing "
                "does not apply to shotcrete (Clause 9-21-2-1-4)."
            ),
        )

    # 3. Bundled bars blocked (Clause 9-21-5-6 pending visual verification)
    if is_bundled:
        bundled_diag = EngineeringDiagnostic(
            code="UNVERIFIED_BUNDLED_BAR_SPACING",
            severity=DiagnosticSeverity.BLOCK,
            message=(
                f"Rule '{rule_id}' is blocked: bundled bars require the "
                "equivalent bar diameter of Clause 9-21-5-6, which is "
                "text-located but not visually verified. "
                "UNVERIFIED_RULE_BLOCKED (UNSUPPORTED_CONFIGURATION)."
            ),
            rule_id=rule_id,
            field_name="is_bundled",
            required_verification=(
                "Visually verify Mabhas 9 Clause 9-21-5-6 (bundle equivalent "
                "diameter) against the source PDF before unblocking bundled "
                "bar spacing."
            ),
        )
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="mm",
            outcome=EvaluationOutcome.UNVERIFIED_RULE_BLOCKED,
            diagnostics=(bundled_diag,),
            message=bundled_diag.message,
        )

    # 4. Deterministic input validation
    diagnostics: List[EngineeringDiagnostic] = []
    diagnostics.extend(
        validate_beam_geometry(
            geometry, require_effective_depth=False, rule_id=rule_id
        )
    )

    if resolved_db is None:
        diagnostics.append(
            EngineeringDiagnostic(
                code="MISSING_GOVERNING_BAR_DIAMETER",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    "Largest bar diameter db_max is required (clause item ب): "
                    "supply max_bar_diameter_mm or geometry.tension_rebar_groups."
                ),
                rule_id=rule_id,
                field_name="max_bar_diameter_mm",
            )
        )
    elif not math.isfinite(resolved_db) or resolved_db <= 0.0:
        diagnostics.append(
            _validate_diameter(
                resolved_db,
                field_name="max_bar_diameter_mm",
                rule_id=rule_id,
            )
        )

    if aggregate_size_mm is None:
        diagnostics.append(
            EngineeringDiagnostic(
                code="MISSING_AGGREGATE_SIZE",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    "Nominal maximum aggregate size d_agg is required (clause "
                    "item پ: (4/3)*d_agg); it is a mandatory input of Clause "
                    "9-21-2-1-1 and is never silently assumed or defaulted."
                ),
                rule_id=rule_id,
                field_name="aggregate_size_mm",
            )
        )
    elif not math.isfinite(aggregate_size_mm) or aggregate_size_mm <= 0.0:
        diagnostics.append(
            _validate_positive_finite(
                aggregate_size_mm,
                field_name="aggregate_size_mm",
                rule_id=rule_id,
            )
        )

    if provided_clear_spacing_mm is not None and (
        not math.isfinite(provided_clear_spacing_mm)
        or provided_clear_spacing_mm <= 0.0
    ):
        diagnostics.append(
            _validate_positive_finite(
                provided_clear_spacing_mm,
                field_name="provided_clear_spacing_mm",
                rule_id=rule_id,
            )
        )

    if diagnostics:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="mm",
            outcome=EvaluationOutcome.INVALID_INPUT,
            diagnostics=diagnostics,
            message=diagnostics[0].message,
        )

    assert resolved_db is not None  # for type checkers
    assert aggregate_size_mm is not None  # for type checkers

    # 5. Required minimum clear spacing (max of the three clause items)
    limit_25_mm = BG_DETAIL_SPACING_001_MIN_CLEAR_MM
    limit_db_mm = resolved_db
    limit_agg_mm = BG_DETAIL_SPACING_001_AGGREGATE_FACTOR * aggregate_size_mm
    required_spacing_mm = max(limit_25_mm, limit_db_mm, limit_agg_mm)
    if required_spacing_mm == limit_25_mm:
        governing = "25 mm (item الف)"
    elif required_spacing_mm == limit_db_mm:
        governing = "db_max (item ب)"
    else:
        governing = "(4/3)*d_agg (item پ)"

    intermediates: Dict[str, float] = {
        "db_governing_mm": resolved_db,
        "aggregate_size_mm": aggregate_size_mm,
        "limit_absolute_25_mm": limit_25_mm,
        "limit_db_max_mm": limit_db_mm,
        "limit_4_3_d_agg_mm": limit_agg_mm,
        "required_clear_spacing_mm": required_spacing_mm,
    }

    # 6. Verify provided clear spacing when available
    if provided_clear_spacing_mm is None:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=required_spacing_mm,
            unit="mm",
            outcome=EvaluationOutcome.COMPUTED,
            diagnostics=(),
            message=(
                f"Computed required minimum clear bar spacing s_clear >= "
                f"{required_spacing_mm} mm (governed by {governing})."
            ),
        )

    intermediates["provided_clear_spacing_mm"] = provided_clear_spacing_mm
    if provided_clear_spacing_mm >= required_spacing_mm:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=required_spacing_mm,
            unit="mm",
            outcome=EvaluationOutcome.PASS,
            diagnostics=(),
            message=(
                f"PASS: provided clear spacing ({provided_clear_spacing_mm} mm) "
                f">= required ({required_spacing_mm} mm) per Clause 9-21-2-1-1 "
                f"({governing})."
            ),
        )

    fail_diag = EngineeringDiagnostic(
        code="INSUFFICIENT_BAR_CLEAR_SPACING",
        severity=DiagnosticSeverity.ERROR,
        message=(
            f"FAIL: provided clear spacing ({provided_clear_spacing_mm} mm) < "
            f"required ({required_spacing_mm} mm) per Clause 9-21-2-1-1 "
            f"({governing})."
        ),
        rule_id=rule_id,
        field_name="provided_clear_spacing_mm",
    )
    return CalculationTraceStep.from_rule(
        gate.rule,
        normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=required_spacing_mm,
        unit="mm",
        outcome=EvaluationOutcome.FAIL,
        diagnostics=(fail_diag,),
        message=fail_diag.message,
    )


def evaluate_layer_clear_spacing(
    geometry: BeamGeometry,
    *,
    layer_count: Optional[int] = None,
    layers_directly_aligned: Optional[bool] = None,
    provided_layer_clear_spacing_mm: Optional[float] = None,
    is_bundled: bool = False,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate Mabhas 9 multi-layer vertical clear spacing (BG-DETAIL-LAYER-SPACING-001).

    Verified source: Mabhas 9 (1399), Clause 9-21-2-1-2, PDF p. 441 /
    Printed p. 420: for parallel bars placed in SEVERAL horizontal layers,
    (i) the bars of each upper layer must be placed directly above the bars
    of the layer below (vertical alignment), and (ii) the clear distance
    between two successive layers must be at least 25 mm (independent of db
    and aggregate size).

    Required inputs (never silently assumed): the number of reinforcement
    layers (explicit ``layer_count`` or derived from
    ``geometry.tension_rebar_groups`` layer indices) and, for multi-layer
    arrangements, the typed ``layers_directly_aligned`` confirmation. The
    provided clear inter-layer spacing may be omitted (``COMPUTED`` returns
    the 25 mm requirement). ``layer_count == 1`` returns ``NOT_APPLICABLE``;
    bundled bars return ``UNVERIFIED_RULE_BLOCKED`` (Clause 9-21-5-6
    equivalent diameter pending visual verification).
    """
    rule_id = RULE_BG_DETAIL_LAYER_SPACING_001.rule_id

    resolved_spacing: Optional[float] = provided_layer_clear_spacing_mm
    if resolved_spacing is None:
        resolved_spacing = geometry.layer_clear_spacing_mm

    resolved_layers: Optional[int] = layer_count
    if resolved_layers is None and geometry.tension_rebar_groups:
        resolved_layers = max(
            group.layer_index for group in geometry.tension_rebar_groups
        )

    raw_inputs: Dict[str, ScalarInputValue] = {
        "bw_mm": geometry.bw_mm,
        "h_mm": geometry.h_mm,
        "layer_count": resolved_layers,
        "layers_directly_aligned": layers_directly_aligned,
        "layer_clear_spacing_mm": resolved_spacing,
        "is_bundled": is_bundled,
    }

    # 1. Central Gatekeeper check
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(
            normalized_inputs=raw_inputs, unit="mm"
        )

    # 2. Bundled bars blocked (Clause 9-21-5-6 pending visual verification)
    if is_bundled:
        bundled_diag = EngineeringDiagnostic(
            code="UNVERIFIED_BUNDLED_BAR_LAYER_SPACING",
            severity=DiagnosticSeverity.BLOCK,
            message=(
                f"Rule '{rule_id}' is blocked: bundled bars require the "
                "equivalent bar diameter of Clause 9-21-5-6, which is "
                "text-located but not visually verified. "
                "UNVERIFIED_RULE_BLOCKED (UNSUPPORTED_CONFIGURATION)."
            ),
            rule_id=rule_id,
            field_name="is_bundled",
            required_verification=(
                "Visually verify Mabhas 9 Clause 9-21-5-6 (bundle equivalent "
                "diameter) against the source PDF before unblocking bundled "
                "bar layer spacing."
            ),
        )
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="mm",
            outcome=EvaluationOutcome.UNVERIFIED_RULE_BLOCKED,
            diagnostics=(bundled_diag,),
            message=bundled_diag.message,
        )

    # 3. Deterministic input validation
    diagnostics: List[EngineeringDiagnostic] = []
    diagnostics.extend(
        validate_beam_geometry(
            geometry, require_effective_depth=False, rule_id=rule_id
        )
    )

    if resolved_layers is None:
        diagnostics.append(
            EngineeringDiagnostic(
                code="MISSING_LAYER_COUNT",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    "The number of reinforcement layers is required: supply "
                    "layer_count or geometry.tension_rebar_groups with layer "
                    "indices; the layer arrangement is never silently assumed."
                ),
                rule_id=rule_id,
                field_name="layer_count",
            )
        )
    elif (
        isinstance(resolved_layers, bool)
        or not isinstance(resolved_layers, int)
        or resolved_layers < 1
    ):
        diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_LAYER_COUNT",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    f"layer_count must be an integer >= 1, got "
                    f"{resolved_layers!r}."
                ),
                rule_id=rule_id,
                field_name="layer_count",
            )
        )

    if resolved_spacing is not None and (
        not math.isfinite(resolved_spacing) or resolved_spacing <= 0.0
    ):
        diagnostics.append(
            _validate_positive_finite(
                resolved_spacing,
                field_name="layer_clear_spacing_mm",
                rule_id=rule_id,
            )
        )

    if diagnostics:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="mm",
            outcome=EvaluationOutcome.INVALID_INPUT,
            diagnostics=diagnostics,
            message=diagnostics[0].message,
        )

    assert resolved_layers is not None  # for type checkers

    # 4. Single-layer arrangement: rule is not applicable
    if resolved_layers == 1:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="mm",
            outcome=EvaluationOutcome.NOT_APPLICABLE,
            diagnostics=(),
            message=(
                "NOT_APPLICABLE: a single reinforcement layer carries no "
                "inter-layer requirement; Clause 9-21-2-1-2 applies to "
                "multiple horizontal layers."
            ),
        )

    # 5. Multi-layer: vertical alignment is a required typed input (never
    #    silently assumed per Phase 2E Stage A finalization note).
    if layers_directly_aligned is None:
        align_diag = EngineeringDiagnostic(
            code="MISSING_LAYER_ALIGNMENT",
            severity=DiagnosticSeverity.ERROR,
            message=(
                "Vertical alignment confirmation is required for multi-layer "
                "arrangements (Clause 9-21-2-1-2 item i): supply "
                "layers_directly_aligned=True/False; alignment is a typed "
                "input and is never silently assumed."
            ),
            rule_id=rule_id,
            field_name="layers_directly_aligned",
        )
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="mm",
            outcome=EvaluationOutcome.INVALID_INPUT,
            diagnostics=(align_diag,),
            message=align_diag.message,
        )

    required_layer_spacing_mm = BG_DETAIL_LAYER_SPACING_001_MIN_CLEAR_MM
    intermediates: Dict[str, float] = {
        "layer_count": float(resolved_layers),
        "layers_directly_aligned": 1.0 if layers_directly_aligned else 0.0,
        "required_layer_clear_spacing_mm": required_layer_spacing_mm,
    }

    # 6. Alignment violation: clause requirement (i) is not met -> FAIL
    if not layers_directly_aligned:
        fail_align_diag = EngineeringDiagnostic(
            code="LAYERS_NOT_DIRECTLY_ALIGNED",
            severity=DiagnosticSeverity.ERROR,
            message=(
                "FAIL: upper-layer bars are not placed directly above "
                "lower-layer bars; Clause 9-21-2-1-2 item (i) vertical "
                "alignment requirement is not met."
            ),
            rule_id=rule_id,
            field_name="layers_directly_aligned",
        )
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=required_layer_spacing_mm,
            unit="mm",
            outcome=EvaluationOutcome.FAIL,
            diagnostics=(fail_align_diag,),
            message=fail_align_diag.message,
        )

    # 7. Verify provided clear inter-layer spacing when available
    if resolved_spacing is None:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=required_layer_spacing_mm,
            unit="mm",
            outcome=EvaluationOutcome.COMPUTED,
            diagnostics=(),
            message=(
                f"Computed required minimum clear inter-layer spacing "
                f">= {required_layer_spacing_mm} mm with vertically aligned "
                "layers (Clause 9-21-2-1-2)."
            ),
        )

    intermediates["provided_layer_clear_spacing_mm"] = resolved_spacing
    if resolved_spacing >= required_layer_spacing_mm:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=required_layer_spacing_mm,
            unit="mm",
            outcome=EvaluationOutcome.PASS,
            diagnostics=(),
            message=(
                f"PASS: layers aligned and provided clear inter-layer "
                f"spacing ({resolved_spacing} mm) >= required "
                f"({required_layer_spacing_mm} mm) per Clause 9-21-2-1-2."
            ),
        )

    fail_diag = EngineeringDiagnostic(
        code="INSUFFICIENT_LAYER_CLEAR_SPACING",
        severity=DiagnosticSeverity.ERROR,
        message=(
            f"FAIL: provided clear inter-layer spacing ({resolved_spacing} "
            f"mm) < required ({required_layer_spacing_mm} mm) per Clause "
            "9-21-2-1-2 item (ii)."
        ),
        rule_id=rule_id,
        field_name="layer_clear_spacing_mm",
    )
    return CalculationTraceStep.from_rule(
        gate.rule,
        normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=required_layer_spacing_mm,
        unit="mm",
        outcome=EvaluationOutcome.FAIL,
        diagnostics=(fail_diag,),
        message=fail_diag.message,
    )


def evaluate_minimum_concrete_cover(
    geometry: BeamGeometry,
    *,
    exposure: Optional[ConcreteCoverExposureClass] = None,
    cover_bar_diameter_mm: Optional[float] = None,
    provided_cover_mm: Optional[float] = None,
    is_bundled: bool = False,
    has_headed_shear_reinforcement: bool = False,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate Mabhas 9 minimum concrete cover over beam reinforcement (BG-DETAIL-COVER-001).

    Verified source: Mabhas 9 (1399), Clauses 9-4-9-4, 9-4-9-5, 9-4-9-5-1..3
    and Table 9-4-6, PDF pp. 92-93 / Printed pp. 71-72 (normal, non-corrosive
    conditions). Table 9-4-6 beam-relevant rows:

    - Permanent contact with earth (cast against earth): 75 mm.
    - Air/weather or non-permanent earth contact: db 18-58 mm -> 50 mm;
      bars/wires db <= 16 mm -> 40 mm.
    - No air/earth contact, beams (and columns, pedestals, tension members):
      40 mm for longitudinal bars, stirrups, ties, spirals, and hoops.

    Headed shear reinforcement (Clause 9-4-9-5-3): cover over the head/plate
    shall not be less than the member cover — the same computed minimum
    applies (flagged via ``has_headed_shear_reinforcement``).

    The exposure condition is a REQUIRED typed input (never assumed).
    Corrosive/unusual environments are routed to Appendix 9-پ1 per Clause
    9-4-9-6 and deterministically return ``UNVERIFIED_RULE_BLOCKED``.
    The bundled-group rule (Clause 9-4-9-5-2: cover >= min(equivalent group
    diameter, 75 mm earth-contact / 50 mm otherwise)) uses the Clause
    9-21-5-6 equivalent diameter, pending visual verification -> bundled
    input deterministically returns ``UNVERIFIED_RULE_BLOCKED``. Diameter
    classes outside db <= 16 mm and 18 <= db <= 58 mm (weather exposure) are
    never interpolated -> ``UNVERIFIED_RULE_BLOCKED``.
    """
    rule_id = RULE_BG_DETAIL_COVER_001.rule_id

    resolved_cover: Optional[float] = provided_cover_mm
    if resolved_cover is None:
        resolved_cover = geometry.clear_cover_mm

    resolved_db: Optional[float] = cover_bar_diameter_mm
    if resolved_db is None and geometry.tension_rebar_groups:
        resolved_db = max(
            group.bar_diameter_mm for group in geometry.tension_rebar_groups
        )

    raw_inputs: Dict[str, ScalarInputValue] = {
        "bw_mm": geometry.bw_mm,
        "h_mm": geometry.h_mm,
        "exposure_class": exposure.value if exposure is not None else None,
        "cover_bar_diameter_mm": resolved_db,
        "provided_cover_mm": resolved_cover,
        "is_bundled": is_bundled,
        "has_headed_shear_reinforcement": has_headed_shear_reinforcement,
    }

    # 1. Central Gatekeeper check
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(
            normalized_inputs=raw_inputs, unit="mm"
        )

    # 2. Exposure condition is required (never assumed)
    if exposure is None:
        exposure_diag = EngineeringDiagnostic(
            code="MISSING_COVER_EXPOSURE_CLASS",
            severity=DiagnosticSeverity.ERROR,
            message=(
                "The concrete cover exposure condition is required (Table "
                "9-4-6 classes); it is a typed input of Clause 9-4-9-5/Table "
                "9-4-6 and is never silently assumed."
            ),
            rule_id=rule_id,
            field_name="exposure",
        )
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="mm",
            outcome=EvaluationOutcome.INVALID_INPUT,
            diagnostics=(exposure_diag,),
            message=exposure_diag.message,
        )

    # 3. Corrosive / unusual environment routed to Appendix 9-پ1 (blocked)
    if exposure == ConcreteCoverExposureClass.CORROSIVE_ENVIRONMENT:
        corrosive_diag = EngineeringDiagnostic(
            code="CORROSIVE_EXPOSURE_BLOCKED_APPENDIX_9P1",
            severity=DiagnosticSeverity.BLOCK,
            message=(
                f"Rule '{rule_id}' is blocked: corrosive or unusual "
                "environments are governed by Mabhas 9 Appendix 9-پ1 "
                "(durability) per Clauses 9-4-9-6/9-4-9-7, which is not "
                "visually verified. UNVERIFIED_RULE_BLOCKED."
            ),
            rule_id=rule_id,
            field_name="exposure",
            required_verification=(
                "Visually verify Mabhas 9 Appendix 9-پ1 durability cover "
                "requirements before executing corrosive-environment cover "
                "checks."
            ),
        )
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="mm",
            outcome=EvaluationOutcome.UNVERIFIED_RULE_BLOCKED,
            diagnostics=(corrosive_diag,),
            message=corrosive_diag.message,
        )

    # 4. Bundled bars blocked (Clause 9-4-9-5-2 -> equivalent diameter 9-21-5-6)
    if is_bundled:
        bundled_diag = EngineeringDiagnostic(
            code="UNVERIFIED_BUNDLED_BAR_COVER",
            severity=DiagnosticSeverity.BLOCK,
            message=(
                f"Rule '{rule_id}' is blocked: the bundled-group cover rule "
                "(Clause 9-4-9-5-2: min(equivalent group diameter, 75 mm "
                "permanent-earth / 50 mm otherwise)) requires the Clause "
                "9-21-5-6 equivalent diameter, which is text-located but not "
                "visually verified. UNVERIFIED_RULE_BLOCKED."
            ),
            rule_id=rule_id,
            field_name="is_bundled",
            required_verification=(
                "Visually verify Mabhas 9 Clause 9-21-5-6 (bundle equivalent "
                "diameter) against the source PDF before unblocking bundled "
                "bar cover."
            ),
        )
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="mm",
            outcome=EvaluationOutcome.UNVERIFIED_RULE_BLOCKED,
            diagnostics=(bundled_diag,),
            message=bundled_diag.message,
        )

    # 5. Deterministic input validation
    diagnostics: List[EngineeringDiagnostic] = []
    diagnostics.extend(
        validate_beam_geometry(
            geometry, require_effective_depth=False, rule_id=rule_id
        )
    )

    if resolved_db is not None and (
        not math.isfinite(resolved_db) or resolved_db <= 0.0
    ):
        diagnostics.append(
            _validate_diameter(
                resolved_db,
                field_name="cover_bar_diameter_mm",
                rule_id=rule_id,
            )
        )

    if resolved_cover is not None and (
        not math.isfinite(resolved_cover) or resolved_cover <= 0.0
    ):
        diagnostics.append(
            _validate_positive_finite(
                resolved_cover,
                field_name="provided_cover_mm",
                rule_id=rule_id,
            )
        )

    if diagnostics:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="mm",
            outcome=EvaluationOutcome.INVALID_INPUT,
            diagnostics=diagnostics,
            message=diagnostics[0].message,
        )

    # 6. Required minimum cover from Table 9-4-6 (beam member)
    intermediates: Dict[str, float] = {}
    basis: str
    if exposure == ConcreteCoverExposureClass.PERMANENT_EARTH_CONTACT:
        required_cover_mm = BG_DETAIL_COVER_001_PERMANENT_EARTH_MM
        basis = "permanent earth contact (Table 9-4-6 row i)"
    elif exposure == ConcreteCoverExposureClass.NOT_EXPOSED:
        required_cover_mm = BG_DETAIL_COVER_001_BEAM_NOT_EXPOSED_MM
        basis = (
            "no air/earth contact, beams (Table 9-4-6 row iv: longitudinal "
            "bars, stirrups, ties, spirals, hoops)"
        )
    elif exposure == ConcreteCoverExposureClass.WEATHER_OR_EARTH_CONTACT:
        if resolved_db is None:
            db_diag = EngineeringDiagnostic(
                code="MISSING_COVER_BAR_DIAMETER",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    "Governing bar diameter db is required for air/weather or "
                    "non-permanent earth contact exposure (Table 9-4-6 "
                    "diameter classes: <= 16 mm -> 40 mm; 18-58 mm -> 50 mm); "
                    "supply cover_bar_diameter_mm or "
                    "geometry.tension_rebar_groups. Never silently assumed."
                ),
                rule_id=rule_id,
                field_name="cover_bar_diameter_mm",
            )
            return CalculationTraceStep.from_rule(
                gate.rule,
                normalized_inputs=raw_inputs,
                intermediate_values={},
                final_result=None,
                unit="mm",
                outcome=EvaluationOutcome.INVALID_INPUT,
                diagnostics=(db_diag,),
                message=db_diag.message,
            )
        intermediates["db_governing_mm"] = resolved_db
        if resolved_db <= BG_DETAIL_COVER_001_WEATHER_MAX_SMALL_DB_MM:
            required_cover_mm = BG_DETAIL_COVER_001_WEATHER_DB_LE_16_MM
            basis = "air/earth contact, db <= 16 mm (Table 9-4-6 row ii)"
        elif (
            BG_DETAIL_COVER_001_WEATHER_MIN_LARGE_DB_MM
            <= resolved_db
            <= BG_DETAIL_COVER_001_WEATHER_MAX_LARGE_DB_MM
        ):
            required_cover_mm = BG_DETAIL_COVER_001_WEATHER_DB_18_TO_58_MM
            basis = "air/earth contact, db 18-58 mm (Table 9-4-6 row ii)"
        else:
            gap_diag = EngineeringDiagnostic(
                code="UNVERIFIED_COVER_DIAMETER_CLASS",
                severity=DiagnosticSeverity.BLOCK,
                message=(
                    f"Rule '{rule_id}' is blocked: governing bar diameter "
                    f"db = {resolved_db} mm lies outside the Table 9-4-6 "
                    "diameter classes (<= 16 mm and 18-58 mm); the uncovered "
                    "interval is never interpolated. "
                    "UNVERIFIED_RULE_BLOCKED (UNSUPPORTED_CONFIGURATION)."
                ),
                rule_id=rule_id,
                field_name="cover_bar_diameter_mm",
                required_verification=(
                    "Visually verify Table 9-4-6 treatment for bar diameters "
                    "in the (16, 18) mm and > 58 mm intervals before "
                    "executing."
                ),
            )
            return CalculationTraceStep.from_rule(
                gate.rule,
                normalized_inputs=raw_inputs,
                intermediate_values=intermediates,
                final_result=None,
                unit="mm",
                outcome=EvaluationOutcome.UNVERIFIED_RULE_BLOCKED,
                diagnostics=(gap_diag,),
                message=gap_diag.message,
            )
    else:
        # All ConcreteCoverExposureClass members are handled above (the
        # CORROSIVE branch returned in step 3); this branch is unreachable.
        raise ValueError(
            f"Unhandled ConcreteCoverExposureClass member: {exposure!r}"
        )

    intermediates["required_cover_mm"] = required_cover_mm
    if has_headed_shear_reinforcement:
        intermediates["headed_shear_reinforcement_same_minimum"] = (
            required_cover_mm
        )
        headed_note = (
            " Headed shear reinforcement head/plate cover is governed by the "
            "same minimum (Clause 9-4-9-5-3)."
        )
    else:
        headed_note = ""

    # 7. Verify provided cover when available
    if resolved_cover is None:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=required_cover_mm,
            unit="mm",
            outcome=EvaluationOutcome.COMPUTED,
            diagnostics=(),
            message=(
                f"Computed required minimum concrete cover >= "
                f"{required_cover_mm} mm for {basis}."
                f"{headed_note}"
            ),
        )

    intermediates["provided_cover_mm"] = resolved_cover
    if resolved_cover >= required_cover_mm:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=required_cover_mm,
            unit="mm",
            outcome=EvaluationOutcome.PASS,
            diagnostics=(),
            message=(
                f"PASS: provided clear cover ({resolved_cover} mm) >= "
                f"required ({required_cover_mm} mm) for {basis}."
                f"{headed_note}"
            ),
        )

    fail_diag = EngineeringDiagnostic(
        code="INSUFFICIENT_CONCRETE_COVER",
        severity=DiagnosticSeverity.ERROR,
        message=(
            f"FAIL: provided clear cover ({resolved_cover} mm) < required "
            f"({required_cover_mm} mm) for {basis} (Clause 9-4-9-5-1, Table "
            f"9-4-6)."
        ),
        rule_id=rule_id,
        field_name="provided_cover_mm",
    )
    return CalculationTraceStep.from_rule(
        gate.rule,
        normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=required_cover_mm,
        unit="mm",
        outcome=EvaluationOutcome.FAIL,
        diagnostics=(fail_diag,),
        message=fail_diag.message,
    )


def run_mabhas9_beam_detailing_workflow(
    geometry: BeamGeometry,
    *,
    max_longitudinal_bar_diameter_mm: Optional[float] = None,
    is_bundled: bool = False,
    transverse_bar_diameter_mm: Optional[float] = None,
    has_compression_reinforcement: bool = False,
    min_compression_bar_diameter_mm: Optional[float] = None,
    compression_lateral_support_spacing_mm: Optional[float] = None,
    aggregate_size_mm: Optional[float] = None,
    horizontal_clear_spacing_mm: Optional[float] = None,
    is_shotcrete: bool = False,
    rebar_layer_count: Optional[int] = None,
    layers_directly_aligned: Optional[bool] = None,
    cover_exposure: Optional[ConcreteCoverExposureClass] = None,
    cover_bar_diameter_mm: Optional[float] = None,
    provided_cover_mm: Optional[float] = None,
    has_headed_shear_reinforcement: bool = False,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> List[CalculationTraceStep]:
    """Run the verified Mabhas 9 beam detailing workflow (Phase 2D & 2E).

    Executes:
    1. ``BG-DETAIL-TRANS-DIA-001`` — minimum transverse bar diameter
       (always).
    2. ``BG-DETAIL-COMP-LAT-001`` — compression reinforcement lateral support
       spacing (only when ``has_compression_reinforcement=True``; the rule
       requires compression reinforcement to exist).
    3. ``BG-DETAIL-SPACING-001`` — clear bar spacing in a horizontal layer
       (only when the mandatory aggregate input ``aggregate_size_mm`` is
       supplied; Phase 2E Stage B).
    4. ``BG-DETAIL-LAYER-SPACING-001`` — multi-layer vertical alignment and
       clear spacing (only when ``rebar_layer_count`` is supplied; Phase 2E
       Stage B).
    5. ``BG-DETAIL-COVER-001`` — minimum concrete cover (only when the typed
       exposure input ``cover_exposure`` is supplied; Phase 2E Stage B;
       ``provided_cover_mm`` falls back to ``geometry.clear_cover_mm``).

    Returns the ordered trace steps; aggregate them with
    ``beamgenius.engine.beam_checker.aggregate_compliance_report``, which
    enforces the Anti-Misleading-PASS dominance hierarchy
    (``INVALID_INPUT > FAIL > BLOCKED > PARTIAL > PASS``) and never converts
    ``BLOCKED`` into ``PASS``.
    """
    steps: List[CalculationTraceStep] = [
        evaluate_minimum_transverse_bar_diameter(
            geometry,
            max_longitudinal_bar_diameter_mm=max_longitudinal_bar_diameter_mm,
            is_bundled=is_bundled,
            transverse_bar_diameter_mm=transverse_bar_diameter_mm,
            jurisdiction_mode=jurisdiction_mode,
        )
    ]
    if has_compression_reinforcement:
        steps.append(
            evaluate_compression_reinforcement_lateral_support_spacing(
                geometry,
                has_compression_reinforcement=True,
                min_compression_bar_diameter_mm=min_compression_bar_diameter_mm,
                transverse_bar_diameter_mm=transverse_bar_diameter_mm,
                compression_lateral_support_spacing_mm=(
                    compression_lateral_support_spacing_mm
                ),
                jurisdiction_mode=jurisdiction_mode,
            )
        )
    if aggregate_size_mm is not None:
        steps.append(
            evaluate_longitudinal_bar_clear_spacing(
                geometry,
                max_bar_diameter_mm=max_longitudinal_bar_diameter_mm,
                aggregate_size_mm=aggregate_size_mm,
                provided_clear_spacing_mm=horizontal_clear_spacing_mm,
                is_bundled=is_bundled,
                is_shotcrete=is_shotcrete,
                jurisdiction_mode=jurisdiction_mode,
            )
        )
    if rebar_layer_count is not None:
        steps.append(
            evaluate_layer_clear_spacing(
                geometry,
                layer_count=rebar_layer_count,
                layers_directly_aligned=layers_directly_aligned,
                provided_layer_clear_spacing_mm=(geometry.layer_clear_spacing_mm),
                is_bundled=is_bundled,
                jurisdiction_mode=jurisdiction_mode,
            )
        )
    if cover_exposure is not None:
        steps.append(
            evaluate_minimum_concrete_cover(
                geometry,
                exposure=cover_exposure,
                cover_bar_diameter_mm=cover_bar_diameter_mm,
                provided_cover_mm=provided_cover_mm,
                is_bundled=is_bundled,
                has_headed_shear_reinforcement=has_headed_shear_reinforcement,
                jurisdiction_mode=jurisdiction_mode,
            )
        )
    return steps
