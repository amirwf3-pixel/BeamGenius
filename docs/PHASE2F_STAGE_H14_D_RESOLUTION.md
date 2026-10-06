# Phase 2F — Stage H.14: §9-4-8 Source Verification for `BG-TRANS-WIRE-SUBST-PENDING`

**Status: SOURCE VERIFICATION COMPLETE — decision `KEEP_BLOCKED`. No rule implemented.**

> **Supersedes, for §9-4-8 only:** `docs/PHASE2F_STAGE_H13_SOURCE_EVIDENCE.md` §1–§2
> recorded that §9-4-8 could not be inspected because the announced evidence file never
> arrived. That finding was accurate for H.13 and is **not** rewritten here; the H.14
> repair (`3e34d0c`) placed the evidence in `phase2f-source-948/`, and §9-4-8 has now
> been read. H.13's §3 (the §9-21-6-2-3 citation analysis) and §4–§6 remain current and
> are relied upon below.

H.14 resolved the last outstanding source question of Phase 2F: the content of Mabhas 9
Chapter 9-4 Clause 9-4-8, the sole dependency of Clause 9-21-6-2-3 (blocker **D**).
The four committed evidence pages were visually inspected in full. §9-4-8 has now
been read, and the result is that **the substituted-material eligibility it imposes
cannot be evaluated deterministically by BeamGenius**, because it requires
conformity to an external Iranian product standard that is neither available nor
modelled.

The registry entry `BG-TRANS-WIRE-SUBST-PENDING` therefore remains
`VERIFY_PENDING` with `execution_allowed=False`. **No production rule, no code, no
test and no registry change was made in H.14.**

---

## 1. Source identity

| Field | Record |
| :-- | :-- |
| Evidence location | `phase2f-source-948/` (committed, HEAD `3e34d0c`) |
| Files | `p086_printed066.png`, `p087_printed067.png`, `p088_printed068.png`, `p089_printed069.png` |
| Image format | PNG, 595 × 841 px each (A4 portrait, 72 dpi scan) |
| Source document | Iranian National Building Regulations — Mabhas 9 (1399, 5th edition) per `phase2f-source-948/README.md` |
| Running header on all four pages | «۹-۴ مشخصات آرماتورها» ("Chapter 9-4 — Reinforcement Specifications") |
| Printed folios verified on-page | **۶۶, ۶۷, ۶۸, ۶۹** — all four visually confirmed at the page foot |
| PDF page mapping | 86→66, 87→67, 88→68, 89→69 — offset **PDF = printed + 20**, matching the project's established convention for this book |
| Coverage | §9-4-7 (partial, printed p. 66) and §9-4-8 (printed pp. 66–69) |
| Edition corroboration | The images carry no ISBN/edition imprint within this page range. Edition identity rests on (a) the evidence README and (b) **continuity with the committed evidence window** (`phase2f-source-442-472/`): identical running-header typography, identical folio offset (PDF = printed + 20) and identical column layout. Recorded as corroborated, not as an on-page imprint read. |

**Method.** Every load-bearing statement below was read visually from blinded,
high-magnification crops (250 %–600 %) of the committed PNGs. No OCR was used for
any determination; the source text was transcribed and the Persian quotations below
are the verbatim print.

**Source-completeness note.** §9-4-8 ends part-way down printed page 69; the clause
text continues beyond the supplied range (see §2.9 and §5, item 3). This is recorded,
not filled.

---

## 2. §9-4-8 clause-by-clause findings

### 2.0 Section heading — printed p. 66 / PDF 86

> «۹-۴-۸ مشخصات مورد نیاز آرماتورها در طراحی»

"Reinforcement specifications required in design." The clause is a **material-specification
and usage-eligibility** clause; it is not, in the main, a detailing rule.

### 2.1 §9-4-8-1 — deformed requirement; plain restricted to spirals (p. 66)

> «۹-۴-۸-۱ کلیه‌ی آرماتورهای طولی و عرضی مصرفی در سازه‌های بتن آرمه باید آجدار باشند. استفاده از آرماتورهای ساده فقط در دورپیچ‌ها مجاز است.»

"All longitudinal and transverse reinforcement used in reinforced concrete
structures shall be deformed. Use of plain (smooth) reinforcement is permitted
**only in spirals**."

| Question | Finding |
| :-- | :-- |
| Requirement | Deformed reinforcement mandatory for all longitudinal **and transverse** reinforcement |
| Plain reinforcement | Permitted **only** in spirals (`دورپیچ`) |
| Applicability to ties | Expressly in scope — "عرضی" (transverse) |
| Relevant to D? | **Yes, decisively.** It excludes plain wire from tie substitution by a deterministic categorical rule |
| Deterministic? | Yes, given a reinforcement-type input |

This is the clause that makes D's **plain-wire branch deterministically FAIL** rather
than pass by omission.

### 2.2 §9-4-8-2 — measurement of tensile yield stress (p. 66)

Two permitted experimental routes for establishing tensile yield stress:
«الف- روش جابجایی- تنش نظیر ۰/۲ درصد کرنش ماندگار» (offset method at 0.2 %
permanent strain) and «ب- روش توقف نیرو ...» (force-halt method, with the
stipulation that the point must be clear and unambiguous).

| Question | Finding |
| :-- | :-- |
| Requirement | How yield stress is experimentally determined |
| Applicability to D? | Indirect. It governs how a *measured* yield stress is obtained, not how a design value is used |
| Deterministic? | Not an engine computation — it is a laboratory-method provision |

### 2.3 §9-4-8-3 — stress–strain constitutive law (pp. 66–67)

Clause spans the page boundary. The heading on printed p. 66 reads:

> «۹-۴-۸-۳ در کرنش‌های کم‌تر یا مساوی با کرنش حد تسلیم، ...»

The two equations are printed on p. 67 and are unambiguous (they are set in Latin
notation, outside the Persian running text):

- **Eq. (۹-۴-۱):** `fs = Es εs`  — «در صورتی که εs ≤ εy»
- **Eq. (۹-۴-۲):** `fs = fy`  — «در صورتی که εs > εy»

with the accompanying Persian: «در کرنش‌های بزرگ‌تر از کرنش حد تسلیم، تنش فولاد مستقل
از کرنش بوده و مطابق رابطه‌ی (۹-۴-۲) منظور می‌گردد.»

*Recorded conservatively:* the clause's opening line carries inline mathematical
symbols embedded in RTL Persian text, and at this scan resolution their exact
character order cannot be settled to the standard applied elsewhere in this document.
The clause's **content** (elastic branch up to yield, constant fy beyond) is
unambiguous from the two printed equations; the full symbol-by-symbol transcription of
the opening sentence is therefore deliberately **not** asserted.

| Question | Finding |
| :-- | :-- |
| Requirement | Elasto-plastic constitutive law: fs = Es·εs below yield; fs = fy above |
| Relevant to D? | **No.** It is the general steel stress–strain law, already implemented in the verified flexure/shear rules |
| Deterministic? | Yes, but it is not part of the §9-21-6-2-3 substitution condition |

### 2.4 §9-4-8-4 — modulus of elasticity (p. 67)

> «۹-۴-۸-۴ مدول الاستیسیته، Es برای آرماتورها برابر با ۲۰۰۰۰۰ مگاپاسکال است.»

E_s = 200,000 MPa. Already verified and in use (`BG-FLEX-STRAIN-LIMIT`). **Not a new
dependency** for D; recorded for completeness.

### 2.5 §9-4-8-5 — yield-stress cap by table (p. 67)

> «۹-۴-۸-۵ تنش حد تسلیم به کار برده شده در محاسبات برای آرماتورها بستگی به مشخصات فولاد مصرفی داشته و بر اساس نوع کاربری نباید از مقادیر داده شده در جدول ۹-۴-۴ برای آرماتورهای آجدار، و جدول ۹-۴-۵ برای آرماتورهای ساده بیشتر باشد.»

"The tensile yield stress used in calculations shall not exceed the values given in
Table 9-4-4 for **deformed** reinforcement and Table 9-4-5 for **plain**
reinforcement, according to the use."

| Question | Finding |
| :-- | :-- |
| Requirement | Cap the design yield stress at the table value for the specific use |
| Relevance to D | **Yes** — it is the mechanism by which the table becomes mandatory (see §2.7) |
| Deterministic? | Yes, given a reinforcement-type + use + yield-stress input |

### 2.6 §9-4-8-6 — type eligibility by table (p. 67)

> «۹-۴-۸-۶ نوع آرماتورهایی که برای کاربری مشخص ساخته‌ای استفاده می‌شوند، باید برای آرماتورهای آجدار مطابق جدول ۹-۴-۴، و برای آرماتورهای ساده مطابق جدول ۹-۴-۵ باشد.»

"The type of reinforcement used for a given application shall follow Table 9-4-4 for
deformed, and Table 9-4-5 for plain, reinforcement."

| Question | Finding |
| :-- | :-- |
| Requirement | The **type** of reinforcement admissible for a use is table-governed |
| Relevance to D | **Yes, decisively** — see the tie row of Table 9-4-4 (§2.7.2) |
| Deterministic? | Only if the table entry for the specific use is unambiguous |

### 2.7 Table 9-4-4 — «جدول ۹-۴-۴ کاربرد آرماتورهای آجدار طولی و عرضی» (p. 68 / PDF 88)

Column structure (right to left): **کاربرد** (use) │ **محل مورد استفاده** (location of
use) │ **حداکثر مقدار R̄ برای کاربردی در محاسبات (مگاپاسکال)** (maximum design value) │
**نوع آرماتور** split into **میلگردهای آجدار** (deformed bars) and **سیم‌های آجدار**
(deformed wires) │ **ملاحظات** (remarks).

#### 2.7.1 Footnotes (verified verbatim, p. 68)

> «[۱] اعداد این ستون بیانگر حداکثر مقدار R̄ برای هر رده آرماتور است.»

> «[۲] استفاده از شبکه‌های آجدار جوشی نیز مجاز است.»

Footnote [۲] — "use of welded **deformed** meshes is also permitted" — is the **only**
provision anywhere in the delivered evidence that admits welded mesh as a material.
Its placement is therefore decisive and was verified at 500 % magnification:

#### 2.7.2 Placement of footnote [۲] — the decisive structural finding

| Group (کاربرد) | Row (محل مورد استفاده) | R̄ cap | Bar type column | Wire type column | ملاحظات |
| :-- | :-- | :-- | :-- | :-- | :-- |
| خمش، نیروی محوری، حرارت و انقباض | قاب‌های لرزه‌ای ویژه | 550 | بند ۹-۴-۹ | غیر مجاز | - |
| خمش، نیروی محوری، حرارت و انقباض | کلیه‌ی اجزای دیوارهای لرزه‌ای ویژه | 550 | همه رده‌های آجدار | همه رده‌های آجدار | - |
| خمش، نیروی محوری، حرارت و انقباض | **سایر موارد** | 550 | همه رده‌های آجدار | همه رده‌های آجدار | **[۲]** |
| خمش، نیروی محوری، حرارت و انقباض | سیستم‌های لرزه‌ای ویژه / دورپیچ‌ها / سایر موارد | 700 / 700 / 550 | همه رده‌های آجدار | همه رده‌های آجدار / غیر مجاز | - |
| **برش** (shear) | قاب‌های لرزه‌ای ویژه / کلیه‌ی اجزای دیوارهای لرزه‌ای ویژه | 550 | همه رده‌های آجدار | همه رده‌های آجدار | - |
| **برش** (shear) | **خاموت‌ها، پست‌ها، تنگ‌ها** | **۴۲۰** | **همه رده‌های آجدار** | **همه رده‌های آجدار** | **-** |
| **برش** (shear) | برش اصطکاک | 420 | همه رده‌های آجدار | همه رده‌های آجدار | - |
| **پیچش** (torsion) | آرماتورهای طولی و عرضی | 420 | همه رده‌های آجدار | همه رده‌های آجدار | - |

**Finding:** footnote [۲] is attached to the `سایر موارد` ("other cases") row of the
**خمش، نیروی محوری، حرارت و انقباض** (flexure / axial force / thermal / shrinkage)
group — **not** to any row of the **برش** (shear) group, and specifically **not** to
the row `خاموت‌ها، پست‌ها، تنگ‌ها` (stirrups, hangers, **ties**) whose remarks cell is
`-`.

Therefore, for the specific use that §9-21-6-2-3 addresses — a **tie** (`تنگ`) in
**shear** — Table 9-4-4 as printed admits **deformed bars and deformed wires of all
grades, capped at 420 MPa**, and its remarks cell does **not** carry the welded-mesh
permission.

#### 2.7.3 Consequences for the two substitute materials of §9-21-6-2-3

| Substitute in §9-21-6-2-3 | Table 9-4-4 (shear / tie row) | Outcome |
| :-- | :-- | :-- |
| **سیم آجدار** (deformed wire) | `سیم‌های آجدار` = «همه رده‌های آجدار», R̄ ≤ 420 MPa | **Admitted** — deterministically evaluable |
| **شبکه‌ی آرماتور سیم جوش شده** (welded wire mesh) | Not listed; remarks cell is `-`; the only mesh permission in the table, footnote [۲], sits on the flexure/axial `سایر موارد` row | **Ambiguous** — see §4.2 |

### 2.8 Table 9-4-5 — «جدول ۹-۴-۵ کاربرد آرماتورهای دورپیچ ساده» (p. 69 / PDF 89)

Title translates as "use of **plain spiral** reinforcement". Rows cover concrete
confinement of special seismic systems (700), spirals (700), spirals in shear (420)
and spirals in torsion (420). The grade column reads «انواع آرماتورهای گرم و سرد
نوردیده که دارای ویژگی‌های جدول ۹-۴-۳ می‌باشند».

This table confirms §9-4-8-1 from the other direction: **plain** reinforcement has a
table at all only because of the spiral exception.

### 2.9 §9-4-8-7 — conformity to an Iranian national standard (p. 69 / PDF 89) — **the load-bearing blocker**

> «۹-۴-۸-۷ سیم‌های ساده و آجدار و شبکه‌های جوشی ساخته شده از سیم‌های ساده و آجدار باید مطابق استاندارد ملی ایران به شماره ۱۱۵۵۸ باشند.»

"Plain and deformed wires, and welded meshes made from plain and deformed wires, shall
conform to Iranian National Standard No. **11558**."

| Question | Finding |
| :-- | :-- |
| Requirement | **Product-conformity** to an external national standard (INSO 11558) |
| Applies to plain wire | Yes |
| Applies to deformed wire | **Yes** |
| Applies to welded mesh (plain-wire mesh) | **Yes** |
| Applies to welded mesh (deformed-wire mesh) | **Yes** |
| Relevance to D | **Direct and obligatory.** §9-21-6-2-3 requires compliance with §9-4-8, and every material §9-21-6-2-3 permits — deformed wire *and* both welded-mesh variants — falls under §9-4-8-7 |
| Deterministic? | **No.** See §4.1 |

Note the scope: §9-4-8-7 is drafted to cover **all four** wire categories, so it
cannot be avoided by choosing one substitute material over the other. It is not a
deformed-wire-only or mesh-only condition.

### 2.10 §9-4-8-8 — deformed-wire diameter limits (p. 69 / PDF 89)

> «۹-۴-۸-۸ در سیم‌های آجدار، فقط استفاده از قطرهای ۱/۵ تا ۱۶ میلی‌متر مجاز است. در صورت استفاده از سیم‌های آجدار با قطرهای بزرگ‌تر از ۱۶ میلی‌متر، طول‌های مهاری و وصله با منظور نمودن این سیم‌ها مشابه سیم‌های ساده، و با استفاده از بند ۹-۲۱-۳-۷ محاسبه می‌گردند.»

"In deformed wires, only diameters from **1.5 to 16 mm** are permitted. If deformed
wires larger than 16 mm are used, anchorage and splice lengths shall be calculated
treating them as plain wires, using Clause **9-21-3-7**."

| Question | Finding |
| :-- | :-- |
| Requirement | Deformed-wire diameter window 1.5–16 mm inclusive; above 16 mm → recompute as plain wire per §9-21-3-7 |
| Relevance to D | **Yes** — a diameter-eligibility condition on the deformed-wire substitute |
| Deterministic? | Yes, given a wire-diameter input |

### 2.11 §9-4-8-9 — special seismic longitudinal reinforcement (p. 69, truncated)

> «۹-۴-۸-۹ در آرماتورهای طولی آجدار در قاب‌های ویژه و دیوارهای لرزه‌ای ویژه و اجزای آنها از جمله دیوار پایه‌ها و تیرهای همبند که تحت اثر لنگر خمشی، نیروی محوری، و یا هر دو به صورت توام قرار می‌گیرند، باید ...»

Verbatim opening scope, then a stipulation of three conditions, of which two were
readable before the page ends:

> «الف- تنش تسلیم اندازه‌گیری شده در آزمایشگاه از تنش حد تسلیم در محاسبات، R̄، بیش از ۱۲۵ مگاپاسکال فراتر نرود.»

> «ب- نسبت تاب کششی اندازه‌گیری شده در آزمایشگاه به تنش حد تسلیم اندازه‌گیری شده در آزمایشگاه از ۱/۲۵ کمتر نباشد.»

| Question | Finding |
| :-- | :-- |
| Scope | **Longitudinal** (± آرماتورهای طولی) deformed bars in special frames / special seismic walls and their elements |
| Relevance to D | **None** — D concerns transverse ties, not longitudinal bars. Recorded for completeness and to prevent mis-import |
| Complete? | **No** — the clause continues past printed p. 69; the closing items fall outside the delivered range |

### 2.12 §9-4-8-... location verified

Every numbered item read in the delivered range is accounted for above:
§9-4-8-1, -2, -3, -4, -5, -6, -7, -8, -9. Table 9-4-4 and Table 9-4-5 and both
footnotes of Table 9-4-4 were read. **No clause of §9-4-8 in this range was left
unread**, except that §9-4-8-9's own item list crosses the page boundary.

### 2.13 Adjacent verified material — §9-4-7 «ویژگی‌های جوش پذیری» (partial, p. 66)

Delivered on the same page, above §9-4-8; recorded because it was in scope of the
supplied evidence and is adjacent material, not because it is part of D:

> «۹-۴-۷-۱ شرایط جوش پذیری آرماتورهای مورد استفاده در بتن آرمه و حداقل دمای مورد نیاز پیش گرم و انجام عملیات جوش کاری باید بر مبنای استانداردهای ملی ایران به شماره‌های ۳۱۳۲ و ۱-۲۱۰۵۶ باشند.»

> «۹-۴-۷-۲ عملیات جوش کاری در دمای -۱۸ درجه‌ی سلسیوس و پایین‌تر نباید انجام شوند.»

> «۹-۴-۷-۳ بعد از پایان جوش کاری، باید اجازه داد تا آرماتور به طور طبیعی سرد شود. شتاب دادن به فرآیند سرد شدن مجاز نمی‌باشد.»

Two observations relevant to *other* blockers (not to D): §9-4-7-1 imposes conformity
to **two further** Iranian national standards (3132 and 1-21056) for welding
operations; §9-4-7-2/-3 are deterministic temperature/process conditions. These are
recorded as verified source available for a future stage — they do **not** resolve
§9-21-4-7-3's Mabhas 10 dependency (blocker E), which is a different book.

---

## 3. Exact §9-21-6-2-3 relationship

Verified in H.13 from committed evidence
(`df8067a:phase2f-source-442-472/page-466.jpg`, printed p. 446 / PDF p. 466):

> «۹-۲۱-۶-۲-۳ استفاده از سیم آجدار یا شبکه‌ی آرماتور سیم جوش شده به عنوان جایگزین تنگ آجدار، با سطح مقطع معادل میلگرد آجدار با در نظر گرفتن الزامات ۹-۲۱-۶-۲-۱ و ۹-۴-۸ مجاز است.»

Structural decomposition, now with §9-4-8 read:

| # | Component | Source | Status after H.14 |
| :-- | :-- | :-- | :-- |
| 1 | Permission (not obligation) — «مجاز است» | 9-21-6-2-3 | Verified |
| 2 | Substitute material: deformed wire **or** welded wire mesh | 9-21-6-2-3 | Verified |
| 3 | Replaced item: a deformed tie (`تنگ آجدار`) | 9-21-6-2-3 | Verified |
| 4 | **Equivalent cross-sectional area** | 9-21-6-2-3 (self-contained) | **Deterministic** — derivable from existing area inputs |
| 5 | Compliance with **§9-21-6-2-1** (tie spacing) | 9-21-6-2-1 | **Already verified + executable** as `BG-TRANS-TIE-SPACING-001` |
| 6 | Compliance with **§9-4-8** | §9-4-8 (this stage) | **Read — but not fully deterministic** (§4) |

**Confirmed and unchanged:** the clause references exactly §9-21-6-2-1 and §9-4-8.
It does **not** reach §9-21-6-1, so blockers **A** (§9-21-6-1-3-ب) and **B**
(§9-21-6-1-5) are **not inherited** by D.

> **Registry metadata discrepancy (recorded, not silently corrected).** The
> `RuleReference` for `BG-TRANS-WIRE-SUBST-PENDING` in
> `src/beamgenius/registry/catalog.py` currently describes the clause as
> "subject to Clauses 9-21-6-2-1, **9-21-6-2-2** and National Building Regulations
> Clause 9-4-8". The verified print carries **no** §9-21-6-2-2 citation. This is a
> descriptive-metadata inaccuracy in a **non-executable** entry; it is recorded here
> for a future maintenance stage and was deliberately **not** edited in H.14, which
> is documentation-only.

> **Stale matrix lines (recorded, deliberately not edited).**
> `docs/PHASE2_SOURCE_VERIFICATION_MATRIX.md` still carries pre-H.14 statements that
> §9-4-8 pages were "not delivered" / "out of window" (e.g. the lines for
> `9-21-6-2-3`, `BG-TRANS-WIRE-SUBST-PENDING` and the Chapter 9-4 dependency list).
> Those statements are now factually superseded. H.14 is documentation-only and does
> **not** rewrite that historical matrix; correcting it belongs to a dedicated
> maintenance stage, together with the registry metadata fix above.

---

## 4. Minimum dependency surface and the deterministic gate

### 4.1 The blocking finding: §9-4-8-7 requires an external product standard

§9-21-6-2-3's operative condition is "با در نظر گرفتن الزامات ۹-۴-۸" — compliance with
§9-4-8. §9-4-8-7 mandates conformity to **استاندارد ملی ایران به شماره ۱۱۵۵۸**
(Iranian National Standard No. 11558) for **plain wires, deformed wires, and welded
meshes made from plain or deformed wires**. Since §9-21-6-2-3 admits only wire-based
substitutes (deformed wire or welded-wire mesh), **every permitted branch of D falls
under §9-4-8-7**. There is no branch of D that avoids it.

Consequences against the implementation gate:

| Gate condition | Assessment |
| :-- | :-- |
| The relevant §9-4-8 requirement is visually verified | **Yes** |
| The dependency is completely understood | **Yes** — and it terminates in an external document |
| **No external source is required for the implemented branch** | **FAILS** — INSO 11558 is an external product standard; it is not in the repository, was not supplied, and is not obtainable in this environment |
| **All required inputs are deterministic** | **FAILS** — BeamGenius models no material-certification/conformity datum. The only ways to proceed would be (a) a caller-supplied assertion that the wire conforms (an unverifiable self-declaration, not a deterministic evaluation), or (b) a default (explicitly forbidden) |
| No unresolved ambiguity remains | **FAILS** — §4.2 |
| Rule can fail closed without a false PASS | **FAILS** — a rule that ignored §9-4-8-7 would PASS non-conforming material; a rule that always BLOCKED on it would not evaluate the clause it claims to implement |
| RuleReference can be completed | Yes |
| Focused tests can cover the full logical condition | **No** — the conformity condition has no evaluable content |

Per the H.14 brief: *"If even one required part cannot be determined reliably, KEEP D
blocked."* Three conditions fail. **D is not implementable.**

### 4.2 The secondary finding: the welded-mesh branch is ambiguous

§9-21-6-2-3 expressly permits «شبکه‌ی آرماتور سیم جوش شده» (welded wire mesh) as a
tie substitute. But it subjects that permission to §9-4-8, and §9-4-8-6 requires the
*type* of reinforcement used to follow **Table 9-4-4** — whose shear/tie row
(`خاموت‌ها، پست‌ها، تنگ‌ها`) lists only «همه رده‌های آجدار» of deformed bars and
deformed wires and whose remarks cell is `-`.

The only mesh permission printed in Table 9-4-4 is footnote [۲]
(«استفاده از شبکه‌های آجدار جوشی نیز مجاز است»), and it is attached to the
flexure/axial `سایر موارد` row — **not** to the shear tie row (§2.7.2, verified at 500 %).

Two readings are therefore possible and the source does not adjudicate between them:

- **Reading 1** — §9-21-6-2-3's own express permission governs, and the mesh
  substitute need only satisfy the *general* material conditions (§9-4-8-1 deformed,
  §9-4-8-7 conformity) without any shear-row mention in the table.
- **Reading 2** — Table 9-4-4 is mandatory for type eligibility via §9-4-8-6, so a
  mesh substitute for a **tie** is admitted only if the mesh qualifies under some
  row that carries footnote [۲]; the shear tie row does not.

The two readings have materially different consequences for whether a mesh-to-tie
substitution PASSes. Choosing one would be an engineering assumption not supported by
the printed source — precisely the outcome the brief forbids. Note also that under
**either** reading §9-4-8-7 still applies, so this ambiguity is secondary to §4.1; it
is recorded because a future stage must settle it before any mesh branch is written.

### 4.3 What would have been deterministic

For completeness, and to define the *eventual* implementation surface if the external
dependency were ever satisfied, these components were verified as deterministic:

| Condition | Verification | Deterministic rule available |
| :-- | :-- | :-- |
| Equivalent cross-sectional area of substitute ≥ replaced deformed tie | §9-21-6-2-3 | Yes — from existing area/diameter inputs |
| §9-21-6-2-1 tie spacing | already executable | Yes — `BG-TRANS-TIE-SPACING-001` |
| Plain wire excluded from ties | §9-4-8-1 + Table 9-4-5 | Yes — categorical FAIL |
| Deformed wire diameter 1.5–16 mm | §9-4-8-8 | Yes — numeric window, inclusive |
| Deformed wire > 16 mm → recompute as plain per §9-21-3-7 | §9-4-8-8 sentence 2 | Yes — redirect to an existing rule family |
| Yield cap 420 MPa for shear ties | §9-4-8-5 + Table 9-4-4 tie row | Yes — numeric cap |
| Conformity to INSO 11558 | §9-4-8-7 | **No** — external standard |
| Welded-mesh admissibility for a tie | §9-4-8-6 + Table 9-4-4 | **No** — ambiguous (§4.2) |

This is why a partial implementation was rejected: the deterministic components
(area equivalence, diameter window, yield cap, plain-wire exclusion) do **not**
constitute the clause's condition. A rule containing only them would PASS a
non-conforming wire and would therefore be a **false PASS** — explicitly prohibited.

### 4.4 Required BeamGenius inputs — audit result

Searched the existing domain/engine layer before considering any new input:

| Datum | Exists today? | Where |
| :-- | :-- | :-- |
| Reinforcement type (bar vs wire) | Partially | `SpiralSpliceBarType` (DEFORMED_BAR / DEFORMED_WIRE / PLAIN_WIRE), `WireSurfaceClass` |
| Plain vs deformed | Yes | `SpiralSpliceBarType`, `WireSurfaceClass`, `WireSurfaceClass`-derived routing in `development_length_mabhas9.py` |
| Wire diameter | Yes | tie/wire inputs across the transverse and development rules |
| Yield stress | Yes | `fyt`/`fy` inputs in shear, flexure, transverse rules |
| Equivalent-area information | Yes | `StirrupLayout.single_leg_area_mm2` / `av_mm2`; bundle equivalent-diameter rule |
| Welded-wire flag | Partially (mesh anchorage only) | `evaluate_wire_tie_utie` inputs; no *substitution* concept exists |
| **Material conformity to an external national standard** | **No** | **Nothing anywhere in `src/` or `docs/` references INSO 11558** (nor 3132 / 1-21056) |

Classification of the missing datum: it is **not** (A) derivable from existing data,
and adding it as (B) a new explicit input would not make the rule deterministic — a
boolean "wire conforms to INSO 11558" is a caller assertion about a document this
project cannot read, i.e. category **(C): depends on external
certification/specification information**. That is a blocking category, not an input
to be invented.

---

## 5. Decision

**`BG-TRANS-WIRE-SUBST-PENDING` remains `VERIFY_PENDING` with
`execution_allowed=False`. No rule was implemented, and no partial rule was
implemented.**

Precise reason:

1. **§9-4-8-7 (verified, printed p. 69) requires conformity to INSO 11558 for every
   material §9-21-6-2-3 permits.** That requirement is a product-conformity condition
   against an external national standard which is not in the repository, not
   supplied, not obtainable here, and not modelled as an input. Implementing D
   without it would create a FALSE PASS path; implementing it with a caller
   self-declaration would be an unverifiable assertion, not a deterministic
   evaluation. → gate condition *"no external source is required for the implemented
   branch"* fails.
2. **The welded-mesh branch is genuinely ambiguous** between §9-21-6-2-3's express
   permission and Table 9-4-4's shear/tie row via §9-4-8-6 (§4.2). → gate condition
   *"no unresolved ambiguity remains"* fails.
3. **The delivered evidence range is incomplete for the clause set**: §9-4-8-9's
   conditions continue past printed p. 69 (§2.11). §9-4-8-9 concerns longitudinal
   bars in special seismic systems and is therefore not expected to bear on D, but
   the truncation is recorded so that no future stage assumes §9-4-8 was read in its
   entirety.

Optional rule audit performed under section 4 of the brief: a partial rule would have
had to be *either* dishonest (ignore §9-4-8-7) *or* degenerate (block on a condition
it cannot evaluate). Neither is acceptable, so no rule was created.

### Rule ID

**None created.** No `RuleReference` was added, modified, promoted or deprecated.
`BG-TRANS-WIRE-SUBST-PENDING` keeps its existing identity, `VERIFY_PENDING` status and
`execution_allowed=False`.

---

## 6. Required inputs — as they would stand

For the record, if the external dependency were ever discharged, D would require:
substitute material class (deformed wire / welded mesh), substitute wire diameter(s),
substitute area or bar/wire count, the replaced deformed tie's area, yield stress,
and the §9-21-6-2-1 inputs already consumed by `BG-TRANS-TIE-SPACING-001`. The
mesh-equivalence geometry (wires per tie perimeter / equal-area construction) is **not**
currently modelled and would need a dedicated design decision. **None of these were
implemented**, and this list is a planning record only — it is not an implementation
claim, and it does not imply the remaining blockers may be bypassed.

---

## 7. A / B / C / E — unchanged

No new evidence on A, B, C or E was introduced, and none was reopened.

| Blocker | Clause | Status | Note |
| :-- | :-- | :-- | :-- |
| **A** `BG-TRANS-TIE-ANCHOR-PENDING` | §9-21-6-1-3-ب | `KEEP_BLOCKED` | Unchanged; not touched by D's dependency (D does not reach §9-21-6-1) |
| **B** `BG-TRANS-WIRE-TIE-PENDING` | §9-21-6-1-5 | `SOURCE_WORK_REQUIRED` | Unchanged; the H.12 datum ambiguity persists |
| **C** `BG-TRANS-TORSION-TIE-PENDING` | §9-21-6-1-6-ب & §9-21-6-2-7-ب | `KEEP_BLOCKED` | Unchanged; transitive on A |
| **E** `BG-TRANS-SPIRAL-SPLICE-SEL-PENDING` | §9-21-6-3-5-الف → §9-21-4-7-3 → **Mabhas 10** | `EXTERNAL_DEPENDENCY` | Unchanged. §9-4-7 (verified this stage) is **not** Mabhas 10 and does not discharge this dependency |

The four executable torsion routes
(`BG-TRANS-TORSION-TIE-135HOOK-001`, `-SEISMIC-HOOK-001`, `-STANDARD-HOOK-001`,
`-WIRE-ROUTE-001`) were not modified.

---

## 8. Validation

| Gate | Result |
| :-- | :-- |
| `PYTHONPATH=src pytest` | **673 passed** |
| `PYTHONPATH=src mypy --strict` | **clean — 23 source files** |
| Registry | **121 total / 63 executable / 48 blocked / 10 reference** — unchanged |
| Duplicate Rule IDs | **0** |
| §9-21-6 (clause-prefix predicate) | **21 executable / 5 blocked** — unchanged |
| `BG-TRANS-WIRE-SUBST-PENDING` | `execution_allowed=False`, `VERIFY_PENDING` — unchanged |
| `git diff --check` | clean |
| Engine governance | no new engine code, no new imports, no runtime file/PDF access added |
| Files changed | `docs/PHASE2F_STAGE_H14_D_RESOLUTION.md` only |

---

## 9. What remains, precisely

To promote D, one of the following is required — and nothing less:

1. **The content of INSO 11558**, or a determination by the project owner that
   §9-4-8-7 is out of scope for engine evaluation (a *scope* decision, which must be
   explicit and recorded, not an engine default). Without one of these, D's condition
   cannot be completed.
2. **A resolution of the mesh/tie ambiguity** in §4.2 — either an authoritative
   reading of Table 9-4-4's applicability to §9-21-6-2-3, or the remaining evidence
   range (printed p. 70 onward) if it bears on the clause.
3. Optionally, **printed p. 70** to complete §9-4-8-9 (recorded for completeness; not
   expected to affect D).

---

*H.14 is source verification only. §9-4-8 has now been read in full for the delivered
range, and the verified result is that its condition for §9-21-6-2-3 terminates in an
external product standard. No rule is implemented, and none may be implemented until
that is resolved.*
