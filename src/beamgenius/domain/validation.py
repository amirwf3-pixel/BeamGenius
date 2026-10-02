"""Deterministic input validation and effective-depth resolution for BeamGenius."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Dict, List, Optional, Sequence, Tuple

from beamgenius.domain.enums import (
    DiagnosticSeverity,
    FlangeCondition,
    SectionType,
)
from beamgenius.domain.models import (
    BeamGeometry,
    ConcreteMaterial,
    RebarGroup,
    RebarMaterial,
    StirrupLayout,
)
from beamgenius.domain.trace import EngineeringDiagnostic

# Verified code limit from Mabhas 9 Clause 9-11-5-1-1 / 9-11-5-1-2 (BG-FLEX-MIN-001)
MABHAS9_FLEX_MIN_MAX_FY_MPA: float = 550.0


@dataclass(frozen=True)
class EffectiveDepthResolution:
    """Result of resolving the effective depth d from BeamGeometry."""

    d_mm: Optional[float]
    source: str  # "EXPLICIT_D", "ACTUAL_REBAR_GEOMETRY", or "UNRESOLVED"
    diagnostics: Tuple[EngineeringDiagnostic, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "diagnostics", tuple(self.diagnostics))

    @property
    def is_valid(self) -> bool:
        """Return True if a valid effective depth was resolved without errors."""
        return self.d_mm is not None and not any(
            diag.severity == DiagnosticSeverity.ERROR for diag in self.diagnostics
        )


def _is_finite_positive(value: float) -> bool:
    return math.isfinite(value) and value > 0.0


def _is_finite_non_negative(value: float) -> bool:
    return math.isfinite(value) and value >= 0.0


def validate_rebar_group(
    group: RebarGroup,
    *,
    h_mm: Optional[float] = None,
    rule_id: Optional[str] = None,
) -> Tuple[EngineeringDiagnostic, ...]:
    """Validate a single RebarGroup for physical/mathematical validity."""
    diagnostics: List[EngineeringDiagnostic] = []

    if not _is_finite_positive(group.bar_diameter_mm):
        diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_REBAR_DIAMETER",
                severity=DiagnosticSeverity.ERROR,
                message=f"Rebar diameter must be finite and > 0 mm, got {group.bar_diameter_mm}.",
                rule_id=rule_id,
                field_name="bar_diameter_mm",
            )
        )
    elif h_mm is not None and _is_finite_positive(h_mm) and group.bar_diameter_mm >= h_mm:
        diagnostics.append(
            EngineeringDiagnostic(
                code="IMPOSSIBLE_REBAR_DIAMETER_FOR_HEIGHT",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    f"Rebar diameter ({group.bar_diameter_mm} mm) cannot be >= "
                    f"section height h ({h_mm} mm)."
                ),
                rule_id=rule_id,
                field_name="bar_diameter_mm",
            )
        )

    if isinstance(group.bar_count, bool) or not isinstance(group.bar_count, int) or group.bar_count <= 0:
        diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_REBAR_COUNT",
                severity=DiagnosticSeverity.ERROR,
                message=f"Rebar count must be a positive integer, got {group.bar_count}.",
                rule_id=rule_id,
                field_name="bar_count",
            )
        )

    if isinstance(group.layer_index, bool) or not isinstance(group.layer_index, int) or group.layer_index <= 0:
        diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_REBAR_LAYER_INDEX",
                severity=DiagnosticSeverity.ERROR,
                message=f"Rebar layer_index must be a positive integer >= 1, got {group.layer_index}.",
                rule_id=rule_id,
                field_name="layer_index",
            )
        )

    if group.centroid_from_tension_face_mm is not None:
        if not _is_finite_positive(group.centroid_from_tension_face_mm):
            diagnostics.append(
                EngineeringDiagnostic(
                    code="INVALID_REBAR_CENTROID",
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        "centroid_from_tension_face_mm must be finite and > 0 mm, "
                        f"got {group.centroid_from_tension_face_mm}."
                    ),
                    rule_id=rule_id,
                    field_name="centroid_from_tension_face_mm",
                )
            )
        elif (
            _is_finite_positive(group.bar_diameter_mm)
            and group.centroid_from_tension_face_mm < group.bar_diameter_mm / 2.0
        ):
            diagnostics.append(
                EngineeringDiagnostic(
                    code="IMPOSSIBLE_REBAR_CENTROID_BELOW_RADIUS",
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        f"centroid_from_tension_face_mm ({group.centroid_from_tension_face_mm} mm) "
                        f"cannot be less than bar radius ({group.bar_diameter_mm / 2.0} mm)."
                    ),
                    rule_id=rule_id,
                    field_name="centroid_from_tension_face_mm",
                )
            )
        elif h_mm is not None and _is_finite_positive(h_mm) and group.centroid_from_tension_face_mm >= h_mm:
            diagnostics.append(
                EngineeringDiagnostic(
                    code="IMPOSSIBLE_REBAR_CENTROID_EXCEEDS_HEIGHT",
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        f"centroid_from_tension_face_mm ({group.centroid_from_tension_face_mm} mm) "
                        f"must be < section height h ({h_mm} mm)."
                    ),
                    rule_id=rule_id,
                    field_name="centroid_from_tension_face_mm",
                )
            )

    return tuple(diagnostics)


def resolve_effective_depth(
    geometry: BeamGeometry,
    *,
    rule_id: Optional[str] = None,
) -> EffectiveDepthResolution:
    """Resolve effective depth d according to the Phase 1 Effective Depth Precedence Rule.

    Precedence & consistency rules:
    1. BG-MOST-5-48A/B (h - 65, h - 90) are NEVER used here.
    2. If actual reinforcement geometry provides a determinable centroid from the
       tension face, compute d_actual = h - y_centroid.
    3. If explicit d_effective_mm is supplied:
       - Validate 0 < d_effective_mm < h_mm.
       - If d_actual is also determinable and conflicts with d_effective_mm,
         emit an INVALID_INPUT error for inconsistent geometry.
       - Otherwise use explicit d_effective_mm.
    4. If explicit d_effective_mm is NOT supplied and actual reinforcement geometry
       is present but incomplete (e.g., multi-layer bars without layer spacing or
       centroids), emit an explicit diagnostic explaining what geometry is missing.
    5. If neither explicit d_effective_mm nor reinforcement geometry is supplied,
       emit an explicit diagnostic requiring d_effective_mm or reinforcement geometry.
    """
    diagnostics: List[EngineeringDiagnostic] = []

    if not _is_finite_positive(geometry.h_mm):
        diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_SECTION_HEIGHT",
                severity=DiagnosticSeverity.ERROR,
                message=f"Beam total height h_mm must be finite and > 0 mm, got {geometry.h_mm}.",
                rule_id=rule_id,
                field_name="h_mm",
            )
        )
        return EffectiveDepthResolution(
            d_mm=None,
            source="UNRESOLVED",
            diagnostics=tuple(diagnostics),
        )

    # Validate explicit d_effective_mm if provided
    explicit_d: Optional[float] = geometry.d_effective_mm
    if explicit_d is not None:
        if not _is_finite_positive(explicit_d):
            diagnostics.append(
                EngineeringDiagnostic(
                    code="INVALID_EFFECTIVE_DEPTH",
                    severity=DiagnosticSeverity.ERROR,
                    message=f"Effective depth d_effective_mm must be finite and > 0 mm, got {explicit_d}.",
                    rule_id=rule_id,
                    field_name="d_effective_mm",
                )
            )
            return EffectiveDepthResolution(
                d_mm=None,
                source="UNRESOLVED",
                diagnostics=tuple(diagnostics),
            )
        if explicit_d >= geometry.h_mm:
            diagnostics.append(
                EngineeringDiagnostic(
                    code="IMPOSSIBLE_EFFECTIVE_DEPTH_GE_HEIGHT",
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        f"Effective depth d_effective_mm ({explicit_d} mm) must be strictly "
                        f"less than total section height h_mm ({geometry.h_mm} mm)."
                    ),
                    rule_id=rule_id,
                    field_name="d_effective_mm",
                )
            )
            return EffectiveDepthResolution(
                d_mm=None,
                source="UNRESOLVED",
                diagnostics=tuple(diagnostics),
            )

    # Check if actual reinforcement geometry can determine d
    actual_d: Optional[float] = None
    if geometry.tension_rebar_groups:
        for grp in geometry.tension_rebar_groups:
            diagnostics.extend(validate_rebar_group(grp, h_mm=geometry.h_mm, rule_id=rule_id))
        if any(d.severity == DiagnosticSeverity.ERROR for d in diagnostics):
            return EffectiveDepthResolution(
                d_mm=None,
                source="UNRESOLVED",
                diagnostics=tuple(diagnostics),
            )

        all_have_explicit_centroid = all(
            grp.centroid_from_tension_face_mm is not None for grp in geometry.tension_rebar_groups
        )
        any_has_explicit_centroid = any(
            grp.centroid_from_tension_face_mm is not None for grp in geometry.tension_rebar_groups
        )

        if any_has_explicit_centroid and not all_have_explicit_centroid:
            if explicit_d is None:
                diagnostics.append(
                    EngineeringDiagnostic(
                        code="INCONSISTENT_REBAR_GROUP_CENTROIDS",
                        severity=DiagnosticSeverity.ERROR,
                        message=(
                            "Some tension_rebar_groups specify centroid_from_tension_face_mm "
                            "while others omit it; cannot deterministically resolve effective depth."
                        ),
                        rule_id=rule_id,
                        field_name="tension_rebar_groups",
                    )
                )
                return EffectiveDepthResolution(
                    d_mm=None,
                    source="UNRESOLVED",
                    diagnostics=tuple(diagnostics),
                )

        if all_have_explicit_centroid:
            total_area = sum(grp.total_area_mm2 for grp in geometry.tension_rebar_groups)
            weighted_moment = 0.0
            for grp in geometry.tension_rebar_groups:
                assert grp.centroid_from_tension_face_mm is not None
                weighted_moment += grp.total_area_mm2 * grp.centroid_from_tension_face_mm
            weighted_y = weighted_moment / total_area
            actual_d = geometry.h_mm - weighted_y
        elif geometry.clear_cover_mm is not None or geometry.stirrup_diameter_mm is not None:
            # Validate any explicitly supplied cover/stirrup/layer_spacing values first
            if geometry.clear_cover_mm is not None and not _is_finite_positive(
                geometry.clear_cover_mm
            ):
                diagnostics.append(
                    EngineeringDiagnostic(
                        code="INVALID_CLEAR_COVER",
                        severity=DiagnosticSeverity.ERROR,
                        message=(
                            "clear_cover_mm must be finite and > 0 mm when supplied, "
                            f"got {geometry.clear_cover_mm}."
                        ),
                        rule_id=rule_id,
                        field_name="clear_cover_mm",
                    )
                )
                return EffectiveDepthResolution(
                    d_mm=None,
                    source="UNRESOLVED",
                    diagnostics=tuple(diagnostics),
                )
            if geometry.stirrup_diameter_mm is not None and not _is_finite_non_negative(
                geometry.stirrup_diameter_mm
            ):
                diagnostics.append(
                    EngineeringDiagnostic(
                        code="INVALID_STIRRUP_DIAMETER_FOR_DEPTH",
                        severity=DiagnosticSeverity.ERROR,
                        message=(
                            "stirrup_diameter_mm must be finite and >= 0 mm when supplied, "
                            f"got {geometry.stirrup_diameter_mm}."
                        ),
                        rule_id=rule_id,
                        field_name="stirrup_diameter_mm",
                    )
                )
                return EffectiveDepthResolution(
                    d_mm=None,
                    source="UNRESOLVED",
                    diagnostics=tuple(diagnostics),
                )
            if (
                geometry.layer_clear_spacing_mm is not None
                and not _is_finite_positive(geometry.layer_clear_spacing_mm)
            ):
                diagnostics.append(
                    EngineeringDiagnostic(
                        code="MISSING_LAYER_CLEAR_SPACING",
                        severity=DiagnosticSeverity.ERROR,
                        message=(
                            "layer_clear_spacing_mm must be finite and > 0 mm when supplied, "
                            f"got {geometry.layer_clear_spacing_mm}."
                        ),
                        rule_id=rule_id,
                        field_name="layer_clear_spacing_mm",
                    )
                )
                return EffectiveDepthResolution(
                    d_mm=None,
                    source="UNRESOLVED",
                    diagnostics=tuple(diagnostics),
                )

            layers: Dict[int, List[RebarGroup]] = {}
            for grp in geometry.tension_rebar_groups:
                layers.setdefault(grp.layer_index, []).append(grp)

            max_layer = max(layers.keys())
            expected_layers = set(range(1, max_layer + 1))
            if set(layers.keys()) != expected_layers:
                diagnostics.append(
                    EngineeringDiagnostic(
                        code="NON_CONTIGUOUS_REBAR_LAYERS",
                        severity=DiagnosticSeverity.ERROR,
                        message=(
                            f"Rebar layer indices must be contiguous starting at 1, "
                            f"got {sorted(layers.keys())}."
                        ),
                        rule_id=rule_id,
                        field_name="tension_rebar_groups",
                    )
                )
                return EffectiveDepthResolution(
                    d_mm=None,
                    source="UNRESOLVED",
                    diagnostics=tuple(diagnostics),
                )

            has_complete_layer_metadata = (
                geometry.clear_cover_mm is not None
                and geometry.stirrup_diameter_mm is not None
                and (max_layer == 1 or geometry.layer_clear_spacing_mm is not None)
            )

            if has_complete_layer_metadata:
                assert geometry.clear_cover_mm is not None
                assert geometry.stirrup_diameter_mm is not None
                layer_bottom_y: Dict[int, float] = {}
                current_bottom = geometry.clear_cover_mm + geometry.stirrup_diameter_mm
                for layer_idx in range(1, max_layer + 1):
                    layer_bottom_y[layer_idx] = current_bottom
                    layer_max_db = max(g.bar_diameter_mm for g in layers[layer_idx])
                    spacing = (
                        geometry.layer_clear_spacing_mm
                        if geometry.layer_clear_spacing_mm is not None
                        else 0.0
                    )
                    current_bottom = current_bottom + layer_max_db + spacing

                total_area = sum(grp.total_area_mm2 for grp in geometry.tension_rebar_groups)
                weighted_y = (
                    sum(
                        grp.total_area_mm2
                        * (layer_bottom_y[grp.layer_index] + grp.bar_diameter_mm / 2.0)
                        for grp in geometry.tension_rebar_groups
                    )
                    / total_area
                )
                actual_d = geometry.h_mm - weighted_y
            elif explicit_d is None:
                # Only fail on incomplete optional detailing metadata when explicit_d is absent
                if geometry.clear_cover_mm is None:
                    diagnostics.append(
                        EngineeringDiagnostic(
                            code="INVALID_CLEAR_COVER",
                            severity=DiagnosticSeverity.ERROR,
                            message=(
                                "clear_cover_mm must be finite and > 0 mm when deriving "
                                "effective depth from reinforcement geometry."
                            ),
                            rule_id=rule_id,
                            field_name="clear_cover_mm",
                        )
                    )
                elif geometry.stirrup_diameter_mm is None:
                    diagnostics.append(
                        EngineeringDiagnostic(
                            code="INVALID_STIRRUP_DIAMETER_FOR_DEPTH",
                            severity=DiagnosticSeverity.ERROR,
                            message=(
                                "stirrup_diameter_mm must be explicitly supplied (>= 0 mm) when "
                                "deriving effective depth from clear_cover_mm and rebar layers."
                            ),
                            rule_id=rule_id,
                            field_name="stirrup_diameter_mm",
                        )
                    )
                elif max_layer > 1 and geometry.layer_clear_spacing_mm is None:
                    diagnostics.append(
                        EngineeringDiagnostic(
                            code="MISSING_LAYER_CLEAR_SPACING",
                            severity=DiagnosticSeverity.ERROR,
                            message=(
                                "Multi-layer tension reinforcement requires explicit positive "
                                "layer_clear_spacing_mm (or explicit group centroids) to "
                                "deterministically compute effective depth d."
                            ),
                            rule_id=rule_id,
                            field_name="layer_clear_spacing_mm",
                        )
                    )
                return EffectiveDepthResolution(
                    d_mm=None,
                    source="UNRESOLVED",
                    diagnostics=tuple(diagnostics),
                )
        elif explicit_d is None and len(geometry.tension_rebar_groups) > 0:
            max_layer_no_cover = max(grp.layer_index for grp in geometry.tension_rebar_groups)
            if max_layer_no_cover > 1 and geometry.layer_clear_spacing_mm is None:
                diagnostics.append(
                    EngineeringDiagnostic(
                        code="MISSING_LAYER_CLEAR_SPACING",
                        severity=DiagnosticSeverity.ERROR,
                        message=(
                            "Multi-layer tension reinforcement requires explicit positive "
                            "layer_clear_spacing_mm and cover/stirrup geometry (or explicit "
                            "group centroids) to deterministically compute effective depth d."
                        ),
                        rule_id=rule_id,
                        field_name="layer_clear_spacing_mm",
                    )
                )
                return EffectiveDepthResolution(
                    d_mm=None,
                    source="UNRESOLVED",
                    diagnostics=tuple(diagnostics),
                )

    if actual_d is not None:
        if actual_d <= 0.0 or actual_d >= geometry.h_mm:
            diagnostics.append(
                EngineeringDiagnostic(
                    code="IMPOSSIBLE_DERIVED_EFFECTIVE_DEPTH",
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        f"Derived effective depth d ({actual_d} mm) from reinforcement geometry "
                        f"is outside valid range (0, {geometry.h_mm} mm)."
                    ),
                    rule_id=rule_id,
                    field_name="tension_rebar_groups",
                )
            )
            return EffectiveDepthResolution(
                d_mm=None,
                source="UNRESOLVED",
                diagnostics=tuple(diagnostics),
            )
        if explicit_d is not None:
            if abs(explicit_d - actual_d) > 1e-6:
                diagnostics.append(
                    EngineeringDiagnostic(
                        code="CONFLICTING_EXPLICIT_AND_GEOMETRIC_D",
                        severity=DiagnosticSeverity.ERROR,
                        message=(
                            f"Explicit d_effective_mm ({explicit_d} mm) conflicts with "
                            f"effective depth derived from actual reinforcement geometry ({actual_d} mm)."
                        ),
                        rule_id=rule_id,
                        field_name="d_effective_mm",
                    )
                )
                return EffectiveDepthResolution(
                    d_mm=None,
                    source="UNRESOLVED",
                    diagnostics=tuple(diagnostics),
                )
            return EffectiveDepthResolution(
                d_mm=explicit_d,
                source="EXPLICIT_D",
                diagnostics=tuple(diagnostics),
            )
        return EffectiveDepthResolution(
            d_mm=actual_d,
            source="ACTUAL_REBAR_GEOMETRY",
            diagnostics=tuple(diagnostics),
        )

    if explicit_d is not None:
        return EffectiveDepthResolution(
            d_mm=explicit_d,
            source="EXPLICIT_D",
            diagnostics=tuple(diagnostics),
        )

    diagnostics.append(
        EngineeringDiagnostic(
            code="MISSING_EFFECTIVE_DEPTH",
            severity=DiagnosticSeverity.ERROR,
            message=(
                "Effective depth d is not determinable: provide explicit d_effective_mm "
                "or complete reinforcement geometry (centroids or cover + stirrup diameter). "
                "Automatic fallback to h - 65 or h - 90 is prohibited."
            ),
            rule_id=rule_id,
            field_name="d_effective_mm",
        )
    )
    return EffectiveDepthResolution(
        d_mm=None,
        source="UNRESOLVED",
        diagnostics=tuple(diagnostics),
    )


def validate_beam_geometry(
    geometry: BeamGeometry,
    *,
    require_effective_depth: bool = True,
    rule_id: Optional[str] = None,
) -> Tuple[EngineeringDiagnostic, ...]:
    """Validate BeamGeometry dimensions, flange consistency, and effective depth."""
    diagnostics: List[EngineeringDiagnostic] = []

    if not _is_finite_positive(geometry.bw_mm):
        diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_BEAM_WIDTH",
                severity=DiagnosticSeverity.ERROR,
                message=f"Beam web width bw_mm must be finite and > 0 mm, got {geometry.bw_mm}.",
                rule_id=rule_id,
                field_name="bw_mm",
            )
        )

    if not _is_finite_positive(geometry.h_mm):
        diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_SECTION_HEIGHT",
                severity=DiagnosticSeverity.ERROR,
                message=f"Beam height h_mm must be finite and > 0 mm, got {geometry.h_mm}.",
                rule_id=rule_id,
                field_name="h_mm",
            )
        )

    if geometry.section_type == SectionType.RECTANGULAR:
        if geometry.flange_condition != FlangeCondition.NO_FLANGE:
            diagnostics.append(
                EngineeringDiagnostic(
                    code="INCONSISTENT_RECTANGULAR_FLANGE_CONDITION",
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        "RECTANGULAR section cannot have flange_condition "
                        f"{geometry.flange_condition.value}."
                    ),
                    rule_id=rule_id,
                    field_name="flange_condition",
                )
            )
    else:
        if geometry.bf_mm is not None:
            if not _is_finite_positive(geometry.bf_mm):
                diagnostics.append(
                    EngineeringDiagnostic(
                        code="INVALID_FLANGE_WIDTH",
                        severity=DiagnosticSeverity.ERROR,
                        message=f"Flange width bf_mm must be finite and > 0 mm, got {geometry.bf_mm}.",
                        rule_id=rule_id,
                        field_name="bf_mm",
                    )
                )
            elif _is_finite_positive(geometry.bw_mm) and geometry.bf_mm <= geometry.bw_mm:
                diagnostics.append(
                    EngineeringDiagnostic(
                        code="INCONSISTENT_FLANGE_WIDTH_LE_WEB",
                        severity=DiagnosticSeverity.ERROR,
                        message=(
                            f"Flange width bf_mm ({geometry.bf_mm} mm) for {geometry.section_type.value} "
                            f"must be > web width bw_mm ({geometry.bw_mm} mm)."
                        ),
                        rule_id=rule_id,
                        field_name="bf_mm",
                    )
                )

    if geometry.tf_mm is not None:
        if not _is_finite_positive(geometry.tf_mm):
            diagnostics.append(
                EngineeringDiagnostic(
                    code="INVALID_FLANGE_THICKNESS",
                    severity=DiagnosticSeverity.ERROR,
                    message=f"Flange/slab thickness tf_mm must be finite and > 0 mm, got {geometry.tf_mm}.",
                    rule_id=rule_id,
                    field_name="tf_mm",
                )
            )
        elif (
            geometry.section_type in (SectionType.T_SECTION, SectionType.L_SECTION)
            and _is_finite_positive(geometry.h_mm)
            and geometry.tf_mm >= geometry.h_mm
        ):
            diagnostics.append(
                EngineeringDiagnostic(
                    code="INCONSISTENT_FLANGE_THICKNESS_GE_HEIGHT",
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        f"Flange thickness tf_mm ({geometry.tf_mm} mm) for flanged section "
                        f"must be < total beam height h_mm ({geometry.h_mm} mm)."
                    ),
                    rule_id=rule_id,
                    field_name="tf_mm",
                )
            )

    if geometry.is_integral_with_slab and geometry.tf_mm is None:
        diagnostics.append(
            EngineeringDiagnostic(
                code="MISSING_SLAB_THICKNESS_FOR_INTEGRAL_BEAM",
                severity=DiagnosticSeverity.ERROR,
                message="is_integral_with_slab=True requires explicit slab thickness tf_mm.",
                rule_id=rule_id,
                field_name="tf_mm",
            )
        )

    for grp in geometry.tension_rebar_groups:
        diagnostics.extend(
            validate_rebar_group(
                grp,
                h_mm=geometry.h_mm if _is_finite_positive(geometry.h_mm) else None,
                rule_id=rule_id,
            )
        )

    if require_effective_depth and not any(
        d.severity == DiagnosticSeverity.ERROR for d in diagnostics
    ):
        resolution = resolve_effective_depth(geometry, rule_id=rule_id)
        diagnostics.extend(resolution.diagnostics)

    return tuple(diagnostics)


def validate_concrete_material(
    concrete: ConcreteMaterial,
    *,
    rule_id: Optional[str] = None,
) -> Tuple[EngineeringDiagnostic, ...]:
    """Validate ConcreteMaterial properties."""
    diagnostics: List[EngineeringDiagnostic] = []
    if not _is_finite_positive(concrete.fc_prime_mpa):
        diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_CONCRETE_STRENGTH",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    f"Concrete compressive strength fc_prime_mpa must be finite and > 0 MPa, "
                    f"got {concrete.fc_prime_mpa}."
                ),
                rule_id=rule_id,
                field_name="fc_prime_mpa",
            )
        )
    return tuple(diagnostics)


def validate_rebar_material(
    rebar: RebarMaterial,
    *,
    enforce_mabhas9_flex_min_fy_limit: bool = False,
    require_fyt: bool = False,
    rule_id: Optional[str] = None,
) -> Tuple[EngineeringDiagnostic, ...]:
    """Validate RebarMaterial properties and applicable verified code limits."""
    diagnostics: List[EngineeringDiagnostic] = []

    if not _is_finite_positive(rebar.fy_mpa):
        diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_REBAR_FY",
                severity=DiagnosticSeverity.ERROR,
                message=f"Rebar yield strength fy_mpa must be finite and > 0 MPa, got {rebar.fy_mpa}.",
                rule_id=rule_id,
                field_name="fy_mpa",
            )
        )
    elif enforce_mabhas9_flex_min_fy_limit and rebar.fy_mpa > MABHAS9_FLEX_MIN_MAX_FY_MPA:
        diagnostics.append(
            EngineeringDiagnostic(
                code="FY_EXCEEDS_MABHAS9_FLEX_MIN_LIMIT",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    f"Longitudinal yield strength fy_mpa ({rebar.fy_mpa} MPa) exceeds "
                    f"verified Mabhas 9 limit of {MABHAS9_FLEX_MIN_MAX_FY_MPA} MPa for BG-FLEX-MIN-001."
                ),
                rule_id=rule_id,
                field_name="fy_mpa",
            )
        )

    if rebar.fyt_mpa is not None and not _is_finite_positive(rebar.fyt_mpa):
        diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_REBAR_FYT",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    f"Transverse rebar yield strength fyt_mpa must be finite and > 0 MPa, "
                    f"got {rebar.fyt_mpa}."
                ),
                rule_id=rule_id,
                field_name="fyt_mpa",
            )
        )
    elif require_fyt and not _is_finite_positive(rebar.effective_fyt_mpa):
        diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_EFFECTIVE_FYT",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    f"Effective transverse yield strength fyt must be finite and > 0 MPa, "
                    f"got {rebar.effective_fyt_mpa}."
                ),
                rule_id=rule_id,
                field_name="fyt_mpa",
            )
        )

    if not _is_finite_positive(rebar.es_mpa):
        diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_REBAR_ES",
                severity=DiagnosticSeverity.ERROR,
                message=f"Modulus of elasticity es_mpa must be finite and > 0 MPa, got {rebar.es_mpa}.",
                rule_id=rule_id,
                field_name="es_mpa",
            )
        )

    return tuple(diagnostics)


def validate_stirrup_layout(
    stirrups: StirrupLayout,
    *,
    require_transverse_spacing: bool = False,
    rule_id: Optional[str] = None,
) -> Tuple[EngineeringDiagnostic, ...]:
    """Validate StirrupLayout parameters."""
    diagnostics: List[EngineeringDiagnostic] = []

    if not _is_finite_positive(stirrups.bar_diameter_mm):
        diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_STIRRUP_BAR_DIAMETER",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    f"Stirrup bar_diameter_mm must be finite and > 0 mm, "
                    f"got {stirrups.bar_diameter_mm}."
                ),
                rule_id=rule_id,
                field_name="bar_diameter_mm",
            )
        )

    if isinstance(stirrups.num_legs, bool) or not isinstance(stirrups.num_legs, int) or stirrups.num_legs <= 0:
        diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_STIRRUP_NUM_LEGS",
                severity=DiagnosticSeverity.ERROR,
                message=f"Stirrup num_legs must be a positive integer, got {stirrups.num_legs}.",
                rule_id=rule_id,
                field_name="num_legs",
            )
        )

    if not _is_finite_positive(stirrups.longitudinal_spacing_s_mm):
        diagnostics.append(
            EngineeringDiagnostic(
                code="INVALID_STIRRUP_LONGITUDINAL_SPACING",
                severity=DiagnosticSeverity.ERROR,
                message=(
                    "Stirrup longitudinal_spacing_s_mm must be finite and > 0 mm, "
                    f"got {stirrups.longitudinal_spacing_s_mm}."
                ),
                rule_id=rule_id,
                field_name="longitudinal_spacing_s_mm",
            )
        )

    if stirrups.transverse_leg_spacing_st_mm is not None:
        if not _is_finite_positive(stirrups.transverse_leg_spacing_st_mm):
            diagnostics.append(
                EngineeringDiagnostic(
                    code="INVALID_STIRRUP_TRANSVERSE_SPACING",
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        "Stirrup transverse_leg_spacing_st_mm must be finite and > 0 mm, "
                        f"got {stirrups.transverse_leg_spacing_st_mm}."
                    ),
                    rule_id=rule_id,
                    field_name="transverse_leg_spacing_st_mm",
                )
            )
    elif require_transverse_spacing:
        diagnostics.append(
            EngineeringDiagnostic(
                code="MISSING_STIRRUP_TRANSVERSE_SPACING",
                severity=DiagnosticSeverity.ERROR,
                message="Stirrup transverse_leg_spacing_st_mm is required for full spacing verification.",
                rule_id=rule_id,
                field_name="transverse_leg_spacing_st_mm",
            )
        )

    return tuple(diagnostics)


def validate_non_negative_force(
    value_n: float,
    *,
    field_name: str,
    rule_id: Optional[str] = None,
) -> Tuple[EngineeringDiagnostic, ...]:
    """Validate that a force input (such as Vs or Vu) is finite and >= 0 N."""
    if not _is_finite_non_negative(value_n):
        return (
            EngineeringDiagnostic(
                code=f"INVALID_FORCE_{field_name.upper()}",
                severity=DiagnosticSeverity.ERROR,
                message=f"Force {field_name} must be finite and >= 0 N, got {value_n}.",
                rule_id=rule_id,
                field_name=field_name,
            ),
        )
    return ()
