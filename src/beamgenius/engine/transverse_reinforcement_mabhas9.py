"""Mabhas 9 (1399) Phase 2F Stage G transverse-reinforcement evaluators.

Verified production rules (visually re-verified 2026-10-06 from the committed
Mabhas 9, 1399 5th ed. evidence scan ``phase2f-source-442-472`` @ ``df8067a``;
footer-confirmed Printed pp. 443-450 / PDF pp. 463-470):

- ``BG-TRANS-TIE-SHEAR-EXTENT-001``: confining tie used as shear reinforcement
  extends to the effective depth d from the compression face (9-21-6-1-1),
- ``BG-TRANS-CLOSED-TIE-LAP-001``: two-U-tie closed-tie leg lap >= anchorage/3,
  full-depth lap sufficient when depth >= 450 mm and force/leg < 40 kN
  (9-21-6-1-8),
- ``BG-TRANS-TIE-SPACING-001``: tie clear spacing >= d_agg/3 and c-c spacing <=
  min(16*db_long, 48*db_trans, smallest member dim) (9-21-6-2-1),
- ``BG-TRANS-TIE-DIA-001``: minimum tie diameter 10 mm (db_long <= 32 mm) /
  12 mm (db_long >= 34 mm or bundled); 32 < db_long < 34 mm -> BLOCKED
  (9-21-6-2-2),
- ``BG-TRANS-RECT-TIE-001``: laterally-unrestrained longitudinal bar clear
  spacing <= 150 mm from the nearest restrained longitudinal bar (9-21-6-2-4-ب),
- ``BG-TRANS-CIRC-TIE-001``: circular-tie end overlap >= 150 mm (9-21-6-2-5-الف),
- ``BG-TRANS-SPIRAL-SPACING-001``: spiral clear spacing >= max(d_agg/3, 25 mm)
  and pitch <= 75 mm (9-21-6-3-1),
- ``BG-TRANS-SPIRAL-DIA-001``: spiral wire/bar diameter >= 10 mm (9-21-6-3-2),
- ``BG-TRANS-SPIRAL-RATIO-001``: spiral volumetric ratio
  rho_s >= 0.45*(A_g/A_ch - 1)*f'c/f_y_tau with f_y_tau <= 700 MPa
  [Eq. (9-21-8)] (9-21-6-3-3),
- ``BG-TRANS-SPIRAL-ANCHOR-001``: spiral end anchorage by 1.5 extra turns at
  each end (9-21-6-3-4),
- ``BG-TRANS-SPIRAL-LAP-001``: spiral lap splice length = max(k*d_b, 300 mm),
  k = 48 or 72 per Table 9-21-7 (9-21-6-3-6).

Explicitly NOT promoted (kept BLOCKED / VERIFY_PENDING — out-of-scope
dependencies or unresolved semantics; see the blocked sentinel rules
``BG-TRANS-TIE-ANCHOR-PENDING`` (9-21-6-1-3 boundary ambiguity),
``BG-TRANS-WIRE-TIE-PENDING`` (9-21-6-1-4/-1-5 welded-wire positioning),
``BG-TRANS-TORSION-TIE-PENDING`` (9-21-6-1-6/-1-7/-2-7 hook geometry),
``BG-TRANS-WIRE-SUBST-PENDING`` (9-21-6-2-3 -> Clause 9-4-8),
``BG-TRANS-SPIRAL-SPLICE-SEL-PENDING`` (9-21-6-3-5 -> Clause 9-21-4-7), and
``BG-TRANS-DORGIR-PENDING`` (9-21-6-4 seismic hook)).

Deterministic contract of every evaluator (in order):

1. Central Gatekeeper check (``evaluate_rule_gate``) runs FIRST.
2. Missing required engineering inputs return ``UNVERIFIED_RULE_BLOCKED``
   (BLOCKED) with ``MISSING_*`` diagnostics — missing values are never
   assumed or defaulted.
3. Malformed input values (non-finite, non-positive, wrong type) return
   ``INVALID_INPUT``.
4. Verified violations return an explicit ``FAIL``; out-of-scope
   configurations return ``NOT_APPLICABLE``. BLOCKED is never converted to
   PASS. A configuration whose (type, coating, end-condition) combination is
   not printed in Table 9-21-7 is deterministically BLOCKED.
5. No National Building Regulations Chapter 9-4 / Chapter 10 / Mostofinejad
   dependency is imported or invented; this module does not import the
   reference package and reads no source file at runtime.

Import explicitly, e.g.::

    from beamgenius.engine.transverse_reinforcement_mabhas9 import (
        evaluate_spiral_ratio,
    )
"""

from __future__ import annotations

import math
from enum import Enum
from typing import Dict, List, Optional

from beamgenius.domain.enums import (
    DiagnosticSeverity,
    EvaluationOutcome,
    JurisdictionMode,
)
from beamgenius.domain.trace import (
    CalculationTraceStep,
    EngineeringDiagnostic,
    RuleReference,
    ScalarInputValue,
)
from beamgenius.engine.detailing_spacing_mabhas9 import (
    _blocked_step,
    _invalid_step,
    _malformed_value_diagnostic,
    _missing_input_diagnostic,
)
from beamgenius.registry.catalog import (
    RULE_BG_TRANS_CIRC_TIE_001,
    RULE_BG_TRANS_CLOSED_TIE_LAP_001,
    RULE_BG_TRANS_RECT_TIE_001,
    RULE_BG_TRANS_SPIRAL_ANCHOR_001,
    RULE_BG_TRANS_SPIRAL_DIA_001,
    RULE_BG_TRANS_SPIRAL_LAP_001,
    RULE_BG_TRANS_SPIRAL_RATIO_001,
    RULE_BG_TRANS_SPIRAL_SPACING_001,
    RULE_BG_TRANS_TIE_DIA_001,
    RULE_BG_TRANS_TIE_SHEAR_EXTENT_001,
    RULE_BG_TRANS_TIE_SPACING_001,
)
from beamgenius.registry.gatekeeper import GatekeeperDecision, evaluate_rule_gate


# --- Clause 9-21-6-2-1 tie spacing (PDF p. 466 / Printed p. 446)
BG_TRANS_TIE_CLEAR_AGG_DIVISOR: float = 3.0
BG_TRANS_TIE_CC_LONG_FACTOR: float = 16.0
BG_TRANS_TIE_CC_TRANS_FACTOR: float = 48.0

# --- Clause 9-21-6-2-2 minimum tie diameter (PDF p. 466 / Printed p. 446)
BG_TRANS_TIE_DIA_SMALL_MM: float = 10.0
BG_TRANS_TIE_DIA_LARGE_MM: float = 12.0
BG_TRANS_TIE_DIA_SMALL_MAX_DB_MM: float = 32.0
BG_TRANS_TIE_DIA_LARGE_MIN_DB_MM: float = 34.0

# --- Clause 9-21-6-2-4-ب unrestrained longitudinal bar (PDF p. 467 / Printed p. 447)
BG_TRANS_RECT_TIE_UNRESTRAINED_MAX_CLEAR_MM: float = 150.0

# --- Clause 9-21-6-2-5-الف circular-tie overlap (PDF p. 467 / Printed p. 447)
BG_TRANS_CIRC_TIE_MIN_OVERLAP_MM: float = 150.0

# --- Clause 9-21-6-3-1 spiral spacing (PDF p. 468 / Printed p. 448)
BG_TRANS_SPIRAL_CLEAR_AGG_DIVISOR: float = 3.0
BG_TRANS_SPIRAL_CLEAR_MIN_MM: float = 25.0
BG_TRANS_SPIRAL_MAX_PITCH_MM: float = 75.0

# --- Clause 9-21-6-3-2 minimum spiral diameter (PDF p. 468 / Printed p. 448)
BG_TRANS_SPIRAL_MIN_DIA_MM: float = 10.0

# --- Clause 9-21-6-3-3 Eq. (9-21-8) spiral ratio (PDF p. 468 / Printed p. 448)
BG_TRANS_SPIRAL_RATIO_COEFF: float = 0.45
BG_TRANS_SPIRAL_FYT_MAX_MPA: float = 700.0

# --- Clause 9-21-6-3-4 spiral anchorage (PDF p. 468 / Printed p. 448)
BG_TRANS_SPIRAL_ANCHOR_EXTRA_TURNS: float = 1.5

# --- Clause 9-21-6-3-6 / Table 9-21-7 spiral lap splice (PDF p. 469 / Printed p. 449)
BG_TRANS_SPIRAL_LAP_MIN_MM: float = 300.0

# --- Clause 9-21-6-1-8 two-U-tie closed-tie leg lap (PDF pp. 465-466 / Printed pp. 445-446)
BG_TRANS_CLOSED_TIE_LAP_DIVISOR: float = 3.0
BG_TRANS_CLOSED_TIE_FULL_DEPTH_MIN_DEPTH_MM: float = 450.0
BG_TRANS_CLOSED_TIE_FULL_DEPTH_MAX_FORCE_N: float = 40_000.0


class SpiralSpliceBarType(str, Enum):
    """Spliced bar/wire type per Table 9-21-7 (Clause 9-21-6-3-6)."""

    DEFORMED_BAR = "deformed_bar"
    DEFORMED_WIRE = "deformed_wire"
    PLAIN_BAR = "plain_bar"
    PLAIN_WIRE = "plain_wire"


class SpiralSpliceCoating(str, Enum):
    """Coating class per Table 9-21-7 (Clause 9-21-6-3-6)."""

    UNCOATED = "uncoated"
    GALVANIZED = "galvanized"
    EPOXY = "epoxy"
    DUAL_COATED = "dual_coated"


class SpiralSpliceEndCondition(str, Enum):
    """Spliced-bar end condition per Table 9-21-7 (Clause 9-21-6-3-6)."""

    NO_HOOK = "no_hook"
    STANDARD_TRANSVERSE_HOOK = "standard_transverse_hook"


# Table 9-21-7 multiplier (k in lap = k*d_b) keyed by
# (bar/wire type, coating, end condition). Values are the verbatim visual
# reads of Table 9-21-7 (PDF p. 469 / Printed p. 449). Any combination not
# listed here is not printed in the source table and is deterministically
# BLOCKED by evaluate_spiral_lap_splice (never interpreted).
_TABLE_9_21_7_MULTIPLIER: Dict[
    tuple[SpiralSpliceBarType, SpiralSpliceCoating, SpiralSpliceEndCondition], float
] = {
    # میلگرد آجدار (deformed bar)
    (SpiralSpliceBarType.DEFORMED_BAR, SpiralSpliceCoating.UNCOATED, SpiralSpliceEndCondition.NO_HOOK): 48.0,
    (SpiralSpliceBarType.DEFORMED_BAR, SpiralSpliceCoating.GALVANIZED, SpiralSpliceEndCondition.NO_HOOK): 48.0,
    (SpiralSpliceBarType.DEFORMED_BAR, SpiralSpliceCoating.EPOXY, SpiralSpliceEndCondition.NO_HOOK): 72.0,
    (SpiralSpliceBarType.DEFORMED_BAR, SpiralSpliceCoating.DUAL_COATED, SpiralSpliceEndCondition.NO_HOOK): 72.0,
    (SpiralSpliceBarType.DEFORMED_BAR, SpiralSpliceCoating.EPOXY, SpiralSpliceEndCondition.STANDARD_TRANSVERSE_HOOK): 48.0,
    (SpiralSpliceBarType.DEFORMED_BAR, SpiralSpliceCoating.DUAL_COATED, SpiralSpliceEndCondition.STANDARD_TRANSVERSE_HOOK): 48.0,
    # سیم آجدار (deformed wire)
    (SpiralSpliceBarType.DEFORMED_WIRE, SpiralSpliceCoating.UNCOATED, SpiralSpliceEndCondition.NO_HOOK): 48.0,
    (SpiralSpliceBarType.DEFORMED_WIRE, SpiralSpliceCoating.EPOXY, SpiralSpliceEndCondition.NO_HOOK): 72.0,
    (SpiralSpliceBarType.DEFORMED_WIRE, SpiralSpliceCoating.EPOXY, SpiralSpliceEndCondition.STANDARD_TRANSVERSE_HOOK): 48.0,
    # میلگرد ساده (plain bar)
    (SpiralSpliceBarType.PLAIN_BAR, SpiralSpliceCoating.UNCOATED, SpiralSpliceEndCondition.NO_HOOK): 72.0,
    (SpiralSpliceBarType.PLAIN_BAR, SpiralSpliceCoating.GALVANIZED, SpiralSpliceEndCondition.NO_HOOK): 72.0,
    (SpiralSpliceBarType.PLAIN_BAR, SpiralSpliceCoating.UNCOATED, SpiralSpliceEndCondition.STANDARD_TRANSVERSE_HOOK): 48.0,
    (SpiralSpliceBarType.PLAIN_BAR, SpiralSpliceCoating.GALVANIZED, SpiralSpliceEndCondition.STANDARD_TRANSVERSE_HOOK): 48.0,
    # سیم ساده (plain wire)
    (SpiralSpliceBarType.PLAIN_WIRE, SpiralSpliceCoating.UNCOATED, SpiralSpliceEndCondition.NO_HOOK): 72.0,
    (SpiralSpliceBarType.PLAIN_WIRE, SpiralSpliceCoating.UNCOATED, SpiralSpliceEndCondition.STANDARD_TRANSVERSE_HOOK): 48.0,
}


def _pass_step(
    gate: GatekeeperDecision,
    *,
    raw_inputs: Dict[str, ScalarInputValue],
    intermediates: Dict[str, float],
    final_result: Optional[float],
    unit: str,
    message: str,
) -> CalculationTraceStep:
    """Build a PASS step (verified requirement satisfied)."""
    return CalculationTraceStep.from_rule(
        gate.rule,
        normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=final_result,
        unit=unit,
        outcome=EvaluationOutcome.PASS,
        diagnostics=(),
        message=message,
    )


def _computed_step(
    gate: GatekeeperDecision,
    *,
    raw_inputs: Dict[str, ScalarInputValue],
    intermediates: Dict[str, float],
    final_result: float,
    unit: str,
    message: str,
) -> CalculationTraceStep:
    """Build a COMPUTED step (deterministic value produced)."""
    return CalculationTraceStep.from_rule(
        gate.rule,
        normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=final_result,
        unit=unit,
        outcome=EvaluationOutcome.COMPUTED,
        diagnostics=(),
        message=message,
    )


def _not_applicable_step(
    gate: GatekeeperDecision,
    *,
    raw_inputs: Dict[str, ScalarInputValue],
    unit: str,
    message: str,
) -> CalculationTraceStep:
    """Build a NOT_APPLICABLE step through an allowed gate."""
    return CalculationTraceStep.from_rule(
        gate.rule,
        normalized_inputs=raw_inputs,
        intermediate_values={},
        final_result=None,
        unit=unit,
        outcome=EvaluationOutcome.NOT_APPLICABLE,
        diagnostics=(),
        message=message,
    )


def _fail_step(
    gate: GatekeeperDecision,
    *,
    raw_inputs: Dict[str, ScalarInputValue],
    intermediates: Dict[str, float],
    final_result: Optional[float],
    unit: str,
    diagnostic: EngineeringDiagnostic,
) -> CalculationTraceStep:
    """Build a FAIL step carrying a single ERROR diagnostic."""
    return CalculationTraceStep.from_rule(
        gate.rule,
        normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=final_result,
        unit=unit,
        outcome=EvaluationOutcome.FAIL,
        diagnostics=(diagnostic,),
        message=diagnostic.message,
    )


def _require_positive(
    value: Optional[float],
    *,
    code: str,
    field_name: str,
    message: str,
    rule: RuleReference,
    missing: List[EngineeringDiagnostic],
    invalid: List[EngineeringDiagnostic],
) -> None:
    """Classify a required positive scalar as missing or malformed."""
    if value is None:
        missing.append(
            _missing_input_diagnostic(code, message, rule=rule, field_name=field_name)
        )
    elif not math.isfinite(value) or value <= 0.0:
        invalid.append(
            _malformed_value_diagnostic(value, field_name=field_name, rule=rule)
        )


# --- BG-TRANS-TIE-SHEAR-EXTENT-001 (Clause 9-21-6-1-1, PDF p. 463 / Printed p. 443)
def evaluate_tie_shear_extent(
    *,
    used_as_shear_reinforcement: Optional[bool] = None,
    tie_extent_from_compression_face_mm: Optional[float] = None,
    effective_depth_mm: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate the shear-reinforcement tie extent (BG-TRANS-TIE-SHEAR-EXTENT-001).

    Verified source: Mabhas 9 (1399), Clause 9-21-6-1-1, PDF p. 463 /
    Printed p. 443: where a tie is used as shear reinforcement, it must
    extend to the effective depth d measured from the compression face.

    ``used_as_shear_reinforcement`` is a required typed classification (never
    assumed). If the tie is not used as shear reinforcement the d-extent
    check is NOT_APPLICABLE. Otherwise the provided tie extent must be at
    least the effective depth d.
    """
    rule_id = RULE_BG_TRANS_TIE_SHEAR_EXTENT_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "used_as_shear_reinforcement": used_as_shear_reinforcement,
        "tie_extent_from_compression_face_mm": tie_extent_from_compression_face_mm,
        "effective_depth_mm": effective_depth_mm,
    }

    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")
    rule = gate.rule

    used_raw: object = used_as_shear_reinforcement
    if used_raw is None:
        return _blocked_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _missing_input_diagnostic(
                    "MISSING_USED_AS_SHEAR_REINFORCEMENT",
                    (
                        "Whether the tie is used as shear reinforcement is "
                        "required to apply the effective-depth extent of "
                        "Clause 9-21-6-1-1; it is never assumed. Missing "
                        "required input -> BLOCKED."
                    ),
                    rule=rule,
                    field_name="used_as_shear_reinforcement",
                )
            ],
        )
    if not isinstance(used_raw, bool):
        return _invalid_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                EngineeringDiagnostic(
                    code="INVALID_USED_AS_SHEAR_REINFORCEMENT",
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        "used_as_shear_reinforcement must be a bool, got "
                        f"{used_raw!r}."
                    ),
                    rule_id=rule_id,
                    field_name="used_as_shear_reinforcement",
                )
            ],
        )

    if not used_raw:
        return _not_applicable_step(
            gate,
            raw_inputs=raw_inputs,
            unit="mm",
            message=(
                "NOT_APPLICABLE: the effective-depth extent of Clause "
                "9-21-6-1-1 applies only where the tie is used as shear "
                "reinforcement; this tie is not, so the d-extent check does "
                "not apply."
            ),
        )

    invalid: List[EngineeringDiagnostic] = []
    missing: List[EngineeringDiagnostic] = []
    _require_positive(
        tie_extent_from_compression_face_mm,
        code="MISSING_TIE_EXTENT",
        field_name="tie_extent_from_compression_face_mm",
        message=(
            "The tie extent from the compression face is required for the "
            "Clause 9-21-6-1-1 check; it is never assumed. Missing required "
            "input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    _require_positive(
        effective_depth_mm,
        code="MISSING_EFFECTIVE_DEPTH",
        field_name="effective_depth_mm",
        message=(
            "The effective depth d is required for the Clause 9-21-6-1-1 "
            "check; it is never assumed. Missing required input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    if invalid:
        return _invalid_step(gate, raw_inputs=raw_inputs, diagnostics=invalid)
    if missing:
        return _blocked_step(gate, raw_inputs=raw_inputs, diagnostics=missing)
    assert tie_extent_from_compression_face_mm is not None
    assert effective_depth_mm is not None

    intermediates: Dict[str, float] = {
        "tie_extent_from_compression_face_mm": tie_extent_from_compression_face_mm,
        "effective_depth_mm": effective_depth_mm,
        "required_extent_mm": effective_depth_mm,
    }
    if tie_extent_from_compression_face_mm >= effective_depth_mm:
        return _pass_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates=intermediates,
            final_result=effective_depth_mm,
            unit="mm",
            message=(
                f"PASS: shear-reinforcement tie extends {tie_extent_from_compression_face_mm} mm "
                f"from the compression face >= effective depth d = {effective_depth_mm} mm "
                "per Clause 9-21-6-1-1."
            ),
        )
    diag = EngineeringDiagnostic(
        code="TIE_EXTENT_LESS_THAN_EFFECTIVE_DEPTH",
        severity=DiagnosticSeverity.ERROR,
        message=(
            f"FAIL: a tie used as shear reinforcement must extend to the "
            f"effective depth d = {effective_depth_mm} mm from the compression "
            f"face per Clause 9-21-6-1-1; the provided extent "
            f"{tie_extent_from_compression_face_mm} mm is insufficient."
        ),
        rule_id=rule_id,
        field_name="tie_extent_from_compression_face_mm",
    )
    return _fail_step(
        gate,
        raw_inputs=raw_inputs,
        intermediates=intermediates,
        final_result=effective_depth_mm,
        unit="mm",
        diagnostic=diag,
    )


# --- BG-TRANS-CLOSED-TIE-LAP-001 (Clause 9-21-6-1-8, PDF pp. 465-466 / Printed pp. 445-446)
def evaluate_closed_tie_lap(
    *,
    anchorage_length_mm: Optional[float] = None,
    total_depth_mm: Optional[float] = None,
    force_per_leg_n: Optional[float] = None,
    provided_leg_lap_mm: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate the two-U-tie closed-tie leg lap (BG-TRANS-CLOSED-TIE-LAP-001).

    Verified source: Mabhas 9 (1399), Clause 9-21-6-1-8, PDF pp. 465-466 /
    Printed pp. 445-446: a closed tie may be built from two U-ties; the
    U-tie leg lap must be at least one third of the anchorage length. In
    members with total depth >= 450 mm and force per leg (f_y * tie area)
    < 40 kN, a leg lap continuing across the full member depth is
    sufficient.

    The anchorage length is a caller-provided verified value (never computed
    here; missing -> BLOCKED). Total depth, force per leg, and the provided
    leg lap are required typed inputs.
    """
    rule_id = RULE_BG_TRANS_CLOSED_TIE_LAP_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "anchorage_length_mm": anchorage_length_mm,
        "total_depth_mm": total_depth_mm,
        "force_per_leg_n": force_per_leg_n,
        "provided_leg_lap_mm": provided_leg_lap_mm,
    }

    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")
    rule = gate.rule

    invalid: List[EngineeringDiagnostic] = []
    missing: List[EngineeringDiagnostic] = []
    _require_positive(
        anchorage_length_mm,
        code="MISSING_ANCHORAGE_LENGTH",
        field_name="anchorage_length_mm",
        message=(
            "The anchorage length is a caller-provided verified value "
            "required for the Clause 9-21-6-1-8 leg-lap check; it is never "
            "computed or assumed here. Missing required input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    _require_positive(
        total_depth_mm,
        code="MISSING_TOTAL_DEPTH",
        field_name="total_depth_mm",
        message=(
            "The member total depth is required for the Clause 9-21-6-1-8 "
            "full-depth-lap exception; it is never assumed. Missing required "
            "input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    _require_positive(
        force_per_leg_n,
        code="MISSING_FORCE_PER_LEG",
        field_name="force_per_leg_n",
        message=(
            "The force per leg (f_y * tie area) is required for the Clause "
            "9-21-6-1-8 full-depth-lap exception; it is never assumed. "
            "Missing required input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    _require_positive(
        provided_leg_lap_mm,
        code="MISSING_PROVIDED_LEG_LAP",
        field_name="provided_leg_lap_mm",
        message=(
            "The provided U-tie leg lap is required for the Clause 9-21-6-1-8 "
            "check; it is never assumed. Missing required input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    if invalid:
        return _invalid_step(gate, raw_inputs=raw_inputs, diagnostics=invalid)
    if missing:
        return _blocked_step(gate, raw_inputs=raw_inputs, diagnostics=missing)
    assert anchorage_length_mm is not None
    assert total_depth_mm is not None
    assert force_per_leg_n is not None
    assert provided_leg_lap_mm is not None

    base_required_mm = anchorage_length_mm / BG_TRANS_CLOSED_TIE_LAP_DIVISOR
    full_depth_exception = (
        total_depth_mm >= BG_TRANS_CLOSED_TIE_FULL_DEPTH_MIN_DEPTH_MM
        and force_per_leg_n < BG_TRANS_CLOSED_TIE_FULL_DEPTH_MAX_FORCE_N
    )
    required_lap_mm = (
        min(base_required_mm, total_depth_mm) if full_depth_exception else base_required_mm
    )

    intermediates: Dict[str, float] = {
        "anchorage_length_mm": anchorage_length_mm,
        "total_depth_mm": total_depth_mm,
        "force_per_leg_n": force_per_leg_n,
        "provided_leg_lap_mm": provided_leg_lap_mm,
        "base_required_lap_mm": base_required_mm,
        "governing_required_lap_mm": required_lap_mm,
        "full_depth_exception_applied": 1.0 if full_depth_exception else 0.0,
    }
    if provided_leg_lap_mm >= required_lap_mm:
        note = (
            " (full-depth-lap exception of 9-21-6-1-8 applied: depth >= 450 mm "
            "and force/leg < 40 kN)"
            if full_depth_exception
            else ""
        )
        return _pass_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates=intermediates,
            final_result=required_lap_mm,
            unit="mm",
            message=(
                f"PASS: provided U-tie leg lap {provided_leg_lap_mm} mm >= required "
                f"{required_lap_mm} mm per Clause 9-21-6-1-8{note}."
            ),
        )
    diag = EngineeringDiagnostic(
        code="CLOSED_TIE_LEG_LAP_INSUFFICIENT",
        severity=DiagnosticSeverity.ERROR,
        message=(
            f"FAIL: the U-tie leg lap must be at least {required_lap_mm} mm "
            f"(one third of the anchorage length"
            + (
                ", relaxed to the full member depth by the 9-21-6-1-8 exception"
                if full_depth_exception
                else ""
            )
            + f") per Clause 9-21-6-1-8; provided {provided_leg_lap_mm} mm."
        ),
        rule_id=rule_id,
        field_name="provided_leg_lap_mm",
    )
    return _fail_step(
        gate,
        raw_inputs=raw_inputs,
        intermediates=intermediates,
        final_result=required_lap_mm,
        unit="mm",
        diagnostic=diag,
    )


# --- BG-TRANS-TIE-SPACING-001 (Clause 9-21-6-2-1, PDF p. 466 / Printed p. 446)
def evaluate_tie_spacing(
    *,
    provided_clear_spacing_mm: Optional[float] = None,
    provided_center_to_center_spacing_mm: Optional[float] = None,
    aggregate_size_mm: Optional[float] = None,
    longitudinal_bar_diameter_mm: Optional[float] = None,
    transverse_bar_diameter_mm: Optional[float] = None,
    smallest_member_dimension_mm: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate the tie spacing limits (BG-TRANS-TIE-SPACING-001).

    Verified source: Mabhas 9 (1399), Clause 9-21-6-2-1, PDF p. 466 /
    Printed p. 446: (الف) clear spacing >= d_agg/3; (ب) centre-to-centre tie
    spacing <= min(16*db_longitudinal, 48*db_transverse, smallest member
    dimension). PASS only when both limits hold; a violated limit -> FAIL.
    """
    rule_id = RULE_BG_TRANS_TIE_SPACING_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "provided_clear_spacing_mm": provided_clear_spacing_mm,
        "provided_center_to_center_spacing_mm": provided_center_to_center_spacing_mm,
        "aggregate_size_mm": aggregate_size_mm,
        "longitudinal_bar_diameter_mm": longitudinal_bar_diameter_mm,
        "transverse_bar_diameter_mm": transverse_bar_diameter_mm,
        "smallest_member_dimension_mm": smallest_member_dimension_mm,
    }

    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")
    rule = gate.rule

    invalid: List[EngineeringDiagnostic] = []
    missing: List[EngineeringDiagnostic] = []
    _require_positive(
        provided_clear_spacing_mm,
        code="MISSING_PROVIDED_CLEAR_SPACING",
        field_name="provided_clear_spacing_mm",
        message=(
            "The provided tie clear spacing is required for the Clause "
            "9-21-6-2-1-الف check; it is never assumed. Missing required "
            "input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    _require_positive(
        provided_center_to_center_spacing_mm,
        code="MISSING_PROVIDED_CC_SPACING",
        field_name="provided_center_to_center_spacing_mm",
        message=(
            "The provided centre-to-centre tie spacing is required for the "
            "Clause 9-21-6-2-1-ب check; it is never assumed. Missing required "
            "input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    _require_positive(
        aggregate_size_mm,
        code="MISSING_AGGREGATE_SIZE",
        field_name="aggregate_size_mm",
        message=(
            "The largest nominal aggregate size is required for the Clause "
            "9-21-6-2-1-الف clear-spacing limit; it is never assumed. Missing "
            "required input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    _require_positive(
        longitudinal_bar_diameter_mm,
        code="MISSING_LONGITUDINAL_BAR_DIAMETER",
        field_name="longitudinal_bar_diameter_mm",
        message=(
            "The longitudinal bar diameter is required for the Clause "
            "9-21-6-2-1-ب c-c spacing limit (16*db); it is never assumed. "
            "Missing required input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    _require_positive(
        transverse_bar_diameter_mm,
        code="MISSING_TRANSVERSE_BAR_DIAMETER",
        field_name="transverse_bar_diameter_mm",
        message=(
            "The transverse (tie) bar diameter is required for the Clause "
            "9-21-6-2-1-ب c-c spacing limit (48*db); it is never assumed. "
            "Missing required input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    _require_positive(
        smallest_member_dimension_mm,
        code="MISSING_SMALLEST_MEMBER_DIMENSION",
        field_name="smallest_member_dimension_mm",
        message=(
            "The smallest member dimension is required for the Clause "
            "9-21-6-2-1-ب c-c spacing limit; it is never assumed. Missing "
            "required input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    if invalid:
        return _invalid_step(gate, raw_inputs=raw_inputs, diagnostics=invalid)
    if missing:
        return _blocked_step(gate, raw_inputs=raw_inputs, diagnostics=missing)
    assert provided_clear_spacing_mm is not None
    assert provided_center_to_center_spacing_mm is not None
    assert aggregate_size_mm is not None
    assert longitudinal_bar_diameter_mm is not None
    assert transverse_bar_diameter_mm is not None
    assert smallest_member_dimension_mm is not None

    min_clear_required_mm = aggregate_size_mm / BG_TRANS_TIE_CLEAR_AGG_DIVISOR
    limit_16 = BG_TRANS_TIE_CC_LONG_FACTOR * longitudinal_bar_diameter_mm
    limit_48 = BG_TRANS_TIE_CC_TRANS_FACTOR * transverse_bar_diameter_mm
    max_cc_allowed_mm = min(limit_16, limit_48, smallest_member_dimension_mm)

    intermediates: Dict[str, float] = {
        "provided_clear_spacing_mm": provided_clear_spacing_mm,
        "provided_center_to_center_spacing_mm": provided_center_to_center_spacing_mm,
        "aggregate_size_mm": aggregate_size_mm,
        "min_clear_required_mm": min_clear_required_mm,
        "cc_limit_16db_mm": limit_16,
        "cc_limit_48db_mm": limit_48,
        "smallest_member_dimension_mm": smallest_member_dimension_mm,
        "max_cc_allowed_mm": max_cc_allowed_mm,
    }
    clear_ok = provided_clear_spacing_mm >= min_clear_required_mm
    cc_ok = provided_center_to_center_spacing_mm <= max_cc_allowed_mm
    if clear_ok and cc_ok:
        return _pass_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates=intermediates,
            final_result=max_cc_allowed_mm,
            unit="mm",
            message=(
                f"PASS: tie clear spacing {provided_clear_spacing_mm} mm >= "
                f"{min_clear_required_mm} mm (d_agg/3) and c-c spacing "
                f"{provided_center_to_center_spacing_mm} mm <= {max_cc_allowed_mm} mm "
                "per Clause 9-21-6-2-1."
            ),
        )
    reasons: List[str] = []
    if not clear_ok:
        reasons.append(
            f"clear spacing {provided_clear_spacing_mm} mm < {min_clear_required_mm} mm (d_agg/3)"
        )
    if not cc_ok:
        reasons.append(
            f"c-c spacing {provided_center_to_center_spacing_mm} mm > {max_cc_allowed_mm} mm "
            "(min of 16*db_long, 48*db_trans, smallest member dim)"
        )
    diag = EngineeringDiagnostic(
        code="TIE_SPACING_LIMIT_VIOLATED",
        severity=DiagnosticSeverity.ERROR,
        message=(
            "FAIL: tie spacing violates Clause 9-21-6-2-1 — " + "; ".join(reasons) + "."
        ),
        rule_id=rule_id,
        field_name="provided_center_to_center_spacing_mm",
    )
    return _fail_step(
        gate,
        raw_inputs=raw_inputs,
        intermediates=intermediates,
        final_result=max_cc_allowed_mm,
        unit="mm",
        diagnostic=diag,
    )


# --- BG-TRANS-TIE-DIA-001 (Clause 9-21-6-2-2, PDF p. 466 / Printed p. 446)
def evaluate_tie_diameter(
    *,
    longitudinal_bar_diameter_mm: Optional[float] = None,
    is_bundled: Optional[bool] = None,
    provided_tie_diameter_mm: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate the minimum tie diameter (BG-TRANS-TIE-DIA-001).

    Verified source: Mabhas 9 (1399), Clause 9-21-6-2-2, PDF p. 466 /
    Printed p. 446: (الف) 10 mm for longitudinal bars up to 32 mm; (ب) 12 mm
    for longitudinal bars of 34 mm and larger, or longitudinal bar bundles.
    A non-bundled longitudinal bar with 32 < d_b < 34 mm (e.g. 33 mm) is in
    neither verified branch and is deterministically BLOCKED.
    """
    rule_id = RULE_BG_TRANS_TIE_DIA_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "longitudinal_bar_diameter_mm": longitudinal_bar_diameter_mm,
        "is_bundled": is_bundled,
        "provided_tie_diameter_mm": provided_tie_diameter_mm,
    }

    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")
    rule = gate.rule

    bundled_raw: object = is_bundled
    if bundled_raw is None:
        return _blocked_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _missing_input_diagnostic(
                    "MISSING_IS_BUNDLED",
                    (
                        "Whether the longitudinal bars are bundled is required "
                        "to select the Clause 9-21-6-2-2 tie-diameter branch; "
                        "it is never assumed. Missing required input -> BLOCKED."
                    ),
                    rule=rule,
                    field_name="is_bundled",
                )
            ],
        )
    if not isinstance(bundled_raw, bool):
        return _invalid_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                EngineeringDiagnostic(
                    code="INVALID_IS_BUNDLED",
                    severity=DiagnosticSeverity.ERROR,
                    message=f"is_bundled must be a bool, got {bundled_raw!r}.",
                    rule_id=rule_id,
                    field_name="is_bundled",
                )
            ],
        )

    invalid: List[EngineeringDiagnostic] = []
    missing: List[EngineeringDiagnostic] = []
    _require_positive(
        longitudinal_bar_diameter_mm,
        code="MISSING_LONGITUDINAL_BAR_DIAMETER",
        field_name="longitudinal_bar_diameter_mm",
        message=(
            "The longitudinal bar diameter is required to select the Clause "
            "9-21-6-2-2 tie-diameter branch; it is never assumed. Missing "
            "required input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    _require_positive(
        provided_tie_diameter_mm,
        code="MISSING_PROVIDED_TIE_DIAMETER",
        field_name="provided_tie_diameter_mm",
        message=(
            "The provided tie diameter is required for the Clause 9-21-6-2-2 "
            "check; it is never assumed. Missing required input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    if invalid:
        return _invalid_step(gate, raw_inputs=raw_inputs, diagnostics=invalid)
    if missing:
        return _blocked_step(gate, raw_inputs=raw_inputs, diagnostics=missing)
    assert longitudinal_bar_diameter_mm is not None
    assert provided_tie_diameter_mm is not None

    if bundled_raw:
        required_dia_mm = BG_TRANS_TIE_DIA_LARGE_MM
        branch = "ب (bundled -> 12 mm)"
    elif longitudinal_bar_diameter_mm <= BG_TRANS_TIE_DIA_SMALL_MAX_DB_MM:
        required_dia_mm = BG_TRANS_TIE_DIA_SMALL_MM
        branch = "الف (db <= 32 mm -> 10 mm)"
    elif longitudinal_bar_diameter_mm >= BG_TRANS_TIE_DIA_LARGE_MIN_DB_MM:
        required_dia_mm = BG_TRANS_TIE_DIA_LARGE_MM
        branch = "ب (db >= 34 mm -> 12 mm)"
    else:
        return _blocked_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _missing_input_diagnostic(
                    "TIE_DIA_NO_VERIFIED_BRANCH",
                    (
                        "BLOCKED: Clause 9-21-6-2-2 assigns 10 mm to "
                        "longitudinal bars up to 32 mm (الف) and 12 mm to bars "
                        "34 mm and larger or bundles (ب); a non-bundled bar with "
                        f"d_b = {longitudinal_bar_diameter_mm} mm lies in the "
                        "unverified 32 < d_b < 34 mm gap and is never "
                        "interpolated."
                    ),
                    rule=rule,
                    field_name="longitudinal_bar_diameter_mm",
                    required_verification=(
                        "Verify a governing branch for 32 < d_b < 34 mm against "
                        "the primary source before executing."
                    ),
                )
            ],
        )

    intermediates: Dict[str, float] = {
        "longitudinal_bar_diameter_mm": longitudinal_bar_diameter_mm,
        "provided_tie_diameter_mm": provided_tie_diameter_mm,
        "required_tie_diameter_mm": required_dia_mm,
        "is_bundled": 1.0 if bundled_raw else 0.0,
    }
    if provided_tie_diameter_mm >= required_dia_mm:
        return _pass_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates=intermediates,
            final_result=required_dia_mm,
            unit="mm",
            message=(
                f"PASS: provided tie diameter {provided_tie_diameter_mm} mm >= "
                f"required {required_dia_mm} mm per Clause 9-21-6-2-2 {branch}."
            ),
        )
    diag = EngineeringDiagnostic(
        code="TIE_DIAMETER_BELOW_MINIMUM",
        severity=DiagnosticSeverity.ERROR,
        message=(
            f"FAIL: Clause 9-21-6-2-2 {branch} requires a tie diameter >= "
            f"{required_dia_mm} mm; provided {provided_tie_diameter_mm} mm."
        ),
        rule_id=rule_id,
        field_name="provided_tie_diameter_mm",
    )
    return _fail_step(
        gate,
        raw_inputs=raw_inputs,
        intermediates=intermediates,
        final_result=required_dia_mm,
        unit="mm",
        diagnostic=diag,
    )


# --- BG-TRANS-RECT-TIE-001 (Clause 9-21-6-2-4-ب, PDF p. 467 / Printed p. 447)
def evaluate_rect_tie_unrestrained_spacing(
    *,
    unrestrained_bar_clear_spacing_mm: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate the rectangular-tie unrestrained-bar spacing (BG-TRANS-RECT-TIE-001).

    Verified source: Mabhas 9 (1399), Clause 9-21-6-2-4-ب, PDF p. 467 /
    Printed p. 447: a longitudinal bar without lateral (tie-bend) restraint
    must not have clear spacing greater than 150 mm from a restrained
    longitudinal bar.
    """
    rule_id = RULE_BG_TRANS_RECT_TIE_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "unrestrained_bar_clear_spacing_mm": unrestrained_bar_clear_spacing_mm,
    }

    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")
    rule = gate.rule

    invalid: List[EngineeringDiagnostic] = []
    missing: List[EngineeringDiagnostic] = []
    _require_positive(
        unrestrained_bar_clear_spacing_mm,
        code="MISSING_UNRESTRAINED_BAR_CLEAR_SPACING",
        field_name="unrestrained_bar_clear_spacing_mm",
        message=(
            "The clear spacing of the laterally-unrestrained longitudinal bar "
            "to the nearest restrained longitudinal bar is required for the "
            "Clause 9-21-6-2-4-ب check; it is never assumed. Missing required "
            "input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    if invalid:
        return _invalid_step(gate, raw_inputs=raw_inputs, diagnostics=invalid)
    if missing:
        return _blocked_step(gate, raw_inputs=raw_inputs, diagnostics=missing)
    assert unrestrained_bar_clear_spacing_mm is not None

    max_clear_mm = BG_TRANS_RECT_TIE_UNRESTRAINED_MAX_CLEAR_MM
    intermediates: Dict[str, float] = {
        "unrestrained_bar_clear_spacing_mm": unrestrained_bar_clear_spacing_mm,
        "max_clear_spacing_mm": max_clear_mm,
    }
    if unrestrained_bar_clear_spacing_mm <= max_clear_mm:
        return _pass_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates=intermediates,
            final_result=max_clear_mm,
            unit="mm",
            message=(
                f"PASS: laterally-unrestrained longitudinal bar clear spacing "
                f"{unrestrained_bar_clear_spacing_mm} mm <= {max_clear_mm} mm per "
                "Clause 9-21-6-2-4-ب."
            ),
        )
    diag = EngineeringDiagnostic(
        code="RECT_TIE_UNRESTRAINED_SPACING_EXCEEDS_LIMIT",
        severity=DiagnosticSeverity.ERROR,
        message=(
            f"FAIL: a longitudinal bar without lateral restraint must have "
            f"clear spacing <= {max_clear_mm} mm from a restrained longitudinal "
            f"bar per Clause 9-21-6-2-4-ب; provided {unrestrained_bar_clear_spacing_mm} mm."
        ),
        rule_id=rule_id,
        field_name="unrestrained_bar_clear_spacing_mm",
    )
    return _fail_step(
        gate,
        raw_inputs=raw_inputs,
        intermediates=intermediates,
        final_result=max_clear_mm,
        unit="mm",
        diagnostic=diag,
    )


# --- BG-TRANS-CIRC-TIE-001 (Clause 9-21-6-2-5-الف, PDF p. 467 / Printed p. 447)
def evaluate_circular_tie_overlap(
    *,
    tie_end_overlap_mm: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate the circular-tie end overlap (BG-TRANS-CIRC-TIE-001).

    Verified source: Mabhas 9 (1399), Clause 9-21-6-2-5-الف, PDF p. 467 /
    Printed p. 447: at each circular-tie end the bars must overlap by at
    least 150 mm.
    """
    rule_id = RULE_BG_TRANS_CIRC_TIE_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {"tie_end_overlap_mm": tie_end_overlap_mm}

    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")
    rule = gate.rule

    invalid: List[EngineeringDiagnostic] = []
    missing: List[EngineeringDiagnostic] = []
    _require_positive(
        tie_end_overlap_mm,
        code="MISSING_TIE_END_OVERLAP",
        field_name="tie_end_overlap_mm",
        message=(
            "The circular-tie end overlap is required for the Clause "
            "9-21-6-2-5-الف check; it is never assumed. Missing required "
            "input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    if invalid:
        return _invalid_step(gate, raw_inputs=raw_inputs, diagnostics=invalid)
    if missing:
        return _blocked_step(gate, raw_inputs=raw_inputs, diagnostics=missing)
    assert tie_end_overlap_mm is not None

    min_overlap_mm = BG_TRANS_CIRC_TIE_MIN_OVERLAP_MM
    intermediates: Dict[str, float] = {
        "tie_end_overlap_mm": tie_end_overlap_mm,
        "min_overlap_mm": min_overlap_mm,
    }
    if tie_end_overlap_mm >= min_overlap_mm:
        return _pass_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates=intermediates,
            final_result=min_overlap_mm,
            unit="mm",
            message=(
                f"PASS: circular-tie end overlap {tie_end_overlap_mm} mm >= "
                f"{min_overlap_mm} mm per Clause 9-21-6-2-5-الف."
            ),
        )
    diag = EngineeringDiagnostic(
        code="CIRCULAR_TIE_OVERLAP_BELOW_MINIMUM",
        severity=DiagnosticSeverity.ERROR,
        message=(
            f"FAIL: at each circular-tie end the bars must overlap by at least "
            f"{min_overlap_mm} mm per Clause 9-21-6-2-5-الف; provided "
            f"{tie_end_overlap_mm} mm."
        ),
        rule_id=rule_id,
        field_name="tie_end_overlap_mm",
    )
    return _fail_step(
        gate,
        raw_inputs=raw_inputs,
        intermediates=intermediates,
        final_result=min_overlap_mm,
        unit="mm",
        diagnostic=diag,
    )


# --- BG-TRANS-SPIRAL-SPACING-001 (Clause 9-21-6-3-1, PDF p. 468 / Printed p. 448)
def evaluate_spiral_spacing(
    *,
    provided_clear_spacing_mm: Optional[float] = None,
    provided_pitch_mm: Optional[float] = None,
    aggregate_size_mm: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate the spiral spacing limits (BG-TRANS-SPIRAL-SPACING-001).

    Verified source: Mabhas 9 (1399), Clause 9-21-6-3-1, PDF p. 468 /
    Printed p. 448: (الف) clear spacing >= max(d_agg/3, 25 mm); (ب) pitch
    <= 75 mm. PASS only when both limits hold; a violated limit -> FAIL.
    """
    rule_id = RULE_BG_TRANS_SPIRAL_SPACING_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "provided_clear_spacing_mm": provided_clear_spacing_mm,
        "provided_pitch_mm": provided_pitch_mm,
        "aggregate_size_mm": aggregate_size_mm,
    }

    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")
    rule = gate.rule

    invalid: List[EngineeringDiagnostic] = []
    missing: List[EngineeringDiagnostic] = []
    _require_positive(
        provided_clear_spacing_mm,
        code="MISSING_PROVIDED_CLEAR_SPACING",
        field_name="provided_clear_spacing_mm",
        message=(
            "The provided spiral clear spacing is required for the Clause "
            "9-21-6-3-1-الف check; it is never assumed. Missing required "
            "input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    _require_positive(
        provided_pitch_mm,
        code="MISSING_PROVIDED_PITCH",
        field_name="provided_pitch_mm",
        message=(
            "The provided spiral pitch is required for the Clause 9-21-6-3-1-ب "
            "check; it is never assumed. Missing required input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    _require_positive(
        aggregate_size_mm,
        code="MISSING_AGGREGATE_SIZE",
        field_name="aggregate_size_mm",
        message=(
            "The largest aggregate size is required for the Clause 9-21-6-3-1-الف "
            "clear-spacing limit; it is never assumed. Missing required input "
            "-> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    if invalid:
        return _invalid_step(gate, raw_inputs=raw_inputs, diagnostics=invalid)
    if missing:
        return _blocked_step(gate, raw_inputs=raw_inputs, diagnostics=missing)
    assert provided_clear_spacing_mm is not None
    assert provided_pitch_mm is not None
    assert aggregate_size_mm is not None

    min_clear_required_mm = max(
        aggregate_size_mm / BG_TRANS_SPIRAL_CLEAR_AGG_DIVISOR,
        BG_TRANS_SPIRAL_CLEAR_MIN_MM,
    )
    max_pitch_mm = BG_TRANS_SPIRAL_MAX_PITCH_MM
    intermediates: Dict[str, float] = {
        "provided_clear_spacing_mm": provided_clear_spacing_mm,
        "provided_pitch_mm": provided_pitch_mm,
        "aggregate_size_mm": aggregate_size_mm,
        "min_clear_required_mm": min_clear_required_mm,
        "max_pitch_mm": max_pitch_mm,
    }
    clear_ok = provided_clear_spacing_mm >= min_clear_required_mm
    pitch_ok = provided_pitch_mm <= max_pitch_mm
    if clear_ok and pitch_ok:
        return _pass_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates=intermediates,
            final_result=max_pitch_mm,
            unit="mm",
            message=(
                f"PASS: spiral clear spacing {provided_clear_spacing_mm} mm >= "
                f"{min_clear_required_mm} mm (max of d_agg/3 and 25 mm) and pitch "
                f"{provided_pitch_mm} mm <= {max_pitch_mm} mm per Clause 9-21-6-3-1."
            ),
        )
    reasons: List[str] = []
    if not clear_ok:
        reasons.append(
            f"clear spacing {provided_clear_spacing_mm} mm < {min_clear_required_mm} mm "
            "(max of d_agg/3 and 25 mm)"
        )
    if not pitch_ok:
        reasons.append(f"pitch {provided_pitch_mm} mm > {max_pitch_mm} mm")
    diag = EngineeringDiagnostic(
        code="SPIRAL_SPACING_LIMIT_VIOLATED",
        severity=DiagnosticSeverity.ERROR,
        message="FAIL: spiral spacing violates Clause 9-21-6-3-1 — " + "; ".join(reasons) + ".",
        rule_id=rule_id,
        field_name="provided_pitch_mm",
    )
    return _fail_step(
        gate,
        raw_inputs=raw_inputs,
        intermediates=intermediates,
        final_result=max_pitch_mm,
        unit="mm",
        diagnostic=diag,
    )


# --- BG-TRANS-SPIRAL-DIA-001 (Clause 9-21-6-3-2, PDF p. 468 / Printed p. 448)
def evaluate_spiral_diameter(
    *,
    provided_spiral_diameter_mm: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate the minimum spiral diameter (BG-TRANS-SPIRAL-DIA-001).

    Verified source: Mabhas 9 (1399), Clause 9-21-6-3-2, PDF p. 468 /
    Printed p. 448: the spiral wire/bar diameter for cast-in-place concrete
    must be at least 10 mm.
    """
    rule_id = RULE_BG_TRANS_SPIRAL_DIA_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "provided_spiral_diameter_mm": provided_spiral_diameter_mm
    }

    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")
    rule = gate.rule

    invalid: List[EngineeringDiagnostic] = []
    missing: List[EngineeringDiagnostic] = []
    _require_positive(
        provided_spiral_diameter_mm,
        code="MISSING_PROVIDED_SPIRAL_DIAMETER",
        field_name="provided_spiral_diameter_mm",
        message=(
            "The provided spiral diameter is required for the Clause 9-21-6-3-2 "
            "check; it is never assumed. Missing required input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    if invalid:
        return _invalid_step(gate, raw_inputs=raw_inputs, diagnostics=invalid)
    if missing:
        return _blocked_step(gate, raw_inputs=raw_inputs, diagnostics=missing)
    assert provided_spiral_diameter_mm is not None

    min_dia_mm = BG_TRANS_SPIRAL_MIN_DIA_MM
    intermediates: Dict[str, float] = {
        "provided_spiral_diameter_mm": provided_spiral_diameter_mm,
        "min_spiral_diameter_mm": min_dia_mm,
    }
    if provided_spiral_diameter_mm >= min_dia_mm:
        return _pass_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates=intermediates,
            final_result=min_dia_mm,
            unit="mm",
            message=(
                f"PASS: spiral diameter {provided_spiral_diameter_mm} mm >= "
                f"{min_dia_mm} mm per Clause 9-21-6-3-2."
            ),
        )
    diag = EngineeringDiagnostic(
        code="SPIRAL_DIAMETER_BELOW_MINIMUM",
        severity=DiagnosticSeverity.ERROR,
        message=(
            f"FAIL: the spiral wire/bar diameter for cast-in-place concrete must "
            f"be at least {min_dia_mm} mm per Clause 9-21-6-3-2; provided "
            f"{provided_spiral_diameter_mm} mm."
        ),
        rule_id=rule_id,
        field_name="provided_spiral_diameter_mm",
    )
    return _fail_step(
        gate,
        raw_inputs=raw_inputs,
        intermediates=intermediates,
        final_result=min_dia_mm,
        unit="mm",
        diagnostic=diag,
    )


# --- BG-TRANS-SPIRAL-RATIO-001 (Clause 9-21-6-3-3 & Eq. (9-21-8), PDF p. 468 / Printed p. 448)
def evaluate_spiral_ratio(
    *,
    gross_area_mm2: Optional[float] = None,
    core_area_mm2: Optional[float] = None,
    concrete_strength_mpa: Optional[float] = None,
    spiral_yield_stress_mpa: Optional[float] = None,
    provided_rho_s: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate the spiral volumetric ratio (BG-TRANS-SPIRAL-RATIO-001).

    Verified source: Mabhas 9 (1399), Clause 9-21-6-3-3 & Eq. (9-21-8),
    PDF p. 468 / Printed p. 448: rho_s >= 0.45*(A_g/A_ch - 1)*f'c/f_y_tau,
    with the spiral yield stress f_y_tau not taken greater than 700 MPa.
    """
    rule_id = RULE_BG_TRANS_SPIRAL_RATIO_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "gross_area_mm2": gross_area_mm2,
        "core_area_mm2": core_area_mm2,
        "concrete_strength_mpa": concrete_strength_mpa,
        "spiral_yield_stress_mpa": spiral_yield_stress_mpa,
        "provided_rho_s": provided_rho_s,
    }

    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="ratio")
    rule = gate.rule

    invalid: List[EngineeringDiagnostic] = []
    missing: List[EngineeringDiagnostic] = []
    _require_positive(
        gross_area_mm2,
        code="MISSING_GROSS_AREA",
        field_name="gross_area_mm2",
        message=(
            "The gross area A_g is required for Eq. (9-21-8); it is never "
            "assumed. Missing required input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    _require_positive(
        core_area_mm2,
        code="MISSING_CORE_AREA",
        field_name="core_area_mm2",
        message=(
            "The core area A_ch is required for Eq. (9-21-8); it is never "
            "assumed. Missing required input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    _require_positive(
        concrete_strength_mpa,
        code="MISSING_CONCRETE_STRENGTH",
        field_name="concrete_strength_mpa",
        message=(
            "The concrete strength f'c is required for Eq. (9-21-8); it is "
            "never assumed. Missing required input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    _require_positive(
        spiral_yield_stress_mpa,
        code="MISSING_SPIRAL_YIELD_STRESS",
        field_name="spiral_yield_stress_mpa",
        message=(
            "The spiral yield stress f_y_tau is required for Eq. (9-21-8); it "
            "is never assumed. Missing required input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    _require_positive(
        provided_rho_s,
        code="MISSING_PROVIDED_RHO_S",
        field_name="provided_rho_s",
        message=(
            "The provided spiral volumetric ratio rho_s is required for the "
            "Clause 9-21-6-3-3 check; it is never assumed. Missing required "
            "input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    if invalid:
        return _invalid_step(gate, raw_inputs=raw_inputs, diagnostics=invalid)
    if missing:
        return _blocked_step(gate, raw_inputs=raw_inputs, diagnostics=missing)
    assert gross_area_mm2 is not None
    assert core_area_mm2 is not None
    assert concrete_strength_mpa is not None
    assert spiral_yield_stress_mpa is not None
    assert provided_rho_s is not None

    fyt_cap = BG_TRANS_SPIRAL_FYT_MAX_MPA
    if spiral_yield_stress_mpa > fyt_cap:
        diag = EngineeringDiagnostic(
            code="SPIRAL_FYT_EXCEEDS_700_LIMIT",
            severity=DiagnosticSeverity.ERROR,
            message=(
                f"FAIL: the spiral yield stress f_y_tau must not be taken "
                f"greater than {fyt_cap} MPa for Eq. (9-21-8) per Clause "
                f"9-21-6-3-3; provided f_y_tau = {spiral_yield_stress_mpa} MPa."
            ),
            rule_id=rule_id,
            field_name="spiral_yield_stress_mpa",
        )
        return _fail_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates={"spiral_yield_stress_mpa": spiral_yield_stress_mpa, "fyt_cap_mpa": fyt_cap},
            final_result=None,
            unit="ratio",
            diagnostic=diag,
        )

    ag_over_ach = gross_area_mm2 / core_area_mm2
    required_rho = (
        BG_TRANS_SPIRAL_RATIO_COEFF
        * (ag_over_ach - 1.0)
        * (concrete_strength_mpa / spiral_yield_stress_mpa)
    )
    intermediates: Dict[str, float] = {
        "gross_area_mm2": gross_area_mm2,
        "core_area_mm2": core_area_mm2,
        "concrete_strength_mpa": concrete_strength_mpa,
        "spiral_yield_stress_mpa": spiral_yield_stress_mpa,
        "provided_rho_s": provided_rho_s,
        "ag_over_ach": ag_over_ach,
        "required_rho_s": required_rho,
    }
    if provided_rho_s >= required_rho:
        return _pass_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates=intermediates,
            final_result=required_rho,
            unit="ratio",
            message=(
                f"PASS: provided rho_s = {provided_rho_s} >= required "
                f"{required_rho} = 0.45*(A_g/A_ch - 1)*f'c/f_y_tau per Eq. (9-21-8)."
            ),
        )
    diag = EngineeringDiagnostic(
        code="SPIRAL_RATIO_BELOW_REQUIRED",
        severity=DiagnosticSeverity.ERROR,
        message=(
            f"FAIL: Eq. (9-21-8) requires rho_s >= {required_rho} = "
            f"0.45*({gross_area_mm2}/{core_area_mm2} - 1)*{concrete_strength_mpa}/"
            f"{spiral_yield_stress_mpa}; provided rho_s = {provided_rho_s}."
        ),
        rule_id=rule_id,
        field_name="provided_rho_s",
    )
    return _fail_step(
        gate,
        raw_inputs=raw_inputs,
        intermediates=intermediates,
        final_result=required_rho,
        unit="ratio",
        diagnostic=diag,
    )


# --- BG-TRANS-SPIRAL-ANCHOR-001 (Clause 9-21-6-3-4, PDF p. 468 / Printed p. 448)
def evaluate_spiral_anchor_turns(
    *,
    extra_turns_each_end: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate the spiral end anchorage (BG-TRANS-SPIRAL-ANCHOR-001).

    Verified source: Mabhas 9 (1399), Clause 9-21-6-3-4, PDF p. 468 /
    Printed p. 448: spiral anchorage at each end is provided by one and a
    half extra turns of the spiral.
    """
    rule_id = RULE_BG_TRANS_SPIRAL_ANCHOR_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {"extra_turns_each_end": extra_turns_each_end}

    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="turns")
    rule = gate.rule

    invalid: List[EngineeringDiagnostic] = []
    missing: List[EngineeringDiagnostic] = []
    _require_positive(
        extra_turns_each_end,
        code="MISSING_EXTRA_TURNS",
        field_name="extra_turns_each_end",
        message=(
            "The number of extra spiral turns at each end is required for the "
            "Clause 9-21-6-3-4 check; it is never assumed. Missing required "
            "input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    if invalid:
        return _invalid_step(gate, raw_inputs=raw_inputs, diagnostics=invalid)
    if missing:
        return _blocked_step(gate, raw_inputs=raw_inputs, diagnostics=missing)
    assert extra_turns_each_end is not None

    required_turns = BG_TRANS_SPIRAL_ANCHOR_EXTRA_TURNS
    intermediates: Dict[str, float] = {
        "extra_turns_each_end": extra_turns_each_end,
        "required_extra_turns": required_turns,
    }
    if extra_turns_each_end >= required_turns:
        return _pass_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates=intermediates,
            final_result=required_turns,
            unit="turns",
            message=(
                f"PASS: extra spiral turns at each end {extra_turns_each_end} >= "
                f"{required_turns} per Clause 9-21-6-3-4."
            ),
        )
    diag = EngineeringDiagnostic(
        code="SPIRAL_ANCHOR_TURNS_BELOW_MINIMUM",
        severity=DiagnosticSeverity.ERROR,
        message=(
            f"FAIL: spiral anchorage requires at least {required_turns} extra "
            f"turns at each end per Clause 9-21-6-3-4; provided "
            f"{extra_turns_each_end}."
        ),
        rule_id=rule_id,
        field_name="extra_turns_each_end",
    )
    return _fail_step(
        gate,
        raw_inputs=raw_inputs,
        intermediates=intermediates,
        final_result=required_turns,
        unit="turns",
        diagnostic=diag,
    )


# --- BG-TRANS-SPIRAL-LAP-001 (Clause 9-21-6-3-6 & Table 9-21-7, PDF p. 469 / Printed p. 449)
def evaluate_spiral_lap_splice(
    *,
    splice_bar_type: Optional[SpiralSpliceBarType] = None,
    coating_class: Optional[SpiralSpliceCoating] = None,
    end_condition: Optional[SpiralSpliceEndCondition] = None,
    bar_diameter_mm: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate the spiral lap splice length (BG-TRANS-SPIRAL-LAP-001).

    Verified source: Mabhas 9 (1399), Clause 9-21-6-3-6 & Table 9-21-7,
    PDF p. 469 / Printed p. 449: lap = max(k*d_b, 300 mm), with k = 48 or 72
    selected from Table 9-21-7 by (bar/wire type, coating, end condition).
    A (type, coating, end-condition) combination not printed in Table 9-21-7
    is deterministically BLOCKED (no interpretation).
    """
    rule_id = RULE_BG_TRANS_SPIRAL_LAP_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "splice_bar_type": (
            splice_bar_type.value if isinstance(splice_bar_type, SpiralSpliceBarType) else splice_bar_type
        ),
        "coating_class": (
            coating_class.value if isinstance(coating_class, SpiralSpliceCoating) else coating_class
        ),
        "end_condition": (
            end_condition.value if isinstance(end_condition, SpiralSpliceEndCondition) else end_condition
        ),
        "bar_diameter_mm": bar_diameter_mm,
    }

    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")
    rule = gate.rule

    for name, value, enum_cls in (
        ("splice_bar_type", splice_bar_type, SpiralSpliceBarType),
        ("coating_class", coating_class, SpiralSpliceCoating),
        ("end_condition", end_condition, SpiralSpliceEndCondition),
    ):
        if value is None:
            return _blocked_step(
                gate,
                raw_inputs=raw_inputs,
                diagnostics=[
                    _missing_input_diagnostic(
                        "MISSING_" + name.upper(),
                        (
                            f"The {name} is required to select the Table 9-21-7 "
                            "spiral lap-splice length; it is never assumed. "
                            "Missing required input -> BLOCKED."
                        ),
                        rule=rule,
                        field_name=name,
                    )
                ],
            )
        if not isinstance(value, enum_cls):
            return _invalid_step(
                gate,
                raw_inputs=raw_inputs,
                diagnostics=[
                    EngineeringDiagnostic(
                        code="INVALID_" + name.upper(),
                        severity=DiagnosticSeverity.ERROR,
                        message=f"{name} must be a {enum_cls.__name__} value, got {value!r}.",
                        rule_id=rule_id,
                        field_name=name,
                    )
                ],
            )

    invalid: List[EngineeringDiagnostic] = []
    missing: List[EngineeringDiagnostic] = []
    _require_positive(
        bar_diameter_mm,
        code="MISSING_BAR_DIAMETER",
        field_name="bar_diameter_mm",
        message=(
            "The spliced bar diameter d_b is required for the Table 9-21-7 "
            "spiral lap-splice length; it is never assumed. Missing required "
            "input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    if invalid:
        return _invalid_step(gate, raw_inputs=raw_inputs, diagnostics=invalid)
    if missing:
        return _blocked_step(gate, raw_inputs=raw_inputs, diagnostics=missing)
    assert splice_bar_type is not None
    assert coating_class is not None
    assert end_condition is not None
    assert bar_diameter_mm is not None

    key = (splice_bar_type, coating_class, end_condition)
    multiplier = _TABLE_9_21_7_MULTIPLIER.get(key)
    if multiplier is None:
        return _blocked_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _missing_input_diagnostic(
                    "SPIRAL_LAP_COMBINATION_NOT_IN_TABLE_9_21_7",
                    (
                        "BLOCKED: the combination (type="
                        f"{splice_bar_type.value}, coating={coating_class.value}, "
                        f"end={end_condition.value}) is not printed in Table "
                        "9-21-7 and is never interpreted. Supply a combination "
                        "that appears in the verified table."
                    ),
                    rule=rule,
                    field_name="splice_bar_type",
                    required_verification=(
                        "Verify the applicable Table 9-21-7 row against the "
                        "primary source before executing."
                    ),
                )
            ],
        )

    lap_raw_mm = multiplier * bar_diameter_mm
    lap_mm = max(lap_raw_mm, BG_TRANS_SPIRAL_LAP_MIN_MM)
    intermediates: Dict[str, float] = {
        "bar_diameter_mm": bar_diameter_mm,
        "table_multiplier_k": multiplier,
        "lap_before_floor_mm": lap_raw_mm,
        "min_lap_length_mm": BG_TRANS_SPIRAL_LAP_MIN_MM,
    }
    return _computed_step(
        gate,
        raw_inputs=raw_inputs,
        intermediates=intermediates,
        final_result=lap_mm,
        unit="mm",
        message=(
            f"Computed spiral lap splice length = max(k*d_b, 300 mm) = "
            f"max({multiplier}*{bar_diameter_mm}, {BG_TRANS_SPIRAL_LAP_MIN_MM}) = "
            f"{lap_mm} mm per Clause 9-21-6-3-6 / Table 9-21-7."
        ),
    )
