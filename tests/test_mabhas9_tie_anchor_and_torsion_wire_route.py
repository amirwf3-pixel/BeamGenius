"""Focused tests for the Phase 2F Stage H.7 rules (Mabhas 9, 1399).

Rules under test (all Mabhas 9, 1399 5th ed.; visually re-verified 2026-10-06
from the committed evidence scan phase2f-source-442-472 @ df8067a):

- ``BG-TRANS-TIE-ANCHOR-STD-HOOK-001`` — Clause 9-21-6-1-3-الف
  (PDF p. 463 / Printed p. 443), hook geometry delegated to Table 9-21-2
- ``BG-TRANS-TORSION-TIE-WIRE-ROUTE-001`` — the Clause 9-21-6-1-4 route of
  Clause 9-21-6-1-6-ب (PDF p. 464 / Printed p. 444) and Clause 9-21-6-2-7-ب
  (PDF p. 468 / Printed p. 448), U-tie geometry delegated to
  BG-TRANS-WIRE-TIE-UTIE-001

Stage H.7 source-fidelity note (Clause 9-21-6-1-3, PDF p. 463): the clause has
THREE branches. The branch letters were read at high magnification (ب carries
one dot below, پ carries three):

- (الف) bars/wires with d_b <= 16 mm, AND bars with d_b 18-25 mm with
  f_y < 280 MPa -> standard hook around the longitudinal bar
- (ب)  bars with d_b 18-25 mm and f_y > 280 MPa -> standard hook plus an
  embedment length plus a minimum outer bend diameter
  0.17*f_y/(lambda*sqrt(f'c))*d_b
- (پ)  in joists, bars/wires with d_b <= 12 mm -> standard hook

The f_y < 280 MPa condition attaches to the 18-25 mm sub-condition only, so
d_b <= 16 mm carries no f_y gate. Only branch (الف) is implemented; (ب) and
(پ) remain blocked. Genuine source gaps are asserted to stay BLOCKED — never a
false PASS and never an interpolated boundary.
"""

from __future__ import annotations

import pytest

from beamgenius.domain.enums import EvaluationOutcome, JurisdictionMode
from beamgenius.engine.transverse_reinforcement_mabhas9 import (
    WireTieUtieAlternative,
    evaluate_standard_hook,
    evaluate_tie_anchor_std_hook,
    evaluate_torsion_tie_wire_route,
    evaluate_wire_tie_utie,
)
from beamgenius.registry.catalog import (
    RULE_BG_TRANS_SPIRAL_SPLICE_SEL_PENDING,
    RULE_BG_TRANS_STANDARD_HOOK_001,
    RULE_BG_TRANS_TIE_ANCHOR_PENDING,
    RULE_BG_TRANS_TIE_ANCHOR_STD_HOOK_001,
    RULE_BG_TRANS_TORSION_TIE_PENDING,
    RULE_BG_TRANS_TORSION_TIE_WIRE_ROUTE_001,
    RULE_BG_TRANS_WIRE_SUBST_PENDING,
    RULE_BG_TRANS_WIRE_TIE_PENDING,
    RULE_BG_TRANS_WIRE_TIE_UTIE_001,
    list_all_rules,
    list_blocked_rules,
    list_mabhas9_executable_rules,
)

# --- helpers ---------------------------------------------------------------


def _outcome(step: object) -> EvaluationOutcome:
    return step.outcome  # type: ignore[attr-defined]


def _codes(step: object) -> set[str]:
    return {d.code for d in step.diagnostics}  # type: ignore[attr-defined]


def _tie_anchor(**overrides: object) -> object:
    """A valid Clause 9-21-6-1-3-الف + Table 9-21-2 input set."""
    kwargs: dict[str, object] = {
        "yield_stress_mpa": 300.0,
        "bar_diameter_mm": 12.0,
        "hook_angle_deg": 90.0,
        "inner_bend_diameter_mm": 48.0,
        "straight_extension_mm": 75.0,
        "encloses_longitudinal_bar": True,
    }
    kwargs.update(overrides)
    return evaluate_tie_anchor_std_hook(**kwargs)  # type: ignore[arg-type]


def _wire_route(**overrides: object) -> object:
    """A valid Clause 9-21-6-1-4-الف route input set."""
    kwargs: dict[str, object] = {
        "concrete_around_anchorage_not_liable_to_spall": True,
        "alternative": WireTieUtieAlternative.ALEF,
        "wire_spacing_mm": 50.0,
        "wires_in_upper_part_of_utie": True,
    }
    kwargs.update(overrides)
    return evaluate_torsion_tie_wire_route(**kwargs)  # type: ignore[arg-type]


# --- BG-TRANS-TIE-ANCHOR-STD-HOOK-001: applicability -----------------------


def test_tie_anchor_alef_db_le_16_passes() -> None:
    # Clause 9-21-6-1-3-الف, first sub-condition: d_b <= 16 mm, no f_y gate.
    step = _tie_anchor(bar_diameter_mm=12.0, inner_bend_diameter_mm=48.0,
                       straight_extension_mm=75.0)
    assert _outcome(step) is EvaluationOutcome.PASS


def test_tie_anchor_alef_db_le_16_passes_with_high_fy() -> None:
    # Source-faithful: d_b <= 16 mm carries NO f_y gate, so f_y = 500 MPa is
    # still branch (الف). (Branch (ب) covers only d_b 18-25 mm with f_y > 280.)
    step = _tie_anchor(yield_stress_mpa=500.0, bar_diameter_mm=12.0,
                       inner_bend_diameter_mm=48.0, straight_extension_mm=75.0)
    assert _outcome(step) is EvaluationOutcome.PASS


def test_tie_anchor_alef_db_16_boundary_passes() -> None:
    step = _tie_anchor(bar_diameter_mm=16.0, inner_bend_diameter_mm=64.0,
                       straight_extension_mm=96.0)
    assert _outcome(step) is EvaluationOutcome.PASS


def test_tie_anchor_alef_db_18_25_low_fy_passes() -> None:
    # Second sub-condition: d_b 18-25 mm with f_y < 280 MPa.
    step = _tie_anchor(yield_stress_mpa=250.0, bar_diameter_mm=20.0,
                       hook_angle_deg=135.0, inner_bend_diameter_mm=120.0,
                       straight_extension_mm=240.0)
    assert _outcome(step) is EvaluationOutcome.PASS


def test_tie_anchor_alef_db_25_low_fy_passes() -> None:
    step = _tie_anchor(yield_stress_mpa=250.0, bar_diameter_mm=25.0,
                       hook_angle_deg=135.0, inner_bend_diameter_mm=150.0,
                       straight_extension_mm=300.0)
    assert _outcome(step) is EvaluationOutcome.PASS


def test_tie_anchor_alef_fy_just_below_280_passes() -> None:
    step = _tie_anchor(yield_stress_mpa=279.0, bar_diameter_mm=20.0,
                       hook_angle_deg=135.0, inner_bend_diameter_mm=120.0,
                       straight_extension_mm=240.0)
    assert _outcome(step) is EvaluationOutcome.PASS


# --- BG-TRANS-TIE-ANCHOR-STD-HOOK-001: genuine source gaps ----------------


def test_tie_anchor_fy_280_blocked() -> None:
    # f_y = 280 MPa is in neither (الف) (< 280) nor (ب) (> 280).
    step = _tie_anchor(yield_stress_mpa=280.0, bar_diameter_mm=20.0,
                       hook_angle_deg=135.0, inner_bend_diameter_mm=120.0,
                       straight_extension_mm=240.0)
    assert _outcome(step) is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert "TIE_ANCHOR_FY_280_IN_GAP" in _codes(step)


def test_tie_anchor_fy_280_blocked_even_for_small_db() -> None:
    # The f_y = 280 gap only bites for the 18-25 mm sub-condition; d_b <= 16 mm
    # has no f_y gate, so this case must PASS (guards against over-blocking).
    step = _tie_anchor(yield_stress_mpa=280.0, bar_diameter_mm=12.0,
                       inner_bend_diameter_mm=48.0, straight_extension_mm=75.0)
    assert _outcome(step) is EvaluationOutcome.PASS


def test_tie_anchor_db_17_blocked() -> None:
    step = _tie_anchor(bar_diameter_mm=17.0, inner_bend_diameter_mm=68.0,
                       straight_extension_mm=102.0)
    assert _outcome(step) is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert "TIE_ANCHOR_DB_IN_GAP" in _codes(step)


def test_tie_anchor_db_above_25_blocked() -> None:
    step = _tie_anchor(bar_diameter_mm=28.0, inner_bend_diameter_mm=112.0,
                       straight_extension_mm=168.0)
    assert _outcome(step) is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert "TIE_ANCHOR_DB_ABOVE_TABLE" in _codes(step)


def test_tie_anchor_db_18_25_high_fy_blocked_branch_be() -> None:
    # d_b 18-25 mm with f_y >= 280 MPa belongs to branch (ب), not implemented.
    step = _tie_anchor(yield_stress_mpa=500.0, bar_diameter_mm=20.0,
                       hook_angle_deg=135.0, inner_bend_diameter_mm=120.0,
                       straight_extension_mm=240.0)
    assert _outcome(step) is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert (
        "TIE_ANCHOR_FY_ABOVE_280_B_BRANCH_NOT_IMPLEMENTED" in _codes(step)
    )


def test_tie_anchor_db_below_10_blocked_through_delegate() -> None:
    # d_b < 10 mm is outside Table 9-21-2; BLOCKED via the standard-hook
    # dependency rather than by an invented local rule.
    step = _tie_anchor(bar_diameter_mm=8.0, inner_bend_diameter_mm=32.0,
                       straight_extension_mm=48.0)
    assert _outcome(step) is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert "STANDARD_HOOK_DB_BELOW_TABLE" in _codes(step)


def test_tie_anchor_180_deg_hook_blocked_through_delegate() -> None:
    step = _tie_anchor(hook_angle_deg=180.0, inner_bend_diameter_mm=48.0,
                       straight_extension_mm=65.0)
    assert _outcome(step) is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert "STANDARD_HOOK_180_DEG_NOT_IMPLEMENTED" in _codes(step)


def test_tie_anchor_unsupported_angle_blocked_through_delegate() -> None:
    step = _tie_anchor(hook_angle_deg=120.0)
    assert _outcome(step) is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert "STANDARD_HOOK_ANGLE_NOT_IN_TABLE_9_21_2" in _codes(step)


# --- BG-TRANS-TIE-ANCHOR-STD-HOOK-001: missing / invalid ------------------


def test_tie_anchor_missing_fy_blocked() -> None:
    step = _tie_anchor(yield_stress_mpa=None)
    assert _outcome(step) is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert "MISSING_YIELD_STRESS" in _codes(step)


def test_tie_anchor_missing_db_blocked() -> None:
    step = _tie_anchor(bar_diameter_mm=None)
    assert _outcome(step) is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert "MISSING_BAR_DIAMETER" in _codes(step)


def test_tie_anchor_missing_hook_angle_blocked() -> None:
    # Clause 9-21-6-1-3-الف names no unique angle; it is never assumed.
    step = _tie_anchor(hook_angle_deg=None)
    assert _outcome(step) is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert "MISSING_HOOK_ANGLE" in _codes(step)


@pytest.mark.parametrize(
    "field",
    ["inner_bend_diameter_mm", "straight_extension_mm"],
)
def test_tie_anchor_missing_hook_geometry_blocked(field: str) -> None:
    step = _tie_anchor(**{field: None})
    assert _outcome(step) is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED


def test_tie_anchor_missing_encloses_blocked() -> None:
    step = _tie_anchor(encloses_longitudinal_bar=None)
    assert _outcome(step) is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert "MISSING_ENCLOSES_LONGITUDINAL_BAR" in _codes(step)


def test_tie_anchor_not_enclosing_fails() -> None:
    step = _tie_anchor(encloses_longitudinal_bar=False)
    assert _outcome(step) is EvaluationOutcome.FAIL
    assert "TIE_ANCHOR_STANDARD_HOOK_GEOMETRY_NOT_SATISFIED" in _codes(step)


def test_tie_anchor_invalid_delegated_geometry_fails() -> None:
    step = _tie_anchor(inner_bend_diameter_mm=10.0)
    assert _outcome(step) is EvaluationOutcome.FAIL
    assert "TIE_ANCHOR_STANDARD_HOOK_GEOMETRY_NOT_SATISFIED" in _codes(step)


def test_tie_anchor_malformed_db_invalid_input() -> None:
    step = _tie_anchor(bar_diameter_mm=-5.0)
    assert _outcome(step) is EvaluationOutcome.INVALID_INPUT


def test_tie_anchor_non_bool_encloses_invalid_input() -> None:
    step = _tie_anchor(encloses_longitudinal_bar="yes")  # type: ignore[arg-type]
    assert _outcome(step) is EvaluationOutcome.INVALID_INPUT


def test_tie_anchor_jurisdiction_blocked_under_mostofinejad() -> None:
    step = evaluate_tie_anchor_std_hook(
        yield_stress_mpa=300.0,
        bar_diameter_mm=12.0,
        hook_angle_deg=90.0,
        inner_bend_diameter_mm=48.0,
        straight_extension_mm=75.0,
        encloses_longitudinal_bar=True,
        jurisdiction_mode=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    )
    assert _outcome(step) is EvaluationOutcome.JURISDICTION_BLOCKED


# --- BG-TRANS-TIE-ANCHOR-STD-HOOK-001: delegation -------------------------


def test_tie_anchor_delegation_matches_standard_hook() -> None:
    """The rule must not duplicate Table 9-21-2; it must agree with it."""
    # (f_y, angle, d_b, inner bend, straight extension) — f_y is chosen so the
    # Clause 9-21-6-1-3-الف applicability gate passes, isolating the delegated
    # Table 9-21-2 geometry check.
    for fy, angle, db, inner, ext in [
        (300.0, 90.0, 12.0, 48.0, 75.0),
        (250.0, 135.0, 20.0, 120.0, 240.0),
        (300.0, 90.0, 16.0, 64.0, 96.0),
        (250.0, 135.0, 25.0, 150.0, 300.0),
    ]:
        anchor = evaluate_tie_anchor_std_hook(
            yield_stress_mpa=fy,
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
        assert _outcome(anchor) is _outcome(direct) is EvaluationOutcome.PASS


def test_tie_anchor_delegation_matches_standard_hook_on_failure() -> None:
    anchor = _tie_anchor(inner_bend_diameter_mm=20.0)
    direct = evaluate_standard_hook(
        hook_angle_deg=90.0,
        bar_diameter_mm=12.0,
        inner_bend_diameter_mm=20.0,
        straight_extension_mm=75.0,
        encloses_longitudinal_bar=True,
    )
    assert _outcome(anchor) is _outcome(direct) is EvaluationOutcome.FAIL


# --- BG-TRANS-TORSION-TIE-WIRE-ROUTE-001: route + delegation --------------


def test_wire_route_alef_passes() -> None:
    step = _wire_route()
    assert _outcome(step) is EvaluationOutcome.PASS


def test_wire_route_be_passes() -> None:
    step = _wire_route(
        alternative=WireTieUtieAlternative.BE,
        wire_spacing_mm=None,
        wires_in_upper_part_of_utie=None,
        effective_depth_mm=400.0,
        wire1_dist_from_compression_mm=80.0,
        wire2_dist_from_compression_mm=50.0,
        wire1_to_wire2_spacing_mm=60.0,
        wire2_on_hook=False,
    )
    assert _outcome(step) is EvaluationOutcome.PASS


def test_wire_route_delegation_matches_wire_tie_utie() -> None:
    route = _wire_route()
    direct = evaluate_wire_tie_utie(
        alternative=WireTieUtieAlternative.ALEF,
        wire_spacing_mm=50.0,
        wires_in_upper_part_of_utie=True,
    )
    assert _outcome(route) is _outcome(direct) is EvaluationOutcome.PASS


def test_wire_route_delegation_matches_wire_tie_utie_on_failure() -> None:
    route = _wire_route(wire_spacing_mm=60.0)
    direct = evaluate_wire_tie_utie(
        alternative=WireTieUtieAlternative.ALEF,
        wire_spacing_mm=60.0,
        wires_in_upper_part_of_utie=True,
    )
    assert _outcome(route) is _outcome(direct) is EvaluationOutcome.FAIL


def test_wire_route_invalid_utie_geometry_fails() -> None:
    step = _wire_route(wire_spacing_mm=60.0)
    assert _outcome(step) is EvaluationOutcome.FAIL
    assert "TORSION_TIE_WIRE_ROUTE_GEOMETRY_NOT_SATISFIED" in _codes(step)


def test_wire_route_not_upper_part_fails() -> None:
    step = _wire_route(wires_in_upper_part_of_utie=False)
    assert _outcome(step) is EvaluationOutcome.FAIL


def test_wire_route_missing_alternative_blocked() -> None:
    step = _wire_route(alternative=None, wire_spacing_mm=None,
                       wires_in_upper_part_of_utie=None)
    assert _outcome(step) is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert "MISSING_ALTERNATIVE" in _codes(step)


def test_wire_route_missing_route_data_blocked() -> None:
    step = _wire_route(wire_spacing_mm=None, wires_in_upper_part_of_utie=None)
    assert _outcome(step) is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED


def test_wire_route_missing_precondition_blocked() -> None:
    step = _wire_route(concrete_around_anchorage_not_liable_to_spall=None)
    assert _outcome(step) is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert "MISSING_CONCRETE_NOT_LIABLE_TO_SPALL" in _codes(step)


def test_wire_route_non_bool_precondition_invalid() -> None:
    step = _wire_route(concrete_around_anchorage_not_liable_to_spall="no")
    assert _outcome(step) is EvaluationOutcome.INVALID_INPUT


def test_wire_route_spall_precondition_false_not_applicable() -> None:
    # If the surrounding concrete IS liable to deteriorate, the (ب) route is
    # unavailable and the tie must use the (الف) routes instead.
    step = _wire_route(concrete_around_anchorage_not_liable_to_spall=False)
    assert _outcome(step) is EvaluationOutcome.NOT_APPLICABLE


def test_wire_route_jurisdiction_blocked_under_mostofinejad() -> None:
    step = evaluate_torsion_tie_wire_route(
        concrete_around_anchorage_not_liable_to_spall=True,
        alternative=WireTieUtieAlternative.ALEF,
        wire_spacing_mm=50.0,
        wires_in_upper_part_of_utie=True,
        jurisdiction_mode=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    )
    assert _outcome(step) is EvaluationOutcome.JURISDICTION_BLOCKED


# --- OR semantics: one executable route != whole clause executable ---------


def test_wire_route_does_not_promote_the_913_route() -> None:
    """The Clause 9-21-6-1-3 route of the (ب) branches stays blocked."""
    assert RULE_BG_TRANS_TORSION_TIE_PENDING.execution_allowed is False
    desc = RULE_BG_TRANS_TORSION_TIE_PENDING.description or ""
    reason = RULE_BG_TRANS_TORSION_TIE_PENDING.blocked_reason or ""
    # The 9-21-6-1-4 route is explicitly no longer blocked...
    assert "NO LONGER blocked" in reason
    # ...but the 9-21-6-1-3 route is still retained here.
    assert "9-21-6-1-3 route stays blocked" in reason
    assert "9-21-6-1-3 route stays BLOCKED here" in desc
    # The sentinel must not claim the whole clause is executable.
    assert "does NOT make the whole (ب) clause executable" in desc
    # ...nor may the 9-21-6-1-4 route still be described as blocked.
    assert "9-21-6-1-4 is still blocked" not in (desc + reason)


def test_wire_route_rule_metadata_is_verified_and_executable() -> None:
    rule = RULE_BG_TRANS_TORSION_TIE_WIRE_ROUTE_001
    assert rule.status == "VERIFIED"
    assert str(rule.category).endswith("CODE_RULE")
    assert str(rule.jurisdiction).endswith("MABHAS_9_COMPLIANCE")
    assert rule.execution_allowed is True
    assert rule.blocked_reason is None
    assert rule.pdf_page == 464 and rule.printed_page == 444
    assert "9-21-6-1-4" in rule.clause_or_equation
    assert "9-21-6-1-6-ب" in rule.clause_or_equation
    assert "9-21-6-2-7-ب" in rule.clause_or_equation
    assert rule.dependencies == ("BG-TRANS-WIRE-TIE-UTIE-001",)
    assert rule.description and rule.symbolic_formula


def test_tie_anchor_rule_metadata_is_verified_and_executable() -> None:
    rule = RULE_BG_TRANS_TIE_ANCHOR_STD_HOOK_001
    assert rule.status == "VERIFIED"
    assert str(rule.category).endswith("CODE_RULE")
    assert str(rule.jurisdiction).endswith("MABHAS_9_COMPLIANCE")
    assert rule.execution_allowed is True
    assert rule.blocked_reason is None
    assert rule.pdf_page == 463 and rule.printed_page == 443
    assert "9-21-6-1-3-الف" in rule.clause_or_equation
    assert rule.dependencies == ("BG-TRANS-STANDARD-HOOK-001",)
    assert rule.description and rule.symbolic_formula
    # M4: the erroneous "and 8-25 mm" range wording is gone. (The bare token
    # "8-25" is deliberately NOT asserted absent: "d_b 18-25 mm" legitimately
    # contains it, and the H.7 correction note quotes the old value.)
    assert "and 8-25 mm" not in (rule.description or "")
    assert "d_b <= 16 mm and 8-25 mm" not in (rule.description or "")
    assert "and 8-25 mm" not in (rule.blocked_reason or "")
    assert "bars 8-25 mm with f_y" not in (rule.description or "")
    # The source-faithful ranges are stated explicitly.
    assert "d_b <= 16 mm" in (rule.description or "")
    assert "18-25 mm" in (rule.description or "")


# --- sentinel narrowing ---------------------------------------------------


def test_tie_anchor_pending_narrowed_to_be_only() -> None:
    rule = RULE_BG_TRANS_TIE_ANCHOR_PENDING
    assert rule.execution_allowed is False
    assert rule.status == "VERIFY_PENDING"
    clause = rule.clause_or_equation or ""
    # No longer claims the whole clause.
    assert "Clause 9-21-6-1-3 (Printed" not in clause
    # Only the unimplemented branch remains: branch (ب) needs lambda and an
    # embedment datum. Branch (پ) was promoted by Stage H.8.
    assert "9-21-6-1-3-ب" in clause
    assert "9-21-6-1-3-پ" not in clause
    # M4: the "8-25 mm" wording is gone (specific erroneous phrasing only —
    # "d_b 18-25 mm" legitimately contains the "8-25" substring, and the
    # correction note itself quotes the old value).
    assert "and 8-25 mm" not in (rule.description or "")
    assert "d_b <= 16 mm and 8-25 mm" not in (rule.description or "")
    assert "and 8-25 mm" not in (rule.blocked_reason or "")
    # The promoted branches are named.
    assert "BG-TRANS-TIE-ANCHOR-STD-HOOK-001" in (rule.description or "")
    assert "BG-TRANS-TIE-ANCHOR-JOIST-STD-HOOK-001" in (rule.description or "")
    assert "BG-TRANS-TIE-ANCHOR-JOIST-STD-HOOK-001" in (rule.blocked_reason or "")
    # The corrected source-faithful sub-conditions are stated.
    assert "d_b <= 16 mm" in (rule.description or "")
    assert "d_b 18-25 mm" in (rule.description or "")
    # Genuine gaps still recorded.
    reason = rule.blocked_reason or ""
    assert "f_y = 280 MPa" in reason
    assert "d_b = 17 mm" in reason
    assert "d_b > 25 mm" in reason
    # The joist branch must no longer be described as unimplemented.
    assert "branch (پ) is a deterministic joist case that" not in reason


def test_spiral_splice_sel_pending_pages_corrected_m1() -> None:
    rule = RULE_BG_TRANS_SPIRAL_SPLICE_SEL_PENDING
    # M1: Clause 9-21-6-3-5-الف is on PDF 468 / Printed 448 (469/449 is where
    # Clause 9-21-6-3-5-ب and Table 9-21-7 live).
    assert rule.pdf_page == 468
    assert rule.printed_page == 448
    assert "9-21-6-3-5-الف" in rule.clause_or_equation
    # The blocked dependency is unchanged.
    assert rule.execution_allowed is False
    assert rule.dependencies == ("BG-DEV-SPLICE-WELDED-MECH-PENDING",)
    assert "9-21-4-7" in (rule.blocked_reason or "")


def test_135hook_description_no_longer_says_914_blocked_m2() -> None:
    from beamgenius.registry.catalog import RULE_BG_TRANS_TORSION_TIE_135HOOK_001

    rule = RULE_BG_TRANS_TORSION_TIE_135HOOK_001
    desc = rule.description or ""
    assert "still-blocked Clauses 9-21-6-1-3 and 9-21-6-1-4" not in desc
    assert "9-21-6-1-4 is no longer blocked" in desc
    # Scope unchanged: this rule still implements only the 135-degree hook.
    assert rule.execution_allowed is True
    assert "9-21-6-1-6-الف" in rule.clause_or_equation


def test_dorgir_clause_citation_includes_943_m3() -> None:
    from beamgenius.registry.catalog import RULE_BG_TRANS_DORGIR_001

    rule = RULE_BG_TRANS_DORGIR_001
    clause = rule.clause_or_equation or ""
    assert "9-21-6-4-1" in clause
    assert "9-21-6-4-2" in clause
    assert "9-21-6-4-3" in clause
    assert rule.execution_allowed is True
    assert rule.dependencies == ("BG-TRANS-SEISMIC-HOOK-001",)


# --- all other §9-21-6 sentinels remain blocked --------------------------


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


def test_wire_tie_pending_still_blocks_915_only() -> None:
    rule = RULE_BG_TRANS_WIRE_TIE_PENDING
    assert rule.execution_allowed is False
    assert "9-21-6-1-5" in rule.clause_or_equation
    assert "9-21-6-1-4" not in rule.clause_or_equation


# --- registry integrity ---------------------------------------------------


def test_new_rules_are_registered_and_executable() -> None:
    executable = {r.rule_id for r in list_mabhas9_executable_rules()}
    assert "BG-TRANS-TIE-ANCHOR-STD-HOOK-001" in executable
    assert "BG-TRANS-TORSION-TIE-WIRE_ROUTE-001".replace("_", "-") in executable
    blocked = {r.rule_id for r in list_blocked_rules()}
    assert "BG-TRANS-TIE-ANCHOR-STD-HOOK-001" not in blocked
    assert "BG-TRANS-TORSION-TIE-WIRE-ROUTE-001" not in blocked


def test_registry_counts_and_no_duplicates() -> None:
    all_rules = list_all_rules()
    assert len(all_rules) == 121
    assert len(list_mabhas9_executable_rules()) == 63
    assert len(list_blocked_rules()) == 48
    ids = [r.rule_id for r in all_rules]
    assert len(ids) == len(set(ids))


def test_section_9216_counts() -> None:
    exe = [
        r for r in list_mabhas9_executable_rules()
        if "9-21-6" in (r.clause_or_equation or "")
    ]
    blk = [
        r for r in list_blocked_rules()
        if "9-21-6" in (r.clause_or_equation or "")
    ]
    # 19 §9-21-6 rules + the 2 H.7 anchorage rules + the H.8 joist rule,
    # plus 2 §9-21-3 rules that cite Table 9-21-6 / Eq. (9-21-6-الف/ب).
    assert len(exe) == 23
    assert len(blk) == 5


def test_new_rule_dependencies_are_executable() -> None:
    from beamgenius.registry.catalog import get_rule

    for rid in ("BG-TRANS-TIE-ANCHOR-STD-HOOK-001",
                "BG-TRANS-TORSION-TIE-WIRE-ROUTE-001"):
        rule = get_rule(rid)
        assert rule is not None
        for dep in rule.dependencies:
            dep_rule = get_rule(dep)
            assert dep_rule is not None
            assert dep_rule.execution_allowed is True, dep


def test_no_duplicate_rule_ids_across_registry() -> None:
    ids = [r.rule_id for r in list_all_rules()]
    seen: set[str] = set()
    for rid in ids:
        assert rid not in seen, rid
        seen.add(rid)
