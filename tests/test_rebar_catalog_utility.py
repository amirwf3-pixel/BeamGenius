"""Tests for the mathematical rebar catalog utility."""

from __future__ import annotations

import math

import pytest

from beamgenius.domain import RebarGroup
from beamgenius.rebar import (
    RebarCatalogCandidate,
    compute_single_bar_area_mm2,
    compute_total_rebar_area_mm2,
    enumerate_rebar_candidates,
    evaluate_rebar_combination,
)


def test_single_bar_and_total_area_exact_formulas() -> None:
    assert compute_single_bar_area_mm2(20.0) == pytest.approx(math.pi * 100.0, rel=1e-12)
    assert compute_single_bar_area_mm2(25.0) == pytest.approx(math.pi * 625.0 / 4.0, rel=1e-12)
    assert compute_single_bar_area_mm2(30.0) == pytest.approx(math.pi * 900.0 / 4.0, rel=1e-12)

    groups = (
        RebarGroup(bar_diameter_mm=25.0, bar_count=2),
        RebarGroup(bar_diameter_mm=30.0, bar_count=1),
    )
    expected_area = 2.0 * (math.pi * 25.0**2 / 4.0) + 1.0 * (math.pi * 30.0**2 / 4.0)
    assert compute_total_rebar_area_mm2(groups) == pytest.approx(expected_area, rel=1e-12)


def test_rebar_combination_candidate_always_has_constructability_verified_false() -> None:
    cand = evaluate_rebar_combination(
        (
            RebarGroup(bar_diameter_mm=25.0, bar_count=2),
            RebarGroup(bar_diameter_mm=30.0, bar_count=1),
        ),
        target_area_mm2=1636.0,
    )
    assert cand.constructability_verified is False
    assert cand.total_bar_count == 3
    assert cand.label == "2Φ25 + 1Φ30"
    assert round(cand.total_area_mm2) == 1689
    assert cand.excess_area_mm2 == pytest.approx(cand.total_area_mm2 - 1636.0)


def test_enumerate_rebar_candidates_deterministic_and_constructability_unverified() -> None:
    candidates = enumerate_rebar_candidates(
        1636.0,
        allowed_diameters_mm=(25, 28, 30),
        min_bars=2,
        max_bars=4,
        allow_mixed_two_sizes=True,
        max_excess_ratio=0.25,
    )
    assert len(candidates) > 0
    labels = [c.label for c in candidates]
    assert "2Φ25 + 1Φ30" in labels
    assert "3Φ28" in labels

    for idx, cand in enumerate(candidates):
        assert cand.constructability_verified is False
        assert cand.total_area_mm2 >= 1636.0
        if idx > 0:
            assert cand.total_area_mm2 >= candidates[idx - 1].total_area_mm2 - 1e-6


def test_rebar_catalog_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError):
        compute_single_bar_area_mm2(0.0)
    with pytest.raises(ValueError):
        compute_total_rebar_area_mm2(())
    with pytest.raises(ValueError):
        enumerate_rebar_candidates(-100.0)
    with pytest.raises(ValueError):
        enumerate_rebar_candidates(1000.0, min_bars=4, max_bars=2)


def test_aud_03_rebar_catalog_candidate_runtime_tuple_coercion() -> None:
    grp = RebarGroup(bar_diameter_mm=25.0, bar_count=3)
    cand = RebarCatalogCandidate(
        groups=[grp],  # type: ignore[arg-type]
        total_area_mm2=grp.total_area_mm2,
        target_area_mm2=1400.0,
        excess_area_mm2=grp.total_area_mm2 - 1400.0,
    )
    assert isinstance(cand.groups, tuple)
    assert cand.constructability_verified is False


