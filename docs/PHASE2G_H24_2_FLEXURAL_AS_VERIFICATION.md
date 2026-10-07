# H.24.2 Flexural As,req Source Verification

**BeamGenius — visual source verification of `BG-FLEX-RECT-REQ-AS-001`**

**Audit only. No implementation. No promotion. No registry change. No calculation-logic change.**

**FINAL DECISION: `REMAINS VERIFY_PENDING` — `execution_allowed=False`.**

---

## 0. Summary

The `phase2g-source-flexure/` package was received, checksum-verified (16/16 OK), and every
image inspected visually at up to 6× magnification. **The package does not contain the pages
required for the target rule.**

The filenames are **PDF page numbers**, not printed page numbers. Footer inspection establishes
a uniform **−20** offset: the ten Mabhas 9 images are **printed 87–94, 112, 179**, not printed
107–114, 132, 199. Nine of the ten pages are §9-6 (structural analysis) and §9-10 (slabs)
content. Exactly **one** page — printed 112 — is flexural, and it contains only the
**design inequality**, not the **resistance model**.

Consequently the Mabhas 9 flexural model (stress block α₀, β₁, strain compatibility, `a`/`c`
relations, `Mn`) — which the derivation must invert — is **not visually verified in this
package**, and the Mostofinejad pages supplied (printed 189–194) are a **different range** from
the ones the registry records for (5-46)/(5-47) (printed 200).

Per the governing rules — *"Do not promote a rule merely because a formula looks mathematically
reasonable"*, *"Do not invent missing assumptions, coefficients, symbols, phi factors, stress
blocks, or applicability limits"*, and *"Mabhas 9 wins over Mostofinejad if they conflict"* —
the only defensible outcome is **REMAINS VERIFY_PENDING with no implementation**.

---

## 1. Baseline and governance

| Item | Value |
| :-- | :-- |
| Branch | `arena/b9cd291a-beamgenius` |
| HEAD at audit entry | `f22ff45` (stale-boot artifact, 9th occurrence) |
| Recovery | `git fetch origin` → `git fetch --unshallow origin` → `git reset --mixed origin/arena/…` → `git checkout HEAD -- .` (non-destructive; no `--hard`, no amend, no rebase, no force-push) |
| HEAD at work start | **`7f2c6b1`** — *docs: add Phase 2G flexure source evidence* |
| `origin/main` | `df8067a750ffc7984c9dc5d80220ad9013503aa6` — untouched |
| Clone depth | deepened (`--unshallow`) locally; no branch, commit, tag or remote altered |

Governance applied, verbatim from the stage brief: Mabhas 9 (1399, 5th ed.) is the governing
source; Mostofinejad Vol. 1 is methodology/reference only; OCR is navigation only; visual
inspection of source-page images is mandatory; ACI/CSA/Eurocode may **not** substitute for
Mabhas 9; incomplete or ambiguous evidence keeps the rule `VERIFY_PENDING`.

---

## 2. Package integrity

| Field | Value |
| :-- | :-- |
| Path | `phase2g-source-flexure/` |
| Commit | `7f2c6b1` (also `bacfada` ancestry) |
| Branch | `arena/b9cd291a-beamgenius` |
| Contents | `Mabhas9/` 10 JPG · `Mostofinejad/` 6 JPG · `SHA256SUMS.txt` |
| Type | page-image evidence (no OCR substitutes) |
| Checksums | **16/16 verified** against `SHA256SUMS.txt` |
| Manifest quirk | `SHA256SUMS.txt` uses **Windows path separators** (`\`) and a BOM; paths already include the package root. Verified programmatically after normalisation. |
| Resolution | Mabhas 9 images 2480×3505 (300 dpi A4); Mostofinejad 2893×4094 (350 dpi A4) |

---

## 3. Verified printed page numbers (authoritative identity)

Footers were read directly from the page images at 6× magnification. **Every** Mabhas 9 page
carries its numeral centred at the bottom, just beneath the rule; **every** Mostofinejad page
carries its folio in the top corner.

### 3.1 Mabhas 9 — uniform offset **−20**

| File | Printed footer | Offset (printed − filename) | Chapter / section on the page |
| :-- | :-- | :-- | :-- |
| `page-107.jpg` | **۸۷** (87) | −20 | §9-6-4-4, §9-6-5-1 (تحلیل سیستمها) |
| `page-108.jpg` | **۸۸** (88) | −20 | §9-6-5-3-1-1, §9-6-5-3 |
| `page-109.jpg` | **۸۹** (89) | −20 | Table 9-6-2 (ممان اینرسی مؤثر) |
| `page-110.jpg` | **۹۰** (90) | −20 | §9-6-5-3-1-2-1, §9-6-5-4-1/-4-2 |
| `page-111.jpg` | **۹۱** (91) | −20 | §9-6-5-4-2-2-4, Eqs. (9-6-5)…(9-6-8) |
| `page-112.jpg` | **۹۲** (92) | −20 | §9-6-5-4-2-3, Eqs. (9-6-9), (9-6-11), (9-6-12) |
| `page-113.jpg` | **۹۳** (93) | −20 | §9-6-5-4-2-3-3, Eqs. (9-6-14)…(9-6-17) |
| `page-114.jpg` | **۹۴** (94) | −20 | Eq. (9-6-13), §9-6-5-4-4 |
| **`page-132.jpg`** | **۱۱۲** (112) | −20 | **§9-8 opening, §9-8-1-3, §9-8-1-4, §9-8-2-1** |
| `page-199.jpg` | **۱۷۹** (179) | −20 | §9-10-10-4/-5/-6, §9-10-10-9 (دالها) |

The offset is corroborated independently by three sources:

1. **Direct footer reading** of all ten images → exactly −20, no exceptions.
2. The **previously footer-verified** §9-21 evidence window: `page-462.jpg` = printed **۴۴۲** ⇒ −20.
3. `BG-FLEX-MIN-001`'s recorded attribution "PDF p. 220 / printed p. 199" ⇒ +21 ≈ +20.

**This is the first time the flexure package's page identity has been established by direct
footer inspection.** The offsets previously recorded in the project (`−91` for Phase 2B flexure,
`+21` for Phase 2B shear) are **both inconsistent with the actual document**; the corrected
uniform offset for this Mabhas 9 rendition is **−20**.

### 3.2 Mostofinejad — uniform offset **+11**

| File | Printed folio | Offset | Content |
| :-- | :-- | :-- | :-- |
| `mostofinejad_flex_base-200.jpg` | **۱۸۹** (189) | +11 | ρmax derivation, a_max/d_t = (3/7)β₁ (5-32), (5-33-الف/ب), (5-34), (5-35) |
| `mostofinejad_flex_base-201.jpg` | **۱۹۰** (190) | +11 | (5-36), (5-37); ACI 318-99 legacy ρmax discussion |
| `mostofinejad_flex_base-202.jpg` | **۱۹۱** (191) | +11 | §5-ب minimum steel; Mn & Mcr; **ρmin ≈ (1/7)√f′c/fy (5-38)** |
| `mostofinejad_flex_base-203.jpg` | **۱۹۲** (192) | +11 | **(5-39) As,min**, (5-40); **Example 5-1** statement |
| `mostofinejad_flex_base-204.jpg` | **۱۹۳** (193) | +11 | Example 5-1 solution: ρb = 0.0303, Mn = 331.03 kN·m, εt = 0.0067 → TC, φ = 0.9 |
| `mostofinejad_flex_base-205.jpg` | **۱۹۴** (194) | +11 | φMn = 297.9 kN·m; **Example 5-2** — transition zone, φ by interpolation |

**Registry cross-check.** `docs/MOSTOFINEJAD_FORMULA_REGISTRY.md` records (5-46)/(5-47) at
**PDF 211 / printed 200** ⇒ +11. The offset agrees; the **pages supplied are 189–194, not
200–205**. Equations (5-46) and (5-47) are therefore **not in this package**.

---

## 4. Clause-by-clause findings — Mabhas 9

### 4.1 The only flexural page: printed 112 (`page-132.jpg`)

**Visually verified content:**

| Element | Verified text / equation |
| :-- | :-- |
| Chapter heading | **۹-۸ ارزیابی مقاومت مقطع در خمش، بار محوری، برش- اصطکاک** |
| §9-8-1-3 | «رعایت ضوابط لازم این فصل برای همهی اعضای بتن آرمه است؛ مگر آن که عضو یا ناحیهای از عضو بر اساس مدلهای بست و بند که در پیوست ۹-پ۳ آمدهاند، طراحی شود.» |
| §9-8-1-4 | «طرح مقطع بتن آرمه طوری انجام میشود که بر اساس رابطهی عمومی (۹-۱-۱)، مقاومت طراحی، φSₙ، از مقاومت مورد نیاز، U، کمتر نباشد.» |
| **Eq. (9-8-1-الف)** | **φ Mₙ ≥ Mᵤ** |
| Eq. (9-8-1-ب) | φ Vₙ ≥ Vᵤ |
| Eq. (9-8-1-پ) | φ Tₙ ≥ Tᵤ |
| Eq. (9-8-1-ت) | φ Pₙ ≥ Pᵤ |
| Symbols paragraph | «Mₙ، Vₙ، Tₙ، Pₙ به ترتیب مقاومت خمشی اسمی، مقاومت برشی اسمی، مقاومت پیچشی اسمی و مقاومت فشاری اسمی مقطع» — nominal resistances per this chapter |
| Demand definitions | «Mᵤ، Vᵤ، Tᵤ، Pᵤ … مقاومتهای مورد نیاز … نیروهای محوری نهایی هستند که با تحلیل الاستیک سازه تحت بارهای ضریبدار به دست میآیند» — **factored** demands from elastic analysis |
| §9-8-2 | **مقاومت خمشی** (heading only) |
| §9-8-2-1 | **کلیات** (heading only — page ends here) |

**This is a genuine, first-time visual verification of the governing design inequality
`φMₙ ≥ Mᵤ` and of its clause number, equation number and page (printed 112).**

**What printed 112 does NOT contain** (it ends at the §9-8-2-1 heading): the general
assumptions, the equivalent rectangular stress block, α₀, β₁, the strain-compatibility
relation, the `a`/`c` geometry, or any expression for `Mₙ`.

### 4.2 The other nine Mabhas 9 pages

All are non-flexural and carry **no** flexural design content:

| Printed | Verified subject matter |
| :-- | :-- |
| 87 | §9-6-4-4 moment redistribution; §9-6-5-1 elastic first-order analysis |
| 88 | §9-6-5-3-1-1, §9-6-5-3 member stiffness properties |
| 89 | Table 9-6-2 effective moment of inertia Ie |
| 90 | §9-6-5-3-1-2-1, §9-6-5-4-1, §9-6-5-4-2 second-order effects |
| 91 | §9-6-5-4-2-2-4, Eqs. (9-6-5)…(9-6-8) effective stiffness |
| 92 | §9-6-5-4-2-3, Eqs. (9-6-9), (9-6-11), (9-6-12) moment magnification |
| 93 | §9-6-5-4-2-3-3, Eqs. (9-6-14)…(9-6-17) stability index / δs |
| 94 | Eq. (9-6-13) M₂,min = P_u(15 + 0.03h); §9-6-5-4-4 |
| 179 | §9-10-10-4/-5/-6, §9-10-10-9 slab strip moments |

**Discrepancy report (required by the brief):** nine of ten Mabhas 9 images are **not** the
expected printed pages. The intended pages are §9-7-4 (φ) and §9-8-2 (resistance model), which
under the verified −20 offset are **PDF 127–134 ≈ printed 107–114** — i.e. the filenames were
built by treating the *printed* targets as *PDF* indices. See §8.

---

## 5. Clause-by-clause findings — Mostofinejad (printed 189–194)

**Source:** Davood Mostofinejad, *Reinforced Concrete Structures* Vol. 1, Chapter 5
(«طراحی تیر تحت خمش — مفاهیم اساسی و مقاطع مستطیلی»). All 16 pages bear the `Prozhefa.com`
watermark; the copy is annotated (handwritten notes), which does not affect the printed text.

### 5.1 Equations visually verified

| Eq. | Verified content |
| :-- | :-- |
| (5-32) | a_max/d_t = εcu/(εcu+εt)·β₁ = (3/7)β₁ |
| (5-33-الف) | a = 0.003/(0.003+εt)·β·d |
| (5-33-ب) | a_b = 0.003/(0.003+εy)·β·d |
| (5-34) | ρ/ρ_b = a/a_b = (0.003+εy)/(0.003+εt) |
| (5-35) | **ρ_max = (600+f_y)/1400 · ρ_b** |
| (5-36) | ρ_max = 0.364 β₁ f′c/f_y |
| (5-37) | ρ_max = 0.364 β₁ (d_t/d)(f′c/f_y) |
| (5-38) | **ρ_min ≈ (1/7)√f′c/f_y** |
| **(5-39)** | **A_s,min = √f′c/(4f_y)·b_w·d ≥ 1.4/f_y·b_w·d** |
| (5-40) | ρ_min = √f′c/(4f_y) ≥ 1.4/f_y |
| §5-ب | M_n = ρ f_y b d²(1 − 0.59 ρ f_y/f′c); M_cr = f_r I_tr/(h − ȳ) |
| §5-ب | 3Φ30 → **A_s = 2121 mm²**, ρ = 0.0157 |

### 5.2 The supplied example, independently re-computed

**Example 5-1** (printed 193): b = 300 mm, d = 450 mm, 3Φ30, f_y = 400 MPa, f′c = 28 MPa.

| Quantity | Source prints | Re-computed here | Agreement |
| :-- | :-- | :-- | :-- |
| ρ | 0.0157 | 0.0157 (= 2121/135000) | **exact** |
| ρ_b = 0.85β₁(f′c/f_y)(600/(600+f_y)) | 0.0303 | 0.0303 | **exact** |
| M_n = ρbd²f_y(1−0.59ρf_y/f′c) | 331.03 kN·m | 331.22 kN·m | 0.06 % (rounded ρ) |
| a = A_sf_y/(0.85f′c b) | 118.8 mm | 118.8 mm | **exact** |
| c = a/β₁ | 139.8 mm | 139.8 mm | **exact** |
| ε_t = εcu(d_t−c)/c | 0.0067 | 0.0067 | **exact** |
| Regime | ε_t > 0.005 ⇒ **TC**, φ = 0.9 | confirmed | **exact** |
| φM_n | 297.9 kN·m | 298.1 kN·m | 0.07 % |

**Example 5-2** (printed 194): A_s = 2724 mm² ⇒ ρ = 0.0202 < ρ_b; M_n = 407.29 kN·m;
a = 152.6 mm; c = 179.5 mm; **ε_t = 0.00452** ⇒ *"از آن جا که 0.002 < ε_t < 0.005 است، مقطع در
ناحیهای انتقالی (بین کنترلکشش و فشارکنترل) قرار دارد؛ و φ را باید با درون یابی به دست آورد"*
— i.e. **φ by interpolation**; and ρ_max = 0.364β₁f′c/f_y = **0.0217**, a/d_t = 0.339 <
a_max/d_t = 0.364.

**All re-computed values agree.** The Mostofinejad model is internally consistent and its
worked examples reproduce exactly.

### 5.3 What these pages are — and are not

- They are an **explicitly ACI 318-based** flexure design methodology: the text says
  «آیین نامه ACI 318» repeatedly, uses the **0.85** stress-block coefficient, the **0.59**
  moment coefficient, ACI's **ρ_max = 0.75ρ_b** legacy / 0.364β₁f′c/f_y form, ACI's
  **ε_t = 0.005** tension-controlled threshold, and ACI's **φ = 0.9 / transition
  interpolation**.
- They contain **no** Mabhas 9 clause, no Mabhas 9 φ table, and no Mabhas 9 stress block.
- **(5-46) and (5-47) are not in this package** — the registry places them on printed 200
  (+11 ⇒ PDF 211), which was not supplied.
- Consequently the earlier open question about (5-46)/(5-47) being *section-sizing* rather than
  *As-for-fixed-b,d* **cannot be re-verified here**. What *is* now verified is the underlying
  coefficient: **0.59 is the rounded ACI value 1/(2×0.85) = 0.588235**, i.e. an implied
  α₀ = 1/(2×0.59) = **0.847458**, a **+0.30 %** departure from the exact 0.588235.

### 5.4 Mostofinejad's role under the governance hierarchy

Mostofinejad may **support methodology and cross-checking only**. It cannot supply the
governing model: it is ACI-derived, whereas the target rule is a `MABHAS_9_COMPLIANCE` rule.
Reusing its model — or the existing `reference/mostofinejad_ch5.solve_required_as` helper —
for `BG-FLEX-RECT-REQ-AS-001` would be **model substitution**, prohibited by the brief (§7) and
by the standing governance.

---

## 6. What is verified vs. what is missing

### 6.1 Verified in this stage (new)

| # | Item | Page | Status |
| :-- | :-- | :-- | :-- |
| 1 | §9-8 scope and heading structure | printed 112 | **VERIFIED_SOURCE** |
| 2 | §9-8-1-3 scope statement | printed 112 | **VERIFIED_SOURCE** |
| 3 | §9-8-1-4 design philosophy statement | printed 112 | **VERIFIED_SOURCE** |
| 4 | **Eq. (9-8-1-الف): φMₙ ≥ Mᵤ** | printed 112 | **VERIFIED_SOURCE** |
| 5 | Eqs. (9-8-1-ب/پ/ت) | printed 112 | **VERIFIED_SOURCE** |
| 6 | Mᵤ defined as **factored** demand from elastic analysis | printed 112 | **VERIFIED_SOURCE** |
| 7 | §9-8-2 / §9-8-2-1 headings; page terminates | printed 112 | **VERIFIED_SOURCE** |
| 8 | Flexure package page identity = printed, offset −20 | all 10 | **VERIFIED_SOURCE** |
| 9 | Mostofinejad printed 189–194 content, Eqs. (5-32)…(5-40) | 189–194 | **VERIFIED_SOURCE (methodology)** |
| 10 | Mostofinejad offset +11; (5-46)/(5-47) **not** supplied | 189–194 | **VERIFIED_SOURCE** |

### 6.2 MISSING — required to derive `As,req`

| # | Required source | Clause / equation | Correct page under the verified −20 offset | In package? |
| :-- | :-- | :-- | :-- | :-- |
| M1 | General flexural assumptions | §9-8-2-1-1, §9-8-2-2-1…−2-2-5 | PDF **133–134** (printed 113–114) | **NO** |
| M2 | Equivalent rectangular stress block: α₀, β₁ definitions | §9-8-2-2-6, §9-8-2-2-7, Eqs. (9-8-2), (9-8-3-الف), (9-8-3-ب), (9-8-4) | PDF **133–134** (printed 113–114) | **NO** |
| M3 | Strain compatibility εcu = 0.003, εt relation | §9-8-2-2-2/-2-2-3 | PDF **133–134** (printed 113–114) | **NO** |
| M4 | Nominal moment Mₙ expression | §9-8-2 (body) | PDF **133–134** (printed 113–114) | **NO** |
| M5 | **φ factor values and Table 9-7-2**, Eqs. (9-7-10-الف/ب) | §9-7-4-1…−4-4, Table 9-7-2 | PDF **127–129** (printed 107–109) | **NO** |
| M6 | Ductility / max-steel limit | §9-11-2-3 | PDF **152** (printed 132) | **NO** |
| M7 | **A_s,min** clauses and the 4/3 waiver | §9-11-5-1-1, −1-2, −1-3 | PDF **219** (printed 199) | **NO** |
| M8 | εcu value | §9-8-2-2-2 (and §9-4-8-4 for Es) | PDF 133–134 | **NO** |

*Only M8's companion `E_s = 200 000 MPa` is recorded from a previously verified stage; it is
not re-verified here.*

### 6.3 Consequence

`φMₙ ≥ Mᵤ` is verified. `Mₙ(A_s)` is **not**. The derivation `Mᵤ → A_s` requires exactly
`Mₙ(A_s)`, together with the φ model (M5), the applicability limit (M6) and the minimum-steel
floor (M7). **Three of the four pillars are absent, and the fourth is only a shell.**

---

## 7. Answers to the specific engineering questions

| Q | Question | Answer from verified evidence |
| :-- | :-- | :-- |
| A | Mabhas 9 provisions governing rectangular singly-reinforced flexural design | **PARTIAL.** §9-8-1-3/-4 and Eq. (9-8-1-الف) verified. The substantive provisions (§9-8-2-1, §9-8-2-2, §9-7-4, §9-11-2-3, §9-11-5) are **not in the package** |
| B | Exact stress/strain model | **NOT VERIFIABLE** — §9-8-2-2 assumptions absent |
| C | Exact concrete compression-block model | **NOT VERIFIABLE** — Eqs. (9-8-2), (9-8-3-الف/ب), (9-8-4) absent |
| D | Relationship between Mᵤ, A_s, f_y, f′c, b, d, a/c | **NOT VERIFIABLE** for Mabhas 9. Mostofinejad supplies the ACI form (verified, printed 191/193/194) — usable for cross-check only |
| E | φ factor and its conditions | **NOT VERIFIABLE** — §9-7-4 and Table 9-7-2 absent |
| F | Direct equation for A_s, or iteration/root-solving? | **NOT DETERMINABLE** from the supplied pages |
| G | Algebraic quadratic derived from the source | **NOT PERFORMABLE** — the source equations to be inverted are absent. (The algebra is already recorded in H.24 §7 as `DERIVED`; it remains untraceable to verified pages) |
| H | Is the smaller root necessarily governing? | **NOT PROVABLE from source here** — requires the verified tension-controlled/ductility limit (M5, M6) |
| I | Applicability limits | **NOT ESTABLISHED** — only the general §9-8-1-3 scope statement is verified |
| J | Must A_s,req be combined with A_s,min, and where from? | The requirement is plausible but **§9-11-5 is absent**; Mostofinejad's (5-39) is ACI-based and cannot supply it |
| K | Does the source support `As,design = max(As,flexure, As,min)`? | **NOT SUPPORTED BY VERIFIED EVIDENCE** |

---

## 8. Promotion gate

Applying the brief's §8 checklist verbatim:

| # | Condition | Result |
| :-- | :-- | :-- |
| 1 | Governing Mabhas 9 source visually verified | **FAIL** — only §9-8-1-4 verified; the model, φ, limits and A_s,min are absent |
| 2 | Exact clause/page references known | **PARTIAL→FAIL** — for the rule's *substantive* clauses: unknown |
| 3 | Equations and symbols unambiguous | **FAIL** — α₀, β₁, `a`, `Mₙ` unverified for Mabhas 9 |
| 4 | Applicability defined | **FAIL** |
| 5 | All required inputs represented in the engine | **PASS** (`bw_mm`, `d_effective_mm`, `fc_prime_mpa`, `fy_mpa`, `es_mpa`, `mu_nmm`, `section_type`) |
| 6 | No unsupported assumption needed | **FAIL** — implementing now would require importing α₀/β₁/φ from ACI-based material |
| 7 | φ/model limits defined | **FAIL** — Table 9-7-2 absent |
| 8 | Boundary cases defined | **FAIL** — tension-controlled boundary cannot be sourced |
| 9 | Numerical domain / invalid cases defined | **FAIL** |
| 10 | Rule independently testable | **FAIL** — no verified Mabhas 9 model to test against; expected values would have to be invented |
| 11 | No Mostofinejad-for-Mabhas-9 substitution | **FAIL if implemented** — the only complete fixed-b,d model available is ACI-derived |

### ⇒ Promotion not allowed. `BG-FLEX-RECT-REQ-AS-001` remains **UNREGISTERED**, `VERIFY_PENDING`, `execution_allowed=False`.

---

## 9. Model differences recorded (for the record)

| Aspect | Mabhas 9 (recorded, unverified here) | Mostofinejad (verified, printed 189–194) | Divergence |
| :-- | :-- | :-- | :-- |
| Stress-block coefficient | α₀ = 0.85 (f′c ≤ 55 MPa), reducing above | fixed **0.85** (ACI) | same at low f′c |
| Moment coefficient | 1/(2α₀) = 0.588235 at α₀ = 0.85 | **0.59** (rounded) | **+0.30 %** |
| Implied α₀ from coefficient | 0.85 | 1/(2×0.59) = **0.847458** | −0.30 % |
| Above f′c = 55 MPa | α₀ reduces ⇒ coefficient rises | **0.59 fixed** | grows with f′c |
| φ | Table 9-7-2 (not verified) | 0.9 TC; **interpolation** for 0.002 < εt < 0.005 | unquantified |
| Max steel | §9-11-2-3 (not verified) | 0.364β₁f′c/fy; legacy 0.75ρ_b discussed | unquantified |
| Min steel | §9-11-5 (not verified) | **(5-39) √f′c/(4f_y)b_wd ≥ 1.4/f_y·b_wd** (ACI) | unquantified |

**Consequence:** the existing helper `reference/mostofinejad_ch5.solve_required_as` embodies the
Mostofinejad/ACI model. It **must remain** `MOSTOFINEJAD_METHODOLOGY_ONLY` and **must not** be
registered as a Mabhas 9 compliance implementation.

---

## 10. Exact remediation (precise, evidence-derived — not a guess)

The required pages, expressed in **both** the image-naming convention and the printed identity,
derived from the verified −20 offset:

| Material | Printed pages needed | Equivalent file/PDF indices | Clauses to be verified |
| :-- | :-- | :-- | :-- |
| Mabhas 9 | **113–114** | `page-133.jpg`, `page-134.jpg` | §9-8-2-1-1, §9-8-2-2-1…−2-2-8; Eqs. (9-8-2), (9-8-3-الف/ب), (9-8-4); Mₙ |
| Mabhas 9 | **107–109** | `page-127.jpg` … `page-129.jpg` | §9-7-4-1…−4-4; Table 9-7-2; Eqs. (9-7-10-الف/ب) |
| Mabhas 9 | **132** | `page-152.jpg` | §9-11-2-3 ductility limit |
| Mabhas 9 | **199** | `page-219.jpg` | §9-11-5-1-1…−1-3 minimum steel |
| Mostofinejad *(only if (5-46)/(5-47) cross-check is wanted)* | **200–205** | `…-211.jpg` … `…-216.jpg` | Eqs. (5-46), (5-47); Examples 5-5/5-6 |

**Already supplied and usable:** printed **112** (`page-132.jpg`) — keep it; it supplies
Eq. (9-8-1-الف) and the §9-8 scope.

*No re-upload is *requested* as a matter of process — this is a factual finding that the
package contains printed 87–94/112/179 rather than the flexural range. The five images above
are what the verified offset says is actually needed; the two that are closest to the stated
§9-8 target are PDF 133–134.*

---

## 11. Final decision

```
SOURCE VERIFICATION RESULT : PARTIAL — 1 of 10 Mabhas 9 pages is flexural; the resistance
                             model, phi model, ductility limit and As,min are NOT in the
                             package. Mostofinejad pages supplied are printed 189-194,
                             not the recorded 200-205.
IMPLEMENTATION DECISION    : REMAINS VERIFY_PENDING — execution_allowed = False.
                             NO implementation. NO registration. NO calculation-logic change.
```

**What changed this stage:** the page-identity question is now **closed by direct footer
inspection** (Mabhas 9 = −20; Mostofinejad = +11; the project's recorded −91 and +21 flexure
offsets are both wrong), Eq. (9-8-1-الف) `φMₙ ≥ Mᵤ` is **visually verified**, the Mostofinejad
methodology on printed 189–194 is **verified and its examples reproduce exactly**, and the
**exact missing pages are enumerated** rather than described vaguely.

**What did not change:** the rule. No registry entry, no status, no executable flag, no code.

---

## Appendix — Inspection log

| Step | Method | Result |
| :-- | :-- | :-- |
| Integrity | SHA-256 vs `SHA256SUMS.txt`, path-normalised | 16/16 OK |
| Page identity | footer/folio crop at 6× / 5× magnification, dark-pixel band profiling to locate numerals | −20 (Mabhas 9), +11 (Mostofinejad) |
| Content | full-page reads + mid/bottom band montages for all 16 images | mapped in §3 |
| Equations | direct reading of typed formulae at native resolution | §§5.1 |
| Cross-check | independent re-computation of Examples 5-1 and 5-2 | exact agreement |
| Coefficient | algebraic comparison of 0.59 vs 1/(2×0.85) | +0.30 % (ACI rounding) |
| Gate | brief §8 checklist applied item-by-item | 9 of 11 fail; no implementation |

**Engineering baseline at exit:** `pytest` 673 passed · `mypy --strict src` clean ·
registry 121 / 63 / 48 / 10 · duplicate Rule IDs 0 · §9-21-6 21 / 5 — **all unchanged**.
