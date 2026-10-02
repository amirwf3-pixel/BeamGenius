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
| `BG-SHEAR-MIN-001` | Minimum Shear Reinforcement & Table 9-11-2 Exceptions | Clause 9-11-5-2 & Table 9-11-2, PDF p. 221 |
| `BG-SHEAR-SPACING-001` | Maximum Stirrup Spacing ($s$ and $s_t$) | Clause 9-11-6-5-3, PDF p. 227 |

### Isolated Reference / Textbook Methodology (`JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY`)

Permitted verified equations from `docs/MOSTOFINEJAD_FORMULA_REGISTRY.md` (`BG-MOST-5-46`, `5-47`, `5-48A`, `5-48B`, `5-49`, `5-50`, `5-54`, `5-55`, `5-56`, `5-61`) are isolated in `beamgenius.reference` solely for reproducing Mostofinejad Vol. 1 methodology and worked examples (`Example 5-5` and `Example 5-6`). Calling any reference equation under `MABHAS_9_COMPLIANCE` returns `JURISDICTION_BLOCKED`.

---

## Jurisdiction Modes

- `JurisdictionMode.MABHAS_9_COMPLIANCE`: Production Iranian code compliance mode. Executes only `BG-FLEX-MIN-001`, `BG-SHEAR-MIN-001`, and `BG-SHEAR-SPACING-001`.
- `JurisdictionMode.MOSTOFINEJAD_METHODOLOGY_ONLY`: Isolated reference methodology mode for textbook verification. Never implies Iranian Mabhas 9 code compliance.

---

## Blocked Workflows & Current Limitations

Until primary source pages are visually verified and promoted to `docs/VERIFIED_RULES.md`, the following workflows deterministically return `EvaluationOutcome.UNVERIFIED_RULE_BLOCKED` with full diagnostic trace steps:

- **Mabhas 9 Flexural Capacity / Resistance** (`BG-MABHAS9-FLEX-CAP-BLOCKED`)
- **Full Shear Capacity Design & Check** (`BG-SHEAR-CAP-BLOCKED`, `BG-SHEAR-VC-BLOCKED`, `BG-SHEAR-VS-DEMAND-BLOCKED`, `BG-SHEAR-VS-MAX-BLOCKED`)
- **T/L Section Flange-in-Tension Effective Width** (under `BG-FLEX-MIN-001`)
- **Table 9-11-2 Steel-Fiber RC Exception without Explicit $\phi$** and **One-Way Joist Exception** (under `BG-SHEAR-MIN-001`)
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
