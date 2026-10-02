"""Mabhas 9 verified minimum flexural reinforcement evaluator (BG-FLEX-MIN-001)."""

from __future__ import annotations

import math
from typing import Dict, List, Optional

from beamgenius.domain.enums import (
    DiagnosticSeverity,
    EvaluationOutcome,
    FlangeCondition,
    JurisdictionMode,
    OverallComplianceStatus,
    SectionType,
)
from beamgenius.domain.models import (
    BeamGeometry,
    ConcreteMaterial,
    RebarMaterial,
)
from beamgenius.domain.trace import (
    BeamComplianceReport,
    CalculationTraceStep,
    EngineeringDiagnostic,
    ScalarInputValue,
    select_dominant_outcome,
)
from beamgenius.domain.validation import (
    resolve_effective_depth,
    validate_beam_geometry,
    validate_concrete_material,
    validate_rebar_material,
)
from beamgenius.registry.catalog import (
    RULE_BG_FLEX_DOUBLY_REINF_PENDING,
    RULE_BG_FLEX_FLANGE_WIDTH_PENDING,
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
    as_provided_mm2: Optional[float] = None,
    as_compression_mm2: Optional[float] = None,
    require_design_inputs: bool = False,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate Mabhas 9 flexural resistance workflow (`BG-MABHAS9-FLEX-CAP-BLOCKED`).

    Governance & Execution Order:
    1. Enforces jurisdiction gate (`MABHAS_9_COMPLIANCE` required; otherwise returns
       `EvaluationOutcome.JURISDICTION_BLOCKED`).
    2. Validates section geometry (`bw_mm`, `h_mm`, flange consistency), concrete
       (`fc_prime_mpa > 0`), steel (`fy_mpa > 0`), `as_provided_mm2`, `as_compression_mm2`,
       `mu_nmm`, and resolves effective depth `d` via Phase 1 precedence
       (`EXPLICIT_D -> ACTUAL_REBAR_GEOMETRY -> UNRESOLVED`, never `h - 65` or `h - 90`).
       Returns `EvaluationOutcome.INVALID_INPUT` when any physical input or `d` is invalid.
    3. Explicitly blocks T- and L-sections (`FLANGED_SECTION_FLEXURAL_RESISTANCE_UNVERIFIED`)
       without silently falling back to rectangular behavior.
    4. Explicitly blocks doubly reinforced sections with compression reinforcement
       (`DOUBLY_REINFORCED_FLEXURAL_RESISTANCE_UNVERIFIED`) without silently ignoring `As'`.
    5. Returns `EvaluationOutcome.UNVERIFIED_RULE_BLOCKED` for rectangular singly
       reinforced sections until the Mabhas 9 stress-block parameters
       (`BG-FLEX-STRESS-BLOCK-PENDING`), resistance factor (`BG-FLEX-PHI-FACTOR-PENDING`),
       and strain/ductility limits (`BG-FLEX-STRAIN-LIMIT-PENDING`) are visually verified
       from the Mabhas 9 source PDF and registered in `docs/VERIFIED_RULES.md`.
    """
    rule_id = RULE_BG_MABHAS9_FLEX_CAP_BLOCKED.rule_id
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
        "as_compression_mm2": as_compression_mm2,
        "mu_nmm": mu_nmm,
    }

    # 1. Jurisdiction check
    if jurisdiction_mode != JurisdictionMode.MABHAS_9_COMPLIANCE:
        jur_diag = EngineeringDiagnostic(
            code="JURISDICTION_MISMATCH_BLOCKED",
            severity=DiagnosticSeverity.BLOCK,
            message=(
                f"Rule '{rule_id}' belongs to jurisdiction "
                f"'{JurisdictionMode.MABHAS_9_COMPLIANCE.value}' and cannot execute "
                f"in '{jurisdiction_mode.value}'."
            ),
            rule_id=rule_id,
        )
        return CalculationTraceStep.from_rule(
            RULE_BG_MABHAS9_FLEX_CAP_BLOCKED,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="N*mm",
            outcome=EvaluationOutcome.JURISDICTION_BLOCKED,
            diagnostics=(jur_diag,),
            message=jur_diag.message,
        )

    # 2. Deterministic physical input & effective-depth validation
    diagnostics: List[EngineeringDiagnostic] = []
    diagnostics.extend(
        validate_beam_geometry(geometry, require_effective_depth=False, rule_id=rule_id)
    )
    diagnostics.extend(validate_concrete_material(concrete, rule_id=rule_id))
    diagnostics.extend(
        validate_rebar_material(
            rebar,
            enforce_mabhas9_flex_min_fy_limit=False,
            rule_id=rule_id,
        )
    )

    if as_provided_mm2 is not None and (
        not math.isfinite(as_provided_mm2) or as_provided_mm2 <= 0.0
    ):
        diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_AS_PROVIDED",
                severity=DiagnosticSeverity.ERROR,
                message=f"as_provided_mm2 must be finite and > 0 mm^2, got {as_provided_mm2}.",
                rule_id=rule_id,
                field_name="as_provided_mm2",
            )
        )
    elif require_design_inputs and resolved_as_provided is None:
        diagnostics.append(
            EngineeringDiagnostic(
                code="MISSING_PROVIDED_TENSILE_REINFORCEMENT",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    "Provided tensile reinforcement area (as_provided_mm2 or "
                    "geometry.tension_rebar_groups) is required for flexural resistance evaluation."
                ),
                rule_id=rule_id,
                field_name="as_provided_mm2",
            )
        )

    if as_compression_mm2 is not None and (
        not math.isfinite(as_compression_mm2) or as_compression_mm2 < 0.0
    ):
        diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_AS_COMPRESSION",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    f"as_compression_mm2 must be finite and >= 0 mm^2 when supplied, "
                    f"got {as_compression_mm2}."
                ),
                rule_id=rule_id,
                field_name="as_compression_mm2",
            )
        )

    if mu_nmm is not None and (not math.isfinite(mu_nmm) or mu_nmm < 0.0):
        diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_FACTORED_MOMENT_MU",
                severity=DiagnosticSeverity.ERROR,
                message=f"Factored moment mu_nmm must be finite and >= 0 N*mm, got {mu_nmm}.",
                rule_id=rule_id,
                field_name="mu_nmm",
            )
        )
    elif require_design_inputs and mu_nmm is None:
        diagnostics.append(
            EngineeringDiagnostic(
                code="MISSING_FACTORED_MOMENT_MU",
                severity=DiagnosticSeverity.ERROR,
                message="Factored moment mu_nmm (>= 0 N*mm) is required for flexural resistance evaluation.",
                rule_id=rule_id,
                field_name="mu_nmm",
            )
        )

    if diagnostics:
        return CalculationTraceStep.from_rule(
            RULE_BG_MABHAS9_FLEX_CAP_BLOCKED,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="N*mm",
            outcome=EvaluationOutcome.INVALID_INPUT,
            diagnostics=diagnostics,
            message=diagnostics[0].message,
        )

    d_res = resolve_effective_depth(geometry, rule_id=rule_id)
    if not d_res.is_valid or d_res.d_mm is None:
        return CalculationTraceStep.from_rule(
            RULE_BG_MABHAS9_FLEX_CAP_BLOCKED,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="N*mm",
            outcome=EvaluationOutcome.INVALID_INPUT,
            diagnostics=d_res.diagnostics,
            message=(
                d_res.diagnostics[0].message
                if d_res.diagnostics
                else "Failed to resolve effective depth d for flexural resistance check."
            ),
        )

    raw_inputs["d_effective_mm"] = d_res.d_mm
    raw_inputs["d_resolution_source"] = d_res.source

    # 3. Configuration gate: T- and L-sections must never silently fall back to rectangular
    if geometry.section_type in (SectionType.T_SECTION, SectionType.L_SECTION):
        flanged_diag = EngineeringDiagnostic(
            code="FLANGED_SECTION_FLEXURAL_RESISTANCE_UNVERIFIED",
            severity=DiagnosticSeverity.BLOCK,
            message=(
                f"Flexural resistance is blocked for {geometry.section_type.value} "
                f"({RULE_BG_FLEX_FLANGE_WIDTH_PENDING.rule_id}): Mabhas 9 effective flange "
                "width and flanged section flexural capacity rules are not yet visually "
                "verified in docs/VERIFIED_RULES.md. Silent fallback to rectangular "
                "behavior is prohibited."
            ),
            rule_id=rule_id,
            field_name="section_type",
            required_verification=(
                "Visually verify Mabhas 9 T- and L-beam effective flange width and "
                "flanged flexural resistance clauses and register in docs/VERIFIED_RULES.md."
            ),
        )
        return CalculationTraceStep.from_rule(
            RULE_BG_MABHAS9_FLEX_CAP_BLOCKED,
            normalized_inputs=raw_inputs,
            intermediate_values={"d_effective_mm": d_res.d_mm},
            final_result=None,
            unit="N*mm",
            outcome=EvaluationOutcome.UNVERIFIED_RULE_BLOCKED,
            diagnostics=(flanged_diag,),
            message=flanged_diag.message,
        )

    # 4. Configuration gate: Doubly reinforced sections must never silently ignore As'
    if as_compression_mm2 is not None and as_compression_mm2 > 0.0:
        doubly_diag = EngineeringDiagnostic(
            code="DOUBLY_REINFORCED_FLEXURAL_RESISTANCE_UNVERIFIED",
            severity=DiagnosticSeverity.BLOCK,
            message=(
                f"Flexural resistance is blocked for doubly reinforced section with "
                f"as_compression_mm2 = {as_compression_mm2} mm^2 "
                f"({RULE_BG_FLEX_DOUBLY_REINF_PENDING.rule_id}): Mabhas 9 compression "
                "reinforcement flexural capacity rules are not yet visually verified in "
                "docs/VERIFIED_RULES.md."
            ),
            rule_id=rule_id,
            field_name="as_compression_mm2",
            required_verification=(
                "Visually verify Mabhas 9 doubly reinforced beam flexural capacity "
                "clauses and register in docs/VERIFIED_RULES.md."
            ),
        )
        return CalculationTraceStep.from_rule(
            RULE_BG_MABHAS9_FLEX_CAP_BLOCKED,
            normalized_inputs=raw_inputs,
            intermediate_values={
                "d_effective_mm": d_res.d_mm,
                "as_compression_mm2": as_compression_mm2,
            },
            final_result=None,
            unit="N*mm",
            outcome=EvaluationOutcome.UNVERIFIED_RULE_BLOCKED,
            diagnostics=(doubly_diag,),
            message=doubly_diag.message,
        )

    # 5. Singly reinforced rectangular beam: evaluate central verification gate
    return build_blocked_workflow_trace(
        rule_id,
        active_jurisdiction=jurisdiction_mode,
        normalized_inputs=raw_inputs,
        additional_context=(
            "Mabhas 9 flexural capacity calculation cannot execute until Mabhas 9 "
            "flexural resistance rules (BG-FLEX-STRESS-BLOCK-PENDING, "
            "BG-FLEX-PHI-FACTOR-PENDING, BG-FLEX-STRAIN-LIMIT-PENDING) are visually "
            "verified from the Mabhas 9 source PDF and added to docs/VERIFIED_RULES.md."
        ),
        unit="N*mm",
    )


def run_mabhas9_flexural_workflow(
    geometry: BeamGeometry,
    concrete: ConcreteMaterial,
    rebar: RebarMaterial,
    *,
    as_provided_mm2: Optional[float] = None,
    mu_nmm: Optional[float] = None,
    as_required_by_analysis_mm2: Optional[float] = None,
    as_compression_mm2: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> BeamComplianceReport:
    """Run the deterministic Mabhas 9 flexural evaluation workflow (Phase 2B).

    Executes:
    1. Verified `BG-FLEX-MIN-001` (`evaluate_minimum_flexural_reinforcement`)
    2. Flexural capacity evaluation (`evaluate_mabhas9_flexural_capacity` with
       `require_design_inputs=True`)

    Aggregates both trace steps under the Anti-Misleading-PASS dominance hierarchy
    (`INVALID_INPUT > FAIL > BLOCKED > PARTIAL > PASS`). Never returns `PASS` when
    flexural capacity rules are `UNVERIFIED_RULE_BLOCKED`.
    """
    min_step = evaluate_minimum_flexural_reinforcement(
        geometry,
        concrete,
        rebar,
        as_provided_mm2=as_provided_mm2,
        as_required_by_analysis_mm2=as_required_by_analysis_mm2,
        require_provided_rebar=True,
        jurisdiction_mode=jurisdiction_mode,
    )
    cap_step = evaluate_mabhas9_flexural_capacity(
        geometry,
        concrete,
        rebar,
        mu_nmm=mu_nmm,
        as_provided_mm2=as_provided_mm2,
        as_compression_mm2=as_compression_mm2,
        require_design_inputs=True,
        jurisdiction_mode=jurisdiction_mode,
    )

    steps = (min_step, cap_step)
    diagnostics = (*min_step.diagnostics, *cap_step.diagnostics)
    outcomes_by_rule: Dict[str, EvaluationOutcome] = {}
    for step in steps:
        if step.rule_id in outcomes_by_rule:
            outcomes_by_rule[step.rule_id] = select_dominant_outcome(
                outcomes_by_rule[step.rule_id], step.outcome
            )
        else:
            outcomes_by_rule[step.rule_id] = step.outcome

    outcomes_set = {step.outcome for step in steps}
    if EvaluationOutcome.INVALID_INPUT in outcomes_set:
        overall_status = OverallComplianceStatus.INVALID_INPUT
    elif EvaluationOutcome.FAIL in outcomes_set:
        overall_status = OverallComplianceStatus.FAIL
    elif (
        EvaluationOutcome.UNVERIFIED_RULE_BLOCKED in outcomes_set
        or EvaluationOutcome.JURISDICTION_BLOCKED in outcomes_set
    ):
        overall_status = OverallComplianceStatus.BLOCKED
    elif (
        EvaluationOutcome.COMPUTED in outcomes_set
        or EvaluationOutcome.NOT_APPLICABLE in outcomes_set
    ):
        overall_status = OverallComplianceStatus.PARTIAL
    else:
        overall_status = OverallComplianceStatus.PASS

    return BeamComplianceReport(
        overall_status=overall_status,
        jurisdiction_mode=jurisdiction_mode,
        trace_steps=steps,
        diagnostics=diagnostics,
        outcomes_by_rule=outcomes_by_rule,
    )
