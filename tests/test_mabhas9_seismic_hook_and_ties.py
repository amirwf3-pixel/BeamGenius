"""Focused tests for the Phase 2F Stage H.3 verified hook / دورگیر / tie rules.

Rules under test (all Mabhas 9, 1399 5th ed.; visually re-verified 2026-10-06
from the committed evidence scan phase2f-source-442-472 @ df8067a):

- ``BG-TRANS-SEISMIC-HOOK-001`` — Clause 9-21-2-2-4 (PDF p. 442 / Printed p. 442)
- ``BG-TRANS-DORGIR-001`` — Clauses 9-21-6-4-1 & 9-21-6-4-2 (PDF p. 470 / Printed p. 450)
- ``BG-TRANS-TWO-PIECE-TIE-001`` — Clause 9-21-6-1-7 (PDF p. 465 / Printed p. 445)
- ``BG-TRANS-TORSION-TIE-135HOOK-001`` — Clause 9-21-6-1-6-الف (PDF p. 464 / Printed p. 444)
- ``BG-TRANS-TORSION-TIE-SEISMIC-HOOK-001`` — Clause 9-21-6-2-7-الف seismic option
  (PDF p. 467 / Printed p. 447), hook geometry per Clause 9-21-2-2-4 (PDF p. 442)

Every expected outcome was hand-checked against the visually verified source
text; OCR was never used as authority. The still-blocked delegated branches
(Clause 9-21-6-1-6-ب, Clause 9-21-6-2-7-ب, and the Clause 9-21-6-2-7-الف standard
135-degree hook option) are asserted to remain non-executable.
"""

from __future__ import annotations

import pytest

from beamgenius.domain.enums import EvaluationOutcome, JurisdictionMode
from beamgenius.engine.transverse_reinforcement_mabhas9 import (
    DorgirConstruction,
    evaluate_dorgir,
    evaluate_seismic_hook,
    evaluate_torsion_tie_135hook,
    evaluate_torsion_tie_seismic_hook,
    evaluate_two_piece_tie,
)
from beamgenius.registry.catalog import (
    RULE_BG_TRANS_DORGIR_001,
    RULE_BG_TRANS_SEISMIC_HOOK_001,
    RULE_BG_TRANS_TORSION_TIE_135HOOK_001,
    RULE_BG_TRANS_TORSION_TIE_PENDING,
    RULE_BG_TRANS_TORSION_TIE_SEISMIC_HOOK_001,
    RULE_BG_TRANS_TWO_PIECE_TIE_001,
    RULE_BG_TRANS_WIRE_SUBST_PENDING,
    RULE_BG_TRANS_WIRE_TIE_PENDING,
    get_rule,
    list_blocked_rules,
    list_mabhas9_executable_rules,
)
from beamgenius.registry.gatekeeper import evaluate_rule_gate

MOST = JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY

NEW_EXECUTABLE_RULES = (
    RULE_BG_TRANS_SEISMIC_HOOK_001,
    RULE_BG_TRANS_DORGIR_001,
    RULE_BG_TRANS_TWO_PIECE_TIE_001,
    RULE_BG_TRANS_TORSION_TIE_135HOOK_001,
    RULE_BG_TRANS_TORSION_TIE_SEISMIC_HOOK_001,
)

# Branches that must STAY blocked after Stage H.3.
STILL_BLOCKED_SENTINELS = (
    RULE_BG_TRANS_TORSION_TIE_PENDING,
    RULE_BG_TRANS_WIRE_TIE_PENDING,
    RULE_BG_TRANS_WIRE_SUBST_PENDING,
)


# ============================================================================
# Registry / gatekeeper integration & false-PASS prevention
# ============================================================================

@pytest.mark.parametrize("rule", NEW_EXECUTABLE_RULES, ids=lambda r: r.rule_id)
def test_new_rules_are_verified_code_rules_allowed_in_mabhas(rule) -> None:
    assert rule.status.value == "VERIFIED"
    assert rule.category.value == "CODE_RULE"
    assert rule.jurisdiction is JurisdictionMode.MABHAS_9_COMPLIANCE
    assert rule.execution_allowed is True
    assert rule.pdf_page is not None and rule.printed_page is not None
    assert rule.blocked_reason is None

    dec = evaluate_rule_gate(
        rule.rule_id, active_jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE
    )
    assert dec.allowed
    # Blocked under the reference (Mostofinejad) jurisdiction -> never a false PASS.
    dec_most = evaluate_rule_gate(rule.rule_id, active_jurisdiction=MOST)
    assert not dec_most.allowed
    assert dec_most.blocked_outcome == EvaluationOutcome.JURISDICTION_BLOCKED


def test_dependent_rules_depend_on_seismic_hook() -> None:
    assert RULE_BG_TRANS_DORGIR_001.dependencies == ("BG-TRANS-SEISMIC-HOOK-001",)
    assert (
        RULE_BG_TRANS_TORSION_TIE_SEISMIC_HOOK_001.dependencies
        == ("BG-TRANS-SEISMIC-HOOK-001",)
    )
    # The dependency is itself executable, so both rules are gate-allowed.
    ex = {r.rule_id for r in list_mabhas9_executable_rules()}
    assert "BG-TRANS-SEISMIC-HOOK-001" in ex
    assert evaluate_rule_gate("BG-TRANS-DORGIR-001").allowed
    assert evaluate_rule_gate("BG-TRANS-TORSION-TIE-SEISMIC-HOOK-001").allowed


def test_dorgir_pending_sentinel_removed() -> None:
    # The combined DORGIR pending sentinel is fully replaced by the executable rule.
    assert get_rule("BG-TRANS-DORGIR-PENDING") is None
    assert get_rule("BG-TRANS-DORGIR-001") is not None


@pytest.mark.parametrize("rule", STILL_BLOCKED_SENTINELS, ids=lambda r: r.rule_id)
def test_delegated_blocked_branches_remain_blocked(rule) -> None:
    for mode in JurisdictionMode:
        dec = evaluate_rule_gate(rule.rule_id, active_jurisdiction=mode)
        assert not dec.allowed
        assert dec.blocked_outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert rule.execution_allowed is False
    assert rule.status.value == "VERIFY_PENDING"
    assert rule.blocked_reason is not None and len(rule.blocked_reason) > 0
    assert rule.rule_id in {r.rule_id for r in list_blocked_rules()}


def test_no_standard_hook_rule_was_implemented() -> None:
    # The Clause 9-21-6-2-7-الف standard 135-degree hook option (Table 9-21-2-2)
    # must remain non-executable: no executable rule implements it, and the
    # narrowed torsion-tie sentinel still carries it as blocked.
    executable_ids = {r.rule_id for r in list_mabhas9_executable_rules()}
    assert not any("STANDARD" in rid for rid in executable_ids)
    assert "Table 9-21-2-2" in (RULE_BG_TRANS_TORSION_TIE_PENDING.description or "")


# ============================================================================
# BG-TRANS-SEISMIC-HOOK-001 — Clause 9-21-2-2-4
# ============================================================================

def test_seismic_hook_135_bend_passes() -> None:
    step = evaluate_seismic_hook(
        circular_dorgir=False,
        bend_angle_deg=135.0,
        straight_extension_mm=120.0,  # >= 6*20 = 120
        bar_diameter_mm=20.0,
    )
    assert step.outcome is EvaluationOutcome.PASS
    assert step.rule_id == "BG-TRANS-SEISMIC-HOOK-001"


def test_seismic_hook_bend_below_135_fails() -> None:
    step = evaluate_seismic_hook(
        circular_dorgir=False,
        bend_angle_deg=134.0,
        straight_extension_mm=120.0,
        bar_diameter_mm=20.0,
    )
    assert step.outcome is EvaluationOutcome.FAIL
    assert step.diagnostics[0].code == "SEISMIC_HOOK_BEND_BELOW_MINIMUM"


def test_seismic_hook_extension_satisfies_6db_passes() -> None:
    step = evaluate_seismic_hook(
        circular_dorgir=False,
        bend_angle_deg=135.0,
        straight_extension_mm=60.0,  # == 6*10
        bar_diameter_mm=10.0,
    )
    assert step.outcome is EvaluationOutcome.PASS


def test_seismic_hook_extension_satisfies_75mm_passes() -> None:
    step = evaluate_seismic_hook(
        circular_dorgir=False,
        bend_angle_deg=135.0,
        straight_extension_mm=75.0,  # >= 75 (and 6*10 = 60)
        bar_diameter_mm=10.0,
    )
    assert step.outcome is EvaluationOutcome.PASS


def test_seismic_hook_extension_satisfies_neither_fails() -> None:
    step = evaluate_seismic_hook(
        circular_dorgir=False,
        bend_angle_deg=135.0,
        straight_extension_mm=50.0,  # < 6*20 = 120 and < 75
        bar_diameter_mm=20.0,
    )
    assert step.outcome is EvaluationOutcome.FAIL
    assert step.diagnostics[0].code == "SEISMIC_HOOK_EXTENSION_BELOW_MINIMUM"


def test_seismic_hook_circular_90_exception_passes() -> None:
    step = evaluate_seismic_hook(
        circular_dorgir=True,
        bend_angle_deg=90.0,
        straight_extension_mm=120.0,
        bar_diameter_mm=20.0,
    )
    assert step.outcome is EvaluationOutcome.PASS


def test_seismic_hook_circular_below_90_fails() -> None:
    step = evaluate_seismic_hook(
        circular_dorgir=True,
        bend_angle_deg=89.0,
        straight_extension_mm=120.0,
        bar_diameter_mm=20.0,
    )
    assert step.outcome is EvaluationOutcome.FAIL
    assert step.diagnostics[0].code == "SEISMIC_HOOK_BEND_BELOW_MINIMUM"


def test_seismic_hook_missing_inputs_blocked_never_pass() -> None:
    assert evaluate_seismic_hook().outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    # circular classification missing (never defaulted) -> BLOCKED
    assert (
        evaluate_seismic_hook(
            bend_angle_deg=135.0,
            straight_extension_mm=120.0,
            bar_diameter_mm=20.0,
        ).outcome
        is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    )


def test_seismic_hook_invalid_inputs() -> None:
    assert (
        evaluate_seismic_hook(
            circular_dorgir=False,
            bend_angle_deg=-5.0,
            straight_extension_mm=120.0,
            bar_diameter_mm=20.0,
        ).outcome
        is EvaluationOutcome.INVALID_INPUT
    )
    # bend angle beyond a physical bend -> INVALID (guards against a false PASS)
    assert (
        evaluate_seismic_hook(
            circular_dorgir=False,
            bend_angle_deg=200.0,
            straight_extension_mm=120.0,
            bar_diameter_mm=20.0,
        ).outcome
        is EvaluationOutcome.INVALID_INPUT
    )
    # non-bool circular classification -> INVALID
    assert (
        evaluate_seismic_hook(
            circular_dorgir="yes",  # type: ignore[arg-type]
            bend_angle_deg=135.0,
            straight_extension_mm=120.0,
            bar_diameter_mm=20.0,
        ).outcome
        is EvaluationOutcome.INVALID_INPUT
    )


def test_seismic_hook_blocked_in_mostofinejad_mode() -> None:
    step = evaluate_seismic_hook(
        circular_dorgir=False,
        bend_angle_deg=135.0,
        straight_extension_mm=120.0,
        bar_diameter_mm=20.0,
        jurisdiction_mode=MOST,
    )
    assert step.outcome is EvaluationOutcome.JURISDICTION_BLOCKED


# ============================================================================
# BG-TRANS-DORGIR-001 — Clauses 9-21-6-4-1 & 9-21-6-4-2
# ============================================================================

def test_dorgir_closed_tie_passes() -> None:
    step = evaluate_dorgir(
        dorgir_construction=DorgirConstruction.CLOSED_TIE,
        uses_interconnected_headed_bars=False,
    )
    assert step.outcome is EvaluationOutcome.PASS
    assert step.rule_id == "BG-TRANS-DORGIR-001"


def test_dorgir_wound_continuous_passes() -> None:
    step = evaluate_dorgir(
        dorgir_construction=DorgirConstruction.WOUND_CONTINUOUS,
        uses_interconnected_headed_bars=False,
    )
    assert step.outcome is EvaluationOutcome.PASS


def test_dorgir_headed_bars_prohibited_fails() -> None:
    for construction in DorgirConstruction:
        step = evaluate_dorgir(
            dorgir_construction=construction,
            uses_interconnected_headed_bars=True,
            # supply a valid multi-part hook so headed-bar use is the sole cause
            hook_bend_angle_deg=135.0,
            hook_straight_extension_mm=120.0,
            hook_bar_diameter_mm=20.0,
            hook_circular_dorgir=False,
            hook_encloses_longitudinal_bar=True,
        )
        assert step.outcome is EvaluationOutcome.FAIL
        assert step.diagnostics[0].code == "DORGIR_HEADED_BARS_PROHIBITED"


def test_dorgir_multipart_valid_passes() -> None:
    step = evaluate_dorgir(
        dorgir_construction=DorgirConstruction.MULTI_PART,
        uses_interconnected_headed_bars=False,
        hook_bend_angle_deg=135.0,
        hook_straight_extension_mm=120.0,
        hook_bar_diameter_mm=20.0,
        hook_circular_dorgir=False,
        hook_encloses_longitudinal_bar=True,
    )
    assert step.outcome is EvaluationOutcome.PASS


def test_dorgir_multipart_component_hook_bend_fails() -> None:
    # Delegated to the seismic-hook rule: a 120-degree component hook FAILS.
    step = evaluate_dorgir(
        dorgir_construction=DorgirConstruction.MULTI_PART,
        uses_interconnected_headed_bars=False,
        hook_bend_angle_deg=120.0,
        hook_straight_extension_mm=120.0,
        hook_bar_diameter_mm=20.0,
        hook_circular_dorgir=False,
        hook_encloses_longitudinal_bar=True,
    )
    assert step.outcome is EvaluationOutcome.FAIL
    assert (
        step.diagnostics[0].code == "DORGIR_COMPONENT_SEISMIC_HOOK_NOT_SATISFIED"
    )


def test_dorgir_multipart_component_hook_extension_fails() -> None:
    step = evaluate_dorgir(
        dorgir_construction=DorgirConstruction.MULTI_PART,
        uses_interconnected_headed_bars=False,
        hook_bend_angle_deg=135.0,
        hook_straight_extension_mm=40.0,  # < 6*20 = 120 and < 75
        hook_bar_diameter_mm=20.0,
        hook_circular_dorgir=False,
        hook_encloses_longitudinal_bar=True,
    )
    assert step.outcome is EvaluationOutcome.FAIL
    assert (
        step.diagnostics[0].code == "DORGIR_COMPONENT_SEISMIC_HOOK_NOT_SATISFIED"
    )


def test_dorgir_multipart_hook_not_enclosing_longitudinal_bar_fails() -> None:
    step = evaluate_dorgir(
        dorgir_construction=DorgirConstruction.MULTI_PART,
        uses_interconnected_headed_bars=False,
        hook_bend_angle_deg=135.0,
        hook_straight_extension_mm=120.0,
        hook_bar_diameter_mm=20.0,
        hook_circular_dorgir=False,
        hook_encloses_longitudinal_bar=False,
    )
    assert step.outcome is EvaluationOutcome.FAIL
    assert step.diagnostics[0].code == "DORGIR_HOOK_NOT_ENCLOSING_LONGITUDINAL_BAR"


def test_dorgir_multipart_missing_hook_inputs_blocked() -> None:
    step = evaluate_dorgir(
        dorgir_construction=DorgirConstruction.MULTI_PART,
        uses_interconnected_headed_bars=False,
        hook_encloses_longitudinal_bar=True,
    )
    assert step.outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED


def test_dorgir_missing_construction_blocked() -> None:
    assert evaluate_dorgir().outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert (
        evaluate_dorgir(
            dorgir_construction=DorgirConstruction.CLOSED_TIE
        ).outcome
        is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    )


def test_dorgir_invalid_construction_input() -> None:
    step = evaluate_dorgir(
        dorgir_construction="closed",  # type: ignore[arg-type]
        uses_interconnected_headed_bars=False,
    )
    assert step.outcome is EvaluationOutcome.INVALID_INPUT


# ============================================================================
# BG-TRANS-TWO-PIECE-TIE-001 — Clause 9-21-6-1-7
# ============================================================================

def test_two_piece_tie_valid_passes() -> None:
    step = evaluate_two_piece_tie(
        u_tie_bend_angle_deg=135.0,
        second_member_bend_angle_deg=90.0,
        second_member_adjacent_nonspalling_face=True,
    )
    assert step.outcome is EvaluationOutcome.PASS
    assert step.rule_id == "BG-TRANS-TWO-PIECE-TIE-001"


def test_two_piece_tie_u_bend_below_135_fails() -> None:
    step = evaluate_two_piece_tie(
        u_tie_bend_angle_deg=130.0,
        second_member_bend_angle_deg=90.0,
        second_member_adjacent_nonspalling_face=True,
    )
    assert step.outcome is EvaluationOutcome.FAIL
    assert step.diagnostics[0].code == "TWO_PIECE_U_BEND_BELOW_135"


def test_two_piece_tie_member_bend_not_90_fails() -> None:
    step = evaluate_two_piece_tie(
        u_tie_bend_angle_deg=135.0,
        second_member_bend_angle_deg=80.0,
        second_member_adjacent_nonspalling_face=True,
    )
    assert step.outcome is EvaluationOutcome.FAIL
    assert step.diagnostics[0].code == "TWO_PIECE_MEMBER_BEND_NOT_90"


def test_two_piece_tie_wrong_face_fails() -> None:
    step = evaluate_two_piece_tie(
        u_tie_bend_angle_deg=135.0,
        second_member_bend_angle_deg=90.0,
        second_member_adjacent_nonspalling_face=False,
    )
    assert step.outcome is EvaluationOutcome.FAIL
    assert (
        step.diagnostics[0].code == "TWO_PIECE_MEMBER_BEND_NOT_AT_NONSPALLING_FACE"
    )


def test_two_piece_tie_missing_inputs_blocked() -> None:
    assert evaluate_two_piece_tie().outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert (
        evaluate_two_piece_tie(
            u_tie_bend_angle_deg=135.0,
            second_member_bend_angle_deg=90.0,
        ).outcome
        is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    )


# ============================================================================
# BG-TRANS-TORSION-TIE-135HOOK-001 — Clause 9-21-6-1-6-الف
# ============================================================================

def test_torsion_tie_135hook_valid_passes() -> None:
    step = evaluate_torsion_tie_135hook(
        hook_bend_angle_deg=135.0,
        hook_engages_longitudinal_bar=True,
    )
    assert step.outcome is EvaluationOutcome.PASS
    assert step.rule_id == "BG-TRANS-TORSION-TIE-135HOOK-001"


def test_torsion_tie_135hook_bend_below_135_fails() -> None:
    step = evaluate_torsion_tie_135hook(
        hook_bend_angle_deg=120.0,
        hook_engages_longitudinal_bar=True,
    )
    assert step.outcome is EvaluationOutcome.FAIL
    assert step.diagnostics[0].code == "TORSION_TIE_135_HOOK_BEND_BELOW_135"


def test_torsion_tie_135hook_not_engaging_bar_fails() -> None:
    step = evaluate_torsion_tie_135hook(
        hook_bend_angle_deg=135.0,
        hook_engages_longitudinal_bar=False,
    )
    assert step.outcome is EvaluationOutcome.FAIL
    assert (
        step.diagnostics[0].code == "TORSION_TIE_135_HOOK_NOT_ENGAGING_LONGITUDINAL_BAR"
    )


def test_torsion_tie_135hook_missing_inputs_blocked() -> None:
    assert (
        evaluate_torsion_tie_135hook().outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    )
    assert (
        evaluate_torsion_tie_135hook(hook_bend_angle_deg=135.0).outcome
        is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    )


# ============================================================================
# BG-TRANS-TORSION-TIE-SEISMIC-HOOK-001 — Clause 9-21-6-2-7-الف (seismic option)
# ============================================================================

def _seismic_tie_kwargs(**overrides):  # type: ignore[no-untyped-def]
    base = dict(
        hook_bend_angle_deg=135.0,
        hook_straight_extension_mm=120.0,
        hook_bar_diameter_mm=20.0,
        hook_circular_dorgir=False,
        hook_engages_longitudinal_bar=True,
        bend_end_anchored_in_core_concrete=True,
    )
    base.update(overrides)
    return base


def test_torsion_tie_seismic_hook_valid_passes() -> None:
    step = evaluate_torsion_tie_seismic_hook(**_seismic_tie_kwargs())
    assert step.outcome is EvaluationOutcome.PASS
    assert step.rule_id == "BG-TRANS-TORSION-TIE-SEISMIC-HOOK-001"


def test_torsion_tie_seismic_hook_not_in_core_concrete_fails() -> None:
    step = evaluate_torsion_tie_seismic_hook(
        **_seismic_tie_kwargs(bend_end_anchored_in_core_concrete=False)
    )
    assert step.outcome is EvaluationOutcome.FAIL
    assert step.diagnostics[0].code == "TORSION_TIE_BEND_END_NOT_IN_CORE_CONCRETE"


def test_torsion_tie_seismic_hook_not_engaging_bar_fails() -> None:
    step = evaluate_torsion_tie_seismic_hook(
        **_seismic_tie_kwargs(hook_engages_longitudinal_bar=False)
    )
    assert step.outcome is EvaluationOutcome.FAIL
    assert (
        step.diagnostics[0].code
        == "TORSION_TIE_SEISMIC_HOOK_NOT_ENGAGING_LONGITUDINAL_BAR"
    )


def test_torsion_tie_seismic_hook_geometry_delegated_fails() -> None:
    # Bad seismic-hook geometry is delegated to BG-TRANS-SEISMIC-HOOK-001.
    step = evaluate_torsion_tie_seismic_hook(
        **_seismic_tie_kwargs(hook_bend_angle_deg=100.0)
    )
    assert step.outcome is EvaluationOutcome.FAIL
    assert step.diagnostics[0].code == "TORSION_TIE_SEISMIC_HOOK_GEOMETRY_NOT_SATISFIED"


def test_torsion_tie_seismic_hook_missing_geometry_blocked() -> None:
    step = evaluate_torsion_tie_seismic_hook(
        hook_engages_longitudinal_bar=True,
        bend_end_anchored_in_core_concrete=True,
    )
    assert step.outcome is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED


def test_torsion_tie_seismic_hook_missing_inputs_blocked() -> None:
    assert (
        evaluate_torsion_tie_seismic_hook().outcome
        is EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    )
