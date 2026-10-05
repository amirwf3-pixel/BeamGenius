"""Mabhas 9 (1399) Phase 2F Stage E lap-splice & bearing-splice evaluators.

Verified production rules (visually re-verified 2026-10-06 from the committed
Mabhas 9, 1399 5th ed. evidence scan ``phase2f-source-442-472`` @ ``df8067a``;
footer-confirmed Printed pp. 436-441 / PDF pp. 456-461):

- ``BG-DEV-LAP-APPLIC-001``: permitted splice methods (9-21-4-1-1) and the
  lap-splice diameter applicability limit (9-21-4-1-2),
- ``BG-DEV-LAP-SPACING-001``: contact-lap transverse centre-to-centre
  spacing <= lap/5 and <= 150 mm (9-21-4-1-4),
- ``BG-DEV-LAP-TENSION-001``: tension lap length l_st = 1.3*l_d (type B) /
  1.0*l_d (type A), min 300 mm (9-21-4-2-1),
- ``BG-DEV-LAP-TENSION-DIFFDIA-001``: different-diameter tension lap
  l_s >= max(l_d larger bar, l_st smaller bar) (9-21-4-2),
- ``BG-DEV-LAP-COMPRESSION-001``: compression lap length l_sc =
  0.071*f_y*d_b (f_y <= 420) / (0.13*f_y - 24)*d_b (f_y > 420), min 300 mm,
  d_b <= 34 mm (9-21-4-5-1),
- ``BG-DEV-LAP-COMPRESSION-DIFFDIA-001``: different-diameter compression lap
  l_s >= max(l_dc larger bar per 9-21-3-8, l_sc smaller bar per 9-21-4-5-1)
  (9-21-4-5-2),
- ``BG-DEV-SPLICE-BEARING-001``: bearing splice of compression-only bars
  (perpendicular sawn ends, coaxial, confined member; end-face deviation
  <= 5 deg, axial misalignment <= 3 deg) (9-21-4-6).

Explicitly NOT promoted (kept BLOCKED / VERIFY_PENDING, out-of-scope
dependencies or unresolved semantics — see the blocked sentinel rules
``BG-DEV-LAP-WIRE-DEFORMED-PENDING`` (9-21-4-3),
``BG-DEV-LAP-WIRE-PLAIN-PENDING`` (9-21-4-4, incl. the 9-21-4-4-1-ب «و یا»
disjunct) and ``BG-DEV-SPLICE-WELDED-MECH-PENDING`` (9-21-4-7)):

- 9-21-4-3 / 9-21-4-4 welded-wire mesh laps depend on National Building
  Regulations Chapter 9-4 welded-wire steel specifications (pages not
  delivered) and 9-21-4-4-1-ب carries an unresolved «و یا» disjunct.
- 9-21-4-7 welded/mechanical splices depend on Chapter 10 welding
  requirements (pages not delivered).

Deterministic contract of every evaluator (in order):

1. Central Gatekeeper check (``evaluate_rule_gate``) runs FIRST.
2. Missing required engineering inputs return ``UNVERIFIED_RULE_BLOCKED``
   (BLOCKED) with ``MISSING_*`` diagnostics — missing values are never
   assumed or defaulted.
3. Malformed input values (non-finite, non-positive, wrong type) return
   ``INVALID_INPUT``.
4. Verified violations return an explicit ``FAIL``; out-of-scope
   configurations return ``NOT_APPLICABLE``. BLOCKED is never converted to
   PASS.
5. Lap lengths are expressed in terms of the verified Clause 9-21-3
   development length ``l_d`` / ``l_dc``. These are NEVER computed here:
   they are caller-provided verified values (Stage C
   ``BG-DEV-LENGTH-*``), and a missing one deterministically returns
   BLOCKED (``MISSING_DEVELOPMENT_LENGTH``). No Chapter 9-4 / Chapter 10 /
  Mostofinejad dependency is imported or invented.
6. The excess-reinforcement development-length reduction of 9-21-3-9 is NOT
   applied to any lap length (9-21-4-1-5 forbids it); the caller supplies
   the already-final ``l_d``.
7. Every step attaches the registry ``RuleReference``, a
   ``CalculationTraceStep``, and explicit diagnostic codes.

Import explicitly, e.g.::

    from beamgenius.engine.development_lap_splice_mabhas9 import (
        evaluate_lap_splice_tension,
    )
"""

from __future__ import annotations

import math
from enum import Enum
from typing import Dict, List, Optional, Tuple

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
    RULE_BG_DEV_LAP_APPLIC_001,
    RULE_BG_DEV_LAP_COMPRESSION_001,
    RULE_BG_DEV_LAP_COMPRESSION_DIFFDIA_001,
    RULE_BG_DEV_LAP_SPACING_001,
    RULE_BG_DEV_LAP_TENSION_001,
    RULE_BG_DEV_LAP_TENSION_DIFFDIA_001,
    RULE_BG_DEV_SPLICE_BEARING_001,
)
from beamgenius.registry.gatekeeper import GatekeeperDecision, evaluate_rule_gate


class SpliceMethod(str, Enum):
    """Permitted bar-splice method (Clause 9-21-4-1-1)."""

    LAP = "lap"
    BEARING = "bearing"
    WELDED = "welded"
    MECHANICAL = "mechanical"


class BarStressAction(str, Enum):
    """Governing bar stress action for the lap applicability limit."""

    TENSION = "tension"
    COMPRESSION = "compression"


class TensionLapClass(str, Enum):
    """Tension lap splice class (Clause 9-21-4-2-1): A (reduced) / B (general)."""

    A = "A"
    B = "B"


# --- BG-DEV-LAP-APPLIC-001 (Clause 9-21-4-1-1/-2, PDF p. 456 / Printed p. 436)
BG_LAP_APPLIC_MAX_LAP_DIAMETER_MM: float = 34.0
# Clause 9-21-4-1-2-ب: compression lap of a max-42 mm bar to a <= 34 mm bar,
# satisfying 9-21-4-5-2 (PDF p. 457 / Printed p. 437)
BG_LAP_APPLIC_COMP_MAX_LARGER_DIAMETER_MM: float = 42.0

# --- BG-DEV-LAP-SPACING-001 (Clause 9-21-4-1-4, PDF p. 457 / Printed p. 437)
BG_LAP_SPACING_DIVISOR: float = 5.0
BG_LAP_SPACING_MAX_MM: float = 150.0

# --- BG-DEV-LAP-TENSION-001 (Clause 9-21-4-2-1, PDF p. 457 / Printed p. 437)
BG_LAP_TENSION_CLASS_B_FACTOR: float = 1.3
BG_LAP_TENSION_CLASS_A_FACTOR: float = 1.0
BG_LAP_TENSION_CLASS_A_MIN_PROVIDED_RATIO: float = 2.0
BG_LAP_TENSION_CLASS_A_MAX_SPLICED_FRACTION: float = 0.5
BG_LAP_TENSION_MIN_LENGTH_MM: float = 300.0

# --- BG-DEV-LAP-COMPRESSION-001 (Clause 9-21-4-5-1, PDF p. 459 / Printed p. 439)
BG_LAP_COMPRESSION_MAX_DIAMETER_MM: float = 34.0
BG_LAP_COMPRESSION_FY_THRESHOLD_MPA: float = 420.0
BG_LAP_COMPRESSION_LOW_COEFF: float = 0.071
BG_LAP_COMPRESSION_HIGH_SLOPE: float = 0.13
BG_LAP_COMPRESSION_HIGH_INTERCEPT: float = 24.0
BG_LAP_COMPRESSION_MIN_LENGTH_MM: float = 300.0

# --- BG-DEV-SPLICE-BEARING-001 (Clause 9-21-4-6-3, PDF p. 460 / Printed p. 440)
BG_SPLICE_BEARING_MAX_END_FACE_DEVIATION_DEG: float = 5.0
BG_SPLICE_BEARING_MAX_MISALIGNMENT_DEG: float = 3.0


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


def evaluate_lap_splice_applicability(
    *,
    splice_method: Optional[SpliceMethod] = None,
    bar_stress_action: Optional[BarStressAction] = None,
    bar_diameter_mm: Optional[float] = None,
    larger_bar_diameter_mm: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate bar-splice method & lap diameter applicability (BG-DEV-LAP-APPLIC-001).

    Verified source: Mabhas 9 (1399), Clauses 9-21-4-1-1 & 9-21-4-1-2,
    PDF p. 456 / Printed p. 436 (and 9-21-4-1-2-ب, PDF p. 457 / Printed 437):

    - 9-21-4-1-1: bar splices are permitted by one of four methods — lap,
      bearing, welded, mechanical.
    - 9-21-4-1-2-الف: a lap splice is permitted, in tension and compression,
      for bars with diameter d_b <= 34 mm.
    - 9-21-4-1-2-ب: in compression, a lap splice of a bar of maximum diameter
      42 mm to a bar of diameter <= 34 mm is permitted (length governed by
      9-21-4-5-2).

    The splice method and bar diameters are required typed inputs (never
    assumed). A non-lap method is a permitted method (9-21-4-1-1) whose
    specifics are governed by its own clause (NOT the lap applicability
    limit). For a lap splice: d_b > 34 mm in tension, or a compression lap
    outside the 34 mm / 42->34 mm limits -> FAIL.
    """
    rule_id = RULE_BG_DEV_LAP_APPLIC_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "splice_method": (
            splice_method.value if isinstance(splice_method, SpliceMethod) else splice_method
        ),
        "bar_stress_action": (
            bar_stress_action.value
            if isinstance(bar_stress_action, BarStressAction)
            else bar_stress_action
        ),
        "bar_diameter_mm": bar_diameter_mm,
        "larger_bar_diameter_mm": larger_bar_diameter_mm,
    }

    # 1. Central Gatekeeper check
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")
    rule = gate.rule

    # 2. Splice method (9-21-4-1-1): required typed input
    method_raw: object = splice_method
    if method_raw is None:
        return _blocked_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _missing_input_diagnostic(
                    "MISSING_SPLICE_METHOD",
                    (
                        "The bar-splice method is required to apply Clause "
                        "9-21-4-1 (lap / bearing / welded / mechanical); it is "
                        "never assumed. Missing required input -> BLOCKED."
                    ),
                    rule=rule,
                    field_name="splice_method",
                )
            ],
        )
    if not isinstance(method_raw, SpliceMethod):
        return _invalid_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                EngineeringDiagnostic(
                    code="INVALID_SPLICE_METHOD",
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        "splice_method must be a SpliceMethod enumeration "
                        f"value, got {method_raw!r}."
                    ),
                    rule_id=rule_id,
                    field_name="splice_method",
                )
            ],
        )
    method_typed: SpliceMethod = method_raw

    # Non-lap methods: permitted per 9-21-4-1-1; the lap diameter limit of
    # 9-21-4-1-2 is lap-specific and does not apply.
    if method_typed is not SpliceMethod.LAP:
        return CalculationTraceStep.from_rule(
            rule,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="1",
            outcome=EvaluationOutcome.NOT_APPLICABLE,
            diagnostics=(),
            message=(
                f"NOT_APPLICABLE: '{method_typed.value}' splice is a permitted "
                "method per Clause 9-21-4-1-1; the lap diameter applicability "
                "limit of Clause 9-21-4-1-2 is lap-specific. Evaluate the "
                "clause governing this method (bearing 9-21-4-6, welded/"
                "mechanical 9-21-4-7)."
            ),
        )

    # 3. Lap method: stress action and diameter are required
    action_raw: object = bar_stress_action
    if action_raw is None:
        return _blocked_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                _missing_input_diagnostic(
                    "MISSING_BAR_STRESS_ACTION",
                    (
                        "The governing bar stress action (tension/compression) "
                        "is required to apply the lap applicability limit of "
                        "Clause 9-21-4-1-2; it is never assumed. Missing "
                        "required input -> BLOCKED."
                    ),
                    rule=rule,
                    field_name="bar_stress_action",
                )
            ],
        )
    if not isinstance(action_raw, BarStressAction):
        return _invalid_step(
            gate,
            raw_inputs=raw_inputs,
            diagnostics=[
                EngineeringDiagnostic(
                    code="INVALID_BAR_STRESS_ACTION",
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        "bar_stress_action must be a BarStressAction "
                        f"enumeration value, got {action_raw!r}."
                    ),
                    rule_id=rule_id,
                    field_name="bar_stress_action",
                )
            ],
        )
    action_typed: BarStressAction = action_raw

    invalid_diagnostics: List[EngineeringDiagnostic] = []
    missing_diagnostics: List[EngineeringDiagnostic] = []

    if bar_diameter_mm is None:
        missing_diagnostics.append(
            _missing_input_diagnostic(
                "MISSING_BAR_DIAMETER",
                (
                    "The governing bar diameter d_b is required for the lap "
                    "applicability limit of Clause 9-21-4-1-2; it is never "
                    "assumed. Missing required input -> BLOCKED."
                ),
                rule=rule,
                field_name="bar_diameter_mm",
            )
        )
    elif not math.isfinite(bar_diameter_mm) or bar_diameter_mm <= 0.0:
        invalid_diagnostics.append(
            _malformed_value_diagnostic(
                bar_diameter_mm,
                field_name="bar_diameter_mm",
                rule=rule,
            )
        )

    if larger_bar_diameter_mm is not None and (
        not math.isfinite(larger_bar_diameter_mm) or larger_bar_diameter_mm <= 0.0
    ):
        invalid_diagnostics.append(
            _malformed_value_diagnostic(
                larger_bar_diameter_mm,
                field_name="larger_bar_diameter_mm",
                rule=rule,
            )
        )

    if invalid_diagnostics:
        return _invalid_step(gate, raw_inputs=raw_inputs, diagnostics=invalid_diagnostics)
    if missing_diagnostics:
        return _blocked_step(gate, raw_inputs=raw_inputs, diagnostics=missing_diagnostics)
    assert bar_diameter_mm is not None

    intermediates: Dict[str, float] = {
        "bar_diameter_mm": bar_diameter_mm,
        "max_lap_diameter_mm": BG_LAP_APPLIC_MAX_LAP_DIAMETER_MM,
    }
    if larger_bar_diameter_mm is not None:
        intermediates["larger_bar_diameter_mm"] = larger_bar_diameter_mm
        intermediates["comp_max_larger_diameter_mm"] = (
            BG_LAP_APPLIC_COMP_MAX_LARGER_DIAMETER_MM
        )

    # 4. Clause 9-21-4-1-2 limits
    if action_typed is BarStressAction.TENSION:
        if bar_diameter_mm <= BG_LAP_APPLIC_MAX_LAP_DIAMETER_MM:
            return CalculationTraceStep.from_rule(
                rule,
                normalized_inputs=raw_inputs,
                intermediate_values=intermediates,
                final_result=bar_diameter_mm,
                unit="mm",
                outcome=EvaluationOutcome.PASS,
                diagnostics=(),
                message=(
                    f"PASS: lap splice permitted in tension for d_b = "
                    f"{bar_diameter_mm} mm <= {BG_LAP_APPLIC_MAX_LAP_DIAMETER_MM} mm "
                    "per Clause 9-21-4-1-2-الف."
                ),
            )
        diag = EngineeringDiagnostic(
            code="LAP_NOT_PERMITTED_DIAMETER_EXCEEDS_LIMIT",
            severity=DiagnosticSeverity.ERROR,
            message=(
                f"FAIL: lap splice in tension is permitted only for d_b <= "
                f"{BG_LAP_APPLIC_MAX_LAP_DIAMETER_MM} mm per Clause 9-21-4-1-2-الف; "
                f"d_b = {bar_diameter_mm} mm exceeds the limit."
            ),
            rule_id=rule_id,
            field_name="bar_diameter_mm",
        )
        return _fail_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates=intermediates,
            final_result=bar_diameter_mm,
            unit="mm",
            diagnostic=diag,
        )

    # COMPRESSION
    if larger_bar_diameter_mm is not None:
        # Clause 9-21-4-1-2-ب: larger <= 42 mm to smaller (d_b) <= 34 mm
        if (
            larger_bar_diameter_mm <= BG_LAP_APPLIC_COMP_MAX_LARGER_DIAMETER_MM
            and bar_diameter_mm <= BG_LAP_APPLIC_MAX_LAP_DIAMETER_MM
        ):
            return CalculationTraceStep.from_rule(
                rule,
                normalized_inputs=raw_inputs,
                intermediate_values=intermediates,
                final_result=bar_diameter_mm,
                unit="mm",
                outcome=EvaluationOutcome.PASS,
                diagnostics=(),
                message=(
                    f"PASS: compression lap of a {larger_bar_diameter_mm} mm bar "
                    f"to a {bar_diameter_mm} mm bar is permitted per Clause "
                    "9-21-4-1-2-ب (larger <= 42 mm, smaller <= 34 mm; length per "
                    "Clause 9-21-4-5-2)."
                ),
            )
        diag = EngineeringDiagnostic(
            code="LAP_NOT_PERMITTED_COMPRESSION_DIAMETER_LIMITS",
            severity=DiagnosticSeverity.ERROR,
            message=(
                f"FAIL: compression lap of different-diameter bars is permitted "
                f"only for a larger bar <= "
                f"{BG_LAP_APPLIC_COMP_MAX_LARGER_DIAMETER_MM} mm to a smaller bar "
                f"<= {BG_LAP_APPLIC_MAX_LAP_DIAMETER_MM} mm per Clause 9-21-4-1-2-ب; "
                f"got larger = {larger_bar_diameter_mm} mm, smaller = "
                f"{bar_diameter_mm} mm."
            ),
            rule_id=rule_id,
            field_name="bar_diameter_mm",
        )
        return _fail_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates=intermediates,
            final_result=bar_diameter_mm,
            unit="mm",
            diagnostic=diag,
        )

    if bar_diameter_mm <= BG_LAP_APPLIC_MAX_LAP_DIAMETER_MM:
        return CalculationTraceStep.from_rule(
            rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=bar_diameter_mm,
            unit="mm",
            outcome=EvaluationOutcome.PASS,
            diagnostics=(),
            message=(
                f"PASS: lap splice permitted in compression for d_b = "
                f"{bar_diameter_mm} mm <= {BG_LAP_APPLIC_MAX_LAP_DIAMETER_MM} mm "
                "per Clause 9-21-4-1-2-الف."
            ),
        )
    diag = EngineeringDiagnostic(
        code="LAP_NOT_PERMITTED_DIAMETER_EXCEEDS_LIMIT",
        severity=DiagnosticSeverity.ERROR,
        message=(
            f"FAIL: lap splice in compression is permitted only for d_b <= "
            f"{BG_LAP_APPLIC_MAX_LAP_DIAMETER_MM} mm per Clause 9-21-4-1-2-الف "
            f"(or a larger bar <= "
            f"{BG_LAP_APPLIC_COMP_MAX_LARGER_DIAMETER_MM} mm to a smaller bar <= "
            f"{BG_LAP_APPLIC_MAX_LAP_DIAMETER_MM} mm per 9-21-4-1-2-ب); d_b = "
            f"{bar_diameter_mm} mm exceeds the single-bar limit."
        ),
        rule_id=rule_id,
        field_name="bar_diameter_mm",
    )
    return _fail_step(
        gate,
        raw_inputs=raw_inputs,
        intermediates=intermediates,
        final_result=bar_diameter_mm,
        unit="mm",
        diagnostic=diag,
    )


def evaluate_lap_splice_spacing(
    *,
    lap_length_mm: Optional[float] = None,
    transverse_center_to_center_spacing_mm: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate contact-lap transverse spacing (BG-DEV-LAP-SPACING-001).

    Verified source: Mabhas 9 (1399), Clause 9-21-4-1-4, PDF p. 457 /
    Printed p. 437: «برای وصله‌ی پوششی تماسی در اعضای خمشی، فاصله‌ی عرضی
    مرکز به مرکز میلگردهای وصله شده نباید از یک پنجم طول وصله و ۱۵۰
    میلی‌متر تجاوز نماید.» — for a contact lap splice in flexural members,
    the transverse centre-to-centre spacing of the spliced bars shall not
    exceed one fifth of the lap length and 150 mm:

        s_transverse <= min(lap_length / 5, 150 mm)

    The lap length and the transverse spacing are required typed inputs
    (never assumed). A spacing above the limit -> FAIL.
    """
    rule_id = RULE_BG_DEV_LAP_SPACING_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "lap_length_mm": lap_length_mm,
        "transverse_center_to_center_spacing_mm": transverse_center_to_center_spacing_mm,
    }

    # 1. Central Gatekeeper check
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")
    rule = gate.rule

    invalid_diagnostics: List[EngineeringDiagnostic] = []
    missing_diagnostics: List[EngineeringDiagnostic] = []

    if lap_length_mm is None:
        missing_diagnostics.append(
            _missing_input_diagnostic(
                "MISSING_LAP_LENGTH",
                (
                    "The lap splice length is required for the one-fifth "
                    "transverse-spacing limit of Clause 9-21-4-1-4; it is never "
                    "assumed. Missing required input -> BLOCKED."
                ),
                rule=rule,
                field_name="lap_length_mm",
            )
        )
    elif not math.isfinite(lap_length_mm) or lap_length_mm <= 0.0:
        invalid_diagnostics.append(
            _malformed_value_diagnostic(
                lap_length_mm, field_name="lap_length_mm", rule=rule
            )
        )

    if transverse_center_to_center_spacing_mm is None:
        missing_diagnostics.append(
            _missing_input_diagnostic(
                "MISSING_TRANSVERSE_SPACING",
                (
                    "The transverse centre-to-centre spacing of the spliced "
                    "bars is required (Clause 9-21-4-1-4); it is never assumed. "
                    "Missing required input -> BLOCKED."
                ),
                rule=rule,
                field_name="transverse_center_to_center_spacing_mm",
            )
        )
    elif (
        not math.isfinite(transverse_center_to_center_spacing_mm)
        or transverse_center_to_center_spacing_mm <= 0.0
    ):
        invalid_diagnostics.append(
            _malformed_value_diagnostic(
                transverse_center_to_center_spacing_mm,
                field_name="transverse_center_to_center_spacing_mm",
                rule=rule,
            )
        )

    if invalid_diagnostics:
        return _invalid_step(gate, raw_inputs=raw_inputs, diagnostics=invalid_diagnostics)
    if missing_diagnostics:
        return _blocked_step(gate, raw_inputs=raw_inputs, diagnostics=missing_diagnostics)
    assert lap_length_mm is not None
    assert transverse_center_to_center_spacing_mm is not None

    lap_fifth_mm = lap_length_mm / BG_LAP_SPACING_DIVISOR
    limit_mm = min(lap_fifth_mm, BG_LAP_SPACING_MAX_MM)

    intermediates: Dict[str, float] = {
        "lap_length_mm": lap_length_mm,
        "lap_length_over_five_mm": lap_fifth_mm,
        "absolute_max_transverse_spacing_mm": BG_LAP_SPACING_MAX_MM,
        "max_permitted_transverse_spacing_mm": limit_mm,
        "provided_transverse_spacing_mm": transverse_center_to_center_spacing_mm,
    }

    if transverse_center_to_center_spacing_mm > limit_mm:
        diag = EngineeringDiagnostic(
            code="CONTACT_LAP_TRANSVERSE_SPACING_EXCEEDED",
            severity=DiagnosticSeverity.ERROR,
            message=(
                f"FAIL: transverse centre-to-centre spacing "
                f"{transverse_center_to_center_spacing_mm} mm > min(lap/5, 150 mm) "
                f"= {limit_mm} mm required by Clause 9-21-4-1-4."
            ),
            rule_id=rule_id,
            field_name="transverse_center_to_center_spacing_mm",
        )
        return _fail_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates=intermediates,
            final_result=limit_mm,
            unit="mm",
            diagnostic=diag,
        )

    return CalculationTraceStep.from_rule(
        rule,
        normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=limit_mm,
        unit="mm",
        outcome=EvaluationOutcome.PASS,
        diagnostics=(),
        message=(
            f"PASS: transverse centre-to-centre spacing "
            f"{transverse_center_to_center_spacing_mm} mm <= min(lap/5, 150 mm) "
            f"= {limit_mm} mm per Clause 9-21-4-1-4."
        ),
    )


def evaluate_lap_splice_tension(
    *,
    development_length_mm: Optional[float] = None,
    tension_lap_class: Optional[TensionLapClass] = None,
    as_provided_over_required_ratio: Optional[float] = None,
    fraction_of_provided_bars_spliced: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate the tension lap splice length (BG-DEV-LAP-TENSION-001).

    Verified source: Mabhas 9 (1399), Clause 9-21-4-2-1, PDF p. 457 /
    Printed p. 437:

    - general (type B):  l_st = 1.3 * l_d
    - reduced (type A):  l_st = 1.0 * l_d  only if (الف) the reinforcement
      provided within the lap length is at least 2x the required AND (ب) at
      most half of the provided reinforcement is spliced within the lap
      length;
    - in all cases l_st >= 300 mm; l_d is the tension development length per
      9-21-4-2-1-1 (Clause 9-21-3-1).

    l_d is a caller-provided verified value (Stage C ``BG-DEV-LENGTH-*``);
    it is NEVER computed here. A missing l_d -> BLOCKED
    (``MISSING_DEVELOPMENT_LENGTH``). The excess-reinforcement reduction of
    9-21-3-9 is NOT applied (9-21-4-1-5). Requesting type A when the two
    enabling conditions are not satisfied -> FAIL (the reduction is not
    permitted); evaluate type B instead.
    """
    rule_id = RULE_BG_DEV_LAP_TENSION_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "development_length_mm": development_length_mm,
        "tension_lap_class": (
            tension_lap_class.value
            if isinstance(tension_lap_class, TensionLapClass)
            else tension_lap_class
        ),
        "as_provided_over_required_ratio": as_provided_over_required_ratio,
        "fraction_of_provided_bars_spliced": fraction_of_provided_bars_spliced,
    }

    # 1. Central Gatekeeper check
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")
    rule = gate.rule

    invalid_diagnostics: List[EngineeringDiagnostic] = []
    missing_diagnostics: List[EngineeringDiagnostic] = []

    # 2. Verified development length l_d (consumed, never computed)
    if development_length_mm is None:
        missing_diagnostics.append(
            _missing_input_diagnostic(
                "MISSING_DEVELOPMENT_LENGTH",
                (
                    "The verified tension development length l_d (Clause "
                    "9-21-3-1 / 9-21-4-2-1-1) is required input for the tension "
                    "lap length of Clause 9-21-4-2-1; Clause 9-21-3 is NOT "
                    "computed by this rule (VERIFY_PENDING here). Missing "
                    "required input -> BLOCKED, never an invented value."
                ),
                rule=rule,
                field_name="development_length_mm",
                required_verification=(
                    "Supply the tension development length from a verified "
                    "Clause 9-21-3 evaluation (e.g. BG-DEV-LENGTH-TENSION-001); "
                    "the engine does not compute Clause 9-21-3 here."
                ),
            )
        )
    elif not math.isfinite(development_length_mm) or development_length_mm <= 0.0:
        invalid_diagnostics.append(
            _malformed_value_diagnostic(
                development_length_mm,
                field_name="development_length_mm",
                rule=rule,
            )
        )

    # 3. Tension lap class (required typed input)
    class_raw: object = tension_lap_class
    if class_raw is None:
        missing_diagnostics.append(
            _missing_input_diagnostic(
                "MISSING_TENSION_LAP_CLASS",
                (
                    "The tension lap class (A reduced / B general) is required "
                    "to select the 1.0*l_d / 1.3*l_d factor of Clause 9-21-4-2-1; "
                    "it is never assumed. Missing required input -> BLOCKED."
                ),
                rule=rule,
                field_name="tension_lap_class",
            )
        )
    elif not isinstance(class_raw, TensionLapClass):
        invalid_diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_TENSION_LAP_CLASS",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    "tension_lap_class must be a TensionLapClass enumeration "
                    f"value, got {class_raw!r}."
                ),
                rule_id=rule_id,
                field_name="tension_lap_class",
            )
        )

    if invalid_diagnostics:
        return _invalid_step(gate, raw_inputs=raw_inputs, diagnostics=invalid_diagnostics)
    if missing_diagnostics:
        return _blocked_step(gate, raw_inputs=raw_inputs, diagnostics=missing_diagnostics)
    assert development_length_mm is not None
    class_typed: TensionLapClass = class_raw  # type: ignore[assignment]

    # 4. Select the factor; class A requires the two enabling conditions
    if class_typed is TensionLapClass.B:
        factor = BG_LAP_TENSION_CLASS_B_FACTOR
        intermediates: Dict[str, float] = {
            "development_length_mm": development_length_mm,
            "lap_class_b_factor": factor,
        }
    else:
        # Type A: both conditions required and must hold.
        if as_provided_over_required_ratio is None or (
            fraction_of_provided_bars_spliced is None
        ):
            return _blocked_step(
                gate,
                raw_inputs=raw_inputs,
                diagnostics=[
                    _missing_input_diagnostic(
                        "MISSING_CLASS_A_CONDITIONS",
                        (
                            "Type A lap (1.0*l_d) requires both enabling "
                            "conditions of Clause 9-21-4-2-1: the provided/"
                            "required reinforcement ratio (>= 2) and the "
                            "fraction of provided bars spliced (<= 1/2). They "
                            "are never assumed. Missing required input -> BLOCKED."
                        ),
                        rule=rule,
                        field_name="as_provided_over_required_ratio",
                        required_verification=(
                            "Supply as_provided_over_required_ratio and "
                            "fraction_of_provided_bars_spliced, or evaluate the "
                            "general type B lap."
                        ),
                    )
                ],
            )
        if (
            not math.isfinite(as_provided_over_required_ratio)
            or as_provided_over_required_ratio <= 0.0
            or not math.isfinite(fraction_of_provided_bars_spliced)
            or fraction_of_provided_bars_spliced <= 0.0
        ):
            return _invalid_step(
                gate,
                raw_inputs=raw_inputs,
                diagnostics=[
                    _malformed_value_diagnostic(
                        as_provided_over_required_ratio,
                        field_name="as_provided_over_required_ratio",
                        rule=rule,
                    ),
                    _malformed_value_diagnostic(
                        fraction_of_provided_bars_spliced,
                        field_name="fraction_of_provided_bars_spliced",
                        rule=rule,
                    ),
                ],
            )
        condition_provided_ok = (
            as_provided_over_required_ratio >= BG_LAP_TENSION_CLASS_A_MIN_PROVIDED_RATIO
        )
        condition_spliced_ok = (
            fraction_of_provided_bars_spliced
            <= BG_LAP_TENSION_CLASS_A_MAX_SPLICED_FRACTION
        )
        if not (condition_provided_ok and condition_spliced_ok):
            diag = EngineeringDiagnostic(
                code="CLASS_A_CONDITIONS_NOT_MET",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    "FAIL: type A tension lap (1.0*l_d) is permitted only when "
                    "provided reinforcement >= 2x required AND at most half of "
                    "the provided reinforcement is spliced within the lap "
                    "length (Clause 9-21-4-2-1). Got provided/required = "
                    f"{as_provided_over_required_ratio} and spliced fraction = "
                    f"{fraction_of_provided_bars_spliced}; evaluate the general "
                    "type B lap (1.3*l_d) instead."
                ),
                rule_id=rule_id,
                field_name="tension_lap_class",
            )
            return _fail_step(
                gate,
                raw_inputs=raw_inputs,
                intermediates={
                    "development_length_mm": development_length_mm,
                    "as_provided_over_required_ratio": as_provided_over_required_ratio,
                    "fraction_of_provided_bars_spliced": fraction_of_provided_bars_spliced,
                    "class_a_min_provided_ratio": (
                        BG_LAP_TENSION_CLASS_A_MIN_PROVIDED_RATIO
                    ),
                    "class_a_max_spliced_fraction": (
                        BG_LAP_TENSION_CLASS_A_MAX_SPLICED_FRACTION
                    ),
                },
                final_result=None,
                unit="mm",
                diagnostic=diag,
            )
        factor = BG_LAP_TENSION_CLASS_A_FACTOR
        intermediates = {
            "development_length_mm": development_length_mm,
            "lap_class_a_factor": factor,
            "as_provided_over_required_ratio": as_provided_over_required_ratio,
            "fraction_of_provided_bars_spliced": fraction_of_provided_bars_spliced,
        }

    # 5. l_st = factor * l_d, floored at 300 mm
    lst_raw_mm = factor * development_length_mm
    lst_mm = max(lst_raw_mm, BG_LAP_TENSION_MIN_LENGTH_MM)
    intermediates["lap_class_factor"] = factor
    intermediates["lap_length_before_floor_mm"] = lst_raw_mm
    intermediates["min_lap_length_mm"] = BG_LAP_TENSION_MIN_LENGTH_MM

    return CalculationTraceStep.from_rule(
        rule,
        normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=lst_mm,
        unit="mm",
        outcome=EvaluationOutcome.COMPUTED,
        diagnostics=(),
        message=(
            f"Computed tension lap splice length l_st = {factor} * l_d = "
            f"{factor} * {development_length_mm} = {lst_raw_mm} mm, floored at "
            f"{BG_LAP_TENSION_MIN_LENGTH_MM} mm -> {lst_mm} mm per Clause "
            "9-21-4-2-1 (no excess-reinforcement l_d reduction per 9-21-4-1-5)."
        ),
    )


def evaluate_lap_splice_tension_diffdia(
    *,
    development_length_larger_bar_mm: Optional[float] = None,
    tension_lap_length_smaller_bar_mm: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate a different-diameter tension lap (BG-DEV-LAP-TENSION-DIFFDIA-001).

    Verified source: Mabhas 9 (1399), Clause 9-21-4-2 (mixed diameter),
    PDF p. 458 / Printed p. 438: when a lap splice joins bars of different
    diameters, the lap length l_s shall not be less than either of:

        (الف) the development length l_d for the larger bar;
        (ب) the tension lap length l_st for the smaller bar.

    i.e.  l_s >= max(l_d_larger, l_st_smaller).

    Both governing lengths are caller-provided verified values (Stage C
    ``l_d`` and Clause 9-21-4-2-1 ``l_st``); they are NEVER computed here.
    A missing one -> BLOCKED (``MISSING_*``). The lap applicability limit
    of 9-21-4-1-2 (d_b <= 34 mm in tension) still governs and is checked by
    ``BG-DEV-LAP-APPLIC-001``.
    """
    rule_id = RULE_BG_DEV_LAP_TENSION_DIFFDIA_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "development_length_larger_bar_mm": development_length_larger_bar_mm,
        "tension_lap_length_smaller_bar_mm": tension_lap_length_smaller_bar_mm,
    }

    # 1. Central Gatekeeper check
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")
    rule = gate.rule

    invalid_diagnostics: List[EngineeringDiagnostic] = []
    missing_diagnostics: List[EngineeringDiagnostic] = []

    if development_length_larger_bar_mm is None:
        missing_diagnostics.append(
            _missing_input_diagnostic(
                "MISSING_DEVELOPMENT_LENGTH_LARGER_BAR",
                (
                    "The verified development length l_d for the larger bar is "
                    "required (Clause 9-21-4-2-الف); it is never computed here. "
                    "Missing required input -> BLOCKED."
                ),
                rule=rule,
                field_name="development_length_larger_bar_mm",
                required_verification=(
                    "Supply the larger-bar development length from a verified "
                    "Clause 9-21-3 evaluation."
                ),
            )
        )
    elif (
        not math.isfinite(development_length_larger_bar_mm)
        or development_length_larger_bar_mm <= 0.0
    ):
        invalid_diagnostics.append(
            _malformed_value_diagnostic(
                development_length_larger_bar_mm,
                field_name="development_length_larger_bar_mm",
                rule=rule,
            )
        )

    if tension_lap_length_smaller_bar_mm is None:
        missing_diagnostics.append(
            _missing_input_diagnostic(
                "MISSING_TENSION_LAP_LENGTH_SMALLER_BAR",
                (
                    "The tension lap length l_st for the smaller bar (Clause "
                    "9-21-4-2-ب) is required; it is never computed here. Missing "
                    "required input -> BLOCKED."
                ),
                rule=rule,
                field_name="tension_lap_length_smaller_bar_mm",
                required_verification=(
                    "Supply the smaller-bar tension lap length from "
                    "BG-DEV-LAP-TENSION-001 (Clause 9-21-4-2-1)."
                ),
            )
        )
    elif (
        not math.isfinite(tension_lap_length_smaller_bar_mm)
        or tension_lap_length_smaller_bar_mm <= 0.0
    ):
        invalid_diagnostics.append(
            _malformed_value_diagnostic(
                tension_lap_length_smaller_bar_mm,
                field_name="tension_lap_length_smaller_bar_mm",
                rule=rule,
            )
        )

    if invalid_diagnostics:
        return _invalid_step(gate, raw_inputs=raw_inputs, diagnostics=invalid_diagnostics)
    if missing_diagnostics:
        return _blocked_step(gate, raw_inputs=raw_inputs, diagnostics=missing_diagnostics)
    assert development_length_larger_bar_mm is not None
    assert tension_lap_length_smaller_bar_mm is not None

    ls_mm = max(development_length_larger_bar_mm, tension_lap_length_smaller_bar_mm)

    intermediates: Dict[str, float] = {
        "development_length_larger_bar_mm": development_length_larger_bar_mm,
        "tension_lap_length_smaller_bar_mm": tension_lap_length_smaller_bar_mm,
        "governing_lap_length_mm": ls_mm,
    }

    return CalculationTraceStep.from_rule(
        rule,
        normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=ls_mm,
        unit="mm",
        outcome=EvaluationOutcome.COMPUTED,
        diagnostics=(),
        message=(
            f"Computed different-diameter tension lap length l_s = max(l_d "
            f"larger = {development_length_larger_bar_mm}, l_st smaller = "
            f"{tension_lap_length_smaller_bar_mm}) = {ls_mm} mm per Clause "
            "9-21-4-2."
        ),
    )


def evaluate_lap_splice_compression(
    *,
    bar_diameter_mm: Optional[float] = None,
    yield_stress_mpa: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate the compression lap splice length (BG-DEV-LAP-COMPRESSION-001).

    Verified source: Mabhas 9 (1399), Clause 9-21-4-5-1, PDF p. 459 /
    Printed p. 439: the compression lap length l_sc of deformed bars with
    diameter d_b <= 34 mm is:

        (الف) f_y <= 420 MPa:  l_sc = 0.071 * f_y * d_b
        (ب) f_y >  420 MPa:  l_sc = (0.13 * f_y - 24) * d_b

    and in all cases l_sc >= 300 mm.

    d_b and f_y are required typed inputs (never assumed). d_b > 34 mm ->
    NOT_APPLICABLE (the 9-21-4-5-1 formula is limited to d_b <= 34 mm; use
    the different-diameter compression lap of 9-21-4-5-2 /
    ``BG-DEV-LAP-COMPRESSION-DIFFDIA-001`` for the smaller bar).
    """
    rule_id = RULE_BG_DEV_LAP_COMPRESSION_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "bar_diameter_mm": bar_diameter_mm,
        "yield_stress_mpa": yield_stress_mpa,
    }

    # 1. Central Gatekeeper check
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")
    rule = gate.rule

    invalid_diagnostics: List[EngineeringDiagnostic] = []
    missing_diagnostics: List[EngineeringDiagnostic] = []

    if bar_diameter_mm is None:
        missing_diagnostics.append(
            _missing_input_diagnostic(
                "MISSING_BAR_DIAMETER",
                (
                    "The bar diameter d_b is required for the compression lap "
                    "length of Clause 9-21-4-5-1; it is never assumed. Missing "
                    "required input -> BLOCKED."
                ),
                rule=rule,
                field_name="bar_diameter_mm",
            )
        )
    elif not math.isfinite(bar_diameter_mm) or bar_diameter_mm <= 0.0:
        invalid_diagnostics.append(
            _malformed_value_diagnostic(
                bar_diameter_mm, field_name="bar_diameter_mm", rule=rule
            )
        )

    if yield_stress_mpa is None:
        missing_diagnostics.append(
            _missing_input_diagnostic(
                "MISSING_YIELD_STRESS",
                (
                    "The reinforcement yield stress f_y is required for the "
                    "compression lap length of Clause 9-21-4-5-1; it is never "
                    "assumed. Missing required input -> BLOCKED."
                ),
                rule=rule,
                field_name="yield_stress_mpa",
            )
        )
    elif not math.isfinite(yield_stress_mpa) or yield_stress_mpa <= 0.0:
        invalid_diagnostics.append(
            _malformed_value_diagnostic(
                yield_stress_mpa, field_name="yield_stress_mpa", rule=rule
            )
        )

    if invalid_diagnostics:
        return _invalid_step(gate, raw_inputs=raw_inputs, diagnostics=invalid_diagnostics)
    if missing_diagnostics:
        return _blocked_step(gate, raw_inputs=raw_inputs, diagnostics=missing_diagnostics)
    assert bar_diameter_mm is not None
    assert yield_stress_mpa is not None

    # Clause 9-21-4-5-1 formula applies only for d_b <= 34 mm
    if bar_diameter_mm > BG_LAP_COMPRESSION_MAX_DIAMETER_MM:
        return _not_applicable_step(
            gate,
            raw_inputs=raw_inputs,
            unit="mm",
            message=(
                f"NOT_APPLICABLE: the Clause 9-21-4-5-1 compression lap formula "
                f"applies to bars with d_b <= "
                f"{BG_LAP_COMPRESSION_MAX_DIAMETER_MM} mm; d_b = {bar_diameter_mm} mm "
                "is out of its direct scope. For a larger-to-smaller bar lap use "
                "the different-diameter compression lap of Clause 9-21-4-5-2 "
                "(BG-DEV-LAP-COMPRESSION-DIFFDIA-001), which governs the "
                "smaller bar via this clause."
            ),
        )

    if yield_stress_mpa <= BG_LAP_COMPRESSION_FY_THRESHOLD_MPA:
        coeff = BG_LAP_COMPRESSION_LOW_COEFF
        lsc_raw_mm = coeff * yield_stress_mpa * bar_diameter_mm
        branch = "f_y <= 420 MPa: l_sc = 0.071*f_y*d_b"
    else:
        coeff = (
            BG_LAP_COMPRESSION_HIGH_SLOPE * yield_stress_mpa
            - BG_LAP_COMPRESSION_HIGH_INTERCEPT
        )
        lsc_raw_mm = coeff * bar_diameter_mm
        branch = "f_y > 420 MPa: l_sc = (0.13*f_y - 24)*d_b"

    lsc_mm = max(lsc_raw_mm, BG_LAP_COMPRESSION_MIN_LENGTH_MM)

    intermediates: Dict[str, float] = {
        "bar_diameter_mm": bar_diameter_mm,
        "yield_stress_mpa": yield_stress_mpa,
        "fy_threshold_mpa": BG_LAP_COMPRESSION_FY_THRESHOLD_MPA,
        "effective_coefficient": coeff,
        "lap_length_before_floor_mm": lsc_raw_mm,
        "min_lap_length_mm": BG_LAP_COMPRESSION_MIN_LENGTH_MM,
    }

    return CalculationTraceStep.from_rule(
        rule,
        normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=lsc_mm,
        unit="mm",
        outcome=EvaluationOutcome.COMPUTED,
        diagnostics=(),
        message=(
            f"Computed compression lap splice length l_sc ({branch}) = "
            f"{lsc_raw_mm} mm, floored at {BG_LAP_COMPRESSION_MIN_LENGTH_MM} mm -> "
            f"{lsc_mm} mm per Clause 9-21-4-5-1."
        ),
    )


def evaluate_lap_splice_compression_diffdia(
    *,
    compression_dev_length_larger_bar_mm: Optional[float] = None,
    compression_lap_length_smaller_bar_mm: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate a different-diameter compression lap (BG-DEV-LAP-COMPRESSION-DIFFDIA-001).

    Verified source: Mabhas 9 (1399), Clause 9-21-4-5-2, PDF p. 460 /
    Printed p. 440: when a compression lap splice joins bars of different
    diameters, the lap length shall not be less than either of:

        (الف) the compression development length l_dc for the larger bar,
              computed per Clause 9-21-3-8;
        (ب) the compression lap length l_sc for the smaller bar, computed
              per Clause 9-21-4-5-1.

    i.e.  l_s >= max(l_dc_larger, l_sc_smaller).

    Both governing lengths are caller-provided verified values (Stage C
    ``l_dc`` and Clause 9-21-4-5-1 ``l_sc``); they are NEVER computed here.
    A missing one -> BLOCKED (``MISSING_*``).
    """
    rule_id = RULE_BG_DEV_LAP_COMPRESSION_DIFFDIA_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "compression_dev_length_larger_bar_mm": compression_dev_length_larger_bar_mm,
        "compression_lap_length_smaller_bar_mm": compression_lap_length_smaller_bar_mm,
    }

    # 1. Central Gatekeeper check
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")
    rule = gate.rule

    invalid_diagnostics: List[EngineeringDiagnostic] = []
    missing_diagnostics: List[EngineeringDiagnostic] = []

    if compression_dev_length_larger_bar_mm is None:
        missing_diagnostics.append(
            _missing_input_diagnostic(
                "MISSING_COMPRESSION_DEV_LENGTH_LARGER_BAR",
                (
                    "The verified compression development length l_dc for the "
                    "larger bar (Clause 9-21-4-5-2-الف / 9-21-3-8) is required; "
                    "it is never computed here. Missing required input -> BLOCKED."
                ),
                rule=rule,
                field_name="compression_dev_length_larger_bar_mm",
                required_verification=(
                    "Supply the larger-bar compression development length from a "
                    "verified Clause 9-21-3-8 evaluation "
                    "(BG-DEV-LENGTH-COMPRESSION-001)."
                ),
            )
        )
    elif (
        not math.isfinite(compression_dev_length_larger_bar_mm)
        or compression_dev_length_larger_bar_mm <= 0.0
    ):
        invalid_diagnostics.append(
            _malformed_value_diagnostic(
                compression_dev_length_larger_bar_mm,
                field_name="compression_dev_length_larger_bar_mm",
                rule=rule,
            )
        )

    if compression_lap_length_smaller_bar_mm is None:
        missing_diagnostics.append(
            _missing_input_diagnostic(
                "MISSING_COMPRESSION_LAP_LENGTH_SMALLER_BAR",
                (
                    "The compression lap length l_sc for the smaller bar "
                    "(Clause 9-21-4-5-2-ب / 9-21-4-5-1) is required; it is never "
                    "computed here. Missing required input -> BLOCKED."
                ),
                rule=rule,
                field_name="compression_lap_length_smaller_bar_mm",
                required_verification=(
                    "Supply the smaller-bar compression lap length from "
                    "BG-DEV-LAP-COMPRESSION-001 (Clause 9-21-4-5-1)."
                ),
            )
        )
    elif (
        not math.isfinite(compression_lap_length_smaller_bar_mm)
        or compression_lap_length_smaller_bar_mm <= 0.0
    ):
        invalid_diagnostics.append(
            _malformed_value_diagnostic(
                compression_lap_length_smaller_bar_mm,
                field_name="compression_lap_length_smaller_bar_mm",
                rule=rule,
            )
        )

    if invalid_diagnostics:
        return _invalid_step(gate, raw_inputs=raw_inputs, diagnostics=invalid_diagnostics)
    if missing_diagnostics:
        return _blocked_step(gate, raw_inputs=raw_inputs, diagnostics=missing_diagnostics)
    assert compression_dev_length_larger_bar_mm is not None
    assert compression_lap_length_smaller_bar_mm is not None

    ls_mm = max(
        compression_dev_length_larger_bar_mm, compression_lap_length_smaller_bar_mm
    )

    intermediates: Dict[str, float] = {
        "compression_dev_length_larger_bar_mm": compression_dev_length_larger_bar_mm,
        "compression_lap_length_smaller_bar_mm": compression_lap_length_smaller_bar_mm,
        "governing_lap_length_mm": ls_mm,
    }

    return CalculationTraceStep.from_rule(
        rule,
        normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=ls_mm,
        unit="mm",
        outcome=EvaluationOutcome.COMPUTED,
        diagnostics=(),
        message=(
            f"Computed different-diameter compression lap length l_s = max(l_dc "
            f"larger = {compression_dev_length_larger_bar_mm}, l_sc smaller = "
            f"{compression_lap_length_smaller_bar_mm}) = {ls_mm} mm per Clause "
            "9-21-4-5-2."
        ),
    )


def evaluate_splice_bearing(
    *,
    bars_compression_only: Optional[bool] = None,
    ends_cut_perpendicular: Optional[bool] = None,
    bars_coaxial: Optional[bool] = None,
    member_has_confinement: Optional[bool] = None,
    end_face_deviation_deg: Optional[float] = None,
    axial_misalignment_deg: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate a bearing splice of compression-only bars (BG-DEV-SPLICE-BEARING-001).

    Verified source: Mabhas 9 (1399), Clause 9-21-4-6, PDF p. 460 /
    Printed p. 440:

    - 9-21-4-6-1: for bars ONLY under compression, force transfer by bearing
      between two bars whose ends are cut perpendicular to the bar axis is
      permitted; the two spliced bars must be coaxial (e.g. via a ring).
    - 9-21-4-6-2: a bearing splice is permitted only in members with
      confinement (خاموت: tied / spiral / دورگیر).
    - 9-21-4-6-3: the bar ends must lie on a flat surface perpendicular to
      the bar axis with a maximum end-face deviation of 5 degrees, and the
      two bars must be connected so that their axial misalignment does not
      exceed 3 degrees.

    All six conditions are required typed inputs (never assumed). The first
    violated condition (checked in clause order 6-1, 6-2, 6-3) -> FAIL; all
    satisfied -> PASS. This rule checks geometry/applicability only — it does
    not transfer or verify any force.
    """
    rule_id = RULE_BG_DEV_SPLICE_BEARING_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "bars_compression_only": bars_compression_only,
        "ends_cut_perpendicular": ends_cut_perpendicular,
        "bars_coaxial": bars_coaxial,
        "member_has_confinement": member_has_confinement,
        "end_face_deviation_deg": end_face_deviation_deg,
        "axial_misalignment_deg": axial_misalignment_deg,
    }

    # 1. Central Gatekeeper check
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="deg")
    rule = gate.rule

    invalid_diagnostics: List[EngineeringDiagnostic] = []
    missing_diagnostics: List[EngineeringDiagnostic] = []

    bool_fields: Tuple[Tuple[str, object], ...] = (
        ("bars_compression_only", bars_compression_only),
        ("ends_cut_perpendicular", ends_cut_perpendicular),
        ("bars_coaxial", bars_coaxial),
        ("member_has_confinement", member_has_confinement),
    )
    for field_name, value in bool_fields:
        if value is None:
            missing_diagnostics.append(
                _missing_input_diagnostic(
                    "MISSING_" + field_name.upper(),
                    (
                        f"{field_name} is required to evaluate the bearing "
                        "splice conditions of Clause 9-21-4-6; it is never "
                        "assumed. Missing required input -> BLOCKED."
                    ),
                    rule=rule,
                    field_name=field_name,
                )
            )
        elif not isinstance(value, bool):
            invalid_diagnostics.append(
                EngineeringDiagnostic(
                    code="INVALID_" + field_name.upper(),
                    severity=DiagnosticSeverity.ERROR,
                    message=f"{field_name} must be a bool, got {value!r}.",
                    rule_id=rule_id,
                    field_name=field_name,
                )
            )

    if end_face_deviation_deg is None:
        missing_diagnostics.append(
            _missing_input_diagnostic(
                "MISSING_END_FACE_DEVIATION_DEG",
                (
                    "end_face_deviation_deg is required to evaluate the bearing "
                    "splice angular limits of Clause 9-21-4-6-3; it is never "
                    "assumed. Missing required input -> BLOCKED."
                ),
                rule=rule,
                field_name="end_face_deviation_deg",
            )
        )
    elif not math.isfinite(end_face_deviation_deg) or end_face_deviation_deg < 0.0:
        invalid_diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_END_FACE_DEVIATION_DEG",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    "end_face_deviation_deg must be a finite angle >= 0 degrees, "
                    f"got {end_face_deviation_deg!r}."
                ),
                rule_id=rule_id,
                field_name="end_face_deviation_deg",
            )
        )

    if axial_misalignment_deg is None:
        missing_diagnostics.append(
            _missing_input_diagnostic(
                "MISSING_AXIAL_MISALIGNMENT_DEG",
                (
                    "axial_misalignment_deg is required to evaluate the bearing "
                    "splice angular limits of Clause 9-21-4-6-3; it is never "
                    "assumed. Missing required input -> BLOCKED."
                ),
                rule=rule,
                field_name="axial_misalignment_deg",
            )
        )
    elif not math.isfinite(axial_misalignment_deg) or axial_misalignment_deg < 0.0:
        invalid_diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_AXIAL_MISALIGNMENT_DEG",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    "axial_misalignment_deg must be a finite angle >= 0 degrees, "
                    f"got {axial_misalignment_deg!r}."
                ),
                rule_id=rule_id,
                field_name="axial_misalignment_deg",
            )
        )

    if invalid_diagnostics:
        return _invalid_step(gate, raw_inputs=raw_inputs, diagnostics=invalid_diagnostics)
    if missing_diagnostics:
        return _blocked_step(gate, raw_inputs=raw_inputs, diagnostics=missing_diagnostics)

    bars_compression_only_typed: bool = bars_compression_only  # type: ignore[assignment]
    ends_cut_perpendicular_typed: bool = ends_cut_perpendicular  # type: ignore[assignment]
    bars_coaxial_typed: bool = bars_coaxial  # type: ignore[assignment]
    member_has_confinement_typed: bool = member_has_confinement  # type: ignore[assignment]
    assert end_face_deviation_deg is not None
    assert axial_misalignment_deg is not None

    intermediates: Dict[str, float] = {
        "bars_compression_only": 1.0 if bars_compression_only_typed else 0.0,
        "ends_cut_perpendicular": 1.0 if ends_cut_perpendicular_typed else 0.0,
        "bars_coaxial": 1.0 if bars_coaxial_typed else 0.0,
        "member_has_confinement": 1.0 if member_has_confinement_typed else 0.0,
        "end_face_deviation_deg": end_face_deviation_deg,
        "max_end_face_deviation_deg": BG_SPLICE_BEARING_MAX_END_FACE_DEVIATION_DEG,
        "axial_misalignment_deg": axial_misalignment_deg,
        "max_misalignment_deg": BG_SPLICE_BEARING_MAX_MISALIGNMENT_DEG,
    }

    def _fail(code: str, message: str, field_name: str) -> CalculationTraceStep:
        return _fail_step(
            gate,
            raw_inputs=raw_inputs,
            intermediates=intermediates,
            final_result=None,
            unit="deg",
            diagnostic=EngineeringDiagnostic(
                code=code,
                severity=DiagnosticSeverity.ERROR,
                message=message,
                rule_id=rule_id,
                field_name=field_name,
            ),
        )

    # Clause 9-21-4-6-1 conditions
    if not bars_compression_only_typed:
        return _fail(
            "BEARING_SPLICE_REQUIRES_COMPRESSION_ONLY",
            (
                "FAIL: a bearing splice is permitted only for bars under "
                "compression alone (Clause 9-21-4-6-1); these bars are not "
                "compression-only."
            ),
            "bars_compression_only",
        )
    if not ends_cut_perpendicular_typed:
        return _fail(
            "BEARING_SPLICE_ENDS_NOT_PERPENDICULAR",
            (
                "FAIL: bearing-splice bar ends must be cut perpendicular to "
                "the bar axis (Clause 9-21-4-6-1)."
            ),
            "ends_cut_perpendicular",
        )
    if not bars_coaxial_typed:
        return _fail(
            "BEARING_SPLICE_NOT_COAXIAL",
            (
                "FAIL: the two spliced bars must be coaxial (e.g. via a ring) "
                "for a bearing splice (Clause 9-21-4-6-1)."
            ),
            "bars_coaxial",
        )

    # Clause 9-21-4-6-2 condition
    if not member_has_confinement_typed:
        return _fail(
            "BEARING_SPLICE_NO_CONFINEMENT",
            (
                "FAIL: a bearing splice is permitted only in members with "
                "confinement (خاموت; tied / spiral / دورگیر) per Clause "
                "9-21-4-6-2."
            ),
            "member_has_confinement",
        )

    # Clause 9-21-4-6-3 angular limits
    if end_face_deviation_deg > BG_SPLICE_BEARING_MAX_END_FACE_DEVIATION_DEG:
        return _fail(
            "BEARING_SPLICE_END_FACE_DEVIATION_EXCEEDED",
            (
                f"FAIL: bar-end face deviation {end_face_deviation_deg} deg > "
                f"{BG_SPLICE_BEARING_MAX_END_FACE_DEVIATION_DEG} deg maximum per "
                "Clause 9-21-4-6-3."
            ),
            "end_face_deviation_deg",
        )
    if axial_misalignment_deg > BG_SPLICE_BEARING_MAX_MISALIGNMENT_DEG:
        return _fail(
            "BEARING_SPLICE_MISALIGNMENT_EXCEEDED",
            (
                f"FAIL: axial misalignment {axial_misalignment_deg} deg > "
                f"{BG_SPLICE_BEARING_MAX_MISALIGNMENT_DEG} deg maximum per Clause "
                "9-21-4-6-3."
            ),
            "axial_misalignment_deg",
        )

    return CalculationTraceStep.from_rule(
        rule,
        normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=None,
        unit="deg",
        outcome=EvaluationOutcome.PASS,
        diagnostics=(),
        message=(
            "PASS: bearing splice of compression-only bars with perpendicular "
            "coaxial ends in a confined member, end-face deviation "
            f"{end_face_deviation_deg} deg <= "
            f"{BG_SPLICE_BEARING_MAX_END_FACE_DEVIATION_DEG} deg and axial "
            f"misalignment {axial_misalignment_deg} deg <= "
            f"{BG_SPLICE_BEARING_MAX_MISALIGNMENT_DEG} deg, satisfies Clause "
            "9-21-4-6."
        ),
    )
