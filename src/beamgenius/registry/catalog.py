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
