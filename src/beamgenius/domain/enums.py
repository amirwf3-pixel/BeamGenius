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


class ConcreteCoverExposureClass(str, Enum):
    """Concrete surface exposure condition for minimum cover (Mabhas 9 Table 9-4-6).

    The exposure condition is a REQUIRED typed input of `BG-DETAIL-COVER-001`
    and must never be silently assumed.

    NOT_EXPOSED:
        Concrete not exposed to air/weather and not in contact with earth.
    WEATHER_OR_EARTH_CONTACT:
        Concrete exposed to air/weather or in non-permanent contact with earth.
    PERMANENT_EARTH_CONTACT:
        Concrete cast against and remaining in permanent contact with earth.
    CORROSIVE_ENVIRONMENT:
        Corrosive or otherwise unusual environment: governed by Mabhas 9
        Appendix 9-پ1 (durability) per Clauses 9-4-9-6/9-4-9-7 — NOT verified
        for execution; deterministically blocked.
    """

    NOT_EXPOSED = "NOT_EXPOSED"
    WEATHER_OR_EARTH_CONTACT = "WEATHER_OR_EARTH_CONTACT"
    PERMANENT_EARTH_CONTACT = "PERMANENT_EARTH_CONTACT"
    CORROSIVE_ENVIRONMENT = "CORROSIVE_ENVIRONMENT"


class ConcreteCoverMemberClass(str, Enum):
    """Member classification for Mabhas 9 Table 9-4-6 minimum cover rows.

    The member type is a REQUIRED typed input of ``BG-DETAIL-COVER-001``;
    an unknown member type deterministically returns ``INVALID_INPUT``.

    BEAM / COLUMN / PEDESTAL / TENSION_MEMBER:
        Table 9-4-6 row (iv): 40 mm (not exposed to air/earth) over
        longitudinal bars, stirrups, ties, spirals, and hoops.
    SLAB / JOIST / WALL:
        Table 9-4-6 row (iii): db > 36 mm -> 40 mm; db <= 34 mm -> 20 mm
        (not exposed to air/earth). The (34, 36] mm interval is not covered
        by the table and is never interpolated.
    """

    BEAM = "BEAM"
    COLUMN = "COLUMN"
    PEDESTAL = "PEDESTAL"
    TENSION_MEMBER = "TENSION_MEMBER"
    SLAB = "SLAB"
    JOIST = "JOIST"
    WALL = "WALL"


class CoverReinforcementType(str, Enum):
    """Reinforcement class whose concrete cover is being checked.

    Table 9-4-6 row (iv) covers longitudinal bars, stirrups, ties, spirals,
    and hoops at 40 mm for beams/columns/pedestals/tension members; the type
    is a REQUIRED typed input identifying which reinforcement class the
    cover value applies to.
    """

    LONGITUDINAL = "LONGITUDINAL"
    TRANSVERSE = "TRANSVERSE"


class ConcreteWeightClass(str, Enum):
    """Concrete weight classification for the lambda factor (Mabhas 9 Clause 9-21-3-1-6).

    The weight class is a REQUIRED typed input of every Clause 9-21-3
    development-length evaluator and is never silently assumed.

    NORMAL_WEIGHT: lambda = 1.0.
    LIGHTWEIGHT: lambda = 0.75.
    """

    NORMAL_WEIGHT = "NORMAL_WEIGHT"
    LIGHTWEIGHT = "LIGHTWEIGHT"


class SteelGradeClass(str, Enum):
    """Reinforcing steel grade class for the psi_g factor (Mabhas 9 Table 9-21-3).

    S340/S350/S400/S420: psi_g = 1.0.
    S500/S520: psi_g = 1.15.
    The grade class is a REQUIRED typed input (never assumed); the numeric
    yield stress f_y remains a separate REQUIRED numeric input.
    """

    S340 = "S340"
    S350 = "S350"
    S400 = "S400"
    S420 = "S420"
    S500 = "S500"
    S520 = "S520"


class BarCoatingClass(str, Enum):
    """Bar coating classification for the psi_e coating factor (Tables 9-21-3
    / 9-21-5 / 9-21-6).

    UNCOATED_OR_GALVANIZED: psi_e = 1.0 everywhere the table applies.
    EPOXY_OR_DUAL_COATED: psi_e per the verified table branch conditions.
    """

    UNCOATED_OR_GALVANIZED = "UNCOATED_OR_GALVANIZED"
    EPOXY_OR_DUAL_COATED = "EPOXY_OR_DUAL_COATED"


class WireSurfaceClass(str, Enum):
    """Surface class of welded-wire reinforcement (Mabhas 9 Clauses
    9-21-3-6 and 9-21-3-7).

    UNCOATED / EPOXY: governed by 9-21-3-6 for deformed wires <= 16 mm
    (epoxy mesh carries the explicit psi_e = 1.0 permission of 9-21-3-6-1).
    GALVANIZIZED-galvanized mesh: routed to 9-21-3-7 by 9-21-3-6-4 and is
    NOT_APPLICABLE in the deformed-wire rule.
    """

    UNCOATED = "UNCOATED"
    EPOXY = "EPOXY"
    GALVANIZED = "GALVANIZED"


class AnchorConnectionClass(str, Enum):
    """Anchorage connection classification for the headed-bar psi_p factor
    (Mabhas 9 Table 9-21-6).

    BEAM_COLUMN_JOINT: a beam-column joint anchorage; A_tt >= 0.3*A_ts
    qualifies for psi_p = 1.0 (A_tt per Clause 9-21-3-4-4).
    ANY_OTHER: any other connection; only the anchored-bar spacing (> 6*d_b)
    branch qualifies for psi_p = 1.0.
    """

    BEAM_COLUMN_JOINT = "BEAM_COLUMN_JOINT"
    ANY_OTHER = "ANY_OTHER"


class CompressionConfinementClass(str, Enum):
    """Confinement classification for the compression psi_r factor
    (Mabhas 9 Clause 9-21-3-8-1).

    SPIRAL: confinement by a spiral (دورپیچ) -> psi_r = 0.75.
    CIRCULAR_TIE: continuous circular tie with diameter > 6 mm at spacing
    < 100 mm (both are REQUIRED typed inputs) -> psi_r = 0.75, else 1.0.
    WIRE_TIE: the printed «تنگ سیمی» (wire tie) branch (diameter > 12 mm at
    spacing < 100 mm). The exact Persian noun of this branch is
    VERIFY_PENDING per the source-verification record; the branch is
    deterministically BLOCKED and never executed.
    DORGIR_9_21_6_4: closed confinement tie (دوریگر) per Clause 9-21-6-4 at
    spacing < 100 mm (REQUIRED typed input) -> psi_r = 0.75, else 1.0.
    NONE: none of the listed confinement classes -> psi_r = 1.0.
    """

    SPIRAL = "SPIRAL"
    CIRCULAR_TIE = "CIRCULAR_TIE"
    WIRE_TIE = "WIRE_TIE"
    DORGIR_9_21_6_4 = "DORGIR_9_21_6_4"
    NONE = "NONE"


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
