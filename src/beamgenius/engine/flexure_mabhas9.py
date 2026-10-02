"""Mabhas 9 verified flexural reinforcement and resistance evaluators.

Verified Rules Implemented (docs/VERIFIED_RULES.md):
- BG-FLEX-MIN-001: Minimum Flexural Reinforcement (Clauses 9-11-5-1-1 / 9-11-5-1-2 / 9-11-5-1-3)
- BG-FLEX-STRESS-BLOCK: Equivalent Rectangular Compression Stress-Block Parameters (Clauses 9-8-2-2-6 / 9-8-2-2-7)
- BG-FLEX-STRAIN-LIMIT: Flexural Strain Compatibility and Tension-Controlled Beam Ductility Limit (Clauses 9-8-2-2-2 / 9-8-2-2-3 / 9-7-4-2 / 9-11-2-3)
- BG-FLEX-PHI-FACTOR: Flexural Strength Reduction Factor phi (Clauses 9-7-4-1..9-7-4-4, Table 9-7-2)
- BG-FLEX-RECT-SINGLY-001: Rectangular Singly-Reinforced Beam Flexural Resistance (Clauses 9-8-1-4, 9-8-2-2, 9-11-2-3)
- BG-FLEX-TBEAM-B-EFF-001: Non-Prestressed T-Beam and L-Beam Effective Compression Flange Width (Clauses 9-6-3-3-1, Table 9-6-1, 9-6-3-3-2, 9-11-2-5)

Explicitly Blocked Unverified Flexural Paths:
- BG-FLEX-RECT-DOUBLY-001: Doubly-Reinforced Rectangular Beam Flexural Resistance (VERIFY_PENDING)
- BG-FLEX-TBEAM-CAP-001: T-Beam Flanged Flexural Resistance (VERIFY_PENDING)
- BG-FLEX-LBEAM-CAP-001: L-Beam Flanged Flexural Resistance (VERIFY_PENDING)
"""

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
    RULE_BG_FLEX_LBEAM_CAP_001,
    RULE_BG_FLEX_MIN_001,
    RULE_BG_FLEX_PHI_FACTOR,
    RULE_BG_FLEX_RECT_DOUBLY_001,
    RULE_BG_FLEX_RECT_SINGLY_001,
    RULE_BG_FLEX_STRAIN_LIMIT,
    RULE_BG_FLEX_STRESS_BLOCK,
    RULE_BG_FLEX_TBEAM_B_EFF_001,
    RULE_BG_FLEX_TBEAM_CAP_001,
)
from beamgenius.registry.gatekeeper import evaluate_rule_gate

# ============================================================================
# VERIFIED CONSTANTS — MABHAS 9 (1399)
# ============================================================================

# BG-FLEX-MIN-001 (Mabhas 9 Clause 9-11-5-1-1 / 9-11-5-1-2 / 9-11-5-1-3)
BG_FLEX_MIN_001_SQRT_FC_COEFF: float = 0.25
BG_FLEX_MIN_001_CONST_STRESS_MPA: float = 1.4
BG_FLEX_MIN_001_WAIVER_FACTOR: float = 4.0 / 3.0

# Mabhas 9 Clause 9-3-3-3 structural concrete compressive strength bounds
MABHAS9_FC_PRIME_MIN_MPA: float = 20.0
MABHAS9_FC_PRIME_MAX_MPA: float = 70.0

# BG-FLEX-STRESS-BLOCK (Mabhas 9 Clauses 9-8-2-2-6 & 9-8-2-2-7, Eqs. 9-8-2, 9-8-3-الف, 9-8-3-ب, 9-8-4)
BG_FLEX_BETA1_MAX: float = 0.85
BG_FLEX_BETA1_MIN: float = 0.65
BG_FLEX_BETA1_THRESHOLD_FC_MPA: float = 28.0
BG_FLEX_BETA1_STEP_COEFF: float = 0.05
BG_FLEX_BETA1_STEP_DIVISOR_MPA: float = 7.0

BG_FLEX_ALPHA0_DEFAULT: float = 0.85
BG_FLEX_ALPHA0_MIN: float = 0.75
BG_FLEX_ALPHA0_THRESHOLD_FC_MPA: float = 55.0
BG_FLEX_ALPHA0_SLOPE_PER_MPA: float = 0.004

# BG-FLEX-STRAIN-LIMIT & BG-FLEX-PHI-FACTOR (Mabhas 9 Clauses 9-8-2-2-3, 9-7-4-2..9-7-4-4, Table 9-7-2, 9-11-2-3)
BG_FLEX_EPSILON_CU: float = 0.003
BG_FLEX_TENSION_CONTROLLED_DELTA_STRAIN: float = 0.003
BG_FLEX_PHI_TENSION_CONTROLLED: float = 0.90
BG_FLEX_PHI_COMPRESSION_SPIRAL: float = 0.75
BG_FLEX_PHI_COMPRESSION_OTHER: float = 0.65

# BG-FLEX-TBEAM-B-EFF-001 (Mabhas 9 Clauses 9-6-3-3-1, Table 9-6-1, 9-6-3-3-2)
BG_FLEX_TBEAM_OVERHANG_HF_MULT: float = 8.0
BG_FLEX_TBEAM_OVERHANG_SW_DIV: float = 2.0
BG_FLEX_TBEAM_OVERHANG_LN_DIV: float = 8.0

BG_FLEX_LBEAM_OVERHANG_HF_MULT: float = 6.0
BG_FLEX_LBEAM_OVERHANG_SW_DIV: float = 2.0
BG_FLEX_LBEAM_OVERHANG_LN_DIV: float = 12.0

BG_FLEX_ISOLATED_TBEAM_MIN_HF_BW_RATIO: float = 0.5
BG_FLEX_ISOLATED_TBEAM_MAX_BF_BW_RATIO: float = 4.0

_STRAIN_TOLERANCE: float = 1e-12
_MOMENT_REL_TOLERANCE: float = 1e-12


def _compute_alpha0_beta1(fc_prime_mpa: float) -> tuple[float, float]:
    """Compute verified Mabhas 9 stress-block parameters (alpha_0, beta_1)."""
    if fc_prime_mpa <= BG_FLEX_BETA1_THRESHOLD_FC_MPA:
        beta_1 = BG_FLEX_BETA1_MAX
    else:
        beta_1 = max(
            BG_FLEX_BETA1_MAX
            - BG_FLEX_BETA1_STEP_COEFF
            * (fc_prime_mpa - BG_FLEX_BETA1_THRESHOLD_FC_MPA)
            / BG_FLEX_BETA1_STEP_DIVISOR_MPA,
            BG_FLEX_BETA1_MIN,
        )

    if fc_prime_mpa <= BG_FLEX_ALPHA0_THRESHOLD_FC_MPA:
        alpha_0 = BG_FLEX_ALPHA0_DEFAULT
    else:
        alpha_0 = max(
            BG_FLEX_ALPHA0_DEFAULT
            - BG_FLEX_ALPHA0_SLOPE_PER_MPA
            * (fc_prime_mpa - BG_FLEX_ALPHA0_THRESHOLD_FC_MPA),
            BG_FLEX_ALPHA0_MIN,
        )

    return alpha_0, beta_1


def _compute_phi_and_regime(
    epsilon_t: float,
    epsilon_ty: float,
    *,
    is_spiral_transverse: bool = False,
) -> tuple[float, str]:
    """Compute verified Mabhas 9 flexural strength reduction factor phi and strain regime."""
    epsilon_t_tc = epsilon_ty + BG_FLEX_TENSION_CONTROLLED_DELTA_STRAIN
    phi_cc = (
        BG_FLEX_PHI_COMPRESSION_SPIRAL
        if is_spiral_transverse
        else BG_FLEX_PHI_COMPRESSION_OTHER
    )

    if epsilon_t <= epsilon_ty + _STRAIN_TOLERANCE:
        return phi_cc, "COMPRESSION_CONTROLLED"
    if epsilon_t >= epsilon_t_tc - _STRAIN_TOLERANCE:
        return BG_FLEX_PHI_TENSION_CONTROLLED, "TENSION_CONTROLLED"

    # Transition zone: Clause 9-7-4-4, Eqs. (9-7-10-الف) and (9-7-10-ب)
    delta_phi = BG_FLEX_PHI_TENSION_CONTROLLED - phi_cc
    phi = phi_cc + delta_phi * (
        (epsilon_t - epsilon_ty) / BG_FLEX_TENSION_CONTROLLED_DELTA_STRAIN
    )
    return phi, "TRANSITION_ZONE"


def _resolve_extreme_tension_depth_dt(
    geometry: BeamGeometry,
    d_effective_mm: float,
) -> float:
    """Resolve distance dt from extreme compression fiber to extreme tension reinforcement.

    For single-layer reinforcement or when only explicit d_effective_mm is given,
    dt == d_effective_mm. For multi-layer reinforcement with explicit centroids or
    cover/stirrup geometry, dt is the depth to the outermost tension layer (>= d).
    """
    if not geometry.tension_rebar_groups:
        return d_effective_mm

    if all(
        grp.centroid_from_tension_face_mm is not None
        for grp in geometry.tension_rebar_groups
    ):
        min_y = min(
            grp.centroid_from_tension_face_mm
            for grp in geometry.tension_rebar_groups
            if grp.centroid_from_tension_face_mm is not None
        )
        dt_candidate = geometry.h_mm - min_y
        if 0.0 < dt_candidate < geometry.h_mm:
            return max(dt_candidate, d_effective_mm)

    if geometry.clear_cover_mm is not None and geometry.stirrup_diameter_mm is not None:
        layer_1_groups = [
            grp for grp in geometry.tension_rebar_groups if grp.layer_index == 1
        ]
        if layer_1_groups:
            min_y = (
                geometry.clear_cover_mm
                + geometry.stirrup_diameter_mm
                + max(grp.bar_diameter_mm for grp in layer_1_groups) / 2.0
            )
            dt_candidate = geometry.h_mm - min_y
            if 0.0 < dt_candidate < geometry.h_mm:
                return max(dt_candidate, d_effective_mm)

    return d_effective_mm


def _validate_mabhas9_fc_bounds(
    concrete: ConcreteMaterial,
    *,
    rule_id: str,
) -> List[EngineeringDiagnostic]:
    """Validate Mabhas 9 Clause 9-3-3-3 structural concrete strength range (20 <= f'c <= 70 MPa)."""
    diagnostics: List[EngineeringDiagnostic] = []
    if concrete.fc_prime_mpa < MABHAS9_FC_PRIME_MIN_MPA:
        diagnostics.append(
            EngineeringDiagnostic(
                code="FC_BELOW_MABHAS9_MINIMUM",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    f"Concrete compressive strength fc_prime_mpa ({concrete.fc_prime_mpa} MPa) "
                    f"is below the Mabhas 9 Clause 9-3-3-3 minimum structural limit of "
                    f"{MABHAS9_FC_PRIME_MIN_MPA} MPa."
                ),
                rule_id=rule_id,
                field_name="fc_prime_mpa",
            )
        )
    elif concrete.fc_prime_mpa > MABHAS9_FC_PRIME_MAX_MPA:
        diagnostics.append(
            EngineeringDiagnostic(
                code="FC_EXCEEDS_MABHAS9_MAXIMUM",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    f"Concrete compressive strength fc_prime_mpa ({concrete.fc_prime_mpa} MPa) "
                    f"exceeds the Mabhas 9 Clause 9-3-3-3 maximum limit of "
                    f"{MABHAS9_FC_PRIME_MAX_MPA} MPa."
                ),
                rule_id=rule_id,
                field_name="fc_prime_mpa",
            )
        )
    return diagnostics


# ============================================================================
# 1. MINIMUM FLEXURAL REINFORCEMENT (BG-FLEX-MIN-001)
# ============================================================================


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


# ============================================================================
# 2. EQUIVALENT RECTANGULAR STRESS-BLOCK PARAMETERS (BG-FLEX-STRESS-BLOCK)
# ============================================================================


def evaluate_mabhas9_stress_block_parameters(
    concrete: ConcreteMaterial,
    *,
    c_mm: Optional[float] = None,
    enforce_code_fc_bounds: bool = True,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate Mabhas 9 equivalent rectangular concrete compression stress-block parameters.

    Rule ID: `BG-FLEX-STRESS-BLOCK`
    Source: Mabhas 9 (1399), PDF pp. 22-23, Printed pp. 113-114,
            Clauses 9-8-2-2-6 & 9-8-2-2-7, Eqs. (9-8-2), (9-8-3-الف), (9-8-3-ب), (9-8-4).
    """
    rule_id = RULE_BG_FLEX_STRESS_BLOCK.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "fc_prime_mpa": concrete.fc_prime_mpa,
        "c_mm": c_mm,
        "enforce_code_fc_bounds": enforce_code_fc_bounds,
    }

    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(
            normalized_inputs=raw_inputs, unit="dimensionless"
        )

    diagnostics: List[EngineeringDiagnostic] = []
    diagnostics.extend(validate_concrete_material(concrete, rule_id=rule_id))
    if not diagnostics and enforce_code_fc_bounds:
        diagnostics.extend(_validate_mabhas9_fc_bounds(concrete, rule_id=rule_id))

    if c_mm is not None and (not math.isfinite(c_mm) or c_mm <= 0.0):
        diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_NEUTRAL_AXIS_DEPTH",
                severity=DiagnosticSeverity.ERROR,
                message=f"Neutral-axis depth c_mm must be finite and > 0 mm, got {c_mm}.",
                rule_id=rule_id,
                field_name="c_mm",
            )
        )

    if diagnostics:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="dimensionless",
            outcome=EvaluationOutcome.INVALID_INPUT,
            diagnostics=diagnostics,
            message=diagnostics[0].message,
        )

    alpha_0, beta_1 = _compute_alpha0_beta1(concrete.fc_prime_mpa)
    intermediates: Dict[str, float] = {
        "alpha_0": alpha_0,
        "beta_1": beta_1,
    }
    if c_mm is not None:
        a_mm = beta_1 * c_mm
        intermediates["c_mm"] = c_mm
        intermediates["a_mm"] = a_mm

    return CalculationTraceStep.from_rule(
        gate.rule,
        normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=beta_1,
        unit="dimensionless",
        outcome=EvaluationOutcome.COMPUTED,
        diagnostics=(),
        message=(
            f"Computed Mabhas 9 stress-block parameters: alpha_0 = {alpha_0:.4f}, "
            f"beta_1 = {beta_1:.4f} for f'c = {concrete.fc_prime_mpa:.2f} MPa."
        ),
    )


# ============================================================================
# 3. FLEXURAL STRENGTH REDUCTION FACTOR PHI (BG-FLEX-PHI-FACTOR)
# ============================================================================


def evaluate_mabhas9_phi_factor(
    epsilon_t: float,
    rebar: RebarMaterial,
    *,
    is_spiral_transverse: bool = False,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate Mabhas 9 flexural strength reduction factor phi (`BG-FLEX-PHI-FACTOR`).

    Source: Mabhas 9 (1399), PDF pp. 16-18, Printed pp. 107-109,
            Clauses 9-7-4-1..9-7-4-4, Table 9-7-2, Eqs. (9-7-10-الف) & (9-7-10-ب).
    """
    rule_id = RULE_BG_FLEX_PHI_FACTOR.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "epsilon_t": epsilon_t,
        "fy_mpa": rebar.fy_mpa,
        "es_mpa": rebar.es_mpa,
        "is_spiral_transverse": is_spiral_transverse,
    }

    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(
            normalized_inputs=raw_inputs, unit="dimensionless"
        )

    diagnostics: List[EngineeringDiagnostic] = []
    diagnostics.extend(
        validate_rebar_material(
            rebar,
            enforce_mabhas9_flex_min_fy_limit=True,
            rule_id=rule_id,
        )
    )
    if not math.isfinite(epsilon_t) or epsilon_t < 0.0:
        diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_NET_TENSILE_STRAIN",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    f"Net tensile strain epsilon_t must be finite and >= 0, got {epsilon_t}."
                ),
                rule_id=rule_id,
                field_name="epsilon_t",
            )
        )

    if diagnostics:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="dimensionless",
            outcome=EvaluationOutcome.INVALID_INPUT,
            diagnostics=diagnostics,
            message=diagnostics[0].message,
        )

    epsilon_ty = rebar.fy_mpa / rebar.es_mpa
    epsilon_t_tc = epsilon_ty + BG_FLEX_TENSION_CONTROLLED_DELTA_STRAIN
    phi, regime = _compute_phi_and_regime(
        epsilon_t,
        epsilon_ty,
        is_spiral_transverse=is_spiral_transverse,
    )
    raw_inputs["strain_regime"] = regime

    intermediates: Dict[str, float] = {
        "epsilon_t": epsilon_t,
        "epsilon_ty": epsilon_ty,
        "epsilon_t_tension_controlled_limit": epsilon_t_tc,
        "phi": phi,
    }

    return CalculationTraceStep.from_rule(
        gate.rule,
        normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=phi,
        unit="dimensionless",
        outcome=EvaluationOutcome.COMPUTED,
        diagnostics=(),
        message=(
            f"Computed Mabhas 9 flexural resistance factor phi = {phi:.4f} "
            f"({regime}, epsilon_t = {epsilon_t:.6f}, epsilon_ty = {epsilon_ty:.6f})."
        ),
    )


# ============================================================================
# 4. STRAIN COMPATIBILITY & BEAM DUCTILITY LIMIT (BG-FLEX-STRAIN-LIMIT)
# ============================================================================


def evaluate_mabhas9_strain_and_ductility_limit(
    c_mm: float,
    dt_mm: float,
    rebar: RebarMaterial,
    *,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate Mabhas 9 flexural strain compatibility and Clause 9-11-2-3 beam ductility limit.

    Rule ID: `BG-FLEX-STRAIN-LIMIT`
    Source: Mabhas 9 (1399), PDF pp. 16-18, 22, 41, Printed pp. 107-109, 113, 132,
            Clauses 9-8-2-2-2, 9-8-2-2-3, 9-7-4-2, 9-11-2-3.
    """
    rule_id = RULE_BG_FLEX_STRAIN_LIMIT.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "c_mm": c_mm,
        "dt_mm": dt_mm,
        "fy_mpa": rebar.fy_mpa,
        "es_mpa": rebar.es_mpa,
    }

    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(
            normalized_inputs=raw_inputs, unit="dimensionless"
        )

    diagnostics: List[EngineeringDiagnostic] = []
    diagnostics.extend(
        validate_rebar_material(
            rebar,
            enforce_mabhas9_flex_min_fy_limit=True,
            rule_id=rule_id,
        )
    )
    if not math.isfinite(c_mm) or c_mm <= 0.0:
        diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_NEUTRAL_AXIS_DEPTH",
                severity=DiagnosticSeverity.ERROR,
                message=f"Neutral-axis depth c_mm must be finite and > 0 mm, got {c_mm}.",
                rule_id=rule_id,
                field_name="c_mm",
            )
        )
    if not math.isfinite(dt_mm) or dt_mm <= 0.0:
        diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_EXTREME_TENSION_DEPTH",
                severity=DiagnosticSeverity.ERROR,
                message=f"Extreme tension depth dt_mm must be finite and > 0 mm, got {dt_mm}.",
                rule_id=rule_id,
                field_name="dt_mm",
            )
        )
    elif math.isfinite(c_mm) and c_mm >= dt_mm:
        diagnostics.append(
            EngineeringDiagnostic(
                code="NEUTRAL_AXIS_EXCEEDS_TENSION_DEPTH",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    f"Neutral-axis depth c_mm ({c_mm} mm) must be < extreme tension "
                    f"depth dt_mm ({dt_mm} mm)."
                ),
                rule_id=rule_id,
                field_name="c_mm",
            )
        )

    if diagnostics:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="dimensionless",
            outcome=EvaluationOutcome.INVALID_INPUT,
            diagnostics=diagnostics,
            message=diagnostics[0].message,
        )

    epsilon_ty = rebar.fy_mpa / rebar.es_mpa
    epsilon_t_min_beam = epsilon_ty + BG_FLEX_TENSION_CONTROLLED_DELTA_STRAIN
    epsilon_t = BG_FLEX_EPSILON_CU * (dt_mm - c_mm) / c_mm
    c_over_dt = c_mm / dt_mm
    c_over_dt_max_tc = BG_FLEX_EPSILON_CU / (
        epsilon_ty + BG_FLEX_EPSILON_CU + BG_FLEX_TENSION_CONTROLLED_DELTA_STRAIN
    )
    c_max_tc_mm = c_over_dt_max_tc * dt_mm

    intermediates: Dict[str, float] = {
        "epsilon_cu": BG_FLEX_EPSILON_CU,
        "epsilon_ty": epsilon_ty,
        "epsilon_t_min_beam": epsilon_t_min_beam,
        "epsilon_t": epsilon_t,
        "c_over_dt": c_over_dt,
        "c_over_dt_max_tc": c_over_dt_max_tc,
        "c_max_tc_mm": c_max_tc_mm,
    }

    if epsilon_t >= epsilon_t_min_beam - _STRAIN_TOLERANCE:
        raw_inputs["strain_regime"] = "TENSION_CONTROLLED"
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=epsilon_t,
            unit="dimensionless",
            outcome=EvaluationOutcome.PASS,
            diagnostics=(),
            message=(
                f"PASS: Section is tension-controlled per Clause 9-11-2-3 "
                f"(epsilon_t = {epsilon_t:.6f} >= {epsilon_t_min_beam:.6f})."
            ),
        )

    _, regime = _compute_phi_and_regime(epsilon_t, epsilon_ty)
    raw_inputs["strain_regime"] = regime
    fail_diag = EngineeringDiagnostic(
        code="SECTION_NOT_TENSION_CONTROLLED_PER_9_11_2_3",
        severity=DiagnosticSeverity.ERROR,
        message=(
            f"FAIL: Net tensile strain epsilon_t ({epsilon_t:.6f}) < "
            f"epsilon_ty + 0.003 ({epsilon_t_min_beam:.6f}); non-prestressed beams "
            f"with Pu < 0.10*f'c*Ag must be tension-controlled under Clause 9-11-2-3."
        ),
        rule_id=rule_id,
        field_name="c_mm",
    )
    return CalculationTraceStep.from_rule(
        gate.rule,
        normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=epsilon_t,
        unit="dimensionless",
        outcome=EvaluationOutcome.FAIL,
        diagnostics=(fail_diag,),
        message=fail_diag.message,
    )


# ============================================================================
# 5. T-BEAM & L-BEAM EFFECTIVE COMPRESSION FLANGE WIDTH (BG-FLEX-TBEAM-B-EFF-001)
# ============================================================================


def evaluate_mabhas9_effective_flange_width(
    geometry: BeamGeometry,
    *,
    clear_web_spacing_sw_mm: Optional[float] = None,
    clear_span_ln_mm: Optional[float] = None,
    is_isolated_t_beam: Optional[bool] = None,
    bf_provided_mm: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate Mabhas 9 non-prestressed T-beam and L-beam effective compression flange width.

    Rule ID: `BG-FLEX-TBEAM-B-EFF-001`
    Source: Mabhas 9 (1399), PDF pp. 12-13, 41, Printed pp. 103-104, 132,
            Clauses 9-6-3-3-1, Table 9-6-1, 9-6-3-3-2, and 9-11-2-5.
    """
    rule_id = RULE_BG_FLEX_TBEAM_B_EFF_001.rule_id
    resolved_sw = (
        clear_web_spacing_sw_mm
        if clear_web_spacing_sw_mm is not None
        else geometry.clear_web_spacing_sw_mm
    )
    resolved_ln = (
        clear_span_ln_mm
        if clear_span_ln_mm is not None
        else geometry.clear_span_ln_mm
    )
    resolved_isolated = (
        is_isolated_t_beam
        if is_isolated_t_beam is not None
        else geometry.is_isolated_t_beam
    )
    resolved_bf_provided = (
        bf_provided_mm if bf_provided_mm is not None else geometry.bf_mm
    )

    raw_inputs: Dict[str, ScalarInputValue] = {
        "bw_mm": geometry.bw_mm,
        "h_mm": geometry.h_mm,
        "tf_mm": geometry.tf_mm,
        "section_type": geometry.section_type.value,
        "flange_condition": geometry.flange_condition.value,
        "clear_web_spacing_sw_mm": resolved_sw,
        "clear_span_ln_mm": resolved_ln,
        "is_isolated_t_beam": resolved_isolated,
        "bf_provided_mm": resolved_bf_provided,
    }

    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")

    diagnostics: List[EngineeringDiagnostic] = []
    diagnostics.extend(
        validate_beam_geometry(geometry, require_effective_depth=False, rule_id=rule_id)
    )

    if geometry.section_type not in (SectionType.T_SECTION, SectionType.L_SECTION):
        diagnostics.append(
            EngineeringDiagnostic(
                code="EFFECTIVE_FLANGE_WIDTH_REQUIRES_FLANGED_SECTION",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    f"Rule '{rule_id}' requires SectionType.T_SECTION or L_SECTION, "
                    f"got {geometry.section_type.value}."
                ),
                rule_id=rule_id,
                field_name="section_type",
            )
        )

    if geometry.tf_mm is None:
        diagnostics.append(
            EngineeringDiagnostic(
                code="MISSING_FLANGE_THICKNESS",
                severity=DiagnosticSeverity.ERROR,
                message="Flange/slab thickness tf_mm (> 0 mm) is required to evaluate effective flange width.",
                rule_id=rule_id,
                field_name="tf_mm",
            )
        )

    if bf_provided_mm is not None and (
        not math.isfinite(bf_provided_mm) or bf_provided_mm <= geometry.bw_mm
    ):
        diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_FLANGE_WIDTH",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    f"bf_provided_mm must be finite and > bw_mm ({geometry.bw_mm} mm), "
                    f"got {bf_provided_mm}."
                ),
                rule_id=rule_id,
                field_name="bf_provided_mm",
            )
        )

    if not diagnostics and geometry.flange_condition == FlangeCondition.FLANGE_IN_TENSION:
        block_diag = EngineeringDiagnostic(
            code="FLANGE_IN_TENSION_EFFECTIVE_WIDTH_UNVERIFIED",
            severity=DiagnosticSeverity.BLOCK,
            message=(
                f"Rule '{rule_id}' (Table 9-6-1 / Clause 9-6-3-3) governs compression "
                f"flanges only; {geometry.section_type.value} with FLANGE_IN_TENSION "
                "remains UNVERIFIED_RULE_BLOCKED."
            ),
            rule_id=rule_id,
            field_name="flange_condition",
            required_verification=(
                "Visually verify the Mabhas 9 provision for T/L sections with flange "
                "in tension and register it in docs/VERIFIED_RULES.md."
            ),
        )
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="mm",
            outcome=EvaluationOutcome.UNVERIFIED_RULE_BLOCKED,
            diagnostics=(block_diag,),
            message=block_diag.message,
        )

    if not diagnostics and geometry.flange_condition == FlangeCondition.NO_FLANGE:
        diagnostics.append(
            EngineeringDiagnostic(
                code="INCONSISTENT_FLANGED_SECTION_NO_FLANGE",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    f"{geometry.section_type.value} cannot have "
                    "flange_condition == FlangeCondition.NO_FLANGE."
                ),
                rule_id=rule_id,
                field_name="flange_condition",
            )
        )

    if resolved_isolated:
        if geometry.section_type != SectionType.T_SECTION:
            diagnostics.append(
                EngineeringDiagnostic(
                    code="ISOLATED_FLANGE_RULE_ONLY_FOR_T_SECTION",
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        "Clause 9-6-3-3-2 isolated beam flange limits apply only to "
                        "SectionType.T_SECTION."
                    ),
                    rule_id=rule_id,
                    field_name="is_isolated_t_beam",
                )
            )
    else:
        if resolved_sw is None or not math.isfinite(resolved_sw) or resolved_sw <= 0.0:
            diagnostics.append(
                EngineeringDiagnostic(
                    code="INVALID_CLEAR_WEB_SPACING_SW",
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        "clear_web_spacing_sw_mm (sw) must be finite and > 0 mm for "
                        f"Table 9-6-1 evaluation, got {resolved_sw}."
                    ),
                    rule_id=rule_id,
                    field_name="clear_web_spacing_sw_mm",
                )
            )
        if resolved_ln is None or not math.isfinite(resolved_ln) or resolved_ln <= 0.0:
            diagnostics.append(
                EngineeringDiagnostic(
                    code="INVALID_CLEAR_SPAN_LN",
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        "clear_span_ln_mm (ln) must be finite and > 0 mm for "
                        f"Table 9-6-1 evaluation, got {resolved_ln}."
                    ),
                    rule_id=rule_id,
                    field_name="clear_span_ln_mm",
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

    assert geometry.tf_mm is not None
    hf_mm = geometry.tf_mm
    bw_mm = geometry.bw_mm

    # Case A: Isolated T-beam per Clause 9-6-3-3-2
    if resolved_isolated:
        hf_min_mm = BG_FLEX_ISOLATED_TBEAM_MIN_HF_BW_RATIO * bw_mm
        bf_limit_mm = BG_FLEX_ISOLATED_TBEAM_MAX_BF_BW_RATIO * bw_mm
        raw_inputs["governing_criterion"] = "ISOLATED_T_BEAM_CLAUSE_9_6_3_3_2"
        intermediates: Dict[str, float] = {
            "bw_mm": bw_mm,
            "hf_mm": hf_mm,
            "hf_min_isolated_mm": hf_min_mm,
            "bf_effective_limit_mm": bf_limit_mm,
        }
        fail_diags: List[EngineeringDiagnostic] = []
        if hf_mm < hf_min_mm - 1e-9:
            fail_diags.append(
                EngineeringDiagnostic(
                    code="ISOLATED_T_BEAM_FLANGE_THICKNESS_TOO_SMALL",
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        f"FAIL: Isolated T-beam flange thickness hf ({hf_mm:.2f} mm) < "
                        f"0.5 * bw ({hf_min_mm:.2f} mm) required by Clause 9-6-3-3-2."
                    ),
                    rule_id=rule_id,
                    field_name="tf_mm",
                )
            )
        if resolved_bf_provided is not None:
            intermediates["bf_provided_mm"] = resolved_bf_provided
            if resolved_bf_provided > bf_limit_mm + 1e-9:
                fail_diags.append(
                    EngineeringDiagnostic(
                        code="ISOLATED_T_BEAM_FLANGE_WIDTH_EXCEEDED",
                        severity=DiagnosticSeverity.ERROR,
                        message=(
                            f"FAIL: Isolated T-beam flange width bf ({resolved_bf_provided:.2f} mm) > "
                            f"4 * bw ({bf_limit_mm:.2f} mm) permitted by Clause 9-6-3-3-2."
                        ),
                        rule_id=rule_id,
                        field_name="bf_provided_mm",
                    )
                )
        if fail_diags:
            return CalculationTraceStep.from_rule(
                gate.rule,
                normalized_inputs=raw_inputs,
                intermediate_values=intermediates,
                final_result=bf_limit_mm,
                unit="mm",
                outcome=EvaluationOutcome.FAIL,
                diagnostics=fail_diags,
                message=fail_diags[0].message,
            )
        if resolved_bf_provided is not None:
            return CalculationTraceStep.from_rule(
                gate.rule,
                normalized_inputs=raw_inputs,
                intermediate_values=intermediates,
                final_result=bf_limit_mm,
                unit="mm",
                outcome=EvaluationOutcome.PASS,
                diagnostics=(),
                message=(
                    f"PASS: Isolated T-beam satisfies Clause 9-6-3-3-2 "
                    f"(hf = {hf_mm:.2f} >= {hf_min_mm:.2f} mm, "
                    f"bf = {resolved_bf_provided:.2f} <= {bf_limit_mm:.2f} mm)."
                ),
            )
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=bf_limit_mm,
            unit="mm",
            outcome=EvaluationOutcome.COMPUTED,
            diagnostics=(),
            message=(
                f"Computed isolated T-beam maximum effective flange width "
                f"bf,limit = {bf_limit_mm:.2f} mm under Clause 9-6-3-3-2."
            ),
        )

    # Case B: Slab-integral T-beam or L-beam per Clause 9-6-3-3-1 & Table 9-6-1
    assert resolved_sw is not None
    assert resolved_ln is not None

    if geometry.section_type == SectionType.T_SECTION:
        overhang_hf = BG_FLEX_TBEAM_OVERHANG_HF_MULT * hf_mm
        overhang_sw = resolved_sw / BG_FLEX_TBEAM_OVERHANG_SW_DIV
        overhang_ln = resolved_ln / BG_FLEX_TBEAM_OVERHANG_LN_DIV
        num_flange_sides = 2.0
    else:
        overhang_hf = BG_FLEX_LBEAM_OVERHANG_HF_MULT * hf_mm
        overhang_sw = resolved_sw / BG_FLEX_LBEAM_OVERHANG_SW_DIV
        overhang_ln = resolved_ln / BG_FLEX_LBEAM_OVERHANG_LN_DIV
        num_flange_sides = 1.0

    governing_overhang = min(overhang_hf, overhang_sw, overhang_ln)
    if governing_overhang == overhang_hf:
        governing_criterion = "FLANGE_THICKNESS_HF"
    elif governing_overhang == overhang_sw:
        governing_criterion = "WEB_CLEAR_SPACING_SW"
    else:
        governing_criterion = "CLEAR_SPAN_LN"

    raw_inputs["governing_criterion"] = governing_criterion
    bf_limit_mm = bw_mm + num_flange_sides * governing_overhang

    intermediates = {
        "bw_mm": bw_mm,
        "hf_mm": hf_mm,
        "sw_mm": resolved_sw,
        "ln_mm": resolved_ln,
        "overhang_limit_from_hf_mm": overhang_hf,
        "overhang_limit_from_sw_mm": overhang_sw,
        "overhang_limit_from_ln_mm": overhang_ln,
        "governing_overhang_each_side_mm": governing_overhang,
        "num_flange_sides": num_flange_sides,
        "bf_effective_limit_mm": bf_limit_mm,
    }

    if resolved_bf_provided is None:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=bf_limit_mm,
            unit="mm",
            outcome=EvaluationOutcome.COMPUTED,
            diagnostics=(),
            message=(
                f"Computed {geometry.section_type.value} effective flange width "
                f"bf = {bf_limit_mm:.4f} mm under Table 9-6-1 "
                f"(governed by {governing_criterion})."
            ),
        )

    intermediates["bf_provided_mm"] = resolved_bf_provided
    if resolved_bf_provided <= bf_limit_mm + 1e-9:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=bf_limit_mm,
            unit="mm",
            outcome=EvaluationOutcome.PASS,
            diagnostics=(),
            message=(
                f"PASS: Provided flange width bf ({resolved_bf_provided:.4f} mm) <= "
                f"Table 9-6-1 limit ({bf_limit_mm:.4f} mm, governed by {governing_criterion})."
            ),
        )

    exceed_diag = EngineeringDiagnostic(
        code="EFFECTIVE_FLANGE_WIDTH_EXCEEDS_TABLE_9_6_1_LIMIT",
        severity=DiagnosticSeverity.ERROR,
        message=(
            f"FAIL: Provided flange width bf ({resolved_bf_provided:.4f} mm) exceeds "
            f"Mabhas 9 Table 9-6-1 effective flange width limit ({bf_limit_mm:.4f} mm, "
            f"governed by {governing_criterion})."
        ),
        rule_id=rule_id,
        field_name="bf_provided_mm",
    )
    return CalculationTraceStep.from_rule(
        gate.rule,
        normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=bf_limit_mm,
        unit="mm",
        outcome=EvaluationOutcome.FAIL,
        diagnostics=(exceed_diag,),
        message=exceed_diag.message,
    )


# ============================================================================
# 6. RECTANGULAR SINGLY-REINFORCED FLEXURAL RESISTANCE (BG-FLEX-RECT-SINGLY-001)
#    AND EXPLICIT BLOCKING OF DOUBLY-REINFORCED & FLANGED SECTIONS
# ============================================================================


def evaluate_mabhas9_flexural_capacity(
    geometry: BeamGeometry,
    concrete: ConcreteMaterial,
    rebar: RebarMaterial,
    *,
    mu_nmm: Optional[float] = None,
    as_provided_mm2: Optional[float] = None,
    as_compression_mm2: Optional[float] = None,
    require_design_inputs: bool = False,
    enforce_code_material_bounds: bool = True,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate Mabhas 9 beam flexural capacity and compliance.

    Governance & Execution Order:
    1. Identifies the applicable rule by section configuration:
       - `BG-FLEX-TBEAM-CAP-001` for `SectionType.T_SECTION`
       - `BG-FLEX-LBEAM-CAP-001` for `SectionType.L_SECTION`
       - `BG-FLEX-RECT-DOUBLY-001` for rectangular sections with `as_compression_mm2 > 0`
       - `BG-FLEX-RECT-SINGLY-001` for rectangular singly-reinforced sections
    2. Enforces jurisdiction gate (`MABHAS_9_COMPLIANCE` required; otherwise returns
       `EvaluationOutcome.JURISDICTION_BLOCKED`).
    3. Validates section geometry (`bw_mm`, `h_mm`, flange consistency), concrete
       (`fc_prime_mpa > 0` and 20 <= f'c <= 70 MPa per Clause 9-3-3-3), steel
       (`fy_mpa > 0`, `es_mpa > 0`, and fy <= 550 MPa per Table 9-4-4),
       `as_provided_mm2`, `as_compression_mm2`, `mu_nmm`, and resolves effective
       depth `d` via Phase 1 precedence (`EXPLICIT_D -> ACTUAL_REBAR_GEOMETRY -> UNRESOLVED`,
       never `h - 65` or `h - 90`). Returns `EvaluationOutcome.INVALID_INPUT` when any
       physical input or `d` is invalid.
    4. Explicitly blocks T- and L-sections (`FLANGED_SECTION_FLEXURAL_RESISTANCE_UNVERIFIED`)
       without silently falling back to rectangular behavior.
    5. Explicitly blocks doubly reinforced sections with compression reinforcement
       (`DOUBLY_REINFORCED_FLEXURAL_RESISTANCE_UNVERIFIED`) without silently ignoring `As'`.
    6. Executes verified rectangular singly-reinforced Mabhas 9 flexural resistance
       (`BG-FLEX-RECT-SINGLY-001`), enforcing both:
       - Clause 9-11-2-3 tension-controlled ductility / maximum reinforcement limit
         (`epsilon_t >= epsilon_ty + 0.003`), and
       - Clause 9-8-1-4 Eq. (9-8-1-الف) design strength check (`phi * Mn >= Mu`).
    """
    if geometry.section_type == SectionType.T_SECTION:
        active_rule = RULE_BG_FLEX_TBEAM_CAP_001
    elif geometry.section_type == SectionType.L_SECTION:
        active_rule = RULE_BG_FLEX_LBEAM_CAP_001
    elif as_compression_mm2 is not None and as_compression_mm2 > 0.0:
        active_rule = RULE_BG_FLEX_RECT_DOUBLY_001
    else:
        active_rule = RULE_BG_FLEX_RECT_SINGLY_001

    rule_id = active_rule.rule_id
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
        "es_mpa": rebar.es_mpa,
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
            active_rule,
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
    if not any(d.field_name == "fc_prime_mpa" for d in diagnostics) and enforce_code_material_bounds:
        diagnostics.extend(_validate_mabhas9_fc_bounds(concrete, rule_id=rule_id))

    diagnostics.extend(
        validate_rebar_material(
            rebar,
            enforce_mabhas9_flex_min_fy_limit=enforce_code_material_bounds,
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
            active_rule,
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
            active_rule,
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

    d_mm = d_res.d_mm
    raw_inputs["d_effective_mm"] = d_mm
    raw_inputs["d_resolution_source"] = d_res.source

    # 3. Configuration gate: T- and L-sections must never silently fall back to rectangular
    if geometry.section_type in (SectionType.T_SECTION, SectionType.L_SECTION):
        flanged_diag = EngineeringDiagnostic(
            code="FLANGED_SECTION_FLEXURAL_RESISTANCE_UNVERIFIED",
            severity=DiagnosticSeverity.BLOCK,
            message=(
                f"Flexural resistance is blocked for {geometry.section_type.value} "
                f"({active_rule.rule_id}): while effective compression flange width bf "
                f"is verified under {RULE_BG_FLEX_TBEAM_B_EFF_001.rule_id}, full flanged "
                "section flexural capacity decomposition is not yet verified in "
                "docs/VERIFIED_RULES.md. Silent fallback to rectangular behavior is prohibited."
            ),
            rule_id=rule_id,
            field_name="section_type",
            required_verification=(
                "Visually verify Mabhas 9 T- and L-beam flanged flexural capacity "
                "decomposition rules and register in docs/VERIFIED_RULES.md."
            ),
        )
        return CalculationTraceStep.from_rule(
            active_rule,
            normalized_inputs=raw_inputs,
            intermediate_values={"d_effective_mm": d_mm},
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
                f"({RULE_BG_FLEX_RECT_DOUBLY_001.rule_id}): Mabhas 9 doubly-reinforced "
                "beam procedural flexural capacity rules are not yet verified in "
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
            RULE_BG_FLEX_RECT_DOUBLY_001,
            normalized_inputs=raw_inputs,
            intermediate_values={
                "d_effective_mm": d_mm,
                "as_compression_mm2": as_compression_mm2,
            },
            final_result=None,
            unit="N*mm",
            outcome=EvaluationOutcome.UNVERIFIED_RULE_BLOCKED,
            diagnostics=(doubly_diag,),
            message=doubly_diag.message,
        )

    # 5. Singly reinforced rectangular beam: enforce central gatekeeper
    gate = evaluate_rule_gate(
        RULE_BG_FLEX_RECT_SINGLY_001.rule_id,
        active_jurisdiction=jurisdiction_mode,
    )
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="N*mm")

    if resolved_as_provided is None:
        missing_as_diag = EngineeringDiagnostic(
            code="MISSING_PROVIDED_TENSILE_REINFORCEMENT",
            severity=DiagnosticSeverity.ERROR,
            message=(
                "Provided tensile reinforcement area (as_provided_mm2 or "
                "geometry.tension_rebar_groups) is required to evaluate rectangular "
                "singly-reinforced flexural resistance."
            ),
            rule_id=rule_id,
            field_name="as_provided_mm2",
        )
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values={"d_effective_mm": d_mm},
            final_result=None,
            unit="N*mm",
            outcome=EvaluationOutcome.INVALID_INPUT,
            diagnostics=(missing_as_diag,),
            message=missing_as_diag.message,
        )

    # 6. Execute verified Mabhas 9 rectangular singly-reinforced flexural calculations
    bw_mm = geometry.bw_mm
    fc_mpa = concrete.fc_prime_mpa
    fy_mpa = rebar.fy_mpa
    es_mpa = rebar.es_mpa
    dt_mm = _resolve_extreme_tension_depth_dt(geometry, d_mm)
    raw_inputs["dt_extreme_tension_mm"] = dt_mm

    alpha_0, beta_1 = _compute_alpha0_beta1(fc_mpa)
    epsilon_ty = fy_mpa / es_mpa
    epsilon_t_min_beam = epsilon_ty + BG_FLEX_TENSION_CONTROLLED_DELTA_STRAIN

    # Tension-controlled ductility limits (Clause 9-11-2-3 & Clause 9-7-4-2)
    c_over_dt_max_tc = BG_FLEX_EPSILON_CU / (
        epsilon_ty + BG_FLEX_EPSILON_CU + BG_FLEX_TENSION_CONTROLLED_DELTA_STRAIN
    )
    c_max_tc_mm = c_over_dt_max_tc * dt_mm
    a_max_tc_mm = beta_1 * c_max_tc_mm
    as_max_tc_mm2 = (alpha_0 * fc_mpa * bw_mm * a_max_tc_mm) / fy_mpa
    rho_max_tc = as_max_tc_mm2 / (bw_mm * d_mm)
    rho_provided = resolved_as_provided / (bw_mm * d_mm)

    # Equilibrium with yielding steel assumption (fs = fy, Clause 9-4-8-3 Eq. 9-4-2)
    a_yield_mm = (resolved_as_provided * fy_mpa) / (alpha_0 * fc_mpa * bw_mm)
    c_yield_mm = a_yield_mm / beta_1
    epsilon_t_yield = BG_FLEX_EPSILON_CU * (dt_mm - c_yield_mm) / c_yield_mm

    if epsilon_t_yield >= epsilon_ty - _STRAIN_TOLERANCE:
        a_mm = a_yield_mm
        c_mm = c_yield_mm
        epsilon_t = epsilon_t_yield
        fs_mpa = fy_mpa
    else:
        # Over-reinforced compression-controlled strain-compatibility quadratic:
        # (alpha_0 * f'c * beta_1 * bw) * c^2 + (As * Es * epsilon_cu) * c - (As * Es * epsilon_cu * dt) = 0
        quad_a = alpha_0 * fc_mpa * beta_1 * bw_mm
        quad_b = resolved_as_provided * es_mpa * BG_FLEX_EPSILON_CU
        quad_c = -quad_b * dt_mm
        discriminant = quad_b * quad_b - 4.0 * quad_a * quad_c
        c_mm = (-quad_b + math.sqrt(max(discriminant, 0.0))) / (2.0 * quad_a)
        a_mm = beta_1 * c_mm
        epsilon_t = BG_FLEX_EPSILON_CU * (dt_mm - c_mm) / c_mm
        fs_mpa = min(es_mpa * max(epsilon_t, 0.0), fy_mpa)

    phi, strain_regime = _compute_phi_and_regime(epsilon_t, epsilon_ty)
    raw_inputs["strain_regime"] = strain_regime

    tension_force_n = resolved_as_provided * fs_mpa
    lever_arm_mm = d_mm - a_mm / 2.0
    mn_nmm = tension_force_n * lever_arm_mm
    phi_mn_nmm = phi * mn_nmm

    intermediates: Dict[str, float] = {
        "d_effective_mm": d_mm,
        "dt_extreme_tension_mm": dt_mm,
        "alpha_0": alpha_0,
        "beta_1": beta_1,
        "epsilon_cu": BG_FLEX_EPSILON_CU,
        "epsilon_ty": epsilon_ty,
        "epsilon_t_min_beam": epsilon_t_min_beam,
        "c_over_dt_max_tc": c_over_dt_max_tc,
        "c_max_tc_mm": c_max_tc_mm,
        "a_max_tc_mm": a_max_tc_mm,
        "as_max_tc_mm2": as_max_tc_mm2,
        "rho_max_tc": rho_max_tc,
        "as_provided_mm2": resolved_as_provided,
        "rho_provided": rho_provided,
        "c_mm": c_mm,
        "a_mm": a_mm,
        "c_over_dt": c_mm / dt_mm,
        "epsilon_t": epsilon_t,
        "fs_mpa": fs_mpa,
        "tension_force_n": tension_force_n,
        "lever_arm_z_mm": lever_arm_mm,
        "mn_nmm": mn_nmm,
        "phi": phi,
        "phi_mn_nmm": phi_mn_nmm,
    }
    if mu_nmm is not None:
        intermediates["mu_nmm"] = mu_nmm
        if phi_mn_nmm > 0.0:
            intermediates["demand_capacity_ratio_mu_over_phi_mn"] = (
                mu_nmm / phi_mn_nmm
            )

    eval_diagnostics: List[EngineeringDiagnostic] = []

    # Check 1: Mandatory tension-controlled ductility / maximum reinforcement limit (Clause 9-11-2-3)
    if epsilon_t < epsilon_t_min_beam - _STRAIN_TOLERANCE:
        eval_diagnostics.append(
            EngineeringDiagnostic(
                code="MAX_REINFORCEMENT_DUCTILITY_LIMIT_EXCEEDED",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    f"FAIL: Provided tensile reinforcement As ({resolved_as_provided:.4f} mm^2) "
                    f"exceeds maximum tension-controlled reinforcement As,max,tc "
                    f"({as_max_tc_mm2:.4f} mm^2); net tensile strain epsilon_t ({epsilon_t:.6f}) "
                    f"< epsilon_ty + 0.003 ({epsilon_t_min_beam:.6f}) required by Mabhas 9 "
                    "Clause 9-11-2-3 and Clause 9-7-4-2."
                ),
                rule_id=rule_id,
                field_name="as_provided_mm2",
            )
        )

    # Check 2: Design flexural strength check phi*Mn >= Mu (Clause 9-8-1-4 Eq. 9-8-1-الف)
    if mu_nmm is not None:
        tolerance_nmm = max(1e-6, abs(phi_mn_nmm) * _MOMENT_REL_TOLERANCE)
        if phi_mn_nmm + tolerance_nmm < mu_nmm:
            eval_diagnostics.append(
                EngineeringDiagnostic(
                    code="INSUFFICIENT_FLEXURAL_CAPACITY",
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        f"FAIL: Design flexural resistance phi*Mn ({phi_mn_nmm:.2f} N*mm) "
                        f"< factored moment demand Mu ({mu_nmm:.2f} N*mm) required by "
                        "Mabhas 9 Clause 9-8-1-4 Eq. (9-8-1-الف)."
                    ),
                    rule_id=rule_id,
                    field_name="mu_nmm",
                )
            )

    if eval_diagnostics:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=phi_mn_nmm,
            unit="N*mm",
            outcome=EvaluationOutcome.FAIL,
            diagnostics=eval_diagnostics,
            message=eval_diagnostics[0].message,
        )

    if mu_nmm is not None:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=phi_mn_nmm,
            unit="N*mm",
            outcome=EvaluationOutcome.PASS,
            diagnostics=(),
            message=(
                f"PASS: phi*Mn ({phi_mn_nmm:.2f} N*mm) >= Mu ({mu_nmm:.2f} N*mm) "
                f"and section is tension-controlled (epsilon_t = {epsilon_t:.6f} >= "
                f"{epsilon_t_min_beam:.6f})."
            ),
        )

    return CalculationTraceStep.from_rule(
        gate.rule,
        normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=phi_mn_nmm,
        unit="N*mm",
        outcome=EvaluationOutcome.COMPUTED,
        diagnostics=(),
        message=(
            f"Computed design flexural resistance phi*Mn = {phi_mn_nmm:.2f} N*mm "
            f"(Mn = {mn_nmm:.2f} N*mm, phi = {phi:.2f}, epsilon_t = {epsilon_t:.6f})."
        ),
    )


# ============================================================================
# 7. MABHAS 9 FLEXURAL WORKFLOW ORCHESTRATOR
# ============================================================================


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
    (`INVALID_INPUT > FAIL > BLOCKED > PARTIAL > PASS`):
    - Returns `PASS` when rectangular singly-reinforced flexural resistance
      (`BG-FLEX-RECT-SINGLY-001`) and minimum reinforcement (`BG-FLEX-MIN-001`)
      both pass.
    - Returns `BLOCKED` (or `FAIL`/`INVALID_INPUT` if a higher-priority failure
      exists) when the section is a T-beam, L-beam, or doubly-reinforced beam.
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
