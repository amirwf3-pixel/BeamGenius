"""Focused tests for the Phase 2F Stage H.8 joist tie standard-hook rule.

Rule under test (Mabhas 9, 1399 5th ed.; visually re-verified 2026-10-06 from
the committed evidence scan phase2f-source-442-472 @ df8067a, page 463 /
printed page 443):

- ``BG-TRANS-TIE-ANCHOR-JOIST-STD-HOOK-001`` — Clause 9-21-6-1-3-پ
  (PDF p. 463 / Printed p. 443), hook geometry delegated to
  BG-TRANS-STANDARD-HOOK-001

Verbatim source read of Clause 9-21-6-1-3 (PDF p. 463), which has THREE
branches. The branch-marker glyphs were cropped at >=10x magnification and
their sub-bowl dots counted (ب carries one dot, پ carries three):

    «مهار میلگرد و سیم آجدار در خاموت باید منطبق بر شرایط زیر باشد:»
    (Alef) bars/wires with d_b <= 16 mm, AND bars with d_b 18-25 mm with
           f_y < 280 MPa -> standard hook around the longitudinal bar.
    (ب)   bars with d_b 18-25 mm and f_y > 280 MPa -> standard hook plus an
           embedment length plus a minimum outer bend diameter
           0.17*f_y/(lambda*sqrt(f'c))*d_b.
    (پ)   «در تیرچه‌ها، برای میلگردها یا سیم‌های با قطر کوچکتر یا مساوی ۱۲
           میلی‌متر، وجوب قلاب استاندارد.»
           In joists (تیرچه‌ها), bars/wires with d_b <= 12 mm -> standard hook.

Branch (پ) is fully deterministic: joist context AND d_b <= 12 mm, with no
f_y condition, no embedment length and no bend-diameter formula. Branch (ب)
remains blocked (lambda undefined in §9-21-6, positional embedment datum) and
branch (الف) behaviour is unchanged by this stage.
"""

from __future__ import annotations

import pytest

from beamgenius.domain.enums import EvaluationOutcome, JurisdictionMode
from beamgenius.engine.transverse_reinforcement_mabhas9 import (
    evaluate_standard_hook,
    evaluate_tie_anchor_joist_std_hook,
    evaluate_tie_anchor_std_hook,
)
from beamgenius.registry.catalog import (
    RULE_BG_TRANS_TIE_ANCHOR_JOIST_STD_HOOK_001,
    RULE_BG_TRANS_TIE_ANCHOR_PENDING,
    RULE_BG_TRANS_TIE_ANCHOR_STD_HOOK_001,
    RULE_BG_TRANS_TORSION_TIE_PENDING,
    RULE_BG_TRANS_WIRE_SUBST_PENDING,
    RULE_BG_TRANS_WIRE_TIE_PENDING,
    RULE_BG_TRANS_SPIRAL_SPLICE_SEL_PENDING,
    get_rule,
    list_all_rules,
    list_blocked_rules,
    list_mabhas9_executable_rules,
)


# --- helpers ---------------------------------------------------------------


def _outcome(step: object) -> EvaluationOutcome:
    return step.outcome  # type: ignore[attr-defined]


def _codes(step: object) -> set[str]:
    return {d.code for d in step.diagnostics}  # type: ignore[attr-defined]


def _joist(**overrides: object) -> object:
    """A valid Clause 9-21-6-1-3-پ + Table 9-21-2 input set."""
    kwargs: dict[str, object] = {
        "in_joist": True,
        "bar_diameter_mm": 10.0,
        "hook_angle_deg": 90.0,
        "inner_bend_diameter_mm": 40.0,
        "straight_extension_mm": 75.0,
        "encloses_longitudinal_bar": True,
    }
    kwargs.update(overrides)
    return evaluate_tie_anchor_joist_std_hook(**kwargs)  # type: ignore[arg-type]


# --- applicability: joist context ----------------------------------------


def test_joist_valid_applicable_case_passes() -> None:
    step = _joist()
    assert _outcome(step) is EvaluationOutcome.PASS


def test_joist_db_exactly_12_boundary_passes() -> None:
    # d_b <= 12 mm is printed; 12 mm itself is included.
    step = _joist(bar_diameter_mm=12.0, inner_bend_diameter_mm=48.0,
                  straight_extension_mm=75.0)
    assert _outcome(step) is EvaluationOutcome.PASS


def test_joist_db_10_passes() -> None:
    step = _joist(bar_diameter_mm=10.0, inner_bend_diameter_mm=40.0,
                  straight_extension_mm=75.0)
    assert _outcome(step) is EvaluationOutcome.PASS


def test_joist_db_just_above_boundary_is_blocked() -> None:
    # 12.5 mm is above the printed 12 mm joist limit -> BLOCKED, never
    # interpolated and never silently falling back to another branch.
    step = _joist(bar_diameter_mm=12.5, inner_bend_diameter_mm=50.0,
                  straight_extension_mm=75.0)
    assert _outcome(step) is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert "TIE_ANCHOR_JOIST_DB_ABOVE_LIMIT" in _codes(step)


def test_joist_db_16_is_blocked() -> None:
    step = _joist(bar_diameter_mm=16.0, inner_bend_diameter_mm=64.0,
                  straight_extension_mm=96.0)
    assert _outcome(step) is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert "TIE_ANCHOR_JOIST_DB_ABOVE_LIMIT" in _codes(step)


def test_joist_db_20_is_blocked() -> None:
    step = _joist(bar_diameter_mm=20.0, hook_angle_deg=135.0,
                  inner_bend_diameter_mm=120.0, straight_extension_mm=240.0)
    assert _outcome(step) is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert "TIE_ANCHOR_JOIST_DB_ABOVE_LIMIT" in _codes(step)


def test_joist_db_above_table_is_blocked() -> None:
    step = _joist(bar_diameter_mm=30.0, inner_bend_diameter_mm=120.0,
                  straight_extension_mm=180.0)
    assert _outcome(step) is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert "TIE_ANCHOR_JOIST_DB_ABOVE_LIMIT" in _codes(step)


def test_non_joist_member_is_not_applicable() -> None:
    # Branch (پ) simply does not govern a non-joist member; the anchorage
    # follows branch (الف) or (ب) instead. Same context precedent as
    # BG-TRANS-TORSION-TIE-WIRE-ROUTE-001.
    step = _joist(in_joist=False)
    assert _outcome(step) is EvaluationOutcome.NOT_APPLICABLE


def test_joist_context_is_not_assumed() -> None:
    step = _joist(in_joist=None)
    assert _outcome(step) is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert "MISSING_IN_JOIST" in _codes(step)


def test_non_bool_in_joist_is_invalid_input() -> None:
    step = _joist(in_joist="yes")  # type: ignore[arg-type]
    assert _outcome(step) is EvaluationOutcome.INVALID_INPUT
    assert "INVALID_IN_JOIST" in _codes(step)


# --- missing required inputs -> BLOCKED -----------------------------------


@pytest.mark.parametrize(
    "field",
    ["bar_diameter_mm", "hook_angle_deg", "inner_bend_diameter_mm",
     "straight_extension_mm"],
)
def test_joist_missing_required_input_is_blocked(field: str) -> None:
    step = _joist(**{field: None})
    assert _outcome(step) is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED


def test_joist_missing_enclosure_is_blocked() -> None:
    step = _joist(encloses_longitudinal_bar=None)
    assert _outcome(step) is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert "MISSING_ENCLOSES_LONGITUDINAL_BAR" in _codes(step)


def test_joist_missing_angle_code() -> None:
    step = _joist(hook_angle_deg=None)
    assert _outcome(step) is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert "MISSING_HOOK_ANGLE" in _codes(step)


def test_joist_malformed_bar_diameter_is_invalid_input() -> None:
    step = _joist(bar_diameter_mm=-5.0)
    assert _outcome(step) is EvaluationOutcome.INVALID_INPUT


def test_joist_non_bool_enclosure_is_invalid_input() -> None:
    step = _joist(encloses_longitudinal_bar="yes")  # type: ignore[arg-type]
    assert _outcome(step) is EvaluationOutcome.INVALID_INPUT


# --- delegation to BG-TRANS-STANDARD-HOOK-001 -----------------------------


def test_joist_delegation_matches_standard_hook() -> None:
    """Geometry is not duplicated; the outcomes must agree with the delegate."""
    for angle, db, inner, ext in [
        (90.0, 10.0, 40.0, 75.0),
        (90.0, 12.0, 48.0, 75.0),
        (135.0, 12.0, 72.0, 144.0),
    ]:
        joist = evaluate_tie_anchor_joist_std_hook(
            in_joist=True,
            bar_diameter_mm=db,
            hook_angle_deg=angle,
            inner_bend_diameter_mm=inner,
            straight_extension_mm=ext,
            encloses_longitudinal_bar=True,
        )
        direct = evaluate_standard_hook(
            hook_angle_deg=angle,
            bar_diameter_mm=db,
            inner_bend_diameter_mm=inner,
            straight_extension_mm=ext,
            encloses_longitudinal_bar=True,
        )
        assert _outcome(joist) is _outcome(direct) is EvaluationOutcome.PASS


def test_joist_delegation_matches_standard_hook_on_failure() -> None:
    joist = _joist(inner_bend_diameter_mm=10.0)
    direct = evaluate_standard_hook(
        hook_angle_deg=90.0,
        bar_diameter_mm=10.0,
        inner_bend_diameter_mm=10.0,
        straight_extension_mm=75.0,
        encloses_longitudinal_bar=True,
    )
    assert _outcome(joist) is _outcome(direct) is EvaluationOutcome.FAIL
    assert (
        "TIE_ANCHOR_JOIST_STANDARD_HOOK_GEOMETRY_NOT_SATISFIED" in _codes(joist)
    )


def test_joist_invalid_delegated_geometry_fails() -> None:
    step = _joist(inner_bend_diameter_mm=10.0)
    assert _outcome(step) is EvaluationOutcome.FAIL


def test_joist_not_enclosing_longitudinal_bar_fails() -> None:
    step = _joist(encloses_longitudinal_bar=False)
    assert _outcome(step) is EvaluationOutcome.FAIL


def test_joist_180_degree_hook_blocked_through_delegate() -> None:
    step = _joist(hook_angle_deg=180.0, inner_bend_diameter_mm=40.0,
                  straight_extension_mm=60.0)
    assert _outcome(step) is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert "STANDARD_HOOK_180_DEG_NOT_IMPLEMENTED" in _codes(step)


def test_joist_unsupported_angle_blocked_through_delegate() -> None:
    step = _joist(hook_angle_deg=120.0)
    assert _outcome(step) is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert "STANDARD_HOOK_ANGLE_NOT_IN_TABLE_9_21_2" in _codes(step)


def test_joist_db_below_table_blocked_through_delegate() -> None:
    # d_b < 10 mm is outside Table 9-21-2; BLOCKED via the standard-hook
    # dependency rather than by an invented local rule.
    step = _joist(bar_diameter_mm=8.0, inner_bend_diameter_mm=32.0,
                  straight_extension_mm=48.0)
    assert _outcome(step) is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert "STANDARD_HOOK_DB_BELOW_TABLE" in _codes(step)


def test_joist_rule_does_not_require_yield_stress() -> None:
    """Branch (پ) carries no f_y condition, so no f_y input may be invented."""
    import inspect

    params = inspect.signature(evaluate_tie_anchor_joist_std_hook).parameters
    assert "yield_stress_mpa" not in params
    # The rule still works with no f_y supplied at all.
    step = _joist()
    assert _outcome(step) is EvaluationOutcome.PASS


def test_joist_jurisdiction_blocked_under_mostofinejad() -> None:
    step = evaluate_tie_anchor_joist_std_hook(
        in_joist=True,
        bar_diameter_mm=10.0,
        hook_angle_deg=90.0,
        inner_bend_diameter_mm=40.0,
        straight_extension_mm=75.0,
        encloses_longitudinal_bar=True,
        jurisdiction_mode=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    )
    assert _outcome(step) is EvaluationOutcome.JURISDICTION_BLOCKED


# --- branch (الف) behaviour is unchanged ----------------------------------


def test_branch_alef_small_db_still_passes_with_high_fy() -> None:
    # d_b <= 16 mm carries NO f_y gate (H.7 source-faithful ruling).
    step = evaluate_tie_anchor_std_hook(
        yield_stress_mpa=500.0,
        bar_diameter_mm=12.0,
        hook_angle_deg=90.0,
        inner_bend_diameter_mm=48.0,
        straight_extension_mm=75.0,
        encloses_longitudinal_bar=True,
    )
    assert _outcome(step) is EvaluationOutcome.PASS


def test_branch_alef_18_25_low_fy_still_passes() -> None:
    step = evaluate_tie_anchor_std_hook(
        yield_stress_mpa=250.0,
        bar_diameter_mm=20.0,
        hook_angle_deg=135.0,
        inner_bend_diameter_mm=120.0,
        straight_extension_mm=240.0,
        encloses_longitudinal_bar=True,
    )
    assert _outcome(step) is EvaluationOutcome.PASS


def test_branch_alef_fy_280_still_blocked() -> None:
    step = evaluate_tie_anchor_std_hook(
        yield_stress_mpa=280.0,
        bar_diameter_mm=20.0,
        hook_angle_deg=135.0,
        inner_bend_diameter_mm=120.0,
        straight_extension_mm=240.0,
        encloses_longitudinal_bar=True,
    )
    assert _outcome(step) is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert "TIE_ANCHOR_FY_280_IN_GAP" in _codes(step)


def test_branch_alef_db_17_still_blocked() -> None:
    step = evaluate_tie_anchor_std_hook(
        yield_stress_mpa=300.0,
        bar_diameter_mm=17.0,
        hook_angle_deg=90.0,
        inner_bend_diameter_mm=68.0,
        straight_extension_mm=102.0,
        encloses_longitudinal_bar=True,
    )
    assert _outcome(step) is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert "TIE_ANCHOR_DB_IN_GAP" in _codes(step)


def test_branch_alef_db_above_25_still_blocked() -> None:
    step = evaluate_tie_anchor_std_hook(
        yield_stress_mpa=300.0,
        bar_diameter_mm=28.0,
        hook_angle_deg=90.0,
        inner_bend_diameter_mm=112.0,
        straight_extension_mm=168.0,
        encloses_longitudinal_bar=True,
    )
    assert _outcome(step) is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert "TIE_ANCHOR_DB_ABOVE_TABLE" in _codes(step)


# --- branch (ب) remains BLOCKED -------------------------------------------


def test_branch_be_remains_blocked() -> None:
    """d_b 18-25 mm with f_y >= 280 MPa belongs to the unimplemented (ب)."""
    for fy in (281.0, 300.0, 500.0):
        step = evaluate_tie_anchor_std_hook(
            yield_stress_mpa=fy,
            bar_diameter_mm=20.0,
            hook_angle_deg=135.0,
            inner_bend_diameter_mm=120.0,
            straight_extension_mm=240.0,
            encloses_longitudinal_bar=True,
        )
        assert _outcome(step) is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
        assert (
            "TIE_ANCHOR_FY_ABOVE_280_B_BRANCH_NOT_IMPLEMENTED" in _codes(step)
        )


def test_branch_be_not_reachable_through_the_joist_rule() -> None:
    # A joist with a large bar is NOT silently routed into branch (ب) either.
    step = _joist(bar_diameter_mm=20.0, hook_angle_deg=135.0,
                  inner_bend_diameter_mm=120.0, straight_extension_mm=240.0)
    assert _outcome(step) is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert "TIE_ANCHOR_JOIST_DB_ABOVE_LIMIT" in _codes(step)


def test_tie_anchor_sentinel_keeps_only_branch_be() -> None:
    rule = RULE_BG_TRANS_TIE_ANCHOR_PENDING
    assert rule.execution_allowed is False
    assert rule.status == "VERIFY_PENDING"
    clause = rule.clause_or_equation or ""
    # Narrowed from "ب & پ" (H.7) to ب only (H.8).
    assert "9-21-6-1-3-ب" in clause
    assert "9-21-6-1-3-پ" not in clause
    desc = rule.description or ""
    reason = rule.blocked_reason or ""
    # Both promoted branches are named, so the sentinel no longer claims them.
    assert "BG-TRANS-TIE-ANCHOR-STD-HOOK-001" in desc
    assert "BG-TRANS-TIE-ANCHOR-JOIST-STD-HOOK-001" in desc
    assert "BG-TRANS-TIE-ANCHOR-JOIST-STD-HOOK-001" in reason
    # The joist branch is no longer described as unimplemented.
    assert "branch (پ) is a deterministic joist case that" not in reason
    # The genuine gaps are still recorded.
    assert "f_y = 280 MPa" in reason
    assert "d_b = 17 mm" in reason
    assert "d_b > 25 mm" in reason


def test_torsion_tie_sentinel_still_blocked_and_updated() -> None:
    rule = RULE_BG_TRANS_TORSION_TIE_PENDING
    assert rule.execution_allowed is False
    assert rule.status == "VERIFY_PENDING"
    reason = rule.blocked_reason or ""
    desc = rule.description or ""
    # The 9-21-6-1-4 route is no longer blocked...
    assert "NO LONGER blocked" in reason
    # ...but the 9-21-6-1-3 route (branch ب + boundary gaps) stays blocked.
    assert "9-21-6-1-3 route stays blocked" in reason
    # Branches (الف) and (پ) are now executable; branch (ب) is not.
    assert "BG-TRANS-TIE-ANCHOR-JOIST-STD-HOOK-001" in desc
    assert "BG-TRANS-TIE-ANCHOR-JOIST-STD-HOOK-001" in reason
    # The whole (ب) clause must not be claimed executable.
    assert "does NOT make the whole (ب) clause executable" in desc


# --- other §9-21-6 sentinels remain blocked -------------------------------


def test_other_sentinels_remain_blocked() -> None:
    for rule in (
        RULE_BG_TRANS_TIE_ANCHOR_PENDING,
        RULE_BG_TRANS_TORSION_TIE_PENDING,
        RULE_BG_TRANS_WIRE_TIE_PENDING,
        RULE_BG_TRANS_WIRE_SUBST_PENDING,
        RULE_BG_TRANS_SPIRAL_SPLICE_SEL_PENDING,
    ):
        assert rule.execution_allowed is False, rule.rule_id
        assert rule.status == "VERIFY_PENDING", rule.rule_id
        assert rule.blocked_reason, rule.rule_id


# --- registry integrity ---------------------------------------------------


def test_joist_rule_metadata_is_verified_and_executable() -> None:
    rule = RULE_BG_TRANS_TIE_ANCHOR_JOIST_STD_HOOK_001
    assert rule.rule_id == "BG-TRANS-TIE-ANCHOR-JOIST-STD-HOOK-001"
    assert rule.status == "VERIFIED"
    assert str(rule.category).endswith("CODE_RULE")
    assert str(rule.jurisdiction).endswith("MABHAS_9_COMPLIANCE")
    assert rule.execution_allowed is True
    assert rule.blocked_reason is None
    assert rule.pdf_page == 463 and rule.printed_page == 443
    assert "9-21-6-1-3-پ" in rule.clause_or_equation
    assert rule.dependencies == ("BG-TRANS-STANDARD-HOOK-001",)
    assert rule.description and rule.symbolic_formula
    # Requirement + applicability + input semantics are all present.
    d = rule.description
    assert "Applicability:" in d
    assert "Required Inputs:" in d
    assert "BLOCKED" in d
    # The source term تیرچه / joist is preserved.
    assert "joist" in d.lower()


def test_joist_rule_is_registered_and_executable() -> None:
    executable = {r.rule_id for r in list_mabhas9_executable_rules()}
    blocked = {r.rule_id for r in list_blocked_rules()}
    assert "BG-TRANS-TIE-ANCHOR-JOIST-STD-HOOK-001" in executable
    assert "BG-TRANS-TIE-ANCHOR-JOIST-STD-HOOK-001" not in blocked
    assert "BG-TRANS-TIE-ANCHOR-PENDING" in blocked


def test_registry_counts_and_no_duplicates() -> None:
    all_rules = list_all_rules()
    assert len(all_rules) == 121
    assert len(list_mabhas9_executable_rules()) == 63
    assert len(list_blocked_rules()) == 48
    ids = [r.rule_id for r in all_rules]
    assert len(ids) == len(set(ids))


def _governs_section_9216(rule: object) -> bool:
    """True when the rule's governing clause is a 9-21-6 clause.

    A raw substring match is not usable here: two §9-21-3 rules cite
    "Table 9-21-6" and "Eq. (9-21-6-...)" inside their clause strings.
    """
    clause = rule.clause_or_equation or ""  # type: ignore[attr-defined]
    return clause.startswith("Clause 9-21-6") or clause.startswith("Clauses 9-21-6")


def test_section_9216_counts() -> None:
    exe = [r for r in list_mabhas9_executable_rules() if _governs_section_9216(r)]
    blk = [r for r in list_blocked_rules() if _governs_section_9216(r)]
    # 19 base §9-21-6 rules + BG-TRANS-TIE-ANCHOR-STD-HOOK-001 (H.7) +
    # BG-TRANS-TIE-ANCHOR-JOIST-STD-HOOK-001 (H.8).
    assert len(exe) == 21
    # Tie-anchorage (branch ب only), wire-tie, torsion-tie, wire-substitution,
    # spiral-splice-selection.
    assert len(blk) == 5
    blocked_ids = {r.rule_id for r in blk}
    assert blocked_ids == {
        "BG-TRANS-TIE-ANCHOR-PENDING",
        "BG-TRANS-WIRE-TIE-PENDING",
        "BG-TRANS-TORSION-TIE-PENDING",
        "BG-TRANS-WIRE-SUBST-PENDING",
        "BG-TRANS-SPIRAL-SPLICE-SEL-PENDING",
    }
    # Nothing else was promoted by this stage.
    assert "BG-TRANS-TIE-ANCHOR-JOIST-STD-HOOK-001" not in blocked_ids


def test_joist_rule_dependency_is_executable() -> None:
    dep = get_rule("BG-TRANS-STANDARD-HOOK-001")
    assert dep is not None
    assert dep.execution_allowed is True
    assert dep.status == "VERIFIED"


def test_joist_rule_is_separate_from_alef_rule() -> None:
    """Different applicability -> different rules; never merged."""
    assert (
        RULE_BG_TRANS_TIE_ANCHOR_JOIST_STD_HOOK_001.rule_id
        != RULE_BG_TRANS_TIE_ANCHOR_STD_HOOK_001.rule_id
    )
    assert (
        RULE_BG_TRANS_TIE_ANCHOR_JOIST_STD_HOOK_001.clause_or_equation
        != RULE_BG_TRANS_TIE_ANCHOR_STD_HOOK_001.clause_or_equation
    )
    # The Alef rule still requires f_y; the joist rule does not.
    assert "f_y" in (RULE_BG_TRANS_TIE_ANCHOR_STD_HOOK_001.description or "")
    assert (
        "yield_stress_mpa is deliberately not an input"
        in (RULE_BG_TRANS_TIE_ANCHOR_JOIST_STD_HOOK_001.description or "")
    )
