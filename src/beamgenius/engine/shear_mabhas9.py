"""Mabhas 9 verified shear reinforcement evaluators (BG-SHEAR-MIN-001, BG-SHEAR-SPACING-001)."""

from __future__ import annotations

import math
from typing import Dict, List, Optional

from beamgenius.domain.enums import (
    DiagnosticSeverity,
    EvaluationOutcome,
    JurisdictionMode,
)
from beamgenius.domain.models import (
    BeamGeometry,
    ConcreteMaterial,
    RebarMaterial,
    StirrupLayout,
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
    validate_non_negative_force,
    validate_rebar_material,
    validate_stirrup_layout,
)
from beamgenius.registry.catalog import (
    RULE_BG_SHEAR_CAP_BLOCKED,
    RULE_BG_SHEAR_MIN_001,
    RULE_BG_SHEAR_SPACING_001,
    RULE_BG_SHEAR_VC_BLOCKED,
    RULE_BG_SHEAR_VS_DEMAND_BLOCKED,
    RULE_BG_SHEAR_VS_MAX_BLOCKED,
)
from beamgenius.registry.gatekeeper import (
    build_blocked_workflow_trace,
    evaluate_rule_gate,
)

# Constants tied to BG-SHEAR-MIN-001 (Mabhas 9 Clause 9-11-5-2 & Table 9-11-2)
BG_SHEAR_MIN_001_SQRT_FC_COEFF: float = 0.062
BG_SHEAR_MIN_001_CONST_STRESS_MPA: float = 0.35
BG_SHEAR_MIN_001_SHALLOW_H_LIMIT_MM: float = 250.0
BG_SHEAR_MIN_001_INTEGRAL_TF_FACTOR: float = 2.5
BG_SHEAR_MIN_001_INTEGRAL_BW_FACTOR: float = 0.5
BG_SHEAR_MIN_001_MAX_EXCEPTION_H_MM: float = 600.0
BG_SHEAR_MIN_001_SFRC_MAX_FC_MPA: float = 40.0
BG_SHEAR_MIN_001_SFRC_VU_COEFF: float = 0.17

# Constants tied to BG-SHEAR-SPACING-001 (Mabhas 9 Clause 9-11-6-5-3, docs/VERIFIED_RULES.md)
BG_SHEAR_SPACING_001_VS_THRESHOLD_COEFF: float = 0.33
BG_SHEAR_SPACING_001_COND1_S_D_DIVISOR: float = 2.0
BG_SHEAR_SPACING_001_COND1_S_CAP_MM: float = 600.0
BG_SHEAR_SPACING_001_COND1_ST_D_DIVISOR: float = 1.0
BG_SHEAR_SPACING_001_COND1_ST_CAP_MM: float = 600.0
BG_SHEAR_SPACING_001_COND2_S_D_DIVISOR: float = 4.0
BG_SHEAR_SPACING_001_COND2_S_CAP_MM: float = 300.0
BG_SHEAR_SPACING_001_COND2_ST_D_DIVISOR: float = 2.0
BG_SHEAR_SPACING_001_COND2_ST_CAP_MM: float = 300.0


def evaluate_minimum_shear_reinforcement(
    geometry: BeamGeometry,
    concrete: ConcreteMaterial,
    rebar: RebarMaterial,
    *,
    stirrups: Optional[StirrupLayout] = None,
    av_over_s_provided_mm2_per_mm: Optional[float] = None,
    vu_n: Optional[float] = None,
    phi_shear_explicit: Optional[float] = None,
    require_provided_stirrups: bool = False,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate Mabhas 9 Minimum Shear Reinforcement (BG-SHEAR-MIN-001).

    Formula (Mabhas 9, PDF p. 221, Clause 9-11-5-2):
        (Av/s)min = max(0.062 * sqrt(f'c) * bw / fyt, 0.35 * bw / fyt)

    Table 9-11-2 Exception Handling:
    1. h <= 250 mm -> EXEMPT
    2. Beam integral with slab AND h <= max(2.5 * tf, 0.5 * bw) AND h <= 600 mm -> EXEMPT
    3. Steel-fiber normal RC AND h <= 600 mm AND f'c <= 40 MPa AND
       Vu <= phi * 0.17 * sqrt(f'c) * bw * d -> EXEMPT (only when phi is explicitly supplied;
       if steel-fiber RC is requested without explicit phi -> UNVERIFIED_RULE_BLOCKED)
    4. One-way joist -> UNVERIFIED_RULE_BLOCKED
    """
    rule_id = RULE_BG_SHEAR_MIN_001.rule_id
    resolved_av_over_s = (
        av_over_s_provided_mm2_per_mm
        if av_over_s_provided_mm2_per_mm is not None
        else (stirrups.av_over_s_mm2_per_mm if stirrups is not None else None)
    )

    raw_inputs: Dict[str, ScalarInputValue] = {
        "bw_mm": geometry.bw_mm,
        "h_mm": geometry.h_mm,
        "d_effective_mm": geometry.d_effective_mm,
        "tf_mm": geometry.tf_mm,
        "is_integral_with_slab": geometry.is_integral_with_slab,
        "is_one_way_joist": geometry.is_one_way_joist,
        "fc_prime_mpa": concrete.fc_prime_mpa,
        "is_steel_fiber_normal_rc": concrete.is_steel_fiber_normal_rc,
        "fyt_mpa": rebar.effective_fyt_mpa,
        "av_over_s_provided_mm2_per_mm": resolved_av_over_s,
        "vu_n": vu_n,
        "phi_shear_explicit": phi_shear_explicit,
    }

    # 1. Central Gatekeeper check
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm^2/mm")

    # 2. Deterministic input validation
    diagnostics: List[EngineeringDiagnostic] = []
    diagnostics.extend(
        validate_beam_geometry(geometry, require_effective_depth=False, rule_id=rule_id)
    )
    diagnostics.extend(validate_concrete_material(concrete, rule_id=rule_id))
    diagnostics.extend(validate_rebar_material(rebar, require_fyt=True, rule_id=rule_id))

    if stirrups is not None:
        diagnostics.extend(
            validate_stirrup_layout(
                stirrups, require_transverse_spacing=False, rule_id=rule_id
            )
        )

    if av_over_s_provided_mm2_per_mm is not None and (
        not math.isfinite(av_over_s_provided_mm2_per_mm)
        or av_over_s_provided_mm2_per_mm < 0.0
    ):
        diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_AV_OVER_S_PROVIDED",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    "av_over_s_provided_mm2_per_mm must be finite and >= 0 mm^2/mm, "
                    f"got {av_over_s_provided_mm2_per_mm}."
                ),
                rule_id=rule_id,
                field_name="av_over_s_provided_mm2_per_mm",
            )
        )

    if vu_n is not None:
        diagnostics.extend(
            validate_non_negative_force(vu_n, field_name="vu_n", rule_id=rule_id)
        )

    if phi_shear_explicit is not None and (
        not math.isfinite(phi_shear_explicit)
        or phi_shear_explicit <= 0.0
        or phi_shear_explicit > 1.0
    ):
        diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_PHI_SHEAR",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    f"phi_shear_explicit must be in (0, 1], got {phi_shear_explicit}."
                ),
                rule_id=rule_id,
                field_name="phi_shear_explicit",
            )
        )

    if diagnostics:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="mm^2/mm",
            outcome=EvaluationOutcome.INVALID_INPUT,
            diagnostics=diagnostics,
            message=diagnostics[0].message,
        )

    # 3. Governance rule: Steel-fiber RC without explicit phi -> UNVERIFIED_RULE_BLOCKED
    if concrete.is_steel_fiber_normal_rc and phi_shear_explicit is None:
        sfrc_phi_diag = EngineeringDiagnostic(
            code="SFRC_SHEAR_EXCEPTION_MISSING_EXPLICIT_PHI",
            severity=DiagnosticSeverity.BLOCK,
            message=(
                f"Rule '{rule_id}' is blocked for steel-fiber normal reinforced concrete "
                "(Table 9-11-2 Exception 3) because explicit phi_shear_explicit was not "
                "supplied and the Mabhas 9 shear strength reduction factor phi is not yet "
                "verified in docs/VERIFIED_RULES.md."
            ),
            rule_id=rule_id,
            field_name="phi_shear_explicit",
            required_verification=(
                "Supply phi_shear_explicit or visually verify Mabhas 9 shear phi "
                "and register in docs/VERIFIED_RULES.md."
            ),
        )
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="mm^2/mm",
            outcome=EvaluationOutcome.UNVERIFIED_RULE_BLOCKED,
            diagnostics=(sfrc_phi_diag,),
            message=sfrc_phi_diag.message,
        )

    # 4. Compute (Av/s)min
    fyt_mpa = rebar.effective_fyt_mpa
    sqrt_fc = math.sqrt(concrete.fc_prime_mpa)
    term_1 = BG_SHEAR_MIN_001_SQRT_FC_COEFF * sqrt_fc * geometry.bw_mm / fyt_mpa
    term_2 = BG_SHEAR_MIN_001_CONST_STRESS_MPA * geometry.bw_mm / fyt_mpa
    av_over_s_min = max(term_1, term_2)

    intermediates: Dict[str, float] = {
        "sqrt_fc_mpa": sqrt_fc,
        "av_over_s_term_1_mm2_per_mm": term_1,
        "av_over_s_term_2_mm2_per_mm": term_2,
        "av_over_s_min_mm2_per_mm": av_over_s_min,
    }
    if resolved_av_over_s is not None:
        intermediates["av_over_s_provided_mm2_per_mm"] = resolved_av_over_s

    # 5. Evaluate Table 9-11-2 Exceptions 1 and 2 before requiring Vu/d for Exception 3
    # Exception 1: Shallow beam h <= 250 mm
    if geometry.h_mm <= BG_SHEAR_MIN_001_SHALLOW_H_LIMIT_MM:
        ex1_diag = EngineeringDiagnostic(
            code="TABLE_9_11_2_EXCEPTION_1_SHALLOW_BEAM",
            severity=DiagnosticSeverity.INFO,
            message=(
                f"Table 9-11-2 Exception 1 satisfied: shallow beam h ({geometry.h_mm} mm) "
                f"<= {BG_SHEAR_MIN_001_SHALLOW_H_LIMIT_MM} mm."
            ),
            rule_id=rule_id,
        )
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=av_over_s_min,
            unit="mm^2/mm",
            outcome=EvaluationOutcome.EXEMPT,
            diagnostics=(ex1_diag,),
            message=ex1_diag.message,
        )

    # Exception 2: Beam integral with slab: h <= max(2.5*tf, 0.5*bw) and h <= 600 mm
    if geometry.is_integral_with_slab and geometry.tf_mm is not None:
        integral_limit_mm = max(
            BG_SHEAR_MIN_001_INTEGRAL_TF_FACTOR * geometry.tf_mm,
            BG_SHEAR_MIN_001_INTEGRAL_BW_FACTOR * geometry.bw_mm,
        )
        intermediates["integral_slab_depth_limit_mm"] = integral_limit_mm
        if (
            geometry.h_mm <= integral_limit_mm
            and geometry.h_mm <= BG_SHEAR_MIN_001_MAX_EXCEPTION_H_MM
        ):
            ex2_diag = EngineeringDiagnostic(
                code="TABLE_9_11_2_EXCEPTION_2_INTEGRAL_SLAB",
                severity=DiagnosticSeverity.INFO,
                message=(
                    f"Table 9-11-2 Exception 2 satisfied: beam integral with slab has "
                    f"h ({geometry.h_mm} mm) <= max(2.5*tf, 0.5*bw) ({integral_limit_mm} mm) "
                    f"and h <= {BG_SHEAR_MIN_001_MAX_EXCEPTION_H_MM} mm."
                ),
                rule_id=rule_id,
            )
            return CalculationTraceStep.from_rule(
                gate.rule,
                normalized_inputs=raw_inputs,
                intermediate_values=intermediates,
                final_result=av_over_s_min,
                unit="mm^2/mm",
                outcome=EvaluationOutcome.EXEMPT,
                diagnostics=(ex2_diag,),
                message=ex2_diag.message,
            )

    # 6. Evaluate Table 9-11-2 Exception 3 (Steel-fiber normal RC: h <= 600 mm, f'c <= 40 MPa)
    if (
        concrete.is_steel_fiber_normal_rc
        and phi_shear_explicit is not None
        and geometry.h_mm <= BG_SHEAR_MIN_001_MAX_EXCEPTION_H_MM
        and concrete.fc_prime_mpa <= BG_SHEAR_MIN_001_SFRC_MAX_FC_MPA
    ):
        if vu_n is None:
            sfrc_vu_diag = EngineeringDiagnostic(
                code="SFRC_SHEAR_EXCEPTION_MISSING_VU",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    "Factored shear vu_n is required to evaluate Table 9-11-2 Exception 3 "
                    "for steel-fiber normal reinforced concrete."
                ),
                rule_id=rule_id,
                field_name="vu_n",
            )
            return CalculationTraceStep.from_rule(
                gate.rule,
                normalized_inputs=raw_inputs,
                intermediate_values=intermediates,
                final_result=None,
                unit="mm^2/mm",
                outcome=EvaluationOutcome.INVALID_INPUT,
                diagnostics=(sfrc_vu_diag,),
                message=sfrc_vu_diag.message,
            )

        d_res = resolve_effective_depth(geometry, rule_id=rule_id)
        if not d_res.is_valid or d_res.d_mm is None:
            return CalculationTraceStep.from_rule(
                gate.rule,
                normalized_inputs=raw_inputs,
                intermediate_values=intermediates,
                final_result=None,
                unit="mm^2/mm",
                outcome=EvaluationOutcome.INVALID_INPUT,
                diagnostics=d_res.diagnostics,
                message=(
                    d_res.diagnostics[0].message
                    if d_res.diagnostics
                    else "Failed to resolve effective depth d for SFRC exception check."
                ),
            )
        d_for_sfrc = d_res.d_mm
        raw_inputs["d_effective_mm"] = d_for_sfrc

        sfrc_vu_limit_n = (
            phi_shear_explicit
            * BG_SHEAR_MIN_001_SFRC_VU_COEFF
            * sqrt_fc
            * geometry.bw_mm
            * d_for_sfrc
        )
        intermediates["d_effective_mm"] = d_for_sfrc
        intermediates["sfrc_vu_limit_n"] = sfrc_vu_limit_n
        if vu_n <= sfrc_vu_limit_n:
            ex3_diag = EngineeringDiagnostic(
                code="TABLE_9_11_2_EXCEPTION_3_STEEL_FIBER_RC",
                severity=DiagnosticSeverity.INFO,
                message=(
                    f"Table 9-11-2 Exception 3 satisfied: steel-fiber RC with "
                    f"h ({geometry.h_mm} mm) <= 600 mm, f'c ({concrete.fc_prime_mpa} MPa) <= 40 MPa, "
                    f"and Vu ({vu_n:.2f} N) <= {sfrc_vu_limit_n:.2f} N."
                ),
                rule_id=rule_id,
            )
            return CalculationTraceStep.from_rule(
                gate.rule,
                normalized_inputs=raw_inputs,
                intermediate_values=intermediates,
                final_result=av_over_s_min,
                unit="mm^2/mm",
                outcome=EvaluationOutcome.EXEMPT,
                diagnostics=(ex3_diag,),
                message=ex3_diag.message,
            )

    # 7. Table 9-11-2 Exception 4: One-way joist is UNVERIFIED_RULE_BLOCKED
    if geometry.is_one_way_joist:
        joist_diag = EngineeringDiagnostic(
            code="ONE_WAY_JOIST_EXCEPTION_UNVERIFIED",
            severity=DiagnosticSeverity.BLOCK,
            message=(
                f"Rule '{rule_id}' is blocked for one-way joists (Table 9-11-2 Exception 4): "
                "the applicable one-way joist provision is not yet verified in "
                "docs/VERIFIED_RULES.md."
            ),
            rule_id=rule_id,
            field_name="is_one_way_joist",
            required_verification=(
                "Visually verify the Mabhas 9 one-way joist shear exception clause "
                "and register in docs/VERIFIED_RULES.md."
            ),
        )
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=None,
            unit="mm^2/mm",
            outcome=EvaluationOutcome.UNVERIFIED_RULE_BLOCKED,
            diagnostics=(joist_diag,),
            message=joist_diag.message,
        )

    # 8. Standard (Av/s)_provided >= (Av/s)_min check
    if resolved_av_over_s is None:
        if require_provided_stirrups:
            missing_diag = EngineeringDiagnostic(
                code="MISSING_PROVIDED_SHEAR_REINFORCEMENT",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    "Provided shear reinforcement (stirrups or av_over_s_provided_mm2_per_mm) "
                    "is required when minimum shear reinforcement is not exempt."
                ),
                rule_id=rule_id,
                field_name="stirrups",
            )
            return CalculationTraceStep.from_rule(
                gate.rule,
                normalized_inputs=raw_inputs,
                intermediate_values=intermediates,
                final_result=None,
                unit="mm^2/mm",
                outcome=EvaluationOutcome.INVALID_INPUT,
                diagnostics=(missing_diag,),
                message=missing_diag.message,
            )

        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=av_over_s_min,
            unit="mm^2/mm",
            outcome=EvaluationOutcome.COMPUTED,
            diagnostics=(),
            message=f"Computed (Av/s)min = {av_over_s_min:.6f} mm^2/mm under BG-SHEAR-MIN-001.",
        )

    if resolved_av_over_s >= av_over_s_min:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=av_over_s_min,
            unit="mm^2/mm",
            outcome=EvaluationOutcome.PASS,
            diagnostics=(),
            message=(
                f"PASS: (Av/s)provided ({resolved_av_over_s:.6f} mm^2/mm) >= "
                f"(Av/s)min ({av_over_s_min:.6f} mm^2/mm)."
            ),
        )

    fail_diag = EngineeringDiagnostic(
        code="INSUFFICIENT_MINIMUM_SHEAR_REINFORCEMENT",
        severity=DiagnosticSeverity.ERROR,
        message=(
            f"FAIL: (Av/s)provided ({resolved_av_over_s:.6f} mm^2/mm) < "
            f"(Av/s)min ({av_over_s_min:.6f} mm^2/mm) required by BG-SHEAR-MIN-001."
        ),
        rule_id=rule_id,
        field_name="av_over_s_provided_mm2_per_mm",
    )
    return CalculationTraceStep.from_rule(
        gate.rule,
        normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=av_over_s_min,
        unit="mm^2/mm",
        outcome=EvaluationOutcome.FAIL,
        diagnostics=(fail_diag,),
        message=fail_diag.message,
    )


def evaluate_maximum_stirrup_spacing(
    geometry: BeamGeometry,
    concrete: ConcreteMaterial,
    *,
    vs_n: Optional[float] = None,
    vu_n: Optional[float] = None,
    stirrups: Optional[StirrupLayout] = None,
    s_provided_mm: Optional[float] = None,
    st_provided_mm: Optional[float] = None,
    require_provided_stirrups: bool = False,
    require_transverse_spacing: bool = False,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate Mabhas 9 Maximum Stirrup Spacing (BG-SHEAR-SPACING-001).

    Authoritative source: docs/VERIFIED_RULES.md (Mabhas 9, PDF p. 227, Clause 9-11-6-5-3).
    Threshold:
        Vs_threshold = 0.33 * sqrt(f'c) * bw * d

    Condition 1 (Vs <= Vs_threshold, including exact equality Vs == Vs_threshold):
        s_max  = min(d / 2, 600 mm)
        st_max = min(d, 600 mm)

    Condition 2 (Vs > Vs_threshold):
        s_max  = min(d / 4, 300 mm)
        st_max = min(d / 2, 300 mm)

    Governance:
    - Does NOT derive Vs from Vu/Vc.
    - If caller provides Vu without Vs, returns UNVERIFIED_RULE_BLOCKED.
    """
    rule_id = RULE_BG_SHEAR_SPACING_001.rule_id
    resolved_s = (
        s_provided_mm
        if s_provided_mm is not None
        else (stirrups.longitudinal_spacing_s_mm if stirrups is not None else None)
    )
    resolved_st = (
        st_provided_mm
        if st_provided_mm is not None
        else (stirrups.transverse_leg_spacing_st_mm if stirrups is not None else None)
    )

    raw_inputs: Dict[str, ScalarInputValue] = {
        "bw_mm": geometry.bw_mm,
        "h_mm": geometry.h_mm,
        "d_effective_mm": geometry.d_effective_mm,
        "fc_prime_mpa": concrete.fc_prime_mpa,
        "vs_n": vs_n,
        "vu_n": vu_n,
        "s_provided_mm": resolved_s,
        "st_provided_mm": resolved_st,
    }

    # 1. Central Gatekeeper check
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")

    # 2. If caller provides Vu but not Vs -> UNVERIFIED_RULE_BLOCKED (cannot derive Vs from Vu/Vc)
    if vs_n is None and vu_n is not None:
        vs_block_diag = EngineeringDiagnostic(
            code="VS_DERIVATION_FROM_VU_UNVERIFIED_BLOCKED",
            severity=DiagnosticSeverity.BLOCK,
            message=(
                f"Rule '{rule_id}' is blocked: caller supplied Vu ({vu_n} N) without Vs. "
                "Deriving Vs from Vu and Vc (BG-SHEAR-VS-DEMAND-BLOCKED / BG-SHEAR-VC-BLOCKED) "
                "is prohibited until Mabhas 9 and Mostofinejad Chapter 7 shear capacity "
                "rules are verified in docs/VERIFIED_RULES.md."
            ),
            rule_id=rule_id,
            field_name="vs_n",
            required_verification=(
                "Visually verify Mabhas 9 Vc and Vs demand equations and register "
                "them in docs/VERIFIED_RULES.md, or supply Vs explicitly."
            ),
        )
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="mm",
            outcome=EvaluationOutcome.UNVERIFIED_RULE_BLOCKED,
            diagnostics=(vs_block_diag,),
            message=vs_block_diag.message,
        )

    # 3. Deterministic input validation
    diagnostics: List[EngineeringDiagnostic] = []
    if vs_n is None:
        diagnostics.append(
            EngineeringDiagnostic(
                code="MISSING_VS_FORCE",
                severity=DiagnosticSeverity.ERROR,
                message="Shear force carried by stirrups vs_n (>= 0 N) is required for BG-SHEAR-SPACING-001.",
                rule_id=rule_id,
                field_name="vs_n",
            )
        )
    else:
        diagnostics.extend(
            validate_non_negative_force(vs_n, field_name="vs_n", rule_id=rule_id)
        )

    diagnostics.extend(
        validate_beam_geometry(geometry, require_effective_depth=False, rule_id=rule_id)
    )
    diagnostics.extend(validate_concrete_material(concrete, rule_id=rule_id))

    if stirrups is not None:
        diagnostics.extend(
            validate_stirrup_layout(
                stirrups,
                require_transverse_spacing=require_transverse_spacing,
                rule_id=rule_id,
            )
        )
    else:
        if s_provided_mm is not None and (
            not math.isfinite(s_provided_mm) or s_provided_mm <= 0.0
        ):
            diagnostics.append(
                EngineeringDiagnostic(
                    code="INVALID_S_PROVIDED",
                    severity=DiagnosticSeverity.ERROR,
                    message=f"s_provided_mm must be finite and > 0 mm, got {s_provided_mm}.",
                    rule_id=rule_id,
                    field_name="s_provided_mm",
                )
            )
        if st_provided_mm is not None and (
            not math.isfinite(st_provided_mm) or st_provided_mm <= 0.0
        ):
            diagnostics.append(
                EngineeringDiagnostic(
                    code="INVALID_ST_PROVIDED",
                    severity=DiagnosticSeverity.ERROR,
                    message=f"st_provided_mm must be finite and > 0 mm, got {st_provided_mm}.",
                    rule_id=rule_id,
                    field_name="st_provided_mm",
                )
            )
        elif require_transverse_spacing and st_provided_mm is None:
            diagnostics.append(
                EngineeringDiagnostic(
                    code="MISSING_ST_PROVIDED",
                    severity=DiagnosticSeverity.ERROR,
                    message="Transverse leg spacing st_provided_mm is required when require_transverse_spacing=True.",
                    rule_id=rule_id,
                    field_name="st_provided_mm",
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

    # 4. Resolve effective depth d
    d_res = resolve_effective_depth(geometry, rule_id=rule_id)
    if not d_res.is_valid or d_res.d_mm is None:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="mm",
            outcome=EvaluationOutcome.INVALID_INPUT,
            diagnostics=d_res.diagnostics,
            message=(
                d_res.diagnostics[0].message
                if d_res.diagnostics
                else "Failed to resolve effective depth d."
            ),
        )

    if require_provided_stirrups and resolved_s is None:
        missing_s_diag = EngineeringDiagnostic(
            code="MISSING_PROVIDED_STIRRUP_SPACING",
            severity=DiagnosticSeverity.ERROR,
            message=(
                "Provided stirrup spacing (stirrups or s_provided_mm) is required "
                "for spacing compliance check."
            ),
            rule_id=rule_id,
            field_name="s_provided_mm",
        )
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="mm",
            outcome=EvaluationOutcome.INVALID_INPUT,
            diagnostics=(missing_s_diag,),
            message=missing_s_diag.message,
        )

    assert vs_n is not None
    d_mm = d_res.d_mm
    raw_inputs["d_effective_mm"] = d_mm
    raw_inputs["d_resolution_source"] = d_res.source

    # 5. Compute threshold and Condition 1 / Condition 2 spacing limits
    sqrt_fc = math.sqrt(concrete.fc_prime_mpa)
    vs_threshold_n = (
        BG_SHEAR_SPACING_001_VS_THRESHOLD_COEFF * sqrt_fc * geometry.bw_mm * d_mm
    )

    if vs_n <= vs_threshold_n:
        condition_branch = 1.0
        s_max_mm = min(
            d_mm / BG_SHEAR_SPACING_001_COND1_S_D_DIVISOR,
            BG_SHEAR_SPACING_001_COND1_S_CAP_MM,
        )
        st_max_mm = min(
            d_mm / BG_SHEAR_SPACING_001_COND1_ST_D_DIVISOR,
            BG_SHEAR_SPACING_001_COND1_ST_CAP_MM,
        )
    else:
        condition_branch = 2.0
        s_max_mm = min(
            d_mm / BG_SHEAR_SPACING_001_COND2_S_D_DIVISOR,
            BG_SHEAR_SPACING_001_COND2_S_CAP_MM,
        )
        st_max_mm = min(
            d_mm / BG_SHEAR_SPACING_001_COND2_ST_D_DIVISOR,
            BG_SHEAR_SPACING_001_COND2_ST_CAP_MM,
        )

    intermediates: Dict[str, float] = {
        "d_effective_mm": d_mm,
        "sqrt_fc_mpa": sqrt_fc,
        "vs_threshold_n": vs_threshold_n,
        "vs_n": vs_n,
        "condition_branch": condition_branch,
        "s_max_mm": s_max_mm,
        "st_max_mm": st_max_mm,
    }
    if resolved_s is not None:
        intermediates["s_provided_mm"] = resolved_s
    if resolved_st is not None:
        intermediates["st_provided_mm"] = resolved_st

    if resolved_s is None and resolved_st is None:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=s_max_mm,
            unit="mm",
            outcome=EvaluationOutcome.COMPUTED,
            diagnostics=(),
            message=(
                f"Computed Condition {int(condition_branch)} stirrup spacing limits: "
                f"s_max = {s_max_mm:.4f} mm, st_max = {st_max_mm:.4f} mm."
            ),
        )

    fail_diagnostics: List[EngineeringDiagnostic] = []
    if resolved_s is not None and resolved_s > s_max_mm:
        fail_diagnostics.append(
            EngineeringDiagnostic(
                code="LONGITUDINAL_STIRRUP_SPACING_EXCEEDED",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    f"FAIL: longitudinal stirrup spacing s ({resolved_s:.4f} mm) > "
                    f"s_max ({s_max_mm:.4f} mm) under Condition {int(condition_branch)}."
                ),
                rule_id=rule_id,
                field_name="s_provided_mm",
            )
        )

    if resolved_st is not None and resolved_st > st_max_mm:
        fail_diagnostics.append(
            EngineeringDiagnostic(
                code="TRANSVERSE_STIRRUP_SPACING_EXCEEDED",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    f"FAIL: transverse stirrup leg spacing st ({resolved_st:.4f} mm) > "
                    f"st_max ({st_max_mm:.4f} mm) under Condition {int(condition_branch)}."
                ),
                rule_id=rule_id,
                field_name="st_provided_mm",
            )
        )

    if fail_diagnostics:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=s_max_mm,
            unit="mm",
            outcome=EvaluationOutcome.FAIL,
            diagnostics=fail_diagnostics,
            message=fail_diagnostics[0].message,
        )

    return CalculationTraceStep.from_rule(
        gate.rule,
        normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=s_max_mm,
        unit="mm",
        outcome=EvaluationOutcome.PASS,
        diagnostics=(),
        message=(
            f"PASS (Condition {int(condition_branch)}): stirrup spacing satisfies "
            f"s_max = {s_max_mm:.4f} mm, st_max = {st_max_mm:.4f} mm."
        ),
    )


def evaluate_full_shear_capacity(
    geometry: BeamGeometry,
    concrete: ConcreteMaterial,
    rebar: RebarMaterial,
    *,
    vu_n: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Explicitly blocked workflow for full shear capacity design/check."""
    return build_blocked_workflow_trace(
        RULE_BG_SHEAR_CAP_BLOCKED.rule_id,
        active_jurisdiction=jurisdiction_mode,
        normalized_inputs={
            "bw_mm": geometry.bw_mm,
            "h_mm": geometry.h_mm,
            "d_effective_mm": geometry.d_effective_mm,
            "fc_prime_mpa": concrete.fc_prime_mpa,
            "fyt_mpa": rebar.effective_fyt_mpa,
            "vu_n": vu_n,
        },
    )


def evaluate_concrete_shear_capacity_vc(
    geometry: BeamGeometry,
    concrete: ConcreteMaterial,
    *,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Explicitly blocked workflow for concrete shear resistance Vc."""
    return build_blocked_workflow_trace(
        RULE_BG_SHEAR_VC_BLOCKED.rule_id,
        active_jurisdiction=jurisdiction_mode,
        normalized_inputs={
            "bw_mm": geometry.bw_mm,
            "h_mm": geometry.h_mm,
            "d_effective_mm": geometry.d_effective_mm,
            "fc_prime_mpa": concrete.fc_prime_mpa,
        },
    )


def evaluate_required_shear_steel_demand_vs(
    geometry: BeamGeometry,
    concrete: ConcreteMaterial,
    *,
    vu_n: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Explicitly blocked workflow for deriving Vs demand from Vu and Vc."""
    return build_blocked_workflow_trace(
        RULE_BG_SHEAR_VS_DEMAND_BLOCKED.rule_id,
        active_jurisdiction=jurisdiction_mode,
        normalized_inputs={
            "bw_mm": geometry.bw_mm,
            "h_mm": geometry.h_mm,
            "d_effective_mm": geometry.d_effective_mm,
            "fc_prime_mpa": concrete.fc_prime_mpa,
            "vu_n": vu_n,
        },
    )


def evaluate_maximum_shear_steel_vs_max(
    geometry: BeamGeometry,
    concrete: ConcreteMaterial,
    *,
    vs_n: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Explicitly blocked workflow for maximum cross-sectional shear force Vs,max."""
    return build_blocked_workflow_trace(
        RULE_BG_SHEAR_VS_MAX_BLOCKED.rule_id,
        active_jurisdiction=jurisdiction_mode,
        normalized_inputs={
            "bw_mm": geometry.bw_mm,
            "h_mm": geometry.h_mm,
            "d_effective_mm": geometry.d_effective_mm,
            "fc_prime_mpa": concrete.fc_prime_mpa,
            "vs_n": vs_n,
        },
    )
