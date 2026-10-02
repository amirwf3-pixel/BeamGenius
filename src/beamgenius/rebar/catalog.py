"""Mathematical rebar catalog and area-enumeration utility for BeamGenius Phase 1.

GOVERNANCE RESTRICTION:
This module provides purely mathematical cross-sectional area calculations
(Ab = pi * db^2 / 4, As_total = sum(n_i * Ab_i)) and deterministic enumeration
of bar combinations meeting or exceeding a target area.

It does NOT evaluate clear spacing, concrete cover, development length,
anchorage, detailing, capacity, or constructability, and every candidate
exposes `constructability_verified = False`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import List, Optional, Sequence, Tuple

from beamgenius.domain.models import RebarGroup

STANDARD_REBAR_DIAMETERS_MM: Tuple[int, ...] = (
    10,
    12,
    14,
    16,
    18,
    20,
    22,
    25,
    28,
    30,
    32,
    36,
    40,
)


@dataclass(frozen=True)
class RebarCatalogCandidate:
    """Mathematical bar combination candidate from the rebar catalog.

    `constructability_verified` is permanently fixed to `False` in Phase 1
    because bar spacing, cover, development, and detailing rules are not yet
    verified in `docs/VERIFIED_RULES.md`.
    """

    groups: Tuple[RebarGroup, ...]
    total_area_mm2: float
    target_area_mm2: float
    excess_area_mm2: float
    constructability_verified: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "groups", tuple(self.groups))
        object.__setattr__(self, "constructability_verified", False)

    @property
    def total_bar_count(self) -> int:
        """Return total number of bars across all groups in this candidate."""
        return sum(grp.bar_count for grp in self.groups)

    @property
    def label(self) -> str:
        """Return a deterministic mathematical notation string (e.g. '2Φ25 + 1Φ30')."""
        parts: List[str] = []
        for grp in self.groups:
            db_val = (
                int(grp.bar_diameter_mm)
                if float(grp.bar_diameter_mm).is_integer()
                else grp.bar_diameter_mm
            )
            parts.append(f"{grp.bar_count}Φ{db_val}")
        return " + ".join(parts)


def compute_single_bar_area_mm2(bar_diameter_mm: float) -> float:
    """Compute nominal cross-sectional area of one bar: Ab = pi * db^2 / 4 (mm^2)."""
    if not math.isfinite(bar_diameter_mm) or bar_diameter_mm <= 0.0:
        raise ValueError(f"bar_diameter_mm must be finite and > 0 mm, got {bar_diameter_mm}.")
    return math.pi * (bar_diameter_mm ** 2) / 4.0


def compute_total_rebar_area_mm2(groups: Sequence[RebarGroup]) -> float:
    """Compute total cross-sectional area: As_total = sum(n_i * Ab_i) (mm^2)."""
    if not groups:
        raise ValueError("groups must be a non-empty sequence of RebarGroup instances.")
    total = 0.0
    for grp in groups:
        if isinstance(grp.bar_count, bool) or not isinstance(grp.bar_count, int) or grp.bar_count <= 0:
            raise ValueError(f"bar_count must be a positive integer, got {grp.bar_count}.")
        total += grp.bar_count * compute_single_bar_area_mm2(grp.bar_diameter_mm)
    return total


def evaluate_rebar_combination(
    groups: Sequence[RebarGroup],
    *,
    target_area_mm2: float = 0.0,
) -> RebarCatalogCandidate:
    """Evaluate the mathematical area of a specific bar combination."""
    if not math.isfinite(target_area_mm2) or target_area_mm2 < 0.0:
        raise ValueError(f"target_area_mm2 must be finite and >= 0 mm^2, got {target_area_mm2}.")
    groups_tuple = tuple(groups)
    total_area = compute_total_rebar_area_mm2(groups_tuple)
    return RebarCatalogCandidate(
        groups=groups_tuple,
        total_area_mm2=total_area,
        target_area_mm2=target_area_mm2,
        excess_area_mm2=total_area - target_area_mm2,
    )


def enumerate_rebar_candidates(
    target_area_mm2: float,
    *,
    allowed_diameters_mm: Sequence[int] = STANDARD_REBAR_DIAMETERS_MM,
    min_bars: int = 2,
    max_bars: int = 8,
    allow_mixed_two_sizes: bool = False,
    max_excess_ratio: Optional[float] = 0.50,
) -> Tuple[RebarCatalogCandidate, ...]:
    """Deterministically enumerate mathematical bar combinations with As_total >= target_area_mm2.

    Every candidate returned has `constructability_verified = False`.
    """
    if not math.isfinite(target_area_mm2) or target_area_mm2 <= 0.0:
        raise ValueError(f"target_area_mm2 must be finite and > 0 mm^2, got {target_area_mm2}.")
    if isinstance(min_bars, bool) or min_bars < 1:
        raise ValueError(f"min_bars must be >= 1, got {min_bars}.")
    if isinstance(max_bars, bool) or max_bars < min_bars:
        raise ValueError(f"max_bars ({max_bars}) must be >= min_bars ({min_bars}).")
    if max_excess_ratio is not None and (
        not math.isfinite(max_excess_ratio) or max_excess_ratio < 0.0
    ):
        raise ValueError(f"max_excess_ratio must be finite and >= 0, got {max_excess_ratio}.")

    sorted_diameters = sorted({int(d) for d in allowed_diameters_mm})
    for d in sorted_diameters:
        if d <= 0:
            raise ValueError(f"Allowed bar diameter must be > 0 mm, got {d}.")

    max_area_mm2 = (
        target_area_mm2 * (1.0 + max_excess_ratio)
        if max_excess_ratio is not None
        else float("inf")
    )

    candidates: List[RebarCatalogCandidate] = []

    # 1. Single-diameter combinations
    for db in sorted_diameters:
        for count in range(min_bars, max_bars + 1):
            grp = RebarGroup(bar_diameter_mm=float(db), bar_count=count)
            area = grp.total_area_mm2
            if target_area_mm2 <= area <= max_area_mm2:
                candidates.append(
                    RebarCatalogCandidate(
                        groups=(grp,),
                        total_area_mm2=area,
                        target_area_mm2=target_area_mm2,
                        excess_area_mm2=area - target_area_mm2,
                    )
                )

    # 2. Optional two-diameter combinations (db1 < db2)
    if allow_mixed_two_sizes:
        for idx1, db1 in enumerate(sorted_diameters):
            for db2 in sorted_diameters[idx1 + 1 :]:
                for count1 in range(1, max_bars):
                    for count2 in range(1, max_bars - count1 + 1):
                        if count1 + count2 < min_bars:
                            continue
                        grp1 = RebarGroup(bar_diameter_mm=float(db1), bar_count=count1)
                        grp2 = RebarGroup(bar_diameter_mm=float(db2), bar_count=count2)
                        area = grp1.total_area_mm2 + grp2.total_area_mm2
                        if target_area_mm2 <= area <= max_area_mm2:
                            candidates.append(
                                RebarCatalogCandidate(
                                    groups=(grp1, grp2),
                                    total_area_mm2=area,
                                    target_area_mm2=target_area_mm2,
                                    excess_area_mm2=area - target_area_mm2,
                                )
                            )

    candidates.sort(
        key=lambda c: (
            round(c.total_area_mm2, 6),
            c.total_bar_count,
            tuple((g.bar_diameter_mm, g.bar_count) for g in c.groups),
        )
    )
    return tuple(candidates)
