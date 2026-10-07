# Phase 2F — Stage H.20: Targeted Audit of Blocker A

**`BG-TRANS-TIE-ANCHOR-PENDING` — §9-21-6-1-3(ب)**

**DECISION: `REMAINS BLOCKED — SOURCE AMBIGUITY` (outcome D; primary cause λ applicability,
secondary cause boundary gaps).** No rule was promoted, no evaluator was written, and no
registry value, status, count or `execution_allowed` flag was changed. The only artifact
of this stage is this record.

This stage targeted **blocker A only**. H.18 and H.19 were not reopened; B, C, D and E
were not modified; scope was not broadened. The stage's principal objective — the λ
applicability question — is answered below from source evidence, **not** from engineering
convention.

---

## 1. Scope

| | |
| :-- | :-- |
| Target rule | `BG-TRANS-TIE-ANCHOR-PENDING` |
| Governing clause | §9-21-6-1-3(ب) (printed p. 443 / PDF p. 463) |
| Objective | Determine whether (ب) can now be fully promoted, and specifically whether λ may lawfully be assigned a value |
| Method | Full-resolution visual inspection (up to 12×) of the source pages; equation verification; λ dependency trace; boundary analysis; engine input-model check; promotion gate |
| Out of scope (untouched) | B, C, D, E; H.14/H.16/H.17/H.18/H.19; UI, reports, DXF, optimisation; unrelated rules |

---

## 2. Baseline

| Item | Value |
| :-- | :-- |
| HEAD at stage start | **`22111f8`** (local HEAD was stale at `f22ff45`; recovered to `22111f8` without `--hard`, without rewriting history) |
| Working tree | clean |
| Branch | `arena/b9cd291a-beamgenius` |
| `origin/main` | **`df8067a750ffc7984c9dc5d80220ad9013503aa6`** — untouched, never written |
| Evidence | `phase2f-source-442-472/` on `origin/main` @ `df8067a` (31 JPG + 31 TXT), read **read-only** into git-ignored `working/h20/` |
| Tooling | `/tmp/bgvenv` rebuilt once (Pillow, numpy, pytest, mypy) |
| `pytest` | **673 passed** |
| `mypy --strict` | **clean — 23 source files** |
| Registry | **121 / 63 executable / 48 blocked / 10 reference** |
| Duplicate Rule IDs | **0** |
| §9-21-6 | **21 executable / 5 blocked** |

---

## 3. Source evidence

| PDF page | Printed | Content verified visually this stage |
| :-- | :-- | :-- |
| 442 | ۴۲۲ | §9-21-2-2-2/-2-2-3, §9-21-2-2-4 (seismic hook), Table 9-21-1/9-21-2 header |
| 443 | ۴۴۳ | hook table content |
| **445** | **۴۲۵** | **§9-21-3-1-4, -1-5, -1-6 (λ), §9-21-3-2-1, Eq. (9-21-1)** |
| 444 | ۴۲۴ | §9-21-2-2-6, **§9-21-3 heading «طول گیرایی»**, §9-21-3-1-1 scope, -1-2 |
| **463** | **۴۴۳** | **§9-21-6-1-1, -1-2, §9-21-6-1-3 chapeau + (الف) + (ب)** |

Line bands on PDF 463 were located by pixel profiling of the rendered image (not by eye),
and each line was then read at 3.2×–12×.

---

## 4. Exact §9-21-6-1-3(ب) wording

Read verbatim from PDF p. 463 (printed ۴۴۳), across its four printed lines:

> «۹-۲۱-۶-۱-۳ مهار میلگرد و سیم آجدار در خاموت باید منطبق بر شرایط زیر باشد:
>
> **الف-** در میلگردها یا سیمهای با قطر کوچکتر یا مساوی ۱۶ میلیمتر، و برای میلگردهای با قطر
> ۱۸ تا ۲۵ میلیمتر با تنش تسلیم کمتر از ۲۸۰ مگاپاسکال، وجود قلاب استاندارد پیرامون میلگرد
> طولی.
>
> **ب-** در میلگردهای به قطر ۱۸ تا ۲۵ میلیمتر و تنش تسلیم بیش از ۲۸۰ مگاپاسکال، وجود
> قلاب استاندارد پیرامون میلگرد طولی، به علاوهی طول مدفون بین وسط ارتفاع مقطع و انتهای
> بیرونی قلاب، بیشتر یا مساوی
> `0.17 f_y / (λ √f_c) · d_b`»

**Chapeau:** «مهار میلگرد و سیم آجدار در خاموت **باید منطبق بر شرایط زیر باشد**» — a
conjunctive bundling clause: the tie anchorage must satisfy the following conditions.

---

## 5. Mathematical-expression verification

The formula was rendered at 9×–12× and read glyph by glyph:

| Item | Verified content |
| :-- | :-- |
| Numerator | **`0.17 f_y`** — decimal `0.17`, then `f` with subscript `y` |
| Denominator | **`λ √f_c`** — `λ` (lambda) then the radical |
| **Position of λ** | **OUTSIDE the radical**: λ multiplies √f_c. Visually confirmed at 12× — the radical sign begins to the right of λ and encloses only `f_c` |
| Radicand | **`f_c` (NO prime)** — in sharp contrast with **Eq. (9-21-1)** on PDF 445 (printed ۴۲۵), which prints **`√f′_c`** (f with prime). Both were read at 8×–12× in the same session |
| Diameter variable | **`d_b`** — subscript `b` |
| Full expression | `0.17 · f_y / (λ · √f_c) · d_b` |
| Comparison | «**بیشتر یا مساوی**» (greater than or equal to) — inclusive |

**Consequence of the no-prime finding.** The clause's radicand is written `f_c`, not the
prime-marked `f′_c` used for the cylinder strength in Eq. (9-21-1) and elsewhere. The
delivered window contains **no definition of `f_c`** — its meaning (which concrete
strength quantity, and whether a conversion or cap applies) is not stated in the clause,
in §9-21-6, or anywhere in the window. This is recorded as an **additional** source
gap; it is secondary to the λ question but independently blocks execution.

---

## 6. λ dependency analysis

### 6.1 Where λ appears in the delivered window

| Check | Result |
| :-- | :-- |
| λ occurrences in the evidence window (PDF 442–472) | OCR cannot capture the glyph; **visual inspection of every page that the repo's own audit records as λ-bearing** was therefore used. The documented and re-confirmed occurrence is **PDF 445 / printed 425, §9-21-3-1-6** |
| λ definition clauses | **exactly one** — §9-21-3-1-6. A window-wide sweep for «ضریب بتن سبک» (lightweight-concrete factor) returns **PDF 445 only** |
| Symbols/notation clause in the window («علائم», «نماد», «نمادگذاری», «فهرست علائم») | **none exists** in PDF 442–472 |
| Equations using λ in the window | Eq. (9-21-1) (λ inside the denominator, development length) and §9-21-3-1-6's own definition. Both are inside §9-21-3 |
| §9-21-6-1-3(ب)'s formula | contains λ, on PDF 463 — i.e. λ is used **outside** the chapter that defines it |

### 6.2 Does §9-21-6 cite §9-21-3?

Robust multi-form sweep over the OCR of PDF 463–472, testing both digit orders
(`۹-۲۱-۳` and the RTL-reversed `۳-۲۱-۹`):

- **ZERO §9-21-3 citation forms found in §9-21-6 (PDF 463–472).**
- **Positive control on the same pages:** a §9-21-4 citation form **is** found (PDF 468).
  The zero is therefore a real absence, not an OCR or directionality artifact.

§9-21-6 cites §9-21-4 (for splices), §9-21-2 (for hook geometry), §9-21-6-1-3/-1-4
internally — **but never §9-21-3**, the chapter in which λ is defined.

### 6.3 Outcome classification (per the four permitted outcomes)

| Outcome | Assessment |
| :-- | :-- |
| **A — Explicit cross-reference establishes applicability** | **NOT SATISFIED.** §9-21-6-1-3(ب) carries no cross-reference to §9-21-3 or §9-21-3-1-6, and the sweep proves §9-21-6 never cites §9-21-3 at all |
| **B — General symbol definition establishes applicability** | **NOT SATISFIED.** The window contains **no** symbols/notation clause and no global parameter list. λ's only definition sits inside a single sub-clause |
| **C — The source defines λ globally enough to apply** | **NOT SATISFIED.** The definition is explicitly and narrowly self-scoped — see §7 |
| **D — The source does not establish applicability → ambiguity/blocker** | **SATISFIED** → blocker |

### 6.4 Precedent check (Step 8) — how the project already treats λ

Every **executable** rule in the registry that consumes λ is cited to a clause where λ is
in scope:

| Rule | Governing clause | Status |
| :-- | :-- | :-- |
| `BG-DEV-LENGTH-TENSION-001` | §9-21-3-1-3..6 & Eq. (9-21-1) | executable |
| `BG-DEV-LENGTH-TENSION-TABLE-001` | §9-21-3-2-3 & Table 9-21-4 | executable |
| `BG-DEV-LENGTH-HOOKED-001` | §9-21-3-3-1 & Eq. (9-21-3) | executable |
| `BG-DEV-LENGTH-HEADED-001` | §9-21-3-4-1 & Eq. (9-21-4) | executable |
| `BG-DEV-WIRE-DEFORMED-001` | §9-21-3-6-1 & Eq. (9-21-5) | executable |
| `BG-DEV-WIRE-PLAIN-001` | §9-21-3-7-1 & Eq. (9-21-7) | executable |
| `BG-DEV-LENGTH-COMPRESSION-001` | §9-21-3-8-1 | executable |
| `BG-SHEAR-VC-001` | §9-8-4-4-x (its **own** chapter defines its λ) | executable |

**No rule in the codebase imports λ across chapters.** The project has, consistently and
by design, only ever used λ where the governing clause supplies it. Promoting A would be
the **first** cross-chapter λ import in the project — and this audit finds no source
authority for it.

---

## 7. λ definition / scope analysis

§9-21-3-1-6, read verbatim at 2.6× (PDF 445 / printed ۴۲۵):

> «۹-۲۱-۳-۱-۶ در محاسبه طول گیرایی، λ ضریب بتن سبک برای بتن سبک ۰/۷۵ و برای بتن معمولی
> ۱/۰ در نظر گرفته میشود.»

| Question | Answer (source-based) |
| 1. What does λ represent? | «ضریب بتن سبک» — the **lightweight-concrete coefficient** |
| 2. Permitted values? | **۰/۷۵ (0.75)** for lightweight concrete; **۱/۰ (1.0)** for normal-weight concrete |
| 3. Controlling conditions? | The concrete's weight class (lightweight vs normal) |
| 4. Explicitly limited to development/anchorage length? | **YES.** The clause opens with the scoping phrase «**در محاسبه طول گیرایی**» — "in the calculation of the development length". The immediate neighbour clauses on the same page are scoped identically: §9-21-3-1-5 «در محاسبهی طول گیرایی، مقدار √f′c نباید از ۸/۳ مگاپاسکال تجاوز نماید» and §9-21-3-1-4 «در محاسبهی طول گیرایی، نیازی به اعمال ضریب کاهش مقاومت φ نیست» |
| 5. Does that limitation reach §9-21-6-1-3(ب)'s expression? | **The source does not say.** (ب) requires an *embedment length* between the section mid-depth and the outer hook end — a quantity the clause presents in the same shape as a development length, but §9-21-6-1-3 nowhere states that it is one, nor that §9-21-3's scoped rules apply to it |
| 6. Cross-reference from §9-21-6 to §9-21-3? | **NONE** (§6.2) |
| 7. General clause making the definition globally reusable? | **NONE** (§6.1 — no symbols clause exists in the window) |

**Chapter scope context.** §9-21-3 is titled **«طول گیرایی»** (Development length), and its
own §9-21-3-1-1 declares that chapter's subject: development of bars, deformed wires,
headed bars and welded wire mesh. §9-21-6 is a different chapter (transverse
reinforcement / ties). The fact that §9-21-6-1-3(ب) prints a λ-bearing expression does
not, by itself, import §9-21-3's scoped definitions into §9-21-6 — **and it is exactly
that import which the standing rules prohibit absent an explicit cross-reference.**

**Verdict: λ applicability is NOT established. An evaluator would have to assume it.**

---

## 8. fy boundary analysis

| | Content |
| :-- | :-- |
| **SOURCE TEXT (الف)** | «در میلگردها یا سیمهای با قطر کوچکتر یا مساوی ۱۶ میلیمتر، **و** برای میلگردهای با قطر ۱۸ تا ۲۵ میلیمتر با تنش تسلیم **کمتر از** ۲۸۰ مگاپاسکال، …» |
| **SOURCE TEXT (ب)** | «در میلگردهای به قطر ۱۸ تا ۲۵ میلیمتر **و** تنش تسلیم **بیش از** ۲۸۰ مگاپاسکال، …» |
| **MATHEMATICAL DOMAIN** | (الف): `f_y < 280` (attached to the 18–25 mm sub-condition) · (ب): `f_y > 280` · `f_y = 280` is in **neither** (strict inequalities, both directions) |
| **ENGINE REPRESENTATION** | existing executable rule `BG-TRANS-TIE-ANCHOR-STD-HOOK-001` already implements this reading and returns BLOCKED for `f_y = 280` exactly (`TIE_ANCHOR_FY_280_IN_GAP`) |
| **GAP OR NO GAP** | **GENUINE GAP** — recorded verbatim, never interpolated. Confirmed unchanged |

**No minimum or maximum fy threshold other than 280 MPa appears in the clause.**
(Boundary verified at 3.6× on the page image; the two printed lines were read in full.)

---

## 9. db boundary analysis

| Boundary | SOURCE TEXT | MATHEMATICAL DOMAIN | ENGINE REPRESENTATION | GAP? |
| :-- | :-- | :-- | :-- | :-- |
| Small-bar branch | «قطر **کوچکتر یا مساوی** ۱۶ میلیمتر» | `d_b ≤ 16` (no f_y gate) | implemented (branch الف) | **NO GAP** — inclusive, explicit |
| Large-bar band | «قطر **۱۸ تا ۲۵** میلیمتر» | `18 ≤ d_b ≤ 25` | implemented (branches الف/ب by f_y) | **NO GAP** — band explicit |
| 16 < d_b < 18 | *(silent)* | **undefined** | returns BLOCKED (`TIE_ANCHOR_DB_IN_GAP`); `d_b = 17 mm` specifically is recorded verbatim | **GENUINE GAP** — the clause jumps from ≤16 to ≥18 |
| d_b > 25 | *(silent)* | **undefined** | returns BLOCKED (`TIE_ANCHOR_DB_ABOVE_TABLE`) | **GENUINE GAP** — no branch assigned |

**Note on §9-4-8-8 (processed earlier):** the general deformed-wire diameter window of
1.5–16 mm, and the >16 mm treatment rule, were verified in Stage H.14 and are *not*
imported here — §9-21-6-1-3(ب)'s own printed band (18–25 mm) governs this clause, and the
two sources are not reconciled by any cross-reference in the delivered material.
Boundaries read at 3.6×; no boundary was invented and none is interpolated.

---

## 10. fc analysis

| Question | Finding |
| :-- | :-- |
| Symbol as printed in (ب) | **`√f_c`** — no prime (verified at 12×; §5) |
| Symbol as printed in Eq. (9-21-1) on the same evidence set | **`√f′_c`** — with prime (verified at 8×) |
| Definition of `f_c` in §9-21-6-1-3(ب) | **none** |
| Definition of `f_c` anywhere in the delivered window (PDF 442–472) | **not found** — no clause in the window states what `f_c` denotes |
| Is the §9-21-3-1-5 clamp (`√f′_c` ≤ 8.3 MPa) applicable? | The clamp is scoped «در محاسبهی طول گیرایی» inside §9-21-3 and is **not** cross-referenced by §9-21-6; applying it would be a second unsupported import |
| ENGINE REPRESENTATION | `f'_c` exists as an input elsewhere in the engine, but the clause's `f_c` cannot be assigned that input without assuming they are the same quantity |
| GAP? | **GENUINE SOURCE GAP** — the radicand symbol is undefined in the clause and in the window |

---

## 11. Embedment / hook geometry analysis

| Aspect | Finding |
| :-- | :-- |
| Source requirement | «به علاوهی طول مدفون بین **وسط ارتفاع مقطع** و **انتهای بیرونی قلاب**، بیشتر یا مساوی `0.17 f_y/(λ√f_c)·d_b`» |
| **H.17 finding re-confirmed?** | **YES — re-confirmed visually.** The two endpoints are both present in the print: the **mid-height of the section** («وسط ارتفاع مقطع») and the **outer end of the hook** («انتهای بیرونی قلاب»). H.17's correction of the older "elided referent" claim is upheld; the old claim is **not** reintroduced |
| Quantity to evaluate | the **embedment length** measured between those two points, compared `≥` the formula |
| Is the comparison inclusive? | **Yes** — «بیشتر یا مساوی» |

### 11.1 Engine-input classification (four-way, as directed)

| Required quantity | Classification |
| :-- | :-- |
| `d_b` (bar diameter) | **1 — directly supplied input** (exists in the executable sibling rules) |
| `f_y` (yield stress) | **1 — directly supplied input** |
| Section depth `h` | **1 — directly supplied input** (`BeamGeometry.h_mm`, `domain/models.py` L88/L110) |
| Section mid-height («وسط ارتفاع مقطع») | **2 — deterministic derivation** (`h/2`; the term is explicit in the clause) |
| Outer hook endpoint («انتهای بیرونی قلاب») | **3 — genuinely missing**, but representable: the hook evaluator (`BG-TRANS-STANDARD-HOOK-001`) consumes provided hook geometry (`hook_angle_deg`, `inner_bend_diameter_mm`, `straight_extension_mm`). Locating the outer end would require the as-drawn hook geometry to be supplied. **No default hook geometry may be invented** |
| Embedment length | **4 — cannot be derived** without (3); it is the measured span between the two endpoints, so it must be supplied or derived from supplied hook geometry |
| `f_c` | **3/4 — genuinely missing** (§10); cannot be mapped to `f'_c` without an assumption |
| `λ` | **4 — value cannot be assigned at all** without an unsupported assumption (§6–§7). Both permitted values (0.75, 1.0) are conditional on concrete weight class, and the clause gives no basis for using either here |

---

## 12. Engine input-model analysis — summary

| Needed | Exists? | Source-definable? |
| :-- | :-- | :-- |
| `d_b`, `f_y`, `h_mm` | yes | yes |
| mid-height of section | derived (`h/2`) | yes (explicit term) |
| outer hook end | no (geometry must be supplied) | yes, **if** hook geometry is caller-supplied and never defaulted |
| embedment length | no | yes, **if** supplied or derived from supplied hook geometry |
| `f_c` | no | **NO** — the symbol is undefined in the clause and the window |
| `λ` | no | **NO** — applicability is not established (§6), and the value is conditional on a weight class the clause never mentions |

---

## 13. Existing evaluator / delegate analysis

| Item | Finding |
| :-- | :-- |
| A's entry | `BG-TRANS-TIE-ANCHOR-PENDING` — `VERIFY_PENDING`, `execution_allowed=False`, `dependencies=()`, `symbolic_formula="UNAVAILABLE (execution blocked)"`, PDF 463 / printed 443 |
| Sibling branch rules | `BG-TRANS-TIE-ANCHOR-STD-HOOK-001` (الف, H.7) and `BG-TRANS-TIE-ANCHOR-JOIST-STD-HOOK-001` (پ, H.8) — both executable, both untouched by this stage. Their evaluators implement the boundary gaps of §8/§9 as deterministic BLOCKED returns |
| Hook geometry | delegated to `BG-TRANS-STANDARD-HOOK-001` (Clause 9-21-2-2-2 / Table 9-21-2); no hook geometry is duplicated |
| Any evaluator that already models hook **embedment**? | **No** — no rule in the registry computes an embedment length between a section mid-depth and a hook end |
| Any executable rule that uses λ? | yes — but every one is cited to a clause where λ is in scope (§6.4). **None imports it across chapters.** The implementation was not copied and no precedent authorises the import |

---

## 14. Promotion gate

| # | Condition | Result |
| :-- | :-- | :-- |
| 1 | §9-21-6-1-3(ب) visually verified | **PASS** — all four printed lines read at 3.2×–12× |
| 2 | Mathematical expression unambiguous | **PASS** — numerator, denominator, λ placement, radicand and diameter verified glyph by glyph |
| 3 | Geometric datum unambiguous | **PASS** — mid-height of section ↔ outer hook end; H.17's correction re-confirmed |
| 4 | **λ applicability explicitly source-supported** | **FAIL** — no cross-reference, no symbols clause, no global definition; definition is self-scoped to «در محاسبه طول گیرایی» |
| 5 | **λ values/conditions source-supported for *this* use** | **FAIL** — the weight-class condition is not referenced by the clause |
| 6 | **fy domain source-supported** | **FAIL** — `f_y = 280` exactly lies in neither branch (genuine printed gap) |
| 7 | **db domain source-supported** | **FAIL** — 16 < d_b < 18 and d_b > 25 are assigned by no branch |
| 8 | **fc applicability source-supported** | **FAIL** — `f_c` (no prime) is undefined in the clause and in the window; the §9-21-3-1-5 clamp is not cross-referenced |
| 9 | Hook/embedding geometry representable deterministically | **PASS (conditional)** — representable only with caller-supplied hook geometry; no default may be created |
| 10 | Every required input exists or is deterministically derivable | **FAIL** — `λ` and `f_c` are neither existing nor source-definable |
| 11 | No unsupported assumption required | **FAIL** |
| 12 | Evaluator cannot emit false PASS | **FAIL** — no evaluator can be written over undefined quantities |

**Gate result: 7 of 12 conditions FAIL.** Under the governing rule, A must remain:
`VERIFY_PENDING`, `execution_allowed=False`. **No partial evaluator was created.**
Because the clause's chapeau is bundling («باید منطبق بر شرایط زیر باشد»), a rule covering
only the geometric comparison could return **PASS while λ and f_c were assumed** — a
false PASS, which is prohibited.

---

## 15. Final decision

**Outcome `D` — `REMAINS BLOCKED — SOURCE AMBIGUITY`.**

- **Primary classification: `SOURCE_AMBIGUITY`** — λ applicability is not established by
  any source mechanism (no cross-reference, no symbols clause, no global definition), and
  the definition that does exist is explicitly self-scoped to development-length
  calculation.
- **Secondary classification: `SOURCE–INPUT MODEL GAP`** — `f_c` (unprimed) is undefined in
  the clause and in the window, and the three printed boundary gaps remain.

**`FULLY RESOLVED` is not reached**, therefore **no implementation was performed**:
no evaluator, no RuleReference change, no registry status change, no new execution path.

### 15.1 What this stage resolved (and did not)

| | |
| :-- | :-- |
| **Resolved / confirmed** | (i) the formula is unambiguously `0.17 f_y/(λ√f_c)·d_b`, λ **outside** the radical; (ii) the radicand is `f_c` **without** the prime used in Eq. (9-21-1) — a previously unrecorded distinction; (iii) the embedment endpoints **are** in the print (H.17's correction upheld, old claim not reintroduced); (iv) the comparison is inclusive («بیشتر یا مساوی»); (v) λ has exactly one definition in the window, scoped «در محاسبه طول گیرایی», with no symbols clause and no §9-21-3 citation from §9-21-6 (verified with a positive control); (vi) **no executable rule in the project has ever imported λ across chapters** — the precedent uniformly keeps λ where its clause defines it; (vii) all three H.17 boundary gaps are re-confirmed verbatim at high magnification. |
| **Not resolved** | Whether λ is applicable to §9-21-6-1-3(ب), and what `f_c` denotes. Neither can be answered from the delivered source without assuming. |
| **H.17 status** | **Upheld**, with two refinements (the unprimed `f_c`, and the project-wide λ precedent). |

---

## 16. Exact residual blocker(s)

**Primary — λ applicability (SOURCE_AMBIGUITY).** §9-21-6-1-3(ب) requires a length
`0.17 f_y/(λ√f_c)·d_b` but contains `λ`, while λ is defined only in §9-21-3-1-6, whose own
wording scopes it to «در محاسبه طول گیرایی». §9-21-6 never cites §9-21-3; the window has no
symbols/notation clause; and no clause extends λ to transverse-reinforcement/tie
anchorage. **Assigning λ = 1.0 (or 0.75) here would therefore be an import**, not a
reading — and would additionally require assuming the member's concrete weight class,
which the clause never mentions.

**Secondary — `f_c` undefined (SOURCE–INPUT MODEL GAP).** The printed radicand is `f_c`
(no prime). No clause in the clause or the window defines it, and the §9-21-3-1-5 clamp on
`√f′_c` is scoped inside §9-21-3 and is not cross-referenced.

**Tertiary — printed boundary gaps (unchanged).** `f_y = 280 MPa` exactly lies in neither
branch; `16 < d_b < 18 mm` and `d_b > 25 mm` are assigned to no branch. Recorded verbatim;
never interpolated.

**What would unlock it (nothing less):**

1. an edition, erratum, corrigendum or authoritative annex of Mabhas 9 in which
   §9-21-6 cites §9-21-3-1-6 (or a symbols clause makes λ global), **and** `f_c` is
   defined; **or**
2. an official clarification fixing both λ's applicability and the meaning of `f_c`; **or**
3. an explicit recorded project-level decision on how to treat scoped symbol definitions
   across chapters.
   Engineering convention, the existence of a same-named symbol elsewhere, the neighbouring
   clause, and Mostofinejad (non-governing reference) are **not** admissible substitutes.

---

## 17. Files changed

| File | Change |
| :-- | :-- |
| `docs/PHASE2F_STAGE_H20_TIE_ANCHOR_AUDIT.md` | **this record (new)** |
| — | **Nothing else** — no registry, evaluator, test, catalog or other documentation value was modified |

---

## 18. Validation

| Gate | Result |
| :-- | :-- |
| `PYTHONPATH=src pytest` | **673 passed** |
| `PYTHONPATH=src mypy --strict` | **clean — 23 source files** |
| Registry consistency | **121 total / 63 executable / 48 blocked / 10 reference** — unchanged |
| Duplicate Rule IDs | **0** |
| §9-21-6 | **21 executable / 5 blocked** — unchanged |
| `BG-TRANS-TIE-ANCHOR-PENDING` | `VERIFY_PENDING`, `execution_allowed=False`, `dependencies=()` — unchanged |
| All five sentinels | still non-executable |
| `git diff --check` | clean |
| No unrelated changes | confirmed (single new document) |

**Deltas: none.**

---

## 19. Commit SHA

**Baseline at stage start: `22111f8`.**
**This stage's commit: recorded below** — the SHA is inserted as a follow-up content commit
(never by amending or rewriting history).

*Commit SHAs are recorded in the stage close-out; no history was rewritten, no rebase and
no force-push was used.*

---

## 20. origin/main status

`origin/main` remains at **`df8067a750ffc7984c9dc5d80220ad9013503aa6`**, unmodified.
It was read only (`git ls-tree`, `git show` into the git-ignored `working/h20/`).
No reset, rebase, force-push, history rewrite or branch switch occurred. All work is on
`arena/b9cd291a-beamgenius`.

---

```
DECISION:                 REMAINS BLOCKED — SOURCE AMBIGUITY (outcome D)
RULE:                     BG-TRANS-TIE-ANCHOR-PENDING
STATUS:                   VERIFY_PENDING
EXECUTION_ALLOWED:        False
PRIMARY CLASSIFICATION:   SOURCE_AMBIGUITY (lambda applicability)
SECONDARY CLASSIFICATION: SOURCE–INPUT MODEL GAP (f_c unprimed and undefined;
                          plus three printed boundary gaps)
λ APPLICABILITY:          NOT ESTABLISHED — lambda is defined only at §9-21-3-1-6,
                          self-scoped to «در محاسبه طول گیرایی»; §9-21-6 cites §9-21-3
                          nowhere (verified with positive control); no symbols clause
                          exists in the window; no executable rule in the project has
                          ever imported lambda across chapters.
fy BOUNDARY:              GENUINE GAP — (الف) f_y < 280, (ب) f_y > 280; f_y = 280 MPa
                          exactly lies in neither. Re-confirmed verbatim.
db BOUNDARY:              GENUINE GAPS — ≤16 implemented; 18–25 band explicit;
                          16 < d_b < 18 (incl. d_b = 17 mm) and d_b > 25 assigned by
                          no branch. Re-confirmed verbatim.
GEOMETRY MODEL:           Datum IS present (mid-height of section ↔ outer hook end) —
                          H.17's correction upheld. Representable only with
                          caller-supplied hook geometry; no default created.
                          f_c and λ remain unassignable.
PRIMARY BLOCKER:          lambda applicability (no source mechanism establishes it)
IMPLEMENTATION:           NOT PERFORMED — promotion gate failed 7 of 12 conditions;
                          no partial evaluator (chapeau is bundling ⇒ false-PASS risk)
FILES CHANGED:            docs/PHASE2F_STAGE_H20_TIE_ANCHOR_AUDIT.md (new, only)
PYTEST:                   673 passed
MYPY:                     Success: no issues found in 23 source files
REGISTRY:                 121 / 63 executable / 48 blocked / 10 reference — unchanged
                          (§9-21-6: 21 executable / 5 blocked — unchanged)
COMMIT:                   see §19
ORIGIN/MAIN:              df8067a750ffc7984c9dc5d80220ad9013503aa6 — untouched
```
