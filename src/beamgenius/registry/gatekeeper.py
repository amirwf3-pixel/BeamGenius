"""Centralized Verification and Jurisdiction Gatekeeper for BeamGenius."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Optional, Set, Tuple, Union

from beamgenius.domain.enums import (
    DiagnosticSeverity,
    EvaluationOutcome,
    JurisdictionMode,
    RuleCategory,
    VerificationStatus,
)
from beamgenius.domain.trace import (
    CalculationTraceStep,
    EngineeringDiagnostic,
    RuleReference,
    ScalarInputValue,
)
from beamgenius.registry.catalog import RULE_REGISTRY, get_rule

_EXECUTABLE_VERIFICATION_STATUSES: frozenset[VerificationStatus] = frozenset(
    {
        VerificationStatus.VERIFIED,
        VerificationStatus.VERIFIED_SOURCE,
    }
)

_PERMITTED_REFERENCE_CATEGORIES: frozenset[RuleCategory] = frozenset(
    {
        RuleCategory.METHODOLOGY,
        RuleCategory.PRACTICAL_ESTIMATION,
        RuleCategory.CSA_LSD_METHODOLOGY,
        RuleCategory.DESIGN_CHECK,
    }
)


@dataclass(frozen=True)
class GatekeeperDecision:
    """Result of evaluating a rule execution request through the central gatekeeper."""

    allowed: bool
    rule: RuleReference
    active_jurisdiction: JurisdictionMode
    blocked_outcome: Optional[EvaluationOutcome] = None
    diagnostics: Tuple[EngineeringDiagnostic, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "diagnostics", tuple(self.diagnostics))

    def to_blocked_trace_step(
        self,
        *,
        normalized_inputs: Optional[Mapping[str, ScalarInputValue]] = None,
        unit: str = "UNAVAILABLE",
    ) -> CalculationTraceStep:
        """Build an immutable CalculationTraceStep for a blocked rule request."""
        if self.allowed or self.blocked_outcome is None:
            raise ValueError(
                f"Cannot create a blocked trace step for an allowed rule '{self.rule.rule_id}'."
            )
        primary_message = (
            self.diagnostics[0].message
            if self.diagnostics
            else f"Rule '{self.rule.rule_id}' is blocked ({self.blocked_outcome.value})."
        )
        return CalculationTraceStep.from_rule(
            self.rule,
            normalized_inputs=normalized_inputs if normalized_inputs is not None else {},
            intermediate_values={},
            final_result=None,
            unit=unit,
            outcome=self.blocked_outcome,
            diagnostics=self.diagnostics,
            message=primary_message,
        )


def _find_blocked_transitive_dependency(
    rule: RuleReference,
    registry: Mapping[str, RuleReference],
    visited: Optional[Set[str]] = None,
) -> Optional[Tuple[str, str]]:
    """Traverse rule dependencies recursively to find any blocked or unverified dependency."""
    if visited is None:
        visited = set()
    for dep_id in rule.dependencies:
        if dep_id in visited:
            continue
        visited.add(dep_id)
        dep_rule = registry.get(dep_id)
        if dep_rule is None:
            return (
                dep_id,
                f"Dependency '{dep_id}' is not registered in the authoritative Rule Registry.",
            )
        if dep_rule.status not in _EXECUTABLE_VERIFICATION_STATUSES:
            reason = dep_rule.blocked_reason or (
                f"Dependency '{dep_id}' has non-executable status {dep_rule.status.value}."
            )
            return (dep_id, reason)
        if not dep_rule.execution_allowed:
            reason = dep_rule.blocked_reason or (
                f"Dependency '{dep_id}' has execution_allowed=False."
            )
            return (dep_id, reason)
        nested = _find_blocked_transitive_dependency(dep_rule, registry, visited)
        if nested is not None:
            return nested
    return None


def evaluate_rule_gate(
    rule_id: str,
    active_jurisdiction: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
    *,
    registry: Mapping[str, RuleReference] = RULE_REGISTRY,
) -> GatekeeperDecision:
    """Evaluate whether `rule_id` is permitted to execute under `active_jurisdiction`.

    Enforces in strict order:
    1. Rule registration existence
    2. Transitive dependency verification & block status
    3. Direct verification status
    4. Explicit block status (`execution_allowed`)
    5. Jurisdiction mode & rule category compatibility
    """
    rule = registry.get(rule_id) if registry is not RULE_REGISTRY else get_rule(rule_id)
    if rule is None:
        synthetic_rule = RuleReference(
            rule_id=rule_id,
            title="Unregistered Rule",
            category=RuleCategory.PROJECT_RULE,
            status=VerificationStatus.NOT_CHECKED,
            jurisdiction=active_jurisdiction,
            source_document="UNAVAILABLE",
            pdf_page=None,
            printed_page=None,
            clause_or_equation="UNAVAILABLE",
            symbolic_formula="UNAVAILABLE",
            description="Requested rule is not registered in the authoritative Rule Registry.",
            execution_allowed=False,
            blocked_reason="Rule ID does not exist in RULE_REGISTRY.",
            dependencies=(),
        )
        diag = EngineeringDiagnostic(
            code="UNREGISTERED_RULE_BLOCKED",
            severity=DiagnosticSeverity.BLOCK,
            message=(
                f"Requested rule '{rule_id}' is blocked: rule is not registered in "
                f"RULE_REGISTRY (state: status=NOT_CHECKED, jurisdiction={active_jurisdiction.value}). "
                "Required verification: visual source verification and registration in docs/VERIFIED_RULES.md."
            ),
            rule_id=rule_id,
            required_verification=(
                "Verify rule against primary source (Mabhas 9 or Mostofinejad Vol. 1) "
                "and register in docs/VERIFIED_RULES.md."
            ),
        )
        return GatekeeperDecision(
            allowed=False,
            rule=synthetic_rule,
            active_jurisdiction=active_jurisdiction,
            blocked_outcome=EvaluationOutcome.UNVERIFIED_RULE_BLOCKED,
            diagnostics=(diag,),
        )

    # 1. Check transitive dependencies first so dependent rules report their root dependency block
    blocked_dep = _find_blocked_transitive_dependency(rule, registry)
    if blocked_dep is not None:
        dep_id, dep_reason = blocked_dep
        own_reason = f" ({rule.blocked_reason})" if rule.blocked_reason else ""
        diag = EngineeringDiagnostic(
            code="TRANSITIVE_DEPENDENCY_BLOCKED",
            severity=DiagnosticSeverity.BLOCK,
            message=(
                f"Requested rule '{rule.rule_id}' is blocked via transitive dependency "
                f"'{dep_id}': {dep_reason}{own_reason} "
                f"[state: status={rule.status.value}, category={rule.category.value}, "
                f"rule_jurisdiction={rule.jurisdiction.value}, "
                f"active_jurisdiction={active_jurisdiction.value}]. "
                f"Required verification: resolve and verify '{dep_id}' against primary source."
            ),
            rule_id=rule.rule_id,
            required_verification=(
                f"Verify dependency '{dep_id}' and '{rule.rule_id}' against primary source "
                "material before enabling execution."
            ),
        )
        return GatekeeperDecision(
            allowed=False,
            rule=rule,
            active_jurisdiction=active_jurisdiction,
            blocked_outcome=EvaluationOutcome.UNVERIFIED_RULE_BLOCKED,
            diagnostics=(diag,),
        )

    # 2. Check direct verification status
    if rule.status not in _EXECUTABLE_VERIFICATION_STATUSES:
        reason = rule.blocked_reason or (
            f"Rule status '{rule.status.value}' is not an executable verification status."
        )
        diag = EngineeringDiagnostic(
            code="UNVERIFIED_STATUS_BLOCKED",
            severity=DiagnosticSeverity.BLOCK,
            message=(
                f"Requested rule '{rule.rule_id}' is blocked: {reason} "
                f"[state: status={rule.status.value}, category={rule.category.value}, "
                f"rule_jurisdiction={rule.jurisdiction.value}, "
                f"active_jurisdiction={active_jurisdiction.value}]. "
                "Required verification: visual verification against primary source PDF and "
                "promotion to VERIFIED in docs/VERIFIED_RULES.md."
            ),
            rule_id=rule.rule_id,
            required_verification=(
                rule.blocked_reason
                or "Visual verification against primary source PDF and promotion to VERIFIED."
            ),
        )
        return GatekeeperDecision(
            allowed=False,
            rule=rule,
            active_jurisdiction=active_jurisdiction,
            blocked_outcome=EvaluationOutcome.UNVERIFIED_RULE_BLOCKED,
            diagnostics=(diag,),
        )

    # 3. Check explicit execution_allowed flag
    if not rule.execution_allowed:
        reason = rule.blocked_reason or "Explicitly marked execution_allowed=False in registry."
        diag = EngineeringDiagnostic(
            code="EXPLICIT_RULE_BLOCK",
            severity=DiagnosticSeverity.BLOCK,
            message=(
                f"Requested rule '{rule.rule_id}' is explicitly blocked: {reason} "
                f"[state: status={rule.status.value}, category={rule.category.value}, "
                f"rule_jurisdiction={rule.jurisdiction.value}, "
                f"active_jurisdiction={active_jurisdiction.value}]."
            ),
            rule_id=rule.rule_id,
            required_verification=reason,
        )
        return GatekeeperDecision(
            allowed=False,
            rule=rule,
            active_jurisdiction=active_jurisdiction,
            blocked_outcome=EvaluationOutcome.UNVERIFIED_RULE_BLOCKED,
            diagnostics=(diag,),
        )

    # 4. Check Jurisdiction Mode and Rule Category
    if active_jurisdiction == JurisdictionMode.MABHAS_9_COMPLIANCE:
        if (
            rule.jurisdiction != JurisdictionMode.MABHAS_9_COMPLIANCE
            or rule.status != VerificationStatus.VERIFIED
            or rule.category != RuleCategory.CODE_RULE
        ):
            diag = EngineeringDiagnostic(
                code="JURISDICTION_MISMATCH_MABHAS9",
                severity=DiagnosticSeverity.BLOCK,
                message=(
                    f"Requested rule '{rule.rule_id}' is blocked under active jurisdiction "
                    f"'{active_jurisdiction.value}': only rules with status=VERIFIED, "
                    "category=CODE_RULE, and jurisdiction=MABHAS_9_COMPLIANCE may execute in "
                    "Iranian Mabhas 9 compliance mode "
                    f"[rule state: status={rule.status.value}, category={rule.category.value}, "
                    f"rule_jurisdiction={rule.jurisdiction.value}]. "
                    "Required verification: Mabhas 9 code reconciliation and registration in "
                    "docs/VERIFIED_RULES.md."
                ),
                rule_id=rule.rule_id,
                required_verification=(
                    "Reconcile rule with Mabhas 9 and register as a VERIFIED CODE_RULE in "
                    "docs/VERIFIED_RULES.md."
                ),
            )
            return GatekeeperDecision(
                allowed=False,
                rule=rule,
                active_jurisdiction=active_jurisdiction,
                blocked_outcome=EvaluationOutcome.JURISDICTION_BLOCKED,
                diagnostics=(diag,),
            )
    elif active_jurisdiction == JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY:
        if (
            rule.jurisdiction != JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY
            or rule.status != VerificationStatus.VERIFIED_SOURCE
            or rule.category not in _PERMITTED_REFERENCE_CATEGORIES
        ):
            diag = EngineeringDiagnostic(
                code="JURISDICTION_MISMATCH_REFERENCE",
                severity=DiagnosticSeverity.BLOCK,
                message=(
                    f"Requested rule '{rule.rule_id}' is blocked under active jurisdiction "
                    f"'{active_jurisdiction.value}' "
                    f"[rule state: status={rule.status.value}, category={rule.category.value}, "
                    f"rule_jurisdiction={rule.jurisdiction.value}]."
                ),
                rule_id=rule.rule_id,
                required_verification="Use the rule's designated jurisdiction mode.",
            )
            return GatekeeperDecision(
                allowed=False,
                rule=rule,
                active_jurisdiction=active_jurisdiction,
                blocked_outcome=EvaluationOutcome.JURISDICTION_BLOCKED,
                diagnostics=(diag,),
            )

    return GatekeeperDecision(
        allowed=True,
        rule=rule,
        active_jurisdiction=active_jurisdiction,
        blocked_outcome=None,
        diagnostics=(),
    )


def build_blocked_workflow_trace(
    rule_id: str,
    *,
    active_jurisdiction: JurisdictionMode = JurisdictionMode.MABHAS_9_COMPLIANCE,
    normalized_inputs: Optional[Mapping[str, ScalarInputValue]] = None,
    additional_context: Optional[Union[str, Mapping[str, str]]] = None,
    unit: Optional[str] = None,
) -> CalculationTraceStep:
    """Evaluate a blocked workflow/rule through the gatekeeper and emit its trace step."""
    decision = evaluate_rule_gate(rule_id, active_jurisdiction=active_jurisdiction)
    if decision.allowed:
        raise RuntimeError(
            f"Rule '{rule_id}' is allowed in '{active_jurisdiction.value}'; "
            "do not call build_blocked_workflow_trace on an executable rule."
        )

    context_text: Optional[str] = None
    context_unit: Optional[str] = None
    if isinstance(additional_context, Mapping):
        raw_ctx_unit = additional_context.get("unit") or additional_context.get("step_unit")
        if isinstance(raw_ctx_unit, str) and raw_ctx_unit.strip():
            context_unit = raw_ctx_unit.strip()
        raw_ctx_msg = (
            additional_context.get("context")
            or additional_context.get("message")
            or additional_context.get("detail")
        )
        if isinstance(raw_ctx_msg, str) and raw_ctx_msg.strip():
            context_text = raw_ctx_msg.strip()
    elif isinstance(additional_context, str) and additional_context.strip():
        context_text = additional_context.strip()

    resolved_unit = (
        unit.strip()
        if isinstance(unit, str) and unit.strip()
        else (context_unit if context_unit is not None else "UNAVAILABLE")
    )

    step = decision.to_blocked_trace_step(
        normalized_inputs=normalized_inputs,
        unit=resolved_unit,
    )
    if not context_text:
        return step
    updated_diag = EngineeringDiagnostic(
        code=step.diagnostics[0].code if step.diagnostics else "WORKFLOW_BLOCKED",
        severity=DiagnosticSeverity.BLOCK,
        message=f"{step.message} Context: {context_text}",
        rule_id=step.rule_id,
        required_verification=(
            step.diagnostics[0].required_verification if step.diagnostics else None
        ),
    )
    return CalculationTraceStep.from_rule(
        decision.rule,
        normalized_inputs=step.normalized_inputs,
        intermediate_values={},
        final_result=None,
        unit=step.unit,
        outcome=step.outcome,
        diagnostics=(updated_diag, *step.diagnostics[1:]),
        message=updated_diag.message,
    )
