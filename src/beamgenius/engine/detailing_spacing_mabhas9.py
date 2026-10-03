"""Mabhas 9 (1399) verified Phase 2E Stage B spacing & cover evaluators.

Verified production rules (visually verified 2026-10-03 from Mabhas 9,
1399 5th ed. source-page captures):

- ``BG-DETAIL-LONG-SPACING-001``: minimum clear spacing of parallel
  longitudinal bars in one horizontal layer (Clause 9-21-2-1-1,
  PDF p. 441 / Printed p. 420)
- ``BG-DETAIL-LAYER-SPACING-001``: vertical alignment and minimum clear
  spacing between reinforcement layers (Clause 9-21-2-1-2,
  PDF p. 441 / Printed p. 420)
- ``BG-DETAIL-COVER-001``: minimum concrete cover over reinforcement under
  normal (non-corrosive) conditions (Clauses 9-4-9-4, 9-4-9-5-1..3 +
  Table 9-4-6, PDF pp. 92-93 / Printed pp. 71-72)

Deterministic contract of every evaluator (in order):

1. Central Gatekeeper check (`evaluate_rule_gate`) runs FIRST.
2. Malformed input values (non-finite, non-positive, wrong type) return
   ``INVALID_INPUT``.
3. Missing required engineering inputs return ``UNVERIFIED_RULE_BLOCKED``
   (BLOCKED) with ``MISSING_*`` diagnostics — missing values are never
   assumed or defaulted.
4. SOURCE-verified gaps (bundled-bar equivalent diameter Clause 9-21-5-6,
   corrosive-environment Appendix 9-پ1, uncovered diameter classes) return
   ``UNVERIFIED_RULE_BLOCKED`` — BLOCKED is never converted to PASS.
5. Every step attaches the registry ``RuleReference``, a
   ``CalculationTraceStep``, and explicit diagnostic codes.

Access note: ``evaluate_longitudinal_bar_clear_spacing`` is the verified
production implementation. The legacy blocked-workflow stub of the same
name for the un-promoted ``BG-DETAIL-SPACING-BLOCKED`` sentinel remains in
``beamgenius.engine.beam_checker``; import the verified functions explicitly
from this module, e.g.::

    from beamgenius.engine.detailing_spacing_mabhas9 import (
        evaluate_longitudinal_bar_clear_spacing,
    )
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional

from beamgenius.domain.enums import (
    ConcreteCoverExposureClass,
    ConcreteCoverMemberClass,
    CoverReinforcementType,
    DiagnosticSeverity,
    EvaluationOutcome,
    JurisdictionMode,
)
from beamgenius.domain.models import BeamGeometry
from beamgenius.domain.trace import (
    CalculationTraceStep,
    EngineeringDiagnostic,
    RuleReference,
    ScalarInputValue,
)
from beamgenius.domain.validation import (
    validate_beam_geometry,
)
from beamgenius.registry.catalog import (
    RULE_BG_DETAIL_COVER_001,
    RULE_BG_DETAIL_LAYER_SPACING_001,
    RULE_BG_DETAIL_LONG_SPACING_001,
)
from beamgenius.registry.gatekeeper import GatekeeperDecision, evaluate_rule_gate

# Constants tied to BG-DETAIL-LONG-SPACING-001 (Mabhas 9 Clause 9-21-2-1-1,
# PDF p. 441 / Printed p. 420)
BG_DETAIL_LONG_SPACING_001_MIN_CLEAR_MM: float = 25.0
BG_DETAIL_LONG_SPACING_001_AGGREGATE_FACTOR: float = 4.0 / 3.0

# Constants tied to BG-DETAIL-LAYER-SPACING-001 (Mabhas 9 Clause 9-21-2-1-2,
# PDF p. 441 / Printed p. 420)
BG_DETAIL_LAYER_SPACING_001_MIN_CLEAR_MM: float = 25.0

# Constants tied to BG-DETAIL-COVER-001 (Mabhas 9 Clauses 9-4-9-5-1..3 +
# Table 9-4-6, PDF pp. 92-93 / Printed pp. 71-72)
BG_DETAIL_COVER_001_PERMANENT_EARTH_MM: float = 75.0
BG_DETAIL_COVER_001_WEATHER_DB_18_TO_58_MM: float = 50.0
BG_DETAIL_COVER_001_WEATHER_DB_LE_16_MM: float = 40.0
BG_DETAIL_COVER_001_BEAM_NOT_EXPOSED_MM: float = 40.0
BG_DETAIL_COVER_001_SLAB_NOT_EXPOSED_LARGE_DB_MM: float = 40.0
BG_DETAIL_COVER_001_SLAB_NOT_EXPOSED_SMALL_DB_MM: float = 20.0
BG_DETAIL_COVER_001_WEATHER_MAX_SMALL_DB_MM: float = 16.0
BG_DETAIL_COVER_001_WEATHER_MIN_LARGE_DB_MM: float = 18.0
BG_DETAIL_COVER_001_WEATHER_MAX_LARGE_DB_MM: float = 58.0
BG_DETAIL_COVER_001_SLAB_MAX_SMALL_DB_MM: float = 34.0
BG_DETAIL_COVER_001_SLAB_MIN_LARGE_DB_MM: float = 36.0


def _blocked_step(
    gate: GatekeeperDecision,
    *,
    raw_inputs: Dict[str, ScalarInputValue],
    diagnostics: List[EngineeringDiagnostic],
) -> CalculationTraceStep:
    """Build an UNVERIFIED_RULE_BLOCKED step through an allowed gate.

    Used for unverifiable or missing-input configurations: the rule itself is
    VERIFIED, but this specific configuration cannot be evaluated against the
    visually verified source (missing inputs, unverified branches). BLOCKED
    is never converted to PASS.
    """
    return CalculationTraceStep.from_rule(
        gate.rule,
        normalized_inputs=raw_inputs,
        intermediate_values={},
        final_result=None,
        unit="mm",
        outcome=EvaluationOutcome.UNVERIFIED_RULE_BLOCKED,
        diagnostics=tuple(diagnostics),
        message=diagnostics[0].message,
    )


def _invalid_step(
    gate: GatekeeperDecision,
    *,
    raw_inputs: Dict[str, ScalarInputValue],
    diagnostics: List[EngineeringDiagnostic],
) -> CalculationTraceStep:
    """Build an INVALID_INPUT step for malformed input values."""
    return CalculationTraceStep.from_rule(
        gate.rule,
        normalized_inputs=raw_inputs,
        intermediate_values={},
        final_result=None,
        unit="mm",
        outcome=EvaluationOutcome.INVALID_INPUT,
        diagnostics=tuple(diagnostics),
        message=diagnostics[0].message,
    )


def _missing_input_diagnostic(
    code: str,
    message: str,
    *,
    rule: RuleReference,
    field_name: str,
    required_verification: Optional[str] = None,
) -> EngineeringDiagnostic:
    """Build a missing-required-input diagnostic (severity BLOCK)."""
    return EngineeringDiagnostic(
        code=code,
        severity=DiagnosticSeverity.BLOCK,
        message=message,
        rule_id=rule.rule_id,
        field_name=field_name,
        required_verification=(
            required_verification
            if required_verification is not None
            else (
                "Supply the required engineering input; missing inputs are "
                "never assumed or defaulted."
            )
        ),
    )


def _malformed_value_diagnostic(
    value: object,
    *,
    field_name: str,
    rule: RuleReference,
) -> EngineeringDiagnostic:
    """Build an ERROR diagnostic for a non-finite or non-positive scalar."""
    return EngineeringDiagnostic(
        code="INVALID_" + field_name.upper().replace(" ", "_"),
        severity=DiagnosticSeverity.ERROR,
        message=(
            f"{field_name} must be finite and > 0 mm, got {value!r}."
        ),
        rule_id=rule.rule_id,
        field_name=field_name,
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
    """Evaluate Mabhas 9 minimum clear bar spacing (BG-DETAIL-LONG-SPACING-001).

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
      deterministically returns ``UNVERIFIED_RULE_BLOCKED``
      (``UNVERIFIED_BUNDLE_RULE``); no equivalent diameter is invented.

    Required inputs (never defaulted; missing -> BLOCKED): largest bar
    diameter ``db_max`` (explicit kwarg or resolved from
    ``geometry.tension_rebar_groups``) and nominal maximum aggregate size
    ``d_agg``. Malformed values return ``INVALID_INPUT``. The provided clear
    spacing may be omitted, in which case the required minimum is computed
    (``COMPUTED``).
    """
    rule_id = RULE_BG_DETAIL_LONG_SPACING_001.rule_id

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
    rule = gate.rule

    # 2. Shotcrete exclusion (Clause 9-21-2-1-4)
    if is_shotcrete:
        return CalculationTraceStep.from_rule(
            rule,
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
            code="UNVERIFIED_BUNDLE_RULE",
            severity=DiagnosticSeverity.BLOCK,
            message=(
                f"Rule '{rule_id}' is blocked: bundled bars require the "
                "equivalent bar diameter of Clause 9-21-5-6, which is "
                "text-located but not visually verified (VERIFY_PENDING). "
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
        return _blocked_step(
            gate, raw_inputs=raw_inputs, diagnostics=[bundled_diag]
        )

    # 4. Input validation: malformed -> INVALID_INPUT; missing -> BLOCKED
    invalid_diagnostics: List[EngineeringDiagnostic] = []
    invalid_diagnostics.extend(
        validate_beam_geometry(
            geometry, require_effective_depth=False, rule_id=rule_id
        )
    )
    missing_diagnostics: List[EngineeringDiagnostic] = []

    if resolved_db is None:
        missing_diagnostics.append(
            _missing_input_diagnostic(
                "MISSING_GOVERNING_BAR_DIAMETER",
                (
                    "Largest bar diameter db_max is required (clause item ب): "
                    "supply max_bar_diameter_mm or "
                    "geometry.tension_rebar_groups. Missing required inputs "
                    "are never assumed; BLOCKED."
                ),
                rule=rule,
                field_name="max_bar_diameter_mm",
            )
        )
    elif not math.isfinite(resolved_db) or resolved_db <= 0.0:
        invalid_diagnostics.append(
            _malformed_value_diagnostic(
                resolved_db,
                field_name="max_bar_diameter_mm",
                rule=rule,
            )
        )

    if aggregate_size_mm is None:
        missing_diagnostics.append(
            _missing_input_diagnostic(
                "MISSING_AGGREGATE_SIZE",
                (
                    "Nominal maximum aggregate size d_agg is required "
                    "(clause item پ: (4/3)*d_agg); it is never dropped, "
                    "assumed, or defaulted. Missing required input -> BLOCKED."
                ),
                rule=rule,
                field_name="aggregate_size_mm",
            )
        )
    elif not math.isfinite(aggregate_size_mm) or aggregate_size_mm <= 0.0:
        invalid_diagnostics.append(
            _malformed_value_diagnostic(
                aggregate_size_mm,
                field_name="aggregate_size_mm",
                rule=rule,
            )
        )

    if provided_clear_spacing_mm is not None and (
        not math.isfinite(provided_clear_spacing_mm)
        or provided_clear_spacing_mm <= 0.0
    ):
        invalid_diagnostics.append(
            _malformed_value_diagnostic(
                provided_clear_spacing_mm,
                field_name="provided_clear_spacing_mm",
                rule=rule,
            )
        )

    if invalid_diagnostics:
        return _invalid_step(
            gate, raw_inputs=raw_inputs, diagnostics=invalid_diagnostics
        )
    if missing_diagnostics:
        return _blocked_step(
            gate, raw_inputs=raw_inputs, diagnostics=missing_diagnostics
        )

    assert resolved_db is not None  # for type checkers
    assert aggregate_size_mm is not None  # for type checkers

    # 5. Required minimum clear spacing (max of the three clause items)
    limit_25_mm = BG_DETAIL_LONG_SPACING_001_MIN_CLEAR_MM
    limit_db_mm = resolved_db
    limit_agg_mm = BG_DETAIL_LONG_SPACING_001_AGGREGATE_FACTOR * aggregate_size_mm
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
            rule,
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
            rule,
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
        rule,
        normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=required_spacing_mm,
        unit="mm",
        outcome=EvaluationOutcome.FAIL,
        diagnostics=(fail_diag,),
        message=fail_diag.message,
    )


def evaluate_longitudinal_layer_spacing(
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
    arrangements, the typed ``layers_directly_aligned`` confirmation. Missing
    layer geometry (layer count or alignment) returns
    ``UNVERIFIED_RULE_BLOCKED`` (``MISSING_LAYER_COUNT`` /
    ``MISSING_LAYER_ALIGNMENT``); malformed values return ``INVALID_INPUT``.
    ``layer_count == 1`` returns ``NOT_APPLICABLE``; bundled bars return
    ``UNVERIFIED_RULE_BLOCKED`` (``UNVERIFIED_BUNDLE_RULE``, Clause 9-21-5-6
    pending visual verification).
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
    rule = gate.rule

    # 2. Bundled bars blocked (Clause 9-21-5-6 pending visual verification)
    if is_bundled:
        bundled_diag = EngineeringDiagnostic(
            code="UNVERIFIED_BUNDLE_RULE",
            severity=DiagnosticSeverity.BLOCK,
            message=(
                f"Rule '{rule_id}' is blocked: bundled bars require the "
                "equivalent bar diameter of Clause 9-21-5-6, which is "
                "text-located but not visually verified (VERIFY_PENDING). "
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
        return _blocked_step(
            gate, raw_inputs=raw_inputs, diagnostics=[bundled_diag]
        )

    # 3. Input validation: malformed -> INVALID_INPUT; missing -> BLOCKED
    invalid_diagnostics: List[EngineeringDiagnostic] = []
    invalid_diagnostics.extend(
        validate_beam_geometry(
            geometry, require_effective_depth=False, rule_id=rule_id
        )
    )

    if resolved_layers is None:
        missing_layer_diag = _missing_input_diagnostic(
            "MISSING_LAYER_COUNT",
            (
                "The number of reinforcement layers is required: supply "
                "layer_count or geometry.tension_rebar_groups with layer "
                "indices; the layer arrangement is never silently assumed. "
                "Missing layer geometry -> BLOCKED."
            ),
            rule=rule,
            field_name="layer_count",
        )
        return _blocked_step(
            gate, raw_inputs=raw_inputs, diagnostics=[missing_layer_diag]
        )
    if (
        isinstance(resolved_layers, bool)
        or not isinstance(resolved_layers, int)
        or resolved_layers < 1
    ):
        invalid_layers_diag = EngineeringDiagnostic(
            code="INVALID_LAYER_COUNT",
            severity=DiagnosticSeverity.ERROR,
            message=(
                f"layer_count must be an integer >= 1, got "
                f"{resolved_layers!r}."
            ),
            rule_id=rule_id,
            field_name="layer_count",
        )
        invalid_diagnostics.append(invalid_layers_diag)

    if resolved_spacing is not None and (
        not math.isfinite(resolved_spacing) or resolved_spacing <= 0.0
    ):
        invalid_diagnostics.append(
            _malformed_value_diagnostic(
                resolved_spacing,
                field_name="layer_clear_spacing_mm",
                rule=rule,
            )
        )

    if invalid_diagnostics:
        return _invalid_step(
            gate, raw_inputs=raw_inputs, diagnostics=invalid_diagnostics
        )

    # 4. Single-layer arrangement: rule is not applicable
    if resolved_layers == 1:
        return CalculationTraceStep.from_rule(
            rule,
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
    #    silently assumed); missing layer geometry -> BLOCKED.
    if layers_directly_aligned is None:
        align_diag = _missing_input_diagnostic(
            "MISSING_LAYER_ALIGNMENT",
            (
                "Vertical alignment confirmation is required for multi-layer "
                "arrangements (Clause 9-21-2-1-2 item i): supply "
                "layers_directly_aligned=True/False; alignment is a typed "
                "input and is never silently assumed. Missing layer geometry "
                "-> BLOCKED."
            ),
            rule=rule,
            field_name="layers_directly_aligned",
        )
        return _blocked_step(
            gate, raw_inputs=raw_inputs, diagnostics=[align_diag]
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
            rule,
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
            rule,
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
            rule,
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
        rule,
        normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=required_layer_spacing_mm,
        unit="mm",
        outcome=EvaluationOutcome.FAIL,
        diagnostics=(fail_diag,),
        message=fail_diag.message,
    )


def evaluate_beam_cover(
    geometry: BeamGeometry,
    *,
    exposure: Optional[ConcreteCoverExposureClass] = None,
    member_class: Optional[ConcreteCoverMemberClass] = None,
    reinforcement_type: Optional[CoverReinforcementType] = None,
    cover_bar_diameter_mm: Optional[float] = None,
    provided_cover_mm: Optional[float] = None,
    is_bundled: bool = False,
    has_headed_shear_reinforcement: bool = False,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate Mabhas 9 minimum concrete cover (BG-DETAIL-COVER-001).

    Verified source: Mabhas 9 (1399), Clauses 9-4-9-4, 9-4-9-5, 9-4-9-5-1..3
    and Table 9-4-6, PDF pp. 92-93 / Printed pp. 71-72 (normal, non-corrosive
    conditions). Table 9-4-6 rows:

    - Permanent contact with earth (cast against earth), all members/all bars:
      75 mm.
    - Air/weather or non-permanent earth contact, all members:
      db 18-58 mm -> 50 mm; bars/wires db <= 16 mm -> 40 mm.
    - No air/earth contact:
      - slabs, joists, walls: db > 36 mm -> 40 mm; db <= 34 mm -> 20 mm;
      - beams, columns, pedestals, tension members: 40 mm (longitudinal
        bars, stirrups, ties, spirals, hoops).

    Headed shear reinforcement (Clause 9-4-9-5-3): cover over the head/plate
    shall not be less than the member cover — the same computed minimum
    applies (flagged via ``has_headed_shear_reinforcement``).

    Required typed inputs (never assumed; missing -> BLOCKED): the exposure
    condition, the member class, and the reinforcement type (plus the
    governing bar diameter for the diameter-classed rows). An unknown member
    type (non-enum value) returns ``INVALID_INPUT``. Corrosive/unusual
    environments are routed to Appendix 9-پ1 per Clauses 9-4-9-6/9-4-9-7 —
    deterministically ``UNVERIFIED_RULE_BLOCKED``; Appendix 9-پ1 values are
    never computed here. The bundled-group rule (Clause 9-4-9-5-2 via
    9-21-5-6) is blocked as ``UNVERIFIED_BUNDLE_RULE``. Diameter classes
    outside the visible table classes (weather: (16, 18) mm or > 58 mm;
    unexposed slab/joist/wall: (34, 36] mm) are never interpolated ->
    ``UNVERIFIED_RULE_BLOCKED``.
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
        "member_class": (
            member_class.value
            if isinstance(member_class, ConcreteCoverMemberClass)
            else member_class
        ),
        "reinforcement_type": (
            reinforcement_type.value if reinforcement_type is not None else None
        ),
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
    rule = gate.rule

    # 2. Exposure condition is required (never assumed) -> missing: BLOCKED
    if exposure is None:
        exposure_diag = _missing_input_diagnostic(
            "MISSING_COVER_EXPOSURE_CLASS",
            (
                "The concrete cover exposure condition is required (Table "
                "9-4-6 classes) and is never silently assumed. Missing "
                "exposure -> BLOCKED."
            ),
            rule=rule,
            field_name="exposure",
        )
        return _blocked_step(
            gate, raw_inputs=raw_inputs, diagnostics=[exposure_diag]
        )

    # 3. Corrosive / unusual environment routed to Appendix 9-پ1 (blocked;
    #    its durability values are NOT computed here)
    if exposure == ConcreteCoverExposureClass.CORROSIVE_ENVIRONMENT:
        corrosive_diag = EngineeringDiagnostic(
            code="CORROSIVE_EXPOSURE_BLOCKED_APPENDIX_9P1",
            severity=DiagnosticSeverity.BLOCK,
            message=(
                f"Rule '{rule_id}' is blocked: corrosive or unusual "
                "environments are governed by Mabhas 9 Appendix 9-پ1 "
                "(durability) per Clauses 9-4-9-6/9-4-9-7; Appendix 9-پ1 "
                "values are not visually verified and are never computed "
                "here. UNVERIFIED_RULE_BLOCKED."
            ),
            rule_id=rule_id,
            field_name="exposure",
            required_verification=(
                "Visually verify Mabhas 9 Appendix 9-پ1 durability cover "
                "requirements before executing corrosive-environment cover "
                "checks."
            ),
        )
        return _blocked_step(
            gate, raw_inputs=raw_inputs, diagnostics=[corrosive_diag]
        )

    # 4. Member class: missing -> BLOCKED; unknown member type -> INVALID_INPUT
    #    (runtime guard via an object-typed local: untyped callers can pass
    #    arbitrary values; typed callers are covered by the signature).
    member_class_raw: object = member_class
    if member_class_raw is None:
        member_missing_diag = _missing_input_diagnostic(
            "MISSING_COVER_MEMBER_CLASS",
            (
                "The member type is required (Table 9-4-6 rows distinguish "
                "slabs/joists/walls from beams/columns/pedestals/tension "
                "members) and is never silently assumed. Missing member type "
                "-> BLOCKED."
            ),
            rule=rule,
            field_name="member_class",
        )
        return _blocked_step(
            gate, raw_inputs=raw_inputs, diagnostics=[member_missing_diag]
        )
    if not isinstance(member_class_raw, ConcreteCoverMemberClass):
        member_unknown_diag = EngineeringDiagnostic(
            code="UNKNOWN_COVER_MEMBER_CLASS",
            severity=DiagnosticSeverity.ERROR,
            message=(
                f"Unknown member type {member_class_raw!r}: Table 9-4-6 cover "
                "rows are verified only for BEAM, COLUMN, PEDESTAL, "
                "TENSION_MEMBER, SLAB, JOIST, and WALL. INVALID_INPUT."
            ),
            rule_id=rule_id,
            field_name="member_class",
        )
        return _invalid_step(
            gate, raw_inputs=raw_inputs, diagnostics=[member_unknown_diag]
        )
    member_class_typed: ConcreteCoverMemberClass = member_class_raw

    # 5. Reinforcement type: required typed input (never assumed)
    reinforcement_type_raw: object = reinforcement_type
    if reinforcement_type_raw is None:
        rf_missing_diag = _missing_input_diagnostic(
            "MISSING_COVER_REINFORCEMENT_TYPE",
            (
                "The reinforcement type (LONGITUDINAL / TRANSVERSE, i.e. "
                "longitudinal bars vs stirrups/ties/spirals/hoops) whose "
                "cover is checked is required and is never silently assumed. "
                "Missing reinforcement type -> BLOCKED."
            ),
            rule=rule,
            field_name="reinforcement_type",
        )
        return _blocked_step(
            gate, raw_inputs=raw_inputs, diagnostics=[rf_missing_diag]
        )
    if not isinstance(reinforcement_type_raw, CoverReinforcementType):
        rf_unknown_diag = EngineeringDiagnostic(
            code="UNKNOWN_COVER_REINFORCEMENT_TYPE",
            severity=DiagnosticSeverity.ERROR,
            message=(
                f"Unknown reinforcement type {reinforcement_type_raw!r}: "
                "verified values are LONGITUDINAL and TRANSVERSE. "
                "INVALID_INPUT."
            ),
            rule_id=rule_id,
            field_name="reinforcement_type",
        )
        return _invalid_step(
            gate, raw_inputs=raw_inputs, diagnostics=[rf_unknown_diag]
        )
    reinforcement_type_typed: CoverReinforcementType = reinforcement_type_raw

    # 6. Bundled bars blocked (Clause 9-4-9-5-2 -> equivalent diameter 9-21-5-6)
    if is_bundled:
        bundled_diag = EngineeringDiagnostic(
            code="UNVERIFIED_BUNDLE_RULE",
            severity=DiagnosticSeverity.BLOCK,
            message=(
                f"Rule '{rule_id}' is blocked: the bundled-group cover rule "
                "(Clause 9-4-9-5-2: min(equivalent group diameter, 75 mm "
                "permanent-earth / 50 mm otherwise)) requires the Clause "
                "9-21-5-6 equivalent diameter, which is text-located "
                "(VERIFY_PENDING) and never invented. "
                "UNVERIFIED_RULE_BLOCKED."
            ),
            rule_id=rule_id,
            field_name="is_bundled",
            required_verification=(
                "Visually verify Mabhas 9 Clause 9-21-5-6 (bundle equivalent "
                "diameter) against the source PDF before unblocking bundled "
                "bar cover."
            ),
        )
        return _blocked_step(
            gate, raw_inputs=raw_inputs, diagnostics=[bundled_diag]
        )

    # 7. Malformed numeric values -> INVALID_INPUT
    invalid_diagnostics: List[EngineeringDiagnostic] = []
    invalid_diagnostics.extend(
        validate_beam_geometry(
            geometry, require_effective_depth=False, rule_id=rule_id
        )
    )

    if resolved_db is not None and (
        not math.isfinite(resolved_db) or resolved_db <= 0.0
    ):
        invalid_diagnostics.append(
            _malformed_value_diagnostic(
                resolved_db,
                field_name="cover_bar_diameter_mm",
                rule=rule,
            )
        )

    if resolved_cover is not None and (
        not math.isfinite(resolved_cover) or resolved_cover <= 0.0
    ):
        invalid_diagnostics.append(
            _malformed_value_diagnostic(
                resolved_cover,
                field_name="provided_cover_mm",
                rule=rule,
            )
        )

    if invalid_diagnostics:
        return _invalid_step(
            gate, raw_inputs=raw_inputs, diagnostics=invalid_diagnostics
        )

    # 8. Required minimum cover from Table 9-4-6
    rf_label = (
        "longitudinal bars"
        if reinforcement_type_typed == CoverReinforcementType.LONGITUDINAL
        else "stirrups/ties/spirals/hoops"
    )
    intermediates: Dict[str, float] = {}
    basis: str
    if exposure == ConcreteCoverExposureClass.PERMANENT_EARTH_CONTACT:
        required_cover_mm = BG_DETAIL_COVER_001_PERMANENT_EARTH_MM
        basis = (
            f"permanent earth contact (Table 9-4-6 row i; {rf_label}; "
            f"{member_class_typed.value})"
        )
    elif exposure == ConcreteCoverExposureClass.WEATHER_OR_EARTH_CONTACT:
        if resolved_db is None:
            db_missing_diag = _missing_input_diagnostic(
                "MISSING_COVER_BAR_DIAMETER",
                (
                    "Governing bar diameter db is required for air/weather or "
                    "non-permanent earth contact exposure (Table 9-4-6 "
                    "diameter classes: <= 16 mm -> 40 mm; 18-58 mm -> 50 mm); "
                    "supply cover_bar_diameter_mm or "
                    "geometry.tension_rebar_groups. Never silently assumed; "
                    "BLOCKED."
                ),
                rule=rule,
                field_name="cover_bar_diameter_mm",
            )
            return _blocked_step(
                gate, raw_inputs=raw_inputs, diagnostics=[db_missing_diag]
            )
        intermediates["db_governing_mm"] = resolved_db
        if resolved_db <= BG_DETAIL_COVER_001_WEATHER_MAX_SMALL_DB_MM:
            required_cover_mm = BG_DETAIL_COVER_001_WEATHER_DB_LE_16_MM
            basis = (
                f"air/earth contact, db <= 16 mm (Table 9-4-6 row ii; "
                f"{rf_label})"
            )
        elif (
            BG_DETAIL_COVER_001_WEATHER_MIN_LARGE_DB_MM
            <= resolved_db
            <= BG_DETAIL_COVER_001_WEATHER_MAX_LARGE_DB_MM
        ):
            required_cover_mm = BG_DETAIL_COVER_001_WEATHER_DB_18_TO_58_MM
            basis = (
                f"air/earth contact, db 18-58 mm (Table 9-4-6 row ii; "
                f"{rf_label})"
            )
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
                rule,
                normalized_inputs=raw_inputs,
                intermediate_values=intermediates,
                final_result=None,
                unit="mm",
                outcome=EvaluationOutcome.UNVERIFIED_RULE_BLOCKED,
                diagnostics=(gap_diag,),
                message=gap_diag.message,
            )
    else:
        # NOT_EXPOSED (only remaining member after steps 2-3)
        if member_class_typed in (
            ConcreteCoverMemberClass.BEAM,
            ConcreteCoverMemberClass.COLUMN,
            ConcreteCoverMemberClass.PEDESTAL,
            ConcreteCoverMemberClass.TENSION_MEMBER,
        ):
            required_cover_mm = BG_DETAIL_COVER_001_BEAM_NOT_EXPOSED_MM
            basis = (
                "no air/earth contact, beams/columns/pedestals/tension "
                f"members (Table 9-4-6 row iv; {rf_label})"
            )
        else:
            # slabs, joists, walls: db-classed row (iii)
            if resolved_db is None:
                db_missing_slab_diag = _missing_input_diagnostic(
                    "MISSING_COVER_BAR_DIAMETER",
                    (
                        "Governing bar diameter db is required for "
                        "unexposed slabs/joists/walls (Table 9-4-6 row iii: "
                        "db <= 34 mm -> 20 mm; db > 36 mm -> 40 mm). "
                        "Never silently assumed; BLOCKED."
                    ),
                    rule=rule,
                    field_name="cover_bar_diameter_mm",
                )
                return _blocked_step(
                    gate, raw_inputs=raw_inputs, diagnostics=[db_missing_slab_diag]
                )
            intermediates["db_governing_mm"] = resolved_db
            if resolved_db <= BG_DETAIL_COVER_001_SLAB_MAX_SMALL_DB_MM:
                required_cover_mm = (
                    BG_DETAIL_COVER_001_SLAB_NOT_EXPOSED_SMALL_DB_MM
                )
                basis = (
                    f"no air/earth contact, {member_class_typed.value.lower()}-class "
                    "members (slabs/joists/walls), db <= 34 mm (Table 9-4-6 "
                    "row iii)"
                )
            elif resolved_db > BG_DETAIL_COVER_001_SLAB_MIN_LARGE_DB_MM:
                required_cover_mm = (
                    BG_DETAIL_COVER_001_SLAB_NOT_EXPOSED_LARGE_DB_MM
                )
                basis = (
                    f"no air/earth contact, {member_class_typed.value.lower()}-class "
                    "members (slabs/joists/walls), db > 36 mm (Table 9-4-6 "
                    "row iii)"
                )
            else:
                slab_gap_diag = EngineeringDiagnostic(
                    code="UNVERIFIED_COVER_DIAMETER_CLASS",
                    severity=DiagnosticSeverity.BLOCK,
                    message=(
                        f"Rule '{rule_id}' is blocked: governing bar "
                        f"diameter db = {resolved_db} mm lies in the Table "
                        "9-4-6 uncovered interval (34, 36] mm for "
                        "slabs/joists/walls; the interval is never "
                        "interpolated. UNVERIFIED_RULE_BLOCKED "
                        "(UNSUPPORTED_CONFIGURATION)."
                    ),
                    rule_id=rule_id,
                    field_name="cover_bar_diameter_mm",
                    required_verification=(
                        "Visually verify Table 9-4-6 treatment of bar "
                        "diameters in the (34, 36] mm interval for "
                        "slabs/joists/walls before executing."
                    ),
                )
                return CalculationTraceStep.from_rule(
                    rule,
                    normalized_inputs=raw_inputs,
                    intermediate_values=intermediates,
                    final_result=None,
                    unit="mm",
                    outcome=EvaluationOutcome.UNVERIFIED_RULE_BLOCKED,
                    diagnostics=(slab_gap_diag,),
                    message=slab_gap_diag.message,
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

    # 9. Verify provided cover when available
    if resolved_cover is None:
        return CalculationTraceStep.from_rule(
            rule,
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
            rule,
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
        rule,
        normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=required_cover_mm,
        unit="mm",
        outcome=EvaluationOutcome.FAIL,
        diagnostics=(fail_diag,),
        message=fail_diag.message,
    )
