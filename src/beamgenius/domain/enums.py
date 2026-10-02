"""Domain enumerations for BeamGenius Phase 1 engineering core."""

from __future__ import annotations

from enum import Enum


class SectionType(str, Enum):
    """Cross-sectional geometry classification of a reinforced-concrete beam."""

    RECTANGULAR = "RECTANGULAR"
    T_SECTION = "T_SECTION"
    L_SECTION = "L_SECTION"


class FlangeCondition(str, Enum):
    """Flange stress state for flanged (T or L) beam cross-sections."""

    NO_FLANGE = "NO_FLANGE"
    FLANGE_IN_COMPRESSION = "FLANGE_IN_COMPRESSION"
    FLANGE_IN_TENSION = "FLANGE_IN_TENSION"


class JurisdictionMode(str, Enum):
    """Active engineering jurisdiction / execution mode.

    MABHAS_9_COMPLIANCE:
        Production Iranian building code compliance mode. Only rules with
        VerificationStatus.VERIFIED and RuleCategory.CODE_RULE from Mabhas 9
        are permitted to execute.
    MOSTOFINEJAD_METHODOLOGY_ONLY:
        Isolated textbook/reference methodology mode for reproducing verified
        Mostofinejad Vol. 1 equations and benchmark examples. Never represents
        Iranian Mabhas 9 compliance.
    """

    MABHAS_9_COMPLIANCE = "MABHAS_9_COMPLIANCE"
    MOSTOFINEJAD_METHODOLOGY_ONLY = "MOSTOFINEJAD_METHODOLOGY_ONLY"


class VerificationStatus(str, Enum):
    """Source verification status of an engineering rule or formula."""

    VERIFIED = "VERIFIED"
    VERIFIED_SOURCE = "VERIFIED_SOURCE"
    SOURCE_NOTE_REQUIRES_REVIEW = "SOURCE_NOTE_REQUIRES_REVIEW"
    CODE_REVIEW_REQUIRED = "CODE_REVIEW_REQUIRED"
    VERIFY_PENDING = "VERIFY_PENDING"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    UNRESOLVED = "UNRESOLVED"
    NOT_CHECKED = "NOT_CHECKED"


class RuleCategory(str, Enum):
    """Classification of an engineering rule or reference relation."""

    CODE_RULE = "CODE_RULE"
    ENGINEERING_REFERENCE = "ENGINEERING_REFERENCE"
    METHODOLOGY = "METHODOLOGY"
    PRACTICAL_ESTIMATION = "PRACTICAL_ESTIMATION"
    CSA_LSD_METHODOLOGY = "CSA_LSD_METHODOLOGY"
    DESIGN_CHECK = "DESIGN_CHECK"
    PROJECT_RULE = "PROJECT_RULE"
    TEMPORARY = "TEMPORARY"


class EvaluationOutcome(str, Enum):
    """Deterministic outcome of evaluating a single rule or engineering check."""

    PASS = "PASS"
    FAIL = "FAIL"
    EXEMPT = "EXEMPT"
    COMPUTED = "COMPUTED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNVERIFIED_RULE_BLOCKED = "UNVERIFIED_RULE_BLOCKED"
    JURISDICTION_BLOCKED = "JURISDICTION_BLOCKED"
    INVALID_INPUT = "INVALID_INPUT"


class OverallComplianceStatus(str, Enum):
    """Aggregated compliance status across all requested checks in a report.

    Anti-Misleading-PASS invariant:
    OverallComplianceStatus.PASS is emitted ONLY when every requested check
    has succeeded (PASS or EXEMPT) and zero checks are FAIL,
    UNVERIFIED_RULE_BLOCKED, JURISDICTION_BLOCKED, or INVALID_INPUT.
    """

    PASS = "PASS"
    FAIL = "FAIL"
    PARTIAL = "PARTIAL"
    BLOCKED = "BLOCKED"
    INVALID_INPUT = "INVALID_INPUT"


class DiagnosticSeverity(str, Enum):
    """Severity level for an EngineeringDiagnostic entry."""

    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    BLOCK = "BLOCK"
