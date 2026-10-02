"""Immutable domain models for BeamGenius Phase 1 engineering core.

All dimensional, force, moment, and stress attributes use canonical internal SI
structural units:
- length: mm
- area: mm^2
- force: N
- moment: N*mm
- stress: MPa (N/mm^2)
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Optional, Tuple

from beamgenius.domain.enums import FlangeCondition, SectionType


@dataclass(frozen=True)
class RebarGroup:
    """A group of identical longitudinal reinforcing bars in a single layer.

    Attributes:
        bar_diameter_mm: Nominal bar diameter in mm.
        bar_count: Number of bars in this group.
        layer_index: 1-based layer index measured from the extreme tension face.
        centroid_from_tension_face_mm: Optional explicit distance from the
            extreme tension fiber to the centroid of this bar group in mm.
    """

    bar_diameter_mm: float
    bar_count: int
    layer_index: int = 1
    centroid_from_tension_face_mm: Optional[float] = None

    @property
    def single_bar_area_mm2(self) -> float:
        """Return nominal area of a single bar (pi * db^2 / 4) in mm^2."""
        return math.pi * (self.bar_diameter_mm ** 2) / 4.0

    @property
    def total_area_mm2(self) -> float:
        """Return total cross-sectional area of the bar group in mm^2."""
        return self.bar_count * self.single_bar_area_mm2


@dataclass(frozen=True)
class StirrupLayout:
    """Transverse shear reinforcement configuration at a beam section.

    Attributes:
        bar_diameter_mm: Nominal stirrup bar diameter in mm.
        num_legs: Number of vertical/transverse shear-resisting legs across web.
        longitudinal_spacing_s_mm: Center-to-center spacing along beam axis (s) in mm.
        transverse_leg_spacing_st_mm: Center-to-center spacing of legs across
            beam width (st) in mm, when applicable.
    """

    bar_diameter_mm: float
    num_legs: int
    longitudinal_spacing_s_mm: float
    transverse_leg_spacing_st_mm: Optional[float] = None

    @property
    def single_leg_area_mm2(self) -> float:
        """Return cross-sectional area of one stirrup leg in mm^2."""
        return math.pi * (self.bar_diameter_mm ** 2) / 4.0

    @property
    def av_mm2(self) -> float:
        """Return total transverse shear steel area Av within spacing s in mm^2."""
        return self.num_legs * self.single_leg_area_mm2

    @property
    def av_over_s_mm2_per_mm(self) -> float:
        """Return provided shear reinforcement ratio Av / s in mm^2/mm."""
        return self.av_mm2 / self.longitudinal_spacing_s_mm


@dataclass(frozen=True)
class BeamGeometry:
    """Cross-sectional geometry and reinforcement placement of a beam section.

    Attributes:
        bw_mm: Web width (or rectangular width b) in mm.
        h_mm: Overall section depth in mm.
        d_effective_mm: Explicit effective depth d from extreme compression
            fiber to centroid of tensile reinforcement in mm.
        section_type: Section shape classification (RECTANGULAR, T_SECTION, L_SECTION).
        flange_condition: Flange stress condition for T/L sections.
        bf_mm: Effective flange width in mm (for T/L sections).
        tf_mm: Flange / slab thickness in mm (for T/L sections or slab-integral beams).
        is_integral_with_slab: True if beam is cast monolithically/integrally with slab.
        is_one_way_joist: True if member is a one-way joist.
        tension_rebar_groups: Longitudinal tension reinforcement groups.
        clear_cover_mm: Concrete clear cover to stirrups/outer bars in mm.
        stirrup_diameter_mm: Stirrup bar diameter in mm used for geometry calculation.
        layer_clear_spacing_mm: Vertical clear spacing between rebar layers in mm.
        clear_web_spacing_sw_mm: Clear distance between adjacent webs sw in mm
            (for T/L effective flange width per Mabhas 9 Table 9-6-1).
        clear_span_ln_mm: Beam clear span ln in mm (for T/L effective flange width
            per Mabhas 9 Table 9-6-1).
        is_isolated_t_beam: True if the section is an isolated T-beam governed by
            Mabhas 9 Clause 9-6-3-3-2.
    """

    bw_mm: float
    h_mm: float
    d_effective_mm: Optional[float] = None
    section_type: SectionType = SectionType.RECTANGULAR
    flange_condition: FlangeCondition = FlangeCondition.NO_FLANGE
    bf_mm: Optional[float] = None
    tf_mm: Optional[float] = None
    is_integral_with_slab: bool = False
    is_one_way_joist: bool = False
    tension_rebar_groups: Tuple[RebarGroup, ...] = ()
    clear_cover_mm: Optional[float] = None
    stirrup_diameter_mm: Optional[float] = None
    layer_clear_spacing_mm: Optional[float] = None
    clear_web_spacing_sw_mm: Optional[float] = None
    clear_span_ln_mm: Optional[float] = None
    is_isolated_t_beam: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "tension_rebar_groups", tuple(self.tension_rebar_groups))

    @property
    def provided_tensile_area_mm2(self) -> Optional[float]:
        """Return total tensile steel area from tension_rebar_groups if present."""
        if not self.tension_rebar_groups:
            return None
        return sum(group.total_area_mm2 for group in self.tension_rebar_groups)


@dataclass(frozen=True)
class ConcreteMaterial:
    """Concrete material properties.

    Attributes:
        fc_prime_mpa: Specified cylinder compressive strength f'c in MPa.
        is_steel_fiber_normal_rc: True for steel-fiber normal-weight reinforced
            concrete (used in Table 9-11-2 Exception 3 evaluation).
    """

    fc_prime_mpa: float
    is_steel_fiber_normal_rc: bool = False


@dataclass(frozen=True)
class RebarMaterial:
    """Reinforcing steel material properties.

    Attributes:
        fy_mpa: Specified yield strength of longitudinal reinforcement fy in MPa.
        fyt_mpa: Specified yield strength of transverse reinforcement fyt in MPa.
            If None, defaults to fy_mpa when accessed via effective_fyt_mpa.
        es_mpa: Modulus of elasticity Es in MPa (default 200,000 MPa).
    """

    fy_mpa: float
    fyt_mpa: Optional[float] = None
    es_mpa: float = 200_000.0

    @property
    def effective_fyt_mpa(self) -> float:
        """Return fyt_mpa if explicitly specified, otherwise fy_mpa."""
        return self.fyt_mpa if self.fyt_mpa is not None else self.fy_mpa
