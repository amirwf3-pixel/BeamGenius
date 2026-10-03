# BeamGenius

Deterministic reinforced-concrete beam engineering core governed by the **Iranian National Building Regulations (Mabhas 9)**.

---

## Source Hierarchy

1. **Davood Mostofinejad, *Reinforced Concrete Structures*, Vol. 1**
   - Primary engineering reference for methodology, calculation logic, design procedures, and worked benchmark examples.
2. **Iranian National Building Regulations — Mabhas 9**
   - Governing authority for mandatory Iranian code requirements, limits, applicability conditions, exceptions, and detailing rules.
3. **Conflict & Authority Policy**
   - Where Mostofinejad Vol. 1 and Mabhas 9 differ on a mandatory Iranian code requirement, **Mabhas 9 governs**.
   - `docs/VERIFIED_RULES.md` is authoritative over `docs/DESIGN_RULES.md`.
   - OCR text is a search/navigation aid only and never an executable engineering source by itself.

---

## Phase 1 Scope

Phase 1 implements the deterministic engineering core, rule registry, central gatekeeper, traceability layer, mathematical rebar catalog utility, and isolated textbook reference regression suite.

### Production Mabhas 9 Compliance Rules (`JurisdictionMode.MABHAS_9_COMPLIANCE`)

Only rules with `Status = VERIFIED` and `Type = CODE_RULE` in `docs/VERIFIED_RULES.md` execute in `MABHAS_9_COMPLIANCE`:

| Rule ID | Title | Mabhas 9 Clause & Page |
| :--- | :--- | :--- |
| `BG-FLEX-MIN-001` | Minimum Flexural Reinforcement | Clause 9-11-5-1-1 / 9-11-5-1-2 (Waiver: 9-11-5-1-3), PDF p. 220, Printed p. 199 |
| `BG-FLEX-STRESS-BLOCK` | Equivalent Rectangular Compression Stress-Block Parameters ($\alpha_0$, $\beta_1$, $a = \beta_1 c$) | Clause 9-8-2-2-6, PDF pp. 22–23, Printed pp. 113–114 |
| `BG-FLEX-STRAIN-LIMIT` | Flexural Strain Compatibility & Tension-Controlled Beam Ductility Limit ($\varepsilon_{cu} = 0.003$, $\varepsilon_t \ge \varepsilon_{ty} + 0.003$) | Clauses 9-8-2-1-1, 9-8-2-2-3, 9-11-2-3, 9-7-4-2, PDF pp. 16–22, 209 |
| `BG-FLEX-PHI-FACTOR` | Flexural Strength Reduction Factor $\phi$ | Clause 9-7-4-2..9-7-4-4 & Table 9-7-2, PDF pp. 16–18, Printed pp. 107–109 |
| `BG-FLEX-RECT-SINGLY-001` | Rectangular Singly-Reinforced Beam Flexural Resistance ($\phi M_n \ge M_u$) | Clauses 9-8-1-4, 9-8-2-2, 9-7-4, 9-11-2-3, PDF pp. 16–23, 209 |
| `BG-FLEX-TBEAM-B-EFF-001` | Non-Prestressed T-Beam and L-Beam Effective Compression Flange Width ($b_f$) | Clauses 9-6-3-3-1, 9-6-3-3-2, 9-11-2-5 & Table 9-6-1, Printed p. 91 |
| `BG-DETAIL-TRANS-DIA-001` | Minimum Transverse Reinforcement Diameter ($d_b \le 32 \Rightarrow 10$ mm; $d_b \ge 36$ or bundled $\Rightarrow 12$ mm; $32 < d_b < 36$ blocked) | Clause 9-11-6-5-11, PDF p. 228 |
| `BG-DETAIL-COMP-LAT-001` | Compression Reinforcement Lateral Support Spacing ($s_c \le \min(16 d_b, 48 d_{bt}, b_{\min})$) | Clause 9-11-6-5-12, PDF p. 229 |
| `BG-SHEAR-PHI-001` | Shear Strength Reduction Factor $\phi = 0.75$ and $\phi V_n \ge V_u$ | Clause 9-7-4-1, Table 9-7-2 (Row 2), Eq. (9-8-1-ب), Eq. (9-8-8), PDF pp. 128–131, 140, Printed pp. 107–112, 119 |
| `BG-SHEAR-VC-001` | Concrete One-Way Shear Resistance $V_c$ | Clauses 9-8-4-4-1..9-8-4-4-5, Eqs. (9-8-12-الف/ب), (9-8-13), (9-8-14), 9-8-4-2-2, Tables 9-3-1 & 9-3-2, PDF pp. 76–77, 140–142, Printed pp. 55–56, 119–121 |
| `BG-SHEAR-VS-001` | Transverse Reinforcement Shear Resistance $V_s$ (Vertical & Inclined Stirrups) | Clauses 9-8-4-2-3, 9-4-8-5, 9-8-4-5-1/3/4, Eqs. (9-8-15), (9-8-16), (9-8-17), PDF pp. 89–90, 140–144, Printed pp. 68–69, 119, 121–123 |
| `BG-SHEAR-VS-MAX-001` | Maximum Shear / Web-Crushing Limit ($V_{s,\max}$, $V_{u,\max}$) | Clause 9-8-4-1-3, Eq. (9-8-9), PDF p. 140, Printed p. 119 |
| `BG-SHEAR-MIN-001` | Minimum Shear Reinforcement & Table 9-11-2 Exceptions | Clause 9-11-5-2 & Table 9-11-2, PDF p. 221 |
| `BG-SHEAR-SPACING-001` | Maximum Stirrup Spacing ($s$ and $s_t$) | Clause 9-11-6-5-3, PDF p. 227 |

### Isolated Reference / Textbook Methodology (`JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY`)

Permitted verified equations from `docs/MOSTOFINEJAD_FORMULA_REGISTRY.md` (`BG-MOST-5-46`, `5-47`, `5-48A`, `5-48B`, `5-49`, `5-50`, `5-54`, `5-55`, `5-56`, `5-61`) are isolated in `beamgenius.reference` solely for reproducing Mostofinejad Vol. 1 methodology and worked examples (`Example 5-5` and `Example 5-6`). Calling any reference equation under `MABHAS_9_COMPLIANCE` returns `JURISDICTION_BLOCKED`.

---

## Jurisdiction Modes

- `JurisdictionMode.MABHAS_9_COMPLIANCE`: Production Iranian code compliance mode. Executes only verified `CODE_RULE`s (`BG-FLEX-MIN-001`, `BG-FLEX-STRESS-BLOCK`, `BG-FLEX-STRAIN-LIMIT`, `BG-FLEX-PHI-FACTOR`, `BG-FLEX-RECT-SINGLY-001`, `BG-FLEX-TBEAM-B-EFF-001`, `BG-DETAIL-TRANS-DIA-001`, `BG-DETAIL-COMP-LAT-001`, `BG-SHEAR-PHI-001`, `BG-SHEAR-VC-001`, `BG-SHEAR-VS-001`, `BG-SHEAR-VS-MAX-001`, `BG-SHEAR-MIN-001`, and `BG-SHEAR-SPACING-001`).
- `JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY`: Isolated reference methodology mode for textbook verification. Never implies Iranian Mabhas 9 code compliance.

---

## Blocked Workflows & Current Limitations

Until primary source pages are visually verified and promoted to `docs/VERIFIED_RULES.md`, the following workflows deterministically return `EvaluationOutcome.UNVERIFIED_RULE_BLOCKED` with full diagnostic trace steps:

- **Doubly-Reinforced & Flanged (T/L) Flexural Resistance** (`BG-FLEX-RECT-DOUBLY-001`, `BG-FLEX-TBEAM-CAP-001`, `BG-FLEX-LBEAM-CAP-001`, `BG-MABHAS9-FLEX-CAP-BLOCKED`)
- **Unverified Special Shear Branches**: bent-up longitudinal bars (Eqs. 9-8-18), circular hoops/spirals, web openings, variable-depth haunches, one-way joists (Table 9-11-2 Ex. 4), seismic capacity-design shear (φ = 0.60 / 0.85, Chapter 9-20), shear-torsion interaction, and torsion
- **Legacy Full Shear Capacity Sentinels** (`BG-SHEAR-CAP-BLOCKED`, `BG-SHEAR-VC-BLOCKED`, `BG-SHEAR-VS-DEMAND-BLOCKED`, `BG-SHEAR-VS-MAX-BLOCKED`) — retained as explicit blocked sentinels; Phase 2C production one-way shear capacity runs through the verified rules `BG-SHEAR-PHI-001`, `BG-SHEAR-VC-001`, `BG-SHEAR-VS-001`, and `BG-SHEAR-VS-MAX-001`
- **T/L Section Flange-in-Tension Effective Width** (under `BG-FLEX-MIN-001`)
- **Table 9-11-2 Steel-Fiber RC Exception without Explicit $\phi$** and **One-Way Joist Exception** (under `BG-SHEAR-MIN-001`)
- **Non-Bundled Transverse Diameter Interval $32 < d_b < 36$ mm** (under `BG-DETAIL-TRANS-DIA-001`) — no source-verified interpolation; returns `UNVERIFIED_RULE_BLOCKED` (`UNSUPPORTED_CONFIGURATION`)
- **Longitudinal Bar Clear Spacing, Layer Spacing, Concrete Cover, Development Length ($L_d$), Bar Cutoff, Integrity Reinforcement, Column Continuity, Anchorage, Skin Reinforcement, and Torsion**
- **Mostofinejad Blocked Equations**: `BG-MOST-5-44`, `BG-MOST-5-45`, `BG-MOST-5-51` (`700`-vs-`600` review flag), `BG-MOST-5-52`, `BG-MOST-5-53`, `BG-MOST-5-57`, `BG-MOST-5-58`, `BG-MOST-5-59`, `BG-MOST-5-60`, and `BG-MOST-5-62`
- **Rebar Catalog Utility (`beamgenius.rebar`)**: Computes mathematical bar areas ($A_b = \pi d_b^2 / 4$) and enumerates area-matching combinations only; every candidate exposes `constructability_verified = False`.

---

## Running Tests & Static Type Checks

Run the test suite:

```bash
pytest
```

Run strict static type checking:

```bash
mypy --strict src
```
