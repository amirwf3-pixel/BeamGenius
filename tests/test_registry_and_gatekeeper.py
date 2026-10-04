"""Tests for the central Rule Registry and Gatekeeper."""

from __future__ import annotations

from types import MappingProxyType

import pytest

from beamgenius.domain import (
    EvaluationOutcome,
    JurisdictionMode,
    RuleCategory,
    RuleReference,
    VerificationStatus,
)
from beamgenius.registry import (
    RULE_REGISTRY,
    build_blocked_workflow_trace,
    evaluate_rule_gate,
    get_rule,
    list_all_rules,
    list_blocked_rules,
    list_mabhas9_executable_rules,
    list_reference_executable_rules,
    require_rule,
)


def test_mabhas9_executable_rules_exact_set() -> None:
    executable_ids = tuple(rule.rule_id for rule in list_mabhas9_executable_rules())
    assert executable_ids == (
        "BG-FLEX-MIN-001",
        "BG-FLEX-STRESS-BLOCK",
        "BG-FLEX-STRAIN-LIMIT",
        "BG-FLEX-PHI-FACTOR",
        "BG-FLEX-RECT-SINGLY-001",
        "BG-FLEX-TBEAM-B-EFF-001",
        "BG-DETAIL-TRANS-DIA-001",
        "BG-DETAIL-COMP-LAT-001",
        "BG-DETAIL-LONG-SPACING-001",
        "BG-DETAIL-LAYER-SPACING-001",
        "BG-DETAIL-COVER-001",
        "BG-DETAIL-BUNDLE-001",
        "BG-DETAIL-BUNDLE-002",
        "BG-DETAIL-BUNDLE-003",
        "BG-DETAIL-BUNDLE-004",
        "BG-DETAIL-BUNDLE-005",
        "BG-DETAIL-BUNDLE-006",
        "BG-DETAIL-BUNDLE-007",
        "BG-DETAIL-BUNDLE-008",
        "BG-SHEAR-PHI-001",
        "BG-SHEAR-VC-001",
        "BG-SHEAR-VS-001",
        "BG-SHEAR-VS-MAX-001",
        "BG-SHEAR-MIN-001",
        "BG-SHEAR-SPACING-001",
    )
    for rule in list_mabhas9_executable_rules():
        assert rule.status == VerificationStatus.VERIFIED
        assert rule.category == RuleCategory.CODE_RULE
        assert rule.jurisdiction == JurisdictionMode.MABHAS_9_COMPLIANCE
        assert rule.execution_allowed is True


def test_isolated_reference_executable_rules_exact_set() -> None:
    reference_ids = tuple(rule.rule_id for rule in list_reference_executable_rules())
    assert reference_ids == (
        "BG-MOST-5-46",
        "BG-MOST-5-47",
        "BG-MOST-5-48A",
        "BG-MOST-5-48B",
        "BG-MOST-5-49",
        "BG-MOST-5-50",
        "BG-MOST-5-54",
        "BG-MOST-5-55",
        "BG-MOST-5-56",
        "BG-MOST-5-61",
    )
    for rule in list_reference_executable_rules():
        assert rule.status == VerificationStatus.VERIFIED_SOURCE
        assert rule.jurisdiction == JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY
        assert rule.execution_allowed is True


def test_all_registered_rules_have_complete_metadata() -> None:
    all_rules = list_all_rules()
    assert len(all_rules) >= 35
    for rule in all_rules:
        assert rule.rule_id
        assert rule.title
        assert rule.source_document
        assert rule.clause_or_equation
        assert rule.symbolic_formula
        assert rule.description
        assert require_rule(rule.rule_id) == rule
        if not rule.execution_allowed:
            assert rule.blocked_reason is not None and len(rule.blocked_reason) > 0


def test_gatekeeper_mandatory_examples_from_spec() -> None:
    # Example 1: BG-MOST-5-49 in MABHAS_9_COMPLIANCE -> JURISDICTION_BLOCKED
    dec_49_mabhas = evaluate_rule_gate(
        "BG-MOST-5-49", active_jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE
    )
    assert not dec_49_mabhas.allowed
    assert dec_49_mabhas.blocked_outcome == EvaluationOutcome.JURISDICTION_BLOCKED
    trace_49 = dec_49_mabhas.to_blocked_trace_step()
    assert trace_49.outcome == EvaluationOutcome.JURISDICTION_BLOCKED

    # Example 2: BG-MOST-5-51 -> UNVERIFIED_RULE_BLOCKED in both jurisdictions
    for mode in JurisdictionMode:
        dec_51 = evaluate_rule_gate("BG-MOST-5-51", active_jurisdiction=mode)
        assert not dec_51.allowed
        assert dec_51.blocked_outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED

    # Example 3: BG-MOST-5-52 -> UNVERIFIED_RULE_BLOCKED in both jurisdictions
    for mode in JurisdictionMode:
        dec_52 = evaluate_rule_gate("BG-MOST-5-52", active_jurisdiction=mode)
        assert not dec_52.allowed
        assert dec_52.blocked_outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
        assert any("BG-MOST-5-51" in d.message for d in dec_52.diagnostics)

    # Example 4: BG-FLEX-RECT-DOUBLY-001, BG-FLEX-TBEAM-CAP-001, BG-FLEX-LBEAM-CAP-001,
    # and BG-MABHAS9-FLEX-CAP-BLOCKED -> UNVERIFIED_RULE_BLOCKED
    for blocked_flex_id in (
        "BG-FLEX-RECT-DOUBLY-001",
        "BG-FLEX-TBEAM-CAP-001",
        "BG-FLEX-LBEAM-CAP-001",
        "BG-MABHAS9-FLEX-CAP-BLOCKED",
    ):
        dec_flex_cap = evaluate_rule_gate(
            blocked_flex_id,
            active_jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
        )
        assert not dec_flex_cap.allowed
        assert dec_flex_cap.blocked_outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED

    # Example 5: Verified Phase 2B/2C/2D Mabhas 9 flexural, detailing & shear
    # rules are allowed
    # in MABHAS_9_COMPLIANCE and JURISDICTION_BLOCKED in MOSTOFINEJAD_METHODOLOGY_ONLY
    for verified_flex_id in (
        "BG-FLEX-STRESS-BLOCK",
        "BG-FLEX-STRAIN-LIMIT",
        "BG-FLEX-PHI-FACTOR",
        "BG-FLEX-RECT-SINGLY-001",
        "BG-FLEX-TBEAM-B-EFF-001",
        "BG-DETAIL-TRANS-DIA-001",
        "BG-DETAIL-COMP-LAT-001",
        "BG-SHEAR-PHI-001",
        "BG-SHEAR-VC-001",
        "BG-SHEAR-VS-001",
        "BG-SHEAR-VS-MAX-001",
    ):
        dec_ok = evaluate_rule_gate(
            verified_flex_id,
            active_jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
        )
        assert dec_ok.allowed
        assert dec_ok.blocked_outcome is None

        dec_jur = evaluate_rule_gate(
            verified_flex_id,
            active_jurisdiction=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
        )
        assert not dec_jur.allowed
        assert dec_jur.blocked_outcome == EvaluationOutcome.JURISDICTION_BLOCKED


@pytest.mark.parametrize(
    "blocked_most_id",
    [
        "BG-MOST-5-44",
        "BG-MOST-5-45",
        "BG-MOST-5-51",
        "BG-MOST-5-52",
        "BG-MOST-5-53",
        "BG-MOST-5-57",
        "BG-MOST-5-58",
        "BG-MOST-5-59",
        "BG-MOST-5-60",
        "BG-MOST-5-62",
    ],
)
def test_all_blocked_mostofinejad_rules_blocked_in_every_mode(blocked_most_id: str) -> None:
    for mode in JurisdictionMode:
        decision = evaluate_rule_gate(blocked_most_id, active_jurisdiction=mode)
        assert not decision.allowed
        assert decision.blocked_outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
        step = decision.to_blocked_trace_step()
        assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
        assert len(step.diagnostics) >= 1
        assert step.diagnostics[0].required_verification is not None


@pytest.mark.parametrize(
    "ref_rule_id",
    [
        "BG-MOST-5-46",
        "BG-MOST-5-47",
        "BG-MOST-5-48A",
        "BG-MOST-5-48B",
        "BG-MOST-5-49",
        "BG-MOST-5-50",
        "BG-MOST-5-54",
        "BG-MOST-5-55",
        "BG-MOST-5-56",
        "BG-MOST-5-61",
    ],
)
def test_reference_rules_allowed_only_in_mostofinejad_mode(ref_rule_id: str) -> None:
    dec_mabhas = evaluate_rule_gate(
        ref_rule_id, active_jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE
    )
    assert not dec_mabhas.allowed
    assert dec_mabhas.blocked_outcome == EvaluationOutcome.JURISDICTION_BLOCKED

    dec_ref = evaluate_rule_gate(
        ref_rule_id, active_jurisdiction=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY
    )
    assert dec_ref.allowed
    assert dec_ref.blocked_outcome is None


def test_transitive_dependency_gate_catches_indirect_unverified_dependency() -> None:
    # Construct a custom registry where a hypothetical rule claims VERIFIED_SOURCE & execution_allowed=True
    # but depends transitively on BG-MOST-5-52 -> BG-MOST-5-51.
    hypothetical = RuleReference(
        rule_id="BG-TEST-TRANSITIVE",
        title="Hypothetical Rule Depending on 5-52",
        category=RuleCategory.CSA_LSD_METHODOLOGY,
        status=VerificationStatus.VERIFIED_SOURCE,
        jurisdiction=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
        source_document="Test",
        pdf_page=1,
        printed_page=1,
        clause_or_equation="Test",
        symbolic_formula="Test",
        description="Test transitive block",
        execution_allowed=True,
        blocked_reason=None,
        dependencies=("BG-MOST-5-52",),
    )
    custom_reg = dict(RULE_REGISTRY)
    custom_reg[hypothetical.rule_id] = hypothetical
    decision = evaluate_rule_gate(
        "BG-TEST-TRANSITIVE",
        active_jurisdiction=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
        registry=MappingProxyType(custom_reg),
    )
    assert not decision.allowed
    assert decision.blocked_outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert any(d.code == "TRANSITIVE_DEPENDENCY_BLOCKED" for d in decision.diagnostics)


def test_unregistered_rule_is_blocked() -> None:
    assert get_rule("BG-NON-EXISTENT-999") is None
    with pytest.raises(KeyError):
        require_rule("BG-NON-EXISTENT-999")

    decision = evaluate_rule_gate("BG-NON-EXISTENT-999")
    assert not decision.allowed
    assert decision.blocked_outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    step = decision.to_blocked_trace_step()
    assert step.source_document == "UNAVAILABLE"
    assert step.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert len(list_blocked_rules()) >= 22


def test_aud_07_build_blocked_workflow_trace_preserves_unit_metadata() -> None:
    step_explicit_unit = build_blocked_workflow_trace(
        "BG-MABHAS9-FLEX-CAP-BLOCKED",
        additional_context="Section check requested at midspan",
        unit="N*mm",
    )
    assert step_explicit_unit.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step_explicit_unit.unit == "N*mm"
    assert "Section check requested at midspan" in step_explicit_unit.message

    step_ctx_mapping = build_blocked_workflow_trace(
        "BG-SHEAR-VC-BLOCKED",
        additional_context={"context": "Shear check at d from support", "unit": "N"},
    )
    assert step_ctx_mapping.outcome == EvaluationOutcome.UNVERIFIED_RULE_BLOCKED
    assert step_ctx_mapping.unit == "N"
    assert "Shear check at d from support" in step_ctx_mapping.message

    step_default_unit = build_blocked_workflow_trace(
        "BG-DETAIL-DEV-LEN-BLOCKED",
        additional_context="Straight bar development",
    )
    assert step_default_unit.unit == "UNAVAILABLE"

