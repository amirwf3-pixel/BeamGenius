"""Tests for deterministic domain validation and effective-depth precedence."""

from __future__ import annotations

import math

import pytest

from beamgenius.domain import (
    BeamComplianceReport,
    BeamGeometry,
    CalculationTraceStep,
    ConcreteMaterial,
    DiagnosticSeverity,
    EffectiveDepthResolution,
    EngineeringDiagnostic,
    EvaluationOutcome,
    FlangeCondition,
    JurisdictionMode,
    OverallComplianceStatus,
    RebarGroup,
    RebarMaterial,
    RuleCategory,
    RuleReference,
    SectionType,
    StirrupLayout,
    VerificationStatus,
    resolve_effective_depth,
    validate_beam_geometry,
    validate_concrete_material,
    validate_non_negative_force,
    validate_rebar_group,
    validate_rebar_material,
    validate_stirrup_layout,
)
from beamgenius.reference import (
    evaluate_mostofinejad_eq_5_48a_d_estimate,
    evaluate_mostofinejad_eq_5_48b_d_estimate,
)


@pytest.mark.parametrize("invalid_bw", [0.0, -300.0, float("nan"), float("inf")])
def test_reject_invalid_beam_width(invalid_bw: float) -> None:
    geom = BeamGeometry(bw_mm=invalid_bw, h_mm=500.0, d_effective_mm=435.0)
    diags = validate_beam_geometry(geom)
    assert any(d.code == "INVALID_BEAM_WIDTH" for d in diags)


@pytest.mark.parametrize("invalid_h", [0.0, -500.0, float("nan"), float("inf")])
def test_reject_invalid_beam_height(invalid_h: float) -> None:
    geom = BeamGeometry(bw_mm=300.0, h_mm=invalid_h, d_effective_mm=435.0)
    diags = validate_beam_geometry(geom)
    assert any(d.code == "INVALID_SECTION_HEIGHT" for d in diags)


@pytest.mark.parametrize("invalid_d", [0.0, -10.0, float("nan"), float("inf")])
def test_reject_invalid_effective_depth(invalid_d: float) -> None:
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=invalid_d)
    diags = validate_beam_geometry(geom)
    assert any(d.code == "INVALID_EFFECTIVE_DEPTH" for d in diags)


@pytest.mark.parametrize("impossible_d", [500.0, 550.0])
def test_reject_effective_depth_greater_or_equal_height(impossible_d: float) -> None:
    geom = BeamGeometry(bw_mm=300.0, h_mm=500.0, d_effective_mm=impossible_d)
    diags = validate_beam_geometry(geom)
    assert any(d.code == "IMPOSSIBLE_EFFECTIVE_DEPTH_GE_HEIGHT" for d in diags)


def test_reject_inconsistent_flange_geometry() -> None:
    # Rectangular section with flange in tension is inconsistent
    rect_with_flange = BeamGeometry(
        bw_mm=300.0,
        h_mm=500.0,
        d_effective_mm=435.0,
        section_type=SectionType.RECTANGULAR,
        flange_condition=FlangeCondition.FLANGE_IN_TENSION,
    )
    diags = validate_beam_geometry(rect_with_flange)
    assert any(d.code == "INCONSISTENT_RECTANGULAR_FLANGE_CONDITION" for d in diags)

    # T-section with bf <= bw is inconsistent
    t_narrow_flange = BeamGeometry(
        bw_mm=300.0,
        h_mm=500.0,
        d_effective_mm=435.0,
        section_type=SectionType.T_SECTION,
        flange_condition=FlangeCondition.FLANGE_IN_COMPRESSION,
        bf_mm=300.0,
        tf_mm=100.0,
    )
    diags_t = validate_beam_geometry(t_narrow_flange)
    assert any(d.code == "INCONSISTENT_FLANGE_WIDTH_LE_WEB" for d in diags_t)

    # T-section with tf >= h is inconsistent
    t_thick_flange = BeamGeometry(
        bw_mm=300.0,
        h_mm=500.0,
        d_effective_mm=435.0,
        section_type=SectionType.T_SECTION,
        flange_condition=FlangeCondition.FLANGE_IN_COMPRESSION,
        bf_mm=800.0,
        tf_mm=500.0,
    )
    diags_tf = validate_beam_geometry(t_thick_flange)
    assert any(d.code == "INCONSISTENT_FLANGE_THICKNESS_GE_HEIGHT" for d in diags_tf)

    # Integral with slab without tf_mm
    integral_no_tf = BeamGeometry(
        bw_mm=300.0,
        h_mm=500.0,
        d_effective_mm=435.0,
        is_integral_with_slab=True,
        tf_mm=None,
    )
    diags_int = validate_beam_geometry(integral_no_tf)
    assert any(d.code == "MISSING_SLAB_THICKNESS_FOR_INTEGRAL_BEAM" for d in diags_int)


@pytest.mark.parametrize("invalid_fc", [0.0, -25.0, float("nan"), float("inf")])
def test_reject_invalid_concrete_strength(invalid_fc: float) -> None:
    diags = validate_concrete_material(ConcreteMaterial(fc_prime_mpa=invalid_fc))
    assert any(d.code == "INVALID_CONCRETE_STRENGTH" for d in diags)


def test_rebar_material_validation_and_fy_550_limit() -> None:
    # Negative or zero fy
    assert any(
        d.code == "INVALID_REBAR_FY"
        for d in validate_rebar_material(RebarMaterial(fy_mpa=0.0))
    )
    assert any(
        d.code == "INVALID_REBAR_FYT"
        for d in validate_rebar_material(RebarMaterial(fy_mpa=400.0, fyt_mpa=-10.0))
    )

    # fy = 550.0 MPa is valid under BG-FLEX-MIN-001
    assert (
        validate_rebar_material(
            RebarMaterial(fy_mpa=550.0), enforce_mabhas9_flex_min_fy_limit=True
        )
        == ()
    )

    # fy = 550.001 MPa is rejected when enforce_mabhas9_flex_min_fy_limit=True
    diags_550 = validate_rebar_material(
        RebarMaterial(fy_mpa=550.001), enforce_mabhas9_flex_min_fy_limit=True
    )
    assert any(d.code == "FY_EXCEEDS_MABHAS9_FLEX_MIN_LIMIT" for d in diags_550)


def test_validate_rebar_group_and_stirrup_layout() -> None:
    bad_group = RebarGroup(bar_diameter_mm=-20.0, bar_count=0, layer_index=0)
    diags_grp = validate_rebar_group(bad_group, h_mm=500.0)
    codes = {d.code for d in diags_grp}
    assert "INVALID_REBAR_DIAMETER" in codes
    assert "INVALID_REBAR_COUNT" in codes
    assert "INVALID_REBAR_LAYER_INDEX" in codes

    bad_stirrup = StirrupLayout(
        bar_diameter_mm=0.0,
        num_legs=0,
        longitudinal_spacing_s_mm=-100.0,
        transverse_leg_spacing_st_mm=-50.0,
    )
    diags_st = validate_stirrup_layout(bad_stirrup)
    st_codes = {d.code for d in diags_st}
    assert "INVALID_STIRRUP_BAR_DIAMETER" in st_codes
    assert "INVALID_STIRRUP_NUM_LEGS" in st_codes
    assert "INVALID_STIRRUP_LONGITUDINAL_SPACING" in st_codes
    assert "INVALID_STIRRUP_TRANSVERSE_SPACING" in st_codes

    assert validate_non_negative_force(0.0, field_name="vs_n") == ()
    assert any(
        d.code == "INVALID_FORCE_VS_N"
        for d in validate_non_negative_force(-1.0, field_name="vs_n")
    )


def test_effective_depth_precedence_explicit_and_actual_geometry() -> None:
    # 1. Explicit d_effective_mm used directly
    geom_explicit = BeamGeometry(bw_mm=350.0, h_mm=600.0, d_effective_mm=538.0)
    res_explicit = resolve_effective_depth(geom_explicit)
    assert res_explicit.is_valid
    assert res_explicit.source == "EXPLICIT_D"
    assert res_explicit.d_mm == pytest.approx(538.0)

    # 2. Actual reinforcement geometry via cover + stirrup + 1 layer bar diameter
    # cover=40, stirrup=10, bar=20 -> centroid from bottom = 40 + 10 + 10 = 60 -> d = 600 - 60 = 540 mm
    geom_1layer = BeamGeometry(
        bw_mm=350.0,
        h_mm=600.0,
        clear_cover_mm=40.0,
        stirrup_diameter_mm=10.0,
        tension_rebar_groups=(RebarGroup(bar_diameter_mm=20.0, bar_count=4, layer_index=1),),
    )
    res_1layer = resolve_effective_depth(geom_1layer)
    assert res_1layer.is_valid
    assert res_1layer.source == "ACTUAL_REBAR_GEOMETRY"
    assert res_1layer.d_mm == pytest.approx(540.0)
    # Never equals h - 65 (535 mm)
    assert not math.isclose(res_1layer.d_mm or 0.0, 600.0 - 65.0)

    # 3. Actual reinforcement geometry via 2 layers with explicit layer_clear_spacing_mm = 25 mm
    # Layer 1 (3Φ20): y1 = 40 + 10 + 10 = 60 mm
    # Layer 2 (3Φ20): y2 = 40 + 10 + 20 + 25 + 10 = 105 mm
    # Equal area per layer -> weighted centroid y = (60 + 105) / 2 = 82.5 mm -> d = 600 - 82.5 = 517.5 mm
    geom_2layer = BeamGeometry(
        bw_mm=350.0,
        h_mm=600.0,
        clear_cover_mm=40.0,
        stirrup_diameter_mm=10.0,
        layer_clear_spacing_mm=25.0,
        tension_rebar_groups=(
            RebarGroup(bar_diameter_mm=20.0, bar_count=3, layer_index=1),
            RebarGroup(bar_diameter_mm=20.0, bar_count=3, layer_index=2),
        ),
    )
    res_2layer = resolve_effective_depth(geom_2layer)
    assert res_2layer.is_valid
    assert res_2layer.source == "ACTUAL_REBAR_GEOMETRY"
    assert res_2layer.d_mm == pytest.approx(517.5)
    # Never equals h - 90 (510 mm)
    assert not math.isclose(res_2layer.d_mm or 0.0, 600.0 - 90.0)

    # 4. Multi-layer without layer_clear_spacing_mm or centroids returns explicit diagnostic
    geom_missing_layer_spacing = BeamGeometry(
        bw_mm=350.0,
        h_mm=600.0,
        clear_cover_mm=40.0,
        stirrup_diameter_mm=10.0,
        tension_rebar_groups=(
            RebarGroup(bar_diameter_mm=20.0, bar_count=3, layer_index=1),
            RebarGroup(bar_diameter_mm=20.0, bar_count=3, layer_index=2),
        ),
    )
    res_missing = resolve_effective_depth(geom_missing_layer_spacing)
    assert not res_missing.is_valid
    assert res_missing.d_mm is None
    assert any(d.code == "MISSING_LAYER_CLEAR_SPACING" for d in res_missing.diagnostics)

    # 5. Missing both explicit d and rebar geometry returns MISSING_EFFECTIVE_DEPTH (never guesses h-65)
    geom_no_d = BeamGeometry(bw_mm=350.0, h_mm=600.0)
    res_no_d = resolve_effective_depth(geom_no_d)
    assert not res_no_d.is_valid
    assert res_no_d.d_mm is None
    assert any(d.code == "MISSING_EFFECTIVE_DEPTH" for d in res_no_d.diagnostics)

    # 6. Conflicting explicit d and geometric d is rejected
    geom_conflict = BeamGeometry(
        bw_mm=350.0,
        h_mm=600.0,
        d_effective_mm=535.0,
        clear_cover_mm=40.0,
        stirrup_diameter_mm=10.0,
        tension_rebar_groups=(RebarGroup(bar_diameter_mm=20.0, bar_count=4, layer_index=1),),
    )
    res_conflict = resolve_effective_depth(geom_conflict)
    assert not res_conflict.is_valid
    assert any(d.code == "CONFLICTING_EXPLICIT_AND_GEOMETRIC_D" for d in res_conflict.diagnostics)


def test_mostofinejad_5_48a_b_cannot_override_explicit_or_actual_d() -> None:
    geom_explicit = BeamGeometry(bw_mm=350.0, h_mm=600.0, d_effective_mm=542.0)
    step_a = evaluate_mostofinejad_eq_5_48a_d_estimate(
        600.0,
        geometry=geom_explicit,
        jurisdiction_mode=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    )
    assert step_a.outcome == EvaluationOutcome.INVALID_INPUT
    assert any(d.code == "CANNOT_OVERRIDE_EXPLICIT_EFFECTIVE_DEPTH" for d in step_a.diagnostics)

    geom_rebar = BeamGeometry(
        bw_mm=350.0,
        h_mm=600.0,
        clear_cover_mm=40.0,
        stirrup_diameter_mm=10.0,
        tension_rebar_groups=(RebarGroup(bar_diameter_mm=20.0, bar_count=4, layer_index=1),),
    )
    step_b = evaluate_mostofinejad_eq_5_48b_d_estimate(
        600.0,
        geometry=geom_rebar,
        jurisdiction_mode=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    )
    assert step_b.outcome == EvaluationOutcome.INVALID_INPUT
    assert any(d.code == "CANNOT_OVERRIDE_GEOMETRIC_EFFECTIVE_DEPTH" for d in step_b.diagnostics)


def test_aud_01_explicit_d_preserved_when_optional_detailing_metadata_incomplete() -> None:
    # 1. Explicit d_effective_mm=435.0 + clear_cover_mm=40.0 (with stirrup_diameter_mm=None)
    geom_cover_only = BeamGeometry(
        bw_mm=300.0,
        h_mm=500.0,
        d_effective_mm=435.0,
        clear_cover_mm=40.0,
        stirrup_diameter_mm=None,
    )
    res_cover_only = resolve_effective_depth(geom_cover_only)
    assert res_cover_only.is_valid is True
    assert res_cover_only.d_mm == pytest.approx(435.0)
    assert res_cover_only.source.lower() == "explicit_d"
    assert res_cover_only.diagnostics == ()

    # 2. Explicit d_effective_mm=435.0 + two-layer tension_rebar_groups with layer_clear_spacing_mm=None
    geom_two_layer_incomplete = BeamGeometry(
        bw_mm=300.0,
        h_mm=500.0,
        d_effective_mm=435.0,
        clear_cover_mm=40.0,
        stirrup_diameter_mm=10.0,
        layer_clear_spacing_mm=None,
        tension_rebar_groups=(
            RebarGroup(bar_diameter_mm=20.0, bar_count=3, layer_index=1),
            RebarGroup(bar_diameter_mm=20.0, bar_count=2, layer_index=2),
        ),
    )
    res_two_layer = resolve_effective_depth(geom_two_layer_incomplete)
    assert res_two_layer.is_valid is True
    assert res_two_layer.d_mm == pytest.approx(435.0)
    assert res_two_layer.source.lower() == "explicit_d"
    assert res_two_layer.diagnostics == ()

    # 3. Explicit d_effective_mm=435.0 + complete conflicting geometric reinforcement metadata
    geom_complete_conflict = BeamGeometry(
        bw_mm=300.0,
        h_mm=500.0,
        d_effective_mm=435.0,
        clear_cover_mm=40.0,
        stirrup_diameter_mm=10.0,
        tension_rebar_groups=(
            RebarGroup(bar_diameter_mm=20.0, bar_count=3, layer_index=1),
        ),
    )
    res_conflict = resolve_effective_depth(geom_complete_conflict)
    assert res_conflict.is_valid is False
    assert res_conflict.d_mm is None
    assert any(
        d.code == "CONFLICTING_EXPLICIT_AND_GEOMETRIC_D" for d in res_conflict.diagnostics
    )


def test_aud_03_runtime_tuple_coercion_on_domain_dataclasses() -> None:
    group = RebarGroup(bar_diameter_mm=20.0, bar_count=3, layer_index=1)
    geom = BeamGeometry(
        bw_mm=300.0,
        h_mm=500.0,
        d_effective_mm=435.0,
        tension_rebar_groups=[group],  # type: ignore[arg-type]
    )
    assert isinstance(geom.tension_rebar_groups, tuple)

    rule = RuleReference(
        rule_id="BG-TEST-001",
        title="Test Rule",
        category=RuleCategory.CODE_RULE,
        status=VerificationStatus.VERIFIED,
        jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
        source_document="Mabhas 9",
        pdf_page=1,
        printed_page=1,
        clause_or_equation="Test",
        symbolic_formula="x = 1",
        description="Test rule",
        execution_allowed=True,
        dependencies=["BG-DEP-001"],  # type: ignore[arg-type]
    )
    assert isinstance(rule.dependencies, tuple)

    diag = EngineeringDiagnostic(
        code="TEST_DIAG",
        severity=DiagnosticSeverity.INFO,
        message="Test diagnostic",
        rule_id="BG-TEST-001",
    )
    step = CalculationTraceStep(
        rule_id="BG-TEST-001",
        source_document="Mabhas 9",
        pdf_page=1,
        printed_page=1,
        clause_or_equation="Test",
        verification_status=VerificationStatus.VERIFIED,
        symbolic_formula="x = 1",
        normalized_inputs={"bw_mm": 300.0},
        intermediate_values={"x": 1.0},
        final_result=1.0,
        unit="mm^2",
        outcome=EvaluationOutcome.PASS,
        rule_reference=rule,
        diagnostics=[diag],  # type: ignore[arg-type]
        message="ok",
    )
    assert isinstance(step.diagnostics, tuple)

    report = BeamComplianceReport(
        overall_status=OverallComplianceStatus.PASS,
        jurisdiction_mode=JurisdictionMode.MABHAS_9_COMPLIANCE,
        trace_steps=[step],  # type: ignore[arg-type]
        diagnostics=[diag],  # type: ignore[arg-type]
        outcomes_by_rule={"BG-TEST-001": EvaluationOutcome.PASS},
    )
    assert isinstance(report.trace_steps, tuple)
    assert isinstance(report.diagnostics, tuple)

    d_res = EffectiveDepthResolution(
        d_mm=435.0,
        source="EXPLICIT_D",
        diagnostics=[diag],  # type: ignore[arg-type]
    )
    assert isinstance(d_res.diagnostics, tuple)

