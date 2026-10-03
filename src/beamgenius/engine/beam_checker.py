"""Orchestration and blocked-workflow evaluators for the Mabhas 9 engineering core."""

from __future__ import annotations

from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from beamgenius.domain.enums import (
    ConcreteCoverExposureClass,
    DiagnosticSeverity,
    EvaluationOutcome,
    JurisdictionMode,
    OverallComplianceStatus,
)
from beamgenius.domain.models import (
    BeamGeometry,
    ConcreteMaterial,
    RebarMaterial,
    StirrupLayout,
)
from beamgenius.domain.trace import (
    BeamComplianceReport,
    CalculationTraceStep,
    EngineeringDiagnostic,
    ScalarInputValue,
    select_dominant_outcome,
)
from beamgenius.engine.flexure_mabhas9 import (
    evaluate_mabhas9_effective_flange_width,
    evaluate_mabhas9_flexural_capacity,
    evaluate_mabhas9_stress_block_parameters,
    evaluate_minimum_flexural_reinforcement,
)
from beamgenius.engine.detailing_mabhas9 import (
    evaluate_compression_reinforcement_lateral_support_spacing,
    evaluate_layer_clear_spacing as _verified_layer_clear_spacing,
    evaluate_longitudinal_bar_clear_spacing as _verified_bar_clear_spacing,
    evaluate_minimum_concrete_cover as _verified_min_concrete_cover,
    evaluate_minimum_transverse_bar_diameter as _verified_min_transverse_dia,
)
from beamgenius.engine.shear_mabhas9 import (
    evaluate_concrete_shear_capacity_vc,
    evaluate_full_shear_capacity,
    evaluate_mabhas9_concrete_shear_resistance_vc,
    evaluate_mabhas9_shear_phi_factor,
    evaluate_mabhas9_shear_web_crushing_limit,
    evaluate_mabhas9_transverse_shear_resistance_vs,
    evaluate_maximum_shear_steel_vs_max,
    evaluate_maximum_stirrup_spacing,
    evaluate_minimum_shear_reinforcement,
    evaluate_required_shear_steel_demand_vs,
)
from beamgenius.registry.catalog import (
    RULE_BG_BENT_ANCHOR_PENDING,
    RULE_BG_CUTOFF_COND_PENDING,
    RULE_BG_DETAIL_COMP_LAT_001,
    RULE_BG_DETAIL_COMP_LAT_PENDING,
    RULE_BG_DETAIL_COVER_001,
    RULE_BG_DETAIL_COVER_BLOCKED,
    RULE_BG_DETAIL_LAYER_SPACING_001,
    RULE_BG_DETAIL_LAYER_SPACING_BLOCKED,
    RULE_BG_DETAIL_SPACING_001,
    RULE_BG_DETAIL_SPACING_BLOCKED,
    RULE_BG_DETAIL_TRANS_DIA_001,
    RULE_BG_DETAIL_TRANS_DIA_PENDING,
    RULE_BG_DEV_LENGTH_PENDING,
    RULE_BG_FLEX_EXT_PENDING,
    RULE_BG_FLEX_MIN_001,
    RULE_BG_FLEX_RECT_SINGLY_001,
    RULE_BG_FLEX_STRESS_BLOCK,
    RULE_BG_FLEX_TBEAM_B_EFF_001,
    RULE_BG_INTEG_ANCHOR_PENDING,
    RULE_BG_INTEG_COL_PENDING,
    RULE_BG_INTEG_REINF_PENDING,
    RULE_BG_MABHAS9_FLEX_CAP_BLOCKED,
    RULE_BG_NEG_EXT_PENDING,
    RULE_BG_POS_SIMPLE_PENDING,
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
    RULE_BG_SKIN_REINF_PENDING,
    RULE_BG_TABLE_2_11_99_PENDING,
    RULE_BG_TORSION_PENDING,
)
from beamgenius.registry.gatekeeper import build_blocked_workflow_trace

DEFAULT_MABHAS9_CHECK_RULES: Tuple[str, ...] = (
    RULE_BG_FLEX_MIN_001.rule_id,
    RULE_BG_SHEAR_MIN_001.rule_id,
    RULE_BG_SHEAR_SPACING_001.rule_id,
)


# ============================================================================
# DETERMINISTIC BLOCKED WORKFLOW EVALUATORS (Section 13)
# ============================================================================


def evaluate_longitudinal_bar_clear_spacing(
    geometry: BeamGeometry,
    *,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Blocked workflow for longitudinal bar horizontal clear spacing."""
    return build_blocked_workflow_trace(
        RULE_BG_DETAIL_SPACING_BLOCKED.rule_id,
        active_jurisdiction=jurisdiction_mode,
        normalized_inputs={"bw_mm": geometry.bw_mm, "h_mm": geometry.h_mm},
    )


def evaluate_layer_spacing(
    geometry: BeamGeometry,
    *,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Blocked workflow for multi-layer vertical clear spacing."""
    return build_blocked_workflow_trace(
        RULE_BG_DETAIL_LAYER_SPACING_BLOCKED.rule_id,
        active_jurisdiction=jurisdiction_mode,
        normalized_inputs={
            "bw_mm": geometry.bw_mm,
            "h_mm": geometry.h_mm,
            "layer_clear_spacing_mm": geometry.layer_clear_spacing_mm,
        },
    )


def evaluate_concrete_cover(
    geometry: BeamGeometry,
    *,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Blocked workflow for minimum concrete cover verification."""
    return build_blocked_workflow_trace(
        RULE_BG_DETAIL_COVER_BLOCKED.rule_id,
        active_jurisdiction=jurisdiction_mode,
        normalized_inputs={
            "bw_mm": geometry.bw_mm,
            "h_mm": geometry.h_mm,
            "clear_cover_mm": geometry.clear_cover_mm,
        },
    )


def evaluate_minimum_transverse_bar_diameter(
    geometry: BeamGeometry,
    *,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Blocked workflow for minimum transverse reinforcement diameter (Clause 11-5-6-11-9)."""
    return build_blocked_workflow_trace(
        RULE_BG_DETAIL_TRANS_DIA_PENDING.rule_id,
        active_jurisdiction=jurisdiction_mode,
        normalized_inputs={
            "bw_mm": geometry.bw_mm,
            "h_mm": geometry.h_mm,
            "stirrup_diameter_mm": geometry.stirrup_diameter_mm,
        },
    )


def evaluate_compression_rebar_lateral_support(
    geometry: BeamGeometry,
    *,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Blocked workflow for compression reinforcement lateral support spacing."""
    return build_blocked_workflow_trace(
        RULE_BG_DETAIL_COMP_LAT_PENDING.rule_id,
        active_jurisdiction=jurisdiction_mode,
        normalized_inputs={"bw_mm": geometry.bw_mm, "h_mm": geometry.h_mm},
    )


def evaluate_development_length(
    geometry: BeamGeometry,
    concrete: ConcreteMaterial,
    rebar: RebarMaterial,
    *,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Blocked workflow for bar development length Ld (Clause 2-3-6-9)."""
    return build_blocked_workflow_trace(
        RULE_BG_DEV_LENGTH_PENDING.rule_id,
        active_jurisdiction=jurisdiction_mode,
        normalized_inputs={
            "bw_mm": geometry.bw_mm,
            "h_mm": geometry.h_mm,
            "fc_prime_mpa": concrete.fc_prime_mpa,
            "fy_mpa": rebar.fy_mpa,
        },
    )


def evaluate_bar_cutoff(
    geometry: BeamGeometry,
    *,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Blocked workflow for flexural bar cutoff conditions (Clause 5-2-6-11-9)."""
    return build_blocked_workflow_trace(
        RULE_BG_CUTOFF_COND_PENDING.rule_id,
        active_jurisdiction=jurisdiction_mode,
        normalized_inputs={"bw_mm": geometry.bw_mm, "h_mm": geometry.h_mm},
    )


def evaluate_flexural_bar_extension(
    geometry: BeamGeometry,
    *,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Blocked workflow for flexural bar extension beyond cutoff (Clause 4-2-6-11-9)."""
    return build_blocked_workflow_trace(
        RULE_BG_FLEX_EXT_PENDING.rule_id,
        active_jurisdiction=jurisdiction_mode,
        normalized_inputs={"bw_mm": geometry.bw_mm, "h_mm": geometry.h_mm},
    )


def evaluate_negative_rebar_extension(
    geometry: BeamGeometry,
    *,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Blocked workflow for negative reinforcement extension equation."""
    return build_blocked_workflow_trace(
        RULE_BG_NEG_EXT_PENDING.rule_id,
        active_jurisdiction=jurisdiction_mode,
        normalized_inputs={"bw_mm": geometry.bw_mm, "h_mm": geometry.h_mm},
    )


def evaluate_positive_rebar_simple_support(
    geometry: BeamGeometry,
    *,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Blocked workflow for positive reinforcement at simple supports (Clause 2-3-6-11-9)."""
    return build_blocked_workflow_trace(
        RULE_BG_POS_SIMPLE_PENDING.rule_id,
        active_jurisdiction=jurisdiction_mode,
        normalized_inputs={"bw_mm": geometry.bw_mm, "h_mm": geometry.h_mm},
    )


def evaluate_structural_integrity_reinforcement(
    geometry: BeamGeometry,
    *,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Blocked workflow for structural integrity reinforcement."""
    return build_blocked_workflow_trace(
        RULE_BG_INTEG_REINF_PENDING.rule_id,
        active_jurisdiction=jurisdiction_mode,
        normalized_inputs={"bw_mm": geometry.bw_mm, "h_mm": geometry.h_mm},
    )


def evaluate_continuity_through_column(
    geometry: BeamGeometry,
    *,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Blocked workflow for structural integrity continuity through column region."""
    return build_blocked_workflow_trace(
        RULE_BG_INTEG_COL_PENDING.rule_id,
        active_jurisdiction=jurisdiction_mode,
        normalized_inputs={"bw_mm": geometry.bw_mm, "h_mm": geometry.h_mm},
    )


def evaluate_non_continuous_support_anchorage(
    geometry: BeamGeometry,
    *,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Blocked workflow for structural integrity anchorage at non-continuous supports."""
    return build_blocked_workflow_trace(
        RULE_BG_INTEG_ANCHOR_PENDING.rule_id,
        active_jurisdiction=jurisdiction_mode,
        normalized_inputs={"bw_mm": geometry.bw_mm, "h_mm": geometry.h_mm},
    )


def evaluate_bent_bar_anchorage(
    geometry: BeamGeometry,
    *,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Blocked workflow for bent-bar hook anchorage length."""
    return build_blocked_workflow_trace(
        RULE_BG_BENT_ANCHOR_PENDING.rule_id,
        active_jurisdiction=jurisdiction_mode,
        normalized_inputs={"bw_mm": geometry.bw_mm, "h_mm": geometry.h_mm},
    )


def evaluate_skin_reinforcement(
    geometry: BeamGeometry,
    *,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Blocked workflow for skin reinforcement spacing in deep webs."""
    return build_blocked_workflow_trace(
        RULE_BG_SKIN_REINF_PENDING.rule_id,
        active_jurisdiction=jurisdiction_mode,
        normalized_inputs={"bw_mm": geometry.bw_mm, "h_mm": geometry.h_mm},
    )


def evaluate_torsion(
    geometry: BeamGeometry,
    concrete: ConcreteMaterial,
    rebar: RebarMaterial,
    *,
    tu_nmm: Optional[float] = None,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Blocked workflow for beam torsion design/check."""
    return build_blocked_workflow_trace(
        RULE_BG_TORSION_PENDING.rule_id,
        active_jurisdiction=jurisdiction_mode,
        normalized_inputs={
            "bw_mm": geometry.bw_mm,
            "h_mm": geometry.h_mm,
            "fc_prime_mpa": concrete.fc_prime_mpa,
            "fy_mpa": rebar.fy_mpa,
            "tu_nmm": tu_nmm,
        },
    )


def evaluate_table_9_11_2_remaining_exceptions(
    geometry: BeamGeometry,
    *,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> CalculationTraceStep:
    """Blocked workflow for remaining unverified Table 9-11-2 / 2-11-99 exceptions."""
    return build_blocked_workflow_trace(
        RULE_BG_TABLE_2_11_99_PENDING.rule_id,
        active_jurisdiction=jurisdiction_mode,
        normalized_inputs={"bw_mm": geometry.bw_mm, "h_mm": geometry.h_mm},
    )


# ============================================================================
# REPORT AGGREGATION & ORCHESTRATION (Section 17)
# ============================================================================


def aggregate_compliance_report(
    trace_steps: Sequence[CalculationTraceStep],
    *,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> BeamComplianceReport:
    """Aggregate individual CalculationTraceStep outcomes into a BeamComplianceReport.

    Dominance hierarchy (Anti-Misleading-PASS Policy):
    1. Empty trace_steps -> OverallComplianceStatus.INVALID_INPUT
    2. Any step is INVALID_INPUT -> OverallComplianceStatus.INVALID_INPUT
    3. Any step is FAIL -> OverallComplianceStatus.FAIL
    4. Any step is UNVERIFIED_RULE_BLOCKED or JURISDICTION_BLOCKED -> OverallComplianceStatus.BLOCKED
    5. Any step is COMPUTED or NOT_APPLICABLE (without a full pass/exempt verdict) -> OverallComplianceStatus.PARTIAL
    6. All steps are PASS or EXEMPT -> OverallComplianceStatus.PASS
    """
    if not trace_steps:
        empty_diag = EngineeringDiagnostic(
            code="EMPTY_CHECK_REQUEST",
            severity=DiagnosticSeverity.ERROR,
            message="No calculation trace steps were provided to aggregate_compliance_report.",
        )
        return BeamComplianceReport(
            overall_status=OverallComplianceStatus.INVALID_INPUT,
            jurisdiction_mode=jurisdiction_mode,
            trace_steps=(),
            diagnostics=(empty_diag,),
            outcomes_by_rule={},
        )

    steps_tuple = tuple(trace_steps)
    all_diagnostics: List[EngineeringDiagnostic] = []
    outcomes_by_rule: Dict[str, EvaluationOutcome] = {}

    for step in steps_tuple:
        if step.rule_id in outcomes_by_rule:
            outcomes_by_rule[step.rule_id] = select_dominant_outcome(
                outcomes_by_rule[step.rule_id], step.outcome
            )
        else:
            outcomes_by_rule[step.rule_id] = step.outcome
        all_diagnostics.extend(step.diagnostics)

    outcomes = [step.outcome for step in steps_tuple]

    if any(outcome == EvaluationOutcome.INVALID_INPUT for outcome in outcomes):
        overall = OverallComplianceStatus.INVALID_INPUT
    elif any(outcome == EvaluationOutcome.FAIL for outcome in outcomes):
        overall = OverallComplianceStatus.FAIL
    elif any(
        outcome
        in (
            EvaluationOutcome.UNVERIFIED_RULE_BLOCKED,
            EvaluationOutcome.JURISDICTION_BLOCKED,
        )
        for outcome in outcomes
    ):
        overall = OverallComplianceStatus.BLOCKED
    elif any(
        outcome in (EvaluationOutcome.COMPUTED, EvaluationOutcome.NOT_APPLICABLE)
        for outcome in outcomes
    ):
        overall = OverallComplianceStatus.PARTIAL
    else:
        overall = OverallComplianceStatus.PASS

    return BeamComplianceReport(
        overall_status=overall,
        jurisdiction_mode=jurisdiction_mode,
        trace_steps=steps_tuple,
        diagnostics=tuple(all_diagnostics),
        outcomes_by_rule=outcomes_by_rule,
    )


def run_mabhas9_beam_check(
    geometry: BeamGeometry,
    concrete: ConcreteMaterial,
    rebar: RebarMaterial,
    *,
    stirrups: Optional[StirrupLayout] = None,
    as_provided_mm2: Optional[float] = None,
    as_required_by_analysis_mm2: Optional[float] = None,
    av_over_s_provided_mm2_per_mm: Optional[float] = None,
    vs_n: Optional[float] = None,
    vu_n: Optional[float] = None,
    vc_n: Optional[float] = None,
    nu_n: float = 0.0,
    mu_nmm: Optional[float] = None,
    tu_nmm: Optional[float] = None,
    phi_shear_explicit: Optional[float] = None,
    s_provided_mm: Optional[float] = None,
    st_provided_mm: Optional[float] = None,
    stirrup_angle_deg: float = 90.0,
    has_minimum_shear_reinforcement: bool = True,
    use_detailed_rho_w_equation: bool = False,
    rho_w: Optional[float] = None,
    ag_mm2: Optional[float] = None,
    max_longitudinal_bar_diameter_mm: Optional[float] = None,
    is_bundled: bool = False,
    has_compression_reinforcement: bool = False,
    min_compression_bar_diameter_mm: Optional[float] = None,
    compression_lateral_support_spacing_mm: Optional[float] = None,
    transverse_bar_diameter_mm: Optional[float] = None,
    aggregate_size_mm: Optional[float] = None,
    horizontal_clear_spacing_mm: Optional[float] = None,
    is_shotcrete: bool = False,
    rebar_layer_count: Optional[int] = None,
    layers_directly_aligned: Optional[bool] = None,
    cover_exposure: Optional[ConcreteCoverExposureClass] = None,
    cover_bar_diameter_mm: Optional[float] = None,
    provided_cover_mm: Optional[float] = None,
    has_headed_shear_reinforcement: bool = False,
    requested_rule_ids: Sequence[str] = DEFAULT_MABHAS9_CHECK_RULES,
    jurisdiction_mode: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
) -> BeamComplianceReport:
    """Orchestrate requested beam engineering checks and aggregate a BeamComplianceReport.

    Preserves every individual outcome and trace step in order and guarantees
    that the overall report status is never PASS if any requested check fails,
    has invalid input, or is blocked.

    Note: ``BG-SHEAR-VS-001`` evaluates the Eq. (9-8-15) demand only when both
    ``vu_n`` and ``vc_n`` are supplied, and ``BG-SHEAR-VS-MAX-001`` /
    ``BG-SHEAR-PHI-001`` full limit checks likewise require ``vc_n``.
    """
    if not requested_rule_ids:
        return aggregate_compliance_report((), jurisdiction_mode=jurisdiction_mode)

    steps: List[CalculationTraceStep] = []
    common_inputs: Mapping[str, ScalarInputValue] = {
        "bw_mm": geometry.bw_mm,
        "h_mm": geometry.h_mm,
        "d_effective_mm": geometry.d_effective_mm,
        "fc_prime_mpa": concrete.fc_prime_mpa,
        "fy_mpa": rebar.fy_mpa,
        "fyt_mpa": rebar.effective_fyt_mpa,
        "vs_n": vs_n,
        "vu_n": vu_n,
        "mu_nmm": mu_nmm,
        "tu_nmm": tu_nmm,
    }

    for rule_id in requested_rule_ids:
        if rule_id == RULE_BG_FLEX_MIN_001.rule_id:
            steps.append(
                evaluate_minimum_flexural_reinforcement(
                    geometry,
                    concrete,
                    rebar,
                    as_provided_mm2=as_provided_mm2,
                    as_required_by_analysis_mm2=as_required_by_analysis_mm2,
                    require_provided_rebar=True,
                    jurisdiction_mode=jurisdiction_mode,
                )
            )
        elif rule_id == RULE_BG_SHEAR_MIN_001.rule_id:
            steps.append(
                evaluate_minimum_shear_reinforcement(
                    geometry,
                    concrete,
                    rebar,
                    stirrups=stirrups,
                    av_over_s_provided_mm2_per_mm=av_over_s_provided_mm2_per_mm,
                    vu_n=vu_n,
                    phi_shear_explicit=phi_shear_explicit,
                    require_provided_stirrups=True,
                    jurisdiction_mode=jurisdiction_mode,
                )
            )
        elif rule_id == RULE_BG_SHEAR_SPACING_001.rule_id:
            steps.append(
                evaluate_maximum_stirrup_spacing(
                    geometry,
                    concrete,
                    vs_n=vs_n,
                    vu_n=vu_n,
                    stirrups=stirrups,
                    s_provided_mm=s_provided_mm,
                    st_provided_mm=st_provided_mm,
                    require_provided_stirrups=True,
                    jurisdiction_mode=jurisdiction_mode,
                )
            )
        elif rule_id == RULE_BG_FLEX_RECT_SINGLY_001.rule_id:
            steps.append(
                evaluate_mabhas9_flexural_capacity(
                    geometry,
                    concrete,
                    rebar,
                    as_provided_mm2=as_provided_mm2,
                    mu_nmm=mu_nmm,
                    require_design_inputs=True,
                    jurisdiction_mode=jurisdiction_mode,
                )
            )
        elif rule_id == RULE_BG_FLEX_STRESS_BLOCK.rule_id:
            steps.append(
                evaluate_mabhas9_stress_block_parameters(
                    concrete,
                    jurisdiction_mode=jurisdiction_mode,
                )
            )
        elif rule_id == RULE_BG_FLEX_TBEAM_B_EFF_001.rule_id:
            steps.append(
                evaluate_mabhas9_effective_flange_width(
                    geometry,
                    jurisdiction_mode=jurisdiction_mode,
                )
            )
        elif rule_id == RULE_BG_MABHAS9_FLEX_CAP_BLOCKED.rule_id:
            steps.append(
                build_blocked_workflow_trace(
                    rule_id,
                    active_jurisdiction=jurisdiction_mode,
                    normalized_inputs=common_inputs,
                    unit="N*mm",
                )
            )
        elif rule_id == RULE_BG_SHEAR_PHI_001.rule_id:
            steps.append(
                evaluate_mabhas9_shear_phi_factor(
                    vu_n=vu_n,
                    vc_n=vc_n,
                    vs_n=vs_n,
                    jurisdiction_mode=jurisdiction_mode,
                )
            )
        elif rule_id == RULE_BG_SHEAR_VC_001.rule_id:
            steps.append(
                evaluate_mabhas9_concrete_shear_resistance_vc(
                    geometry,
                    concrete,
                    has_minimum_shear_reinforcement=has_minimum_shear_reinforcement,
                    use_detailed_rho_w_equation=use_detailed_rho_w_equation,
                    rho_w=rho_w,
                    nu_n=nu_n,
                    ag_mm2=ag_mm2,
                    jurisdiction_mode=jurisdiction_mode,
                )
            )
        elif rule_id == RULE_BG_SHEAR_VS_001.rule_id:
            steps.append(
                evaluate_mabhas9_transverse_shear_resistance_vs(
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
            )
        elif rule_id == RULE_BG_SHEAR_VS_MAX_001.rule_id:
            steps.append(
                evaluate_mabhas9_shear_web_crushing_limit(
                    geometry,
                    concrete,
                    vs_n=vs_n,
                    vu_n=vu_n,
                    vc_n=vc_n,
                    has_minimum_shear_reinforcement=has_minimum_shear_reinforcement,
                    tu_nmm=tu_nmm,
                    jurisdiction_mode=jurisdiction_mode,
                )
            )
        elif rule_id == RULE_BG_DETAIL_TRANS_DIA_001.rule_id:
            steps.append(
                _verified_min_transverse_dia(
                    geometry,
                    max_longitudinal_bar_diameter_mm=(
                        max_longitudinal_bar_diameter_mm
                    ),
                    is_bundled=is_bundled,
                    transverse_bar_diameter_mm=transverse_bar_diameter_mm,
                    jurisdiction_mode=jurisdiction_mode,
                )
            )
        elif rule_id == RULE_BG_DETAIL_COMP_LAT_001.rule_id:
            steps.append(
                evaluate_compression_reinforcement_lateral_support_spacing(
                    geometry,
                    has_compression_reinforcement=has_compression_reinforcement,
                    min_compression_bar_diameter_mm=(
                        min_compression_bar_diameter_mm
                    ),
                    transverse_bar_diameter_mm=transverse_bar_diameter_mm,
                    compression_lateral_support_spacing_mm=(
                        compression_lateral_support_spacing_mm
                    ),
                    jurisdiction_mode=jurisdiction_mode,
                )
            )
        elif rule_id == RULE_BG_DETAIL_SPACING_001.rule_id:
            steps.append(
                _verified_bar_clear_spacing(
                    geometry,
                    max_bar_diameter_mm=max_longitudinal_bar_diameter_mm,
                    aggregate_size_mm=aggregate_size_mm,
                    provided_clear_spacing_mm=horizontal_clear_spacing_mm,
                    is_bundled=is_bundled,
                    is_shotcrete=is_shotcrete,
                    jurisdiction_mode=jurisdiction_mode,
                )
            )
        elif rule_id == RULE_BG_DETAIL_LAYER_SPACING_001.rule_id:
            steps.append(
                _verified_layer_clear_spacing(
                    geometry,
                    layer_count=rebar_layer_count,
                    layers_directly_aligned=layers_directly_aligned,
                    is_bundled=is_bundled,
                    jurisdiction_mode=jurisdiction_mode,
                )
            )
        elif rule_id == RULE_BG_DETAIL_COVER_001.rule_id:
            steps.append(
                _verified_min_concrete_cover(
                    geometry,
                    exposure=cover_exposure,
                    cover_bar_diameter_mm=cover_bar_diameter_mm,
                    provided_cover_mm=provided_cover_mm,
                    is_bundled=is_bundled,
                    has_headed_shear_reinforcement=(
                        has_headed_shear_reinforcement
                    ),
                    jurisdiction_mode=jurisdiction_mode,
                )
            )
        elif rule_id == RULE_BG_SHEAR_CAP_BLOCKED.rule_id:
            steps.append(
                evaluate_full_shear_capacity(
                    geometry,
                    concrete,
                    rebar,
                    vu_n=vu_n,
                    jurisdiction_mode=jurisdiction_mode,
                )
            )
        elif rule_id == RULE_BG_SHEAR_VC_BLOCKED.rule_id:
            steps.append(
                evaluate_concrete_shear_capacity_vc(
                    geometry,
                    concrete,
                    jurisdiction_mode=jurisdiction_mode,
                )
            )
        elif rule_id == RULE_BG_SHEAR_VS_DEMAND_BLOCKED.rule_id:
            steps.append(
                evaluate_required_shear_steel_demand_vs(
                    geometry,
                    concrete,
                    vu_n=vu_n,
                    jurisdiction_mode=jurisdiction_mode,
                )
            )
        elif rule_id == RULE_BG_SHEAR_VS_MAX_BLOCKED.rule_id:
            steps.append(
                evaluate_maximum_shear_steel_vs_max(
                    geometry,
                    concrete,
                    vs_n=vs_n,
                    jurisdiction_mode=jurisdiction_mode,
                )
            )
        else:
            steps.append(
                build_blocked_workflow_trace(
                    rule_id,
                    active_jurisdiction=jurisdiction_mode,
                    normalized_inputs=common_inputs,
                )
            )

    return aggregate_compliance_report(steps, jurisdiction_mode=jurisdiction_mode)
