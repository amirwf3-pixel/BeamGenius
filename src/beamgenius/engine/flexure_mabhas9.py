"""Mabhas 9 verified minimum flexural reinforcement evaluator (BG-FLEX-MIN-001)."""

from __future__ import annotations

import math
from typing import Dict, List, Optional

from beamgenius.domain.enums import (
    DiagnosticSeverity,
    EvaluationOutcome,
    FlangeCondition,
    JurisdictionMode,
    SectionType,
)
from beamgenius.domain.models import (
    BeamGeometry,
    ConcreteMaterial,
    RebarMaterial,
)
from beamgenius.domain.trace import (
    CalculationTraceStep,
    EngineeringDiagnostic,
    ScalarInputValue,
)
from beamgenius.domain.validation import (
    resolve_effective_depth,
    validate_beam_geometry,
    validate_concrete_material,
    validate_rebar_material,
)
from beamgenius.registry.catalog import (
    RULE_BG_FLEX_MIN_001,
    RULE_BG_MABHAS9_FLEX_CAP_BLOCKED,
)
from beamgenius.registry.gatekeeper import (
    build_blocked_workflow_trace,
    evaluate_rule_gate,
)

# Constants tied to BG-FLEX-MIN-001 (Mabhas 9 Clause 9-11-5-1-1 / 9-11-5-1-2 / 9-11-5-1-3)
BG_FLEX_MIN_001_SQRT_FC_COEFF: float = 0.25
BG_FLEX_MIN_001_CONST_STRESS_MPA: float = 1.4
BG_FLEX_MIN_001_WAIVER_FACTOR: float = 4.0 / 3.0


def evaluate_minimum_flexural_reinforcement(
    geometry: BeamGeometry,
    concrete: ConcreteMaterial,
    rebar: RebarMaterial,
    *,
    as_provided_mm2: Optional[float] = None,
    as_required_by_analysis_mm2: Optional[float] = None,
    require_provided_rebar: bool = False,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate Mabhas 9 Minimum Flexural Reinforcement (BG-FLEX-MIN-001).

    Formula (Mabhas 9, PDF p. 220, Printed p. 199, Clause 9-11-5-1-1 / 9-11-5-1-2):
        As,min = max(0.25 * sqrt(f'c) * bw * d / fy, 1.4 * bw * d / fy)

    Constraints & Governance:
    - Enforces fy <= 550 MPa (returns INVALID_INPUT if fy > 550 MPa).
    - Blocks T/L sections with flange in tension (UNVERIFIED_RULE_BLOCKED) because
      the flange-in-tension effective-width rule is not yet in docs/VERIFIED_RULES.md.
    - Evaluates Clause 9-11-5-1-3 waiver (As,provided >= 4/3 * As,required_by_analysis)
      only when `as_required_by_analysis_mm2` is explicitly supplied, while always
      retaining the calculated `As,min` in `final_result` and `intermediate_values`.
    """
    rule_id = RULE_BG_FLEX_MIN_001.rule_id
    resolved_as_provided = (
        as_provided_mm2
        if as_provided_mm2 is not None
        else geometry.provided_tensile_area_mm2
    )

    raw_inputs: Dict[str, ScalarInputValue] = {
        "bw_mm": geometry.bw_mm,
        "h_mm": geometry.h_mm,
        "d_effective_mm": geometry.d_effective_mm,
        "section_type": geometry.section_type.value,
        "flange_condition": geometry.flange_condition.value,
        "fc_prime_mpa": concrete.fc_prime_mpa,
        "fy_mpa": rebar.fy_mpa,
        "as_provided_mm2": resolved_as_provided,
        "as_required_by_analysis_mm2": as_required_by_analysis_mm2,
    }

    # 1. Central Gatekeeper check
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm^2")

    # 2. Deterministic input validation
    diagnostics: List[EngineeringDiagnostic] = []
    diagnostics.extend(
        validate_beam_geometry(geometry, require_effective_depth=False, rule_id=rule_id)
    )
    diagnostics.extend(validate_concrete_material(concrete, rule_id=rule_id))
    diagnostics.extend(
        validate_rebar_material(
            rebar,
            enforce_mabhas9_flex_min_fy_limit=True,
            rule_id=rule_id,
        )
    )

    if as_provided_mm2 is not None and (
        not math.isfinite(as_provided_mm2) or as_provided_mm2 < 0.0
    ):
        diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_AS_PROVIDED",
                severity=DiagnosticSeverity.ERROR,
                message=f"as_provided_mm2 must be finite and >= 0 mm^2, got {as_provided_mm2}.",
                rule_id=rule_id,
                field_name="as_provided_mm2",
            )
        )

    if as_required_by_analysis_mm2 is not None and (
        not math.isfinite(as_required_by_analysis_mm2) or as_required_by_analysis_mm2 <= 0.0
    ):
        diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_AS_REQUIRED_BY_ANALYSIS",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    "as_required_by_analysis_mm2 must be finite and > 0 mm^2 when supplied, "
                    f"got {as_required_by_analysis_mm2}."
                ),
                rule_id=rule_id,
                field_name="as_required_by_analysis_mm2",
            )
        )

    if diagnostics:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="mm^2",
            outcome=EvaluationOutcome.INVALID_INPUT,
            diagnostics=diagnostics,
            message=diagnostics[0].message,
        )

    # 3. Check T/L section with flange in tension BEFORE resolving rectangular web formula
    if (
        geometry.section_type in (SectionType.T_SECTION, SectionType.L_SECTION)
        and geometry.flange_condition == FlangeCondition.FLANGE_IN_TENSION
    ):
        block_diag = EngineeringDiagnostic(
            code="FLANGE_IN_TENSION_EFFECTIVE_WIDTH_UNVERIFIED",
            severity=DiagnosticSeverity.BLOCK,
            message=(
                f"Rule '{rule_id}' is blocked for {geometry.section_type.value} with "
                "FLANGE_IN_TENSION: the applicable Mabhas 9 effective-width provision "
                "for T/L sections with the flange in tension is not yet verified in "
                "docs/VERIFIED_RULES.md."
            ),
            rule_id=rule_id,
            field_name="flange_condition",
            required_verification=(
                "Visually verify the Mabhas 9 effective-width provision for T/L sections "
                "with flange in tension and register it in docs/VERIFIED_RULES.md."
            ),
        )
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="mm^2",
            outcome=EvaluationOutcome.UNVERIFIED_RULE_BLOCKED,
            diagnostics=(block_diag,),
            message=block_diag.message,
        )

    # 4. Resolve effective depth d (respecting precedence rule; never using h-65 / h-90)
    d_res = resolve_effective_depth(geometry, rule_id=rule_id)
    if not d_res.is_valid or d_res.d_mm is None:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="mm^2",
            outcome=EvaluationOutcome.INVALID_INPUT,
            diagnostics=d_res.diagnostics,
            message=(
                d_res.diagnostics[0].message
                if d_res.diagnostics
                else "Failed to resolve effective depth d."
            ),
        )

    if require_provided_rebar and resolved_as_provided is None:
        missing_as_diag = EngineeringDiagnostic(
            code="MISSING_PROVIDED_TENSILE_REINFORCEMENT",
            severity=DiagnosticSeverity.ERROR,
            message=(
                "Provided tensile reinforcement area (as_provided_mm2 or "
                "geometry.tension_rebar_groups) is required for compliance checking."
            ),
            rule_id=rule_id,
            field_name="as_provided_mm2",
        )
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="mm^2",
            outcome=EvaluationOutcome.INVALID_INPUT,
            diagnostics=(missing_as_diag,),
            message=missing_as_diag.message,
        )

    d_mm = d_res.d_mm
    raw_inputs["d_effective_mm"] = d_mm
    raw_inputs["d_resolution_source"] = d_res.source

    # 5. Execute verified Mabhas 9 minimum flexural reinforcement formula
    sqrt_fc = math.sqrt(concrete.fc_prime_mpa)
    term_1_mm2 = (
        BG_FLEX_MIN_001_SQRT_FC_COEFF * sqrt_fc * geometry.bw_mm * d_mm / rebar.fy_mpa
    )
    term_2_mm2 = BG_FLEX_MIN_001_CONST_STRESS_MPA * geometry.bw_mm * d_mm / rebar.fy_mpa
    as_min_mm2 = max(term_1_mm2, term_2_mm2)

    intermediates: Dict[str, float] = {
        "d_effective_mm": d_mm,
        "sqrt_fc_mpa": sqrt_fc,
        "as_min_term_1_mm2": term_1_mm2,
        "as_min_term_2_mm2": term_2_mm2,
        "as_min_mm2": as_min_mm2,
    }

    if as_required_by_analysis_mm2 is not None:
        waiver_threshold_mm2 = BG_FLEX_MIN_001_WAIVER_FACTOR * as_required_by_analysis_mm2
        intermediates["as_required_by_analysis_mm2"] = as_required_by_analysis_mm2
        intermediates["waiver_threshold_4_3_as_req_mm2"] = waiver_threshold_mm2

    if resolved_as_provided is None:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=as_min_mm2,
            unit="mm^2",
            outcome=EvaluationOutcome.COMPUTED,
            diagnostics=(),
            message=f"Computed As,min = {as_min_mm2:.4f} mm^2 under BG-FLEX-MIN-001.",
        )

    intermediates["as_provided_mm2"] = resolved_as_provided

    # 6. Clause 9-11-5-1-3 waiver check (only when as_required_by_analysis_mm2 is supplied)
    if as_required_by_analysis_mm2 is not None:
        waiver_threshold_mm2 = intermediates["waiver_threshold_4_3_as_req_mm2"]
        if resolved_as_provided >= waiver_threshold_mm2:
            waiver_diag = EngineeringDiagnostic(
                code="CLAUSE_9_11_5_1_3_WAIVER_APPLIED",
                severity=DiagnosticSeverity.INFO,
                message=(
                    f"Clause 9-11-5-1-3 waiver satisfied: As,provided ({resolved_as_provided:.4f} mm^2) "
                    f">= 4/3 * As,required_by_analysis ({waiver_threshold_mm2:.4f} mm^2). "
                    f"Retained As,min = {as_min_mm2:.4f} mm^2 in trace."
                ),
                rule_id=rule_id,
            )
            return CalculationTraceStep.from_rule(
                gate.rule,
                normalized_inputs=raw_inputs,
                intermediate_values=intermediates,
                final_result=as_min_mm2,
                unit="mm^2",
                outcome=EvaluationOutcome.EXEMPT,
                diagnostics=(waiver_diag,),
                message=waiver_diag.message,
            )

    # 7. Standard As,provided >= As,min comparison
    if resolved_as_provided >= as_min_mm2:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=as_min_mm2,
            unit="mm^2",
            outcome=EvaluationOutcome.PASS,
            diagnostics=(),
            message=(
                f"PASS: As,provided ({resolved_as_provided:.4f} mm^2) >= "
                f"As,min ({as_min_mm2:.4f} mm^2)."
            ),
        )

    fail_diag = EngineeringDiagnostic(
        code="INSUFFICIENT_MINIMUM_FLEXURAL_REINFORCEMENT",
        severity=DiagnosticSeverity.ERROR,
        message=(
            f"FAIL: As,provided ({resolved_as_provided:.4f} mm^2) < "
            f"As,min ({as_min_mm2:.4f} mm^2) required by BG-FLEX-MIN-001."
        ),
        rule_id=rule_id,
        field_name="as_provided_mm2",
    )
    return CalculationTraceStep.from_rule(
        gate.rule,
        normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=as_min_mm2,
        unit="mm^2",
        outcome=EvaluationOutcome.FAIL,
        diagnostics=(fail_diag,),
        message=fail_diag.message,
    )


def evaluate_mabhas9_flexural_capacity(
    geometry: BeamGeometry,
    concrete: ConcreteMaterial,
    rebar: RebarMaterial,
    *,
    mu_nmm: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Explicitly blocked workflow for Mabhas 9 flexural capacity/resistance.

    Returns UNVERIFIED_RULE_BLOCKED until Mabhas 9 stress-block parameters,
    material resistance factors, and strain limits are verified in
    docs/VERIFIED_RULES.md.
    """
    return build_blocked_workflow_trace(
        RULE_BG_MABHAS9_FLEX_CAP_BLOCKED.rule_id,
        active_jurisdiction=jurisdiction_mode,
        normalized_inputs={
            "bw_mm": geometry.bw_mm,
            "h_mm": geometry.h_mm,
            "d_effective_mm": geometry.d_effective_mm,
            "fc_prime_mpa": concrete.fc_prime_mpa,
            "fy_mpa": rebar.fy_mpa,
            "mu_nmm": mu_nmm,
        },
        additional_context=(
            "Mabhas 9 flexural capacity calculation cannot execute until Mabhas 9 "
            "flexural resistance rules are verified and added to docs/VERIFIED_RULES.md."
        ),
    )
