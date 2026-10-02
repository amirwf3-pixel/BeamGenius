"""Single authoritative in-code Rule Registry for BeamGenius Phase 1."""

from __future__ import annotations

from types import MappingProxyType
from typing import Dict, Mapping, Optional, Tuple

from beamgenius.domain.enums import (
    JurisdictionMode,
    RuleCategory,
    VerificationStatus,
)
from beamgenius.domain.trace import RuleReference

SOURCE_MABHAS_9: str = "Iranian National Building Regulations — Mabhas 9"
SOURCE_MOSTOFINEJAD_VOL1: str = (
    "Davood Mostofinejad, Reinforced Concrete Structures, Vol. 1"
)

# ============================================================================
# 1. VERIFIED PRODUCTION MABHAS 9 CODE RULES (docs/VERIFIED_RULES.md)
# ============================================================================

RULE_BG_FLEX_MIN_001 = RuleReference(
    rule_id="BG-FLEX-MIN-001",
    title="Minimum Flexural Reinforcement",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=220,
    printed_page=199,
    clause_or_equation="Clause 9-11-5-1-1 / 9-11-5-1-2 (Waiver: Clause 9-11-5-1-3)",
    symbolic_formula="As,min = max(0.25 * sqrt(f'c) * bw * d / fy, 1.4 * bw * d / fy)",
    description=(
        "Minimum tensile flexural reinforcement required in flexural member sections, "
        "subject to fy <= 550 MPa and Clause 9-11-5-1-3 one-third excess waiver."
    ),
    execution_allowed=True,
    blocked_reason=None,
    dependencies=(),
)

RULE_BG_SHEAR_MIN_001 = RuleReference(
    rule_id="BG-SHEAR-MIN-001",
    title="Minimum Shear Reinforcement",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=221,
    printed_page=None,
    clause_or_equation="Clause 9-11-5-2 & Table 9-11-2",
    symbolic_formula="(Av/s)min = max(0.062 * sqrt(f'c) * bw / fyt, 0.35 * bw / fyt)",
    description=(
        "Minimum required transverse shear reinforcement ratio (Av/s)min where "
        "minimum shear reinforcement is required after evaluating Table 9-11-2 exceptions."
    ),
    execution_allowed=True,
    blocked_reason=None,
    dependencies=(),
)

RULE_BG_SHEAR_SPACING_001 = RuleReference(
    rule_id="BG-SHEAR-SPACING-001",
    title="Maximum Stirrup Spacing",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=227,
    printed_page=None,
    clause_or_equation="Clause 9-11-6-5-3",
    symbolic_formula=(
        "If Vs <= 0.33*sqrt(f'c)*bw*d: s <= min(d/2, 600), st <= min(d, 600); "
        "else: s <= min(d/4, 300), st <= min(d/2, 300)"
    ),
    description=(
        "Maximum longitudinal (s) and transverse-leg (st) stirrup spacing limits "
        "governed by threshold Vs = 0.33 * sqrt(f'c) * bw * d."
    ),
    execution_allowed=True,
    blocked_reason=None,
    dependencies=(),
)

# ============================================================================
# 2. ISOLATED MOSTOFINEJAD CHAPTER 5 REFERENCE METHODOLOGY
#    (docs/MOSTOFINEJAD_FORMULA_REGISTRY.md)
# ============================================================================

RULE_BG_MOST_5_46 = RuleReference(
    rule_id="BG-MOST-5-46",
    title="Flexural Resistance Factor kn",
    category=RuleCategory.METHODOLOGY,
    status=VerificationStatus.VERIFIED_SOURCE,
    jurisdiction=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    source_document=SOURCE_MOSTOFINEJAD_VOL1,
    pdf_page=211,
    printed_page=200,
    clause_or_equation="Eq. (5-46)",
    symbolic_formula="kn = f'c * omega * (1 - 0.59 * omega), where omega = rho * fy / f'c",
    description=(
        "Calculates the nominal flexural capacity coefficient kn for a rectangular "
        "section in Mostofinejad reference methodology."
    ),
    execution_allowed=True,
    blocked_reason=None,
    dependencies=(),
)

RULE_BG_MOST_5_47 = RuleReference(
    rule_id="BG-MOST-5-47",
    title="Section-Size Parameter b*d^2",
    category=RuleCategory.METHODOLOGY,
    status=VerificationStatus.VERIFIED_SOURCE,
    jurisdiction=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    source_document=SOURCE_MOSTOFINEJAD_VOL1,
    pdf_page=211,
    printed_page=200,
    clause_or_equation="Eq. (5-47)",
    symbolic_formula="b * d^2 = Mn / kn = Mu / (phi * kn)",
    description="Determines the section-size parameter b*d^2 in Mostofinejad reference methodology.",
    execution_allowed=True,
    blocked_reason=None,
    dependencies=(),
)

RULE_BG_MOST_5_48A = RuleReference(
    rule_id="BG-MOST-5-48A",
    title="Practical Effective Depth Estimate (Single Layer)",
    category=RuleCategory.PRACTICAL_ESTIMATION,
    status=VerificationStatus.VERIFIED_SOURCE,
    jurisdiction=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    source_document=SOURCE_MOSTOFINEJAD_VOL1,
    pdf_page=211,
    printed_page=200,
    clause_or_equation="Eq. (5-48-a)",
    symbolic_formula="d ≈ h - 65 mm",
    description=(
        "Practical initial dimensioning estimate for one layer of tension reinforcement; "
        "never overrides explicit or geometry-derived effective depth d."
    ),
    execution_allowed=True,
    blocked_reason=None,
    dependencies=(),
)

RULE_BG_MOST_5_48B = RuleReference(
    rule_id="BG-MOST-5-48B",
    title="Practical Effective Depth Estimate (Two Layers)",
    category=RuleCategory.PRACTICAL_ESTIMATION,
    status=VerificationStatus.VERIFIED_SOURCE,
    jurisdiction=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    source_document=SOURCE_MOSTOFINEJAD_VOL1,
    pdf_page=211,
    printed_page=200,
    clause_or_equation="Eq. (5-48-b)",
    symbolic_formula="d ≈ h - 90 mm",
    description=(
        "Practical initial dimensioning estimate for two layers of tension reinforcement; "
        "never overrides explicit or geometry-derived effective depth d."
    ),
    execution_allowed=True,
    blocked_reason=None,
    dependencies=(),
)

RULE_BG_MOST_5_49 = RuleReference(
    rule_id="BG-MOST-5-49",
    title="CSA Equivalent Rectangular Stress-Block Parameter alpha_1",
    category=RuleCategory.CSA_LSD_METHODOLOGY,
    status=VerificationStatus.VERIFIED_SOURCE,
    jurisdiction=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    source_document=SOURCE_MOSTOFINEJAD_VOL1,
    pdf_page=218,
    printed_page=207,
    clause_or_equation="Eq. (5-49)",
    symbolic_formula="alpha_1 = max(0.85 - 0.0015 * f'c, 0.67)",
    description=(
        "CSA A23.3-14 equivalent rectangular stress-block parameter alpha_1. "
        "Isolated textbook reference methodology only; not an Iranian Mabhas 9 rule."
    ),
    execution_allowed=True,
    blocked_reason=None,
    dependencies=(),
)

RULE_BG_MOST_5_50 = RuleReference(
    rule_id="BG-MOST-5-50",
    title="CSA Equivalent Rectangular Stress-Block Parameter beta_1",
    category=RuleCategory.CSA_LSD_METHODOLOGY,
    status=VerificationStatus.VERIFIED_SOURCE,
    jurisdiction=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    source_document=SOURCE_MOSTOFINEJAD_VOL1,
    pdf_page=218,
    printed_page=207,
    clause_or_equation="Eq. (5-50)",
    symbolic_formula="beta_1 = max(0.97 - 0.0025 * f'c, 0.67)",
    description=(
        "CSA A23.3-14 equivalent rectangular stress-block parameter beta_1. "
        "Isolated textbook reference methodology only; not an Iranian Mabhas 9 rule."
    ),
    execution_allowed=True,
    blocked_reason=None,
    dependencies=(),
)

RULE_BG_MOST_5_54 = RuleReference(
    rule_id="BG-MOST-5-54",
    title="CSA Tension-Controlled Stress-Block Depth a",
    category=RuleCategory.CSA_LSD_METHODOLOGY,
    status=VerificationStatus.VERIFIED_SOURCE,
    jurisdiction=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    source_document=SOURCE_MOSTOFINEJAD_VOL1,
    pdf_page=219,
    printed_page=208,
    clause_or_equation="Eq. (5-54)",
    symbolic_formula="a = (As * phi_s * fy) / (alpha_1 * phi_c * f'c * b)",
    description=(
        "Stress-block depth for the source's tension-controlled path (CSA A23.3-14). "
        "Isolated reference methodology only."
    ),
    execution_allowed=True,
    blocked_reason=None,
    dependencies=("BG-MOST-5-49",),
)

RULE_BG_MOST_5_55 = RuleReference(
    rule_id="BG-MOST-5-55",
    title="CSA Tension-Controlled Resisting Moment Mr",
    category=RuleCategory.CSA_LSD_METHODOLOGY,
    status=VerificationStatus.VERIFIED_SOURCE,
    jurisdiction=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    source_document=SOURCE_MOSTOFINEJAD_VOL1,
    pdf_page=219,
    printed_page=208,
    clause_or_equation="Eq. (5-55)",
    symbolic_formula="Mr = T * z = As * phi_s * fy * (d - a / 2)",
    description=(
        "Resisting moment for the source's tension-controlled path (CSA A23.3-14). "
        "Isolated reference methodology only."
    ),
    execution_allowed=True,
    blocked_reason=None,
    dependencies=("BG-MOST-5-54",),
)

RULE_BG_MOST_5_56 = RuleReference(
    rule_id="BG-MOST-5-56",
    title="CSA Tension-Controlled Resisting Moment Mr (Reinforcement Ratio Form)",
    category=RuleCategory.CSA_LSD_METHODOLOGY,
    status=VerificationStatus.VERIFIED_SOURCE,
    jurisdiction=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    source_document=SOURCE_MOSTOFINEJAD_VOL1,
    pdf_page=219,
    printed_page=208,
    clause_or_equation="Eq. (5-56)",
    symbolic_formula=(
        "Mr = rho * phi_s * fy * b * d^2 * (1 - (rho * phi_s * fy) / (2 * alpha_1 * phi_c * f'c))"
    ),
    description=(
        "Alternative form of Eq. (5-55) using reinforcement ratio rho (CSA A23.3-14). "
        "Isolated reference methodology only."
    ),
    execution_allowed=True,
    blocked_reason=None,
    dependencies=("BG-MOST-5-49",),
)

RULE_BG_MOST_5_61 = RuleReference(
    rule_id="BG-MOST-5-61",
    title="Source Limit-State Flexural Resistance Check",
    category=RuleCategory.DESIGN_CHECK,
    status=VerificationStatus.VERIFIED_SOURCE,
    jurisdiction=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    source_document=SOURCE_MOSTOFINEJAD_VOL1,
    pdf_page=220,
    printed_page=209,
    clause_or_equation="Eq. (5-61)",
    symbolic_formula="Mf <= Mr",
    description=(
        "Source limit-state flexural resistance check; final Iranian-code resistance "
        "framework must come from Mabhas 9."
    ),
    execution_allowed=True,
    blocked_reason=None,
    dependencies=(),
)

# ============================================================================
# 3. HARD-BLOCKED MOSTOFINEJAD EQUATIONS
# ============================================================================

RULE_BG_MOST_5_44 = RuleReference(
    rule_id="BG-MOST-5-44",
    title="Mostofinejad Unresolved Equation (5-44)",
    category=RuleCategory.METHODOLOGY,
    status=VerificationStatus.UNRESOLVED,
    jurisdiction=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    source_document=SOURCE_MOSTOFINEJAD_VOL1,
    pdf_page=211,
    printed_page=200,
    clause_or_equation="Eq. (5-44)",
    symbolic_formula="UNAVAILABLE (not visible in supplied source pages)",
    description="Referenced on PDF page 211 / printed page 200 but not visible in supplied pages.",
    execution_allowed=False,
    blocked_reason=(
        "Equation (5-44) is UNRESOLVED: the equation is not visible in the supplied "
        "source pages. Visual verification of the source page is required."
    ),
    dependencies=(),
)

RULE_BG_MOST_5_45 = RuleReference(
    rule_id="BG-MOST-5-45",
    title="Mostofinejad Unresolved Equation (5-45)",
    category=RuleCategory.METHODOLOGY,
    status=VerificationStatus.UNRESOLVED,
    jurisdiction=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    source_document=SOURCE_MOSTOFINEJAD_VOL1,
    pdf_page=211,
    printed_page=200,
    clause_or_equation="Eq. (5-45)",
    symbolic_formula="UNAVAILABLE (not visible in supplied source pages)",
    description=(
        "Referenced on PDF page 211 / printed page 200 but not visible in supplied pages."
    ),
    execution_allowed=False,
    blocked_reason=(
        "Equation (5-45) is UNRESOLVED: the equation is not visible in the supplied "
        "source pages. Visual verification of the source page is required."
    ),
    dependencies=(),
)

RULE_BG_MOST_5_51 = RuleReference(
    rule_id="BG-MOST-5-51",
    title="Balanced-Condition Neutral-Axis Depth cb",
    category=RuleCategory.CSA_LSD_METHODOLOGY,
    status=VerificationStatus.SOURCE_NOTE_REQUIRES_REVIEW,
    jurisdiction=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    source_document=SOURCE_MOSTOFINEJAD_VOL1,
    pdf_page=218,
    printed_page=207,
    clause_or_equation="Eq. (5-51)",
    symbolic_formula="cb = (epsilon_cu / (epsilon_cu + epsilon_y)) * d = (700 / (700 + fy)) * d",
    description=(
        "Balanced-condition neutral-axis depth; flagged SOURCE_NOTE_REQUIRES_REVIEW "
        "due to 700-vs-600 (epsilon_cu=0.003) discrepancy."
    ),
    execution_allowed=False,
    blocked_reason=(
        "BG-MOST-5-51 is blocked (SOURCE_NOTE_REQUIRES_REVIEW): the origin of the "
        "numerical factor 700 alongside epsilon_cu = 0.003 must be reconciled against "
        "the surrounding source text before execution."
    ),
    dependencies=(),
)

RULE_BG_MOST_5_52 = RuleReference(
    rule_id="BG-MOST-5-52",
    title="CSA Balanced Reinforcement Area Asb",
    category=RuleCategory.CSA_LSD_METHODOLOGY,
    status=VerificationStatus.SOURCE_NOTE_REQUIRES_REVIEW,
    jurisdiction=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    source_document=SOURCE_MOSTOFINEJAD_VOL1,
    pdf_page=218,
    printed_page=207,
    clause_or_equation="Eq. (5-52)",
    symbolic_formula="Asb = alpha_1 * beta_1 * b * d * (phi_c / phi_s) * (f'c / fy) * (700 / (700 + fy))",
    description=(
        "CSA balanced reinforcement area Asb; transitively blocked by BG-MOST-5-51 "
        "(700-vs-600 review issue)."
    ),
    execution_allowed=False,
    blocked_reason=(
        "Transitively blocked by BG-MOST-5-51: embeds the unresolved 700 / (700 + fy) "
        "balanced neutral-axis term."
    ),
    dependencies=("BG-MOST-5-49", "BG-MOST-5-50", "BG-MOST-5-51"),
)

RULE_BG_MOST_5_53 = RuleReference(
    rule_id="BG-MOST-5-53",
    title="CSA Balanced Reinforcement Ratio rho_b",
    category=RuleCategory.CSA_LSD_METHODOLOGY,
    status=VerificationStatus.SOURCE_NOTE_REQUIRES_REVIEW,
    jurisdiction=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    source_document=SOURCE_MOSTOFINEJAD_VOL1,
    pdf_page=218,
    printed_page=207,
    clause_or_equation="Eq. (5-53)",
    symbolic_formula="rho_b = alpha_1 * beta_1 * (phi_c / phi_s) * (f'c / fy) * (700 / (700 + fy))",
    description=(
        "CSA balanced reinforcement ratio rho_b; transitively blocked by BG-MOST-5-51 "
        "(700-vs-600 review issue)."
    ),
    execution_allowed=False,
    blocked_reason=(
        "Transitively blocked by BG-MOST-5-51: embeds the unresolved 700 / (700 + fy) "
        "balanced neutral-axis term."
    ),
    dependencies=("BG-MOST-5-49", "BG-MOST-5-50", "BG-MOST-5-51"),
)

RULE_BG_MOST_5_57 = RuleReference(
    rule_id="BG-MOST-5-57",
    title="CSA Over-Reinforced Stress-Block Quadratic Equation",
    category=RuleCategory.CSA_LSD_METHODOLOGY,
    status=VerificationStatus.SOURCE_NOTE_REQUIRES_REVIEW,
    jurisdiction=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    source_document=SOURCE_MOSTOFINEJAD_VOL1,
    pdf_page=219,
    printed_page=208,
    clause_or_equation="Eq. (5-57)",
    symbolic_formula=(
        "a^2 + ((700 * phi_s * rho) / (alpha_1 * phi_c * f'c)) * d * a "
        "- ((700 * phi_s * rho) / (alpha_1 * phi_c * f'c)) * beta_1 * d^2 = 0"
    ),
    description=(
        "Quadratic formulation for CSA compression-controlled path; transitively "
        "blocked by BG-MOST-5-51 (factor 700)."
    ),
    execution_allowed=False,
    blocked_reason=(
        "Transitively blocked by BG-MOST-5-51: embeds the unresolved factor 700 "
        "from Eq. (5-51)."
    ),
    dependencies=("BG-MOST-5-49", "BG-MOST-5-50", "BG-MOST-5-51"),
)

RULE_BG_MOST_5_58 = RuleReference(
    rule_id="BG-MOST-5-58",
    title="CSA Over-Reinforced Auxiliary Variable alpha",
    category=RuleCategory.CSA_LSD_METHODOLOGY,
    status=VerificationStatus.SOURCE_NOTE_REQUIRES_REVIEW,
    jurisdiction=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    source_document=SOURCE_MOSTOFINEJAD_VOL1,
    pdf_page=220,
    printed_page=209,
    clause_or_equation="Eq. (5-58)",
    symbolic_formula="alpha = (700 * phi_s * rho * d) / (alpha_1 * phi_c * f'c)",
    description=(
        "Auxiliary parameter alpha used to solve Eq. (5-57); transitively blocked "
        "by BG-MOST-5-51 (factor 700)."
    ),
    execution_allowed=False,
    blocked_reason=(
        "Transitively blocked by BG-MOST-5-51 and BG-MOST-5-57: embeds the "
        "unresolved factor 700."
    ),
    dependencies=("BG-MOST-5-49", "BG-MOST-5-51", "BG-MOST-5-57"),
)

RULE_BG_MOST_5_59 = RuleReference(
    rule_id="BG-MOST-5-59",
    title="CSA Over-Reinforced Stress-Block Depth Solution a",
    category=RuleCategory.CSA_LSD_METHODOLOGY,
    status=VerificationStatus.SOURCE_NOTE_REQUIRES_REVIEW,
    jurisdiction=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    source_document=SOURCE_MOSTOFINEJAD_VOL1,
    pdf_page=220,
    printed_page=209,
    clause_or_equation="Eq. (5-59)",
    symbolic_formula="a = 0.5 * (sqrt(alpha^2 + 4 * beta_1 * d * alpha) - alpha)",
    description=(
        "Positive root of Eq. (5-57) using alpha from Eq. (5-58); transitively "
        "blocked by BG-MOST-5-51."
    ),
    execution_allowed=False,
    blocked_reason=(
        "Transitively blocked by BG-MOST-5-51, BG-MOST-5-57, and BG-MOST-5-58."
    ),
    dependencies=("BG-MOST-5-50", "BG-MOST-5-57", "BG-MOST-5-58"),
)

RULE_BG_MOST_5_60 = RuleReference(
    rule_id="BG-MOST-5-60",
    title="CSA Over-Reinforced Resisting Moment Mr",
    category=RuleCategory.CSA_LSD_METHODOLOGY,
    status=VerificationStatus.SOURCE_NOTE_REQUIRES_REVIEW,
    jurisdiction=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    source_document=SOURCE_MOSTOFINEJAD_VOL1,
    pdf_page=220,
    printed_page=209,
    clause_or_equation="Eq. (5-60)",
    symbolic_formula="Mr = alpha_1 * phi_c * f'c * a * b * (d - a / 2)",
    description=(
        "Resisting moment for CSA over-reinforced/compression-controlled path; "
        "transitively blocked by BG-MOST-5-59 and BG-MOST-5-51."
    ),
    execution_allowed=False,
    blocked_reason=(
        "Transitively blocked by BG-MOST-5-59 and BG-MOST-5-51: requires "
        "over-reinforced stress-block depth a derived from factor 700."
    ),
    dependencies=("BG-MOST-5-49", "BG-MOST-5-59"),
)

RULE_BG_MOST_5_62 = RuleReference(
    rule_id="BG-MOST-5-62",
    title="CSA Factored Moment Load Combination",
    category=RuleCategory.CSA_LSD_METHODOLOGY,
    status=VerificationStatus.CODE_REVIEW_REQUIRED,
    jurisdiction=JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY,
    source_document=SOURCE_MOSTOFINEJAD_VOL1,
    pdf_page=220,
    printed_page=209,
    clause_or_equation="Eq. (5-62)",
    symbolic_formula="Mf = 1.25 * MD + 1.5 * ML >= 1.4 * MD",
    description=(
        "CSA A23.3-14 factored load combination recorded in source registry; "
        "strictly prohibited as an executable load-combination engine."
    ),
    execution_allowed=False,
    blocked_reason=(
        "BG-MOST-5-62 is hard-blocked as an executable rule: it is a CSA load "
        "combination and must never be used as an Iranian load-combination engine."
    ),
    dependencies=(),
)

# ============================================================================
# 4. BLOCKED UNVERIFIED MABHAS 9 & CHAPTER 7 WORKFLOWS
# ============================================================================

RULE_BG_FLEX_STRESS_BLOCK_PENDING = RuleReference(
    rule_id="BG-FLEX-STRESS-BLOCK-PENDING",
    title="Mabhas 9 Equivalent Rectangular Compression Stress-Block Parameters",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFY_PENDING,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=None,
    printed_page=None,
    clause_or_equation="UNAVAILABLE (Pending visual verification of Mabhas 9 stress-block clauses)",
    symbolic_formula="UNAVAILABLE",
    description=(
        "Mabhas 9 equivalent rectangular concrete compression stress-block "
        "intensity and depth factors (alpha_1, beta_1)."
    ),
    execution_allowed=False,
    blocked_reason=(
        "Mabhas 9 equivalent rectangular stress-block parameters are not yet "
        "visually verified from the Mabhas 9 source PDF in docs/VERIFIED_RULES.md; "
        "ACI/CSA stress-block formulas must not be substituted."
    ),
    dependencies=(),
)

RULE_BG_FLEX_PHI_FACTOR_PENDING = RuleReference(
    rule_id="BG-FLEX-PHI-FACTOR-PENDING",
    title="Mabhas 9 Flexural Strength / Material Reduction Factors",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFY_PENDING,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=None,
    printed_page=None,
    clause_or_equation="UNAVAILABLE (Pending visual verification of Mabhas 9 resistance factor clauses)",
    symbolic_formula="UNAVAILABLE",
    description=(
        "Mabhas 9 flexural resistance reduction factor phi (or material partial "
        "factors) and transition-zone strain interpolation."
    ),
    execution_allowed=False,
    blocked_reason=(
        "Mabhas 9 flexural resistance reduction factors are not yet visually "
        "verified from the Mabhas 9 source PDF in docs/VERIFIED_RULES.md."
    ),
    dependencies=(),
)

RULE_BG_FLEX_STRAIN_LIMIT_PENDING = RuleReference(
    rule_id="BG-FLEX-STRAIN-LIMIT-PENDING",
    title="Mabhas 9 Flexural Strain Compatibility and Ductility / Maximum Steel Limits",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFY_PENDING,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=None,
    printed_page=None,
    clause_or_equation="UNAVAILABLE (Pending visual verification of Mabhas 9 strain/ductility limits)",
    symbolic_formula="UNAVAILABLE",
    description=(
        "Mabhas 9 maximum usable concrete compressive strain epsilon_cu, minimum "
        "net tensile strain epsilon_t, neutral-axis ratio c/d limit, and maximum "
        "reinforcement limit."
    ),
    execution_allowed=False,
    blocked_reason=(
        "Mabhas 9 ultimate concrete strain and tension-controlled ductility limits "
        "are not yet visually verified from the Mabhas 9 source PDF in docs/VERIFIED_RULES.md."
    ),
    dependencies=(),
)

RULE_BG_FLEX_DOUBLY_REINF_PENDING = RuleReference(
    rule_id="BG-FLEX-DOUBLY-REINF-PENDING",
    title="Mabhas 9 Doubly Reinforced Beam Flexural Resistance",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFY_PENDING,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=None,
    printed_page=None,
    clause_or_equation="UNAVAILABLE (Pending visual verification of Mabhas 9 compression-steel flexure clauses)",
    symbolic_formula="UNAVAILABLE",
    description=(
        "Mabhas 9 flexural resistance procedure for doubly reinforced sections "
        "with compression reinforcement As'."
    ),
    execution_allowed=False,
    blocked_reason=(
        "Mabhas 9 doubly reinforced beam flexural resistance and compression-steel "
        "strain-compatibility clauses are not yet visually verified in docs/VERIFIED_RULES.md."
    ),
    dependencies=(
        "BG-FLEX-STRESS-BLOCK-PENDING",
        "BG-FLEX-PHI-FACTOR-PENDING",
        "BG-FLEX-STRAIN-LIMIT-PENDING",
    ),
)

RULE_BG_FLEX_FLANGE_WIDTH_PENDING = RuleReference(
    rule_id="BG-FLEX-FLANGE-WIDTH-PENDING",
    title="Mabhas 9 T- and L-Beam Effective Flange Width and Flanged Flexural Resistance",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFY_PENDING,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=None,
    printed_page=None,
    clause_or_equation="UNAVAILABLE (Pending visual verification of Mabhas 9 T/L-beam clauses)",
    symbolic_formula="UNAVAILABLE",
    description=(
        "Mabhas 9 effective flange width bf and flanged flexural resistance for "
        "T- and L-sections."
    ),
    execution_allowed=False,
    blocked_reason=(
        "Mabhas 9 T- and L-section effective flange width and flanged flexural "
        "resistance clauses are not yet visually verified in docs/VERIFIED_RULES.md."
    ),
    dependencies=(
        "BG-FLEX-STRESS-BLOCK-PENDING",
        "BG-FLEX-PHI-FACTOR-PENDING",
        "BG-FLEX-STRAIN-LIMIT-PENDING",
    ),
)

RULE_BG_MABHAS9_FLEX_CAP_BLOCKED = RuleReference(
    rule_id="BG-MABHAS9-FLEX-CAP-BLOCKED",
    title="Mabhas 9 Flexural Capacity and Resistance Check",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFY_PENDING,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=None,
    printed_page=None,
    clause_or_equation="UNAVAILABLE (Pending Mabhas 9 flexural resistance verification)",
    symbolic_formula="UNAVAILABLE",
    description=(
        "Mabhas 9 flexural capacity/resistance calculation (stress-block parameters, "
        "resistance factors, strain/reinforcement limits)."
    ),
    execution_allowed=False,
    blocked_reason=(
        "Mabhas 9 flexural resistance equations, material/strength reduction factors, "
        "and maximum reinforcement limits are not yet verified in docs/VERIFIED_RULES.md."
    ),
    dependencies=(
        "BG-FLEX-STRESS-BLOCK-PENDING",
        "BG-FLEX-PHI-FACTOR-PENDING",
        "BG-FLEX-STRAIN-LIMIT-PENDING",
    ),
)

RULE_BG_SHEAR_CAP_BLOCKED = RuleReference(
    rule_id="BG-SHEAR-CAP-BLOCKED",
    title="Full Shear Capacity Design and Check",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFY_PENDING,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=None,
    printed_page=None,
    clause_or_equation="UNAVAILABLE (Pending Mabhas 9 & Mostofinejad Ch. 7 verification)",
    symbolic_formula="UNAVAILABLE",
    description="Full beam shear capacity design and compliance checking.",
    execution_allowed=False,
    blocked_reason=(
        "Full shear capacity design/checking is blocked until Mabhas 9 and "
        "Mostofinejad Chapter 7 shear capacity rules (Vc, Vs demand, Vs,max) are "
        "visually verified and registered in docs/VERIFIED_RULES.md."
    ),
    dependencies=(),
)

RULE_BG_SHEAR_VC_BLOCKED = RuleReference(
    rule_id="BG-SHEAR-VC-BLOCKED",
    title="Concrete Shear Resistance Vc Calculation",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFY_PENDING,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=None,
    printed_page=None,
    clause_or_equation="UNAVAILABLE (Pending Vc verification)",
    symbolic_formula="UNAVAILABLE",
    description="Nominal/factored shear resistance provided by concrete Vc.",
    execution_allowed=False,
    blocked_reason=(
        "Concrete shear resistance Vc equation is not yet verified in "
        "docs/VERIFIED_RULES.md."
    ),
    dependencies=(),
)

RULE_BG_SHEAR_VS_DEMAND_BLOCKED = RuleReference(
    rule_id="BG-SHEAR-VS-DEMAND-BLOCKED",
    title="Required Transverse Steel Shear Force Vs from Vu and Vc",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFY_PENDING,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=None,
    printed_page=None,
    clause_or_equation="UNAVAILABLE (Pending Vs demand & Vc verification)",
    symbolic_formula="UNAVAILABLE",
    description="Derivation of required shear steel resistance Vs from factored shear Vu and Vc.",
    execution_allowed=False,
    blocked_reason=(
        "Cannot derive Vs from Vu because Vc and shear strength reduction factors "
        "are not yet verified in docs/VERIFIED_RULES.md."
    ),
    dependencies=("BG-SHEAR-VC-BLOCKED",),
)

RULE_BG_SHEAR_VS_MAX_BLOCKED = RuleReference(
    rule_id="BG-SHEAR-VS-MAX-BLOCKED",
    title="Maximum Shear Reinforcement Capacity Limit Vs,max",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFY_PENDING,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=None,
    printed_page=None,
    clause_or_equation="UNAVAILABLE (Pending Vs,max verification)",
    symbolic_formula="UNAVAILABLE",
    description="Upper limit on shear force Vs carried by transverse reinforcement.",
    execution_allowed=False,
    blocked_reason=(
        "Maximum cross-sectional shear limit Vs,max is not yet verified in "
        "docs/VERIFIED_RULES.md."
    ),
    dependencies=(),
)

RULE_BG_DETAIL_SPACING_BLOCKED = RuleReference(
    rule_id="BG-DETAIL-SPACING-BLOCKED",
    title="Longitudinal Bar Clear Spacing Check",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFY_PENDING,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=None,
    printed_page=None,
    clause_or_equation="UNAVAILABLE (Pending clear spacing verification)",
    symbolic_formula="UNAVAILABLE",
    description="Minimum clear horizontal spacing between parallel longitudinal bars.",
    execution_allowed=False,
    blocked_reason=(
        "Mabhas 9 minimum horizontal clear spacing rules for longitudinal bars are "
        "not yet verified in docs/VERIFIED_RULES.md."
    ),
    dependencies=(),
)

RULE_BG_DETAIL_LAYER_SPACING_BLOCKED = RuleReference(
    rule_id="BG-DETAIL-LAYER-SPACING-BLOCKED",
    title="Multi-Layer Reinforcement Vertical Clear Spacing Check",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFY_PENDING,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=None,
    printed_page=None,
    clause_or_equation="UNAVAILABLE (Pending layer spacing verification)",
    symbolic_formula="UNAVAILABLE",
    description="Minimum vertical clear spacing between layers of longitudinal reinforcement.",
    execution_allowed=False,
    blocked_reason=(
        "Mabhas 9 minimum vertical layer spacing rules are not yet verified in "
        "docs/VERIFIED_RULES.md."
    ),
    dependencies=(),
)

RULE_BG_DETAIL_COVER_BLOCKED = RuleReference(
    rule_id="BG-DETAIL-COVER-BLOCKED",
    title="Minimum Concrete Cover Check",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFY_PENDING,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=None,
    printed_page=None,
    clause_or_equation="UNAVAILABLE (Pending concrete cover verification)",
    symbolic_formula="UNAVAILABLE",
    description="Minimum required concrete protection cover for reinforcement.",
    execution_allowed=False,
    blocked_reason=(
        "Mabhas 9 minimum concrete cover requirements are not yet verified in "
        "docs/VERIFIED_RULES.md."
    ),
    dependencies=(),
)

RULE_BG_DETAIL_TRANS_DIA_PENDING = RuleReference(
    rule_id="BG-DETAIL-TRANS-DIA-PENDING",
    title="Minimum Transverse Reinforcement Diameter",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFY_PENDING,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=228,
    printed_page=None,
    clause_or_equation="Clause 11-5-6-11-9 (docs/DESIGN_RULES.md, unverified)",
    symbolic_formula="db <= 32 -> >= 10 mm; db >= 36 -> >= 12 mm; bundled -> >= 12 mm",
    description=(
        "Minimum transverse bar diameter rule listed in docs/DESIGN_RULES.md; "
        "not yet promoted to docs/VERIFIED_RULES.md (32-36 mm interval unverified)."
    ),
    execution_allowed=False,
    blocked_reason=(
        "Listed in docs/DESIGN_RULES.md only; not yet visually verified and promoted "
        "to docs/VERIFIED_RULES.md."
    ),
    dependencies=(),
)

RULE_BG_DETAIL_COMP_LAT_PENDING = RuleReference(
    rule_id="BG-DETAIL-COMP-LAT-PENDING",
    title="Compression Reinforcement Lateral Support Spacing",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFY_PENDING,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=229,
    printed_page=None,
    clause_or_equation="Clause 12-5-6-11-9 (docs/DESIGN_RULES.md, unverified)",
    symbolic_formula="sc <= min(16 * db, 48 * dbt, bmin)",
    description="Lateral support spacing for compression reinforcement in beams.",
    execution_allowed=False,
    blocked_reason=(
        "Listed in docs/DESIGN_RULES.md only; not yet visually verified and promoted "
        "to docs/VERIFIED_RULES.md."
    ),
    dependencies=(),
)

RULE_BG_INTEG_REINF_PENDING = RuleReference(
    rule_id="BG-INTEG-REINF-PENDING",
    title="Structural Integrity Reinforcement",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFY_PENDING,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=229,
    printed_page=None,
    clause_or_equation="PDF pages 229-230 (docs/DESIGN_RULES.md, unverified)",
    symbolic_formula=">= max(1/4 As,max+, 2 bars) and >= max(1/6 As-, 2 bars)",
    description="Structural integrity longitudinal reinforcement continuity requirements.",
    execution_allowed=False,
    blocked_reason=(
        "Listed in docs/DESIGN_RULES.md only; not yet visually verified and promoted "
        "to docs/VERIFIED_RULES.md."
    ),
    dependencies=(),
)

RULE_BG_INTEG_COL_PENDING = RuleReference(
    rule_id="BG-INTEG-COL-PENDING",
    title="Continuity Through Column Region",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFY_PENDING,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=230,
    printed_page=None,
    clause_or_equation="Clause 11-6-6-3-9 (docs/DESIGN_RULES.md, unverified)",
    symbolic_formula="UNAVAILABLE (detailing continuity requirement)",
    description="Passage of structural-integrity reinforcement through column core.",
    execution_allowed=False,
    blocked_reason=(
        "Listed in docs/DESIGN_RULES.md only; not yet visually verified and promoted "
        "to docs/VERIFIED_RULES.md."
    ),
    dependencies=(),
)

RULE_BG_INTEG_ANCHOR_PENDING = RuleReference(
    rule_id="BG-INTEG-ANCHOR-PENDING",
    title="Non-Continuous Supports Structural Integrity Anchorage",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFY_PENDING,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=230,
    printed_page=None,
    clause_or_equation="Clause 11-6-6-4-9 (docs/DESIGN_RULES.md, unverified)",
    symbolic_formula="UNAVAILABLE (depends on development/anchorage rules)",
    description="Full yield anchorage of structural-integrity bars at non-continuous supports.",
    execution_allowed=False,
    blocked_reason=(
        "Listed in docs/DESIGN_RULES.md only and depends on unverified anchorage rules; "
        "not yet in docs/VERIFIED_RULES.md."
    ),
    dependencies=("BG-DEV-LENGTH-PENDING",),
)

RULE_BG_FLEX_EXT_PENDING = RuleReference(
    rule_id="BG-FLEX-EXT-PENDING",
    title="Flexural Bar Extension Beyond Cutoff Point",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFY_PENDING,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=224,
    printed_page=None,
    clause_or_equation="Clause 4-2-6-11-9 (docs/DESIGN_RULES.md, unverified)",
    symbolic_formula="Extension >= Ld",
    description="Extension of remaining tension reinforcement beyond theoretical cutoff point.",
    execution_allowed=False,
    blocked_reason=(
        "Listed in docs/DESIGN_RULES.md only and depends on unverified development "
        "length Ld; not yet in docs/VERIFIED_RULES.md."
    ),
    dependencies=("BG-DEV-LENGTH-PENDING",),
)

RULE_BG_POS_SIMPLE_PENDING = RuleReference(
    rule_id="BG-POS-SIMPLE-PENDING",
    title="Positive Reinforcement Continuation at Simple Supports",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFY_PENDING,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=225,
    printed_page=None,
    clause_or_equation="Clause 2-3-6-11-9 (docs/DESIGN_RULES.md, unverified)",
    symbolic_formula=">= 1/4 As,max+ extended >= 150 mm into support",
    description="Positive flexural reinforcement continuation into simple supports.",
    execution_allowed=False,
    blocked_reason=(
        "Listed in docs/DESIGN_RULES.md only; not yet visually verified and promoted "
        "to docs/VERIFIED_RULES.md."
    ),
    dependencies=(),
)

RULE_BG_CUTOFF_COND_PENDING = RuleReference(
    rule_id="BG-CUTOFF-COND-PENDING",
    title="Flexural Reinforcement Cutoff Conditions",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFY_PENDING,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=None,
    printed_page=None,
    clause_or_equation="Clause 5-2-6-11-9 (Pending Verification in docs/DESIGN_RULES.md)",
    symbolic_formula="UNAVAILABLE",
    description="Shear/moment conditions required at flexural bar cutoff locations.",
    execution_allowed=False,
    blocked_reason="Explicitly listed under Pending Verification in docs/DESIGN_RULES.md.",
    dependencies=(),
)

RULE_BG_DEV_LENGTH_PENDING = RuleReference(
    rule_id="BG-DEV-LENGTH-PENDING",
    title="Development Length Ld Equations",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFY_PENDING,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=None,
    printed_page=None,
    clause_or_equation="Clause 2-3-6-9 (Pending Verification in docs/DESIGN_RULES.md)",
    symbolic_formula="UNAVAILABLE",
    description="Tension and compression bar development length equations.",
    execution_allowed=False,
    blocked_reason="Explicitly listed under Pending Verification in docs/DESIGN_RULES.md.",
    dependencies=(),
)

RULE_BG_NEG_EXT_PENDING = RuleReference(
    rule_id="BG-NEG-EXT-PENDING",
    title="Negative Reinforcement Extension Equation",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFY_PENDING,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=None,
    printed_page=None,
    clause_or_equation="UNAVAILABLE (Pending Verification in docs/DESIGN_RULES.md)",
    symbolic_formula="UNAVAILABLE",
    description="Inflection-point extension length requirement for negative reinforcement.",
    execution_allowed=False,
    blocked_reason="Explicitly listed under Pending Verification in docs/DESIGN_RULES.md.",
    dependencies=(),
)

RULE_BG_SKIN_REINF_PENDING = RuleReference(
    rule_id="BG-SKIN-REINF-PENDING",
    title="Skin Reinforcement Spacing",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFY_PENDING,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=None,
    printed_page=None,
    clause_or_equation="UNAVAILABLE (Pending Verification in docs/DESIGN_RULES.md)",
    symbolic_formula="UNAVAILABLE",
    description="Side-face skin reinforcement distribution and spacing in deep webs.",
    execution_allowed=False,
    blocked_reason="Explicitly listed under Pending Verification in docs/DESIGN_RULES.md.",
    dependencies=(),
)

RULE_BG_BENT_ANCHOR_PENDING = RuleReference(
    rule_id="BG-BENT-ANCHOR-PENDING",
    title="Bent-Bar Standard Hook Anchorage Length",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFY_PENDING,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=None,
    printed_page=None,
    clause_or_equation="UNAVAILABLE (Pending Verification in docs/DESIGN_RULES.md)",
    symbolic_formula="UNAVAILABLE",
    description="Development length ldh of bars in tension terminating in a standard hook.",
    execution_allowed=False,
    blocked_reason="Explicitly listed under Pending Verification in docs/DESIGN_RULES.md.",
    dependencies=(),
)

RULE_BG_TORSION_PENDING = RuleReference(
    rule_id="BG-TORSION-PENDING",
    title="Beam Torsion Design and Compliance Rules",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFY_PENDING,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=None,
    printed_page=None,
    clause_or_equation="UNAVAILABLE (Pending Verification in docs/DESIGN_RULES.md)",
    symbolic_formula="UNAVAILABLE",
    description="Threshold torsion, torsional shear stress, and longitudinal/transverse torsion steel.",
    execution_allowed=False,
    blocked_reason="Explicitly listed under Pending Verification in docs/DESIGN_RULES.md.",
    dependencies=(),
)

RULE_BG_TABLE_2_11_99_PENDING = RuleReference(
    rule_id="BG-TABLE-2-11-99-PENDING",
    title="Remaining Table 2-11-99 / 9-11-2 Shear Exceptions",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFY_PENDING,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=221,
    printed_page=None,
    clause_or_equation="Table 9-11-2 / OCR Table 2-11-99 (Pending Verification)",
    symbolic_formula="UNAVAILABLE",
    description="Unverified exception clauses (including one-way joists) in Table 9-11-2.",
    execution_allowed=False,
    blocked_reason=(
        "Explicitly listed under Pending Verification in docs/DESIGN_RULES.md and "
        "requires visual source verification of the applicable joist/exception clauses."
    ),
    dependencies=(),
)

_ALL_RULES_TUPLE: Tuple[RuleReference, ...] = (
    # Verified Mabhas 9 rules
    RULE_BG_FLEX_MIN_001,
    RULE_BG_SHEAR_MIN_001,
    RULE_BG_SHEAR_SPACING_001,
    # Isolated Mostofinejad reference rules
    RULE_BG_MOST_5_46,
    RULE_BG_MOST_5_47,
    RULE_BG_MOST_5_48A,
    RULE_BG_MOST_5_48B,
    RULE_BG_MOST_5_49,
    RULE_BG_MOST_5_50,
    RULE_BG_MOST_5_54,
    RULE_BG_MOST_5_55,
    RULE_BG_MOST_5_56,
    RULE_BG_MOST_5_61,
    # Blocked Mostofinejad rules
    RULE_BG_MOST_5_44,
    RULE_BG_MOST_5_45,
    RULE_BG_MOST_5_51,
    RULE_BG_MOST_5_52,
    RULE_BG_MOST_5_53,
    RULE_BG_MOST_5_57,
    RULE_BG_MOST_5_58,
    RULE_BG_MOST_5_59,
    RULE_BG_MOST_5_60,
    RULE_BG_MOST_5_62,
    # Blocked Mabhas 9 & Ch. 7 workflows
    RULE_BG_FLEX_STRESS_BLOCK_PENDING,
    RULE_BG_FLEX_PHI_FACTOR_PENDING,
    RULE_BG_FLEX_STRAIN_LIMIT_PENDING,
    RULE_BG_FLEX_DOUBLY_REINF_PENDING,
    RULE_BG_FLEX_FLANGE_WIDTH_PENDING,
    RULE_BG_MABHAS9_FLEX_CAP_BLOCKED,
    RULE_BG_SHEAR_CAP_BLOCKED,
    RULE_BG_SHEAR_VC_BLOCKED,
    RULE_BG_SHEAR_VS_DEMAND_BLOCKED,
    RULE_BG_SHEAR_VS_MAX_BLOCKED,
    RULE_BG_DETAIL_SPACING_BLOCKED,
    RULE_BG_DETAIL_LAYER_SPACING_BLOCKED,
    RULE_BG_DETAIL_COVER_BLOCKED,
    RULE_BG_DETAIL_TRANS_DIA_PENDING,
    RULE_BG_DETAIL_COMP_LAT_PENDING,
    RULE_BG_INTEG_REINF_PENDING,
    RULE_BG_INTEG_COL_PENDING,
    RULE_BG_INTEG_ANCHOR_PENDING,
    RULE_BG_FLEX_EXT_PENDING,
    RULE_BG_POS_SIMPLE_PENDING,
    RULE_BG_CUTOFF_COND_PENDING,
    RULE_BG_DEV_LENGTH_PENDING,
    RULE_BG_NEG_EXT_PENDING,
    RULE_BG_SKIN_REINF_PENDING,
    RULE_BG_BENT_ANCHOR_PENDING,
    RULE_BG_TORSION_PENDING,
    RULE_BG_TABLE_2_11_99_PENDING,
)

_REGISTRY_DICT: Dict[str, RuleReference] = {rule.rule_id: rule for rule in _ALL_RULES_TUPLE}
RULE_REGISTRY: Mapping[str, RuleReference] = MappingProxyType(_REGISTRY_DICT)


def get_rule(rule_id: str) -> Optional[RuleReference]:
    """Retrieve a RuleReference by ID, or None if not registered."""
    return RULE_REGISTRY.get(rule_id)


def require_rule(rule_id: str) -> RuleReference:
    """Retrieve a registered RuleReference by ID or raise KeyError."""
    if rule_id not in RULE_REGISTRY:
        raise KeyError(f"Rule '{rule_id}' is not registered in RULE_REGISTRY.")
    return RULE_REGISTRY[rule_id]


def list_all_rules() -> Tuple[RuleReference, ...]:
    """Return all registered rules in deterministic order."""
    return _ALL_RULES_TUPLE


def list_mabhas9_executable_rules() -> Tuple[RuleReference, ...]:
    """Return all rules permitted to execute in MABHAS_9_COMPLIANCE mode."""
    return tuple(
        rule
        for rule in _ALL_RULES_TUPLE
        if rule.jurisdiction == JurisdictionMode.MABHAS_9_COMPLIANCE
        and rule.status == VerificationStatus.VERIFIED
        and rule.category == RuleCategory.CODE_RULE
        and rule.execution_allowed
    )


def list_reference_executable_rules() -> Tuple[RuleReference, ...]:
    """Return all rules permitted to execute in MOSTOFINEJAD_METHODOLOGY_ONLY mode."""
    return tuple(
        rule
        for rule in _ALL_RULES_TUPLE
        if rule.jurisdiction == JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY
        and rule.status == VerificationStatus.VERIFIED_SOURCE
        and rule.execution_allowed
    )


def list_blocked_rules() -> Tuple[RuleReference, ...]:
    """Return all registered rules that are blocked from execution."""
    return tuple(rule for rule in _ALL_RULES_TUPLE if not rule.execution_allowed)
