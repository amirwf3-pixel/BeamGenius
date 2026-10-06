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
    RULE_BG_TRANS_DORGIR_001,
    RULE_BG_TRANS_RECT_TIE_001,
    RULE_BG_TRANS_SEISMIC_HOOK_001,
    RULE_BG_TRANS_SPIRAL_ANCHOR_001,
    RULE_BG_TRANS_SPIRAL_DIA_001,
    RULE_BG_TRANS_SPIRAL_LAP_001,
    RULE_BG_TRANS_SPIRAL_RATIO_001,
    RULE_BG_TRANS_SPIRAL_SPACING_001,
    RULE_BG_TRANS_SPIRAL_SPLICE_LAP_SEL_001,
    RULE_BG_TRANS_STANDARD_HOOK_001,
    RULE_BG_TRANS_TIE_ANCHOR_STD_HOOK_001,
    RULE_BG_TRANS_TIE_DIA_001,
    RULE_BG_TRANS_TIE_SHEAR_EXTENT_001,
    RULE_BG_TRANS_TIE_SPACING_001,
    RULE_BG_TRANS_TORSION_TIE_135HOOK_001,
    RULE_BG_TRANS_TORSION_TIE_SEISMIC_HOOK_001,
    RULE_BG_TRANS_TORSION_TIE_STANDARD_HOOK_001,
    RULE_BG_TRANS_TORSION_TIE_WIRE_ROUTE_001,
    RULE_BG_TRANS_TWO_PIECE_TIE_001,
    RULE_BG_TRANS_WIRE_TIE_UTIE_001,
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

# --- Clause 9-21-2-2-4 seismic hook geometry (PDF p. 442 / Printed p. 442).
# Geometry is stated inline in 9-21-2-2-4; the terminological phrase
# "مطابق تعریف فصل ۹-۲۰" is NOT a dependency on Chapter 9-20 and Chapter 9-20
# is never imported. The straight extension is satisfied by >= 6*d_b OR
# >= 75 mm (verbatim "۶d_b و یا ۷۵ میلی‌متر"); the bend is >= 135 deg, relaxed
# to >= 90 deg only for circular دورگیر (دورگیرهای دایروی).
BG_TRANS_SEISMIC_HOOK_MIN_BEND_DEG: float = 135.0
BG_TRANS_SEISMIC_HOOK_CIRCULAR_MIN_BEND_DEG: float = 90.0
BG_TRANS_SEISMIC_HOOK_EXT_DB_FACTOR: float = 6.0
BG_TRANS_SEISMIC_HOOK_EXT_ABS_MIN_MM: float = 75.0
BG_TRANS_SEISMIC_HOOK_MAX_BEND_DEG: float = 180.0

# --- Clause 9-21-2-2-2 & Table 9-21-2 standard transverse-bar hook geometry
# (PDF pp. 442-443 / Printed pp. 442-443). Verbatim visual reads of Table
# 9-21-2 (PDF p. 443): for BOTH the 90-degree and 135-degree standard hooks,
# d_b 10-16 mm -> minimum inner bend diameter 4*d_b and straight extension
# max(6*d_b, 75 mm); d_b 18-25 mm -> minimum inner bend diameter 6*d_b and
# straight extension 12*d_b. d_b = 17 mm is the gap between the printed
# 10-16 and 18-25 rows; d_b < 10 mm and d_b > 25 mm are outside the table;
# all three are deterministically BLOCKED (never interpolated). The
# 180-degree hook (also printed with the same geometry) is a distinct
# configuration not exercised by any Clause 9-21-6 rule in this stage and is
# deterministically BLOCKED (deferred).
BG_TRANS_STD_HOOK_DB_SMALL_MIN_MM: float = 10.0
BG_TRANS_STD_HOOK_DB_SMALL_MAX_MM: float = 16.0
BG_TRANS_STD_HOOK_DB_LARGE_MIN_MM: float = 18.0
BG_TRANS_STD_HOOK_DB_LARGE_MAX_MM: float = 25.0
BG_TRANS_STD_HOOK_SMALL_INNER_DB_FACTOR: float = 4.0
BG_TRANS_STD_HOOK_LARGE_INNER_DB_FACTOR: float = 6.0
BG_TRANS_STD_HOOK_SMALL_EXT_DB_FACTOR: float = 6.0
BG_TRANS_STD_HOOK_SMALL_EXT_ABS_MIN_MM: float = 75.0
BG_TRANS_STD_HOOK_LARGE_EXT_DB_FACTOR: float = 12.0
BG_TRANS_STD_HOOK_SUPPORTED_ANGLES: tuple[float, ...] = (90.0, 135.0)

# --- Clause 9-21-6-1-4 welded-wire U-tie leg anchorage (PDF p. 464 /
# Printed p. 444). Verbatim numeric conditions (one-of الف/ب).
BG_TRANS_WIRE_TIE_UTIE_ALEF_SPACING_MM: float = 50.0
BG_TRANS_WIRE_TIE_UTIE_BE_QUARTER_DEPTH: float = 0.25
BG_TRANS_WIRE_TIE_UTIE_BE_MIN_SPACING_MM: float = 50.0
BG_TRANS_WIRE_TIE_UTIE_BE_BEND_DIA_FACTOR: float = 8.0

# --- Clause 9-21-6-3-5-ب spiral lap-splice route yield-stress limit
# (PDF pp. 468-469 / Printed pp. 448-449). The lap route is permitted for
# f_y <= 420 MPa; f_y > 420 MPa is not covered and is deterministically
# BLOCKED.
BG_TRANS_SPIRAL_SPLICE_LAP_MAX_FY_MPA: float = 420.0

# --- Clause 9-21-6-1-3 tie deformed-bar anchorage (PDF p. 463 / Printed p. 443).
# Verbatim visual read of Clause 9-21-6-1-3 (PDF p. 463), which has THREE
# branches (الف / ب / پ — the branch letters were read at high magnification;
# ب carries one dot below and پ carries three):
#   (الف) bars/wires with d_b <= 16 mm, AND bars with d_b 18-25 mm with
#         f_y < 280 MPa -> standard hook around the longitudinal bar.
#   (ب)  bars with d_b 18-25 mm and f_y > 280 MPa -> standard hook around the
#         longitudinal bar plus an embedment length plus a minimum outer bend
#         diameter 0.17*f_y/(lambda*sqrt(f'c))*d_b.
#   (پ)  in joists (تیرچه‌ها), bars/wires with d_b <= 12 mm -> standard hook.
# Stage H.7 promotes ONLY branch (الف); branches (ب) and (پ) remain blocked
# under BG-TRANS-TIE-ANCHOR-PENDING. Genuine source gaps, never interpolated:
# f_y = 280 MPa exactly is in neither (الف) nor (ب); d_b = 17 mm falls in the
# gap between the printed <= 16 mm and 18-25 mm sub-conditions; d_b > 25 mm is
# assigned to neither branch. All are deterministically BLOCKED.
BG_TRANS_TIE_ANCHOR_FY_LIMIT_MPA: float = 280.0
BG_TRANS_TIE_ANCHOR_DB_SMALL_MAX_MM: float = 16.0
BG_TRANS_TIE_ANCHOR_DB_LARGE_MIN_MM: float = 18.0
BG_TRANS_TIE_ANCHOR_DB_LARGE_MAX_MM: float = 25.0
BG_TRANS_TIE_ANCHOR_DB_JOIST_MAX_MM: float = 12.0

# --- Clause 9-21-6-1-7 two-piece torsion tie (PDF p. 465 / Printed p. 445)
BG_TRANS_TWO_PIECE_U_BEND_MIN_DEG: float = 135.0
BG_TRANS_TWO_PIECE_MEMBER_BEND_DEG: float = 90.0

# --- Clause 9-21-6-1-6-الف torsion/integrity tie 135-degree hook (PDF p. 464 / Printed p. 444)
BG_TRANS_TIE_135_HOOK_MIN_BEND_DEG: float = 135.0


class DorgirConstruction(str, Enum):
    """دورگیر construction class per Clause 9-21-6-4 (PDF p. 470 / Printed p. 450).

    CLOSED_TIE: closed ties (تنگ‌های بسته) — Clause 9-21-6-4-1.
    WOUND_CONTINUOUS: wound continuously (پیچیده شده به صورت پیوسته) — Clause 9-21-6-4-1.
    MULTI_PART: several parts, each with a seismic hook at both ends — Clause 9-21-6-4-2.
    """

    CLOSED_TIE = "closed_tie"
    WOUND_CONTINUOUS = "wound_continuous"
    MULTI_PART = "multi_part"


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


class WireTieUtieAlternative(str, Enum):
    """Welded-wire U-tie leg anchorage alternative per Clause 9-21-6-1-4.

    ALEF (الف): two longitudinal wires at 50 mm spacing in the U-tie upper
    part. BE (ب): one wire < 1/4 effective depth from the compression face,
    a second wire closer to the compression face than the first and > 50 mm
    from it, the second on the leg or on a hook with bend dia >= 8x tie wire
    dia. Clause 9-21-6-1-4 is a one-of condition; the caller selects the
    alternative relied upon.
    """

    ALEF = "alef"
    BE = "be"


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


# --- BG-TRANS-SEISMIC-HOOK-001 (Clause 9-21-2-2-4, PDF p. 442 / Printed p. 442)
def evaluate_seismic_hook(
    *,
    circular_dorgir: Optional[bool] = None,
    bend_angle_deg: Optional[float] = None,
    straight_extension_mm: Optional[float] = None,
    bar_diameter_mm: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate the seismic-hook geometry (BG-TRANS-SEISMIC-HOOK-001).

    Verified source: Mabhas 9 (1399), Clause 9-21-2-2-4, PDF p. 442 /
    Printed p. 442: a seismic hook (قلاب لرزه‌ای) has a bend of at least 135
    degrees and a straight extension after the bend of at least 6*d_b or 75 mm;
    in circular دورگیر (دورگیرهای دایروی) the bend may be at least 90 degrees.
    The geometry is stated inline in 9-21-2-2-4; the terminological phrase
    "مطابق تعریف فصل ۹-۲۰" is NOT a dependency on Chapter 9-20 and Chapter 9-20
    is never imported.

    ``circular_dorgir`` (whether the circular-dorgir 90-degree exception
    applies), ``bend_angle_deg``, ``straight_extension_mm`` and
    ``bar_diameter_mm`` are REQUIRED typed inputs (never assumed or
    defaulted). Missing/invalid inputs -> BLOCKED/INVALID_INPUT, never PASS.
    """
    rule_id = RULE_BG_TRANS_SEISMIC_HOOK_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "circular_dorgir": circular_dorgir,
        "bend_angle_deg": bend_angle_deg,
        "straight_extension_mm": straight_extension_mm,
        "bar_diameter_mm": bar_diameter_mm,
    }

    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")
    rule = gate.rule

    circular_raw: object = circular_dorgir
    if circular_raw is None:
        return _blocked_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _missing_input_diagnostic(
                    "MISSING_CIRCULAR_DORGIR",
                    (
                        "Whether the circular-dorgir 90-degree bend exception "
                        "of Clause 9-21-2-2-4 applies is required to select the "
                        "minimum seismic-hook bend (90 vs 135 degrees); it is "
                        "never assumed. Missing required input -> BLOCKED."
                    ),
                    rule=rule,
                    field_name="circular_dorgir",
                )
            ],
        )
    if not isinstance(circular_raw, bool):
        return _invalid_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                EngineeringDiagnostic(
                    code="INVALID_CIRCULAR_DORGIR",
                    severity=DiagnosticSeverity.ERROR,
                    message=f"circular_dorgir must be a bool, got {circular_raw!r}.",
                    rule_id=rule_id,
                    field_name="circular_dorgir",
                )
            ],
        )

    invalid: List[EngineeringDiagnostic] = []
    missing: List[EngineeringDiagnostic] = []
    _require_positive(
        bend_angle_deg,
        code="MISSING_BEND_ANGLE",
        field_name="bend_angle_deg",
        message=(
            "The seismic-hook bend angle is required for the Clause 9-21-2-2-4 "
            "check; it is never assumed. Missing required input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    _require_positive(
        straight_extension_mm,
        code="MISSING_STRAIGHT_EXTENSION",
        field_name="straight_extension_mm",
        message=(
            "The straight extension after the bend is required for the Clause "
            "9-21-2-2-4 check; it is never assumed. Missing required input -> "
            "BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    _require_positive(
        bar_diameter_mm,
        code="MISSING_BAR_DIAMETER",
        field_name="bar_diameter_mm",
        message=(
            "The bar diameter d_b is required for the 6*d_b seismic-hook "
            "extension of Clause 9-21-2-2-4; it is never assumed. Missing "
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
    assert bend_angle_deg is not None
    assert straight_extension_mm is not None
    assert bar_diameter_mm is not None

    if bend_angle_deg > BG_TRANS_SEISMIC_HOOK_MAX_BEND_DEG:
        return _invalid_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                EngineeringDiagnostic(
                    code="INVALID_BEND_ANGLE",
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        "bend_angle_deg must be in (0, 180] degrees, got "
                        f"{bend_angle_deg!r}."
                    ),
                    rule_id=rule_id,
                    field_name="bend_angle_deg",
                )
            ],
        )

    min_bend_deg = (
        BG_TRANS_SEISMIC_HOOK_CIRCULAR_MIN_BEND_DEG
        if circular_raw
        else BG_TRANS_SEISMIC_HOOK_MIN_BEND_DEG
    )
    ext_6db_mm = BG_TRANS_SEISMIC_HOOK_EXT_DB_FACTOR * bar_diameter_mm
    ext_abs_mm = BG_TRANS_SEISMIC_HOOK_EXT_ABS_MIN_MM
    ext_via_6db = straight_extension_mm >= ext_6db_mm
    ext_via_75 = straight_extension_mm >= ext_abs_mm

    if bend_angle_deg < min_bend_deg:
        diag = EngineeringDiagnostic(
            code="SEISMIC_HOOK_BEND_BELOW_MINIMUM",
            severity=DiagnosticSeverity.ERROR,
            message=(
                f"FAIL: a seismic hook per Clause 9-21-2-2-4 requires a bend of "
                f"at least {min_bend_deg} degrees "
                f"({'circular دورگیر' if circular_raw else 'non-circular'}); the "
                f"provided bend {bend_angle_deg} degrees is insufficient."
            ),
            rule_id=rule_id,
            field_name="bend_angle_deg",
        )
        return _fail_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates={
                "bend_angle_deg": bend_angle_deg,
                "min_bend_deg": min_bend_deg,
            },
            final_result=bend_angle_deg,
            unit="deg",
            diagnostic=diag,
        )

    if not (ext_via_6db or ext_via_75):
        diag = EngineeringDiagnostic(
            code="SEISMIC_HOOK_EXTENSION_BELOW_MINIMUM",
            severity=DiagnosticSeverity.ERROR,
            message=(
                f"FAIL: the straight extension after the bend of a seismic hook "
                f"per Clause 9-21-2-2-4 must be at least 6*d_b = {ext_6db_mm} mm "
                f"or {ext_abs_mm} mm; the provided extension "
                f"{straight_extension_mm} mm satisfies neither."
            ),
            rule_id=rule_id,
            field_name="straight_extension_mm",
        )
        return _fail_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates={
                "straight_extension_mm": straight_extension_mm,
                "extension_6db_mm": ext_6db_mm,
                "extension_abs_min_mm": ext_abs_mm,
            },
            final_result=straight_extension_mm,
            unit="mm",
            diagnostic=diag,
        )

    intermediates: Dict[str, float] = {
        "bend_angle_deg": bend_angle_deg,
        "min_bend_deg": min_bend_deg,
        "straight_extension_mm": straight_extension_mm,
        "extension_6db_mm": ext_6db_mm,
        "extension_abs_min_mm": ext_abs_mm,
    }
    return _pass_step(
        gate,
        raw_inputs=raw_inputs,
        intermediates=intermediates,
        final_result=straight_extension_mm,
        unit="mm",
        message=(
            f"PASS: seismic hook per Clause 9-21-2-2-4 — bend {bend_angle_deg} "
            f"deg >= {min_bend_deg} deg and straight extension "
            f"{straight_extension_mm} mm >= 6*d_b = {ext_6db_mm} mm "
            f"(or >= {ext_abs_mm} mm)."
        ),
    )


# --- BG-TRANS-DORGIR-001 (Clause 9-21-6-4-1 & 9-21-6-4-2, PDF p. 470 / Printed p. 450)
def evaluate_dorgir(
    *,
    dorgir_construction: Optional[DorgirConstruction] = None,
    uses_interconnected_headed_bars: Optional[bool] = None,
    hook_bend_angle_deg: Optional[float] = None,
    hook_straight_extension_mm: Optional[float] = None,
    hook_bar_diameter_mm: Optional[float] = None,
    hook_circular_dorgir: Optional[bool] = None,
    hook_encloses_longitudinal_bar: Optional[bool] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate the confinement tie دورگیر (BG-TRANS-DORGIR-001).

    Verified source: Mabhas 9 (1399), Clauses 9-21-6-4-1 & 9-21-6-4-2,
    PDF p. 470 / Printed p. 450. Clause 9-21-6-4-1: دورگیر shall consist of
    closed ties or be wound continuously. Clause 9-21-6-4-2: دورگیر may be
    made of several parts, each anchored at both ends by a seismic hook per
    Clause 9-21-2-2-4; each hook encloses one longitudinal bar; interconnected
    headed bars (میلگردهای سَر دار متصل به هم) are not permitted as دورگیر.

    ``dorgir_construction`` and ``uses_interconnected_headed_bars`` are
    REQUIRED typed inputs. For MULTI_PART the per-component seismic-hook
    geometry (``hook_bend_angle_deg``, ``hook_straight_extension_mm``,
    ``hook_bar_diameter_mm``, ``hook_circular_dorgir``) and
    ``hook_encloses_longitudinal_bar`` are REQUIRED; the hook geometry is
    delegated to the verified seismic-hook rule (BG-TRANS-SEISMIC-HOOK-001,
    Clause 9-21-2-2-4) rather than duplicated. No geometry beyond these
    clauses is invented. Missing/invalid inputs -> BLOCKED/INVALID_INPUT,
    never PASS.
    """
    rule_id = RULE_BG_TRANS_DORGIR_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "dorgir_construction": (
            dorgir_construction.value
            if isinstance(dorgir_construction, DorgirConstruction)
            else dorgir_construction
        ),
        "uses_interconnected_headed_bars": uses_interconnected_headed_bars,
        "hook_bend_angle_deg": hook_bend_angle_deg,
        "hook_straight_extension_mm": hook_straight_extension_mm,
        "hook_bar_diameter_mm": hook_bar_diameter_mm,
        "hook_circular_dorgir": hook_circular_dorgir,
        "hook_encloses_longitudinal_bar": hook_encloses_longitudinal_bar,
    }

    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")
    rule = gate.rule

    constr_raw: object = dorgir_construction
    if constr_raw is None:
        return _blocked_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _missing_input_diagnostic(
                    "MISSING_DORGIR_CONSTRUCTION",
                    (
                        "The دورگیر construction class (closed tie, wound "
                        "continuous, or multi-part) is required for Clause "
                        "9-21-6-4; it is never assumed. Missing required input "
                        "-> BLOCKED."
                    ),
                    rule=rule,
                    field_name="dorgir_construction",
                )
            ],
        )
    if not isinstance(constr_raw, DorgirConstruction):
        return _invalid_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                EngineeringDiagnostic(
                    code="INVALID_DORGIR_CONSTRUCTION",
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        "dorgir_construction must be a DorgirConstruction "
                        f"value, got {constr_raw!r}."
                    ),
                    rule_id=rule_id,
                    field_name="dorgir_construction",
                )
            ],
        )

    headed_raw: object = uses_interconnected_headed_bars
    if headed_raw is None:
        return _blocked_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _missing_input_diagnostic(
                    "MISSING_USES_INTERCONNECTED_HEADED_BARS",
                    (
                        "Whether interconnected headed bars are used as دورگیر "
                        "is required to apply the Clause 9-21-6-4-2 prohibition; "
                        "it is never assumed. Missing required input -> BLOCKED."
                    ),
                    rule=rule,
                    field_name="uses_interconnected_headed_bars",
                )
            ],
        )
    if not isinstance(headed_raw, bool):
        return _invalid_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                EngineeringDiagnostic(
                    code="INVALID_USES_INTERCONNECTED_HEADED_BARS",
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        "uses_interconnected_headed_bars must be a bool, got "
                        f"{headed_raw!r}."
                    ),
                    rule_id=rule_id,
                    field_name="uses_interconnected_headed_bars",
                )
            ],
        )

    if headed_raw:
        diag = EngineeringDiagnostic(
            code="DORGIR_HEADED_BARS_PROHIBITED",
            severity=DiagnosticSeverity.ERROR,
            message=(
                "FAIL: the use of interconnected headed bars (میلگردهای سَر دار "
                "متصل به هم) as دورگیر is not permitted per Clause 9-21-6-4-2."
            ),
            rule_id=rule_id,
            field_name="uses_interconnected_headed_bars",
        )
        return _fail_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates={},
            final_result=None,
            unit="mm",
            diagnostic=diag,
        )

    if constr_raw in (
        DorgirConstruction.CLOSED_TIE,
        DorgirConstruction.WOUND_CONTINUOUS,
    ):
        return _pass_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates={},
            final_result=None,
            unit="mm",
            message=(
                "PASS: دورگیر consists of "
                f"{constr_raw.value.replace('_', ' ')} per Clause 9-21-6-4-1, "
                "and interconnected headed bars are not used."
            ),
        )

    # MULTI_PART -> Clause 9-21-6-4-2
    encl_raw: object = hook_encloses_longitudinal_bar
    if encl_raw is None:
        return _blocked_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _missing_input_diagnostic(
                    "MISSING_HOOK_ENCLOSES_LONGITUDINAL_BAR",
                    (
                        "Whether each multi-piece دورگیر component hook encloses "
                        "a longitudinal bar is required for Clause 9-21-6-4-2; "
                        "it is never assumed. Missing required input -> BLOCKED."
                    ),
                    rule=rule,
                    field_name="hook_encloses_longitudinal_bar",
                )
            ],
        )
    if not isinstance(encl_raw, bool):
        return _invalid_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                EngineeringDiagnostic(
                    code="INVALID_HOOK_ENCLOSES_LONGITUDINAL_BAR",
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        "hook_encloses_longitudinal_bar must be a bool, got "
                        f"{encl_raw!r}."
                    ),
                    rule_id=rule_id,
                    field_name="hook_encloses_longitudinal_bar",
                )
            ],
        )
    if not encl_raw:
        diag = EngineeringDiagnostic(
            code="DORGIR_HOOK_NOT_ENCLOSING_LONGITUDINAL_BAR",
            severity=DiagnosticSeverity.ERROR,
            message=(
                "FAIL: each multi-piece دورگیر component hook must enclose one "
                "longitudinal bar per Clause 9-21-6-4-2."
            ),
            rule_id=rule_id,
            field_name="hook_encloses_longitudinal_bar",
        )
        return _fail_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates={},
            final_result=None,
            unit="mm",
            diagnostic=diag,
        )

    # Delegate the component hook geometry to the verified seismic-hook rule
    # (Clause 9-21-2-2-4) instead of duplicating its formula.
    hook_step = evaluate_seismic_hook(
        circular_dorgir=hook_circular_dorgir,
        bend_angle_deg=hook_bend_angle_deg,
        straight_extension_mm=hook_straight_extension_mm,
        bar_diameter_mm=hook_bar_diameter_mm,
        jurisdiction_mode=jurisdiction_mode,
    )
    if hook_step.outcome is EvaluationOutcome.PASS:
        hook_ext = hook_straight_extension_mm
        assert hook_ext is not None
        return _pass_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates={"hook_straight_extension_mm": hook_ext},
            final_result=hook_ext,
            unit="mm",
            message=(
                "PASS: multi-piece دورگیر per Clause 9-21-6-4-2 — each component "
                "is anchored at both ends by a seismic hook (Clause 9-21-2-2-4) "
                "that encloses a longitudinal bar, and interconnected headed "
                "bars are not used."
            ),
        )
    if hook_step.outcome is EvaluationOutcome.FAIL:
        diag = EngineeringDiagnostic(
            code="DORGIR_COMPONENT_SEISMIC_HOOK_NOT_SATISFIED",
            severity=DiagnosticSeverity.ERROR,
            message=(
                "FAIL: a multi-piece دورگیر component hook must satisfy the "
                "seismic-hook geometry of Clause 9-21-2-2-4; "
                f"{hook_step.message}"
            ),
            rule_id=rule_id,
            field_name="hook_bend_angle_deg",
        )
        return _fail_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates={},
            final_result=None,
            unit="mm",
            diagnostic=diag,
        )
    if hook_step.outcome is EvaluationOutcome.INVALID_INPUT:
        return _invalid_step(
            gate, raw_inputs=raw_inputs, diagnostics=list(hook_step.diagnostics)
        )
    # hook_step BLOCKED (missing/incomplete seismic-hook inputs) -> propagate.
    return _blocked_step(
        gate, raw_inputs=raw_inputs, diagnostics=list(hook_step.diagnostics)
    )


# --- BG-TRANS-TWO-PIECE-TIE-001 (Clause 9-21-6-1-7, PDF p. 465 / Printed p. 445)
def evaluate_two_piece_tie(
    *,
    u_tie_bend_angle_deg: Optional[float] = None,
    second_member_bend_angle_deg: Optional[float] = None,
    second_member_adjacent_nonspalling_face: Optional[bool] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate the two-piece torsion/integrity tie (BG-TRANS-TWO-PIECE-TIE-001).

    Verified source: Mabhas 9 (1399), Clause 9-21-6-1-7, PDF p. 465 /
    Printed p. 445: a tie for torsion/cracking may be made of two parts — a
    U-shaped tie with 135-degree bends, and a member (سنگراقی) whose 90-degree
    bend shall be adjacent to the member face where the concrete is not
    susceptible to deterioration from flange/slab confinement.

    Only the requirements stated in 9-21-6-1-7 are represented; no bend
    diameter, embedment length, or other geometry is invented.
    ``u_tie_bend_angle_deg``, ``second_member_bend_angle_deg`` and
    ``second_member_adjacent_nonspalling_face`` are REQUIRED typed inputs.
    Missing/invalid inputs -> BLOCKED/INVALID_INPUT, never PASS.
    """
    rule_id = RULE_BG_TRANS_TWO_PIECE_TIE_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "u_tie_bend_angle_deg": u_tie_bend_angle_deg,
        "second_member_bend_angle_deg": second_member_bend_angle_deg,
        "second_member_adjacent_nonspalling_face": (
            second_member_adjacent_nonspalling_face
        ),
    }

    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="deg")
    rule = gate.rule

    invalid: List[EngineeringDiagnostic] = []
    missing: List[EngineeringDiagnostic] = []
    _require_positive(
        u_tie_bend_angle_deg,
        code="MISSING_U_TIE_BEND_ANGLE",
        field_name="u_tie_bend_angle_deg",
        message=(
            "The U-tie bend angle is required for the Clause 9-21-6-1-7 "
            "check; it is never assumed. Missing required input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    _require_positive(
        second_member_bend_angle_deg,
        code="MISSING_SECOND_MEMBER_BEND_ANGLE",
        field_name="second_member_bend_angle_deg",
        message=(
            "The second-member bend angle is required for the Clause 9-21-6-1-7 "
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
    assert u_tie_bend_angle_deg is not None
    assert second_member_bend_angle_deg is not None

    face_raw: object = second_member_adjacent_nonspalling_face
    if face_raw is None:
        return _blocked_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _missing_input_diagnostic(
                    "MISSING_SECOND_MEMBER_ADJACENT_NONSPALLING_FACE",
                    (
                        "Whether the second-member 90-degree bend is adjacent to "
                        "the non-spalling member face is required for Clause "
                        "9-21-6-1-7; it is never assumed. Missing required input "
                        "-> BLOCKED."
                    ),
                    rule=rule,
                    field_name="second_member_adjacent_nonspalling_face",
                )
            ],
        )
    if not isinstance(face_raw, bool):
        return _invalid_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                EngineeringDiagnostic(
                    code="INVALID_SECOND_MEMBER_ADJACENT_NONSPALLING_FACE",
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        "second_member_adjacent_nonspalling_face must be a bool, "
                        f"got {face_raw!r}."
                    ),
                    rule_id=rule_id,
                    field_name="second_member_adjacent_nonspalling_face",
                )
            ],
        )
    for angle in (u_tie_bend_angle_deg, second_member_bend_angle_deg):
        if angle > BG_TRANS_SEISMIC_HOOK_MAX_BEND_DEG:
            return _invalid_step(
                gate,
                raw_inputs=raw_inputs,
                diagnostics=[
                    EngineeringDiagnostic(
                        code="INVALID_BEND_ANGLE",
                        severity=DiagnosticSeverity.ERROR,
                        message=(
                            "bend angles must be in (0, 180] degrees, got "
                            f"{angle!r}."
                        ),
                        rule_id=rule_id,
                    )
                ],
            )

    if u_tie_bend_angle_deg < BG_TRANS_TWO_PIECE_U_BEND_MIN_DEG:
        diag = EngineeringDiagnostic(
            code="TWO_PIECE_U_BEND_BELOW_135",
            severity=DiagnosticSeverity.ERROR,
            message=(
                f"FAIL: the U-tie bends of a two-piece tie per Clause 9-21-6-1-7 "
                f"must be 135 degrees (>= {BG_TRANS_TWO_PIECE_U_BEND_MIN_DEG}); "
                f"the provided {u_tie_bend_angle_deg} degrees is insufficient."
            ),
            rule_id=rule_id,
            field_name="u_tie_bend_angle_deg",
        )
        return _fail_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates={
                "u_tie_bend_angle_deg": u_tie_bend_angle_deg,
                "min_u_bend_deg": BG_TRANS_TWO_PIECE_U_BEND_MIN_DEG,
            },
            final_result=u_tie_bend_angle_deg,
            unit="deg",
            diagnostic=diag,
        )

    if second_member_bend_angle_deg != BG_TRANS_TWO_PIECE_MEMBER_BEND_DEG:
        diag = EngineeringDiagnostic(
            code="TWO_PIECE_MEMBER_BEND_NOT_90",
            severity=DiagnosticSeverity.ERROR,
            message=(
                f"FAIL: the second member of a two-piece tie per Clause "
                f"9-21-6-1-7 must have a 90-degree bend; the provided "
                f"{second_member_bend_angle_deg} degrees is not 90 degrees."
            ),
            rule_id=rule_id,
            field_name="second_member_bend_angle_deg",
        )
        return _fail_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates={
                "second_member_bend_angle_deg": second_member_bend_angle_deg,
                "required_member_bend_deg": BG_TRANS_TWO_PIECE_MEMBER_BEND_DEG,
            },
            final_result=second_member_bend_angle_deg,
            unit="deg",
            diagnostic=diag,
        )

    if not face_raw:
        diag = EngineeringDiagnostic(
            code="TWO_PIECE_MEMBER_BEND_NOT_AT_NONSPALLING_FACE",
            severity=DiagnosticSeverity.ERROR,
            message=(
                "FAIL: the second-member 90-degree bend of a two-piece tie per "
                "Clause 9-21-6-1-7 must be adjacent to the member face where "
                "the concrete is not susceptible to deterioration from "
                "flange/slab confinement."
            ),
            rule_id=rule_id,
            field_name="second_member_adjacent_nonspalling_face",
        )
        return _fail_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates={},
            final_result=None,
            unit="deg",
            diagnostic=diag,
        )

    intermediates: Dict[str, float] = {
        "u_tie_bend_angle_deg": u_tie_bend_angle_deg,
        "second_member_bend_angle_deg": second_member_bend_angle_deg,
    }
    return _pass_step(
        gate,
        raw_inputs=raw_inputs,
        intermediates=intermediates,
        final_result=u_tie_bend_angle_deg,
        unit="deg",
        message=(
            "PASS: two-piece tie per Clause 9-21-6-1-7 — U-tie with 135-degree "
            "bends and a second member with a 90-degree bend adjacent to the "
            "non-spalling member face."
        ),
    )


# --- BG-TRANS-TORSION-TIE-135HOOK-001 (Clause 9-21-6-1-6-الف, PDF p. 464 / Printed p. 444)
def evaluate_torsion_tie_135hook(
    *,
    hook_bend_angle_deg: Optional[float] = None,
    hook_engages_longitudinal_bar: Optional[bool] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate the torsion/integrity tie 135-degree hook (BG-TRANS-TORSION-TIE-135HOOK-001).

    Verified source: Mabhas 9 (1399), Clause 9-21-6-1-6(الف), PDF p. 464 /
    Printed p. 444: both ends of the tie shall be terminated with a 135-degree
    hook around the longitudinal bar. Only the deterministic (الف) branch is
    implemented; this rule's scope is unchanged. The (ب) branch delegates to
    Clauses 9-21-6-1-3-الف/-ب OR Clause 9-21-6-1-4: the 9-21-6-1-4 route is now
    executable (promoted in Stage H.7 to BG-TRANS-TORSION-TIE-WIRE-ROUTE-001,
    which delegates the U-tie geometry to BG-TRANS-WIRE-TIE-UTIE-001) while
    the 9-21-6-1-3 route stays BLOCKED (fy/d_b boundary gap; kept under
    BG-TRANS-TORSION-TIE-PENDING), so the (ب) clause as a whole is NOT
    executed and is not claimed executable here. (Stage H.7 metadata
    correction M2: the earlier wording said both 9-21-6-1-3 and 9-21-6-1-4
    were 'still-blocked'; 9-21-6-1-4 is no longer blocked.)

    ``hook_bend_angle_deg`` (the tie-end hook bend, applying to both ends) and
    ``hook_engages_longitudinal_bar`` are REQUIRED typed inputs. Missing/invalid
    inputs -> BLOCKED/INVALID_INPUT, never PASS.
    """
    rule_id = RULE_BG_TRANS_TORSION_TIE_135HOOK_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "hook_bend_angle_deg": hook_bend_angle_deg,
        "hook_engages_longitudinal_bar": hook_engages_longitudinal_bar,
    }

    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="deg")
    rule = gate.rule

    invalid: List[EngineeringDiagnostic] = []
    missing: List[EngineeringDiagnostic] = []
    _require_positive(
        hook_bend_angle_deg,
        code="MISSING_HOOK_BEND_ANGLE",
        field_name="hook_bend_angle_deg",
        message=(
            "The tie-end hook bend angle is required for the Clause 9-21-6-1-6-"
            "الف check; it is never assumed. Missing required input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    if invalid:
        return _invalid_step(gate, raw_inputs=raw_inputs, diagnostics=invalid)
    if missing:
        return _blocked_step(gate, raw_inputs=raw_inputs, diagnostics=missing)
    assert hook_bend_angle_deg is not None

    engages_raw: object = hook_engages_longitudinal_bar
    if engages_raw is None:
        return _blocked_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _missing_input_diagnostic(
                    "MISSING_HOOK_ENGAGES_LONGITUDINAL_BAR",
                    (
                        "Whether the tie-end hook engages a longitudinal bar is "
                        "required for the Clause 9-21-6-1-6-الف check; it is "
                        "never assumed. Missing required input -> BLOCKED."
                    ),
                    rule=rule,
                    field_name="hook_engages_longitudinal_bar",
                )
            ],
        )
    if not isinstance(engages_raw, bool):
        return _invalid_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                EngineeringDiagnostic(
                    code="INVALID_HOOK_ENGAGES_LONGITUDINAL_BAR",
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        "hook_engages_longitudinal_bar must be a bool, got "
                        f"{engages_raw!r}."
                    ),
                    rule_id=rule_id,
                    field_name="hook_engages_longitudinal_bar",
                )
            ],
        )

    if hook_bend_angle_deg > BG_TRANS_SEISMIC_HOOK_MAX_BEND_DEG:
        return _invalid_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                EngineeringDiagnostic(
                    code="INVALID_BEND_ANGLE",
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        "hook_bend_angle_deg must be in (0, 180] degrees, got "
                        f"{hook_bend_angle_deg!r}."
                    ),
                    rule_id=rule_id,
                    field_name="hook_bend_angle_deg",
                )
            ],
        )

    if hook_bend_angle_deg < BG_TRANS_TIE_135_HOOK_MIN_BEND_DEG:
        diag = EngineeringDiagnostic(
            code="TORSION_TIE_135_HOOK_BEND_BELOW_135",
            severity=DiagnosticSeverity.ERROR,
            message=(
                f"FAIL: both tie ends must be terminated with a 135-degree hook "
                f"per Clause 9-21-6-1-6-الف; the provided bend "
                f"{hook_bend_angle_deg} degrees is below "
                f"{BG_TRANS_TIE_135_HOOK_MIN_BEND_DEG} degrees."
            ),
            rule_id=rule_id,
            field_name="hook_bend_angle_deg",
        )
        return _fail_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates={
                "hook_bend_angle_deg": hook_bend_angle_deg,
                "min_bend_deg": BG_TRANS_TIE_135_HOOK_MIN_BEND_DEG,
            },
            final_result=hook_bend_angle_deg,
            unit="deg",
            diagnostic=diag,
        )

    if not engages_raw:
        diag = EngineeringDiagnostic(
            code="TORSION_TIE_135_HOOK_NOT_ENGAGING_LONGITUDINAL_BAR",
            severity=DiagnosticSeverity.ERROR,
            message=(
                "FAIL: both tie ends must be terminated with a 135-degree hook "
                "around the longitudinal bar per Clause 9-21-6-1-6-الف; the "
                "provided hook does not engage a longitudinal bar."
            ),
            rule_id=rule_id,
            field_name="hook_engages_longitudinal_bar",
        )
        return _fail_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates={"hook_bend_angle_deg": hook_bend_angle_deg},
            final_result=hook_bend_angle_deg,
            unit="deg",
            diagnostic=diag,
        )

    intermediates: Dict[str, float] = {
        "hook_bend_angle_deg": hook_bend_angle_deg,
        "min_bend_deg": BG_TRANS_TIE_135_HOOK_MIN_BEND_DEG,
    }
    return _pass_step(
        gate,
        raw_inputs=raw_inputs,
        intermediates=intermediates,
        final_result=hook_bend_angle_deg,
        unit="deg",
        message=(
            f"PASS: both tie ends terminated with a {hook_bend_angle_deg}-degree "
            "hook engaging the longitudinal bar per Clause 9-21-6-1-6-الف."
        ),
    )


# --- BG-TRANS-TORSION-TIE-SEISMIC-HOOK-001 (Clause 9-21-6-2-7-الف seismic-hook branch,
#     PDF p. 467 / Printed p. 447; hook geometry per Clause 9-21-2-2-4, PDF p. 442)
def evaluate_torsion_tie_seismic_hook(
    *,
    hook_bend_angle_deg: Optional[float] = None,
    hook_straight_extension_mm: Optional[float] = None,
    hook_bar_diameter_mm: Optional[float] = None,
    hook_circular_dorgir: Optional[bool] = None,
    hook_engages_longitudinal_bar: Optional[bool] = None,
    bend_end_anchored_in_core_concrete: Optional[bool] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate the torsion-tie seismic-hook branch (BG-TRANS-TORSION-TIE-SEISMIC-HOOK-001).

    Verified source: Mabhas 9 (1399), Clause 9-21-6-2-7(الف), PDF p. 467 /
    Printed p. 447: both ends of a torsion tie shall be terminated with a
    seismic hook around the longitudinal bar, with the bend end anchored in
    the core concrete. Only the seismic-hook option of 9-21-6-2-7(الف) is
    implemented here; the standard 135-degree hook option is implemented
    separately as BG-TRANS-TORSION-TIE-STANDARD-HOOK-001 (geometry per the
    verified Table 9-21-2, PDF pp. 442-443) and the (ب) branch routes through
    blocked rules — neither is executed here. The seismic-hook geometry is
    delegated to the verified seismic-hook rule (BG-TRANS-SEISMIC-HOOK-001,
    Clause 9-21-2-2-4).

    ``hook_engages_longitudinal_bar`` and
    ``bend_end_anchored_in_core_concrete`` plus the seismic-hook geometry
    inputs are REQUIRED typed inputs. Missing/invalid inputs ->
    BLOCKED/INVALID_INPUT, never PASS.
    """
    rule_id = RULE_BG_TRANS_TORSION_TIE_SEISMIC_HOOK_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "hook_bend_angle_deg": hook_bend_angle_deg,
        "hook_straight_extension_mm": hook_straight_extension_mm,
        "hook_bar_diameter_mm": hook_bar_diameter_mm,
        "hook_circular_dorgir": hook_circular_dorgir,
        "hook_engages_longitudinal_bar": hook_engages_longitudinal_bar,
        "bend_end_anchored_in_core_concrete": bend_end_anchored_in_core_concrete,
    }

    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")
    rule = gate.rule

    engages_raw: object = hook_engages_longitudinal_bar
    if engages_raw is None:
        return _blocked_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _missing_input_diagnostic(
                    "MISSING_HOOK_ENGAGES_LONGITUDINAL_BAR",
                    (
                        "Whether the torsion-tie seismic hook engages a "
                        "longitudinal bar is required for Clause 9-21-6-2-7-الف; "
                        "it is never assumed. Missing required input -> BLOCKED."
                    ),
                    rule=rule,
                    field_name="hook_engages_longitudinal_bar",
                )
            ],
        )
    if not isinstance(engages_raw, bool):
        return _invalid_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                EngineeringDiagnostic(
                    code="INVALID_HOOK_ENGAGES_LONGITUDINAL_BAR",
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        "hook_engages_longitudinal_bar must be a bool, got "
                        f"{engages_raw!r}."
                    ),
                    rule_id=rule_id,
                    field_name="hook_engages_longitudinal_bar",
                )
            ],
        )

    core_raw: object = bend_end_anchored_in_core_concrete
    if core_raw is None:
        return _blocked_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _missing_input_diagnostic(
                    "MISSING_BEND_END_ANCHORED_IN_CORE_CONCRETE",
                    (
                        "Whether the bend end is anchored in the core concrete "
                        "is required for Clause 9-21-6-2-7-الف; it is never "
                        "assumed. Missing required input -> BLOCKED."
                    ),
                    rule=rule,
                    field_name="bend_end_anchored_in_core_concrete",
                )
            ],
        )
    if not isinstance(core_raw, bool):
        return _invalid_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                EngineeringDiagnostic(
                    code="INVALID_BEND_END_ANCHORED_IN_CORE_CONCRETE",
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        "bend_end_anchored_in_core_concrete must be a bool, got "
                        f"{core_raw!r}."
                    ),
                    rule_id=rule_id,
                    field_name="bend_end_anchored_in_core_concrete",
                )
            ],
        )

    if not engages_raw:
        diag = EngineeringDiagnostic(
            code="TORSION_TIE_SEISMIC_HOOK_NOT_ENGAGING_LONGITUDINAL_BAR",
            severity=DiagnosticSeverity.ERROR,
            message=(
                "FAIL: both torsion-tie ends must be terminated with a seismic "
                "hook around the longitudinal bar per Clause 9-21-6-2-7-الف; "
                "the provided hook does not engage a longitudinal bar."
            ),
            rule_id=rule_id,
            field_name="hook_engages_longitudinal_bar",
        )
        return _fail_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates={},
            final_result=None,
            unit="mm",
            diagnostic=diag,
        )

    if not core_raw:
        diag = EngineeringDiagnostic(
            code="TORSION_TIE_BEND_END_NOT_IN_CORE_CONCRETE",
            severity=DiagnosticSeverity.ERROR,
            message=(
                "FAIL: the bend end of the torsion-tie seismic hook must be "
                "anchored in the core concrete per Clause 9-21-6-2-7-الف."
            ),
            rule_id=rule_id,
            field_name="bend_end_anchored_in_core_concrete",
        )
        return _fail_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates={},
            final_result=None,
            unit="mm",
            diagnostic=diag,
        )

    # Delegate the seismic-hook geometry to the verified seismic-hook rule
    # (Clause 9-21-2-2-4) instead of duplicating its formula.
    hook_step = evaluate_seismic_hook(
        circular_dorgir=hook_circular_dorgir,
        bend_angle_deg=hook_bend_angle_deg,
        straight_extension_mm=hook_straight_extension_mm,
        bar_diameter_mm=hook_bar_diameter_mm,
        jurisdiction_mode=jurisdiction_mode,
    )
    if hook_step.outcome is EvaluationOutcome.PASS:
        hook_ext = hook_straight_extension_mm
        assert hook_ext is not None
        return _pass_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates={"hook_straight_extension_mm": hook_ext},
            final_result=hook_ext,
            unit="mm",
            message=(
                "PASS: both torsion-tie ends terminated with a seismic hook "
                "(Clause 9-21-2-2-4) engaging the longitudinal bar, with the "
                "bend end anchored in the core concrete, per Clause 9-21-6-2-7-"
                "الف."
            ),
        )
    if hook_step.outcome is EvaluationOutcome.FAIL:
        diag = EngineeringDiagnostic(
            code="TORSION_TIE_SEISMIC_HOOK_GEOMETRY_NOT_SATISFIED",
            severity=DiagnosticSeverity.ERROR,
            message=(
                "FAIL: the torsion-tie seismic hook must satisfy the seismic-"
                f"hook geometry of Clause 9-21-2-2-4; {hook_step.message}"
            ),
            rule_id=rule_id,
            field_name="hook_bend_angle_deg",
        )
        return _fail_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates={},
            final_result=None,
            unit="mm",
            diagnostic=diag,
        )
    if hook_step.outcome is EvaluationOutcome.INVALID_INPUT:
        return _invalid_step(
            gate, raw_inputs=raw_inputs, diagnostics=list(hook_step.diagnostics)
        )
    return _blocked_step(
        gate, raw_inputs=raw_inputs, diagnostics=list(hook_step.diagnostics)
    )


# --- BG-TRANS-STANDARD-HOOK-001 (Clause 9-21-2-2-2 & Table 9-21-2, PDF pp. 442-443)
def evaluate_standard_hook(
    *,
    hook_angle_deg: Optional[float] = None,
    bar_diameter_mm: Optional[float] = None,
    inner_bend_diameter_mm: Optional[float] = None,
    straight_extension_mm: Optional[float] = None,
    encloses_longitudinal_bar: Optional[bool] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate the standard transverse-bar hook geometry (BG-TRANS-STANDARD-HOOK-001).

    Verified source: Mabhas 9 (1399), Clause 9-21-2-2-2 & 9-21-2-2-3 with
    Table 9-21-2, PDF pp. 442-443 / Printed pp. 442-443: standard hooks for
    transverse bars shall comply with Table 9-21-2 and shall enclose a
    longitudinal bar. For BOTH the 90-degree and 135-degree standard hooks,
    d_b 10-16 mm -> minimum inner bend diameter 4*d_b and straight extension
    max(6*d_b, 75 mm); d_b 18-25 mm -> minimum inner bend diameter 6*d_b and
    straight extension 12*d_b. The 180-degree hook (printed with the same
    geometry but not exercised by any Clause 9-21-6 rule this stage),
    d_b = 17 mm (gap between the printed rows), d_b < 10 mm and d_b > 25 mm
    are deterministically BLOCKED and never interpolated.

    hook_angle_deg, bar_diameter_mm, inner_bend_diameter_mm,
    straight_extension_mm and encloses_longitudinal_bar are REQUIRED typed
    inputs (never assumed). Missing/invalid inputs -> BLOCKED/INVALID_INPUT.
    """
    rule_id = RULE_BG_TRANS_STANDARD_HOOK_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "hook_angle_deg": hook_angle_deg,
        "bar_diameter_mm": bar_diameter_mm,
        "inner_bend_diameter_mm": inner_bend_diameter_mm,
        "straight_extension_mm": straight_extension_mm,
        "encloses_longitudinal_bar": encloses_longitudinal_bar,
    }

    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")
    rule = gate.rule

    encloses_raw: object = encloses_longitudinal_bar
    if encloses_raw is None:
        return _blocked_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _missing_input_diagnostic(
                    "MISSING_ENCLOSES_LONGITUDINAL_BAR",
                    (
                        "Whether the standard hook encloses a longitudinal bar "
                        "is required by Clause 9-21-2-2-2; it is never assumed. "
                        "Missing required input -> BLOCKED."
                    ),
                    rule=rule,
                    field_name="encloses_longitudinal_bar",
                )
            ],
        )
    if not isinstance(encloses_raw, bool):
        return _invalid_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                EngineeringDiagnostic(
                    code="INVALID_ENCLOSES_LONGITUDINAL_BAR",
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        "encloses_longitudinal_bar must be a bool, got "
                        f"{encloses_raw!r}."
                    ),
                    rule_id=rule_id,
                    field_name="encloses_longitudinal_bar",
                )
            ],
        )

    invalid: List[EngineeringDiagnostic] = []
    missing: List[EngineeringDiagnostic] = []
    _require_positive(
        hook_angle_deg,
        code="MISSING_HOOK_ANGLE",
        field_name="hook_angle_deg",
        message=(
            "The standard-hook angle is required to select the Table 9-21-2 "
            "row; it is never assumed. Missing required input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    _require_positive(
        bar_diameter_mm,
        code="MISSING_BAR_DIAMETER",
        field_name="bar_diameter_mm",
        message=(
            "The bar diameter d_b is required to select the Table 9-21-2 "
            "diameter row and the 4*d_b / 6*d_b bend and 6*d_b / 12*d_b "
            "extension limits; it is never assumed. Missing required input "
            "-> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    _require_positive(
        inner_bend_diameter_mm,
        code="MISSING_INNER_BEND_DIAMETER",
        field_name="inner_bend_diameter_mm",
        message=(
            "The inner bend diameter is required for the Table 9-21-2 "
            "standard-hook check; it is never assumed. Missing required "
            "input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    _require_positive(
        straight_extension_mm,
        code="MISSING_STRAIGHT_EXTENSION",
        field_name="straight_extension_mm",
        message=(
            "The straight extension after the bend is required for the Table "
            "9-21-2 standard-hook check; it is never assumed. Missing "
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
    assert hook_angle_deg is not None
    assert bar_diameter_mm is not None
    assert inner_bend_diameter_mm is not None
    assert straight_extension_mm is not None

    # Hook-angle support: only 90 and 135 degrees are implemented this stage.
    if hook_angle_deg == 180.0:
        return _blocked_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _missing_input_diagnostic(
                    "STANDARD_HOOK_180_DEG_NOT_IMPLEMENTED",
                    (
                        "BLOCKED: the 180-degree hook is printed in Table "
                        "9-21-2 with the same geometry, but it is a distinct "
                        "configuration not exercised by any Clause 9-21-6 rule "
                        "in this stage and is deferred to a future stage. "
                        "Supply a 90-degree or 135-degree standard hook."
                    ),
                    rule=rule,
                    field_name="hook_angle_deg",
                )
            ],
        )
    if hook_angle_deg not in BG_TRANS_STD_HOOK_SUPPORTED_ANGLES:
        return _blocked_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _missing_input_diagnostic(
                    "STANDARD_HOOK_ANGLE_NOT_IN_TABLE_9_21_2",
                    (
                        "BLOCKED: Table 9-21-2 specifies only the 90-degree, "
                        "135-degree, and 180-degree standard hooks; the "
                        f"provided hook angle {hook_angle_deg} degrees is not "
                        "a supported standard-hook configuration and is never "
                        "interpreted. Supply a 90-degree or 135-degree hook."
                    ),
                    rule=rule,
                    field_name="hook_angle_deg",
                )
            ],
        )

    # Diameter range selection from Table 9-21-2 (never interpolated).
    if bar_diameter_mm < BG_TRANS_STD_HOOK_DB_SMALL_MIN_MM:
        return _blocked_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _missing_input_diagnostic(
                    "STANDARD_HOOK_DB_BELOW_TABLE",
                    (
                        f"BLOCKED: d_b = {bar_diameter_mm} mm is below the "
                        "smallest diameter row (10-16 mm) printed in Table "
                        "9-21-2; the range is never extrapolated."
                    ),
                    rule=rule,
                    field_name="bar_diameter_mm",
                )
            ],
        )
    if bar_diameter_mm > BG_TRANS_STD_HOOK_DB_LARGE_MAX_MM:
        return _blocked_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _missing_input_diagnostic(
                    "STANDARD_HOOK_DB_ABOVE_TABLE",
                    (
                        f"BLOCKED: d_b = {bar_diameter_mm} mm is above the "
                        "largest diameter row (18-25 mm) printed in Table "
                        "9-21-2; the range is never extrapolated."
                    ),
                    rule=rule,
                    field_name="bar_diameter_mm",
                )
            ],
        )
    if (
        BG_TRANS_STD_HOOK_DB_SMALL_MAX_MM
        < bar_diameter_mm
        < BG_TRANS_STD_HOOK_DB_LARGE_MIN_MM
    ):
        return _blocked_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _missing_input_diagnostic(
                    "STANDARD_HOOK_DB_IN_GAP",
                    (
                        f"BLOCKED: d_b = {bar_diameter_mm} mm falls in the gap "
                        "between the printed 10-16 mm and 18-25 mm rows of "
                        "Table 9-21-2 (no 17 mm row is printed); the gap is "
                        "never interpolated."
                    ),
                    rule=rule,
                    field_name="bar_diameter_mm",
                )
            ],
        )

    if bar_diameter_mm <= BG_TRANS_STD_HOOK_DB_SMALL_MAX_MM:
        min_inner_bend_mm = (
            BG_TRANS_STD_HOOK_SMALL_INNER_DB_FACTOR * bar_diameter_mm
        )
        min_extension_mm = max(
            BG_TRANS_STD_HOOK_SMALL_EXT_DB_FACTOR * bar_diameter_mm,
            BG_TRANS_STD_HOOK_SMALL_EXT_ABS_MIN_MM,
        )
        db_range_label = "10-16 mm"
    else:
        min_inner_bend_mm = (
            BG_TRANS_STD_HOOK_LARGE_INNER_DB_FACTOR * bar_diameter_mm
        )
        min_extension_mm = (
            BG_TRANS_STD_HOOK_LARGE_EXT_DB_FACTOR * bar_diameter_mm
        )
        db_range_label = "18-25 mm"

    if not encloses_raw:
        diag = EngineeringDiagnostic(
            code="STANDARD_HOOK_NOT_ENCLOSING_LONGITUDINAL_BAR",
            severity=DiagnosticSeverity.ERROR,
            message=(
                "FAIL: a standard hook for transverse bars per Clause "
                "9-21-2-2-2 shall enclose a longitudinal bar; the provided "
                "hook does not enclose one."
            ),
            rule_id=rule_id,
            field_name="encloses_longitudinal_bar",
        )
        return _fail_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates={},
            final_result=None,
            unit="mm",
            diagnostic=diag,
        )

    if inner_bend_diameter_mm < min_inner_bend_mm:
        diag = EngineeringDiagnostic(
            code="STANDARD_HOOK_INNER_BEND_BELOW_MINIMUM",
            severity=DiagnosticSeverity.ERROR,
            message=(
                f"FAIL: the inner bend diameter of a {hook_angle_deg}-degree "
                f"standard hook for d_b = {bar_diameter_mm} mm (row "
                f"{db_range_label}) must be at least {min_inner_bend_mm} mm "
                f"per Table 9-21-2; the provided inner bend diameter "
                f"{inner_bend_diameter_mm} mm is insufficient."
            ),
            rule_id=rule_id,
            field_name="inner_bend_diameter_mm",
        )
        return _fail_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates={
                "inner_bend_diameter_mm": inner_bend_diameter_mm,
                "min_inner_bend_diameter_mm": min_inner_bend_mm,
            },
            final_result=inner_bend_diameter_mm,
            unit="mm",
            diagnostic=diag,
        )

    if straight_extension_mm < min_extension_mm:
        diag = EngineeringDiagnostic(
            code="STANDARD_HOOK_EXTENSION_BELOW_MINIMUM",
            severity=DiagnosticSeverity.ERROR,
            message=(
                f"FAIL: the straight extension after the bend of a "
                f"{hook_angle_deg}-degree standard hook for d_b = "
                f"{bar_diameter_mm} mm (row {db_range_label}) must be at "
                f"least {min_extension_mm} mm per Table 9-21-2; the provided "
                f"extension {straight_extension_mm} mm is insufficient."
            ),
            rule_id=rule_id,
            field_name="straight_extension_mm",
        )
        return _fail_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates={
                "straight_extension_mm": straight_extension_mm,
                "min_straight_extension_mm": min_extension_mm,
            },
            final_result=straight_extension_mm,
            unit="mm",
            diagnostic=diag,
        )

    intermediates: Dict[str, float] = {
        "hook_angle_deg": hook_angle_deg,
        "bar_diameter_mm": bar_diameter_mm,
        "inner_bend_diameter_mm": inner_bend_diameter_mm,
        "min_inner_bend_diameter_mm": min_inner_bend_mm,
        "straight_extension_mm": straight_extension_mm,
        "min_straight_extension_mm": min_extension_mm,
    }
    return _pass_step(
        gate,
        raw_inputs=raw_inputs,
        intermediates=intermediates,
        final_result=straight_extension_mm,
        unit="mm",
        message=(
            f"PASS: {hook_angle_deg}-degree standard hook per Clause "
            f"9-21-2-2-2 / Table 9-21-2 (d_b = {bar_diameter_mm} mm, row "
            f"{db_range_label}) — inner bend {inner_bend_diameter_mm} mm >= "
            f"{min_inner_bend_mm} mm, straight extension "
            f"{straight_extension_mm} mm >= {min_extension_mm} mm, enclosing "
            "a longitudinal bar."
        ),
    )


# --- BG-TRANS-TORSION-TIE-STANDARD-HOOK-001 (Clause 9-21-6-2-7-الف standard-hook option)
def evaluate_torsion_tie_standard_hook(
    *,
    hook_bar_diameter_mm: Optional[float] = None,
    hook_inner_bend_diameter_mm: Optional[float] = None,
    hook_straight_extension_mm: Optional[float] = None,
    hook_engages_longitudinal_bar: Optional[bool] = None,
    bend_end_anchored_in_core_concrete: Optional[bool] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate the torsion-tie standard 135-degree hook branch
    (BG-TRANS-TORSION-TIE-STANDARD-HOOK-001).

    Verified source: Mabhas 9 (1399), Clause 9-21-6-2-7(الف), PDF p. 467 /
    Printed p. 447: both ends of a torsion tie shall be terminated with a
    standard 135-degree hook OR a seismic hook around the longitudinal bar,
    with the bend end anchored in the core concrete. Only the standard
    135-degree hook option is implemented here; the seismic-hook option is
    implemented by BG-TRANS-TORSION-TIE-SEISMIC-HOOK-001 and is NOT
    duplicated. The standard-hook geometry is delegated to
    BG-TRANS-STANDARD-HOOK-001 (Clause 9-21-2-2-2 / Table 9-21-2). The (ب)
    branch of Clause 9-21-6-2-7 is NOT included (it remains blocked).

    hook geometry inputs, hook_engages_longitudinal_bar and
    bend_end_anchored_in_core_concrete are REQUIRED typed inputs.
    Missing/invalid -> BLOCKED/INVALID_INPUT, never PASS.
    """
    rule_id = RULE_BG_TRANS_TORSION_TIE_STANDARD_HOOK_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "hook_bar_diameter_mm": hook_bar_diameter_mm,
        "hook_inner_bend_diameter_mm": hook_inner_bend_diameter_mm,
        "hook_straight_extension_mm": hook_straight_extension_mm,
        "hook_engages_longitudinal_bar": hook_engages_longitudinal_bar,
        "bend_end_anchored_in_core_concrete": bend_end_anchored_in_core_concrete,
    }

    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")
    rule = gate.rule

    engages_raw: object = hook_engages_longitudinal_bar
    if engages_raw is None:
        return _blocked_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _missing_input_diagnostic(
                    "MISSING_HOOK_ENGAGES_LONGITUDINAL_BAR",
                    (
                        "Whether the torsion-tie standard hook engages a "
                        "longitudinal bar is required for Clause 9-21-6-2-7-"
                        "الف; it is never assumed. Missing required input -> "
                        "BLOCKED."
                    ),
                    rule=rule,
                    field_name="hook_engages_longitudinal_bar",
                )
            ],
        )
    if not isinstance(engages_raw, bool):
        return _invalid_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                EngineeringDiagnostic(
                    code="INVALID_HOOK_ENGAGES_LONGITUDINAL_BAR",
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        "hook_engages_longitudinal_bar must be a bool, got "
                        f"{engages_raw!r}."
                    ),
                    rule_id=rule_id,
                    field_name="hook_engages_longitudinal_bar",
                )
            ],
        )

    core_raw: object = bend_end_anchored_in_core_concrete
    if core_raw is None:
        return _blocked_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _missing_input_diagnostic(
                    "MISSING_BEND_END_ANCHORED_IN_CORE_CONCRETE",
                    (
                        "Whether the bend end is anchored in the core concrete "
                        "is required for Clause 9-21-6-2-7-الف; it is never "
                        "assumed. Missing required input -> BLOCKED."
                    ),
                    rule=rule,
                    field_name="bend_end_anchored_in_core_concrete",
                )
            ],
        )
    if not isinstance(core_raw, bool):
        return _invalid_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                EngineeringDiagnostic(
                    code="INVALID_BEND_END_ANCHORED_IN_CORE_CONCRETE",
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        "bend_end_anchored_in_core_concrete must be a bool, "
                        f"got {core_raw!r}."
                    ),
                    rule_id=rule_id,
                    field_name="bend_end_anchored_in_core_concrete",
                )
            ],
        )

    if not engages_raw:
        diag = EngineeringDiagnostic(
            code="TORSION_TIE_STANDARD_HOOK_NOT_ENGAGING_LONGITUDINAL_BAR",
            severity=DiagnosticSeverity.ERROR,
            message=(
                "FAIL: both torsion-tie ends must be terminated with a "
                "standard 135-degree hook around the longitudinal bar per "
                "Clause 9-21-6-2-7-الف; the provided hook does not engage a "
                "longitudinal bar."
            ),
            rule_id=rule_id,
            field_name="hook_engages_longitudinal_bar",
        )
        return _fail_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates={},
            final_result=None,
            unit="mm",
            diagnostic=diag,
        )

    if not core_raw:
        diag = EngineeringDiagnostic(
            code="TORSION_TIE_BEND_END_NOT_IN_CORE_CONCRETE",
            severity=DiagnosticSeverity.ERROR,
            message=(
                "FAIL: the bend end of the torsion-tie standard hook must be "
                "anchored in the core concrete per Clause 9-21-6-2-7-الف."
            ),
            rule_id=rule_id,
            field_name="bend_end_anchored_in_core_concrete",
        )
        return _fail_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates={},
            final_result=None,
            unit="mm",
            diagnostic=diag,
        )

    # Delegate the standard 135-degree hook geometry to the verified
    # standard-hook rule (Clause 9-21-2-2-2 / Table 9-21-2) instead of
    # duplicating its table. Longitudinal-bar engagement is already verified
    # above, so it is passed through as enclosing.
    hook_step = evaluate_standard_hook(
        hook_angle_deg=135.0,
        bar_diameter_mm=hook_bar_diameter_mm,
        inner_bend_diameter_mm=hook_inner_bend_diameter_mm,
        straight_extension_mm=hook_straight_extension_mm,
        encloses_longitudinal_bar=True,
        jurisdiction_mode=jurisdiction_mode,
    )
    if hook_step.outcome is EvaluationOutcome.PASS:
        hook_ext = hook_straight_extension_mm
        assert hook_ext is not None
        return _pass_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates={"hook_straight_extension_mm": hook_ext},
            final_result=hook_ext,
            unit="mm",
            message=(
                "PASS: both torsion-tie ends terminated with a standard "
                "135-degree hook (Table 9-21-2) engaging the longitudinal "
                "bar, with the bend end anchored in the core concrete, per "
                "Clause 9-21-6-2-7-الف."
            ),
        )
    if hook_step.outcome is EvaluationOutcome.FAIL:
        diag = EngineeringDiagnostic(
            code="TORSION_TIE_STANDARD_HOOK_GEOMETRY_NOT_SATISFIED",
            severity=DiagnosticSeverity.ERROR,
            message=(
                "FAIL: the torsion-tie standard 135-degree hook must satisfy "
                "the standard-hook geometry of Clause 9-21-2-2-2 / Table "
                f"9-21-2; {hook_step.message}"
            ),
            rule_id=rule_id,
            field_name="hook_inner_bend_diameter_mm",
        )
        return _fail_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates={},
            final_result=None,
            unit="mm",
            diagnostic=diag,
        )
    if hook_step.outcome is EvaluationOutcome.INVALID_INPUT:
        return _invalid_step(
            gate, raw_inputs=raw_inputs, diagnostics=list(hook_step.diagnostics)
        )
    return _blocked_step(
        gate, raw_inputs=raw_inputs, diagnostics=list(hook_step.diagnostics)
    )


# --- BG-TRANS-WIRE-TIE-UTIE-001 (Clause 9-21-6-1-4, PDF p. 464 / Printed p. 444)
def evaluate_wire_tie_utie(
    *,
    alternative: Optional[WireTieUtieAlternative] = None,
    wire_spacing_mm: Optional[float] = None,
    wires_in_upper_part_of_utie: Optional[bool] = None,
    effective_depth_mm: Optional[float] = None,
    wire1_dist_from_compression_mm: Optional[float] = None,
    wire2_dist_from_compression_mm: Optional[float] = None,
    wire1_to_wire2_spacing_mm: Optional[float] = None,
    wire2_on_hook: Optional[bool] = None,
    bend_diameter_mm: Optional[float] = None,
    tie_wire_diameter_mm: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate the welded-wire U-tie leg anchorage (BG-TRANS-WIRE-TIE-UTIE-001).

    Verified source: Mabhas 9 (1399), Clause 9-21-6-1-4, PDF p. 464 /
    Printed p. 444 (Figure 9-21-1, PDF p. 465): the anchorage of one leg of
    a welded-wire-mesh U-stirrup shall satisfy one of the following.
    (الف) two longitudinal wires at 50 mm spacing in the upper part of the
    U-stirrup. (ب) one longitudinal wire less than one-quarter of the
    effective depth from the compression face, and a second longitudinal
    wire closer to the compression face than the first and more than 50 mm
    from the first, where the second wire may be on the stirrup leg or on a
    hook with a minimum bend diameter of eight times the stirrup wire
    diameter. Only these numeric conditions are represented; no geometry is
    inferred from Figure 9-21-1 and no spacing/anchorage/bend requirement is
    invented. The caller selects which alternative (الف/ب) is relied upon.

    ``alternative`` and the selected alternative's geometry are REQUIRED
    typed inputs (never assumed). Missing/invalid -> BLOCKED/INVALID_INPUT.
    """
    rule_id = RULE_BG_TRANS_WIRE_TIE_UTIE_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "alternative": alternative.value if isinstance(alternative, WireTieUtieAlternative) else alternative,
        "wire_spacing_mm": wire_spacing_mm,
        "wires_in_upper_part_of_utie": wires_in_upper_part_of_utie,
        "effective_depth_mm": effective_depth_mm,
        "wire1_dist_from_compression_mm": wire1_dist_from_compression_mm,
        "wire2_dist_from_compression_mm": wire2_dist_from_compression_mm,
        "wire1_to_wire2_spacing_mm": wire1_to_wire2_spacing_mm,
        "wire2_on_hook": wire2_on_hook,
        "bend_diameter_mm": bend_diameter_mm,
        "tie_wire_diameter_mm": tie_wire_diameter_mm,
    }

    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")
    rule = gate.rule

    alternative_raw: object = alternative
    if alternative_raw is None:
        return _blocked_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _missing_input_diagnostic(
                    "MISSING_ALTERNATIVE",
                    (
                        "The Clause 9-21-6-1-4 alternative relied upon (الف or "
                        "ب) is required; it is never assumed. Missing required "
                        "input -> BLOCKED."
                    ),
                    rule=rule,
                    field_name="alternative",
                )
            ],
        )
    if not isinstance(alternative_raw, WireTieUtieAlternative):
        return _invalid_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                EngineeringDiagnostic(
                    code="INVALID_ALTERNATIVE",
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        "alternative must be a WireTieUtieAlternative value, "
                        f"got {alternative_raw!r}."
                    ),
                    rule_id=rule_id,
                    field_name="alternative",
                )
            ],
        )

    if alternative_raw is WireTieUtieAlternative.ALEF:
        return _evaluate_wire_tie_utie_alef(
            gate,
            rule=rule,
            raw_inputs=raw_inputs,
            wire_spacing_mm=wire_spacing_mm,
            wires_in_upper_part_of_utie=wires_in_upper_part_of_utie,
        )
    return _evaluate_wire_tie_utie_be(
        gate,
        rule=rule,
        raw_inputs=raw_inputs,
        effective_depth_mm=effective_depth_mm,
        wire1_dist_from_compression_mm=wire1_dist_from_compression_mm,
        wire2_dist_from_compression_mm=wire2_dist_from_compression_mm,
        wire1_to_wire2_spacing_mm=wire1_to_wire2_spacing_mm,
        wire2_on_hook=wire2_on_hook,
        bend_diameter_mm=bend_diameter_mm,
        tie_wire_diameter_mm=tie_wire_diameter_mm,
    )


def _evaluate_wire_tie_utie_alef(
    gate: GatekeeperDecision,
    *,
    rule: RuleReference,
    raw_inputs: Dict[str, ScalarInputValue],
    wire_spacing_mm: Optional[float],
    wires_in_upper_part_of_utie: Optional[bool],
) -> CalculationTraceStep:
    """Clause 9-21-6-1-4-الف: two longitudinal wires at 50 mm in the U upper part."""
    rule_id = rule.rule_id
    upper_raw: object = wires_in_upper_part_of_utie
    if upper_raw is None:
        return _blocked_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _missing_input_diagnostic(
                    "MISSING_WIRES_IN_UPPER_PART",
                    (
                        "Whether the two longitudinal wires are in the upper "
                        "part of the U-stirrup is required for Clause "
                        "9-21-6-1-4-الف; it is never assumed. Missing required "
                        "input -> BLOCKED."
                    ),
                    rule=rule,
                    field_name="wires_in_upper_part_of_utie",
                )
            ],
        )
    if not isinstance(upper_raw, bool):
        return _invalid_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                EngineeringDiagnostic(
                    code="INVALID_WIRES_IN_UPPER_PART",
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        "wires_in_upper_part_of_utie must be a bool, got "
                        f"{upper_raw!r}."
                    ),
                    rule_id=rule_id,
                    field_name="wires_in_upper_part_of_utie",
                )
            ],
        )

    invalid: List[EngineeringDiagnostic] = []
    missing: List[EngineeringDiagnostic] = []
    _require_positive(
        wire_spacing_mm,
        code="MISSING_WIRE_SPACING",
        field_name="wire_spacing_mm",
        message=(
            "The spacing between the two longitudinal wires is required for "
            "the Clause 9-21-6-1-4-الف 50 mm check; it is never assumed. "
            "Missing required input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    if invalid:
        return _invalid_step(gate, raw_inputs=raw_inputs, diagnostics=invalid)
    if missing:
        return _blocked_step(gate, raw_inputs=raw_inputs, diagnostics=missing)
    assert wire_spacing_mm is not None

    if not upper_raw:
        diag = EngineeringDiagnostic(
            code="WIRE_TIE_UTIE_ALEF_NOT_IN_UPPER_PART",
            severity=DiagnosticSeverity.ERROR,
            message=(
                "FAIL: Clause 9-21-6-1-4-الف requires the two longitudinal "
                "wires to be in the upper part of the U-stirrup; the provided "
                "wires are not."
            ),
            rule_id=rule_id,
            field_name="wires_in_upper_part_of_utie",
        )
        return _fail_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates={},
            final_result=None,
            unit="mm",
            diagnostic=diag,
        )

    if wire_spacing_mm != BG_TRANS_WIRE_TIE_UTIE_ALEF_SPACING_MM:
        diag = EngineeringDiagnostic(
            code="WIRE_TIE_UTIE_ALEF_SPACING_NOT_50MM",
            severity=DiagnosticSeverity.ERROR,
            message=(
                f"FAIL: Clause 9-21-6-1-4-الف requires two longitudinal wires "
                f"at 50 mm spacing; the provided spacing "
                f"{wire_spacing_mm} mm is not 50 mm."
            ),
            rule_id=rule_id,
            field_name="wire_spacing_mm",
        )
        return _fail_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates={
                "wire_spacing_mm": wire_spacing_mm,
                "required_spacing_mm": BG_TRANS_WIRE_TIE_UTIE_ALEF_SPACING_MM,
            },
            final_result=wire_spacing_mm,
            unit="mm",
            diagnostic=diag,
        )

    return _pass_step(
        gate,
        raw_inputs=raw_inputs,
        intermediates={
            "wire_spacing_mm": wire_spacing_mm,
            "required_spacing_mm": BG_TRANS_WIRE_TIE_UTIE_ALEF_SPACING_MM,
        },
        final_result=wire_spacing_mm,
        unit="mm",
        message=(
            "PASS: Clause 9-21-6-1-4-الف — two longitudinal wires at 50 mm "
            "spacing in the upper part of the U-stirrup."
        ),
    )


def _evaluate_wire_tie_utie_be(
    gate: GatekeeperDecision,
    *,
    rule: RuleReference,
    raw_inputs: Dict[str, ScalarInputValue],
    effective_depth_mm: Optional[float],
    wire1_dist_from_compression_mm: Optional[float],
    wire2_dist_from_compression_mm: Optional[float],
    wire1_to_wire2_spacing_mm: Optional[float],
    wire2_on_hook: Optional[bool],
    bend_diameter_mm: Optional[float],
    tie_wire_diameter_mm: Optional[float],
) -> CalculationTraceStep:
    """Clause 9-21-6-1-4-ب: quarter-depth wire + closer second wire > 50 mm
    away, on leg or hook with bend dia >= 8x tie wire dia."""
    rule_id = rule.rule_id
    on_hook_raw: object = wire2_on_hook
    if on_hook_raw is None:
        return _blocked_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _missing_input_diagnostic(
                    "MISSING_WIRE2_ON_HOOK",
                    (
                        "Whether the second wire is on the stirrup leg or on a "
                        "hook is required for Clause 9-21-6-1-4-ب (it selects "
                        "whether the 8x bend-diameter condition applies); it "
                        "is never assumed. Missing required input -> BLOCKED."
                    ),
                    rule=rule,
                    field_name="wire2_on_hook",
                )
            ],
        )
    if not isinstance(on_hook_raw, bool):
        return _invalid_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                EngineeringDiagnostic(
                    code="INVALID_WIRE2_ON_HOOK",
                    severity=DiagnosticSeverity.ERROR,
                    message=f"wire2_on_hook must be a bool, got {on_hook_raw!r}.",
                    rule_id=rule_id,
                    field_name="wire2_on_hook",
                )
            ],
        )

    invalid: List[EngineeringDiagnostic] = []
    missing: List[EngineeringDiagnostic] = []
    _require_positive(
        effective_depth_mm,
        code="MISSING_EFFECTIVE_DEPTH",
        field_name="effective_depth_mm",
        message=(
            "The effective depth is required for the Clause 9-21-6-1-4-ب "
            "one-quarter-depth condition; it is never assumed. Missing "
            "required input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    _require_positive(
        wire1_dist_from_compression_mm,
        code="MISSING_WIRE1_DIST",
        field_name="wire1_dist_from_compression_mm",
        message=(
            "The first wire distance from the compression face is required "
            "for the Clause 9-21-6-1-4-ب one-quarter-depth condition; it is "
            "never assumed. Missing required input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    _require_positive(
        wire2_dist_from_compression_mm,
        code="MISSING_WIRE2_DIST",
        field_name="wire2_dist_from_compression_mm",
        message=(
            "The second wire distance from the compression face is required "
            "for the Clause 9-21-6-1-4-ب closer-to-compression condition; it "
            "is never assumed. Missing required input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    _require_positive(
        wire1_to_wire2_spacing_mm,
        code="MISSING_WIRE1_TO_WIRE2_SPACING",
        field_name="wire1_to_wire2_spacing_mm",
        message=(
            "The spacing between the first and second wires is required for "
            "the Clause 9-21-6-1-4-ب more-than-50 mm condition; it is never "
            "assumed. Missing required input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    if on_hook_raw:
        _require_positive(
            bend_diameter_mm,
            code="MISSING_BEND_DIAMETER",
            field_name="bend_diameter_mm",
            message=(
                "The bend diameter is required for the Clause 9-21-6-1-4-ب "
                "8x-tie-wire-diameter condition when the second wire is on a "
                "hook; it is never assumed. Missing required input -> BLOCKED."
            ),
            rule=rule,
            missing=missing,
            invalid=invalid,
        )
        _require_positive(
            tie_wire_diameter_mm,
            code="MISSING_TIE_WIRE_DIAMETER",
            field_name="tie_wire_diameter_mm",
            message=(
                "The tie/stirrup wire diameter is required for the Clause "
                "9-21-6-1-4-ب 8x-tie-wire-diameter condition when the second "
                "wire is on a hook; it is never assumed. Missing required "
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
    assert effective_depth_mm is not None
    assert wire1_dist_from_compression_mm is not None
    assert wire2_dist_from_compression_mm is not None
    assert wire1_to_wire2_spacing_mm is not None

    quarter_depth_mm = (
        BG_TRANS_WIRE_TIE_UTIE_BE_QUARTER_DEPTH * effective_depth_mm
    )

    if wire1_dist_from_compression_mm >= quarter_depth_mm:
        diag = EngineeringDiagnostic(
            code="WIRE_TIE_UTIE_BE_WIRE1_NOT_WITHIN_QUARTER_DEPTH",
            severity=DiagnosticSeverity.ERROR,
            message=(
                "FAIL: Clause 9-21-6-1-4-ب requires the first longitudinal "
                f"wire to be less than one-quarter of the effective depth "
                f"(< {quarter_depth_mm} mm) from the compression face; the "
                f"provided distance {wire1_dist_from_compression_mm} mm does "
                "not satisfy this."
            ),
            rule_id=rule_id,
            field_name="wire1_dist_from_compression_mm",
        )
        return _fail_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates={
                "wire1_dist_from_compression_mm": wire1_dist_from_compression_mm,
                "quarter_effective_depth_mm": quarter_depth_mm,
            },
            final_result=wire1_dist_from_compression_mm,
            unit="mm",
            diagnostic=diag,
        )

    if wire2_dist_from_compression_mm >= wire1_dist_from_compression_mm:
        diag = EngineeringDiagnostic(
            code="WIRE_TIE_UTIE_BE_WIRE2_NOT_CLOSER_TO_COMPRESSION",
            severity=DiagnosticSeverity.ERROR,
            message=(
                "FAIL: Clause 9-21-6-1-4-ب requires the second longitudinal "
                "wire to be closer to the compression face than the first; "
                f"the provided wire2 distance {wire2_dist_from_compression_mm} "
                f"mm is not less than the wire1 distance "
                f"{wire1_dist_from_compression_mm} mm."
            ),
            rule_id=rule_id,
            field_name="wire2_dist_from_compression_mm",
        )
        return _fail_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates={
                "wire1_dist_from_compression_mm": wire1_dist_from_compression_mm,
                "wire2_dist_from_compression_mm": wire2_dist_from_compression_mm,
            },
            final_result=wire2_dist_from_compression_mm,
            unit="mm",
            diagnostic=diag,
        )

    if wire1_to_wire2_spacing_mm <= BG_TRANS_WIRE_TIE_UTIE_BE_MIN_SPACING_MM:
        diag = EngineeringDiagnostic(
            code="WIRE_TIE_UTIE_BE_SPACING_NOT_ABOVE_50MM",
            severity=DiagnosticSeverity.ERROR,
            message=(
                "FAIL: Clause 9-21-6-1-4-ب requires the second wire to be "
                f"more than 50 mm from the first; the provided spacing "
                f"{wire1_to_wire2_spacing_mm} mm is not greater than 50 mm."
            ),
            rule_id=rule_id,
            field_name="wire1_to_wire2_spacing_mm",
        )
        return _fail_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates={
                "wire1_to_wire2_spacing_mm": wire1_to_wire2_spacing_mm,
                "min_spacing_mm": BG_TRANS_WIRE_TIE_UTIE_BE_MIN_SPACING_MM,
            },
            final_result=wire1_to_wire2_spacing_mm,
            unit="mm",
            diagnostic=diag,
        )

    if on_hook_raw:
        assert bend_diameter_mm is not None
        assert tie_wire_diameter_mm is not None
        min_bend_dia_mm = (
            BG_TRANS_WIRE_TIE_UTIE_BE_BEND_DIA_FACTOR * tie_wire_diameter_mm
        )
        if bend_diameter_mm < min_bend_dia_mm:
            diag = EngineeringDiagnostic(
                code="WIRE_TIE_UTIE_BE_BEND_DIA_BELOW_8X",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    "FAIL: when the second wire is on a hook, Clause "
                    "9-21-6-1-4-ب requires a minimum bend diameter of eight "
                    f"times the tie wire diameter (>= {min_bend_dia_mm} mm); "
                    f"the provided bend diameter {bend_diameter_mm} mm is "
                    "insufficient."
                ),
                rule_id=rule_id,
                field_name="bend_diameter_mm",
            )
            return _fail_step(
                gate,
                raw_inputs=raw_inputs,
                intermediates={
                    "bend_diameter_mm": bend_diameter_mm,
                    "min_bend_diameter_mm": min_bend_dia_mm,
                    "tie_wire_diameter_mm": tie_wire_diameter_mm,
                },
                final_result=bend_diameter_mm,
                unit="mm",
                diagnostic=diag,
            )

    return _pass_step(
        gate,
        raw_inputs=raw_inputs,
        intermediates={
            "quarter_effective_depth_mm": quarter_depth_mm,
            "wire1_dist_from_compression_mm": wire1_dist_from_compression_mm,
            "wire2_dist_from_compression_mm": wire2_dist_from_compression_mm,
            "wire1_to_wire2_spacing_mm": wire1_to_wire2_spacing_mm,
        },
        final_result=wire1_to_wire2_spacing_mm,
        unit="mm",
        message=(
            "PASS: Clause 9-21-6-1-4-ب — first wire within one-quarter of "
            "the effective depth from the compression face, second wire "
            "closer to the compression face and more than 50 mm from the "
            "first"
            + (
                ", with bend diameter >= 8x tie wire diameter."
                if on_hook_raw
                else ", on the stirrup leg."
            )
        ),
    )


# --- BG-TRANS-SPIRAL-SPLICE-LAP-SEL-001 (Clause 9-21-6-3-5-ب, PDF pp. 468-469)
def evaluate_spiral_splice_lap_sel(
    *,
    yield_stress_mpa: Optional[float] = None,
    splice_bar_type: Optional[SpiralSpliceBarType] = None,
    coating_class: Optional[SpiralSpliceCoating] = None,
    end_condition: Optional[SpiralSpliceEndCondition] = None,
    bar_diameter_mm: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate the spiral lap-splice method selection
    (BG-TRANS-SPIRAL-SPLICE-LAP-SEL-001).

    Verified source: Mabhas 9 (1399), Clause 9-21-6-3-5(ب), PDF pp. 468-469 /
    Printed pp. 448-449: a spiral lap splice per Clause 9-21-6-3-6 is
    permitted for bars with yield stress f_y <= 420 MPa. The lap LENGTH is
    delegated to the executable BG-TRANS-SPIRAL-LAP-001 (Clause 9-21-6-3-6 /
    Table 9-21-7: max(k*d_b, 300 mm)) and is NOT recomputed here. f_y > 420
    MPa is not covered by the lap route and is deterministically BLOCKED (the
    only other route, welded/mechanical splice per Clause 9-21-4-7, is
    BLOCKED via National Building Regulations Chapter 10). The
    welded/mechanical route of Clause 9-21-6-3-5(الف) is NOT implemented.

    yield_stress_mpa and the Table 9-21-7 selection inputs are REQUIRED typed
    inputs (never assumed). Missing/invalid -> BLOCKED/INVALID_INPUT.
    """
    rule_id = RULE_BG_TRANS_SPIRAL_SPLICE_LAP_SEL_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "yield_stress_mpa": yield_stress_mpa,
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

    invalid: List[EngineeringDiagnostic] = []
    missing: List[EngineeringDiagnostic] = []
    _require_positive(
        yield_stress_mpa,
        code="MISSING_YIELD_STRESS",
        field_name="yield_stress_mpa",
        message=(
            "The bar yield stress f_y is required to confirm the Clause "
            "9-21-6-3-5-ب lap-splice route (f_y <= 420 MPa); it is never "
            "assumed. Missing required input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    if invalid:
        return _invalid_step(gate, raw_inputs=raw_inputs, diagnostics=invalid)
    if missing:
        return _blocked_step(gate, raw_inputs=raw_inputs, diagnostics=missing)
    assert yield_stress_mpa is not None

    if yield_stress_mpa > BG_TRANS_SPIRAL_SPLICE_LAP_MAX_FY_MPA:
        return _blocked_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _missing_input_diagnostic(
                    "SPIRAL_SPLICE_LAP_FY_ABOVE_420",
                    (
                        f"BLOCKED: f_y = {yield_stress_mpa} MPa exceeds the "
                        "420 MPa limit of the Clause 9-21-6-3-5-ب lap-splice "
                        "route; the only other spiral-splice route (welded / "
                        "mechanical per Clause 9-21-6-3-5-الف -> 9-21-4-7) is "
                        "BLOCKED via National Building Regulations Chapter 10. "
                        "No lap route is available for this f_y."
                    ),
                    rule=rule,
                    field_name="yield_stress_mpa",
                )
            ],
        )

    # Delegate the actual lap length to the verified spiral-lap rule
    # (Clause 9-21-6-3-6 / Table 9-21-7) instead of duplicating its table.
    lap_step = evaluate_spiral_lap_splice(
        splice_bar_type=splice_bar_type,
        coating_class=coating_class,
        end_condition=end_condition,
        bar_diameter_mm=bar_diameter_mm,
        jurisdiction_mode=jurisdiction_mode,
    )
    if lap_step.outcome is EvaluationOutcome.COMPUTED:
        lap_mm = lap_step.final_result
        assert lap_mm is not None
        return _computed_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates={
                "yield_stress_mpa": yield_stress_mpa,
                "max_lap_route_fy_mpa": BG_TRANS_SPIRAL_SPLICE_LAP_MAX_FY_MPA,
                "spiral_lap_length_mm": lap_mm,
            },
            final_result=lap_mm,
            unit="mm",
            message=(
                f"Spiral lap-splice route selected (f_y = {yield_stress_mpa} "
                f"MPa <= {BG_TRANS_SPIRAL_SPLICE_LAP_MAX_FY_MPA} MPa); lap "
                f"length per Clause 9-21-6-3-6 / Table 9-21-7 = {lap_mm} mm "
                "(delegated to BG-TRANS-SPIRAL-LAP-001)."
            ),
        )
    if lap_step.outcome is EvaluationOutcome.FAIL:
        diag = EngineeringDiagnostic(
            code="SPIRAL_SPLICE_LAP_DELEGATED_FAILURE",
            severity=DiagnosticSeverity.ERROR,
            message=(
                "FAIL: the delegated spiral lap-length evaluation failed; "
                f"{lap_step.message}"
            ),
            rule_id=rule_id,
            field_name="splice_bar_type",
        )
        return _fail_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates={},
            final_result=None,
            unit="mm",
            diagnostic=diag,
        )
    if lap_step.outcome is EvaluationOutcome.INVALID_INPUT:
        return _invalid_step(
            gate, raw_inputs=raw_inputs, diagnostics=list(lap_step.diagnostics)
        )
    return _blocked_step(
        gate, raw_inputs=raw_inputs, diagnostics=list(lap_step.diagnostics)
    )


# --- BG-TRANS-TIE-ANCHOR-STD-HOOK-001 (Clause 9-21-6-1-3-الف, PDF p. 463 /
# Printed p. 443)
def evaluate_tie_anchor_std_hook(
    *,
    yield_stress_mpa: Optional[float] = None,
    bar_diameter_mm: Optional[float] = None,
    hook_angle_deg: Optional[float] = None,
    inner_bend_diameter_mm: Optional[float] = None,
    straight_extension_mm: Optional[float] = None,
    encloses_longitudinal_bar: Optional[bool] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate the tie deformed-bar standard-hook anchorage
    (BG-TRANS-TIE-ANCHOR-STD-HOOK-001).

    Verified source: Mabhas 9 (1399), Clause 9-21-6-1-3(الف), PDF p. 463 /
    Printed p. 443: «در میلگردها یا سیم‌های با قطر کوچکتر یا مساوی ۱۶
    میلی‌متر، و برای میلگردهای با قطر ۱۸ تا ۲۵ میلی‌متر با تنش تسلیم کمتر از
    ۲۸۰ مگاپاسکال، وجود قلاب استاندارد پیرامون میلگرد طولی.» Read verbatim
    from the JPG, the f_y < 280 MPa condition attaches to the 18-25 mm
    sub-condition only, so the executable applicability of branch (الف) is
    d_b <= 16 mm (any f_y) OR d_b 18-25 mm with f_y < 280 MPa.

    Clause 9-21-6-1-3 has three branches. Only (الف) is implemented here.
    Branch (ب) (d_b 18-25 mm with f_y > 280 MPa: standard hook plus an
    embedment length plus a minimum outer bend diameter
    0.17*f_y/(lambda*sqrt(f'c))*d_b) and branch (پ) (joists, d_b <= 12 mm)
    remain blocked under BG-TRANS-TIE-ANCHOR-PENDING. Genuine source gaps
    that are deterministically BLOCKED and never interpolated: f_y = 280 MPa
    exactly (in neither (الف) nor (ب)), d_b = 17 mm (gap between the printed
    <= 16 mm and 18-25 mm sub-conditions), d_b > 25 mm (assigned to neither
    branch), and d_b 18-25 mm with f_y >= 280 MPa (belongs to branch (ب)).

    Clause 9-21-6-1-3(الف) requires a «standard hook» without naming a unique
    angle, so the hook angle is a caller-supplied typed input that is
    validated through BG-TRANS-STANDARD-HOOK-001 (Clause 9-21-2-2-2 / Table
    9-21-2) — no angle is silently chosen and no hook geometry is duplicated
    here. Missing hook geometry -> BLOCKED.

    yield_stress_mpa, bar_diameter_mm, hook_angle_deg,
    inner_bend_diameter_mm, straight_extension_mm and
    encloses_longitudinal_bar are REQUIRED typed inputs (never assumed).
    Missing/invalid inputs -> BLOCKED/INVALID_INPUT, never PASS.
    """
    rule_id = RULE_BG_TRANS_TIE_ANCHOR_STD_HOOK_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "yield_stress_mpa": yield_stress_mpa,
        "bar_diameter_mm": bar_diameter_mm,
        "hook_angle_deg": hook_angle_deg,
        "inner_bend_diameter_mm": inner_bend_diameter_mm,
        "straight_extension_mm": straight_extension_mm,
        "encloses_longitudinal_bar": encloses_longitudinal_bar,
    }

    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")
    rule = gate.rule

    encloses_raw: object = encloses_longitudinal_bar
    if encloses_raw is None:
        return _blocked_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _missing_input_diagnostic(
                    "MISSING_ENCLOSES_LONGITUDINAL_BAR",
                    (
                        "Whether the standard hook encloses a longitudinal bar "
                        "is required by Clause 9-21-6-1-3-الف; it is never "
                        "assumed. Missing required input -> BLOCKED."
                    ),
                    rule=rule,
                    field_name="encloses_longitudinal_bar",
                )
            ],
        )
    if not isinstance(encloses_raw, bool):
        return _invalid_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                EngineeringDiagnostic(
                    code="INVALID_ENCLOSES_LONGITUDINAL_BAR",
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        "encloses_longitudinal_bar must be a bool, got "
                        f"{encloses_raw!r}."
                    ),
                    rule_id=rule_id,
                    field_name="encloses_longitudinal_bar",
                )
            ],
        )

    invalid: List[EngineeringDiagnostic] = []
    missing: List[EngineeringDiagnostic] = []
    _require_positive(
        yield_stress_mpa,
        code="MISSING_YIELD_STRESS",
        field_name="yield_stress_mpa",
        message=(
            "The bar yield stress f_y is a required typed input for the "
            "Clause 9-21-6-1-3-الف applicability test; it is never assumed. "
            "Missing required input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    _require_positive(
        bar_diameter_mm,
        code="MISSING_BAR_DIAMETER",
        field_name="bar_diameter_mm",
        message=(
            "The bar diameter d_b is required to select the Clause "
            "9-21-6-1-3-الف sub-condition and the Table 9-21-2 diameter row; "
            "it is never assumed. Missing required input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    _require_positive(
        hook_angle_deg,
        code="MISSING_HOOK_ANGLE",
        field_name="hook_angle_deg",
        message=(
            "The standard-hook angle is required to select the Table 9-21-2 "
            "row; Clause 9-21-6-1-3-الف names no unique angle, so it is "
            "supplied by the caller and never assumed. Missing required "
            "input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    _require_positive(
        inner_bend_diameter_mm,
        code="MISSING_INNER_BEND_DIAMETER",
        field_name="inner_bend_diameter_mm",
        message=(
            "The inner bend diameter is required for the Table 9-21-2 "
            "standard-hook check; it is never assumed. Missing required "
            "input -> BLOCKED."
        ),
        rule=rule,
        missing=missing,
        invalid=invalid,
    )
    _require_positive(
        straight_extension_mm,
        code="MISSING_STRAIGHT_EXTENSION",
        field_name="straight_extension_mm",
        message=(
            "The straight extension after the bend is required for the Table "
            "9-21-2 standard-hook check; it is never assumed. Missing "
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
    assert yield_stress_mpa is not None
    assert bar_diameter_mm is not None
    assert hook_angle_deg is not None
    assert inner_bend_diameter_mm is not None
    assert straight_extension_mm is not None

    # --- Clause 9-21-6-1-3-الف applicability (read verbatim from the JPG).
    # The f_y < 280 MPa condition attaches to the 18-25 mm sub-condition
    # only, so d_b <= 16 mm carries no f_y gate. d_b > 25 mm and the
    # 16 < d_b < 18 gap are assigned to neither sub-condition.
    if bar_diameter_mm > BG_TRANS_TIE_ANCHOR_DB_LARGE_MAX_MM:
        return _blocked_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _missing_input_diagnostic(
                    "TIE_ANCHOR_DB_ABOVE_TABLE",
                    (
                        f"BLOCKED: d_b = {bar_diameter_mm} mm is above the "
                        "largest diameter range (18-25 mm) printed in Clause "
                        "9-21-6-1-3; the range is never extrapolated and the "
                        "bar is assigned to neither branch."
                    ),
                    rule=rule,
                    field_name="bar_diameter_mm",
                )
            ],
        )
    if (
        BG_TRANS_TIE_ANCHOR_DB_SMALL_MAX_MM
        < bar_diameter_mm
        < BG_TRANS_TIE_ANCHOR_DB_LARGE_MIN_MM
    ):
        return _blocked_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _missing_input_diagnostic(
                    "TIE_ANCHOR_DB_IN_GAP",
                    (
                        f"BLOCKED: d_b = {bar_diameter_mm} mm falls in the gap "
                        "between the printed '<= 16 mm' and '18-25 mm' "
                        "sub-conditions of Clause 9-21-6-1-3 (no 17 mm value "
                        "is printed); the gap is never interpolated."
                    ),
                    rule=rule,
                    field_name="bar_diameter_mm",
                )
            ],
        )
    if bar_diameter_mm <= BG_TRANS_TIE_ANCHOR_DB_SMALL_MAX_MM:
        alef_subcondition = "d_b <= 16 mm"
    elif yield_stress_mpa < BG_TRANS_TIE_ANCHOR_FY_LIMIT_MPA:
        alef_subcondition = "d_b 18-25 mm and f_y < 280 MPa"
    elif yield_stress_mpa == BG_TRANS_TIE_ANCHOR_FY_LIMIT_MPA:
        return _blocked_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _missing_input_diagnostic(
                    "TIE_ANCHOR_FY_280_IN_GAP",
                    (
                        f"BLOCKED: f_y = {yield_stress_mpa} MPa is exactly the "
                        "280 MPa boundary printed in Clause 9-21-6-1-3. "
                        "Branch (الف) uses f_y < 280 MPa and branch (ب) uses "
                        "f_y > 280 MPa, so f_y = 280 MPa is in neither; the "
                        "boundary is never interpolated."
                    ),
                    rule=rule,
                    field_name="yield_stress_mpa",
                )
            ],
        )
    else:
        return _blocked_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _missing_input_diagnostic(
                    "TIE_ANCHOR_FY_ABOVE_280_B_BRANCH_NOT_IMPLEMENTED",
                    (
                        f"BLOCKED: d_b = {bar_diameter_mm} mm with "
                        f"f_y = {yield_stress_mpa} MPa belongs to Clause "
                        "9-21-6-1-3(ب), which additionally requires an "
                        "embedment length and a minimum outer bend diameter "
                        "0.17*f_y/(lambda*sqrt(f'c))*d_b. Branch (ب) is not "
                        "implemented (kept blocked under "
                        "BG-TRANS-TIE-ANCHOR-PENDING); no outside-code value "
                        "is substituted."
                    ),
                    rule=rule,
                    field_name="yield_stress_mpa",
                )
            ],
        )

    # Delegate the standard-hook geometry to the verified standard-hook rule
    # (Clause 9-21-2-2-2 / Table 9-21-2) instead of duplicating its table.
    # The angle is caller-supplied because Clause 9-21-6-1-3-الف names no
    # unique angle.
    hook_step = evaluate_standard_hook(
        hook_angle_deg=hook_angle_deg,
        bar_diameter_mm=bar_diameter_mm,
        inner_bend_diameter_mm=inner_bend_diameter_mm,
        straight_extension_mm=straight_extension_mm,
        encloses_longitudinal_bar=encloses_raw,
        jurisdiction_mode=jurisdiction_mode,
    )
    if hook_step.outcome is EvaluationOutcome.PASS:
        return _pass_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates={
                "yield_stress_mpa": yield_stress_mpa,
                "bar_diameter_mm": bar_diameter_mm,
                "hook_angle_deg": hook_angle_deg,
                "inner_bend_diameter_mm": inner_bend_diameter_mm,
                "straight_extension_mm": straight_extension_mm,
            },
            final_result=straight_extension_mm,
            unit="mm",
            message=(
                f"PASS: Clause 9-21-6-1-3-الف applicability ({alef_subcondition}) "
                f"is satisfied and the anchorage is a standard "
                f"{hook_angle_deg}-degree hook per Table 9-21-2 enclosing the "
                "longitudinal bar."
            ),
        )
    if hook_step.outcome is EvaluationOutcome.FAIL:
        diag = EngineeringDiagnostic(
            code="TIE_ANCHOR_STANDARD_HOOK_GEOMETRY_NOT_SATISFIED",
            severity=DiagnosticSeverity.ERROR,
            message=(
                "FAIL: the tie-anchor standard hook must satisfy the "
                "standard-hook geometry of Clause 9-21-2-2-2 / Table 9-21-2; "
                f"{hook_step.message}"
            ),
            rule_id=rule_id,
            field_name="inner_bend_diameter_mm",
        )
        return _fail_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates={},
            final_result=None,
            unit="mm",
            diagnostic=diag,
        )
    if hook_step.outcome is EvaluationOutcome.INVALID_INPUT:
        return _invalid_step(
            gate, raw_inputs=raw_inputs, diagnostics=list(hook_step.diagnostics)
        )
    return _blocked_step(
        gate, raw_inputs=raw_inputs, diagnostics=list(hook_step.diagnostics)
    )


# --- BG-TRANS-TORSION-TIE-WIRE-ROUTE-001 (Clause 9-21-6-1-6-ب / 9-21-6-2-7-ب
# via Clause 9-21-6-1-4, PDF pp. 464 & 468 / Printed pp. 444 & 448)
def evaluate_torsion_tie_wire_route(
    *,
    concrete_around_anchorage_not_liable_to_spall: Optional[bool] = None,
    alternative: Optional[WireTieUtieAlternative] = None,
    wire_spacing_mm: Optional[float] = None,
    wires_in_upper_part_of_utie: Optional[bool] = None,
    effective_depth_mm: Optional[float] = None,
    wire1_dist_from_compression_mm: Optional[float] = None,
    wire2_dist_from_compression_mm: Optional[float] = None,
    wire1_to_wire2_spacing_mm: Optional[float] = None,
    wire2_on_hook: Optional[bool] = None,
    bend_diameter_mm: Optional[float] = None,
    tie_wire_diameter_mm: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate the torsion/integrity-tie welded-wire route
    (BG-TRANS-TORSION-TIE-WIRE-ROUTE-001).

    Verified source: Mabhas 9 (1399). Clause 9-21-6-1-6-ب (PDF p. 464 /
    Printed p. 444) and Clause 9-21-6-2-7-ب (PDF p. 468 / Printed p. 448):
    «در مواردی که بتن پیرامون مهار به دلیل وجود [پال|بال] یا دال مستعد
    متلاشی شدن نیست، [باید] الزامات بندهای ۹-۲۱-۶-۱-۳-الف یا ب، یا
    ۹-۲۱-۶-۱-۴ تامین گردد.» Both clauses state the same precondition (the
    concrete around the anchorage is not susceptible to deterioration from a
    flange/dal) followed by an OR of two routes: Clause 9-21-6-1-3-الف/ب OR
    Clause 9-21-6-1-4.

    This rule implements ONLY the Clause 9-21-6-1-4 route. The U-tie
    anchorage geometry is delegated to BG-TRANS-WIRE-TIE-UTIE-001 and is not
    duplicated. The Clause 9-21-6-1-3 route remains blocked (it carries the
    f_y = 280 MPa / d_b = 17 mm / d_b > 25 mm boundary gap), and the (ب)
    clauses as a whole stay blocked under BG-TRANS-TORSION-TIE-PENDING —
    implementing one OR route does NOT make the whole clause executable.

    ``concrete_around_anchorage_not_liable_to_spall`` is the route
    precondition typed input (never assumed); if it is False the (ب) route is
    not available and this rule is NOT_APPLICABLE. ``alternative`` and the
    selected alternative's geometry are REQUIRED typed inputs. Missing route
    data -> BLOCKED; malformed -> INVALID_INPUT; a violated U-tie condition is
    re-raised with the delegate's own semantics.
    """
    rule_id = RULE_BG_TRANS_TORSION_TIE_WIRE_ROUTE_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "concrete_around_anchorage_not_liable_to_spall": (
            concrete_around_anchorage_not_liable_to_spall
        ),
        "alternative": (
            alternative.value if isinstance(alternative, WireTieUtieAlternative)
            else alternative
        ),
        "wire_spacing_mm": wire_spacing_mm,
        "wires_in_upper_part_of_utie": wires_in_upper_part_of_utie,
        "effective_depth_mm": effective_depth_mm,
        "wire1_dist_from_compression_mm": wire1_dist_from_compression_mm,
        "wire2_dist_from_compression_mm": wire2_dist_from_compression_mm,
        "wire1_to_wire2_spacing_mm": wire1_to_wire2_spacing_mm,
        "wire2_on_hook": wire2_on_hook,
        "bend_diameter_mm": bend_diameter_mm,
        "tie_wire_diameter_mm": tie_wire_diameter_mm,
    }

    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")
    rule = gate.rule

    spall_raw: object = concrete_around_anchorage_not_liable_to_spall
    if spall_raw is None:
        return _blocked_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _missing_input_diagnostic(
                    "MISSING_CONCRETE_NOT_LIABLE_TO_SPALL",
                    (
                        "Whether the concrete around the anchorage is "
                        "susceptible to deterioration from a flange/dal is the "
                        "precondition of the Clause 9-21-6-1-6-ب / "
                        "9-21-6-2-7-ب routes; it is never assumed. Missing "
                        "required input -> BLOCKED."
                    ),
                    rule=rule,
                    field_name="concrete_around_anchorage_not_liable_to_spall",
                )
            ],
        )
    if not isinstance(spall_raw, bool):
        return _invalid_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                EngineeringDiagnostic(
                    code="INVALID_CONCRETE_NOT_LIABLE_TO_SPALL",
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        "concrete_around_anchorage_not_liable_to_spall must be "
                        f"a bool, got {spall_raw!r}."
                    ),
                    rule_id=rule_id,
                    field_name="concrete_around_anchorage_not_liable_to_spall",
                )
            ],
        )
    if not spall_raw:
        return _not_applicable_step(
            gate,
            raw_inputs=raw_inputs,
            unit="mm",
            message=(
                "NOT_APPLICABLE: the concrete around the anchorage IS liable "
                "to deteriorate from a flange/dal, so the Clause "
                "9-21-6-1-6-ب / 9-21-6-2-7-ب routes are not available; the tie "
                "must be anchored by the Clause 9-21-6-1-6-الف / 9-21-6-2-7-الف "
                "routes instead."
            ),
        )

    # Delegate the welded-wire U-tie anchorage geometry to the verified
    # Clause 9-21-6-1-4 rule instead of duplicating it.
    wire_step = evaluate_wire_tie_utie(
        alternative=alternative,
        wire_spacing_mm=wire_spacing_mm,
        wires_in_upper_part_of_utie=wires_in_upper_part_of_utie,
        effective_depth_mm=effective_depth_mm,
        wire1_dist_from_compression_mm=wire1_dist_from_compression_mm,
        wire2_dist_from_compression_mm=wire2_dist_from_compression_mm,
        wire1_to_wire2_spacing_mm=wire1_to_wire2_spacing_mm,
        wire2_on_hook=wire2_on_hook,
        bend_diameter_mm=bend_diameter_mm,
        tie_wire_diameter_mm=tie_wire_diameter_mm,
        jurisdiction_mode=jurisdiction_mode,
    )
    if wire_step.outcome is EvaluationOutcome.PASS:
        return _pass_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates={},
            final_result=None,
            unit="mm",
            message=(
                "PASS: the surrounding concrete is not liable to deteriorate "
                "from a flange/dal and the Clause 9-21-6-1-4 welded-wire "
                "U-tie anchorage route is satisfied, so the Clause "
                "9-21-6-1-6-ب / 9-21-6-2-7-ب anchorage obligation is met via "
                "this OR route. The Clause 9-21-6-1-3 route is NOT evaluated "
                "and stays blocked."
            ),
        )
    if wire_step.outcome is EvaluationOutcome.FAIL:
        diag = EngineeringDiagnostic(
            code="TORSION_TIE_WIRE_ROUTE_GEOMETRY_NOT_SATISFIED",
            severity=DiagnosticSeverity.ERROR,
            message=(
                "FAIL: the Clause 9-21-6-1-4 welded-wire U-tie anchorage must "
                "satisfy Clause 9-21-6-1-4; "
                f"{wire_step.message}"
            ),
            rule_id=rule_id,
            field_name="alternative",
        )
        return _fail_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates={},
            final_result=None,
            unit="mm",
            diagnostic=diag,
        )
    if wire_step.outcome is EvaluationOutcome.NOT_APPLICABLE:
        return _blocked_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=list(wire_step.diagnostics),
        )
    if wire_step.outcome is EvaluationOutcome.INVALID_INPUT:
        return _invalid_step(
            gate, raw_inputs=raw_inputs, diagnostics=list(wire_step.diagnostics)
        )
    return _blocked_step(
        gate, raw_inputs=raw_inputs, diagnostics=list(wire_step.diagnostics)
    )
