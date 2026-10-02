"""Immutable traceability, rule metadata, diagnostic, and report models."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Dict, Mapping, Optional, Sequence, Tuple, Union

from beamgenius.domain.enums import (
    DiagnosticSeverity,
    EvaluationOutcome,
    JurisdictionMode,
    OverallComplianceStatus,
    RuleCategory,
    VerificationStatus,
)

ScalarInputValue = Union[float, int, str, bool, None]

_OUTCOME_DOMINANCE_RANK: Mapping[EvaluationOutcome, int] = MappingProxyType(
    {
        EvaluationOutcome.INVALID_INPUT: 60,
        EvaluationOutcome.FAIL: 50,
        EvaluationOutcome.UNVERIFIED_RULE_BLOCKED: 41,
        EvaluationOutcome.JURISDICTION_BLOCKED: 40,
        EvaluationOutcome.COMPUTED: 31,
        EvaluationOutcome.NOT_APPLICABLE: 30,
        EvaluationOutcome.EXEMPT: 11,
        EvaluationOutcome.PASS: 10,
    }
)


def select_dominant_outcome(
    existing: EvaluationOutcome,
    candidate: EvaluationOutcome,
) -> EvaluationOutcome:
    """Return the dominant (worse) EvaluationOutcome according to the report dominance hierarchy.

    Dominance order:
        INVALID_INPUT > FAIL > BLOCKED (UNVERIFIED_RULE_BLOCKED / JURISDICTION_BLOCKED)
        > PARTIAL (COMPUTED / NOT_APPLICABLE) > PASS / EXEMPT
    """
    if _OUTCOME_DOMINANCE_RANK[candidate] > _OUTCOME_DOMINANCE_RANK[existing]:
        return candidate
    return existing


@dataclass(frozen=True)
class RuleReference:
    """Authoritative metadata descriptor for a registered engineering rule.

    Every executable or blocked rule in BeamGenius is represented by an
    immutable RuleReference instance in the central Rule Registry.
    """

    rule_id: str
    title: str
    category: RuleCategory
    status: VerificationStatus
    jurisdiction: JurisdictionMode
    source_document: str
    pdf_page: Optional[int]
    printed_page: Optional[int]
    clause_or_equation: str
    symbolic_formula: str
    description: str
    execution_allowed: bool
    blocked_reason: Optional[str] = None
    dependencies: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "dependencies", tuple(self.dependencies))


@dataclass(frozen=True)
class EngineeringDiagnostic:
    """Structured diagnostic message emitted during validation or rule evaluation."""

    code: str
    severity: DiagnosticSeverity
    message: str
    rule_id: Optional[str] = None
    field_name: Optional[str] = None
    required_verification: Optional[str] = None


@dataclass(frozen=True)
class CalculationTraceStep:
    """Immutable calculation audit record for a single rule evaluation."""

    rule_id: str
    source_document: str
    pdf_page: Optional[int]
    printed_page: Optional[int]
    clause_or_equation: str
    verification_status: VerificationStatus
    symbolic_formula: str
    normalized_inputs: Mapping[str, ScalarInputValue]
    intermediate_values: Mapping[str, float]
    final_result: Optional[float]
    unit: str
    outcome: EvaluationOutcome
    rule_reference: RuleReference
    diagnostics: Tuple[EngineeringDiagnostic, ...] = ()
    message: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "normalized_inputs",
            MappingProxyType(dict(self.normalized_inputs)),
        )
        object.__setattr__(
            self,
            "intermediate_values",
            MappingProxyType(dict(self.intermediate_values)),
        )
        object.__setattr__(self, "diagnostics", tuple(self.diagnostics))

    @classmethod
    def from_rule(
        cls,
        rule: RuleReference,
        *,
        normalized_inputs: Mapping[str, ScalarInputValue],
        intermediate_values: Mapping[str, float],
        final_result: Optional[float],
        unit: str,
        outcome: EvaluationOutcome,
        diagnostics: Sequence[EngineeringDiagnostic] = (),
        message: str = "",
    ) -> CalculationTraceStep:
        """Construct an immutable CalculationTraceStep directly from a RuleReference."""
        return cls(
            rule_id=rule.rule_id,
            source_document=rule.source_document,
            pdf_page=rule.pdf_page,
            printed_page=rule.printed_page,
            clause_or_equation=rule.clause_or_equation,
            verification_status=rule.status,
            symbolic_formula=rule.symbolic_formula,
            normalized_inputs=dict(normalized_inputs),
            intermediate_values=dict(intermediate_values),
            final_result=final_result,
            unit=unit,
            outcome=outcome,
            rule_reference=rule,
            diagnostics=tuple(diagnostics),
            message=message,
        )


@dataclass(frozen=True)
class BeamComplianceReport:
    """Aggregated compliance report produced by the BeamGenius orchestrator.

    Enforces the Anti-Misleading-PASS policy: `is_compliant` is True if and
    only if `overall_status == OverallComplianceStatus.PASS`.
    """

    overall_status: OverallComplianceStatus
    jurisdiction_mode: JurisdictionMode
    trace_steps: Tuple[CalculationTraceStep, ...]
    diagnostics: Tuple[EngineeringDiagnostic, ...]
    outcomes_by_rule: Mapping[str, EvaluationOutcome] = field(default_factory=dict)

    def __post_init__(self) -> None:
        steps_tuple = tuple(self.trace_steps)
        diags_tuple = tuple(self.diagnostics)
        object.__setattr__(self, "trace_steps", steps_tuple)
        object.__setattr__(self, "diagnostics", diags_tuple)

        outcomes: Dict[str, EvaluationOutcome] = {}
        for step in steps_tuple:
            if step.rule_id in outcomes:
                outcomes[step.rule_id] = select_dominant_outcome(
                    outcomes[step.rule_id], step.outcome
                )
            else:
                outcomes[step.rule_id] = step.outcome

        if self.outcomes_by_rule:
            for rule_id, outcome in self.outcomes_by_rule.items():
                if rule_id in outcomes:
                    outcomes[rule_id] = select_dominant_outcome(
                        outcomes[rule_id], outcome
                    )
                else:
                    outcomes[rule_id] = outcome

        object.__setattr__(self, "outcomes_by_rule", MappingProxyType(outcomes))

    @property
    def is_compliant(self) -> bool:
        """Return True strictly when overall_status is PASS."""
        return self.overall_status == OverallComplianceStatus.PASS
