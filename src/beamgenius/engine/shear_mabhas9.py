"""Mabhas 9 (1399) verified shear capacity and reinforcement evaluators.

Phase 2C verified production rules:
- ``BG-SHEAR-PHI-001``: shear strength reduction factor φ and φVn ≥ Vu check
- ``BG-SHEAR-VC-001``: concrete one-way shear resistance Vc
- ``BG-SHEAR-VS-001``: transverse reinforcement shear resistance Vs and demand
- ``BG-SHEAR-VS-MAX-001``: maximum one-way shear / web-crushing limit

Phase 1 verified production rules:
- ``BG-SHEAR-MIN-001``: minimum shear reinforcement & Table 9-11-2 exceptions
- ``BG-SHEAR-SPACING-001``: maximum stirrup spacing
"""

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
    RULE_BG_SHEAR_PHI_001,
    RULE_BG_SHEAR_SPACING_001,
    RULE_BG_SHEAR_VC_001,
    RULE_BG_SHEAR_VC_BLOCKED,
    RULE_BG_SHEAR_VS_001,
    RULE_BG_SHEAR_VS_DEMAND_BLOCKED,
    RULE_BG_SHEAR_VS_MAX_001,
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


# ============================================================================
# PHASE 2C — VERIFIED MABHAS 9 ONE-WAY SHEAR CAPACITY EVALUATORS
# ============================================================================

# Constants tied to BG-SHEAR-PHI-001 (Mabhas 9 Clauses 9-7-4-1 & 9-8-1-4, Table 9-7-2)
BG_SHEAR_PHI_001_STANDARD: float = 0.75
BG_SHEAR_PHI_001_SEISMIC_CAPACITY_GOVERNED: float = 0.60
BG_SHEAR_PHI_001_SEISMIC_JOINT_COUPLING: float = 0.85

# Constants tied to BG-SHEAR-VC-001 (Mabhas 9 Clauses 9-8-4-4-1..9-8-4-4-5, 9-8-4-2-2)
BG_SHEAR_VC_001_SIMPLIFIED_COEFF: float = 0.17
BG_SHEAR_VC_001_DETAILED_COEFF: float = 0.66
BG_SHEAR_VC_001_MAX_COEFF: float = 0.42
BG_SHEAR_VC_001_MIN_TRANSVERSE_COEFF: float = 0.08
BG_SHEAR_VC_001_SQRT_FC_GENERAL_CAP_MPA: float = 8.3
BG_SHEAR_VC_001_LAMBDA_S_D_DIVISOR_MM: float = 250.0
BG_SHEAR_VC_001_LAMBDA_S_MAX: float = 1.0
BG_SHEAR_VC_001_NU_AG_DIVISOR: float = 6.0
BG_SHEAR_VC_001_NU_STRESS_CAP_RATIO: float = 0.05

# Constants tied to BG-SHEAR-VS-001 (Mabhas 9 Clauses 9-8-4-5, 9-4-8-5, Table 9-4-4)
BG_SHEAR_VS_001_FYT_MAX_MPA: float = 420.0
BG_SHEAR_VS_001_MIN_INCLINED_ANGLE_DEG: float = 45.0
BG_SHEAR_VS_001_MAX_INCLINED_ANGLE_DEG: float = 90.0

# Constants tied to BG-SHEAR-VS-MAX-001 (Mabhas 9 Clause 9-8-4-1-3, Eq. 9-8-9)
BG_SHEAR_VS_MAX_001_COEFF: float = 0.66


def _resolve_sqrt_fc_effective(
    concrete: ConcreteMaterial,
    *,
    has_minimum_shear_reinforcement: bool,
) -> float:
    """Resolve effective sqrt(f'c) per Clause 9-8-4-2-2.

    For one-way shear, sqrt(f'c) is capped at 8.3 MPa unless the member is a
    beam/joist reinforced with at least minimum web shear reinforcement
    (Av >= Av,min per Clause 9-11-5-2), in which case the cap is waived.
    """
    sqrt_fc = math.sqrt(concrete.fc_prime_mpa)
    if has_minimum_shear_reinforcement:
        return sqrt_fc
    return min(sqrt_fc, BG_SHEAR_VC_001_SQRT_FC_GENERAL_CAP_MPA)


def evaluate_mabhas9_shear_phi_factor(
    *,
    vu_n: Optional[float] = None,
    vc_n: Optional[float] = None,
    vs_n: Optional[float] = None,
    is_seismic_capacity_governed: bool = False,
    is_beam_column_joint_or_diagonal_coupling_beam: bool = False,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate Mabhas 9 shear strength reduction factor φ (BG-SHEAR-PHI-001).

    Verified source: Clauses 9-7-4-1, Table 9-7-2 (Row 2), 9-7-4-5,
    9-8-1-4 Eq. (9-8-1-ب), 9-8-4-1-1, 9-8-4-1-2 Eq. (9-8-8).
    Standard non-seismic one-way shear: φ = 0.75.
    Seismic capacity-design branches (φ = 0.60 / 0.85 under Clause 9-7-4-5)
    depend on Chapter 9-20 Ve demands and remain UNVERIFIED_RULE_BLOCKED.
    """
    rule_id = RULE_BG_SHEAR_PHI_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "vu_n": vu_n,
        "vc_n": vc_n,
        "vs_n": vs_n,
        "is_seismic_capacity_governed": is_seismic_capacity_governed,
        "is_beam_column_joint_or_diagonal_coupling_beam": (
            is_beam_column_joint_or_diagonal_coupling_beam
        ),
    }

    # 1. Central Gatekeeper check
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs)

    # 2. Seismic capacity-design branches are blocked on Chapter 9-20 source verification
    if is_seismic_capacity_governed or is_beam_column_joint_or_diagonal_coupling_beam:
        seismic_diag = EngineeringDiagnostic(
            code="SEISMIC_SHEAR_PHI_UNVERIFIED_BLOCKED",
            severity=DiagnosticSeverity.BLOCK,
            message=(
                f"Rule '{rule_id}' is blocked: seismic capacity-design shear strength "
                "reduction factors under Clause 9-7-4-5 (φ = 0.60 for members where "
                "nominal shear strength is less than the shear corresponding to "
                "development of nominal flexural strength in special seismic systems, "
                "and φ = 0.85 for beam-column joints and diagonally reinforced coupling "
                "beams) depend on Chapter 9-20 seismic capacity-design shear demands "
                "(Ve) that are not yet verified in docs/VERIFIED_RULES.md."
            ),
            rule_id=rule_id,
            required_verification=(
                "Visually verify Mabhas 9 Chapter 9-20 seismic capacity-design "
                "shear demand clauses and register them in docs/VERIFIED_RULES.md."
            ),
        )
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="N",
            outcome=EvaluationOutcome.UNVERIFIED_RULE_BLOCKED,
            diagnostics=(seismic_diag,),
            message=seismic_diag.message,
        )

    # 3. Deterministic input validation
    diagnostics: List[EngineeringDiagnostic] = []
    for force_name, force_value in (
        ("vu_n", vu_n),
        ("vc_n", vc_n),
        ("vs_n", vs_n),
    ):
        if force_value is not None:
            diagnostics.extend(
                validate_non_negative_force(force_value, field_name=force_name, rule_id=rule_id)
            )
    if diagnostics:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="N",
            outcome=EvaluationOutcome.INVALID_INPUT,
            diagnostics=diagnostics,
            message=diagnostics[0].message,
        )

    phi = BG_SHEAR_PHI_001_STANDARD
    intermediates: Dict[str, float] = {"phi_shear": phi}

    # 4. Standard one-way shear φ = 0.75; perform φVn >= Vu check when all inputs present
    if vu_n is None and vc_n is None and vs_n is None:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=phi,
            unit="N",
            outcome=EvaluationOutcome.COMPUTED,
            diagnostics=(),
            message="Computed standard one-way shear strength reduction factor φ = 0.75.",
        )

    if vu_n is None or vc_n is None or vs_n is None:
        missing_diag = EngineeringDiagnostic(
            code="INCOMPLETE_FACTORED_SHEAR_CHECK_INPUTS",
            severity=DiagnosticSeverity.ERROR,
            message=(
                "Factored shear adequacy check φVn >= Vu requires ALL of "
                "vu_n, vc_n, and vs_n."
            ),
            rule_id=rule_id,
            field_name="vu_n" if vu_n is None else ("vc_n" if vc_n is None else "vs_n"),
        )
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=phi,
            unit="N",
            outcome=EvaluationOutcome.INVALID_INPUT,
            diagnostics=(missing_diag,),
            message=missing_diag.message,
        )

    vn_n = vc_n + vs_n
    phi_vn_n = phi * vn_n
    intermediates["vn_n"] = vn_n
    intermediates["phi_vn_n"] = phi_vn_n

    if phi_vn_n >= vu_n:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=phi_vn_n,
            unit="N",
            outcome=EvaluationOutcome.PASS,
            diagnostics=(),
            message=(
                f"PASS: φVn ({phi_vn_n:.4f} N) = 0.75 × (Vc {vc_n:.4f} N + "
                f"Vs {vs_n:.4f} N) >= Vu ({vu_n:.4f} N)."
            ),
        )

    fail_diag = EngineeringDiagnostic(
        code="INSUFFICIENT_FACTORED_SHEAR_RESISTANCE",
        severity=DiagnosticSeverity.ERROR,
        message=(
            f"FAIL: φVn ({phi_vn_n:.4f} N) = 0.75 × (Vc {vc_n:.4f} N + "
            f"Vs {vs_n:.4f} N) < Vu ({vu_n:.4f} N)."
        ),
        rule_id=rule_id,
        field_name="vu_n",
    )
    return CalculationTraceStep.from_rule(
        gate.rule,
        normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=phi_vn_n,
        unit="N",
        outcome=EvaluationOutcome.FAIL,
        diagnostics=(fail_diag,),
        message=fail_diag.message,
    )


def evaluate_mabhas9_concrete_shear_resistance_vc(
    geometry: BeamGeometry,
    concrete: ConcreteMaterial,
    *,
    has_minimum_shear_reinforcement: bool = True,
    use_detailed_rho_w_equation: bool = False,
    rho_w: Optional[float] = None,
    as_longitudinal_tension_mm2: Optional[float] = None,
    nu_n: float = 0.0,
    ag_mm2: Optional[float] = None,
    has_web_openings: bool = False,
    is_variable_depth_member: bool = False,
    is_circular_section: bool = False,
    is_one_way_joist_member: bool = False,
    is_seismic_frame_hinge_region: bool = False,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate Mabhas 9 concrete one-way shear resistance Vc (BG-SHEAR-VC-001).

    Verified source: Clauses 9-8-4-4-1..9-8-4-4-5, Eqs. (9-8-12-الف),
    (9-8-12-ب), (9-8-13), (9-8-14), Clause 9-8-4-2-2, Clauses 9-3-2-2 &
    9-3-2-3, Tables 9-3-1 & 9-3-2, Clause 9-3-3-3.

    - Av >= Av,min, simplified Eq. (9-8-12-الف):
        Vc = (0.17·λ·√f'c + Nu/(6Ag))·bw·d
    - Av >= Av,min, detailed Eq. (9-8-12-ب):
        Vc = (0.66·λ·(ρw)^(1/3)·√f'c + Nu/(6Ag))·bw·d
    - Av < Av,min, Eq. (9-8-13):
        Vc = (0.66·λs·λ·(ρw)^(1/3)·√f'c + Nu/(6Ag))·bw·d
    - λs = min(√(2/(1 + d/250)), 1.0)  [Eq. (9-8-14)]
    - Nu/(6Ag) ≤ 0.05·f'c (compression positive, tension negative)
    - 0 ≤ Vc ≤ 0.42·λ·√f'c·bw·d
    - √f'c ≤ 8.3 MPa unless Av ≥ Av,min (Clause 9-8-4-2-2)
    """
    rule_id = RULE_BG_SHEAR_VC_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "bw_mm": geometry.bw_mm,
        "h_mm": geometry.h_mm,
        "d_effective_mm": geometry.d_effective_mm,
        "fc_prime_mpa": concrete.fc_prime_mpa,
        "lambda_factor": concrete.lambda_factor,
        "has_minimum_shear_reinforcement": has_minimum_shear_reinforcement,
        "use_detailed_rho_w_equation": use_detailed_rho_w_equation,
        "rho_w": rho_w,
        "as_longitudinal_tension_mm2": as_longitudinal_tension_mm2,
        "nu_n": nu_n,
        "ag_mm2": ag_mm2,
    }

    # 1. Central Gatekeeper check
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="N")

    # 2. Unverified special-condition branches remain deterministically blocked
    blocked_flags = (
        has_web_openings,
        is_variable_depth_member,
        is_circular_section,
        is_one_way_joist_member,
        is_seismic_frame_hinge_region,
    )
    if any(blocked_flags):
        flag_names = {
            "Clause 9-8-4-1-4 web openings": has_web_openings,
            "Clause 9-8-4-1-6 variable-depth haunch inclined compression": (
                is_variable_depth_member
            ),
            "Clause 9-8-4-2-1 circular section geometry": is_circular_section,
            "Clause 9-11-7 one-way joist provisions": is_one_way_joist_member,
            "Chapter 9-20 seismic frame hinge region": is_seismic_frame_hinge_region,
        }
        active_flags = [name for name, flag in flag_names.items() if flag]
        special_diag = EngineeringDiagnostic(
            code="VC_SPECIAL_CONDITION_UNVERIFIED_BLOCKED",
            severity=DiagnosticSeverity.BLOCK,
            message=(
                f"Rule '{rule_id}' is blocked: unverified special condition(s) "
                f"[{'; '.join(active_flags)}]. These provisions are not yet "
                "verified in docs/VERIFIED_RULES.md and must not be silently "
                "approximated."
            ),
            rule_id=rule_id,
            required_verification=(
                "Visually verify the applicable Mabhas 9 special shear clauses "
                "and register them in docs/VERIFIED_RULES.md."
            ),
        )
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="N",
            outcome=EvaluationOutcome.UNVERIFIED_RULE_BLOCKED,
            diagnostics=(special_diag,),
            message=special_diag.message,
        )

    # 3. Deterministic input validation
    diagnostics: List[EngineeringDiagnostic] = []
    diagnostics.extend(
        validate_beam_geometry(geometry, require_effective_depth=False, rule_id=rule_id)
    )
    diagnostics.extend(validate_concrete_material(concrete, rule_id=rule_id))
    if not math.isfinite(nu_n):
        diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_NU_FORCE",
                severity=DiagnosticSeverity.ERROR,
                message=f"Factored axial force nu_n must be finite (N), got {nu_n}.",
                rule_id=rule_id,
                field_name="nu_n",
            )
        )
    if ag_mm2 is not None and (
        not math.isfinite(ag_mm2) or ag_mm2 <= 0.0
    ):
        diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_GROSS_AREA_AG",
                severity=DiagnosticSeverity.ERROR,
                message=f"Gross section area ag_mm2 must be finite and > 0 mm^2, got {ag_mm2}.",
                rule_id=rule_id,
                field_name="ag_mm2",
            )
        )
    if rho_w is not None and (
        not math.isfinite(rho_w) or rho_w < 0.0
    ):
        diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_RHO_W",
                severity=DiagnosticSeverity.ERROR,
                message=f"Longitudinal reinforcement ratio rho_w must be finite and >= 0, got {rho_w}.",
                rule_id=rule_id,
                field_name="rho_w",
            )
        )
    if as_longitudinal_tension_mm2 is not None and (
        not math.isfinite(as_longitudinal_tension_mm2)
        or as_longitudinal_tension_mm2 < 0.0
    ):
        diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_AS_LONGITUDINAL",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    "as_longitudinal_tension_mm2 must be finite and >= 0 mm^2, "
                    f"got {as_longitudinal_tension_mm2}."
                ),
                rule_id=rule_id,
                field_name="as_longitudinal_tension_mm2",
            )
        )
    if diagnostics:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="N",
            outcome=EvaluationOutcome.INVALID_INPUT,
            diagnostics=diagnostics,
            message=diagnostics[0].message,
        )

    # 4. Resolve effective depth d (Phase 1 precedence; never h-65 / h-90)
    d_res = resolve_effective_depth(geometry, rule_id=rule_id)
    if not d_res.is_valid or d_res.d_mm is None:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="N",
            outcome=EvaluationOutcome.INVALID_INPUT,
            diagnostics=d_res.diagnostics,
            message=(
                d_res.diagnostics[0].message
                if d_res.diagnostics
                else "Failed to resolve effective depth d for Vc."
            ),
        )
    d_mm = d_res.d_mm
    raw_inputs["d_effective_mm"] = d_mm

    # 5. Resolve gross section area Ag and axial stress modifier
    resolved_ag_mm2 = ag_mm2 if ag_mm2 is not None else geometry.bw_mm * geometry.h_mm
    if resolved_ag_mm2 <= 0.0:
        invalid_ag_diag = EngineeringDiagnostic(
            code="INVALID_GROSS_AREA_AG",
            severity=DiagnosticSeverity.ERROR,
            message=(
                f"Gross section area Ag must be > 0 mm^2 for axial modifier; "
                f"got {resolved_ag_mm2}."
            ),
            rule_id=rule_id,
            field_name="ag_mm2",
        )
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="N",
            outcome=EvaluationOutcome.INVALID_INPUT,
            diagnostics=(invalid_ag_diag,),
            message=invalid_ag_diag.message,
        )

    nu_over_6ag = (
        nu_n / (BG_SHEAR_VC_001_NU_AG_DIVISOR * resolved_ag_mm2) if nu_n != 0.0 else 0.0
    )
    nu_stress_cap = BG_SHEAR_VC_001_NU_STRESS_CAP_RATIO * concrete.fc_prime_mpa
    sigma_n_eff = min(nu_over_6ag, nu_stress_cap)

    sqrt_fc_eff = _resolve_sqrt_fc_effective(
        concrete, has_minimum_shear_reinforcement=has_minimum_shear_reinforcement
    )
    lambda_factor = concrete.lambda_factor

    # 6. Resolve longitudinal reinforcement ratio rho_w
    resolved_rho_w: Optional[float] = rho_w
    if resolved_rho_w is None:
        if as_longitudinal_tension_mm2 is not None:
            resolved_rho_w = as_longitudinal_tension_mm2 / (geometry.bw_mm * d_mm)
        elif geometry.provided_tensile_area_mm2 is not None:
            resolved_rho_w = geometry.provided_tensile_area_mm2 / (geometry.bw_mm * d_mm)

    lambda_s = min(
        math.sqrt(2.0 / (1.0 + d_mm / BG_SHEAR_VC_001_LAMBDA_S_D_DIVISOR_MM)),
        BG_SHEAR_VC_001_LAMBDA_S_MAX,
    )

    intermediates: Dict[str, float] = {
        "d_effective_mm": d_mm,
        "ag_mm2": resolved_ag_mm2,
        "sqrt_fc_effective_mpa": sqrt_fc_eff,
        "lambda_factor": lambda_factor,
        "lambda_s": lambda_s,
        "nu_over_6ag_mpa": nu_over_6ag,
        "nu_stress_cap_mpa": nu_stress_cap,
        "sigma_n_effective_mpa": sigma_n_eff,
    }

    # 7. Compute raw Vc per verified branch
    # selected_equation_branch: 1.0 = Eq. (9-8-12-الف),
    # 2.0 = Eq. (9-8-12-ب), 3.0 = Eq. (9-8-13)
    selected_equation_branch: float
    if has_minimum_shear_reinforcement and not use_detailed_rho_w_equation:
        # Eq. (9-8-12-الف): simplified Vc
        selected_equation_branch = 1.0
        vc_term = BG_SHEAR_VC_001_SIMPLIFIED_COEFF * lambda_factor * sqrt_fc_eff
    else:
        # Eq. (9-8-12-ب) detailed (Av >= Av,min) or Eq. (9-8-13) (Av < Av,min)
        if resolved_rho_w is None:
            missing_rho_diag = EngineeringDiagnostic(
                code="MISSING_RHO_W_FOR_DETAILED_VC",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    "Longitudinal reinforcement ratio rho_w (or "
                    "as_longitudinal_tension_mm2 / geometry.tension_rebar_groups) "
                    "is required for detailed Vc Eqs. (9-8-12-ب)/(9-8-13)."
                ),
                rule_id=rule_id,
                field_name="rho_w",
            )
            return CalculationTraceStep.from_rule(
                gate.rule,
                normalized_inputs=raw_inputs,
                intermediate_values=intermediates,
                final_result=None,
                unit="N",
                outcome=EvaluationOutcome.INVALID_INPUT,
                diagnostics=(missing_rho_diag,),
                message=missing_rho_diag.message,
            )
        if resolved_rho_w <= 0.0:
            if not has_minimum_shear_reinforcement:
                # Clause 9-8-4-4-2 excluding statement: Eq. (9-8-13) does not
                # apply when rho_w = 0 (As = 0)
                rho_zero_diag = EngineeringDiagnostic(
                    code="VC_EQ_9_8_13_NOT_APPLICABLE_ZERO_RHO_W",
                    severity=DiagnosticSeverity.BLOCK,
                    message=(
                        f"Rule '{rule_id}' is blocked: Eq. (9-8-13) is not applicable "
                        "when rho_w = 0 (As = 0 / plain concrete) per the exclusion in "
                        "Clause 9-8-4-4-2. Reinforced concrete shear resistance without "
                        "longitudinal tension reinforcement is unverified."
                    ),
                    rule_id=rule_id,
                    field_name="rho_w",
                    required_verification=(
                        "Provide longitudinal tension reinforcement (rho_w > 0) or "
                        "visually verify the applicable Mabhas 9 clause for plain "
                        "concrete shear resistance."
                    ),
                )
                return CalculationTraceStep.from_rule(
                    gate.rule,
                    normalized_inputs=raw_inputs,
                    intermediate_values=intermediates,
                    final_result=None,
                    unit="N",
                    outcome=EvaluationOutcome.UNVERIFIED_RULE_BLOCKED,
                    diagnostics=(rho_zero_diag,),
                    message=rho_zero_diag.message,
                )
            rho_zero_error = EngineeringDiagnostic(
                code="INVALID_RHO_W",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    "rho_w must be > 0 for detailed Vc Eq. (9-8-12-ب); got "
                    f"{resolved_rho_w}."
                ),
                rule_id=rule_id,
                field_name="rho_w",
            )
            return CalculationTraceStep.from_rule(
                gate.rule,
                normalized_inputs=raw_inputs,
                intermediate_values=intermediates,
                final_result=None,
                unit="N",
                outcome=EvaluationOutcome.INVALID_INPUT,
                diagnostics=(rho_zero_error,),
                message=rho_zero_error.message,
            )
        intermediates["rho_w"] = resolved_rho_w
        rho_w_cbrt = resolved_rho_w ** (1.0 / 3.0)
        intermediates["rho_w_cube_root"] = rho_w_cbrt
        if has_minimum_shear_reinforcement:
            selected_equation_branch = 2.0
            vc_term = (
                BG_SHEAR_VC_001_DETAILED_COEFF
                * lambda_factor
                * rho_w_cbrt
                * sqrt_fc_eff
            )
        else:
            selected_equation_branch = 3.0
            vc_term = (
                BG_SHEAR_VC_001_DETAILED_COEFF
                * lambda_s
                * lambda_factor
                * rho_w_cbrt
                * sqrt_fc_eff
            )

    intermediates["vc_base_stress_mpa"] = vc_term
    vc_raw_n = (vc_term + sigma_n_eff) * geometry.bw_mm * d_mm

    # 8. Bounds: 0 <= Vc <= 0.42·λ·√f'c·bw·d (Clause 9-8-4-4-4)
    vc_max_n = (
        BG_SHEAR_VC_001_MAX_COEFF
        * lambda_factor
        * sqrt_fc_eff
        * geometry.bw_mm
        * d_mm
    )
    vc_n = min(max(vc_raw_n, 0.0), vc_max_n)
    intermediates["selected_equation_branch"] = selected_equation_branch
    intermediates["vc_raw_n"] = vc_raw_n
    intermediates["vc_max_n"] = vc_max_n
    intermediates["vc_n"] = vc_n

    return CalculationTraceStep.from_rule(
        gate.rule,
        normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=vc_n,
        unit="N",
        outcome=EvaluationOutcome.COMPUTED,
        diagnostics=(),
        message=(
            f"Computed concrete one-way shear resistance Vc = {vc_n:.4f} N per "
            f"Eq. (9-8-12/13 branch {int(selected_equation_branch)}) "
            f"with 0 <= Vc <= {vc_max_n:.4f} N."
        ),
    )


def evaluate_mabhas9_transverse_shear_resistance_vs(
    geometry: BeamGeometry,
    concrete: ConcreteMaterial,
    rebar: RebarMaterial,
    *,
    stirrups: Optional[StirrupLayout] = None,
    av_over_s_provided_mm2_per_mm: Optional[float] = None,
    stirrup_angle_deg: float = 90.0,
    vu_n: Optional[float] = None,
    vc_n: Optional[float] = None,
    phi_shear: float = BG_SHEAR_PHI_001_STANDARD,
    uses_bent_up_longitudinal_bars: bool = False,
    uses_circular_hoops_or_spirals: bool = False,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate Mabhas 9 transverse shear resistance Vs and demand (BG-SHEAR-VS-001).

    Verified source: Clauses 9-8-4-2-3, 9-4-8-5, Table 9-4-4, 9-8-4-5-1
    Eq. (9-8-15), 9-8-4-5-3 Eq. (9-8-16), 9-8-4-5-4 Eq. (9-8-17).

    - Vs,req = max(Vu / φ - Vc, 0)  [Eq. (9-8-15)]
    - Vertical (α = 90°): Vs = Av·fyt·d / s  [Eq. (9-8-16)]
    - Inclined (45° ≤ α ≤ 90°): Vs = Av·fyt·(sin α + cos α)·d / s  [Eq. (9-8-17)]
    - fyt ≤ 420 MPa (Table 9-4-4)
    """
    rule_id = RULE_BG_SHEAR_VS_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "bw_mm": geometry.bw_mm,
        "h_mm": geometry.h_mm,
        "d_effective_mm": geometry.d_effective_mm,
        "fc_prime_mpa": concrete.fc_prime_mpa,
        "fyt_mpa": rebar.effective_fyt_mpa,
        "stirrup_angle_deg": stirrup_angle_deg,
        "vu_n": vu_n,
        "vc_n": vc_n,
        "phi_shear": phi_shear,
        "uses_bent_up_longitudinal_bars": uses_bent_up_longitudinal_bars,
        "uses_circular_hoops_or_spirals": uses_circular_hoops_or_spirals,
    }

    # 1. Central Gatekeeper check
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="N")

    # 2. Bent-up longitudinal bars and circular hoops/spirals remain blocked
    if uses_bent_up_longitudinal_bars or uses_circular_hoops_or_spirals:
        active = []
        if uses_bent_up_longitudinal_bars:
            active.append("Clause 9-8-4-5-4 ب/پ bent-up longitudinal bars (Eqs. 9-8-18)")
        if uses_circular_hoops_or_spirals:
            active.append("Clauses 9-8-4-2-1 & 9-8-4-5-6 circular hoops / spirals")
        bent_diag = EngineeringDiagnostic(
            code="VS_SPECIAL_REINFORCEMENT_UNVERIFIED_BLOCKED",
            severity=DiagnosticSeverity.BLOCK,
            message=(
                f"Rule '{rule_id}' is blocked: unverified shear reinforcement type(s) "
                f"[{'; '.join(active)}]. These provisions are not yet verified in "
                "docs/VERIFIED_RULES.md."
            ),
            rule_id=rule_id,
            required_verification=(
                "Visually verify the applicable Mabhas 9 shear reinforcement "
                "clauses and register them in docs/VERIFIED_RULES.md."
            ),
        )
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="N",
            outcome=EvaluationOutcome.UNVERIFIED_RULE_BLOCKED,
            diagnostics=(bent_diag,),
            message=bent_diag.message,
        )

    # 3. Deterministic input validation
    diagnostics: List[EngineeringDiagnostic] = []
    diagnostics.extend(
        validate_beam_geometry(geometry, require_effective_depth=False, rule_id=rule_id)
    )
    diagnostics.extend(validate_concrete_material(concrete, rule_id=rule_id))
    diagnostics.extend(validate_rebar_material(rebar, require_fyt=True, rule_id=rule_id))
    if stirrups is not None:
        diagnostics.extend(
            validate_stirrup_layout(stirrups, require_transverse_spacing=False, rule_id=rule_id)
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
    if (
        not math.isfinite(stirrup_angle_deg)
        or stirrup_angle_deg < BG_SHEAR_VS_001_MIN_INCLINED_ANGLE_DEG
        or stirrup_angle_deg > BG_SHEAR_VS_001_MAX_INCLINED_ANGLE_DEG
    ):
        diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_STIRRUP_ANGLE",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    "Stirrup angle α with longitudinal tension reinforcement must "
                    f"be within [{BG_SHEAR_VS_001_MIN_INCLINED_ANGLE_DEG}, "
                    f"{BG_SHEAR_VS_001_MAX_INCLINED_ANGLE_DEG}] degrees per "
                    f"Clause 9-8-4-5-4, got {stirrup_angle_deg}."
                ),
                rule_id=rule_id,
                field_name="stirrup_angle_deg",
            )
        )
    if (
        not math.isfinite(phi_shear)
        or phi_shear <= 0.0
        or phi_shear > 1.0
    ):
        diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_PHI_SHEAR",
                severity=DiagnosticSeverity.ERROR,
                message=f"phi_shear must be in (0, 1], got {phi_shear}.",
                rule_id=rule_id,
                field_name="phi_shear",
            )
        )
    if vu_n is not None:
        diagnostics.extend(
            validate_non_negative_force(vu_n, field_name="vu_n", rule_id=rule_id)
        )
    if vc_n is not None:
        diagnostics.extend(
            validate_non_negative_force(vc_n, field_name="vc_n", rule_id=rule_id)
        )
    if (
        not math.isfinite(concrete.lambda_factor)
        or concrete.lambda_factor < 0.75
        or concrete.lambda_factor > 1.0
    ):
        diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_CONCRETE_LAMBDA_FACTOR",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    f"lambda_factor must be in [0.75, 1.0], got {concrete.lambda_factor}."
                ),
                rule_id=rule_id,
                field_name="lambda_factor",
            )
        )

    # Enforce fyt ≤ 420 MPa for standard non-seismic beam stirrups (Table 9-4-4)
    if (
        math.isfinite(rebar.effective_fyt_mpa)
        and rebar.effective_fyt_mpa > BG_SHEAR_VS_001_FYT_MAX_MPA
    ):
        diagnostics.append(
            EngineeringDiagnostic(
                code="FYT_EXCEEDS_MABHAS9_SHEAR_LIMIT",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    f"Transverse reinforcement yield strength fyt "
                    f"({rebar.effective_fyt_mpa} MPa) exceeds the verified "
                    f"{BG_SHEAR_VS_001_FYT_MAX_MPA} MPa limit of Table 9-4-4 for "
                    "standard non-seismic beam stirrups/ties."
                ),
                rule_id=rule_id,
                field_name="fyt_mpa",
            )
        )

    if diagnostics:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="N",
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
            unit="N",
            outcome=EvaluationOutcome.INVALID_INPUT,
            diagnostics=d_res.diagnostics,
            message=(
                d_res.diagnostics[0].message
                if d_res.diagnostics
                else "Failed to resolve effective depth d for Vs."
            ),
        )
    d_mm = d_res.d_mm
    raw_inputs["d_effective_mm"] = d_mm

    angle_rad = math.radians(stirrup_angle_deg)
    trig_factor = math.sin(angle_rad) + math.cos(angle_rad)  # 1.0 at α = 90°
    fyt_mpa = rebar.effective_fyt_mpa

    intermediates: Dict[str, float] = {
        "d_effective_mm": d_mm,
        "fyt_mpa": fyt_mpa,
        "stirrup_angle_deg": stirrup_angle_deg,
        "sin_plus_cos_alpha": trig_factor,
        "phi_shear": phi_shear,
    }

    # 5. Required Vs and (Av/s)_req from Vu & Vc (Eq. 9-8-15)
    vs_req_n: Optional[float] = None
    if vu_n is not None or vc_n is not None:
        if vu_n is None or vc_n is None:
            missing_diag = EngineeringDiagnostic(
                code="INCOMPLETE_SHEAR_DEMAND_INPUTS",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    "Shear demand evaluation (Eq. 9-8-15) requires BOTH vu_n and vc_n."
                ),
                rule_id=rule_id,
                field_name="vu_n" if vu_n is None else "vc_n",
            )
            return CalculationTraceStep.from_rule(
                gate.rule,
                normalized_inputs=raw_inputs,
                intermediate_values=intermediates,
                final_result=None,
                unit="N",
                outcome=EvaluationOutcome.INVALID_INPUT,
                diagnostics=(missing_diag,),
                message=missing_diag.message,
            )
        vs_req_n = max(vu_n / phi_shear - vc_n, 0.0)
        av_over_s_req = vs_req_n / (fyt_mpa * trig_factor * d_mm)
        intermediates["vs_required_n"] = vs_req_n
        intermediates["av_over_s_required_mm2_per_mm"] = av_over_s_req

    # 6. Provided Vs from stirrups or explicit Av/s
    resolved_av_over_s = (
        av_over_s_provided_mm2_per_mm
        if av_over_s_provided_mm2_per_mm is not None
        else (stirrups.av_over_s_mm2_per_mm if stirrups is not None else None)
    )

    if resolved_av_over_s is None:
        if vs_req_n is None:
            no_data_diag = EngineeringDiagnostic(
                code="INSUFFICIENT_VS_EVALUATION_INPUTS",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    "Provide stirrups / av_over_s_provided_mm2_per_mm for provided Vs "
                    "and/or (vu_n, vc_n) for required Vs demand."
                ),
                rule_id=rule_id,
                field_name="stirrups",
            )
            return CalculationTraceStep.from_rule(
                gate.rule,
                normalized_inputs=raw_inputs,
                intermediate_values=intermediates,
                final_result=None,
                unit="N",
                outcome=EvaluationOutcome.INVALID_INPUT,
                diagnostics=(no_data_diag,),
                message=no_data_diag.message,
            )
        # Demand-only evaluation of Eq. (9-8-15)
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=vs_req_n,
            unit="N",
            outcome=EvaluationOutcome.COMPUTED,
            diagnostics=(),
            message=(
                f"Computed required transverse shear resistance Vs,req = "
                f"{vs_req_n:.4f} N and (Av/s)_req = "
                f"{intermediates['av_over_s_required_mm2_per_mm']:.6f} mm^2/mm."
            ),
        )

    vs_provided_n = resolved_av_over_s * fyt_mpa * trig_factor * d_mm
    intermediates["av_over_s_provided_mm2_per_mm"] = resolved_av_over_s
    intermediates["vs_provided_n"] = vs_provided_n

    if vs_req_n is None:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=vs_provided_n,
            unit="N",
            outcome=EvaluationOutcome.COMPUTED,
            diagnostics=(),
            message=(
                f"Computed provided transverse shear resistance Vs = "
                f"{vs_provided_n:.4f} N (α = {stirrup_angle_deg}°)."
            ),
        )

    if vs_provided_n >= vs_req_n:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=vs_provided_n,
            unit="N",
            outcome=EvaluationOutcome.PASS,
            diagnostics=(),
            message=(
                f"PASS: Vs,provided ({vs_provided_n:.4f} N) >= Vs,req "
                f"({vs_req_n:.4f} N)."
            ),
        )

    fail_diag = EngineeringDiagnostic(
        code="INSUFFICIENT_TRANSVERSE_SHEAR_RESISTANCE",
        severity=DiagnosticSeverity.ERROR,
        message=(
            f"FAIL: Vs,provided ({vs_provided_n:.4f} N) < Vs,req "
            f"({vs_req_n:.4f} N)."
        ),
        rule_id=rule_id,
        field_name="av_over_s_provided_mm2_per_mm",
    )
    return CalculationTraceStep.from_rule(
        gate.rule,
        normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=vs_provided_n,
        unit="N",
        outcome=EvaluationOutcome.FAIL,
        diagnostics=(fail_diag,),
        message=fail_diag.message,
    )


def evaluate_mabhas9_shear_web_crushing_limit(
    geometry: BeamGeometry,
    concrete: ConcreteMaterial,
    *,
    vs_n: Optional[float] = None,
    vu_n: Optional[float] = None,
    vc_n: Optional[float] = None,
    phi_shear: float = BG_SHEAR_PHI_001_STANDARD,
    has_minimum_shear_reinforcement: bool = True,
    tu_nmm: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate Mabhas 9 maximum one-way shear / web-crushing limit (BG-SHEAR-VS-MAX-001).

    Verified source: Clause 9-8-4-1-3, Eq. (9-8-9):

        Vu ≤ φ·(Vc + 0.66·√f'c·bw·d)
        Vs,max = 0.66·√f'c·bw·d
        Vu,max = φ·(Vc + Vs,max)

    Combined shear–torsion interaction (Clause 9-8-6-3-1, Eq. 9-8-26) remains
    out of scope and blocked when torsion demand is present.
    """
    rule_id = RULE_BG_SHEAR_VS_MAX_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "bw_mm": geometry.bw_mm,
        "h_mm": geometry.h_mm,
        "d_effective_mm": geometry.d_effective_mm,
        "fc_prime_mpa": concrete.fc_prime_mpa,
        "lambda_factor": concrete.lambda_factor,
        "vs_n": vs_n,
        "vu_n": vu_n,
        "vc_n": vc_n,
        "phi_shear": phi_shear,
        "tu_nmm": tu_nmm,
    }

    # 1. Central Gatekeeper check
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="N")

    # 2. Torsion interaction is out of scope (BG-TORSION-PENDING)
    if tu_nmm is not None and tu_nmm > 0.0:
        torsion_diag = EngineeringDiagnostic(
            code="SHEAR_TORSION_INTERACTION_UNVERIFIED_BLOCKED",
            severity=DiagnosticSeverity.BLOCK,
            message=(
                f"Rule '{rule_id}' is blocked: combined shear-torsion web-crushing "
                "interaction (Clause 9-8-6-3-1, Eq. 9-8-26) is out of Phase 2C scope "
                "and remains unverified (BG-TORSION-PENDING)."
            ),
            rule_id=rule_id,
            field_name="tu_nmm",
            required_verification=(
                "Exclude torsion demand (tu_nmm = 0) or complete Mabhas 9 torsion "
                "source verification in docs/VERIFIED_RULES.md."
            ),
        )
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="N",
            outcome=EvaluationOutcome.UNVERIFIED_RULE_BLOCKED,
            diagnostics=(torsion_diag,),
            message=torsion_diag.message,
        )

    # 3. Deterministic input validation
    diagnostics: List[EngineeringDiagnostic] = []
    diagnostics.extend(
        validate_beam_geometry(geometry, require_effective_depth=False, rule_id=rule_id)
    )
    diagnostics.extend(validate_concrete_material(concrete, rule_id=rule_id))
    for force_name, force_value in (
        ("vs_n", vs_n),
        ("vu_n", vu_n),
        ("vc_n", vc_n),
    ):
        if force_value is not None:
            diagnostics.extend(
                validate_non_negative_force(force_value, field_name=force_name, rule_id=rule_id)
            )
    if (
        not math.isfinite(phi_shear)
        or phi_shear <= 0.0
        or phi_shear > 1.0
    ):
        diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_PHI_SHEAR",
                severity=DiagnosticSeverity.ERROR,
                message=f"phi_shear must be in (0, 1], got {phi_shear}.",
                rule_id=rule_id,
                field_name="phi_shear",
            )
        )
    if diagnostics:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values={},
            final_result=None,
            unit="N",
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
            unit="N",
            outcome=EvaluationOutcome.INVALID_INPUT,
            diagnostics=d_res.diagnostics,
            message=(
                d_res.diagnostics[0].message
                if d_res.diagnostics
                else "Failed to resolve effective depth d for Vs,max."
            ),
        )
    d_mm = d_res.d_mm
    raw_inputs["d_effective_mm"] = d_mm

    sqrt_fc_eff = _resolve_sqrt_fc_effective(
        concrete, has_minimum_shear_reinforcement=has_minimum_shear_reinforcement
    )
    vs_max_n = (
        BG_SHEAR_VS_MAX_001_COEFF * sqrt_fc_eff * geometry.bw_mm * d_mm
    )
    intermediates: Dict[str, float] = {
        "d_effective_mm": d_mm,
        "sqrt_fc_effective_mpa": sqrt_fc_eff,
        "vs_max_n": vs_max_n,
        "phi_shear": phi_shear,
    }
    if vc_n is not None:
        vu_max_n = phi_shear * (vc_n + vs_max_n)
        intermediates["vc_n"] = vc_n
        intermediates["vu_max_n"] = vu_max_n

    # 5. Evaluate provided Vs and/or Vu against limits
    messages: List[str] = []
    if vs_n is None and vu_n is None:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=vs_max_n,
            unit="N",
            outcome=EvaluationOutcome.COMPUTED,
            diagnostics=(),
            message=(
                f"Computed Vs,max = {vs_max_n:.4f} N"
                + (
                    f" and Vu,max = {intermediates['vu_max_n']:.4f} N."
                    if vc_n is not None
                    else "."
                )
            ),
        )

    fail_diagnostics: List[EngineeringDiagnostic] = []
    if vs_n is not None:
        intermediates["vs_n"] = vs_n
        if vs_n > vs_max_n:
            fail_diagnostics.append(
                EngineeringDiagnostic(
                    code="VS_EXCEEDS_WEB_CRUSHING_LIMIT",
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        f"FAIL: Vs ({vs_n:.4f} N) > Vs,max = 0.66·√f'c·bw·d "
                        f"({vs_max_n:.4f} N) per Clause 9-8-4-1-3 Eq. (9-8-9)."
                    ),
                    rule_id=rule_id,
                    field_name="vs_n",
                )
            )
        else:
            messages.append(f"Vs ({vs_n:.4f} N) <= Vs,max ({vs_max_n:.4f} N)")

    if vu_n is not None:
        if vc_n is None:
            missing_vc_diag = EngineeringDiagnostic(
                code="INCOMPLETE_SHEAR_WEB_CRUSHING_INPUTS",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    "vc_n is required to check Vu ≤ φ·(Vc + 0.66·√f'c·bw·d) "
                    "per Clause 9-8-4-1-3 Eq. (9-8-9)."
                ),
                rule_id=rule_id,
                field_name="vc_n",
            )
            return CalculationTraceStep.from_rule(
                gate.rule,
                normalized_inputs=raw_inputs,
                intermediate_values=intermediates,
                final_result=None,
                unit="N",
                outcome=EvaluationOutcome.INVALID_INPUT,
                diagnostics=(missing_vc_diag,),
                message=missing_vc_diag.message,
            )
        vu_max_n = phi_shear * (vc_n + vs_max_n)
        intermediates["vc_n"] = vc_n
        intermediates["vu_max_n"] = vu_max_n
        intermediates["vu_n"] = vu_n
        if vu_n > vu_max_n:
            fail_diagnostics.append(
                EngineeringDiagnostic(
                    code="VU_EXCEEDS_SECTION_DIMENSION_LIMIT",
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        f"FAIL: Vu ({vu_n:.4f} N) > φ·(Vc + 0.66·√f'c·bw·d) = "
                        f"{vu_max_n:.4f} N per Clause 9-8-4-1-3 Eq. (9-8-9)."
                    ),
                    rule_id=rule_id,
                    field_name="vu_n",
                )
            )
        else:
            messages.append(f"Vu ({vu_n:.4f} N) <= Vu,max ({vu_max_n:.4f} N)")

    if fail_diagnostics:
        return CalculationTraceStep.from_rule(
            gate.rule,
            normalized_inputs=raw_inputs,
            intermediate_values=intermediates,
            final_result=vs_max_n,
            unit="N",
            outcome=EvaluationOutcome.FAIL,
            diagnostics=fail_diagnostics,
            message=fail_diagnostics[0].message,
        )

    return CalculationTraceStep.from_rule(
        gate.rule,
        normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=vs_max_n,
        unit="N",
        outcome=EvaluationOutcome.PASS,
        diagnostics=(),
        message="PASS: " + "; ".join(messages) + ".",
    )


def run_mabhas9_shear_workflow(
    geometry: BeamGeometry,
    concrete: ConcreteMaterial,
    rebar: RebarMaterial,
    *,
    stirrups: Optional[StirrupLayout] = None,
    av_over_s_provided_mm2_per_mm: Optional[float] = None,
    stirrup_angle_deg: float = 90.0,
    vu_n: Optional[float] = None,
    nu_n: float = 0.0,
    has_minimum_shear_reinforcement: bool = True,
    use_detailed_rho_w_equation: bool = False,
    rho_w: Optional[float] = None,
    as_longitudinal_tension_mm2: Optional[float] = None,
    ag_mm2: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> List[CalculationTraceStep]:
    """Run the verified Mabhas 9 (1399) one-way shear workflow.

    Execution order (each step preserves its own outcome; aggregation in
    ``beam_checker.aggregate_compliance_report`` enforces the anti-misleading
    hierarchy INVALID_INPUT > FAIL > BLOCKED > PARTIAL > PASS):

    1. ``BG-SHEAR-PHI-001`` — φ = 0.75 & φVn ≥ Vu check (when all forces known)
    2. ``BG-SHEAR-VC-001`` — concrete shear resistance Vc
    3. ``BG-SHEAR-VS-001`` — transverse reinforcement Vs and demand
    4. ``BG-SHEAR-VS-MAX-001`` — web-crushing / section dimension limit
    """
    steps: List[CalculationTraceStep] = []

    # Step 1: Concrete shear resistance Vc (needed by later steps)
    vc_step = evaluate_mabhas9_concrete_shear_resistance_vc(
        geometry,
        concrete,
        has_minimum_shear_reinforcement=has_minimum_shear_reinforcement,
        use_detailed_rho_w_equation=use_detailed_rho_w_equation,
        rho_w=rho_w,
        as_longitudinal_tension_mm2=as_longitudinal_tension_mm2,
        nu_n=nu_n,
        ag_mm2=ag_mm2,
        jurisdiction_mode=jurisdiction_mode,
    )
    steps.append(vc_step)
    vc_n = vc_step.final_result if vc_step.outcome == EvaluationOutcome.COMPUTED else None

    # Step 2: Phi factor φ = 0.75 (and φVn ≥ Vu only when Vs reaches Step 4)
    steps.append(
        evaluate_mabhas9_shear_phi_factor(
            vu_n=None,
            vc_n=None,
            vs_n=None,
            jurisdiction_mode=jurisdiction_mode,
        )
    )

    # Step 3: Transverse shear resistance Vs / demand
    vs_step = evaluate_mabhas9_transverse_shear_resistance_vs(
        geometry,
        concrete,
        rebar,
        stirrups=stirrups,
        av_over_s_provided_mm2_per_mm=av_over_s_provided_mm2_per_mm,
        stirrup_angle_deg=stirrup_angle_deg,
        vu_n=vu_n,
        vc_n=vc_n,
        jurisdiction_mode=jurisdiction_mode,
    )
    steps.append(vs_step)
    vs_provided_n = vs_step.intermediate_values.get("vs_provided_n")

    # Step 4: Web-crushing / section dimension limit (Vs,max & Vu,max)
    steps.append(
        evaluate_mabhas9_shear_web_crushing_limit(
            geometry,
            concrete,
            vs_n=vs_provided_n,
            vu_n=vu_n,
            vc_n=vc_n,
            has_minimum_shear_reinforcement=has_minimum_shear_reinforcement,
            jurisdiction_mode=jurisdiction_mode,
        )
    )

    # Step 5: Factored shear adequacy φVn = φ(Vc + Vs) >= Vu when fully resolved
    if (
        vu_n is not None
        and vc_n is not None
        and vs_provided_n is not None
        and vs_step.outcome
        in (
            EvaluationOutcome.COMPUTED,
            EvaluationOutcome.PASS,
            EvaluationOutcome.FAIL,
        )
    ):
        steps.append(
            evaluate_mabhas9_shear_phi_factor(
                vu_n=vu_n,
                vc_n=vc_n,
                vs_n=vs_provided_n,
                jurisdiction_mode=jurisdiction_mode,
            )
        )

    return steps
