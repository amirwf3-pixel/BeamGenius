"""Mabhas 9 (1399) verified Phase 2F Stage C development-length evaluators
(Clause 9-21-3 ONLY).

Promoted 2026-10-05 after visual verification of the committed evidence scan
``git show df8067a:phase2f-source-442-472/page-NNN.jpg`` (Printed pp. 424-436 /
PDF pp. 444-456, canonical offset PDF = printed + 20), recorded in
``docs/PHASE2_SOURCE_VERIFICATION_MATRIX.md`` sections 4B/4C and
``docs/VERIFIED_RULES.md``.

Implemented rules (deterministic evaluation; no strength-reduction factor phi
is ever applied in development-length equations per Clause 9-21-3-1-4):

- ``BG-DEV-LENGTH-TENSION-001``: deformed bars/wires in tension, general
  relation Eq. (9-21-1) with K_tr Eq. (9-21-2), confinement cap 2.5,
  Table 9-21-3 factors, 300 mm floor — Clause 9-21-3-1/-2
- ``BG-DEV-LENGTH-TENSION-TABLE-001``: simplified tension development length
  of Table 9-21-4 — Clause 9-21-3-2-3
- ``BG-DEV-LENGTH-HOOKED-001``: standard-hook development length Eq. (9-21-3)
  with Table 9-21-5 factors — Clause 9-21-3-3
- ``BG-DEV-LENGTH-HEADED-001``: headed-bar development length Eq. (9-21-4)
  with Table 9-21-6 factors and the 9-21-3-4-1 applicability limits —
  Clause 9-21-3-4
- ``BG-DEV-MECH-ANCHOR-001``: mechanical anchorage admissibility gate —
  Clause 9-21-3-5 (no length equation is given by the clause and none is
  invented)
- ``BG-DEV-WIRE-DEFORMED-001``: welded deformed-wire mesh Eq. (9-21-5) with
  psi_w of Eqs. (9-21-6-الف/ب) — Clause 9-21-3-6
- ``BG-DEV-WIRE-PLAIN-001``: welded plain-wire mesh Eq. (9-21-7) with the
  150 mm / s+50 mm floors and two-cross-wire minimum — Clause 9-21-3-7
- ``BG-DEV-LENGTH-COMPRESSION-001``: compression development length of
  Clause 9-21-3-8-1-الف with the psi_r confinement factor, 200 mm floor.

Clause 9-21-3-9 excess-reinforcement reduction is implemented only for the
equation cases the clause explicitly lists (9-21-3-2-1-الف, 9-21-3-6-1-الف,
9-21-3-7-1-الف, 9-21-3-8-1-الف), only when every 9-21-3-9-2 prohibition is
absent, and always subject to the preserved floors of 9-21-3-9-1 tail. It is
never offered for hooked/headed/mechanical anchorage (9-21-3-9-2-ث).

VERIFY_PENDING branch (preserved, never silenced): the compression psi_r
«تنگ سیمی» (wire tie, diameter > 12 mm at spacing < 100 mm) branch keeps its
source-record noun ambiguity status; selecting it returns
UNVERIFIED_RULE_BLOCKED (``VERIFY_PENDING_CONFINEMENT_TIE_CLASS``).

Deterministic contract of every evaluator (in order):

1. Central Gatekeeper check (``evaluate_rule_gate``) runs FIRST.
2. Missing required engineering inputs return ``UNVERIFIED_RULE_BLOCKED``
   (``MISSING_*`` diagnostics — missing values are never assumed or
   defaulted).
3. Malformed input values (non-finite, non-positive, wrong type or unknown
   enum) return ``INVALID_INPUT``.
4. Verified prohibition/context violations return ``FAIL`` with explicit
   codes; explicitly routed-out configurations return ``NOT_APPLICABLE``.
5. A BLOCKED result can never become PASS.
6. Every step attaches the registry ``RuleReference``, a
   ``CalculationTraceStep`` with all intermediate values, and explicit
   diagnostic codes.

Import explicitly, e.g.::

    from beamgenius.engine.development_length_mabhas9 import (
        evaluate_dev_length_tension,
    )
"""

from __future__ import annotations

import math
from typing import Dict, List, Mapping, Optional, Tuple, Type, TypeVar, Union

from beamgenius.domain.enums import (
    AnchorConnectionClass,
    BarCoatingClass,
    CompressionConfinementClass,
    DiagnosticSeverity,
    EvaluationOutcome,
    JurisdictionMode,
    SteelGradeClass,
    WireSurfaceClass,
    ConcreteWeightClass,
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
    RULE_BG_DEV_COMPRESSION_001,
    RULE_BG_DEV_LENGTH_HEADED_001,
    RULE_BG_DEV_LENGTH_HOOKED_001,
    RULE_BG_DEV_LENGTH_TENSION_001,
    RULE_BG_DEV_LENGTH_TENSION_TABLE_001,
    RULE_BG_DEV_MECH_ANCHOR_001,
    RULE_BG_DEV_WIRE_DEFORMED_001,
    RULE_BG_DEV_WIRE_PLAIN_001,
)
from beamgenius.registry.gatekeeper import GatekeeperDecision, evaluate_rule_gate

# ----------------------------------------------------------------------------
# Verified constants (Mabhas 9, 1399 5th ed., Clause 9-21-3; evidence scan
# phase2f-source-442-472, canonical offset PDF = printed + 20)
# ----------------------------------------------------------------------------

# Clause 9-21-3-1-5 (Printed p. 425 / PDF p. 445): sqrt(f'c) ceiling
MAX_SQRT_FC_MPA: float = 8.3
# Clause 9-21-3-1-6 (Printed p. 425 / PDF p. 445): lambda weight factors
LAMBDA_NORMAL_WEIGHT: float = 1.0
LAMBDA_LIGHTWEIGHT: float = 0.75
# Eq. (9-21-2) (Printed p. 426 / PDF p. 446)
CONFINEMENT_INDEX_MAX: float = 2.5
K_TR_FACTOR: float = 40.0
# Clause 9-21-3-2-1-ب (Printed p. 426 / PDF p. 446)
MIN_LD_TENSION_MM: float = 300.0
# Eq. (9-21-1) (Printed p. 425-426 / PDF p. 445-446)
FY_FACTOR_TENSION: float = 0.9
# Table 9-21-3 (Printed p. 427 / PDF p. 447)
PSI_G_HIGH_GRADE: float = 1.15
PSI_G_BASE_GRADE: float = 1.0
PSI_E_EPOXY_TIGHT: float = 1.5
PSI_E_EPOXY_OTHER: float = 1.2
PSI_E_UNCOATED: float = 1.0
PSI_S_SMALL: float = 0.8
PSI_S_BASE: float = 1.0
PSI_S_SMALL_DB_LIMIT_MM: float = 20.0
PSI_T_TOP: float = 1.3
PSI_T_OTHER: float = 1.0
PSI_TE_MAX: float = 1.7
EPOXY_TIGHT_COVER_RATIO: float = 3.0
EPOXY_TIGHT_SPACING_RATIO: float = 6.0
# Table 9-21-4 divisors (Printed p. 428 / PDF p. 448)
TABLE_9_21_4_DIVISOR_CONFINED_SMALL: float = 2.1
TABLE_9_21_4_DIVISOR_CONFINED_LARGE: float = 1.7
TABLE_9_21_4_DIVISOR_OTHER_SMALL: float = 1.4
TABLE_9_21_4_DIVISOR_OTHER_LARGE: float = 1.1
# Eq. (9-21-3) hooked (Printed p. 428 / PDF p. 448); floor (3-3-1-ب)
FY_FACTOR_HOOKED: float = 0.043
DB_EXPONENT_HOOKED: float = 1.5
MIN_LDH_DB_FACTOR: float = 8.0
MIN_LDH_MM: float = 150.0
# Table 9-21-5 (Printed p. 430 / PDF p. 450)
PSI_E_HOOKED_EPOXY: float = 1.2
PSI_E_HOOKED_UNCOATED: float = 1.0
PSI_R_HOOKED_CONFINED: float = 1.0
PSI_R_HOOKED_OTHER: float = 1.6
PSI_O_ANCHOR_CORE: float = 1.0
PSI_O_ANCHOR_OTHER: float = 1.25
PSI_R_HOOKED_DB_LIMIT_MM: float = 34.0
PSI_R_HOOKED_ATH_RATIO: float = 0.4
PSI_R_HOOKED_SPACING_RATIO: float = 6.0
SIDE_COVER_ABS_LIMIT_MM: float = 65.0
SIDE_COVER_DB_RATIO: float = 6.0
PSI_C_FC_LIMIT_MPA: float = 42.0
PSI_C_DIVISOR: float = 105.0
PSI_C_OFFSET: float = 0.6
# Eq. (9-21-4) headed (Printed p. 431 / PDF p. 451); floor (3-4-2-ب)
FY_FACTOR_HEADED: float = 0.032
DB_EXPONENT_HEADED: float = 1.5
MIN_LDT_HEADED_DB_FACTOR: float = 8.0
MIN_LDT_HEADED_MM: float = 150.0
# Clause 9-21-3-4-1 limits (Printed pp. 430-431 / PDF pp. 450-451)
HEADED_DB_LIMIT_MM: float = 34.0
HEADED_ABRG_FACTOR: float = 4.0
HEADED_COVER_RATIO: float = 2.0
HEADED_SPACING_RATIO: float = 3.0
# Table 9-21-6 (Printed p. 432 / PDF p. 452)
PSI_P_HEADED_QUALIFIED: float = 1.0
PSI_P_HEADED_OTHER: float = 1.6
PSI_P_ATT_RATIO: float = 0.3
PSI_P_SPACING_RATIO: float = 6.0
# Clause 9-21-3-6 (Printed pp. 433-434 / PDF pp. 453-454)
WIRE_DEFORMED_MAX_DB_MM: float = 16.0
MIN_LD_WIRE_DEFORMED_MM: float = 200.0
PSI_W_FY_OFFSET_MPA: float = 240.0
PSI_W_SPACING_DB_FACTOR: float = 5.0
CROSS_WIRE_MIN_DISTANCE_MM: float = 50.0
# Clause 9-21-3-7 plain wire (Printed pp. 434-435 / PDF pp. 454-455)
FY_FACTOR_WIRE_PLAIN: float = 3.3
MIN_LD_WIRE_PLAIN_MM: float = 150.0
MIN_CROSS_WIRES_IN_LD: int = 2
WIRE_PLAIN_OVERHANG_MM: float = 50.0
# Clause 9-21-3-8 compression (Printed p. 435 / PDF p. 455)
FY_FACTOR_COMPRESSION_A: float = 0.24
FY_FACTOR_COMPRESSION_B: float = 0.043
PSI_R_COMPRESSION_CONFINED: float = 0.75
PSI_R_COMPRESSION_OTHER: float = 1.0
MIN_LD_COMPRESSION_MM: float = 200.0
CIRCULAR_TIE_MIN_DIAMETER_MM: float = 6.0
CONFINEMENT_MAX_SPACING_MM: float = 100.0

_E = TypeVar("_E", SteelGradeClass, ConcreteWeightClass, BarCoatingClass,
             WireSurfaceClass, AnchorConnectionClass,
             CompressionConfinementClass)


# ----------------------------------------------------------------------------
# Shared validation & factor helpers
# ----------------------------------------------------------------------------

def _enum_opt(value: Optional[object]) -> Optional[str]:
    """Return the enum literal for normalized_inputs, tolerating wrong types."""
    if value is None:
        return None
    return getattr(value, "value", str(value))


def _lambda_of(weight: ConcreteWeightClass) -> float:
    """Verified lambda weights of Clause 9-21-3-1-6."""
    if weight is ConcreteWeightClass.NORMAL_WEIGHT:
        return LAMBDA_NORMAL_WEIGHT
    return LAMBDA_LIGHTWEIGHT


def _sqrt_fc_used(fc_mpa: float) -> float:
    """sqrt(f'c) with the Clause 9-21-3-1-5 ceiling of 8.3 MPa."""
    return min(math.sqrt(fc_mpa), MAX_SQRT_FC_MPA)


def _psi_g_of(grade: SteelGradeClass) -> float:
    """Table 9-21-3 psi_g: 1.0 for S340/S350/S400/S420, 1.15 for S500/S520."""
    if grade in (SteelGradeClass.S500, SteelGradeClass.S520):
        return PSI_G_HIGH_GRADE
    return PSI_G_BASE_GRADE


def _psi_s_of(db_mm: float) -> float:
    """Table 9-21-3 psi_s: 0.8 for d_b < 20 mm, else 1.0."""
    if db_mm < PSI_S_SMALL_DB_LIMIT_MM:
        return PSI_S_SMALL
    return PSI_S_BASE


def _psi_e_tension(coating: BarCoatingClass, db_mm: float,
                   concrete_cover_mm: float, clear_spacing_mm: float) -> float:
    """Table 9-21-3 psi_e for tension development (1.5 / 1.2 / 1.0)."""
    if coating is BarCoatingClass.EPOXY_OR_DUAL_COATED:
        if (concrete_cover_mm < EPOXY_TIGHT_COVER_RATIO * db_mm
                or clear_spacing_mm < EPOXY_TIGHT_SPACING_RATIO * db_mm):
            return PSI_E_EPOXY_TIGHT
        return PSI_E_EPOXY_OTHER
    return PSI_E_UNCOATED


def _psi_c_of(fc_mpa: float) -> float:
    """Hooked/headed psi_c: f'c/105 + 0.6 for f'c < 42 MPa, else 1.0."""
    if fc_mpa < PSI_C_FC_LIMIT_MPA:
        return fc_mpa / PSI_C_DIVISOR + PSI_C_OFFSET
    return 1.0


def _req_positive(
    value: Optional[float],
    *,
    field: str,
    rule: RuleReference,
) -> Tuple[Optional[float], List[EngineeringDiagnostic]]:
    """Missing -> BLOCKED diagnostic; malformed -> ERROR diagnostic."""
    if value is None:
        return None, [_missing_input_diagnostic(
            "MISSING_" + field.upper(),
            (f"The engineering input '{field}' is required; missing required "
             "inputs are never assumed or defaulted -> BLOCKED."),
            rule=rule, field_name=field)]
    if not math.isfinite(value) or value <= 0.0:
        return None, [_malformed_value_diagnostic(
            value, field_name=field, rule=rule)]
    return float(value), []


def _req_bool(
    value: Optional[object],
    *,
    field: str,
    rule: RuleReference,
) -> Tuple[Optional[bool], List[EngineeringDiagnostic]]:
    """Missing -> BLOCKED diagnostic; non-bool -> ERROR diagnostic."""
    if value is None:
        return None, [_missing_input_diagnostic(
            "MISSING_" + field.upper(),
            (f"The boolean engineering input '{field}' is required; missing "
             "required inputs are never assumed or defaulted -> BLOCKED."),
            rule=rule, field_name=field)]
    if not isinstance(value, bool):
        return None, [EngineeringDiagnostic(
            code="INVALID_" + field.upper(),
            severity=DiagnosticSeverity.ERROR,
            message=(f"Input '{field}' must be a strict boolean, got "
                     f"{value!r}."),
            rule_id=rule.rule_id, field_name=field)]
    return bool(value), []


def _req_int(
    value: Optional[Union[int, float]],
    *,
    field: str,
    rule: RuleReference,
) -> Tuple[Optional[int], List[EngineeringDiagnostic]]:
    """Missing -> BLOCKED; bool/non-integral -> INVALID."""
    if value is None:
        return None, [_missing_input_diagnostic(
            "MISSING_" + field.upper(),
            (f"The engineering input '{field}' is required; missing required "
             "inputs are never assumed or defaulted -> BLOCKED."),
            rule=rule, field_name=field)]
    if type(value) is bool:
        ok = False
    elif type(value) is int:
        ok = True
    elif isinstance(value, float) and math.isfinite(value) and value.is_integer():
        ok = True
    else:
        ok = False
    if not ok or int(value) < 1:
        return None, [EngineeringDiagnostic(
            code="INVALID_" + field.upper(),
            severity=DiagnosticSeverity.ERROR,
            message=(f"Input '{field}' must be an integer >= 1, got "
                     f"{value!r}."),
            rule_id=rule.rule_id, field_name=field)]
    return int(value), []


def _req_enum(
    value: Optional[object],
    *,
    enum_cls: Type[_E],
    field: str,
    rule: RuleReference,
) -> Tuple[Optional[_E], List[EngineeringDiagnostic]]:
    """Missing -> BLOCKED; not an instance of the enum -> INVALID."""
    if value is None:
        return None, [_missing_input_diagnostic(
            "MISSING_" + field.upper(),
            (f"The typed engineering input '{field}' is required; missing "
             "required inputs are never assumed or defaulted -> BLOCKED."),
            rule=rule, field_name=field)]
    if not isinstance(value, enum_cls):
        valid = ", ".join(member.value for member in enum_cls)
        return None, [EngineeringDiagnostic(
            code="INVALID_" + field.upper(),
            severity=DiagnosticSeverity.ERROR,
            message=(f"Input '{field}' must be a member of "
                     f"{enum_cls.__name__} ({valid}), got {value!r}."),
            rule_id=rule.rule_id, field_name=field)]
    return value, []


def _terminal(
    gate: GatekeeperDecision,
    *,
    raw_inputs: Dict[str, ScalarInputValue],
    diags: List[EngineeringDiagnostic],
) -> Optional[CalculationTraceStep]:
    """Terminate with INVALID_INPUT if any ERROR present, else BLOCKED."""
    if not diags:
        return None
    if any(diag.severity is DiagnosticSeverity.ERROR for diag in diags):
        return _invalid_step(gate, raw_inputs=raw_inputs, diagnostics=diags)
    return _blocked_step(gate, raw_inputs=raw_inputs, diagnostics=diags)


def _apply_excess_reduction(
    *,
    gate: GatekeeperDecision,
    rule: RuleReference,
    raw_inputs: Dict[str, ScalarInputValue],
    ld_equation_mm: float,
    floor_mm: float,
    apply_excess_reinforcement_reduction: Optional[bool],
    as_required_mm2: Optional[float],
    as_provided_mm2: Optional[float],
    at_non_continuous_support: Optional[bool],
    yield_development_required: Optional[bool],
    continuity_required: Optional[bool],
    ductile_seismic_system: Optional[bool],
    pile_head_anchorage: Optional[bool],
    intermediates: Dict[str, float],
) -> Union[float, CalculationTraceStep]:
    """Clause 9-21-3-9 reduction gate; returns final l_d or a terminal step.

    - apply flag is a REQUIRED boolean (never defaulted).
    - When False: final = max(ld_equation, floor) with no reduction.
    - When True: every context boolean of 9-21-3-9-2 is REQUIRED; any True
      context is BLOCKED (``PROHIBITED_EXCESS_REDUCTION_CONTEXT``); the
      required/provided areas are REQUIRED, finite-positive and must satisfy
      as_required <= as_provided (a ratio > 1 would not be a reduction);
      floors of the corresponding ب-clause are preserved after reduction.
    """
    apply_flag, diags = _req_bool(
        apply_excess_reinforcement_reduction,
        field="apply_excess_reinforcement_reduction", rule=rule)
    if diags:
        terminal = _terminal(gate, raw_inputs=raw_inputs, diags=list(diags))
        if terminal is not None:
            return terminal
    assert apply_flag is not None
    ld_final = max(ld_equation_mm, floor_mm)
    intermediates["ld_equation_mm"] = ld_equation_mm
    intermediates["ld_floor_mm"] = floor_mm
    if not apply_flag:
        intermediates["ld_final_mm"] = ld_final
        return ld_final

    fields = [
        ("as_required_mm2", as_required_mm2),
        ("as_provided_mm2", as_provided_mm2),
    ]
    contexts = [
        ("at_non_continuous_support", at_non_continuous_support),
        ("yield_development_required", yield_development_required),
        ("continuity_required", continuity_required),
        ("ductile_seismic_system", ductile_seismic_system),
        ("pile_head_anchorage", pile_head_anchorage),
    ]
    missing_diags: List[EngineeringDiagnostic] = []
    as_req_v: Optional[float] = None
    as_prov_v: Optional[float] = None
    for field, value in fields:
        v, d = _req_positive(value, field=field, rule=rule)
        if d:
            missing_diags.extend(d)
        elif v is not None:
            if field == "as_required_mm2":
                as_req_v = v
            else:
                as_prov_v = v
    context_values: Dict[str, bool] = {}
    for field, value in contexts:
        b, d = _req_bool(value, field=field, rule=rule)
        if d:
            missing_diags.extend(d)
        elif b is not None:
            context_values[field] = b
    if missing_diags:
        terminal = _terminal(gate, raw_inputs=raw_inputs, diags=missing_diags)
        if terminal is not None:
            return terminal
    assert as_req_v is not None and as_prov_v is not None
    if as_req_v > as_prov_v:
        return _invalid_step(
            gate, raw_inputs=raw_inputs,
            diagnostics=[EngineeringDiagnostic(
                code="EXCESS_REDUCTION_REQUIRES_PROVIDED_NOT_BELOW_REQUIRED",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    "Clause 9-21-3-9 grants a reduction by the ratio "
                    "required/provided; as_required_mm2 greater than "
                    "as_provided_mm2 would not be a reduction and cannot be "
                    "applied -> INVALID_INPUT."),
                rule_id=rule.rule_id, field_name="as_required_mm2")])
    for field, presents in sorted(context_values.items()):
        if presents:
            return _blocked_step(
                gate, raw_inputs=raw_inputs,
                diagnostics=[EngineeringDiagnostic(
                    code="PROHIBITED_EXCESS_REDUCTION_CONTEXT",
                    severity=DiagnosticSeverity.BLOCK,
                    message=(
                        f"Clause 9-21-3-9-2 prohibits the excess-reinforcement "
                        f"reduction for the reported context '{field}': the "
                        "reduced development length cannot be computed here -> "
                        "BLOCKED (the unreduced value may still be used from "
                        "an evaluation with the reduction flag False)."),
                    rule_id=rule.rule_id, field_name=field)])
    ratio = as_req_v / as_prov_v
    reduced = ld_equation_mm * ratio
    final_after_floor = max(reduced, floor_mm)
    intermediates["excess_reinforcement_ratio"] = ratio
    intermediates["ld_reduced_mm"] = reduced
    intermediates["ld_final_mm"] = final_after_floor
    return final_after_floor


def _resolve_k_tr(
    *,
    gate: GatekeeperDecision,
    rule: RuleReference,
    raw_inputs: Dict[str, ScalarInputValue],
    apply_k_tr: Optional[bool],
    transverse_area_mm2: Optional[float],
    transverse_spacing_mm: Optional[float],
    developed_bar_count: Optional[Union[int, float]],
) -> Union[float, CalculationTraceStep]:
    """Eq. (9-21-2) K_tr gate: K_tr = 0 is always permitted (9-21-3-2-1)."""
    flag, diags = _req_bool(apply_k_tr, field="apply_k_tr", rule=rule)
    if diags:
        terminal = _terminal(gate, raw_inputs=raw_inputs, diags=list(diags))
        if terminal is not None:
            return terminal
    assert flag is not None
    if not flag:
        return 0.0
    a_tr, d1 = _req_positive(
        transverse_area_mm2, field="transverse_area_mm2", rule=rule)
    s_tr, d2 = _req_positive(
        transverse_spacing_mm, field="transverse_spacing_mm", rule=rule)
    n_dev, d3 = _req_int(
        developed_bar_count, field="developed_bar_count", rule=rule)
    bundled = d1 + d2 + d3
    if bundled:
        terminal = _terminal(gate, raw_inputs=raw_inputs, diags=bundled)
        if terminal is not None:
            return terminal
    assert a_tr is not None and s_tr is not None and n_dev is not None
    return K_TR_FACTOR * a_tr / (s_tr * n_dev)


# ----------------------------------------------------------------------------
# BG-DEV-LENGTH-TENSION-001 — Eq. (9-21-1) general relation
# ----------------------------------------------------------------------------

def evaluate_dev_length_tension(
    *,
    steel_grade: Optional[SteelGradeClass] = None,
    bar_diameter_mm: Optional[float] = None,
    yield_stress_mpa: Optional[float] = None,
    concrete_strength_mpa: Optional[float] = None,
    concrete_weight_class: Optional[ConcreteWeightClass] = None,
    coating_class: Optional[BarCoatingClass] = None,
    top_bar_placement: Optional[bool] = None,
    concrete_cover_mm: Optional[float] = None,
    clear_spacing_mm: Optional[float] = None,
    apply_k_tr: Optional[bool] = None,
    transverse_area_mm2: Optional[float] = None,
    transverse_spacing_mm: Optional[float] = None,
    developed_bar_count: Optional[Union[int, float]] = None,
    apply_excess_reinforcement_reduction: Optional[bool] = None,
    as_required_mm2: Optional[float] = None,
    as_provided_mm2: Optional[float] = None,
    at_non_continuous_support: Optional[bool] = None,
    yield_development_required: Optional[bool] = None,
    continuity_required: Optional[bool] = None,
    ductile_seismic_system: Optional[bool] = None,
    pile_head_anchorage: Optional[bool] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate the Clause 9-21-3-2-1 tension development length Eq. (9-21-1).

    Verified source: Mabhas 9 (1399), Printed pp. 425-427 / PDF pp. 445-447
    (Eq. (9-21-1), Eq. (9-21-2) K_tr, 2.5 cap, 300 mm floor, Table 9-21-3);
    reduction limits Printed pp. 435-436 / PDF pp. 455-456. c_b is resolved
    from the verified definition: min(cover + d_b/2, (clear + d_b)/2).
    """
    rule_id = RULE_BG_DEV_LENGTH_TENSION_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "steel_grade": _enum_opt(steel_grade),
        "bar_diameter_mm": bar_diameter_mm,
        "yield_stress_mpa": yield_stress_mpa,
        "concrete_strength_mpa": concrete_strength_mpa,
        "concrete_weight_class": _enum_opt(concrete_weight_class),
        "coating_class": _enum_opt(coating_class),
        "top_bar_placement": top_bar_placement,
        "concrete_cover_mm": concrete_cover_mm,
        "clear_spacing_mm": clear_spacing_mm,
        "apply_k_tr": apply_k_tr,
        "transverse_area_mm2": transverse_area_mm2,
        "transverse_spacing_mm": transverse_spacing_mm,
        "developed_bar_count": developed_bar_count,
        "apply_excess_reinforcement_reduction": apply_excess_reinforcement_reduction,
        "as_required_mm2": as_required_mm2,
        "as_provided_mm2": as_provided_mm2,
        "at_non_continuous_support": at_non_continuous_support,
        "yield_development_required": yield_development_required,
        "continuity_required": continuity_required,
        "ductile_seismic_system": ductile_seismic_system,
        "pile_head_anchorage": pile_head_anchorage,
    }
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")
    rule = gate.rule

    grade, d = _req_enum(steel_grade, enum_cls=SteelGradeClass,
                         field="steel_grade", rule=rule)
    diags = list(d)
    db, d = _req_positive(bar_diameter_mm, field="bar_diameter_mm", rule=rule)
    diags += d
    fy, d = _req_positive(yield_stress_mpa, field="yield_stress_mpa", rule=rule)
    diags += d
    fc, d = _req_positive(concrete_strength_mpa,
                          field="concrete_strength_mpa", rule=rule)
    diags += d
    weight, d = _req_enum(concrete_weight_class, enum_cls=ConcreteWeightClass,
                          field="concrete_weight_class", rule=rule)
    diags += d
    coating, d = _req_enum(coating_class, enum_cls=BarCoatingClass,
                           field="coating_class", rule=rule)
    diags += d
    top, d = _req_bool(top_bar_placement, field="top_bar_placement", rule=rule)
    diags += d
    cover, d = _req_positive(concrete_cover_mm, field="concrete_cover_mm", rule=rule)
    diags += d
    clear, d = _req_positive(clear_spacing_mm, field="clear_spacing_mm", rule=rule)
    diags += d
    terminal = _terminal(gate, raw_inputs=raw_inputs, diags=diags)
    if terminal is not None:
        return terminal
    assert (grade is not None and db is not None and fy is not None
            and fc is not None and weight is not None and coating is not None
            and top is not None and cover is not None and clear is not None)

    k_tr = _resolve_k_tr(
        gate=gate, rule=rule, raw_inputs=raw_inputs, apply_k_tr=apply_k_tr,
        transverse_area_mm2=transverse_area_mm2,
        transverse_spacing_mm=transverse_spacing_mm,
        developed_bar_count=developed_bar_count)
    if isinstance(k_tr, CalculationTraceStep):
        return k_tr

    c_b = min(cover + db / 2.0, (clear + db) / 2.0)
    conf_index = min((c_b + k_tr) / db, CONFINEMENT_INDEX_MAX)
    psi_t = PSI_T_TOP if top else PSI_T_OTHER
    psi_e = _psi_e_tension(coating, db, cover, clear)
    psi_s = _psi_s_of(db)
    psi_g = _psi_g_of(grade)
    psi_te = min(psi_t * psi_e, PSI_TE_MAX)
    lam = _lambda_of(weight)
    sqrt_fc = _sqrt_fc_used(fc)
    ld_eq = (psi_te * psi_s * psi_g / (lam * conf_index)) * (
        FY_FACTOR_TENSION * fy / sqrt_fc) * db

    intermediates: Dict[str, float] = {
        "psi_t": psi_t, "psi_e": psi_e, "psi_s": psi_s, "psi_g": psi_g,
        "psi_te_capped": psi_te, "lambda": lam, "sqrt_fc_used": sqrt_fc,
        "c_b_mm": c_b, "k_tr_mm": k_tr,
        "confinement_index_capped": conf_index,
    }
    final = _apply_excess_reduction(
        gate=gate, rule=rule, raw_inputs=raw_inputs,
        ld_equation_mm=ld_eq, floor_mm=MIN_LD_TENSION_MM,
        apply_excess_reinforcement_reduction=apply_excess_reinforcement_reduction,
        as_required_mm2=as_required_mm2, as_provided_mm2=as_provided_mm2,
        at_non_continuous_support=at_non_continuous_support,
        yield_development_required=yield_development_required,
        continuity_required=continuity_required,
        ductile_seismic_system=ductile_seismic_system,
        pile_head_anchorage=pile_head_anchorage,
        intermediates=intermediates)
    if isinstance(final, CalculationTraceStep):
        return final
    return CalculationTraceStep.from_rule(
        rule, normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=final, unit="mm", outcome=EvaluationOutcome.COMPUTED,
        diagnostics=(),
        message=(f"Computed tension development length Eq. (9-21-1): l_d = "
                 f"{final:.1f} mm (Eq. value {ld_eq:.1f} mm; floor "
                 f"{MIN_LD_TENSION_MM} mm; Clause 9-21-3-2-1)."))


# ----------------------------------------------------------------------------
# BG-DEV-LENGTH-TENSION-TABLE-001 — Table 9-21-4 simplified provision
# ----------------------------------------------------------------------------

def evaluate_dev_length_tension_table(
    *,
    steel_grade: Optional[SteelGradeClass] = None,
    bar_diameter_mm: Optional[float] = None,
    yield_stress_mpa: Optional[float] = None,
    concrete_strength_mpa: Optional[float] = None,
    concrete_weight_class: Optional[ConcreteWeightClass] = None,
    coating_class: Optional[BarCoatingClass] = None,
    top_bar_placement: Optional[bool] = None,
    concrete_cover_mm: Optional[float] = None,
    clear_spacing_mm: Optional[float] = None,
    min_code_ties_provided_along_ld: Optional[bool] = None,
    apply_excess_reinforcement_reduction: Optional[bool] = None,
    as_required_mm2: Optional[float] = None,
    as_provided_mm2: Optional[float] = None,
    at_non_continuous_support: Optional[bool] = None,
    yield_development_required: Optional[bool] = None,
    continuity_required: Optional[bool] = None,
    ductile_seismic_system: Optional[bool] = None,
    pile_head_anchorage: Optional[bool] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate the simplified tension development length of Table 9-21-4
    (Clause 9-21-3-2-3).

    Verified source: Mabhas 9 (1399), Printed p. 428 / PDF p. 448 (table),
    Printed p. 427 / PDF p. 447 (factors), Printed p. 426 / PDF p. 446
    (300 mm floor of 9-21-3-2-1-ب applies in all cases). Row selection is
    computed from the verified conditions: confined row when
    (clear >= d_b AND minimum code ties provided along l_d) OR
    (clear >= 2*d_b AND cover >= d_b); otherwise the "other cases" row.
    """
    rule_id = RULE_BG_DEV_LENGTH_TENSION_TABLE_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "steel_grade": _enum_opt(steel_grade),
        "bar_diameter_mm": bar_diameter_mm,
        "yield_stress_mpa": yield_stress_mpa,
        "concrete_strength_mpa": concrete_strength_mpa,
        "concrete_weight_class": _enum_opt(concrete_weight_class),
        "coating_class": _enum_opt(coating_class),
        "top_bar_placement": top_bar_placement,
        "concrete_cover_mm": concrete_cover_mm,
        "clear_spacing_mm": clear_spacing_mm,
        "min_code_ties_provided_along_ld": min_code_ties_provided_along_ld,
        "apply_excess_reinforcement_reduction": apply_excess_reinforcement_reduction,
        "as_required_mm2": as_required_mm2,
        "as_provided_mm2": as_provided_mm2,
        "at_non_continuous_support": at_non_continuous_support,
        "yield_development_required": yield_development_required,
        "continuity_required": continuity_required,
        "ductile_seismic_system": ductile_seismic_system,
        "pile_head_anchorage": pile_head_anchorage,
    }
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")
    rule = gate.rule

    grade, d = _req_enum(steel_grade, enum_cls=SteelGradeClass,
                         field="steel_grade", rule=rule)
    diags = list(d)
    db, d = _req_positive(bar_diameter_mm, field="bar_diameter_mm", rule=rule)
    diags += d
    fy, d = _req_positive(yield_stress_mpa, field="yield_stress_mpa", rule=rule)
    diags += d
    fc, d = _req_positive(concrete_strength_mpa,
                          field="concrete_strength_mpa", rule=rule)
    diags += d
    weight, d = _req_enum(concrete_weight_class, enum_cls=ConcreteWeightClass,
                          field="concrete_weight_class", rule=rule)
    diags += d
    coating, d = _req_enum(coating_class, enum_cls=BarCoatingClass,
                           field="coating_class", rule=rule)
    diags += d
    top, d = _req_bool(top_bar_placement, field="top_bar_placement", rule=rule)
    diags += d
    cover, d = _req_positive(concrete_cover_mm, field="concrete_cover_mm", rule=rule)
    diags += d
    clear, d = _req_positive(clear_spacing_mm, field="clear_spacing_mm", rule=rule)
    diags += d
    ties, d = _req_bool(min_code_ties_provided_along_ld,
                        field="min_code_ties_provided_along_ld", rule=rule)
    diags += d
    terminal = _terminal(gate, raw_inputs=raw_inputs, diags=diags)
    if terminal is not None:
        return terminal
    assert (grade is not None and db is not None and fy is not None
            and fc is not None and weight is not None and coating is not None
            and top is not None and cover is not None and clear is not None
            and ties is not None)

    confined = ((clear >= db and ties) or (clear >= 2.0 * db and cover >= db))
    small = db < PSI_S_SMALL_DB_LIMIT_MM
    if confined:
        divisor = (TABLE_9_21_4_DIVISOR_CONFINED_SMALL if small
                   else TABLE_9_21_4_DIVISOR_CONFINED_LARGE)
        table_row = "confined"
    else:
        divisor = (TABLE_9_21_4_DIVISOR_OTHER_SMALL if small
                   else TABLE_9_21_4_DIVISOR_OTHER_LARGE)
        table_row = "other"

    psi_t = PSI_T_TOP if top else PSI_T_OTHER
    psi_e = _psi_e_tension(coating, db, cover, clear)
    psi_g = _psi_g_of(grade)
    psi_te = min(psi_t * psi_e, PSI_TE_MAX)
    lam = _lambda_of(weight)
    sqrt_fc = _sqrt_fc_used(fc)
    ld_eq = (psi_te * psi_g) * fy / (divisor * lam * sqrt_fc) * db

    intermediates: Dict[str, float] = {
        "psi_t": psi_t, "psi_e": psi_e, "psi_g": psi_g,
        "psi_te_capped": psi_te, "lambda": lam, "sqrt_fc_used": sqrt_fc,
        "table_row_is_confined": 1.0 if confined else 0.0,
        "table_divisor": divisor,
    }
    final = _apply_excess_reduction(
        gate=gate, rule=rule, raw_inputs=raw_inputs,
        ld_equation_mm=ld_eq, floor_mm=MIN_LD_TENSION_MM,
        apply_excess_reinforcement_reduction=apply_excess_reinforcement_reduction,
        as_required_mm2=as_required_mm2, as_provided_mm2=as_provided_mm2,
        at_non_continuous_support=at_non_continuous_support,
        yield_development_required=yield_development_required,
        continuity_required=continuity_required,
        ductile_seismic_system=ductile_seismic_system,
        pile_head_anchorage=pile_head_anchorage,
        intermediates=intermediates)
    if isinstance(final, CalculationTraceStep):
        return final
    return CalculationTraceStep.from_rule(
        rule, normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=final, unit="mm", outcome=EvaluationOutcome.COMPUTED,
        diagnostics=(),
        message=(f"Computed simplified tension development length "
                 f"(Table 9-21-4, {table_row} row, divisor {divisor}): l_d = "
                 f"{final:.1f} mm (floor {MIN_LD_TENSION_MM} mm; Clause "
                 "9-21-3-2-3)."))


# ----------------------------------------------------------------------------
# BG-DEV-LENGTH-HOOKED-001 — Eq. (9-21-3)
# ----------------------------------------------------------------------------

def evaluate_dev_length_hooked(
    *,
    bar_diameter_mm: Optional[float] = None,
    yield_stress_mpa: Optional[float] = None,
    concrete_strength_mpa: Optional[float] = None,
    concrete_weight_class: Optional[ConcreteWeightClass] = None,
    coating_class: Optional[BarCoatingClass] = None,
    a_th_mm2: Optional[float] = None,
    a_hs_mm2: Optional[float] = None,
    anchored_bar_clear_spacing_mm: Optional[float] = None,
    anchored_in_column_core: Optional[bool] = None,
    side_cover_normal_to_hook_plane_mm: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate the standard-hook development length Eq. (9-21-3)
    (Clause 9-21-3-3).

    Verified source: Mabhas 9 (1399), Printed p. 428 / PDF p. 448 (equation
    and floor max(8*d_b, 150 mm)), Printed p. 430 / PDF p. 450 (Table
    9-21-5), Printed p. 429 / PDF p. 449 (A_th definition of 9-21-3-3-3).
    No excess-reinforcement reduction is offered (prohibited by 9-21-3-9-2-ث);
    hooks never develop bars in compression (9-21-3-1-3).
    """
    rule_id = RULE_BG_DEV_LENGTH_HOOKED_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "bar_diameter_mm": bar_diameter_mm,
        "yield_stress_mpa": yield_stress_mpa,
        "concrete_strength_mpa": concrete_strength_mpa,
        "concrete_weight_class": _enum_opt(concrete_weight_class),
        "coating_class": _enum_opt(coating_class),
        "a_th_mm2": a_th_mm2,
        "a_hs_mm2": a_hs_mm2,
        "anchored_bar_clear_spacing_mm": anchored_bar_clear_spacing_mm,
        "anchored_in_column_core": anchored_in_column_core,
        "side_cover_normal_to_hook_plane_mm": side_cover_normal_to_hook_plane_mm,
    }
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")
    rule = gate.rule

    db, d = _req_positive(bar_diameter_mm, field="bar_diameter_mm", rule=rule)
    diags = list(d)
    fy, d = _req_positive(yield_stress_mpa, field="yield_stress_mpa", rule=rule)
    diags += d
    fc, d = _req_positive(concrete_strength_mpa,
                          field="concrete_strength_mpa", rule=rule)
    diags += d
    weight, d = _req_enum(concrete_weight_class, enum_cls=ConcreteWeightClass,
                          field="concrete_weight_class", rule=rule)
    diags += d
    coating, d = _req_enum(coating_class, enum_cls=BarCoatingClass,
                           field="coating_class", rule=rule)
    diags += d
    a_th, d = _req_positive(a_th_mm2, field="a_th_mm2", rule=rule)
    diags += d
    a_hs, d = _req_positive(a_hs_mm2, field="a_hs_mm2", rule=rule)
    diags += d
    spacing, d = _req_positive(anchored_bar_clear_spacing_mm,
                               field="anchored_bar_clear_spacing_mm", rule=rule)
    diags += d
    core, d = _req_bool(anchored_in_column_core,
                        field="anchored_in_column_core", rule=rule)
    diags += d
    side, d = _req_positive(side_cover_normal_to_hook_plane_mm,
                            field="side_cover_normal_to_hook_plane_mm", rule=rule)
    diags += d
    terminal = _terminal(gate, raw_inputs=raw_inputs, diags=diags)
    if terminal is not None:
        return terminal
    assert (db is not None and fy is not None and fc is not None
            and weight is not None and coating is not None and a_th is not None
            and a_hs is not None and spacing is not None and core is not None
            and side is not None)

    psi_e = (PSI_E_HOOKED_EPOXY if coating is BarCoatingClass.EPOXY_OR_DUAL_COATED
             else PSI_E_HOOKED_UNCOATED)
    confined = (db <= PSI_R_HOOKED_DB_LIMIT_MM
                and a_th >= PSI_R_HOOKED_ATH_RATIO * a_hs
                and spacing > PSI_R_HOOKED_SPACING_RATIO * db)
    psi_r = PSI_R_HOOKED_CONFINED if confined else PSI_R_HOOKED_OTHER
    core_qualified = (db <= PSI_R_HOOKED_DB_LIMIT_MM and core
                      and (side > SIDE_COVER_ABS_LIMIT_MM
                           or side > SIDE_COVER_DB_RATIO * db))
    psi_o = PSI_O_ANCHOR_CORE if core_qualified else PSI_O_ANCHOR_OTHER
    psi_c = _psi_c_of(fc)
    lam = _lambda_of(weight)
    sqrt_fc = _sqrt_fc_used(fc)
    ld_eq = ((psi_e * psi_r * psi_o * psi_c / lam)
             * (FY_FACTOR_HOOKED * fy / sqrt_fc)
             * db ** DB_EXPONENT_HOOKED)
    floor_mm = max(MIN_LDH_DB_FACTOR * db, MIN_LDH_MM)
    final = max(ld_eq, floor_mm)

    intermediates: Dict[str, float] = {
        "psi_e": psi_e, "psi_r": psi_r, "psi_o": psi_o, "psi_c": psi_c,
        "lambda": lam, "sqrt_fc_used": sqrt_fc,
        "ld_equation_mm": ld_eq, "ld_floor_mm": floor_mm,
        "ld_final_mm": final,
    }
    return CalculationTraceStep.from_rule(
        rule, normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=final, unit="mm", outcome=EvaluationOutcome.COMPUTED,
        diagnostics=(),
        message=(f"Computed standard-hook development length Eq. (9-21-3): "
                 f"l_dh = {final:.1f} mm (Eq. value {ld_eq:.1f} mm; floor "
                 f"{floor_mm:.1f} mm = max(8*d_b, 150 mm); Clause "
                 "9-21-3-3-1)."))


# ----------------------------------------------------------------------------
# BG-DEV-LENGTH-HEADED-001 — Eq. (9-21-4)
# ----------------------------------------------------------------------------

def evaluate_dev_length_headed(
    *,
    bar_diameter_mm: Optional[float] = None,
    yield_stress_mpa: Optional[float] = None,
    concrete_strength_mpa: Optional[float] = None,
    concrete_weight_class: Optional[ConcreteWeightClass] = None,
    coating_class: Optional[BarCoatingClass] = None,
    head_bearing_area_mm2: Optional[float] = None,
    concrete_cover_mm: Optional[float] = None,
    bar_spacing_cc_mm: Optional[float] = None,
    anchored_in_column_core: Optional[bool] = None,
    side_cover_normal_to_head_plane_mm: Optional[float] = None,
    connection_class: Optional[AnchorConnectionClass] = None,
    a_tt_mm2: Optional[float] = None,
    a_ts_mm2: Optional[float] = None,
    anchored_bar_clear_spacing_mm: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate the headed-bar development length Eq. (9-21-4)
    (Clause 9-21-3-4).

    Verified source: Mabhas 9 (1399), Printed pp. 430-432 / PDF pp. 450-452.
    The 9-21-3-4-1 applicability limits are enforced as verifiable FAILs:
    d_b > 34 mm, non-normal-weight concrete, head bearing area < 4*A_b,
    coverage < 2*d_b, spacing < 3*d_b. No reduction (prohibited by
    9-21-3-9-2-ث); heads never develop bars in compression (9-21-3-1-3).
    """
    rule_id = RULE_BG_DEV_LENGTH_HEADED_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "bar_diameter_mm": bar_diameter_mm,
        "yield_stress_mpa": yield_stress_mpa,
        "concrete_strength_mpa": concrete_strength_mpa,
        "concrete_weight_class": _enum_opt(concrete_weight_class),
        "coating_class": _enum_opt(coating_class),
        "head_bearing_area_mm2": head_bearing_area_mm2,
        "concrete_cover_mm": concrete_cover_mm,
        "bar_spacing_cc_mm": bar_spacing_cc_mm,
        "anchored_in_column_core": anchored_in_column_core,
        "side_cover_normal_to_head_plane_mm": side_cover_normal_to_head_plane_mm,
        "connection_class": _enum_opt(connection_class),
        "a_tt_mm2": a_tt_mm2,
        "a_ts_mm2": a_ts_mm2,
        "anchored_bar_clear_spacing_mm": anchored_bar_clear_spacing_mm,
    }
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")
    rule = gate.rule

    db, d = _req_positive(bar_diameter_mm, field="bar_diameter_mm", rule=rule)
    diags = list(d)
    fy, d = _req_positive(yield_stress_mpa, field="yield_stress_mpa", rule=rule)
    diags += d
    fc, d = _req_positive(concrete_strength_mpa,
                          field="concrete_strength_mpa", rule=rule)
    diags += d
    weight, d = _req_enum(concrete_weight_class, enum_cls=ConcreteWeightClass,
                          field="concrete_weight_class", rule=rule)
    diags += d
    coating, d = _req_enum(coating_class, enum_cls=BarCoatingClass,
                           field="coating_class", rule=rule)
    diags += d
    abrg, d = _req_positive(head_bearing_area_mm2,
                            field="head_bearing_area_mm2", rule=rule)
    diags += d
    cover, d = _req_positive(concrete_cover_mm, field="concrete_cover_mm", rule=rule)
    diags += d
    cc, d = _req_positive(bar_spacing_cc_mm, field="bar_spacing_cc_mm", rule=rule)
    diags += d
    core, d = _req_bool(anchored_in_column_core,
                        field="anchored_in_column_core", rule=rule)
    diags += d
    side, d = _req_positive(side_cover_normal_to_head_plane_mm,
                            field="side_cover_normal_to_head_plane_mm", rule=rule)
    diags += d
    conn, d = _req_enum(connection_class, enum_cls=AnchorConnectionClass,
                        field="connection_class", rule=rule)
    diags += d
    spacing, d = _req_positive(anchored_bar_clear_spacing_mm,
                               field="anchored_bar_clear_spacing_mm", rule=rule)
    diags += d
    terminal = _terminal(gate, raw_inputs=raw_inputs, diags=diags)
    if terminal is not None:
        return terminal
    assert (db is not None and fy is not None and fc is not None
            and weight is not None and coating is not None and abrg is not None
            and cover is not None and cc is not None and core is not None
            and side is not None and conn is not None and spacing is not None)

    clause_fails: List[EngineeringDiagnostic] = []
    if db > HEADED_DB_LIMIT_MM:
        clause_fails.append(EngineeringDiagnostic(
            code="HEADED_BAR_DIAMETER_EXCEEDS_LIMIT",
            severity=DiagnosticSeverity.ERROR,
            message=(f"FAIL: headed bar d_b = {db} mm exceeds the 34 mm limit "
                     "of Clause 9-21-3-4-1-ب."),
            rule_id=rule_id, field_name="bar_diameter_mm"))
    if weight is not ConcreteWeightClass.NORMAL_WEIGHT:
        clause_fails.append(EngineeringDiagnostic(
            code="HEADED_BAR_REQUIRES_NORMAL_WEIGHT_CONCRETE",
            severity=DiagnosticSeverity.ERROR,
            message=("FAIL: headed-bar anchorage is permitted only in "
                     "normal-weight concrete per Clause 9-21-3-4-1-ت."),
            rule_id=rule_id, field_name="concrete_weight_class"))
    a_b = math.pi * db ** 2 / 4.0
    if abrg < HEADED_ABRG_FACTOR * a_b:
        clause_fails.append(EngineeringDiagnostic(
            code="HEADED_BEARING_AREA_BELOW_MINIMUM",
            severity=DiagnosticSeverity.ERROR,
            message=(f"FAIL: head bearing section {abrg} mm^2 < 4*A_b = "
                     f"{4.0 * a_b:.1f} mm^2 per Clause 9-21-3-4-1-پ."),
            rule_id=rule_id, field_name="head_bearing_area_mm2"))
    if cover < HEADED_COVER_RATIO * db:
        clause_fails.append(EngineeringDiagnostic(
            code="HEADED_COVER_BELOW_LIMIT",
            severity=DiagnosticSeverity.ERROR,
            message=(f"FAIL: clear cover {cover} mm < 2*d_b = "
                     f"{HEADED_COVER_RATIO * db} mm per Clause 9-21-3-4-1-ث."),
            rule_id=rule_id, field_name="concrete_cover_mm"))
    if cc < HEADED_SPACING_RATIO * db:
        clause_fails.append(EngineeringDiagnostic(
            code="HEADED_SPACING_BELOW_LIMIT",
            severity=DiagnosticSeverity.ERROR,
            message=(f"FAIL: center-to-center spacing {cc} mm < 3*d_b = "
                     f"{HEADED_SPACING_RATIO * db} mm per Clause 9-21-3-4-1-ج."),
            rule_id=rule_id, field_name="bar_spacing_cc_mm"))
    if clause_fails:
        return CalculationTraceStep.from_rule(
            rule, normalized_inputs=raw_inputs, intermediate_values={},
            final_result=None, unit="mm", outcome=EvaluationOutcome.FAIL,
            diagnostics=tuple(clause_fails), message=clause_fails[0].message)

    psi_e = (PSI_E_HOOKED_EPOXY if coating is BarCoatingClass.EPOXY_OR_DUAL_COATED
             else PSI_E_HOOKED_UNCOATED)
    att_required = conn is AnchorConnectionClass.BEAM_COLUMN_JOINT
    if att_required:
        a_tt, d = _req_positive(a_tt_mm2, field="a_tt_mm2", rule=rule)
        diags = list(d)
        a_ts, d = _req_positive(a_ts_mm2, field="a_ts_mm2", rule=rule)
        diags += d
        terminal = _terminal(gate, raw_inputs=raw_inputs, diags=diags)
        if terminal is not None:
            return terminal
        assert a_tt is not None and a_ts is not None
        joint_qualified = a_tt >= PSI_P_ATT_RATIO * a_ts
    else:
        joint_qualified = False
    psi_p = (PSI_P_HEADED_QUALIFIED
             if (joint_qualified or spacing > PSI_P_SPACING_RATIO * db)
             else PSI_P_HEADED_OTHER)
    psi_o_qualified = (core and (side > SIDE_COVER_ABS_LIMIT_MM
                                 or side > SIDE_COVER_DB_RATIO * db))
    psi_o = PSI_O_ANCHOR_CORE if psi_o_qualified else PSI_O_ANCHOR_OTHER
    psi_c = _psi_c_of(fc)
    lam = _lambda_of(weight)
    sqrt_fc = _sqrt_fc_used(fc)
    ld_eq = ((psi_e * psi_c * psi_p * psi_o / lam)
             * (FY_FACTOR_HEADED * fy / sqrt_fc)
             * db ** DB_EXPONENT_HEADED)
    floor_mm = max(MIN_LDT_HEADED_DB_FACTOR * db, MIN_LDT_HEADED_MM)
    final = max(ld_eq, floor_mm)

    intermediates: Dict[str, float] = {
        "psi_e": psi_e, "psi_c": psi_c, "psi_p": psi_p, "psi_o": psi_o,
        "lambda": lam, "sqrt_fc_used": sqrt_fc,
        "ld_equation_mm": ld_eq, "ld_floor_mm": floor_mm,
        "ld_final_mm": final,
    }
    return CalculationTraceStep.from_rule(
        rule, normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=final, unit="mm", outcome=EvaluationOutcome.COMPUTED,
        diagnostics=(),
        message=(f"Computed headed-bar development length Eq. (9-21-4): "
                 f"l_dt = {final:.1f} mm (Eq. value {ld_eq:.1f} mm; floor "
                 f"{floor_mm:.1f} mm = max(8*d_b, 150 mm); Clause "
                 "9-21-3-4-2)."))


# ----------------------------------------------------------------------------
# BG-DEV-MECH-ANCHOR-001 — Clause 9-21-3-5 admissibility gate
# ----------------------------------------------------------------------------

def evaluate_dev_mech_anchorage(
    *,
    device_supplies_yield_capacity: Optional[bool] = None,
    designer_engineer_approved: Optional[bool] = None,
    approved_test_results_present: Optional[bool] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate Clause 9-21-3-5-1 mechanical anchorage admissibility.

    Verified source: Mabhas 9 (1399), Printed p. 433 / PDF p. 453: attachments
    or mechanical devices developing bar yield f_y are permitted only with
    the design engineer's approval; combined anchorage is permitted on the
    basis of approved test results. All three conditions PASS; any False
    FAIL; any missing input BLOCKED. No length equation is given, none is
    computed or invented.
    """
    rule_id = RULE_BG_DEV_MECH_ANCHOR_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "device_supplies_yield_capacity": device_supplies_yield_capacity,
        "designer_engineer_approved": designer_engineer_approved,
        "approved_test_results_present": approved_test_results_present,
    }
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="1")
    rule = gate.rule

    dev, d = _req_bool(device_supplies_yield_capacity,
                       field="device_supplies_yield_capacity", rule=rule)
    diags = list(d)
    eng, d = _req_bool(designer_engineer_approved,
                       field="designer_engineer_approved", rule=rule)
    diags += d
    test, d = _req_bool(approved_test_results_present,
                        field="approved_test_results_present", rule=rule)
    diags += d
    terminal = _terminal(gate, raw_inputs=raw_inputs, diags=diags)
    if terminal is not None:
        return terminal
    assert dev is not None and eng is not None and test is not None

    fails: List[EngineeringDiagnostic] = []
    if not dev:
        fails.append(EngineeringDiagnostic(
            code="MECH_ANCHOR_WITHOUT_YIELD_CAPACITY",
            severity=DiagnosticSeverity.ERROR,
            message=("FAIL: the attachment/device does not supply the bar "
                     "yield capacity f_y required by Clause 9-21-3-5-1."),
            rule_id=rule_id, field_name="device_supplies_yield_capacity"))
    if not eng:
        fails.append(EngineeringDiagnostic(
            code="MECH_ANCHOR_WITHOUT_ENGINEER_APPROVAL",
            severity=DiagnosticSeverity.ERROR,
            message=("FAIL: mechanical anchorage without the design "
                     "engineer's approval is not permitted by Clause "
                     "9-21-3-5-1."),
            rule_id=rule_id, field_name="designer_engineer_approved"))
    if not test:
        fails.append(EngineeringDiagnostic(
            code="MECH_ANCHOR_WITHOUT_APPROVED_TESTS",
            severity=DiagnosticSeverity.ERROR,
            message=("FAIL: mechanical anchorage without approved test "
                     "results is not permitted by Clause 9-21-3-5-1."),
            rule_id=rule_id, field_name="approved_test_results_present"))
    if fails:
        return CalculationTraceStep.from_rule(
            rule, normalized_inputs=raw_inputs, intermediate_values={},
            final_result=None, unit="1", outcome=EvaluationOutcome.FAIL,
            diagnostics=tuple(fails), message=fails[0].message)
    return CalculationTraceStep.from_rule(
        rule, normalized_inputs=raw_inputs, intermediate_values={},
        final_result=None, unit="1", outcome=EvaluationOutcome.PASS,
        diagnostics=(),
        message=("PASS: mechanical anchorage admissible per Clause 9-21-3-5-1 "
                 "(device supplies f_y; design engineer approval; approved "
                 "test results). No anchorage length is computed by this "
                 "rule."))


# ----------------------------------------------------------------------------
# BG-DEV-WIRE-DEFORMED-001 — Eq. (9-21-5)
# ----------------------------------------------------------------------------

def evaluate_dev_wire_deformed(
    *,
    bar_diameter_mm: Optional[float] = None,
    yield_stress_mpa: Optional[float] = None,
    concrete_strength_mpa: Optional[float] = None,
    concrete_weight_class: Optional[ConcreteWeightClass] = None,
    wire_surface_class: Optional[WireSurfaceClass] = None,
    wire_is_deformed: Optional[bool] = None,
    epoxy_psi_e_unit_permission: Optional[bool] = None,
    top_bar_placement: Optional[bool] = None,
    concrete_cover_mm: Optional[float] = None,
    clear_spacing_mm: Optional[float] = None,
    cross_wire_in_development: Optional[bool] = None,
    cross_wire_distance_from_critical_mm: Optional[float] = None,
    anchored_wire_spacing_mm: Optional[float] = None,
    apply_k_tr: Optional[bool] = None,
    transverse_area_mm2: Optional[float] = None,
    transverse_spacing_mm: Optional[float] = None,
    developed_bar_count: Optional[Union[int, float]] = None,
    apply_excess_reinforcement_reduction: Optional[bool] = None,
    as_required_mm2: Optional[float] = None,
    as_provided_mm2: Optional[float] = None,
    at_non_continuous_support: Optional[bool] = None,
    yield_development_required: Optional[bool] = None,
    continuity_required: Optional[bool] = None,
    ductile_seismic_system: Optional[bool] = None,
    pile_head_anchorage: Optional[bool] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate welded deformed-wire mesh tension development Eq. (9-21-5)
    (Clause 9-21-3-6).

    Verified source: Mabhas 9 (1399), Printed pp. 433-434 / PDF pp. 453-454.
    Applicability: deformed wires with d_b <= 16 mm; wires > 16 mm, plain
    wires and galvanized mesh are routed to Clause 9-21-3-7 (NOT_APPLICABLE
    here). psi_w per Eqs. (9-21-6-الف/ب): max of (f_y-240)/f_y and 5*d_b/s,
    each <= 1.0, with a cross wire within l_d at >= 50 mm from the critical
    section; otherwise psi_w = 1.0. Epoxy mesh carries the explicit
    psi_e = 1.0 permission of 9-21-3-6-1 (typed option). Floor 200 mm;
    reduction per 9-21-3-9 with the floor preserved.
    """
    rule_id = RULE_BG_DEV_WIRE_DEFORMED_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "bar_diameter_mm": bar_diameter_mm,
        "yield_stress_mpa": yield_stress_mpa,
        "concrete_strength_mpa": concrete_strength_mpa,
        "concrete_weight_class": _enum_opt(concrete_weight_class),
        "wire_surface_class": _enum_opt(wire_surface_class),
        "wire_is_deformed": wire_is_deformed,
        "epoxy_psi_e_unit_permission": epoxy_psi_e_unit_permission,
        "top_bar_placement": top_bar_placement,
        "concrete_cover_mm": concrete_cover_mm,
        "clear_spacing_mm": clear_spacing_mm,
        "cross_wire_in_development": cross_wire_in_development,
        "cross_wire_distance_from_critical_mm": cross_wire_distance_from_critical_mm,
        "anchored_wire_spacing_mm": anchored_wire_spacing_mm,
        "apply_k_tr": apply_k_tr,
        "transverse_area_mm2": transverse_area_mm2,
        "transverse_spacing_mm": transverse_spacing_mm,
        "developed_bar_count": developed_bar_count,
        "apply_excess_reinforcement_reduction": apply_excess_reinforcement_reduction,
        "as_required_mm2": as_required_mm2,
        "as_provided_mm2": as_provided_mm2,
        "at_non_continuous_support": at_non_continuous_support,
        "yield_development_required": yield_development_required,
        "continuity_required": continuity_required,
        "ductile_seismic_system": ductile_seismic_system,
        "pile_head_anchorage": pile_head_anchorage,
    }
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")
    rule = gate.rule

    db, d = _req_positive(bar_diameter_mm, field="bar_diameter_mm", rule=rule)
    diags = list(d)
    fy, d = _req_positive(yield_stress_mpa, field="yield_stress_mpa", rule=rule)
    diags += d
    fc, d = _req_positive(concrete_strength_mpa,
                          field="concrete_strength_mpa", rule=rule)
    diags += d
    weight, d = _req_enum(concrete_weight_class, enum_cls=ConcreteWeightClass,
                          field="concrete_weight_class", rule=rule)
    diags += d
    surface, d = _req_enum(wire_surface_class, enum_cls=WireSurfaceClass,
                           field="wire_surface_class", rule=rule)
    diags += d
    is_def, d = _req_bool(wire_is_deformed, field="wire_is_deformed", rule=rule)
    diags += d
    terminal = _terminal(gate, raw_inputs=raw_inputs, diags=diags)
    if terminal is not None:
        return terminal
    assert (db is not None and fy is not None and fc is not None
            and weight is not None and surface is not None and is_def is not None)

    # 9-21-3-6-3/-4 routing: outside this rule -> NOT_APPLICABLE
    if not is_def or db > WIRE_DEFORMED_MAX_DB_MM or surface is WireSurfaceClass.GALVANIZED:
        reason = ("plain wire of any diameter, deformed wire with d_b > 16 "
                  "mm, and galvanized welded wire mesh are developed per "
                  "Clause 9-21-3-7 (9-21-3-6-3 / 9-21-3-6-4)")
        return CalculationTraceStep.from_rule(
            rule, normalized_inputs=raw_inputs, intermediate_values={},
            final_result=None, unit="mm", outcome=EvaluationOutcome.NOT_APPLICABLE,
            diagnostics=(),
            message=f"NOT_APPLICABLE: {reason}; use BG-DEV-WIRE-PLAIN-001.")

    if surface is WireSurfaceClass.EPOXY:
        unit_perm, d = _req_bool(epoxy_psi_e_unit_permission,
                                 field="epoxy_psi_e_unit_permission", rule=rule)
        if d:
            terminal = _terminal(gate, raw_inputs=raw_inputs, diags=list(d))
            if terminal is not None:
                return terminal
        assert unit_perm is not None
    else:
        unit_perm = False

    top, d = _req_bool(top_bar_placement, field="top_bar_placement", rule=rule)
    diags = list(d)
    cover, d = _req_positive(concrete_cover_mm, field="concrete_cover_mm", rule=rule)
    diags += d
    clear, d = _req_positive(clear_spacing_mm, field="clear_spacing_mm", rule=rule)
    diags += d
    cross, d = _req_bool(cross_wire_in_development,
                         field="cross_wire_in_development", rule=rule)
    diags += d
    terminal = _terminal(gate, raw_inputs=raw_inputs, diags=diags)
    if terminal is not None:
        return terminal
    assert (top is not None and cover is not None and clear is not None
            and cross is not None)

    dist: Optional[float] = None
    spacing: Optional[float] = None
    if cross:
        dist, d = _req_positive(cross_wire_distance_from_critical_mm,
                                field="cross_wire_distance_from_critical_mm",
                                rule=rule)
        diags = list(d)
        qualified = dist is not None and dist >= CROSS_WIRE_MIN_DISTANCE_MM
        if dist is not None and qualified:
            sp, d = _req_positive(anchored_wire_spacing_mm,
                                  field="anchored_wire_spacing_mm", rule=rule)
            diags += d
            spacing = sp if sp is not None else None
        terminal = _terminal(gate, raw_inputs=raw_inputs, diags=diags)
        if terminal is not None:
            return terminal
    else:
        if cross_wire_distance_from_critical_mm is not None:
            return _invalid_step(
                gate, raw_inputs=raw_inputs,
                diagnostics=[EngineeringDiagnostic(
                    code="INCONSISTENT_CROSS_WIRE_INPUTS",
                    severity=DiagnosticSeverity.ERROR,
                    message=("cross_wire_distance_from_critical_mm must not "
                             "be supplied when cross_wire_in_development is "
                             "False -> INVALID_INPUT."),
                    rule_id=rule_id,
                    field_name="cross_wire_distance_from_critical_mm")])

    k_tr = _resolve_k_tr(
        gate=gate, rule=rule, raw_inputs=raw_inputs, apply_k_tr=apply_k_tr,
        transverse_area_mm2=transverse_area_mm2,
        transverse_spacing_mm=transverse_spacing_mm,
        developed_bar_count=developed_bar_count)
    if isinstance(k_tr, CalculationTraceStep):
        return k_tr

    if cross and dist is not None and dist >= CROSS_WIRE_MIN_DISTANCE_MM:
        assert spacing is not None
        psi_w = max(min((fy - PSI_W_FY_OFFSET_MPA) / fy, 1.0),
                    min(PSI_W_SPACING_DB_FACTOR * db / spacing, 1.0))
    else:
        psi_w = 1.0

    c_b = min(cover + db / 2.0, (clear + db) / 2.0)
    conf_index = min((c_b + k_tr) / db, CONFINEMENT_INDEX_MAX)
    psi_t = PSI_T_TOP if top else PSI_T_OTHER
    if surface is WireSurfaceClass.EPOXY and unit_perm:
        psi_e = 1.0
    elif surface is WireSurfaceClass.EPOXY:
        psi_e = _psi_e_tension(BarCoatingClass.EPOXY_OR_DUAL_COATED,
                               db, cover, clear)
    else:
        psi_e = PSI_E_UNCOATED
    psi_s = _psi_s_of(db)
    psi_te = min(psi_t * psi_e, PSI_TE_MAX)
    lam = _lambda_of(weight)
    sqrt_fc = _sqrt_fc_used(fc)
    ld_eq = (psi_te * psi_s * psi_w / (lam * conf_index)) * (
        FY_FACTOR_TENSION * fy / sqrt_fc) * db

    intermediates: Dict[str, float] = {
        "psi_t": psi_t, "psi_e": psi_e, "psi_s": psi_s, "psi_w": psi_w,
        "psi_te_capped": psi_te, "lambda": lam, "sqrt_fc_used": sqrt_fc,
        "c_b_mm": c_b, "k_tr_mm": k_tr,
        "confinement_index_capped": conf_index,
    }
    final = _apply_excess_reduction(
        gate=gate, rule=rule, raw_inputs=raw_inputs,
        ld_equation_mm=ld_eq, floor_mm=MIN_LD_WIRE_DEFORMED_MM,
        apply_excess_reinforcement_reduction=apply_excess_reinforcement_reduction,
        as_required_mm2=as_required_mm2, as_provided_mm2=as_provided_mm2,
        at_non_continuous_support=at_non_continuous_support,
        yield_development_required=yield_development_required,
        continuity_required=continuity_required,
        ductile_seismic_system=ductile_seismic_system,
        pile_head_anchorage=pile_head_anchorage,
        intermediates=intermediates)
    if isinstance(final, CalculationTraceStep):
        return final
    return CalculationTraceStep.from_rule(
        rule, normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=final, unit="mm", outcome=EvaluationOutcome.COMPUTED,
        diagnostics=(),
        message=(f"Computed welded deformed-wire development length Eq. "
                 f"(9-21-5): l_d = {final:.1f} mm (psi_w = {psi_w:.3f}; "
                 f"floor {MIN_LD_WIRE_DEFORMED_MM} mm; Clause 9-21-3-6)."))


# ----------------------------------------------------------------------------
# BG-DEV-WIRE-PLAIN-001 — Eq. (9-21-7)
# ----------------------------------------------------------------------------

def evaluate_dev_wire_plain(
    *,
    bar_diameter_mm: Optional[float] = None,
    anchored_wire_spacing_mm: Optional[float] = None,
    yield_stress_mpa: Optional[float] = None,
    concrete_strength_mpa: Optional[float] = None,
    concrete_weight_class: Optional[ConcreteWeightClass] = None,
    cross_wires_in_development_length: Optional[Union[int, float]] = None,
    apply_excess_reinforcement_reduction: Optional[bool] = None,
    as_required_mm2: Optional[float] = None,
    as_provided_mm2: Optional[float] = None,
    at_non_continuous_support: Optional[bool] = None,
    yield_development_required: Optional[bool] = None,
    continuity_required: Optional[bool] = None,
    ductile_seismic_system: Optional[bool] = None,
    pile_head_anchorage: Optional[bool] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate welded plain-wire mesh tension development Eq. (9-21-7)
    (Clause 9-21-3-7).

    Verified source: Mabhas 9 (1399), Printed pp. 434-435 / PDF pp. 454-455:
    l_dt = (3.3*f_y/(lambda*sqrt(f'c))) * (A_b/s) to the outermost cross
    wire; floors: the greater of 150 mm and s + 50 mm; at least two cross
    wires within l_dt are required in all cases (fewer is a verifiable
    FAIL). Reduction per 9-21-3-9 with both floors preserved.
    """
    rule_id = RULE_BG_DEV_WIRE_PLAIN_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "bar_diameter_mm": bar_diameter_mm,
        "anchored_wire_spacing_mm": anchored_wire_spacing_mm,
        "yield_stress_mpa": yield_stress_mpa,
        "concrete_strength_mpa": concrete_strength_mpa,
        "concrete_weight_class": _enum_opt(concrete_weight_class),
        "cross_wires_in_development_length": cross_wires_in_development_length,
        "apply_excess_reinforcement_reduction": apply_excess_reinforcement_reduction,
        "as_required_mm2": as_required_mm2,
        "as_provided_mm2": as_provided_mm2,
        "at_non_continuous_support": at_non_continuous_support,
        "yield_development_required": yield_development_required,
        "continuity_required": continuity_required,
        "ductile_seismic_system": ductile_seismic_system,
        "pile_head_anchorage": pile_head_anchorage,
    }
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")
    rule = gate.rule

    db, d = _req_positive(bar_diameter_mm, field="bar_diameter_mm", rule=rule)
    diags = list(d)
    s_w, d = _req_positive(anchored_wire_spacing_mm,
                           field="anchored_wire_spacing_mm", rule=rule)
    diags += d
    fy, d = _req_positive(yield_stress_mpa, field="yield_stress_mpa", rule=rule)
    diags += d
    fc, d = _req_positive(concrete_strength_mpa,
                          field="concrete_strength_mpa", rule=rule)
    diags += d
    weight, d = _req_enum(concrete_weight_class, enum_cls=ConcreteWeightClass,
                          field="concrete_weight_class", rule=rule)
    diags += d
    cross_n, d = _req_int(cross_wires_in_development_length,
                          field="cross_wires_in_development_length", rule=rule)
    diags += d
    terminal = _terminal(gate, raw_inputs=raw_inputs, diags=diags)
    if terminal is not None:
        return terminal
    assert (db is not None and s_w is not None and fy is not None
            and fc is not None and weight is not None and cross_n is not None)

    if cross_n < MIN_CROSS_WIRES_IN_LD:
        fail_diag = EngineeringDiagnostic(
            code="PLAIN_WIRE_FEWER_THAN_TWO_CROSS_WIRES",
            severity=DiagnosticSeverity.ERROR,
            message=(f"FAIL: Clause 9-21-3-7-1 requires at least "
                     f"{MIN_CROSS_WIRES_IN_LD} cross wires within l_dt in "
                     f"all cases; got {cross_n}."),
            rule_id=rule_id,
            field_name="cross_wires_in_development_length")
        return CalculationTraceStep.from_rule(
            rule, normalized_inputs=raw_inputs, intermediate_values={},
            final_result=None, unit="mm", outcome=EvaluationOutcome.FAIL,
            diagnostics=(fail_diag,), message=fail_diag.message)

    a_b = math.pi * db ** 2 / 4.0
    lam = _lambda_of(weight)
    sqrt_fc = _sqrt_fc_used(fc)
    ld_eq = (FY_FACTOR_WIRE_PLAIN * fy / (lam * sqrt_fc)) * (a_b / s_w)
    floor_mm = max(MIN_LD_WIRE_PLAIN_MM, s_w + WIRE_PLAIN_OVERHANG_MM)

    intermediates: Dict[str, float] = {
        "a_b_mm2": a_b, "lambda": lam, "sqrt_fc_used": sqrt_fc,
        "wire_spacing_mm": s_w,
    }
    final = _apply_excess_reduction(
        gate=gate, rule=rule, raw_inputs=raw_inputs,
        ld_equation_mm=ld_eq, floor_mm=floor_mm,
        apply_excess_reinforcement_reduction=apply_excess_reinforcement_reduction,
        as_required_mm2=as_required_mm2, as_provided_mm2=as_provided_mm2,
        at_non_continuous_support=at_non_continuous_support,
        yield_development_required=yield_development_required,
        continuity_required=continuity_required,
        ductile_seismic_system=ductile_seismic_system,
        pile_head_anchorage=pile_head_anchorage,
        intermediates=intermediates)
    if isinstance(final, CalculationTraceStep):
        return final
    return CalculationTraceStep.from_rule(
        rule, normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=final, unit="mm", outcome=EvaluationOutcome.COMPUTED,
        diagnostics=(),
        message=(f"Computed welded plain-wire development length Eq. "
                 f"(9-21-7): l_dt = {final:.1f} mm (Eq. value {ld_eq:.1f} mm; "
                 f"floor {floor_mm:.1f} mm = max(150 mm, s + 50 mm); Clause "
                 "9-21-3-7-1)."))


# ----------------------------------------------------------------------------
# BG-DEV-LENGTH-COMPRESSION-001 — Clause 9-21-3-8-1
# ----------------------------------------------------------------------------

def evaluate_dev_length_compression(
    *,
    bar_diameter_mm: Optional[float] = None,
    yield_stress_mpa: Optional[float] = None,
    concrete_strength_mpa: Optional[float] = None,
    concrete_weight_class: Optional[ConcreteWeightClass] = None,
    confinement_tie_class: Optional[CompressionConfinementClass] = None,
    confinement_tie_diameter_mm: Optional[float] = None,
    confinement_tie_spacing_mm: Optional[float] = None,
    apply_excess_reinforcement_reduction: Optional[bool] = None,
    as_required_mm2: Optional[float] = None,
    as_provided_mm2: Optional[float] = None,
    at_non_continuous_support: Optional[bool] = None,
    yield_development_required: Optional[bool] = None,
    continuity_required: Optional[bool] = None,
    ductile_seismic_system: Optional[bool] = None,
    pile_head_anchorage: Optional[bool] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Evaluate the compression development length of Clause 9-21-3-8-1.

    Verified source: Mabhas 9 (1399), Printed p. 435 / PDF p. 455:
    l_dc = max{ (psi_r*0.24*f_y/(lambda*sqrt(f'c)))*d_b ,
    0.043*f_y*psi_r*d_b }; floor 200 mm. psi_r = 0.75 for the printed
    confinement classes (spiral; circular tie > 6 mm @ < 100 mm; wire tie
    > 12 mm @ < 100 mm; دوریگر per 9-21-6-4 @ < 100 mm), else 1.0. The
    wire-tie branch keeps its VERIFY_PENDING noun status and returns
    UNVERIFIED_RULE_BLOCKED.
    """
    rule_id = RULE_BG_DEV_COMPRESSION_001.rule_id
    raw_inputs: Dict[str, ScalarInputValue] = {
        "bar_diameter_mm": bar_diameter_mm,
        "yield_stress_mpa": yield_stress_mpa,
        "concrete_strength_mpa": concrete_strength_mpa,
        "concrete_weight_class": _enum_opt(concrete_weight_class),
        "confinement_tie_class": _enum_opt(confinement_tie_class),
        "confinement_tie_diameter_mm": confinement_tie_diameter_mm,
        "confinement_tie_spacing_mm": confinement_tie_spacing_mm,
        "apply_excess_reinforcement_reduction": apply_excess_reinforcement_reduction,
        "as_required_mm2": as_required_mm2,
        "as_provided_mm2": as_provided_mm2,
        "at_non_continuous_support": at_non_continuous_support,
        "yield_development_required": yield_development_required,
        "continuity_required": continuity_required,
        "ductile_seismic_system": ductile_seismic_system,
        "pile_head_anchorage": pile_head_anchorage,
    }
    gate = evaluate_rule_gate(rule_id, active_jurisdiction=jurisdiction_mode)
    if not gate.allowed:
        return gate.to_blocked_trace_step(normalized_inputs=raw_inputs, unit="mm")
    rule = gate.rule

    db, d = _req_positive(bar_diameter_mm, field="bar_diameter_mm", rule=rule)
    diags = list(d)
    fy, d = _req_positive(yield_stress_mpa, field="yield_stress_mpa", rule=rule)
    diags += d
    fc, d = _req_positive(concrete_strength_mpa,
                          field="concrete_strength_mpa", rule=rule)
    diags += d
    weight, d = _req_enum(concrete_weight_class, enum_cls=ConcreteWeightClass,
                          field="concrete_weight_class", rule=rule)
    diags += d
    conf, d = _req_enum(confinement_tie_class,
                        enum_cls=CompressionConfinementClass,
                        field="confinement_tie_class", rule=rule)
    diags += d
    terminal = _terminal(gate, raw_inputs=raw_inputs, diags=diags)
    if terminal is not None:
        return terminal
    assert (db is not None and fy is not None and fc is not None
            and weight is not None and conf is not None)

    if conf is CompressionConfinementClass.WIRE_TIE:
        return _blocked_step(
            gate, raw_inputs=raw_inputs,
            diagnostics=[EngineeringDiagnostic(
                code="VERIFY_PENDING_CONFINEMENT_TIE_CLASS",
                severity=DiagnosticSeverity.BLOCK,
                message=(
                    "The compression psi_r = 0.75 branch for the printed "
                    "«تنگ سیمی» (wire tie, diameter > 12 mm at spacing "
                    "< 100 mm) carries a recorded noun ambiguity in the "
                    "source-verification matrix (VERIFY_PENDING). This "
                    "branch remains non-executable -> BLOCKED; select "
                    "SPIRAL / CIRCULAR_TIE / DORGIR_9_21_6_4 / NONE only."),
                rule_id=rule_id, field_name="confinement_tie_class")])

    if conf is CompressionConfinementClass.SPIRAL:
        psi_r = PSI_R_COMPRESSION_CONFINED
    elif conf is CompressionConfinementClass.NONE:
        psi_r = PSI_R_COMPRESSION_OTHER
    else:
        spacing, d = _req_positive(confinement_tie_spacing_mm,
                                   field="confinement_tie_spacing_mm", rule=rule)
        diags = list(d)
        if conf is CompressionConfinementClass.CIRCULAR_TIE:
            diameter, d = _req_positive(confinement_tie_diameter_mm,
                                        field="confinement_tie_diameter_mm",
                                        rule=rule)
            diags += d
        else:
            diameter = None
        terminal = _terminal(gate, raw_inputs=raw_inputs, diags=diags)
        if terminal is not None:
            return terminal
        assert spacing is not None
        qualifies = spacing < CONFINEMENT_MAX_SPACING_MM
        if conf is CompressionConfinementClass.CIRCULAR_TIE and diameter is not None:
            qualifies = qualifies and diameter > CIRCULAR_TIE_MIN_DIAMETER_MM
        psi_r = (PSI_R_COMPRESSION_CONFINED if qualifies
                 else PSI_R_COMPRESSION_OTHER)

    lam = _lambda_of(weight)
    sqrt_fc = _sqrt_fc_used(fc)
    ldc_a = (psi_r * FY_FACTOR_COMPRESSION_A * fy / (lam * sqrt_fc)) * db
    ldc_b = FY_FACTOR_COMPRESSION_B * fy * psi_r * db
    ld_eq = max(ldc_a, ldc_b)

    intermediates: Dict[str, float] = {
        "psi_r": psi_r, "lambda": lam, "sqrt_fc_used": sqrt_fc,
        "ldc_term_a_mm": ldc_a, "ldc_term_b_mm": ldc_b,
    }
    final = _apply_excess_reduction(
        gate=gate, rule=rule, raw_inputs=raw_inputs,
        ld_equation_mm=ld_eq, floor_mm=MIN_LD_COMPRESSION_MM,
        apply_excess_reinforcement_reduction=apply_excess_reinforcement_reduction,
        as_required_mm2=as_required_mm2, as_provided_mm2=as_provided_mm2,
        at_non_continuous_support=at_non_continuous_support,
        yield_development_required=yield_development_required,
        continuity_required=continuity_required,
        ductile_seismic_system=ductile_seismic_system,
        pile_head_anchorage=pile_head_anchorage,
        intermediates=intermediates)
    if isinstance(final, CalculationTraceStep):
        return final
    return CalculationTraceStep.from_rule(
        rule, normalized_inputs=raw_inputs,
        intermediate_values=intermediates,
        final_result=final, unit="mm", outcome=EvaluationOutcome.COMPUTED,
        diagnostics=(),
        message=(f"Computed compression development length (Clause "
                 f"9-21-3-8-1): l_dc = {final:.1f} mm (psi_r = {psi_r}; "
                 f"floor {MIN_LD_COMPRESSION_MM} mm)."))
