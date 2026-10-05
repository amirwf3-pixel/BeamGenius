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

RULE_BG_FLEX_STRESS_BLOCK = RuleReference(
    rule_id="BG-FLEX-STRESS-BLOCK",
    title="Mabhas 9 Equivalent Rectangular Concrete Compression Stress-Block Parameters",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=22,
    printed_page=113,
    clause_or_equation=(
        "Clauses 9-8-2-2-6 & 9-8-2-2-7, Eq. (9-8-2), Eq. (9-8-3-الف), "
        "Eq. (9-8-3-ب), Eq. (9-8-4) (f'c limits: Clause 9-3-3-3)"
    ),
    symbolic_formula=(
        "a = beta_1 * c; beta_1 = 0.85 (f'c <= 28) else max(0.85 - 0.05*(f'c - 28)/7, 0.65); "
        "alpha_0 = 0.85 (f'c <= 55) else max(0.85 - 0.004*(f'c - 55), 0.75)"
    ),
    description=(
        "Equivalent rectangular concrete compression stress-block intensity factor "
        "alpha_0 and depth factor beta_1 under Mabhas 9 (1399) Chapter 9-8."
    ),
    execution_allowed=True,
    blocked_reason=None,
    dependencies=(),
)

RULE_BG_FLEX_STRAIN_LIMIT = RuleReference(
    rule_id="BG-FLEX-STRAIN-LIMIT",
    title="Mabhas 9 Flexural Strain Compatibility and Tension-Controlled Beam Ductility Limit",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=22,
    printed_page=113,
    clause_or_equation=(
        "Clauses 9-8-2-2-2, 9-8-2-2-3, 9-7-4-2, 9-11-2-3 "
        "(Es = 200,000 MPa per 9-4-8-4; fy <= 550 MPa per Table 9-4-4)"
    ),
    symbolic_formula=(
        "epsilon_cu = 0.003; epsilon_ty = fy / Es; "
        "epsilon_t = 0.003 * (dt - c) / c >= epsilon_ty + 0.003 "
        "(c / dt <= 0.003 / (epsilon_ty + 0.006))"
    ),
    description=(
        "Linear strain compatibility at ultimate concrete strain epsilon_cu = 0.003 "
        "and mandatory tension-controlled ductility limit (epsilon_t >= epsilon_ty + 0.003) "
        "for non-prestressed beams with Pu < 0.10 * f'c * Ag."
    ),
    execution_allowed=True,
    blocked_reason=None,
    dependencies=(),
)

RULE_BG_FLEX_PHI_FACTOR = RuleReference(
    rule_id="BG-FLEX-PHI-FACTOR",
    title="Mabhas 9 Flexural Strength Reduction Factor phi",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=16,
    printed_page=107,
    clause_or_equation=(
        "Clauses 9-7-4-1 through 9-7-4-4, Table 9-7-2, "
        "Eq. (9-7-10-الف), Eq. (9-7-10-ب)"
    ),
    symbolic_formula=(
        "phi = 0.90 (epsilon_t >= epsilon_ty + 0.003); "
        "phi = 0.75 spiral / 0.65 other (epsilon_t <= epsilon_ty); "
        "linear transition Eq. (9-7-10-الف)/(9-7-10-ب) for epsilon_ty < epsilon_t < epsilon_ty + 0.003"
    ),
    description=(
        "Strength reduction factor phi for flexure and axial force as a function "
        "of extreme net tensile strain epsilon_t and yield strain epsilon_ty."
    ),
    execution_allowed=True,
    blocked_reason=None,
    dependencies=(),
)

RULE_BG_FLEX_RECT_SINGLY_001 = RuleReference(
    rule_id="BG-FLEX-RECT-SINGLY-001",
    title="Mabhas 9 Rectangular Singly-Reinforced Beam Flexural Resistance",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=22,
    printed_page=113,
    clause_or_equation=(
        "Clauses 9-8-1-4 Eq. (9-8-1-الف), 9-8-2-1-1, 9-8-2-2-1 through 9-8-2-2-8, "
        "9-7-4-2, Table 9-7-2, 9-11-2-3, 9-3-3-3, Table 9-4-4"
    ),
    symbolic_formula=(
        "a = (As * fy) / (alpha_0 * f'c * bw); c = a / beta_1; "
        "Mn = As * fy * (d - a / 2); phi * Mn >= Mu (with epsilon_t >= epsilon_ty + 0.003, phi = 0.90)"
    ),
    description=(
        "Nominal and design flexural capacity (Mn, phi*Mn >= Mu) and tension-controlled "
        "ductility check for rectangular singly-reinforced non-prestressed concrete beams."
    ),
    execution_allowed=True,
    blocked_reason=None,
    dependencies=(
        "BG-FLEX-STRESS-BLOCK",
        "BG-FLEX-STRAIN-LIMIT",
        "BG-FLEX-PHI-FACTOR",
    ),
)

RULE_BG_FLEX_TBEAM_B_EFF_001 = RuleReference(
    rule_id="BG-FLEX-TBEAM-B-EFF-001",
    title="Mabhas 9 Non-Prestressed T-Beam and L-Beam Effective Compression Flange Width",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=12,
    printed_page=103,
    clause_or_equation="Clauses 9-6-3-3-1, Table 9-6-1, 9-6-3-3-2, and 9-11-2-5",
    symbolic_formula=(
        "T-beam: bf <= bw + 2 * min(8*hf, sw/2, ln/8); "
        "L-beam: bf <= bw + min(6*hf, sw/2, ln/12); "
        "Isolated T-beam: hf >= 0.5*bw and bf <= 4*bw"
    ),
    description=(
        "Effective compression flange width bf for non-prestressed T-beams and L-beams "
        "integral with slabs (Table 9-6-1) and isolated T-beams (Clause 9-6-3-3-2)."
    ),
    execution_allowed=True,
    blocked_reason=None,
    dependencies=(),
)

RULE_BG_DETAIL_TRANS_DIA_001 = RuleReference(
    rule_id="BG-DETAIL-TRANS-DIA-001",
    title="Mabhas 9 Minimum Transverse Reinforcement Diameter",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=228,
    printed_page=None,
    clause_or_equation="Clause 9-11-6-5-11",
    symbolic_formula="db <= 32 mm -> dbt >= 10 mm; db >= 36 mm -> dbt >= 12 mm; bundled -> dbt >= 12 mm",
    description=(
        "Minimum transverse reinforcement diameter enclosing longitudinal bars in "
        "beams. The 32 < db < 36 mm interval for non-bundled bars has no verified "
        "interpolation and deterministically returns UNVERIFIED_RULE_BLOCKED."
    ),
    execution_allowed=True,
    blocked_reason=None,
    dependencies=(),
)

RULE_BG_DETAIL_COMP_LAT_001 = RuleReference(
    rule_id="BG-DETAIL-COMP-LAT-001",
    title="Mabhas 9 Compression Reinforcement Lateral Support Spacing",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=229,
    printed_page=None,
    clause_or_equation="Clause 9-11-6-5-12",
    symbolic_formula="sc <= min(16 * db, 48 * dbt, b_min)",
    description=(
        "Longitudinal spacing of transverse reinforcement enclosing compression bars: "
        "db is the smallest diameter of longitudinal compression bars, dbt the "
        "transverse bar diameter, and b_min the least section dimension."
    ),
    execution_allowed=True,
    blocked_reason=None,
    dependencies=(),
)

RULE_BG_DETAIL_LONG_SPACING_001 = RuleReference(
    rule_id="BG-DETAIL-LONG-SPACING-001",
    title="Mabhas 9 Longitudinal Bar Minimum Clear Spacing in a Horizontal Layer",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=441,
    printed_page=420,
    clause_or_equation=(
        "Clause 9-21-2-1-1 (with scope exceptions 9-21-2-1-3 columns/pedestals/"
        "ties/wall boundary elements & 9-21-2-1-4 shotcrete)"
    ),
    symbolic_formula=(
        "s_clear >= max(25 mm, db_max, (4/3) * d_agg); bundled bars blocked "
        "(equivalent diameter 9-21-5-6 VERIFIED as BG-DETAIL-BUNDLE-006; integration pending)"
    ),
    description=(
        "Minimum clear distance between parallel longitudinal bars placed in one "
        "horizontal layer: not less than each of 25 mm, the largest bar diameter "
        "db_max, and 4/3 times the nominal maximum aggregate size d_agg. The column "
        "rule (Clause 9-21-2-1-3: 40 mm / 1.5*db_max) is never substituted; "
        "shotcrete is excluded per Clause 9-21-2-1-4 (NOT_APPLICABLE); bundled "
        "bars deterministically return UNVERIFIED_RULE_BLOCKED until Clause "
        "the Clause 9-21-5-6 equivalent diameter is integrated here (VERIFIED as BG-DETAIL-BUNDLE-006 in a separate stage)."
    ),
    execution_allowed=True,
    blocked_reason=None,
    dependencies=(),
)

RULE_BG_DETAIL_LAYER_SPACING_001 = RuleReference(
    rule_id="BG-DETAIL-LAYER-SPACING-001",
    title="Mabhas 9 Multi-Layer Longitudinal Bar Vertical Clear Spacing and Alignment",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=441,
    printed_page=420,
    clause_or_equation="Clause 9-21-2-1-2",
    symbolic_formula=(
        "multiple horizontal layers: upper bars directly above lower bars "
        "(alignment) AND clear inter-layer distance >= 25 mm"
    ),
    description=(
        "For parallel longitudinal bars placed in several horizontal layers, "
        "the bars of each upper layer must be placed directly above the bars of "
        "the layer below, and the clear distance between two successive layers "
        "must be at least 25 mm (independent of bar diameter and aggregate "
        "size). Vertical alignment is a required typed input and is never "
        "silently assumed; bundled bars deterministically return "
        "UNVERIFIED_RULE_BLOCKED until the Clause 9-21-5-6 equivalent diameter (VERIFIED as BG-DETAIL-BUNDLE-006) is integrated here in a separate stage."
    ),
    execution_allowed=True,
    blocked_reason=None,
    dependencies=(),
)

RULE_BG_DETAIL_COVER_001 = RuleReference(
    rule_id="BG-DETAIL-COVER-001",
    title="Mabhas 9 Minimum Concrete Cover over Beam Reinforcement (Normal Environment)",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=92,
    printed_page=71,
    clause_or_equation=(
        "Clauses 9-4-9-4, 9-4-9-5, 9-4-9-5-1..3 + Table 9-4-6 "
        "(PDF pp. 92-93, Printed pp. 71-72; corrosive routing 9-4-9-6)"
    ),
    symbolic_formula=(
        "cover >= Table 9-4-6 (beams): no air/earth contact -> 40 mm; air/weather "
        "or non-permanent earth contact -> 50 mm (db 18-58) / 40 mm (db <= 16); "
        "permanent earth contact -> 75 mm"
    ),
    description=(
        "Minimum concrete cover over all longitudinal and transverse beam "
        "reinforcement (longitudinal bars, stirrups, ties, spirals, hoops; also "
        "headed shear reinforcement heads/plates per Clause 9-4-9-5-3) under "
        "normal (non-corrosive) conditions per Clauses 9-4-9-4/9-4-9-5-1 and "
        "Table 9-4-6. The exposure condition is a required typed input; "
        "corrosive/unusual environments are routed to Appendix 9-پ1 per Clause "
        "9-4-9-6 and deterministically blocked; the bundled-group rule (Clause "
        "9-4-9-5-2, min(d_eq, 75|50 mm)) is blocked pending integration of the "
        "Clause 9-21-5-6 equivalent diameter, VERIFIED as BG-DETAIL-BUNDLE-006 "
        "and implemented in a separate stage; diameter classes outside db <= 16 mm and 18-58 mm "
        "are never interpolated."
    ),
    execution_allowed=True,
    blocked_reason=None,
    dependencies=(),
)

RULE_BG_SHEAR_PHI_001 = RuleReference(
    rule_id="BG-SHEAR-PHI-001",
    title="Mabhas 9 Shear Strength Reduction Factor phi and Factored One-Way Shear Check",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=128,
    printed_page=107,
    clause_or_equation=(
        "Clauses 9-7-4-1, Table 9-7-2 (Row 2), 9-7-4-5, 9-8-1-4 Eq. (9-8-1-ب), "
        "9-8-4-1-1, 9-8-4-1-2 Eq. (9-8-8), 9-11-3-3, 9-11-4-3"
    ),
    symbolic_formula="phi = 0.75; Vn = Vc + Vs; phi * Vn = phi * (Vc + Vs) >= Vu",
    description=(
        "Strength reduction factor phi = 0.75 for standard one-way shear and "
        "factored shear adequacy check phi*Vn = phi*(Vc + Vs) >= Vu."
    ),
    execution_allowed=True,
    blocked_reason=None,
    dependencies=(),
)

RULE_BG_SHEAR_VC_001 = RuleReference(
    rule_id="BG-SHEAR-VC-001",
    title="Mabhas 9 Concrete One-Way Shear Resistance Vc",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=141,
    printed_page=120,
    clause_or_equation=(
        "Clauses 9-8-4-4-1 through 9-8-4-4-5, Eq. (9-8-12-الف), Eq. (9-8-12-ب), "
        "Eq. (9-8-13), Eq. (9-8-14), 9-8-4-2-2, 9-3-2-2, Tables 9-3-1 & 9-3-2"
    ),
    symbolic_formula=(
        "Av >= Av,min: Vc = (0.17*lambda*sqrt(f'c) + Nu/(6*Ag))*bw*d or "
        "(0.66*lambda*(rho_w)^(1/3)*sqrt(f'c) + Nu/(6*Ag))*bw*d; "
        "Av < Av,min: Vc = (0.66*lambda_s*lambda*(rho_w)^(1/3)*sqrt(f'c) + Nu/(6*Ag))*bw*d; "
        "lambda_s = min(sqrt(2/(1 + d/250)), 1.0); Nu/(6*Ag) <= 0.05*f'c; "
        "0 <= Vc <= 0.42*lambda*sqrt(f'c)*bw*d"
    ),
    description=(
        "Nominal one-way shear resistance Vc provided by concrete under Mabhas 9 (1399) "
        "Section 9-8-4-4 with lightweight factor lambda, size-effect factor lambda_s, "
        "axial load modifier Nu/(6*Ag), and upper/lower bounds."
    ),
    execution_allowed=True,
    blocked_reason=None,
    dependencies=(),
)

RULE_BG_SHEAR_VS_001 = RuleReference(
    rule_id="BG-SHEAR-VS-001",
    title="Mabhas 9 Transverse Reinforcement One-Way Shear Resistance Vs and Demand",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=142,
    printed_page=121,
    clause_or_equation=(
        "Clauses 9-8-4-2-3, 9-4-8-5, Table 9-4-4, 9-8-4-5-1 Eq. (9-8-15), "
        "9-8-4-5-3 Eq. (9-8-16), 9-8-4-5-4 Eq. (9-8-17)"
    ),
    symbolic_formula=(
        "Vs,req = max(Vu / phi - Vc, 0); "
        "Vertical (alpha = 90 deg): Vs = Av * fyt * d / s; "
        "Inclined (45 deg <= alpha <= 90 deg): Vs = Av * fyt * (sin(alpha) + cos(alpha)) * d / s "
        "(with fyt <= 420 MPa per Table 9-4-4)"
    ),
    description=(
        "Transverse shear reinforcement resistance Vs for vertical (Eq. 9-8-16) and "
        "inclined (Eq. 9-8-17) stirrups and required Vs,req = max(Vu/phi - Vc, 0) (Eq. 9-8-15)."
    ),
    execution_allowed=True,
    blocked_reason=None,
    dependencies=("BG-SHEAR-PHI-001",),
)

RULE_BG_SHEAR_VS_MAX_001 = RuleReference(
    rule_id="BG-SHEAR-VS-MAX-001",
    title="Mabhas 9 Maximum One-Way Shear / Web-Crushing Limit (Vs,max and Vu,max)",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=140,
    printed_page=119,
    clause_or_equation="Clause 9-8-4-1-3, Eq. (9-8-9) (with Eq. (9-8-1-ب) & Eq. (9-8-8))",
    symbolic_formula=(
        "Vu <= phi * (Vc + 0.66 * sqrt(f'c) * bw * d); "
        "Vs <= Vs,max = 0.66 * sqrt(f'c) * bw * d"
    ),
    description=(
        "Cross-sectional dimension adequacy / web-crushing limit on Vu and Vs "
        "under Mabhas 9 Clause 9-8-4-1-3 Eq. (9-8-9)."
    ),
    execution_allowed=True,
    blocked_reason=None,
    dependencies=("BG-SHEAR-PHI-001",),
)

RULE_BG_SHEAR_MIN_001 = RuleReference(
    rule_id="BG-SHEAR-MIN-001",
    title="Minimum Shear Reinforcement",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=221,
    printed_page=200,
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
    printed_page=206,
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

RULE_BG_FLEX_RECT_DOUBLY_001 = RuleReference(
    rule_id="BG-FLEX-RECT-DOUBLY-001",
    title="Mabhas 9 Doubly-Reinforced Rectangular Beam Flexural Resistance",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFY_PENDING,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=22,
    printed_page=113,
    clause_or_equation=(
        "Clause 9-8-2-2 (general principles only; procedural doubly-reinforced "
        "decomposition VERIFY_PENDING)"
    ),
    symbolic_formula="UNAVAILABLE (Pending verification of doubly-reinforced procedural rules)",
    description=(
        "Mabhas 9 flexural resistance for rectangular beams with compression "
        "reinforcement As' > 0 (compression steel strain compatibility, displaced "
        "concrete treatment, and Mn = Mn1 + Mn2 split)."
    ),
    execution_allowed=False,
    blocked_reason=(
        "Mabhas 9 doubly-reinforced beam procedural equations (compression-steel "
        "yielding/non-yielding formulation, displaced concrete area treatment, and "
        "Mn1 + Mn2 split) are not yet verified in docs/VERIFIED_RULES.md."
    ),
    dependencies=(
        "BG-FLEX-STRESS-BLOCK",
        "BG-FLEX-STRAIN-LIMIT",
        "BG-FLEX-PHI-FACTOR",
    ),
)

RULE_BG_FLEX_TBEAM_CAP_001 = RuleReference(
    rule_id="BG-FLEX-TBEAM-CAP-001",
    title="Mabhas 9 T-Beam Flanged Flexural Resistance",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFY_PENDING,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=12,
    printed_page=103,
    clause_or_equation=(
        "Clauses 9-6-3-3-1 & 9-8-2-2 (bf verified in BG-FLEX-TBEAM-B-EFF-001; "
        "flanged flexural capacity decomposition VERIFY_PENDING)"
    ),
    symbolic_formula="UNAVAILABLE (Pending verification of T-beam flanged flexural capacity rules)",
    description=(
        "Mabhas 9 flexural resistance for T-beams (neutral axis in flange vs web "
        "decomposition and flange-in-tension slab reinforcement distribution)."
    ),
    execution_allowed=False,
    blocked_reason=(
        "While T-beam effective compression flange width bf is verified under "
        "BG-FLEX-TBEAM-B-EFF-001, full T-beam flanged flexural capacity decomposition "
        "is not yet verified in docs/VERIFIED_RULES.md; silent rectangular fallback "
        "is prohibited."
    ),
    dependencies=(
        "BG-FLEX-TBEAM-B-EFF-001",
        "BG-FLEX-STRESS-BLOCK",
        "BG-FLEX-STRAIN-LIMIT",
        "BG-FLEX-PHI-FACTOR",
    ),
)

RULE_BG_FLEX_LBEAM_CAP_001 = RuleReference(
    rule_id="BG-FLEX-LBEAM-CAP-001",
    title="Mabhas 9 L-Beam Flanged Flexural Resistance",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFY_PENDING,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=12,
    printed_page=103,
    clause_or_equation=(
        "Clauses 9-6-3-3-1 & 9-8-2-2 (bf verified in BG-FLEX-TBEAM-B-EFF-001; "
        "L-beam flanged flexural capacity decomposition VERIFY_PENDING)"
    ),
    symbolic_formula="UNAVAILABLE (Pending verification of L-beam flanged flexural capacity rules)",
    description=(
        "Mabhas 9 flexural resistance for L-beams (flange on one side of web)."
    ),
    execution_allowed=False,
    blocked_reason=(
        "While L-beam effective compression flange width bf is verified under "
        "BG-FLEX-TBEAM-B-EFF-001, full L-beam flanged flexural capacity decomposition "
        "is not yet verified in docs/VERIFIED_RULES.md; silent rectangular fallback "
        "is prohibited."
    ),
    dependencies=(
        "BG-FLEX-TBEAM-B-EFF-001",
        "BG-FLEX-STRESS-BLOCK",
        "BG-FLEX-STRAIN-LIMIT",
        "BG-FLEX-PHI-FACTOR",
    ),
)

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


RULE_BG_DETAIL_BUNDLE_001 = RuleReference(
    rule_id="BG-DETAIL-BUNDLE-001",
    title="Mabhas 9 Bundled Bars — Maximum Number of Bars per Bundle",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=462,
    printed_page=441,
    clause_or_equation="Clause 9-21-5-1 (Printed p. 441 / PDF p. 462)",
    symbolic_formula="n_bundle <= 4",
    description=(
        "The number of bars in a bar bundle (group of bars acting as one unit) "
        "is limited to four (Clause 9-21-5-1). Visually verified from the "
        "Mabhas 9 (1399, 5th ed.) source-page capture with visible footer "
        "‘۴۴۱’ (Printed p. 441; PDF p. 462; verification confirmed 2026-10-03 "
        "and re-confirmed 2026-10-05). Applicability: bar bundles acting as "
        "one unit in structural members (longitudinal bars). A single bar is "
        "not a bundle (NOT_APPLICABLE); more than four bars is a verifiable "
        "code violation (FAIL). Required typed input (never assumed): "
        "bundle_n_bars (integer >= 1)."
    ),
    execution_allowed=True,
    dependencies=(),
)

RULE_BG_DETAIL_BUNDLE_002 = RuleReference(
    rule_id="BG-DETAIL-BUNDLE-002",
    title="Mabhas 9 Bundled Bars — Transverse Enclosure & Compressed-Bundle Tie Diameter",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=463,
    printed_page=442,
    clause_or_equation="Clause 9-21-5-2 (Printed p. 442 / PDF p. 463)",
    symbolic_formula="transverse enclosure required; compressed bundle -> dbt >= 12 mm",
    description=(
        "A bar bundle must be enclosed by transverse reinforcement; the "
        "transverse bars of bundles under compression must be at least 12 mm "
        "in diameter (Clause 9-21-5-2). Visually verified from the Mabhas 9 "
        "(1399, 5th ed.) source-page capture (Printed p. 442 / PDF p. 463; "
        "verification confirmed 2026-10-03 and re-confirmed 2026-10-05). "
        "Applicability: bar bundles including compressed bundles (e.g. "
        "columns, compressed beam bars). Unresolved transverse-spacing "
        "details of Clause 9-21-6 remain outside this rule (no dependency "
        "invented). Required typed inputs (never assumed): bundle_n_bars, "
        "bundle_has_transverse_enclosure, bundle_is_compressed; "
        "transverse_bar_diameter_mm required when bundle_is_compressed."
    ),
    execution_allowed=True,
    dependencies=(),
)

RULE_BG_DETAIL_BUNDLE_003 = RuleReference(
    rule_id="BG-DETAIL-BUNDLE-003",
    title="Mabhas 9 Bundled Bars — Beam Bundle Bar Diameter Prohibition",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=463,
    printed_page=442,
    clause_or_equation="Clause 9-21-5-3 (Printed p. 442 / PDF p. 463)",
    symbolic_formula="beam: bundled db > 34 mm prohibited",
    description=(
        "In beams, bars with diameter larger than 34 mm are not permitted in "
        "bundles (Clause 9-21-5-3 — beam-specific). Visually verified from "
        "the Mabhas 9 (1399, 5th ed.) source-page capture (Printed p. 442 / "
        "PDF p. 463). Applicability: beams only; non-beam member classes "
        "return NOT_APPLICABLE; unknown member classes return INVALID_INPUT; "
        "a bundled beam bar above 34 mm is a verifiable violation (FAIL). "
        "Required typed inputs (never assumed): bundle_n_bars, member_class "
        "(ConcreteCoverMemberClass), bundle_bar_diameter_mm."
    ),
    execution_allowed=True,
    dependencies=(),
)

RULE_BG_DETAIL_BUNDLE_004 = RuleReference(
    rule_id="BG-DETAIL-BUNDLE-004",
    title="Mabhas 9 Bundled Bars — Cutoff Point Staggering in Flexural Members",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=463,
    printed_page=442,
    clause_or_equation="Clause 9-21-5-4 (Printed p. 442 / PDF p. 463)",
    symbolic_formula="min |xi - xj| >= 40 * db between bundle bar cutoff points",
    description=(
        "Along the span of flexural members, the cutoff point of each bar of "
        "a bundle must be at least 40 bar diameters from the cutoff points "
        "of the other bars of the bundle (Clause 9-21-5-4). Visually "
        "verified from the Mabhas 9 (1399, 5th ed.) source-page capture "
        "(Printed p. 442 / PDF p. 463). Applicability: flexural members with "
        "bundled bars being curtailed along the span; when no bundle bar is "
        "cut the rule is NOT_APPLICABLE; insufficient stagger is a verifiable "
        "violation (FAIL). Required typed inputs (never assumed): "
        "bundle_n_bars, bundle_has_cutoffs; bundle_bar_diameter_mm and "
        "bundle_cutoff_positions_mm required when bundle_has_cutoffs."
    ),
    execution_allowed=True,
    dependencies=(),
)

RULE_BG_DETAIL_BUNDLE_005 = RuleReference(
    rule_id="BG-DETAIL-BUNDLE-005",
    title="Mabhas 9 Bundled Bars — Bar Plane Arrangement Limit",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=463,
    printed_page=442,
    clause_or_equation="Clause 9-21-5-5 (Printed p. 442 / PDF p. 463)",
    symbolic_formula="n > 2: bars per plane <= 2, except at splice locations",
    description=(
        "In bundles with more than two bars, not all bar axes may lie in one "
        "plane, and at most two bars may lie in one plane, except at splice "
        "locations (Clause 9-21-5-5). Visually verified from the Mabhas 9 "
        "(1399, 5th ed.) source-page capture (Printed p. 442 / PDF p. 463). "
        "Applicability: bundles with more than two bars (n <= 2 is "
        "NOT_APPLICABLE); an oversized plane arrangement at a non-splice "
        "location is a verifiable violation (FAIL). Required typed inputs "
        "(never assumed): bundle_n_bars, bundle_max_bars_in_single_plane, "
        "bundle_is_splice_location."
    ),
    execution_allowed=True,
    dependencies=(),
)

RULE_BG_DETAIL_BUNDLE_006 = RuleReference(
    rule_id="BG-DETAIL-BUNDLE-006",
    title="Mabhas 9 Bundled Bars — Equivalent Bar Diameter",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=463,
    printed_page=442,
    clause_or_equation="Clause 9-21-5-6 (Printed p. 442 / PDF p. 463)",
    symbolic_formula="d_eq = db * sqrt(n) for n identical bars (equal total area, coincident centroid)",
    description=(
        "For checks whose calculation is based on bar diameter — spacing "
        "limits, minimum cover, confinement coefficient of Clause 9-21-3-2-1 "
        "and coating factor of Clause 9-21-3-2-2 — a bundle is treated as "
        "one equivalent bar of equal total area whose centroid coincides "
        "with the bundle centroid (Clause 9-21-5-6); for n identical bars "
        "the equivalent diameter is db*sqrt(n). Visually verified from the "
        "Mabhas 9 (1399, 5th ed.) source-page capture (Printed p. 442 / PDF "
        "p. 463). Applicability: identical-bar bundles for spacing-limit, "
        "minimum-cover, confinement-coefficient and coating-factor "
        "calculations. Only the identical-bar form is implemented; "
        "mixed-diameter bundles remain BLOCKED (UNSUPPORTED_CONFIGURATION); "
        "development length is NOT computed via d_eq (Clause 9-21-5-7 "
        "provides its own multipliers). Required typed inputs (never "
        "assumed): bundle_n_bars, bundle_bar_diameter_mm, "
        "bundle_bars_identical."
    ),
    execution_allowed=True,
    dependencies=(),
)

RULE_BG_DETAIL_BUNDLE_007 = RuleReference(
    rule_id="BG-DETAIL-BUNDLE-007",
    title="Mabhas 9 Bundled Bars — Development Length Multiplier",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=463,
    printed_page=442,
    clause_or_equation="Clause 9-21-5-7 (Printed p. 442 / PDF p. 463)",
    symbolic_formula="ld_bundle = factor * ld_single; factor: 2-bar 1.00, 3-bar 1.20, 4-bar 1.33",
    description=(
        "The development length of bars in a bundle, in tension or "
        "compression, equals the single-bar development length for a 2-bar "
        "bundle, and is 20% and 33% greater for 3-bar and 4-bar bundles "
        "respectively (Clause 9-21-5-7). Visually verified from the Mabhas 9 "
        "(1399, 5th ed.) source-page capture (Printed p. 442 / PDF p. 463). "
        "Applicability: bar bundles in tension or compression "
        "(development-length scaling only). The underlying development "
        "length of Clause 9-21-3 is NOT computed here — a missing verified "
        "single-bar development length deterministically yields BLOCKED "
        "(MISSING_SINGLE_BAR_DEVELOPMENT_LENGTH), never an invented value. "
        "Required typed inputs (never assumed): bundle_n_bars, "
        "single_bar_development_length_mm."
    ),
    execution_allowed=True,
    dependencies=(),
)

RULE_BG_DETAIL_BUNDLE_008 = RuleReference(
    rule_id="BG-DETAIL-BUNDLE-008",
    title="Mabhas 9 Bundled Bars — Lap Splice Constraints & Multiplier",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=463,
    printed_page=442,
    clause_or_equation="Clause 9-21-5-8 (Printed p. 442 / PDF p. 463)",
    symbolic_formula=(
        "lap = ld_single * factor(9-21-5-7); individual laps must not overlap; "
        "bundle-to-bundle lap prohibited"
    ),
    description=(
        "The lap splice length of each bar in a bundle is computed from the "
        "single-bar development length including the Clause 9-21-5-7 bundle "
        "increase; the laps of individual bars of a bundle must not overlap "
        "along the bars; a lap splice of a whole bundle with another bundle "
        "is prohibited (Clause 9-21-5-8). Visually verified from the Mabhas "
        "9 (1399, 5th ed.) source-page capture (Printed p. 442 / PDF p. 463, "
        "text continuing onto the following page). Applicability: "
        "bar bundles being lap-spliced (bundle-specific splice constraints). "
        "The underlying lap rules of Clause 9-21-4 are NOT computed here — "
        "a missing verified single-bar development length is BLOCKED, never "
        "invented. Required typed inputs (never assumed): bundle_n_bars, "
        "single_bar_development_length_mm, bundle_is_bundle_to_bundle_lap, "
        "bundle_laps_overlap."
    ),
    execution_allowed=True,
    dependencies=(),
)


# ============================================================================
# 1b. VERIFIED PRODUCTION MABHAS 9 CODE RULES: CLAUSE 9-21-3 DEVELOPMENT
#     LENGTH (Phase 2F Stage C, promoted 2026-10-05 — visual verification of
#     the committed phase2f-source-442-472 evidence scan; see
#     docs/VERIFIED_RULES.md and matrix §4B/§4C)
# ============================================================================

RULE_BG_DEV_LENGTH_TENSION_001 = RuleReference(
    rule_id="BG-DEV-LENGTH-TENSION-001",
    title="Mabhas 9 Development Length of Deformed Bars in Tension (General Relation)",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=445,
    printed_page=425,
    clause_or_equation=(
        "Clause 9-21-3-1-3..6 & 9-21-3-2-1 & Eq. (9-21-1) (Printed pp. 425-426 / "
        "PDF pp. 445-446); Eq. (9-21-2) K_tr & cap (Printed p. 426 / PDF p. 446); "
        "Table 9-21-3 factors (Printed p. 427 / PDF p. 447); reduction limits "
        "9-21-3-9 (Printed pp. 435-436 / PDF pp. 455-456)"
    ),
    symbolic_formula=(
        "l_d = (psi_t*psi_e*psi_s*psi_g / (lambda * min((c_b+K_tr)/d_b, 2.5))) * "
        "(0.9 * f_y / sqrt(min(sqrt(f'c), 8.3)**2)) * d_b, >= 300 mm; "
        "K_tr = 40*A_tr/(s*n) (K_tr = 0 always permitted); psi_t*psi_e <= 1.7"
    ),
    description=(
        "Development length of deformed bars or wires in tension, Clause "
        "9-21-3-2-1-الف: l_d = [psi_t*psi_e*psi_s*psi_g/(lambda*((c_b+K_tr)/d_b))] "
        "* (0.9*f_y/sqrt(f'c)) * d_b per Eq. (9-21-1), with c_b = min(distance "
        "from bar center to nearest concrete surface, half center-to-center bar "
        "spacing), K_tr = 40*A_tr/(s*n) per Eq. (9-21-2) (K_tr = 0 is always "
        "permitted even when transverse reinforcement is present), confinement "
        "index (c_b+K_tr)/d_b capped at 2.5, minimum l_d = 300 mm "
        "(9-21-3-2-1-ب). No resistance factor phi (9-21-3-1-4); sqrt(f'c) "
        "clamped at 8.3 MPa (9-21-3-1-5); lambda = 1.0 normal-weight / 0.75 "
        "lightweight (9-21-3-1-6). Modification factors per Table 9-21-3 "
        "(9-21-3-2-2): psi_g = 1.0 (S340/S350/S400/S420) or 1.15 (S500/S520); "
        "psi_e = 1.5 (epoxy/dual-coated with cover < 3*d_b or clear spacing "
        "< 6*d_b) / 1.2 (other epoxy/dual-coated) / 1.0 (uncoated or "
        "galvanized); psi_s = 0.8 (d_b < 20 mm) / 1.0; psi_t = 1.3 (horizontal "
        "bar with >= 300 mm fresh concrete cast below) / 1.0; psi_t*psi_e "
        "<= 1.7. Excess-reinforcement reduction (9-21-3-9) permitted by the "
        "ratio A_s,required/A_s,provided only for the listed equation cases "
        "and only when none of the 9-21-3-9-2 contexts apply; the 300 mm "
        "floor is preserved after any reduction. Visually verified 2026-10-05 "
        "from the committed phase2f-source-442-472 evidence scan "
        "(git show df8067a:phase2f-source-442-472/page-NNN.jpg). Applicability: "
        "tension development of single deformed bars/wires (not hooks/heads — "
        "see BG-DEV-LENGTH-HOOKED-001 / BG-DEV-LENGTH-HEADED-001). Required "
        "typed inputs (never assumed): steel_grade, bar_diameter_mm, "
        "yield_stress_mpa, concrete_strength_mpa, concrete_weight_class, "
        "concrete_cover_mm, clear_spacing_mm, provide_top_bar_placement, "
        "coating_class, apply_k_tr (with transverse_area_mm2, "
        "transverse_spacing_mm, developed_bar_count when True). Reduction "
        "inputs only when excess_reinforcement_reduction is requested."
    ),
    execution_allowed=True,
    dependencies=(),
)

RULE_BG_DEV_LENGTH_TENSION_TABLE_001 = RuleReference(
    rule_id="BG-DEV-LENGTH-TENSION-TABLE-001",
    title="Mabhas 9 Simplified Development Length of Deformed Bars in Tension (Table 9-21-4)",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=448,
    printed_page=428,
    clause_or_equation=(
        "Clause 9-21-3-2-3 & Table 9-21-4 (Printed p. 428 / PDF p. 448); "
        "Table 9-21-3 factors (Printed p. 427 / PDF p. 447); floors "
        "9-21-3-2-1-ب (Printed p. 426 / PDF p. 446)"
    ),
    symbolic_formula=(
        "l_d = psi_t*psi_e*psi_g * f_y/(D*lambda*sqrt(min(sqrt(f'c),8.3)**2)) "
        "* d_b, D = 2.1/1.7 (confined row: (clear >= d_b & min ties) or "
        "(clear >= 2*d_b & cover >= d_b), d_b<20/>=20) or 1.4/1.1 (other); "
        ">= 300 mm"
    ),
    description=(
        "Simplified development length of deformed bars or wires in tension "
        "per Clause 9-21-3-2-3 and Table 9-21-4: l_d = (psi_t*psi_e*psi_g) * "
        "f_y/(D*lambda*sqrt(f'c)) * d_b. Confined row (clear spacing or "
        "splice >= d_b with minimum code ties provided along l_d, OR clear "
        "spacing or splice >= 2*d_b with cover >= d_b): D = 2.1 (d_b < 20 mm) "
        "/ 1.7 (d_b >= 20 mm). Other cases: D = 1.4 / 1.1. In all cases the "
        "300 mm minimum of 9-21-3-2-1-ب governs. Factors per Table 9-21-3 "
        "with the same verification as BG-DEV-LENGTH-TENSION-001 "
        "(psi_t*psi_e <= 1.7; sqrt(f'c) <= 8.3 clamp; lambda weight class). "
        "Excess-reinforcement reduction per 9-21-3-9 with the 300 mm floor "
        "preserved; prohibited contexts (9-21-3-9-2) block the reduction. "
        "Visually verified 2026-10-05 (page-447/448 evidence JPGs). "
        "Applicability: tension development via the simplified table; the "
        "general relation path is BG-DEV-LENGTH-TENSION-001. Required typed "
        "inputs (never assumed): steel_grade, bar_diameter_mm, "
        "yield_stress_mpa, concrete_strength_mpa, concrete_weight_class, "
        "concrete_cover_mm, clear_spacing_mm, provide_top_bar_placement, "
        "coating_class, min_code_ties_provided_along_ld."
    ),
    execution_allowed=True,
    dependencies=(),
)

RULE_BG_DEV_LENGTH_HOOKED_001 = RuleReference(
    rule_id="BG-DEV-LENGTH-HOOKED-001",
    title="Mabhas 9 Development Length of Deformed Bars with Standard Hooks in Tension",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=448,
    printed_page=428,
    clause_or_equation=(
        "Clause 9-21-3-3-1 & Eq. (9-21-3) (Printed p. 428 / PDF p. 448); "
        "Table 9-21-5 factors (Printed p. 430 / PDF p. 450); A_th definition "
        "9-21-3-3-3 (Printed p. 429 / PDF p. 449)"
    ),
    symbolic_formula=(
        "l_dh = (psi_e*psi_r*psi_o*psi_c / lambda) * (0.043 * f_y / "
        "sqrt(min(sqrt(f'c),8.3)**2)) * d_b^1.5, >= max(8*d_b, 150 mm)"
    ),
    description=(
        "Development length of deformed bars anchored with a standard hook in "
        "tension, Clause 9-21-3-3-1-الف: l_dh = [psi_e*psi_r*psi_o*psi_c/lambda] "
        "* (0.043*f_y/sqrt(f'c)) * d_b^1.5 per Eq. (9-21-3); minimum "
        "max(8*d_b, 150 mm) (3-3-1-ب). Table 9-21-5 factors (9-21-3-3-2): "
        "psi_e = 1.2 (epoxy/dual-coated) / 1.0 (uncoated/galvanized); "
        "psi_r = 1.0 (d_b <= 34 mm AND A_th >= 0.40*A_hs AND anchored-bar "
        "spacing > 6*d_b), else 1.6; psi_o = 1.0 (d_b <= 34 mm AND anchored "
        "in a column core AND side cover normal to hook plane > 65 mm or "
        "> 6*d_b), else 1.25; psi_c = f'c/105 + 0.6 (f'c < 42 MPa) / 1.0. "
        "A_th is the total area of enclosing ties/hoops per 9-21-3-3-3 "
        "(length >= 0.75*l_dh from the hook bend; tie placement zones of "
        "3-3-3-الف/ب and the cover < 65 mm enclosure of 3-3-4 are placement "
        "requirements recorded for traceability, not computed by this "
        "length evaluator). Hooks/heads never develop bars in compression "
        "(9-21-3-1-3). Excess-reinforcement reduction is NOT permitted for "
        "hooked anchorage (9-21-3-9-2-ث). Visually verified 2026-10-05 "
        "(page-448/449/450 evidence JPGs). Applicability: tension anchorage "
        "with standard hooks (anchor geometry of Table 9-21-2 out of scope "
        "here). Required typed inputs (never assumed): bar_diameter_mm, "
        "yield_stress_mpa, concrete_strength_mpa, concrete_weight_class, "
        "coating_class, a_th_mm2, a_hs_mm2, anchored_bar_clear_spacing_mm, "
        "anchored_in_column_core, side_cover_normal_to_hook_plane_mm."
    ),
    execution_allowed=True,
    dependencies=(),
)

RULE_BG_DEV_LENGTH_HEADED_001 = RuleReference(
    rule_id="BG-DEV-LENGTH-HEADED-001",
    title="Mabhas 9 Development Length of Headed Deformed Bars in Tension",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=450,
    printed_page=430,
    clause_or_equation=(
        "Clause 9-21-3-4-1 (Printed p. 430-431 / PDF pp. 450-451); Eq. (9-21-4) "
        "9-21-3-4-2 (Printed p. 431 / PDF p. 451); Table 9-21-6 factors "
        "(Printed p. 432 / PDF p. 452)"
    ),
    symbolic_formula=(
        "l_dt = (psi_e*psi_c*psi_p*psi_o / lambda) * (0.032 * f_y / "
        "sqrt(min(sqrt(f'c),8.3)**2)) * d_b^1.5, >= max(8*d_b, 150 mm); "
        "limits: d_b <= 34, A_brg >= 4*A_b, normal-weight only, cover >= "
        "2*d_b, spacing >= 3*d_b"
    ),
    description=(
        "Development length of headed deformed bars in tension, Clause "
        "9-21-3-4-2-الف: l_dt = [psi_e*psi_c*psi_p*psi_o/lambda] * "
        "(0.032*f_y/sqrt(f'c)) * d_b^1.5 per Eq. (9-21-4); minimum "
        "max(8*d_b, 150 mm). Applicability limits of 9-21-3-4-1: bar "
        "diameter <= 34 mm (ب), bearing section of the head >= 4 * bar "
        "area (پ), normal-weight concrete only (ت), clear cover >= 2*d_b "
        "(ث), center-to-center spacing >= 3*d_b (ج). Table 9-21-6 factors "
        "(9-21-3-4-3): psi_e = 1.2 (epoxy/dual-coated) / 1.0 "
        "(uncoated/galvanized); psi_p = 1.0 (d_b <= 34 AND (anchored in a "
        "beam-column joint with A_tt >= 0.3*A_ts, A_tt per 9-21-3-4-4 "
        "within 8*d_b of head, OR anchorage connection with anchored-bar "
        "spacing > 6*d_b)), else 1.6; psi_o = 1.0 (anchored in a column "
        "core with side cover normal to head plane > 65 mm or > 6*d_b), "
        "else 1.25; psi_c = f'c/105 + 0.6 (f'c < 42 MPa) / 1.0. "
        "Excess-reinforcement reduction is NOT permitted for headed "
        "anchorage (9-21-3-9-2-ث); hooks/heads never develop bars in "
        "compression (9-21-3-1-3). Visually verified 2026-10-05 "
        "(page-450/451/452 evidence JPGs). Applicability: tension anchorage "
        "with headed bars meeting every 9-21-3-4-1 limit. Required typed "
        "inputs (never assumed): bar_diameter_mm, yield_stress_mpa, "
        "concrete_strength_mpa, concrete_weight_class, coating_class, "
        "head_bearing_area_mm2, concrete_cover_mm, bar_spacing_cc_mm, "
        "anchored_in_column_core, side_cover_normal_to_head_plane_mm, "
        "connection_class, a_tt_mm2/a_ts_mm2 (beam-column joints), "
        "anchored_bar_clear_spacing_mm."
    ),
    execution_allowed=True,
    dependencies=(),
)

RULE_BG_DEV_MECH_ANCHOR_001 = RuleReference(
    rule_id="BG-DEV-MECH-ANCHOR-001",
    title="Mabhas 9 Mechanical Anchorage of Deformed Bars in Tension",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=453,
    printed_page=433,
    clause_or_equation="Clause 9-21-3-5-1 (Printed p. 433 / PDF p. 453)",
    symbolic_formula=(
        "device/attachment provides f_y capability + design engineer approval "
        "+ approved test results for combined anchorage (no length equation "
        "given)"
    ),
    description=(
        "Clause 9-21-3-5-1: the use of any welded attachment or mechanical "
        "device capable of developing the yield strength f_y of the bar is "
        "permitted only with the design engineer's approval; combined "
        "anchorage (mechanical anchor plus development length between the "
        "critical section and the attachment/device) is permitted on the "
        "basis of approved test results. This evaluator enforces exactly "
        "this three-part gate: required typed inputs (never assumed) "
        "device_supplies_yield_capacity, designer_engineer_approved, and "
        "approved_test_results_present; any missing input is BLOCKED; any "
        "false input is a verifiable FAIL; all three true PASS (admissible "
        "mechanical anchorage). No anchorage length is computed — none is "
        "given by the verified clause and none is invented. Visually verified "
        "2026-10-05 (page-453 evidence JPG). Applicability: tension "
        "mechanical anchorage of deformed bars. Excess-reinforcement "
        "reduction is NOT applicable (9-21-3-9-2-ث)."
    ),
    execution_allowed=True,
    dependencies=(),
)

RULE_BG_DEV_WIRE_DEFORMED_001 = RuleReference(
    rule_id="BG-DEV-WIRE-DEFORMED-001",
    title="Mabhas 9 Development Length of Welded Deformed Wire Mesh in Tension",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=453,
    printed_page=433,
    clause_or_equation=(
        "Clause 9-21-3-6-1 & Eq. (9-21-5) (Printed p. 433 / PDF p. 453); "
        "Eq. (9-21-6-الف/ب) psi_w & 9-21-3-6-3/-4 routing (Printed p. 434 / "
        "PDF p. 454)"
    ),
    symbolic_formula=(
        "l_d = (psi_t*psi_e*psi_s*psi_w / (lambda*min((c_b+K_tr)/d_b,2.5))) * "
        "(0.90*f_y/sqrt(f'c)) * d_b, >= 200 mm; psi_w = max(min((f_y-240)/"
        "f_y,1.0), min(5*d_b/s,1.0)) with cross wire >= 50 mm in l_d, else 1.0"
    ),
    description=(
        "Development length of welded deformed-wire mesh in tension from the "
        "critical section, Clause 9-21-3-6-1-الف: l_d = [psi_t*psi_e*psi_s*"
        "psi_w/(lambda*((c_b+K_tr)/d_b))] * (0.90*f_y/sqrt(f'c)) * d_b per "
        "Eq. (9-21-5); minimum 200 mm (3-6-1-ب). Applicability: DEFORMED "
        "wires with d_b <= 16 mm; plain wire of any diameter, deformed wire "
        "> 16 mm, and galvanized mesh are routed to 9-21-3-7 (3-6-3/-4) and "
        "are NOT_APPLICABLE here. psi_t/psi_e/psi_s per 9-21-3-2-2 "
        "(psi_t*psi_e <= 1.7); for epoxy-coated welded-wire mesh psi_e MAY "
        "be taken 1.0 (explicit permission of 3-6-1). c_b and K_tr per "
        "9-21-3-2-1 (K_tr = 0 always permitted; index <= 2.5). psi_w "
        "(9-21-3-6-2): with at least one cross wire within l_d at >= 50 mm "
        "from the critical section, psi_w is the greater of (f_y-240)/f_y "
        "and 5*d_b/s, each capped at 1.0; with no cross wire in l_d or a "
        "cross wire at < 50 mm, psi_w = 1.0 (s = spacing of the anchored "
        "wires). Excess-reinforcement reduction permitted for the Eq. "
        "(9-21-5) case (9-21-3-9) with the 200 mm floor preserved. "
        "Visually verified 2026-10-05 (page-453/454 evidence JPGs). Required "
        "typed inputs (never assumed): bar_diameter_mm, yield_stress_mpa, "
        "concrete_strength_mpa, concrete_weight_class, wire_surface_class, "
        "epoxy_coated_psi_e_unit_permission (when epoxy), "
        "cross_wire_in_development, cross_wire_distance_from_critical_mm and "
        "anchored_wire_spacing_mm (when a cross wire is present), geometry "
        "cover/spacing inputs as BG-DEV-LENGTH-TENSION-001, apply_k_tr "
        "bundle of transverse inputs."
    ),
    execution_allowed=True,
    dependencies=(),
)

RULE_BG_DEV_WIRE_PLAIN_001 = RuleReference(
    rule_id="BG-DEV-WIRE-PLAIN-001",
    title="Mabhas 9 Development Length of Welded Plain Wire Mesh in Tension",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=454,
    printed_page=434,
    clause_or_equation=(
        "Clause 9-21-3-7-1 & Eq. (9-21-7) (Printed pp. 434-435 / PDF pp. "
        "454-455)"
    ),
    symbolic_formula=(
        "l_dt = (3.3 * f_y / (lambda*sqrt(f'c))) * (A_b / s); floors "
        "max(150 mm, s + 50 mm); >= 2 cross wires within l_dt"
    ),
    description=(
        "Development length of welded plain-wire mesh in tension from the "
        "critical section to the OUTERMOST cross wire, Clause 9-21-3-7-1-الف: "
        "l_dt = (3.3*f_y/(lambda*sqrt(f'c))) * (A_b/s) per Eq. (9-21-7), "
        "where s is the spacing of the anchored wires and A_b the wire "
        "cross-sectional area; minimum: the greater of 150 mm and s + 50 mm "
        "(3-7-1-ب); at least two cross wires must exist within l_dt in all "
        "cases — fewer than two is a verifiable FAIL. No psi factors apply "
        "to this equation. Excess-reinforcement reduction permitted "
        "(9-21-3-9) with both floors (150 mm and s+50 mm) preserved. "
        "Visually verified 2026-10-05 (page-454/455 evidence JPGs). "
        "Applicability: tension development of welded PLAIN wire mesh "
        "(also governs deformed wires > 16 mm and galvanized mesh per "
        "9-21-3-6-3/-4 routing). Required typed inputs (never assumed): "
        "bar_diameter_mm, anchored_wire_spacing_mm, yield_stress_mpa, "
        "concrete_strength_mpa, concrete_weight_class, "
        "cross_wires_in_development_length."
    ),
    execution_allowed=True,
    dependencies=(),
)

RULE_BG_DEV_COMPRESSION_001 = RuleReference(
    rule_id="BG-DEV-LENGTH-COMPRESSION-001",
    title="Mabhas 9 Development Length of Deformed Bars and Wires in Compression",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=455,
    printed_page=435,
    clause_or_equation="Clause 9-21-3-8-1 (Printed p. 435 / PDF p. 455)",
    symbolic_formula=(
        "l_dc = max{ (psi_r * 0.24 * f_y / (lambda*sqrt(f'c))) * d_b, "
        "0.043 * f_y * psi_r * d_b }, >= 200 mm; psi_r = 0.75 for the "
        "listed confinement classes else 1.0"
    ),
    description=(
        "Development length of deformed bars and wires in compression, "
        "Clause 9-21-3-8-1-الف: l_dc = max{ (psi_r*0.24*f_y/(lambda*"
        "sqrt(f'c)))*d_b , 0.043*f_y*psi_r*d_b }; minimum 200 mm "
        "(3-8-1-ب). psi_r = 0.75 for confinement by: a spiral (دورپیچ); a "
        "continuous circular tie with diameter > 6 mm at spacing < 100 mm; "
        "a wire tie (تنگ سیمی) with diameter > 12 mm at spacing < 100 mm "
        "[the exact Persian noun of this branch is VERIFY_PENDING per the "
        "source-verification record — the branch is deterministically "
        "BLOCKED, never executed]; or a دوریگر/دورگیر (confinement tie per "
        "Clause 9-21-6-4) at spacing < 100 mm; psi_r = 1.0 for all other "
        "cases. Hooks/heads never develop bars in compression (9-21-3-1-3). "
        "Excess-reinforcement reduction permitted (9-21-3-9) with the "
        "200 mm floor preserved; prohibited contexts (9-21-3-9-2) block the "
        "reduction. Visually verified 2026-10-05 (page-455 evidence JPG). "
        "Applicability: compression development of single deformed bars/"
        "wires. Required typed inputs (never assumed): bar_diameter_mm, "
        "yield_stress_mpa, concrete_strength_mpa, concrete_weight_class, "
        "confinement_tie_class (with confinement tie diameter/spacing where "
        "a class qualifies)."
    ),
    execution_allowed=True,
    dependencies=(),
)

# ============================================================================
# Phase 2F Stage E — Clause 9-21-4 Lap / Bearing Splices (docs/VERIFIED_RULES.md)
# Visually re-verified 2026-10-06 from phase2f-source-442-472 @ df8067a;
# footer-confirmed Printed pp. 436-441 / PDF pp. 456-461.
# ============================================================================

RULE_BG_DEV_LAP_APPLIC_001 = RuleReference(
    rule_id="BG-DEV-LAP-APPLIC-001",
    title="Mabhas 9 Bar-Splice Methods and Lap Diameter Applicability",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=456,
    printed_page=436,
    clause_or_equation=(
        "Clause 9-21-4-1-1 & 9-21-4-1-2 (Printed p. 436 / PDF p. 456); "
        "9-21-4-1-2-ب (Printed p. 437 / PDF p. 457)"
    ),
    symbolic_formula=(
        "methods in {lap, bearing, welded, mechanical}; lap permitted "
        "(tension & compression) for d_b <= 34 mm; compression lap of a "
        "<= 42 mm bar to a <= 34 mm bar"
    ),
    description=(
        "General Clause 9-21-4-1: bar splices are permitted by one of four "
        "methods (9-21-4-1-1: lap / bearing / welded / mechanical); a lap "
        "splice is permitted, in tension and compression, for bars with "
        "diameter d_b <= 34 mm (9-21-4-1-2-الف), and in compression a lap "
        "splice of a bar of maximum diameter 42 mm to a bar of diameter "
        "<= 34 mm is permitted with the length governed by 9-21-4-5-2 "
        "(9-21-4-1-2-ب). Visually re-verified 2026-10-06 (page-456/457 "
        "evidence JPGs). Applicability: all bar splices (the diameter limit "
        "is lap-specific). Required typed inputs (never assumed): "
        "splice_method, bar_stress_action (for lap), bar_diameter_mm, "
        "larger_bar_diameter_mm (optional, compression different-diameter "
        "case). Missing -> BLOCKED; malformed -> INVALID_INPUT; a lap with "
        "d_b > 34 mm in tension (or outside the compression limits) -> FAIL."
    ),
    execution_allowed=True,
    dependencies=(),
)

RULE_BG_DEV_LAP_SPACING_001 = RuleReference(
    rule_id="BG-DEV-LAP-SPACING-001",
    title="Mabhas 9 Contact-Lap Transverse Centre-to-Centre Spacing",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=457,
    printed_page=437,
    clause_or_equation="Clause 9-21-4-1-4 (Printed p. 437 / PDF p. 457)",
    symbolic_formula="s_transverse <= min(lap_length / 5, 150 mm)",
    description=(
        "For a contact lap splice in flexural members, the transverse "
        "centre-to-centre spacing of the spliced bars shall not exceed one "
        "fifth of the lap length and 150 mm (Clause 9-21-4-1-4). Visually "
        "re-verified 2026-10-06 (page-457 evidence JPG). Applicability: "
        "contact lap splices in flexural members. Required typed inputs "
        "(never assumed): lap_length_mm, "
        "transverse_center_to_center_spacing_mm. Missing -> BLOCKED; "
        "malformed -> INVALID_INPUT; spacing above min(lap/5, 150 mm) -> FAIL."
    ),
    execution_allowed=True,
    dependencies=(),
)

RULE_BG_DEV_LAP_TENSION_001 = RuleReference(
    rule_id="BG-DEV-LAP-TENSION-001",
    title="Mabhas 9 Tension Lap Splice Length",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=457,
    printed_page=437,
    clause_or_equation="Clause 9-21-4-2-1 (Printed p. 437 / PDF p. 457)",
    symbolic_formula=(
        "l_st = 1.3*l_d (type B); l_st = 1.0*l_d (type A) only if provided "
        ">= 2*required AND <= 1/2 of provided spliced; l_st >= 300 mm"
    ),
    description=(
        "Tension lap splice length l_st of deformed bars/wires: general "
        "(type B) l_st = 1.3*l_d; reduced (type A) l_st = 1.0*l_d only when "
        "the reinforcement provided within the lap length is at least 2x the "
        "required AND at most half of the provided reinforcement is spliced "
        "within the lap length (Clause 9-21-4-2-1); minimum l_st = 300 mm. "
        "l_d is the tension development length per 9-21-4-2-1-1 (Clause "
        "9-21-3-1) and is a caller-provided VERIFIED value — never computed "
        "here (missing l_d -> BLOCKED). The excess-reinforcement development "
        "reduction of 9-21-3-9 is NOT applied (9-21-4-1-5). Visually "
        "re-verified 2026-10-06 (page-457 evidence JPG). Applicability: "
        "tension lap splices of bars with d_b <= 34 mm (9-21-4-1-2). Required "
        "typed inputs (never assumed): development_length_mm, "
        "tension_lap_class; as_provided_over_required_ratio and "
        "fraction_of_provided_bars_spliced required for type A. Type A with "
        "unmet conditions -> FAIL."
    ),
    execution_allowed=True,
    dependencies=(),
)

RULE_BG_DEV_LAP_TENSION_DIFFDIA_001 = RuleReference(
    rule_id="BG-DEV-LAP-TENSION-DIFFDIA-001",
    title="Mabhas 9 Different-Diameter Tension Lap Splice Length",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=458,
    printed_page=438,
    clause_or_equation="Clause 9-21-4-2 (different diameters) (Printed p. 438 / PDF p. 458)",
    symbolic_formula=(
        "l_s >= max(l_d for the larger bar, l_st for the smaller bar)"
    ),
    description=(
        "When a tension lap splice joins bars of different diameters, the "
        "lap length l_s shall not be less than either the development length "
        "l_d for the larger bar or the tension lap length l_st for the "
        "smaller bar (Clause 9-21-4-2). Both governing lengths are "
        "caller-provided VERIFIED values (Stage C l_d; Clause 9-21-4-2-1 "
        "l_st) — never computed here (missing -> BLOCKED). Visually "
        "re-verified 2026-10-06 (page-458 evidence JPG). Applicability: "
        "tension lap splices of different-diameter bars (d_b <= 34 mm per "
        "9-21-4-1-2, checked by BG-DEV-LAP-APPLIC-001). Required typed "
        "inputs (never assumed): development_length_larger_bar_mm, "
        "tension_lap_length_smaller_bar_mm."
    ),
    execution_allowed=True,
    dependencies=(),
)

RULE_BG_DEV_LAP_COMPRESSION_001 = RuleReference(
    rule_id="BG-DEV-LAP-COMPRESSION-001",
    title="Mabhas 9 Compression Lap Splice Length",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=459,
    printed_page=439,
    clause_or_equation="Clause 9-21-4-5-1 (Printed p. 439 / PDF p. 459)",
    symbolic_formula=(
        "l_sc = 0.071*f_y*d_b (f_y <= 420 MPa); l_sc = (0.13*f_y - 24)*d_b "
        "(f_y > 420 MPa); l_sc >= 300 mm; d_b <= 34 mm"
    ),
    description=(
        "Compression lap splice length l_sc of deformed bars with diameter "
        "d_b <= 34 mm (Clause 9-21-4-5-1): l_sc = 0.071*f_y*d_b for "
        "f_y <= 420 MPa, and l_sc = (0.13*f_y - 24)*d_b for f_y > 420 MPa; "
        "minimum l_sc = 300 mm. Visually re-verified 2026-10-06 (page-459 "
        "evidence JPG). Applicability: compression lap splices of bars with "
        "d_b <= 34 mm (d_b > 34 mm -> NOT_APPLICABLE, use the "
        "different-diameter compression lap of 9-21-4-5-2 for the smaller "
        "bar). Required typed inputs (never assumed): bar_diameter_mm, "
        "yield_stress_mpa. Missing -> BLOCKED; malformed -> INVALID_INPUT."
    ),
    execution_allowed=True,
    dependencies=(),
)

RULE_BG_DEV_LAP_COMPRESSION_DIFFDIA_001 = RuleReference(
    rule_id="BG-DEV-LAP-COMPRESSION-DIFFDIA-001",
    title="Mabhas 9 Different-Diameter Compression Lap Splice Length",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=460,
    printed_page=440,
    clause_or_equation="Clause 9-21-4-5-2 (Printed p. 440 / PDF p. 460)",
    symbolic_formula=(
        "l_s >= max(l_dc for the larger bar per 9-21-3-8, l_sc for the "
        "smaller bar per 9-21-4-5-1)"
    ),
    description=(
        "When a compression lap splice joins bars of different diameters, "
        "the lap length shall not be less than either the compression "
        "development length l_dc for the larger bar (per Clause 9-21-3-8) or "
        "the compression lap length l_sc for the smaller bar (per Clause "
        "9-21-4-5-1) (Clause 9-21-4-5-2). Both governing lengths are "
        "caller-provided VERIFIED values (Stage C l_dc; Clause 9-21-4-5-1 "
        "l_sc) — never computed here (missing -> BLOCKED). Visually "
        "re-verified 2026-10-06 (page-460 evidence JPG). Applicability: "
        "compression lap splices of different-diameter bars. Required typed "
        "inputs (never assumed): compression_dev_length_larger_bar_mm, "
        "compression_lap_length_smaller_bar_mm."
    ),
    execution_allowed=True,
    dependencies=(),
)

RULE_BG_DEV_SPLICE_BEARING_001 = RuleReference(
    rule_id="BG-DEV-SPLICE-BEARING-001",
    title="Mabhas 9 Bearing Splice of Compression-Only Bars",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFIED,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=460,
    printed_page=440,
    clause_or_equation="Clause 9-21-4-6-1..-6-3 (Printed p. 440 / PDF p. 460)",
    symbolic_formula=(
        "compression-only bars; ends cut perpendicular; coaxial; confined "
        "member; end-face deviation <= 5 deg; axial misalignment <= 3 deg"
    ),
    description=(
        "Bearing splice of bars under compression alone (Clause 9-21-4-6): "
        "force transfer by bearing between two bars whose ends are cut "
        "perpendicular to the bar axis, the two spliced bars coaxial (e.g. "
        "via a ring) (9-21-4-6-1); permitted only in members with "
        "confinement (خاموت: tied / spiral / دورگیر) (9-21-4-6-2); the bar "
        "ends must lie on a flat surface perpendicular to the bar axis with "
        "a maximum end-face deviation of 5 degrees, and the axial "
        "misalignment of the two bars must not exceed 3 degrees (9-21-4-6-3; "
        "the 5 deg value refines an earlier 1.5 deg reading). Visually "
        "re-verified 2026-10-06 (page-460 evidence JPG). Applicability: "
        "bearing splices of compression-only bars; this rule checks "
        "geometry/applicability only and does not transfer force. Required "
        "typed inputs (never assumed): bars_compression_only, "
        "ends_cut_perpendicular, bars_coaxial, member_has_confinement, "
        "end_face_deviation_deg, axial_misalignment_deg. Missing -> BLOCKED; "
        "malformed -> INVALID_INPUT; any unmet condition -> FAIL."
    ),
    execution_allowed=True,
    dependencies=(),
)

RULE_BG_DEV_LAP_WIRE_DEFORMED_PENDING = RuleReference(
    rule_id="BG-DEV-LAP-WIRE-DEFORMED-PENDING",
    title="Welded Deformed-Wire Mesh Tension Lap Splice (PENDING)",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFY_PENDING,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=458,
    printed_page=438,
    clause_or_equation="Clause 9-21-4-3-1..-3-4 (Printed p. 438 / PDF p. 458)",
    symbolic_formula="UNAVAILABLE (execution blocked)",
    description=(
        "Lap splice of welded deformed-wire reinforcement mesh in tension "
        "(Clause 9-21-4-3): l_sd >= max(1.3*l_d, 200 mm) with l_d per "
        "9-21-4-2-1-الف, plus outer cross-wire overlap >= 50 mm and all "
        "wires deformed with d <= 20 mm; unmet conditions route to 9-21-4-2 "
        "or 9-21-4-4, and galvanized welded deformed wire routes to 9-21-4-4."
    ),
    execution_allowed=False,
    blocked_reason=(
        "Execution BLOCKED: Clause 9-21-4-3 depends on National Building "
        "Regulations Chapter 9-4 welded-wire steel specifications (incl. "
        "9-4-8), whose pages are out of the verified window (VERIFY_PENDING), "
        "and its branch conditions reference the plain-wire clause 9-21-4-4 "
        "(unresolved 9-21-4-4-1-ب disjunct). No formula/number is executed."
    ),
    dependencies=(),
)

RULE_BG_DEV_LAP_WIRE_PLAIN_PENDING = RuleReference(
    rule_id="BG-DEV-LAP-WIRE-PLAIN-PENDING",
    title="Welded Plain-Wire Mesh Tension Lap Splice (PENDING)",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFY_PENDING,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=459,
    printed_page=439,
    clause_or_equation="Clause 9-21-4-4-1 (Printed p. 439 / PDF p. 459)",
    symbolic_formula="UNAVAILABLE (execution blocked)",
    description=(
        "Lap splice of welded plain-wire reinforcement mesh in tension "
        "(Clause 9-21-4-4): l_s >= max(1.5*l_d per 9-21-3-7-1-الف; "
        "cross-wire spacing + 50 mm, و یا 150 mm). The 9-21-4-4-1-ب branch "
        "carries the unresolved «و یا» disjunct and is recorded verbatim but "
        "NOT interpreted and NOT executed."
    ),
    execution_allowed=False,
    blocked_reason=(
        "Execution BLOCKED: the 9-21-4-4-1-ب «و یا» disjunct "
        "(«فاصله‌ی بین سیم‌های عمود بر امتداد وصله به علاوه‌ی ۵۰ میلی‌متر، "
        "و یا ۱۵۰ میلی‌متر») leaves the governing combination undetermined "
        "(VERIFY_PENDING; recorded verbatim in the source-verification matrix "
        "§4D.3), and the clause depends on Chapter 9-4 welded-wire steel "
        "specifications (out of window). No interpretation or execution."
    ),
    dependencies=(),
)

RULE_BG_DEV_SPLICE_WELDED_MECH_PENDING = RuleReference(
    rule_id="BG-DEV-SPLICE-WELDED-MECH-PENDING",
    title="Welded and Mechanical Bar Splices (PENDING)",
    category=RuleCategory.CODE_RULE,
    status=VerificationStatus.VERIFY_PENDING,
    jurisdiction=JurisdictionMode.MABHAS_9_COMPLIANCE,
    source_document=SOURCE_MABHAS_9,
    pdf_page=460,
    printed_page=440,
    clause_or_equation=(
        "Clause 9-21-4-7-1..-7-8 (Printed pp. 440-441 / PDF pp. 460-461)"
    ),
    symbolic_formula="UNAVAILABLE (execution blocked)",
    description=(
        "Welded and mechanical splices of deformed bars in tension and "
        "compression (Clause 9-21-4-7): welded splices mainly for "
        "d_b >= 20 mm (9-21-4-7-1/-2); welding must satisfy National "
        "Building Regulations Chapter 10 (9-21-4-7-3); mechanical splices "
        "transfer force by bearing/friction/coupler and develop 1.25*f_y "
        "(9-21-4-7-4..-6); adjacent welded/mechanical splices in tension "
        "members staggered >= 750 mm (9-21-4-7-7/-8)."
    ),
    execution_allowed=False,
    blocked_reason=(
        "Execution BLOCKED: Clause 9-21-4-7-3 requires welding to satisfy "
        "National Building Regulations Chapter 10, whose pages are out of "
        "the verified window (VERIFY_PENDING), and the mechanical-splice "
        "strength-transfer coefficient glyph was not independently "
        "re-confirmed. No formula/number is executed."
    ),
    dependencies=(),
)


_ALL_RULES_TUPLE: Tuple[RuleReference, ...] = (
    # Verified Mabhas 9 rules
    RULE_BG_FLEX_MIN_001,
    RULE_BG_FLEX_STRESS_BLOCK,
    RULE_BG_FLEX_STRAIN_LIMIT,
    RULE_BG_FLEX_PHI_FACTOR,
    RULE_BG_FLEX_RECT_SINGLY_001,
    RULE_BG_FLEX_TBEAM_B_EFF_001,
    RULE_BG_DETAIL_TRANS_DIA_001,
    RULE_BG_DETAIL_COMP_LAT_001,
    RULE_BG_DETAIL_LONG_SPACING_001,
    RULE_BG_DETAIL_LAYER_SPACING_001,
    RULE_BG_DETAIL_COVER_001,
    RULE_BG_DETAIL_BUNDLE_001,
    RULE_BG_DETAIL_BUNDLE_002,
    RULE_BG_DETAIL_BUNDLE_003,
    RULE_BG_DETAIL_BUNDLE_004,
    RULE_BG_DETAIL_BUNDLE_005,
    RULE_BG_DETAIL_BUNDLE_006,
    RULE_BG_DETAIL_BUNDLE_007,
    RULE_BG_DETAIL_BUNDLE_008,
    RULE_BG_DEV_LENGTH_TENSION_001,
    RULE_BG_DEV_LENGTH_TENSION_TABLE_001,
    RULE_BG_DEV_LENGTH_HOOKED_001,
    RULE_BG_DEV_LENGTH_HEADED_001,
    RULE_BG_DEV_MECH_ANCHOR_001,
    RULE_BG_DEV_WIRE_DEFORMED_001,
    RULE_BG_DEV_WIRE_PLAIN_001,
    RULE_BG_DEV_COMPRESSION_001,
    RULE_BG_DEV_LAP_APPLIC_001,
    RULE_BG_DEV_LAP_SPACING_001,
    RULE_BG_DEV_LAP_TENSION_001,
    RULE_BG_DEV_LAP_TENSION_DIFFDIA_001,
    RULE_BG_DEV_LAP_COMPRESSION_001,
    RULE_BG_DEV_LAP_COMPRESSION_DIFFDIA_001,
    RULE_BG_DEV_SPLICE_BEARING_001,
    RULE_BG_SHEAR_PHI_001,
    RULE_BG_SHEAR_VC_001,
    RULE_BG_SHEAR_VS_001,
    RULE_BG_SHEAR_VS_MAX_001,
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
    RULE_BG_FLEX_RECT_DOUBLY_001,
    RULE_BG_FLEX_TBEAM_CAP_001,
    RULE_BG_FLEX_LBEAM_CAP_001,
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
    RULE_BG_DEV_LAP_WIRE_DEFORMED_PENDING,
    RULE_BG_DEV_LAP_WIRE_PLAIN_PENDING,
    RULE_BG_DEV_SPLICE_WELDED_MECH_PENDING,
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
