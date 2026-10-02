"""Isolated Mostofinejad Vol. 1 Chapter 5 reference/textbook methodology module.

GOVERNANCE RESTRICTION:
1. Equations in this module are NOT Iranian Mabhas 9 compliance rules.
2. They may execute ONLY under `JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY`.
3. Calling any function in this module with `JurisdictionMode.MABHAS_9_COMPLIANCE`
   returns `EvaluationOutcome.JURISDICTION_BLOCKED` via the central gatekeeper.
4. Equations BG-MOST-5-44, 5-45, 5-51, 5-52, 5-53, 5-57, 5-58, 5-59, 5-60, and 5-62
   are hard-blocked in ALL modes (`UNVERIFIED_RULE_BLOCKED`).
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

from beamgenius.domain.enums import (
    DiagnosticSeverity,
    EvaluationOutcome,
    JurisdictionMode,
)
from beamgenius.domain.models import BeamGeometry
from beamgenius.domain.trace import (
    CalculationTraceStep,
    EngineeringDiagnostic,
    ScalarInputValue,
)
from beamgenius.domain.validation import resolve_effective_depth
from beamgenius.registry.catalog import (
    RULE_BG_MOST_5_46,
    RULE_BG_MOST_5_47,
    RULE_BG_MOST_5_48A,
    RULE_BG_MOST_5_48B,
    RULE_BG_MOST_5_49,
    RULE_BG_MOST_5_50,
    RULE_BG_MOST_5_54,
    RULE_BG_MOST_5_55,
    RULE_BG_MOST_5_56,
    RULE_BG_MOST_5_61,
)
from beamgenius.registry.gatekeeper import (
    build_blocked_workflow_trace,
    evaluate_rule_gate,
)

# Constants tied to Mostofinejad Vol. 1 Chapter 5 equations
BG_MOST_5_46_OMEGA_COEFF: float = 0.59
BG_MOST_5_48A_DEPTH_DEDUCTION_MM: float = 65.0
BG_MOST_5_48B_DEPTH_DEDUCTION_MM: float = 90.0
BG_MOST_5_49_BASE: float = 0.85
BG_MOST_5_49_FC_SLOPE: float = 0.0015
BG_MOST_5_49_MIN: float = 0.67
BG_MOST_5_50_BASE: float = 0.97
BG_MOST_5_50_FC_SLOPE: float = 0.0025
BG_MOST_5_50_MIN: float = 0.67


def _invalid_step(
    rule_id: str,
    jurisdiction_mode: JurisdictionMode,
    raw_inputs: Dict[str, ScalarInputValue],
    unit: str,
    code: str,
    message: str,
    field_name: Optional[str] = None,
) -> CalculationTraceStep:
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    diag = EngineeringDiagnostic(
        code=code,
        severity=DiagnosticSeverity.ERROR,
        message=message,
        rule_id=rule_id,
        field_name=field_name,
    )
    return CalculationTraceStep.from_rule(
        gate.rule,
        normalized_inputs=raw_inputs,
        intermediate_values={},
        final_result=None,
        unit=unit,
        outcome=EvaluationOutcome.INVALID_INPUT,
        diagnostics=(diag,),
        message=message,
    )


def evaluate_mostofinejad_eq_5_46_kn(
    fc_prime_mpa: float,
    *,
    omega: Optional[float] = None,
    rho: Optional[float] = None,
    fy_mpa: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
) -> CalculationTraceStep:
    """Evaluate BG-MOST-5-46: kn = f'c * omega * (1 - 0.59 * omega), omega = rho * fy / f'c."""
    rule_id = RULE_BG_MOST_5_46.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "fc_prime_mpa": fc_prime_mpa,
        "omega": omega,
        "rho": rho,
        "fy_mpa": fy_mpa,
    }
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="MPa")

    if not math.isfinite(fc_prime_mpa) or fc_prime_mpa <= 0.0:
        return _invalid_step(
            rule_id,
            jurisdiction_mode,
            raw_inputs,
            "MPa",
            "INVALID_FC_PRIME",
            f"fc_prime_mpa must be finite and > 0 MPa, got {fc_prime_mpa}.",
            "fc_prime_mpa",
        )

    resolved_omega: Optional[float] = omega
    if resolved_omega is None:
        if rho is None or fy_mpa is None:
            return _invalid_step(
                rule_id,
                jurisdiction_mode,
                raw_inputs,
                "MPa",
                "MISSING_OMEGA_OR_RHO_FY",
                "Provide either omega or both rho and fy_mpa for BG-MOST-5-46.",
                "omega",
            )
        if not math.isfinite(rho) or rho <= 0.0:
            return _invalid_step(
                rule_id,
                jurisdiction_mode,
                raw_inputs,
                "MPa",
                "INVALID_RHO",
                f"rho must be finite and > 0, got {rho}.",
                "rho",
            )
        if not math.isfinite(fy_mpa) or fy_mpa <= 0.0:
            return _invalid_step(
                rule_id,
                jurisdiction_mode,
                raw_inputs,
                "MPa",
                "INVALID_FY",
                f"fy_mpa must be finite and > 0 MPa, got {fy_mpa}.",
                "fy_mpa",
            )
        resolved_omega = rho * fy_mpa / fc_prime_mpa

    if not math.isfinite(resolved_omega) or resolved_omega <= 0.0 or (
        1.0 - BG_MOST_5_46_OMEGA_COEFF * resolved_omega
    ) <= 0.0:
        return _invalid_step(
            rule_id,
            jurisdiction_mode,
            raw_inputs,
            "MPa",
            "INVALID_OMEGA_RANGE",
            f"omega must be in (0, {1.0 / BG_MOST_5_46_OMEGA_COEFF:.4f}), got {resolved_omega}.",
            "omega",
        )

    kn_mpa = fc_prime_mpa * resolved_omega * (1.0 - BG_MOST_5_46_OMEGA_COEFF * resolved_omega)
    return CalculationTraceStep.from_rule(
        gate.rule,
        normalized_inputs=raw_inputs,
        intermediate_values={"omega": resolved_omega, "kn_mpa": kn_mpa},
        final_result=kn_mpa,
        unit="MPa",
        outcome=EvaluationOutcome.COMPUTED,
        diagnostics=(),
        message=f"Computed kn = {kn_mpa:.4f} MPa under BG-MOST-5-46.",
    )


def evaluate_mostofinejad_eq_5_47_bd2(
    *,
    kn_mpa: float,
    mu_nmm: Optional[float] = None,
    phi: Optional[float] = None,
    mn_nmm: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
) -> CalculationTraceStep:
    """Evaluate BG-MOST-5-47: b * d^2 = Mn / kn = Mu / (phi * kn) (unit: mm^3)."""
    rule_id = RULE_BG_MOST_5_47.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "kn_mpa": kn_mpa,
        "mu_nmm": mu_nmm,
        "phi": phi,
        "mn_nmm": mn_nmm,
    }
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm^3")

    if not math.isfinite(kn_mpa) or kn_mpa <= 0.0:
        return _invalid_step(
            rule_id,
            jurisdiction_mode,
            raw_inputs,
            "mm^3",
            "INVALID_KN",
            f"kn_mpa must be finite and > 0 MPa, got {kn_mpa}.",
            "kn_mpa",
        )

    resolved_mn_nmm: Optional[float] = mn_nmm
    if resolved_mn_nmm is None:
        if mu_nmm is None or phi is None:
            return _invalid_step(
                rule_id,
                jurisdiction_mode,
                raw_inputs,
                "mm^3",
                "MISSING_MOMENT_OR_PHI",
                "Provide either mn_nmm or both mu_nmm and explicit phi for BG-MOST-5-47.",
                "mu_nmm",
            )
        if not math.isfinite(mu_nmm) or mu_nmm <= 0.0:
            return _invalid_step(
                rule_id,
                jurisdiction_mode,
                raw_inputs,
                "mm^3",
                "INVALID_MU",
                f"mu_nmm must be finite and > 0 N*mm, got {mu_nmm}.",
                "mu_nmm",
            )
        if not math.isfinite(phi) or phi <= 0.0 or phi > 1.0:
            return _invalid_step(
                rule_id,
                jurisdiction_mode,
                raw_inputs,
                "mm^3",
                "INVALID_PHI",
                f"phi must be in (0, 1], got {phi}.",
                "phi",
            )
        resolved_mn_nmm = mu_nmm / phi
    elif not math.isfinite(resolved_mn_nmm) or resolved_mn_nmm <= 0.0:
        return _invalid_step(
            rule_id,
            jurisdiction_mode,
            raw_inputs,
            "mm^3",
            "INVALID_MN",
            f"mn_nmm must be finite and > 0 N*mm, got {resolved_mn_nmm}.",
            "mn_nmm",
        )

    bd2_mm3 = resolved_mn_nmm / kn_mpa
    return CalculationTraceStep.from_rule(
        gate.rule,
        normalized_inputs=raw_inputs,
        intermediate_values={"mn_nmm": resolved_mn_nmm, "bd2_mm3": bd2_mm3},
        final_result=bd2_mm3,
        unit="mm^3",
        outcome=EvaluationOutcome.COMPUTED,
        diagnostics=(),
        message=f"Computed b*d^2 = {bd2_mm3:.2f} mm^3 under BG-MOST-5-47.",
    )


def solve_mostofinejad_flexural_steel_from_kn(
    *,
    b_mm: float,
    d_mm: float,
    mu_nmm: float,
    fc_prime_mpa: float,
    fy_mpa: float,
    phi: float,
    kn_override_mpa: Optional[float] = None,
    rho_override: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
) -> Tuple[CalculationTraceStep, CalculationTraceStep]:
    """Solve required flexural reinforcement area As using BG-MOST-5-47 and BG-MOST-5-46.

    Used strictly for isolated Mostofinejad textbook reference examples (Examples 5-5 & 5-6):
    1. BG-MOST-5-47: kn = Mu / (phi * b * d^2)
    2. BG-MOST-5-46: kn = f'c * omega * (1 - 0.59 * omega), rho = omega * f'c / fy, As = rho * b * d.
    """
    gate_47 = evaluate_rule_gate(
        RULE_BG_MOST_5_47.rule_id, active_jurisdiction=jurisdiction_mode
    )
    gate_46 = evaluate_rule_gate(
        RULE_BG_MOST_5_46.rule_id, active_jurisdiction=jurisdiction_mode
    )
    inputs_47: Dict[str, ScalarInputValue] = {
        "b_mm": b_mm,
        "d_mm": d_mm,
        "mu_nmm": mu_nmm,
        "phi": phi,
    }
    inputs_46: Dict[str, ScalarInputValue] = {
        "b_mm": b_mm,
        "d_mm": d_mm,
        "fc_prime_mpa": fc_prime_mpa,
        "fy_mpa": fy_mpa,
        "kn_override_mpa": kn_override_mpa,
        "rho_override": rho_override,
    }
    if not gate_47.allowed or not gate_46.allowed:
        return (
            gate_47.to_blocked_trace_step(normalized_inputs=inputs_47, unit="MPa"),
            gate_46.to_blocked_trace_step(normalized_inputs=inputs_46, unit="mm^2"),
        )

    def _invalid_pair(
        code: str, message: str, field_name: str
    ) -> Tuple[CalculationTraceStep, CalculationTraceStep]:
        return (
            _invalid_step(
                RULE_BG_MOST_5_47.rule_id,
                jurisdiction_mode,
                inputs_47,
                "MPa",
                code,
                message,
                field_name,
            ),
            _invalid_step(
                RULE_BG_MOST_5_46.rule_id,
                jurisdiction_mode,
                inputs_46,
                "mm^2",
                code,
                message,
                field_name,
            ),
        )

    for param_name, param_val in (
        ("b_mm", b_mm),
        ("d_mm", d_mm),
        ("mu_nmm", mu_nmm),
        ("fc_prime_mpa", fc_prime_mpa),
        ("fy_mpa", fy_mpa),
    ):
        if (
            isinstance(param_val, bool)
            or not isinstance(param_val, (int, float))
            or not math.isfinite(float(param_val))
            or float(param_val) <= 0.0
        ):
            return _invalid_pair(
                f"INVALID_{param_name.upper()}",
                f"{param_name} must be finite and > 0, got {param_val}.",
                param_name,
            )

    if (
        isinstance(phi, bool)
        or not isinstance(phi, (int, float))
        or not math.isfinite(float(phi))
        or float(phi) <= 0.0
        or float(phi) > 1.0
    ):
        return _invalid_pair(
            "INVALID_PHI",
            f"phi must be finite and in (0, 1], got {phi}.",
            "phi",
        )

    if kn_override_mpa is not None and (
        isinstance(kn_override_mpa, bool)
        or not isinstance(kn_override_mpa, (int, float))
        or not math.isfinite(float(kn_override_mpa))
        or float(kn_override_mpa) <= 0.0
    ):
        return _invalid_pair(
            "INVALID_KN_OVERRIDE",
            f"kn_override_mpa must be finite and > 0 MPa when supplied, got {kn_override_mpa}.",
            "kn_override_mpa",
        )

    if rho_override is not None and (
        isinstance(rho_override, bool)
        or not isinstance(rho_override, (int, float))
        or not math.isfinite(float(rho_override))
        or float(rho_override) <= 0.0
    ):
        return _invalid_pair(
            "INVALID_RHO_OVERRIDE",
            f"rho_override must be finite and > 0 when supplied, got {rho_override}.",
            "rho_override",
        )

    try:
        bd2_mm3 = b_mm * (d_mm ** 2)
        kn_exact_mpa = mu_nmm / (phi * bd2_mm3)
    except (ZeroDivisionError, OverflowError):
        return _invalid_pair(
            "NUMERICAL_OVERFLOW_IN_SECTION_PARAMETER",
            "Numerical overflow or invalid division while computing b*d^2 and kn.",
            "d_mm",
        )

    if not math.isfinite(bd2_mm3) or bd2_mm3 <= 0.0 or not math.isfinite(kn_exact_mpa) or kn_exact_mpa <= 0.0:
        return _invalid_pair(
            "NUMERICAL_OVERFLOW_IN_SECTION_PARAMETER",
            "Computed b*d^2 or kn is non-finite or non-positive.",
            "d_mm",
        )

    kn_used_mpa = kn_override_mpa if kn_override_mpa is not None else kn_exact_mpa

    step_47 = CalculationTraceStep.from_rule(
        gate_47.rule,
        normalized_inputs=inputs_47,
        intermediate_values={"bd2_mm3": bd2_mm3, "kn_exact_mpa": kn_exact_mpa},
        final_result=kn_used_mpa,
        unit="MPa",
        outcome=EvaluationOutcome.COMPUTED,
        diagnostics=(),
        message=f"Computed required kn = {kn_used_mpa:.4f} MPa from BG-MOST-5-47.",
    )

    try:
        discriminant = (fc_prime_mpa ** 2) - 4.0 * (
            BG_MOST_5_46_OMEGA_COEFF * fc_prime_mpa
        ) * kn_used_mpa
    except OverflowError:
        err_step = _invalid_step(
            RULE_BG_MOST_5_46.rule_id,
            jurisdiction_mode,
            inputs_46,
            "mm^2",
            "NUMERICAL_OVERFLOW_IN_QUADRATIC",
            "Numerical overflow while computing discriminant for BG-MOST-5-46.",
            "fc_prime_mpa",
        )
        return (step_47, err_step)

    if not math.isfinite(discriminant) or discriminant < 0.0:
        err_step = _invalid_step(
            RULE_BG_MOST_5_46.rule_id,
            jurisdiction_mode,
            inputs_46,
            "mm^2",
            "SECTION_OVERSTRESSED_FOR_SINGLE_REINFORCEMENT",
            f"Required kn ({kn_used_mpa:.4f} MPa) exceeds quadratic limit for f'c={fc_prime_mpa} MPa.",
            "mu_nmm",
        )
        return (step_47, err_step)

    omega = (fc_prime_mpa - math.sqrt(discriminant)) / (
        2.0 * BG_MOST_5_46_OMEGA_COEFF * fc_prime_mpa
    )
    rho_exact = omega * fc_prime_mpa / fy_mpa
    rho_used = rho_override if rho_override is not None else rho_exact
    as_req_mm2 = rho_used * b_mm * d_mm

    step_46 = CalculationTraceStep.from_rule(
        gate_46.rule,
        normalized_inputs=inputs_46,
        intermediate_values={
            "kn_mpa": kn_used_mpa,
            "omega": omega,
            "rho_exact": rho_exact,
            "rho_used": rho_used,
            "as_required_mm2": as_req_mm2,
        },
        final_result=as_req_mm2,
        unit="mm^2",
        outcome=EvaluationOutcome.COMPUTED,
        diagnostics=(),
        message=f"Solved required As = {as_req_mm2:.2f} mm^2 from BG-MOST-5-46.",
    )
    return (step_47, step_46)


def _evaluate_depth_estimate(
    rule_id: str,
    deduction_mm: float,
    h_mm: float,
    *,
    geometry: Optional[BeamGeometry] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
) -> CalculationTraceStep:
    raw_inputs: Dict[str, ScalarInputValue] = {
        "h_mm": h_mm,
        "deduction_mm": deduction_mm,
        "has_explicit_d": geometry.d_effective_mm is not None if geometry is not None else False,
    }
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")

    if geometry is not None:
        if geometry.d_effective_mm is not None:
            return _invalid_step(
                rule_id,
                jurisdiction_mode,
                raw_inputs,
                "mm",
                "CANNOT_OVERRIDE_EXPLICIT_EFFECTIVE_DEPTH",
                (
                    f"Rule '{rule_id}' is an initial estimation utility only and cannot "
                    f"replace explicit d_effective_mm ({geometry.d_effective_mm} mm)."
                ),
                "d_effective_mm",
            )
        d_res = resolve_effective_depth(geometry, rule_id=rule_id)
        if d_res.is_valid and d_res.d_mm is not None:
            return _invalid_step(
                rule_id,
                jurisdiction_mode,
                raw_inputs,
                "mm",
                "CANNOT_OVERRIDE_GEOMETRIC_EFFECTIVE_DEPTH",
                (
                    f"Rule '{rule_id}' is an initial estimation utility only and cannot "
                    f"replace effective depth ({d_res.d_mm} mm) determinable from actual "
                    "reinforcement geometry."
                ),
                "tension_rebar_groups",
            )

    if not math.isfinite(h_mm) or h_mm <= deduction_mm:
        return _invalid_step(
            rule_id,
            jurisdiction_mode,
            raw_inputs,
            "mm",
            "INVALID_HEIGHT_FOR_ESTIMATE",
            f"h_mm ({h_mm} mm) must be finite and > {deduction_mm} mm for {rule_id}.",
            "h_mm",
        )

    d_est_mm = h_mm - deduction_mm
    est_diag = EngineeringDiagnostic(
        code="PRACTICAL_DEPTH_ESTIMATE_USED",
        severity=DiagnosticSeverity.WARNING,
        message=(
            f"Estimated d = {d_est_mm:.2f} mm using {rule_id} (h - {deduction_mm:.0f} mm); "
            "initial sizing estimate only — final d must be recalculated from actual detailing."
        ),
        rule_id=rule_id,
    )
    return CalculationTraceStep.from_rule(
        gate.rule,
        normalized_inputs=raw_inputs,
        intermediate_values={"h_mm": h_mm, "deduction_mm": deduction_mm, "d_estimated_mm": d_est_mm},
        final_result=d_est_mm,
        unit="mm",
        outcome=EvaluationOutcome.COMPUTED,
        diagnostics=(est_diag,),
        message=est_diag.message,
    )


def evaluate_mostofinejad_eq_5_48a_d_estimate(
    h_mm: float,
    *,
    geometry: Optional[BeamGeometry] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
) -> CalculationTraceStep:
    """Evaluate BG-MOST-5-48A: d ≈ h - 65 mm (1-layer initial sizing estimate only)."""
    return _evaluate_depth_estimate(
        RULE_BG_MOST_5_48A.rule_id,
        BG_MOST_5_48A_DEPTH_DEDUCTION_MM,
        h_mm,
        geometry=geometry,
        jurisdiction_mode=jurisdiction_mode,
    )


def evaluate_mostofinejad_eq_5_48b_d_estimate(
    h_mm: float,
    *,
    geometry: Optional[BeamGeometry] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
) -> CalculationTraceStep:
    """Evaluate BG-MOST-5-48B: d ≈ h - 90 mm (2-layer initial sizing estimate only)."""
    return _evaluate_depth_estimate(
        RULE_BG_MOST_5_48B.rule_id,
        BG_MOST_5_48B_DEPTH_DEDUCTION_MM,
        h_mm,
        geometry=geometry,
        jurisdiction_mode=jurisdiction_mode,
    )


def evaluate_mostofinejad_eq_5_49_alpha1(
    fc_prime_mpa: float,
    *,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
) -> CalculationTraceStep:
    """Evaluate BG-MOST-5-49 (CSA A23.3-14 reference): alpha_1 = max(0.85 - 0.0015*f'c, 0.67)."""
    rule_id = RULE_BG_MOST_5_49.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {"fc_prime_mpa": fc_prime_mpa}
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="dimensionless")

    if not math.isfinite(fc_prime_mpa) or fc_prime_mpa <= 0.0:
        return _invalid_step(
            rule_id,
            jurisdiction_mode,
            raw_inputs,
            "dimensionless",
            "INVALID_FC_PRIME",
            f"fc_prime_mpa must be finite and > 0 MPa, got {fc_prime_mpa}.",
            "fc_prime_mpa",
        )

    linear_term = BG_MOST_5_49_BASE - BG_MOST_5_49_FC_SLOPE * fc_prime_mpa
    alpha_1 = max(linear_term, BG_MOST_5_49_MIN)
    return CalculationTraceStep.from_rule(
        gate.rule,
        normalized_inputs=raw_inputs,
        intermediate_values={"linear_term": linear_term, "alpha_1": alpha_1},
        final_result=alpha_1,
        unit="dimensionless",
        outcome=EvaluationOutcome.COMPUTED,
        diagnostics=(),
        message=f"Computed CSA reference alpha_1 = {alpha_1:.4f} under BG-MOST-5-49.",
    )


def evaluate_mostofinejad_eq_5_50_beta1(
    fc_prime_mpa: float,
    *,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
) -> CalculationTraceStep:
    """Evaluate BG-MOST-5-50 (CSA A23.3-14 reference): beta_1 = max(0.97 - 0.0025*f'c, 0.67)."""
    rule_id = RULE_BG_MOST_5_50.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {"fc_prime_mpa": fc_prime_mpa}
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="dimensionless")

    if not math.isfinite(fc_prime_mpa) or fc_prime_mpa <= 0.0:
        return _invalid_step(
            rule_id,
            jurisdiction_mode,
            raw_inputs,
            "dimensionless",
            "INVALID_FC_PRIME",
            f"fc_prime_mpa must be finite and > 0 MPa, got {fc_prime_mpa}.",
            "fc_prime_mpa",
        )

    linear_term = BG_MOST_5_50_BASE - BG_MOST_5_50_FC_SLOPE * fc_prime_mpa
    beta_1 = max(linear_term, BG_MOST_5_50_MIN)
    return CalculationTraceStep.from_rule(
        gate.rule,
        normalized_inputs=raw_inputs,
        intermediate_values={"linear_term": linear_term, "beta_1": beta_1},
        final_result=beta_1,
        unit="dimensionless",
        outcome=EvaluationOutcome.COMPUTED,
        diagnostics=(),
        message=f"Computed CSA reference beta_1 = {beta_1:.4f} under BG-MOST-5-50.",
    )


def evaluate_mostofinejad_eq_5_54_a(
    *,
    as_mm2: float,
    fy_mpa: float,
    fc_prime_mpa: float,
    b_mm: float,
    alpha_1: float,
    phi_s: float,
    phi_c: float,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
) -> CalculationTraceStep:
    """Evaluate BG-MOST-5-54 (CSA reference): a = (As * phi_s * fy) / (alpha_1 * phi_c * f'c * b)."""
    rule_id = RULE_BG_MOST_5_54.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "as_mm2": as_mm2,
        "fy_mpa": fy_mpa,
        "fc_prime_mpa": fc_prime_mpa,
        "b_mm": b_mm,
        "alpha_1": alpha_1,
        "phi_s": phi_s,
        "phi_c": phi_c,
    }
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")

    for name, val in raw_inputs.items():
        if not isinstance(val, (int, float)) or not math.isfinite(float(val)) or float(val) <= 0.0:
            return _invalid_step(
                rule_id,
                jurisdiction_mode,
                raw_inputs,
                "mm",
                f"INVALID_{name.upper()}",
                f"{name} must be finite and > 0, got {val}.",
                name,
            )

    tension_force_n = as_mm2 * phi_s * fy_mpa
    denom_n_per_mm = alpha_1 * phi_c * fc_prime_mpa * b_mm
    a_mm = tension_force_n / denom_n_per_mm
    return CalculationTraceStep.from_rule(
        gate.rule,
        normalized_inputs=raw_inputs,
        intermediate_values={
            "tension_force_n": tension_force_n,
            "compression_per_mm_n": denom_n_per_mm,
            "a_mm": a_mm,
        },
        final_result=a_mm,
        unit="mm",
        outcome=EvaluationOutcome.COMPUTED,
        diagnostics=(),
        message=f"Computed CSA reference stress-block depth a = {a_mm:.4f} mm under BG-MOST-5-54.",
    )


def evaluate_mostofinejad_eq_5_55_mr(
    *,
    as_mm2: float,
    fy_mpa: float,
    d_mm: float,
    a_mm: float,
    phi_s: float,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
) -> CalculationTraceStep:
    """Evaluate BG-MOST-5-55 (CSA reference): Mr = As * phi_s * fy * (d - a / 2) (N*mm)."""
    rule_id = RULE_BG_MOST_5_55.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "as_mm2": as_mm2,
        "fy_mpa": fy_mpa,
        "d_mm": d_mm,
        "a_mm": a_mm,
        "phi_s": phi_s,
    }
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="N*mm")

    for name, val in raw_inputs.items():
        if not isinstance(val, (int, float)) or not math.isfinite(float(val)) or float(val) <= 0.0:
            return _invalid_step(
                rule_id,
                jurisdiction_mode,
                raw_inputs,
                "N*mm",
                f"INVALID_{name.upper()}",
                f"{name} must be finite and > 0, got {val}.",
                name,
            )

    lever_arm_z_mm = d_mm - 0.5 * a_mm
    if lever_arm_z_mm <= 0.0:
        return _invalid_step(
            rule_id,
            jurisdiction_mode,
            raw_inputs,
            "N*mm",
            "IMPOSSIBLE_LEVER_ARM",
            f"Lever arm d - a/2 ({lever_arm_z_mm} mm) must be > 0 mm.",
            "a_mm",
        )

    tension_force_n = as_mm2 * phi_s * fy_mpa
    mr_nmm = tension_force_n * lever_arm_z_mm
    return CalculationTraceStep.from_rule(
        gate.rule,
        normalized_inputs=raw_inputs,
        intermediate_values={
            "tension_force_n": tension_force_n,
            "lever_arm_z_mm": lever_arm_z_mm,
            "mr_nmm": mr_nmm,
        },
        final_result=mr_nmm,
        unit="N*mm",
        outcome=EvaluationOutcome.COMPUTED,
        diagnostics=(),
        message=f"Computed CSA reference Mr = {mr_nmm:.2f} N*mm under BG-MOST-5-55.",
    )


def evaluate_mostofinejad_eq_5_56_mr_rho(
    *,
    rho: float,
    fy_mpa: float,
    fc_prime_mpa: float,
    b_mm: float,
    d_mm: float,
    alpha_1: float,
    phi_s: float,
    phi_c: float,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
) -> CalculationTraceStep:
    """Evaluate BG-MOST-5-56 (CSA reference): Mr = rho*phi_s*fy*b*d^2*(1 - rho*phi_s*fy/(2*alpha_1*phi_c*f'c))."""
    rule_id = RULE_BG_MOST_5_56.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "rho": rho,
        "fy_mpa": fy_mpa,
        "fc_prime_mpa": fc_prime_mpa,
        "b_mm": b_mm,
        "d_mm": d_mm,
        "alpha_1": alpha_1,
        "phi_s": phi_s,
        "phi_c": phi_c,
    }
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="N*mm")

    for name, val in raw_inputs.items():
        if not isinstance(val, (int, float)) or not math.isfinite(float(val)) or float(val) <= 0.0:
            return _invalid_step(
                rule_id,
                jurisdiction_mode,
                raw_inputs,
                "N*mm",
                f"INVALID_{name.upper()}",
                f"{name} must be finite and > 0, got {val}.",
                name,
            )

    ratio_term = (rho * phi_s * fy_mpa) / (2.0 * alpha_1 * phi_c * fc_prime_mpa)
    if ratio_term >= 1.0:
        return _invalid_step(
            rule_id,
            jurisdiction_mode,
            raw_inputs,
            "N*mm",
            "INVALID_STRESS_RATIO_TERM",
            f"Term rho*phi_s*fy / (2*alpha_1*phi_c*f'c) ({ratio_term}) must be < 1.0.",
            "rho",
        )

    mr_nmm = rho * phi_s * fy_mpa * b_mm * (d_mm ** 2) * (1.0 - ratio_term)
    return CalculationTraceStep.from_rule(
        gate.rule,
        normalized_inputs=raw_inputs,
        intermediate_values={"ratio_term": ratio_term, "mr_nmm": mr_nmm},
        final_result=mr_nmm,
        unit="N*mm",
        outcome=EvaluationOutcome.COMPUTED,
        diagnostics=(),
        message=f"Computed CSA reference Mr = {mr_nmm:.2f} N*mm under BG-MOST-5-56.",
    )


def evaluate_mostofinejad_eq_5_61_check(
    *,
    mf_nmm: float,
    mr_nmm: float,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
) -> CalculationTraceStep:
    """Evaluate BG-MOST-5-61 (reference resistance check): Mf <= Mr."""
    rule_id = RULE_BG_MOST_5_61.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {"mf_nmm": mf_nmm, "mr_nmm": mr_nmm}
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="N*mm")

    if not math.isfinite(mf_nmm) or mf_nmm < 0.0:
        return _invalid_step(
            rule_id,
            jurisdiction_mode,
            raw_inputs,
            "N*mm",
            "INVALID_MF",
            f"mf_nmm must be finite and >= 0 N*mm, got {mf_nmm}.",
            "mf_nmm",
        )
    if not math.isfinite(mr_nmm) or mr_nmm <= 0.0:
        return _invalid_step(
            rule_id,
            jurisdiction_mode,
            raw_inputs,
            "N*mm",
            "INVALID_MR",
            f"mr_nmm must be finite and > 0 N*mm, got {mr_nmm}.",
            "mr_nmm",
        )

    utilization = mf_nmm / mr_nmm
    outcome = EvaluationOutcome.PASS if mf_nmm <= mr_nmm else EvaluationOutcome.FAIL
    diagnostics: List[EngineeringDiagnostic] = []
    if outcome == EvaluationOutcome.FAIL:
        diagnostics.append(
            EngineeringDiagnostic(
                code="REFERENCE_MOMENT_DEMAND_EXCEEDS_RESISTANCE",
                severity=DiagnosticSeverity.ERROR,
                message=f"Reference check FAIL: Mf ({mf_nmm:.2f} N*mm) > Mr ({mr_nmm:.2f} N*mm).",
                rule_id=rule_id,
            )
        )
    return CalculationTraceStep.from_rule(
        gate.rule,
        normalized_inputs=raw_inputs,
        intermediate_values={
            "mf_nmm": mf_nmm,
            "mr_nmm": mr_nmm,
            "utilization_ratio": utilization,
        },
        final_result=mr_nmm,
        unit="N*mm",
        outcome=outcome,
        diagnostics=diagnostics,
        message=f"Reference check BG-MOST-5-61 ({outcome.value}): Mf={mf_nmm:.2f} N*mm, Mr={mr_nmm:.2f} N*mm.",
    )


def evaluate_mostofinejad_blocked_equation(
    rule_id: str,
    *,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    normalized_inputs: Optional[Dict[str, ScalarInputValue]] = None,
) -> CalculationTraceStep:
    """Route any blocked Mostofinejad equation (5-44, 5-45, 5-51..5-53, 5-57..5-60, 5-62) through gatekeeper."""
    return build_blocked_workflow_trace(
        rule_id,
        active_jurisdiction=jurisdiction_mode,
        normalized_inputs=normalized_inputs,
    )
