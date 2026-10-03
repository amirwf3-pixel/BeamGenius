"""Mabhas 9 (1399) verified beam detailing evaluators (Phase 2D).

Verified production rules (Phase 2D):
- ``BG-DETAIL-TRANS-DIA-001``: minimum transverse reinforcement diameter
  enclosing longitudinal bars (Mabhas 9 Clause 9-11-6-5-11, PDF p. 228)
- ``BG-DETAIL-COMP-LAT-001``: compression reinforcement lateral support
  spacing (Mabhas 9 Clause 9-11-6-5-12, PDF p. 229)

Phase 2E Stage B verified production rules (clear spacing, layer spacing,
concrete cover) live in ``beamgenius.engine.detailing_spacing_mabhas9`` and
are orchestrated together with the Phase 2D rules by
``run_mabhas9_beam_detailing_workflow`` in this module.

Access note: ``evaluate_minimum_transverse_bar_diameter`` is the verified
production implementation. The legacy blocked-workflow stub of the same name
for the un-promoted ``BG-DETAIL-TRANS-DIA-PENDING`` sentinel remains in
``beamgenius.engine.beam_checker``; import the verified function explicitly
from this module, e.g.::

    from beamgenius.engine.detailing_mabhas9 import (
        evaluate_minimum_transverse_bar_diameter,
    )

Both evaluators deterministically return ``UNVERIFIED_RULE_BLOCKED`` for any
input configuration whose Mabhas 9 requirement is not source-verified (e.g.
the non-interpolated ``32 < db < 36 mm`` interval) and never invent values.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional

from beamgenius.domain.models import BeamGeometry
from beamgenius.domain.enums import (
    ConcreteCoverExposureClass,
    ConcreteCoverMemberClass,
    CoverReinforcementType,
    DiagnosticSeverity,
    EvaluationOutcome,
    JurisdictionMode,
)
from beamgenius.domain.trace import (
    CalculationTraceStep,
    EngineeringDiagnostic,
    ScalarInputValue,
)
from beamgenius.domain.validation import (
    validate_beam_geometry,
)
from beamgenius.engine.detailing_spacing_mabhas9 import (
    evaluate_beam_cover,
    evaluate_longitudinal_bar_clear_spacing,
    evaluate_longitudinal_layer_spacing,
)
from beamgenius.registry.catalog import (
    RULE_BG_DETAIL_COMP_LAT_001,
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
    cover_member_class: Optional[ConcreteCoverMemberClass] = None,
    cover_reinforcement_type: Optional[CoverReinforcementType] = None,
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
    3. ``BG-DETAIL-LONG-SPACING-001`` — clear bar spacing in a horizontal
       layer (only when ``aggregate_size_mm`` is supplied; Phase 2E Stage B:
       ``beamgenius.engine.detailing_spacing_mabhas9``).
    4. ``BG-DETAIL-LAYER-SPACING-001`` — multi-layer vertical alignment and
       clear spacing (only when ``rebar_layer_count`` is supplied; Phase 2E
       Stage B).
    5. ``BG-DETAIL-COVER-001`` — minimum concrete cover (only when a cover
       input ``cover_exposure`` or ``cover_member_class`` is supplied;
       Phase 2E Stage B; ``provided_cover_mm`` falls back to
       ``geometry.clear_cover_mm``).

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
            evaluate_longitudinal_layer_spacing(
                geometry,
                layer_count=rebar_layer_count,
                layers_directly_aligned=layers_directly_aligned,
                provided_layer_clear_spacing_mm=(geometry.layer_clear_spacing_mm),
                is_bundled=is_bundled,
                jurisdiction_mode=jurisdiction_mode,
            )
        )
    if cover_exposure is not None or cover_member_class is not None:
        steps.append(
            evaluate_beam_cover(
                geometry,
                exposure=cover_exposure,
                member_class=cover_member_class,
                reinforcement_type=cover_reinforcement_type,
                cover_bar_diameter_mm=cover_bar_diameter_mm,
                provided_cover_mm=provided_cover_mm,
                is_bundled=is_bundled,
                has_headed_shear_reinforcement=has_headed_shear_reinforcement,
                jurisdiction_mode=jurisdiction_mode,
            )
        )
    return steps
