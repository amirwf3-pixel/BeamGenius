# Phase 2F — Stage H.9: Remaining §9-21-6 Blocker Audit

**Status: AUDIT ONLY — no rule was implemented, promoted, or modified.**

> **H.9 is audit-only; no new executable rule is promoted in H.9.**

This document audits (a) the dependency status of the clauses that the remaining
§9-21-6 blockers route through, and (b) the five remaining blocked §9-21-6
sentinels themselves, against the **committed Phase 2F source evidence** and the
**actual registry metadata** (not filename, ID, or substring inference).

---

## 1. Purpose and scope

Stage H.9 audits exactly five registered blockers:

| # | Rule ID | Clause | PDF page | Printed page |
| :-- | :-- | :-- | :-- | :-- |
| A | `BG-TRANS-TIE-ANCHOR-PENDING` | §9-21-6-1-3-ب | 463 | 443 |
| B | `BG-TRANS-WIRE-TIE-PENDING` | §9-21-6-1-5 | 464 | 444 |
| C | `BG-TRANS-TORSION-TIE-PENDING` | §9-21-6-1-6-ب & §9-21-6-2-7-ب (remaining route) | 464–468 | 444–448 |
| D | `BG-TRANS-WIRE-SUBST-PENDING` | §9-21-6-2-3 | 466 | 446 |
| E | `BG-TRANS-SPIRAL-SPLICE-SEL-PENDING` | §9-21-6-3-5-الف | 468 | 448 |

Audit-only constraints honoured:

- No executable rule was added; no blocker was promoted or removed.
- No formula, constant, or engineering behaviour was changed.
- The executable registry set is unchanged (counts in §4 and §13).
- No metadata was changed (see §12 — nothing was proven wrong by the source).

Four already-executable torsion-tie rules were verified as untouched and are
**not** duplicated by this audit: `BG-TRANS-TORSION-TIE-135HOOK-001`,
`BG-TRANS-TORSION-TIE-SEISMIC-HOOK-001`,
`BG-TRANS-TORSION-TIE-STANDARD-HOOK-001`,
`BG-TRANS-TORSION-TIE-WIRE-ROUTE-001`.

---

## 2. Baseline and environment

| Item | Value |
| :-- | :-- |
| Branch | `arena/b9cd291a-beamgenius` |
| Baseline HEAD | `a7be6f7` (Stage H.8, pushed) |
| `origin/main` | `df8067a` (untouched by H.9) |
| Source evidence commit | `df8067a:phase2f-source-442-472/` |
| Registry | 121 total / 63 executable / 48 blocked / 10 reference-executable |

Note on reproducibility: the sandbox environment was reset between turns,
which removes `/tmp` build tool environments and the gitignored `working/`
directory. The source pages were re-extracted from the committed evidence at
`df8067a` (not from any local modification), and the repository was returned to
HEAD `a7be6f7` non-destructively. No source-evidence file was modified.

---

## 3. Source evidence used (visual, JPG-authoritative)

All quotations below were read from the committed `.jpg` page images. The OCR
`.txt` files were used for navigation only; where OCR was garbled (the formula
line of §9-21-6-1-3-ب is unreadable in OCR), the `.jpg` was the authority.

Pages visually inspected this stage:

| PDF page | Printed page | Content used |
| :-- | :-- | :-- |
| 445 | 425 | §9-21-3-1-5 (√f′c ceiling), **§9-21-3-1-6 (λ definition)** |
| 461 | 441 | §9-21-4-7-3 (welding → NBC Chapter 10), §9-21-4-7-4…-6 |
| 463 | 443 | **§9-21-6-1-3 (الف / ب / پ)** — active clause of blocker A |
| 464 | 444 | **§9-21-6-1-4, §9-21-6-1-5, §9-21-6-1-6** — blockers B and C |
| 465 | 445 | Figure 9-21-1 caption and §9-21-6-1-7 (checked for a datum figure) |
| 466 | 446 | **§9-21-6-2-2, §9-21-6-2-3** — blocker D |
| 468 | 448 | **§9-21-6-3-5-الف**, §9-21-6-2-7-ب — blockers C and E |

Window boundary check: the committed evidence set spans PDF 442–472 only.
No page of National Building Regulations Chapter 9-4 (incl. §9-4-8) and no page
of NBC Chapter 10 exists in the committed evidence set. This was verified by
listing the committed evidence directory, not by inference.

---

## 4. Current §9-21-6 counts and the predicate used

Counts are **predicate-dependent**. Both predicates are stated so no number is
quoted without its definition.

| Predicate | Rules | Executable | Blocked |
| :-- | :-- | :-- | :-- |
| A — `clause_or_equation` starts with singular `Clause 9-21-6` | 25 | 20 | 5 |
| B — `clause_or_equation` starts with `Clause`/`Clauses` `9-21-6` | 26 | **21** | **5** |

The only difference is `BG-TRANS-DORGIR-001`, whose clause field is written
`Clauses 9-21-6-4-1, 9-21-6-4-2 & 9-21-6-4-3` (plural, §9-21-6-4). Predicate B
is the one consistent with the standing count **21 executable / 5 blocked**.

The five blocked rules under predicate B are exactly the five audited in §1.
A raw substring search for `9-21-6` anywhere in the clause field returns 28
rules (23 executable); the three extra rules (`BG-DEV-LENGTH-HEADED-001`,
`BG-DEV-WIRE-DEFORMED-001`, `BG-TRANS-DORGIR-001`) merely cite §9-21-6 in
cross-references and are not §9-21-6 rules.

---

## 5. Dependency audit and dependency matrix

Legend: **Verified?** = the clause text was visually verified from committed
evidence. **Executable?** = a registered rule executes it today.

| Dependency | Verified? | Executable? | Relevant blocker(s) | Conclusion |
| :-- | :-- | :-- | :-- | :-- |
| **§9-4-8** (NBC Chapter 9-4, bar/wire material specifications) | **No — out of window.** No Chapter 9-4 page exists in `phase2f-source-442-472`. Only sub-clause numbers §9-4-8-4 (E_s = 200,000 MPa) and §9-4-8-5 (f_yt ≤ 420 MPa) + Table 9-4-4 appear as *citations* inside `BG-FLEX-STRAIN-LIMIT` and `BG-SHEAR-VS-001`, verified from their own evidence pages (PDF 22, 89–90, 140, 142–144 — outside this window). | No (no rule for §9-4-8 exists; the citing rules execute their own clauses). | **D** (and, transitively, `BG-DEV-LAP-WIRE-DEFORMED-PENDING`) | **EXTERNAL_DEPENDENCY.** The welded-wire-steel specification part of §9-4-8 that §9-21-6-2-3 needs is precisely the part with no verified page. Partial numeric verification of §9-4-8-4/-8-5 for *other* clauses does **not** verify §9-4-8 for the substitution rule. |
| **§9-21-4-7** (welded/mechanical splices) | **Yes** — §9-21-4-7-1…-7-8 read from PDF 460–461 / printed 440–441 (recorded in VERIFIED_RULES / matrix §4D as `VERIFIED_SOURCE_ONLY`). | **No** — registered as `BG-DEV-SPLICE-WELDED-MECH-PENDING`, `VERIFY_PENDING`, `execution_allowed=False`. Confirmed by direct registry query. | **E** (registered dependency), and the sentinel itself | **Blocked transitively.** Blocking causes: §9-21-4-7-3 → NBC Chapter 10; plus the mechanical-splice strength-transfer glyph that was not independently re-confirmed. |
| **Chapter 10 (مبحث دهم)** | **No — not delivered.** No page of it exists anywhere in the committed evidence. | No. | **E**; `BG-DEV-SPLICE-WELDED-MECH-PENDING` | **EXTERNAL_DEPENDENCY.** §9-21-4-7-3 explicitly requires Chapter 10 welding compliance; the text exists in-window but the referenced chapter does not. |
| **§9-20-6** (bar bending geometry) | No. | No. | **None** | **Not a dependency.** It is no longer cited by any §9-21-6 blocker's metadata; the historical "geometry lives in Clause 9-20-6" reason was corrected in Stage H.1, and the executable seismic-hook rule documents that «مطابق تعریف فصل ۹-۲۰» is terminological, not a dependency. No action. |
| **§9-21-4-3** (welded deformed-wire laps) | Yes — PDF 458 / printed 438. | **No** — `BG-DEV-LAP-WIRE-DEFORMED-PENDING` blocked on Chapter 9-4 welded-wire specs (incl. §9-4-8) and the §9-21-4-4 branch. | None of A–E directly | Non-executable, but not on any A–E route. Same out-of-window Chapter 9-4 cause as D. |
| **§9-21-4-2** (tension lap splices) | Yes — PDF 457–458 / printed 437–438. | **Yes** — `BG-DEV-LAP-TENSION-001`, `BG-DEV-LAP-TENSION-DIFFDIA-001` verified + executable. | None | Verified and executable; no A–E route consumes it. |
| **§9-21-4-1** (lap types/limits/spacing) | Yes — PDF 456–457 / printed 436–437. | **Yes** — `BG-DEV-LAP-APPLIC-001`, `BG-DEV-LAP-SPACING-001` verified + executable. | None | Verified and executable; no A–E route consumes it. |

Additional dependency-audit findings:

1. **`BG-DEV-SPLICE-WELDED-MECH-PENDING`** carries `dependencies=()` — its block
   is expressed in its own `blocked_reason` (Chapter 10 + unconfirmed glyph), not
   through a registered dependency edge. Verified by direct registry query, not
   by name similarity.
2. **`BG-DEV-LENGTH-PENDING`** is a *legacy placeholder* whose clause field reads
   `Clause 2-3-6-9 (Pending Verification in docs/DESIGN_RULES.md)` — a former OCR
   token, corrected in the project to Clause **9-21-3**, which is fully
   implemented and executable as eight rules (`BG-DEV-LENGTH-TENSION-001`,
   `-TABLE-001`, `-HOOKED-001`, `-HEADED-001`, `BG-DEV-MECH-ANCHOR-001`,
   `BG-DEV-WIRE-DEFORMED-001`, `BG-DEV-WIRE-PLAIN-001`,
   `BG-DEV-LENGTH-COMPRESSION-001`). The sentinel remains registered
   (`VERIFY_PENDING`, `execution_allowed=False`) for anything outside those rules
   and is a registered dependency of other blocked flexure rules
   (`BG-FLEX-EXT-PENDING`, `BG-INTEG-ANCHOR-PENDING`). **No §9-21-6 blocker
   depends on it.**
3. **λ is not a missing symbol — it is an out-of-scope definition.** This is the
   single most important new finding of H.9, and it is recorded in §6 (blocker A).

---

## 6. Blocker A — `BG-TRANS-TIE-ANCHOR-PENDING`

| Field | Value |
| :-- | :-- |
| Clause | §9-21-6-1-3-**ب** (the only remaining branch of the clause) |
| Source location | PDF p. 463 / printed p. 443 (footer ۴۴۳) |
| Registry status | `VERIFY_PENDING`, `execution_allowed=False`, `dependencies=()` |
| Classification | **KEEP_BLOCKED** |

### 6.1 Exact verified requirement (read verbatim from the JPG)

> «ب- در میلگردهای به قطر ۱۸ تا ۲۵ میلی‌متر و تنش تسلیم بیش از ۲۸۰ مگاپاسکال،
> وجود قلاب استاندارد پیرامون میلگرد طولی به علاوه‌ی طول مدفون بین وسط ارتفاع
> مقطع و انتهای … و بیرونی قلاب بیشتر یا مساوی ۰.۱۷f_y/(λ√f_c)·d_b»

The inequality was read from a ≥5× crop of the printed line; the printed
expression is unambiguous: numerator `0.17 f_y`, denominator `λ √f_c` (radical
over f_c), multiplied by `d_b`, compared with «بیرونی قلاب» by «بیشتر یا مساوی»
(greater than or equal to).

Sibling branches (already promoted and unchanged): (الف) →
`BG-TRANS-TIE-ANCHOR-STD-HOOK-001` (§9-21-6-1-3-الف), (پ) →
`BG-TRANS-TIE-ANCHOR-JOIST-STD-HOOK-001` (§9-21-6-1-3-پ). This audit does not
touch them.

### 6.2 Numerical conditions (verified)

| Condition | Value | Evidence |
| :-- | :-- | :-- |
| Bar diameter range | 18–25 mm | printed «۱۸ تا ۲۵ میلی‌متر» |
| Yield-stress condition | f_y > 280 MPa | printed «تنش تسلیم بیش از ۲۸۰ مگاپاسکال» |
| Outer-hook minimum | ≥ 0.17·f_y / (λ·√f′c) · d_b | printed formula line |
| Genuine boundary gaps (unchanged) | f_y = 280 MPa exactly; d_b = 17 mm; d_b > 25 mm | printed ranges exclude them |

### 6.3 λ — present in the source, but defined out of scope

**λ IS printed in the source formula** of §9-21-6-1-3-ب. The audit therefore
records that the blocker's difficulty is *not* a missing symbol.

What §9-21-6 contains: no definition of λ anywhere in §9-21-6-1-3, §9-21-6-1-4,
§9-21-6-1-5, §9-21-6-1-6, or §9-21-6-3.

What *is* in the verified window (visual, PDF p. 445 / printed p. 425):

> «۹-۲۱-۳-۱-۶ در محاسبه طول گیرایی، λ ضریب بتن سبک برای بتن سبک ۰/۷۵ و برای بتن
> معمولی ۱/۰ در نظر گرفته می‌شود.»

That definition is scoped by its own wording to «در محاسبه طول گیرایی» — *in the
development-length (l_d) calculation* of §9-21-3. §9-21-6-1-3-ب is an anchorage
detailing clause, not the development-length calculation; it prints the symbol
without citing §9-21-3-1-6. Adopting the §9-21-3 λ inside this clause is an
**outside-clause substitution** and is not permitted without an authorised
interpretation. H.9 does **not** perform it and does **not** recommend it as a
source-verified fact.

### 6.4 Positional / anchorage data (verified as *under-specified*)

1. **Embedment length.** The requirement is «طول مدفون بین وسط ارتفاع مقطع و
   انتهای …» — an embedment length measured *between the mid-height of the
   section and the end of …*. The line ends at «انتهای» (hence the ellipsis
   printed by earlier stages) and the text resumes with a separate item; no
   figure on this page or on the facing page (PDF 465) supplies the missing
   referent. This is the positional datum the sentinel records. H.9 does not
   resolve it.
2. **Compared quantity of the inequality.** The left-hand side is «بیرونی قلاب»
   ("the outer [aspect] of the hook"), compared with a length. The physical
   quantity (e.g. outer bend diameter vs. outer extent) is not printed with its
   noun. This is a second elision, recorded here rather than resolved.
3. **Enclosure requirement.** «قلاب استاندارد پیرامون میلگرد طولی» — the hook
   must enclose the longitudinal bar. This part *is* deterministic and is already
   modelled by the promoted sibling rules through
   `encloses_longitudinal_bar`; it is not the blocking cause.

### 6.5 Determinism assessment

- Given (i) an authorised λ for this clause, (ii) a defined end datum for the
  embedment length, and (iii) a named outer-hook quantity with its measurement
  datum, the branch would be computable.
- **None of the three is supplied by the verified source today.** Each requires
  either new source pages (e.g. an NBC chapter defining λ for anchorage detailing
  / a clarifying figure) or an authorised interpretation.
- Required hypothetical inputs (recorded for a future stage, not implemented):
  `bar_diameter_mm`, `yield_stress_mpa`, `fc_mpa`, `lambda`, `embedment_length_mm`
  (with datum), outer-hook quantity (with datum), plus the delegated standard-hook
  geometry via `BG-TRANS-STANDARD-HOOK-001`.

### 6.6 Why it remains blocked and recommended next action

Blocking causes: **λ scope (SOURCE_VERIFICATION_REQUIRED)** and **two
under-specified datums (GENUINE_GAP)**, plus the three **GENUINE_GAP** boundary
values. None may be filled from engineering knowledge or from ACI/other codes.

Recommended next action: leave blocked. If a future stage wishes to pursue
branch (ب), it must first obtain authoritative source material that defines λ for
this clause and the two datums; otherwise the branch stays permanently blocked.

---

## 7. Blocker B — `BG-TRANS-WIRE-TIE-PENDING`

| Field | Value |
| :-- | :-- |
| Clause | §9-21-6-1-5 |
| Source location | PDF p. 464 / printed p. 444 (footer ۴۴۴) |
| Registry status | `VERIFY_PENDING`, `execution_allowed=False`, `dependencies=()` |
| Classification | **SOURCE_VERIFICATION_REQUIRED** (execution stays blocked) |

### 7.1 Exact verified requirement (read verbatim from the JPG)

> «۹-۲۱-۶-۱-۵ مهار دو انتهای خاموت متشکل از سیم جوش شده با تنها یک ساق، توسط دو
> سیم طولی با فاصله‌ی حداقل ۵۰ میلی‌متر از یک‌دیگر، با تامین شرایط زیر مجاز است.
> الف- وجود حداقل یک سیم طولی داخلی، با فاصله‌ی بیش‌تر از یک چهارم عمق موثر و
> ۵۰ میلی‌متر از نصف عمق موثر مقطع، هر کدام بزرگ‌تر است.
> ب- سیم طولی خارجی در وجه کششی باید از نزدیک‌ترین میلگردهای طولی اصلی خمشی، به
> وجه کششی نزدیک‌تر باشد.»

### 7.2 Findings

- **Printed numbers exist**: 50 mm minimum wire-to-wire spacing; one quarter of
  the effective depth; 50 mm. The sub-clause (الف) is a "whichever is greater"
  comparison of two distances.
- **Printed precondition exists**: two longitudinal wires at least 50 mm apart,
  forming the two ends of single-leg welded-wire tie.
- **Under-specified measure datum (الف)**: the clause does not state from which
  reference the «۵۰ میلی‌متر از نصف عمق موثر مقطع» distance is measured (nor how
  "half the effective depth" is used as a datum). The "whichever is greater"
  comparison cannot be evaluated until that datum is fixed.
- **Under-specified comparison (ب)**: the outer wire must be «به وجه کششی
  نزدیک‌تر» than the nearest main flexural longitudinal bar. This is a purely
  relative, position-based requirement with **no governing number** and no stated
  measurement procedure.
- **Figure check**: §9-21-6-1-5 does not cite Figure 9-21-1. (Figure 9-21-1 on
  PDF 465 illustrates the U-shaped tie arrangement and carries dimension callouts
  such as «۵۰ mm» and «حداکثر l/4» but is the figure for the U-tie provisions of
  §9-21-6-1-4; it is not referenced by §9-21-6-1-5 and no geometry is read from
  it here.)
- **Determinism verdict: NO.** The requirements are not objectively testable as
  written without an authorised interpretation of (الف)'s datum and (ب)'s
  relative comparison. Missing required engineering input therefore keeps the
  rule blocked; no candidate is proposed.

### 7.3 Recommended next action

Remain blocked. Any promotion would require an authorised interpretation of the
two datums (SOURCE_VERIFICATION_REQUIRED), which H.9 does not supply and does not
invent. If such an interpretation is ever authorised, the caller-measured-input
idiom already used by `BG-TRANS-WIRE-TIE-UTIE-001` is the only permissible shape
for an implementation.

---

## 8. Blocker C — `BG-TRANS-TORSION-TIE-PENDING` (remaining route only)

| Field | Value |
| :-- | :-- |
| Clause | §9-21-6-1-6-ب **and** §9-21-6-2-7-ب |
| Source location | PDF 464 / printed 444 and PDF 468 / printed 448 |
| Registry status | `VERIFY_PENDING`, `execution_allowed=False`, `dependencies=()` |
| Classification | **KEEP_BLOCKED** (transitively via blocker A) |

### 8.1 What is already executable (verified untouched)

Four rules are registered, executable and were **not** modified or duplicated by
H.9: `BG-TRANS-TORSION-TIE-135HOOK-001` (§9-21-6-1-6-الف),
`BG-TRANS-TORSION-TIE-SEISMIC-HOOK-001`,
`BG-TRANS-TORSION-TIE-STANDARD-HOOK-001` (§9-21-6-2-7-الف options), and
`BG-TRANS-TORSION-TIE-WIRE-ROUTE-001` (the §9-21-6-1-4 wire route of the (ب)
branches, promoted in Stage H.7).

### 8.2 Exactly what remains uncovered

Verbatim from the JPGs:

> §9-21-6-1-6-ب (PDF 464): «ب- در مواردی که بتن پیرامون مهار به دلیل وجود بال یا
> دال مستعد متلاشی شدن نیست، مهار را می‌توان با لحاظ نمودن الزامات
> ۹-۲۱-۶-۱-۳-الف یا ب، و یا ۹-۲۱-۶-۱-۴ تامین نمود.»

> §9-21-6-2-7-ب (PDF 468): «ب- در مواردی که بتن پیرامون مهار به دلیل وجود بال یا
> دال مستعد متلاشی شدن نیست، باید الزامات بندهای ۹-۲۱-۶-۱-۳-الف یا ب، یا
> ۹-۲۱-۶-۱-۴ تامین گردد.»

Both clauses offer the OR alternatives: (§9-21-6-1-3-الف **or** §9-21-6-1-3-ب)
**or** §9-21-6-1-4. The §9-21-6-1-4 alternative is executable (H.7). The
§9-21-6-1-3-الف alternative is executable (H.7). **The only unimplemented route
remaining is §9-21-6-1-3-ب**, which is exactly blocker A and inherits every one of
its blocking causes (λ scope, embedment datum, elided outer-hook quantity, and
the three boundary gaps). The (ب) clauses as a whole are therefore retained as
blocked, consistent with the standing OR-delegation semantics (implementing one
OR route never promotes the whole clause).

### 8.3 Recommended next action

Remain blocked until blocker A is resolvable by authoritative source material.
No new rule is proposed; no duplication of the four executable torsion rules.

---

## 9. Blocker D — `BG-TRANS-WIRE-SUBST-PENDING`

| Field | Value |
| :-- | :-- |
| Clause | §9-21-6-2-3 |
| Source location | PDF p. 466 / printed p. 446 (footer ۴۴۶) |
| Registry status | `VERIFY_PENDING`, `execution_allowed=False`, `dependencies=()` |
| Classification | **EXTERNAL_DEPENDENCY** (execution stays blocked) |

### 9.1 Exact verified requirement (read verbatim from the JPG)

> «۹-۲۱-۶-۲-۳ استفاده از سیم آجدار یا شبکه‌ی آرماتور سیم جوش شده به عنوان جایگزین
> تنگ آجدار، با سطح مقطع معادل میلگرد آجدار در نظر گرفتن الزامات ۹-۲۱-۶-۲-۱ و
> ۹-۴-۸ مجاز است.»

Two dependencies are named by the clause itself: **§9-21-6-2-1** and **§9-4-8**.

### 9.2 Dependency verdicts

- **§9-21-6-2-1** (tie spacing): verified and executable as
  `BG-TRANS-TIE-SPACING-001` (PDF 466 / printed 446). Not a blocker.
- **§9-4-8**: **NOT verified and NOT executable.** Findings:
  1. The clause belongs to NBC Chapter 9-4 (bar/wire material specifications);
     **no page of Chapter 9-4 exists in the committed evidence set** (PDF
     442–472 only). This was verified by listing the committed evidence, not
     inferred from a filename.
  2. Registry query confirms no rule executes §9-4-8. The two rules whose clause
     fields *cite* §9-4-8 numbers — `BG-FLEX-STRAIN-LIMIT` (§9-4-8-4, E_s) and
     `BG-SHEAR-VS-001` (§9-4-8-5, f_yt ≤ 420 MPa) — use their own, different
     evidence pages (PDF 22 and 89–90/140/142–144). **A registry reference is not
     proof of verification, and verifying a numeric sub-clause for another
     clause's purpose does not verify §9-4-8 for the welded-wire substitution.**
  3. The part of §9-4-8 that §9-21-6-2-3 needs is precisely the welded-wire
     (mesh) steel specification, for which no verified page exists.
- The "equivalent cross-sectional area" part of §9-21-6-2-3 is itself
  deterministic, but the rule as a whole consumes an unverified external clause,
  so it cannot execute.

### 9.3 Recommended next action

Remain blocked. The prerequisite is delivery and verification of the NBC
Chapter 9-4 pages containing §9-4-8 welded-wire steel specifications (and,
transitively, the same material for `BG-DEV-LAP-WIRE-DEFORMED-PENDING`). Until
then no candidate exists.

---

## 10. Blocker E — `BG-TRANS-SPIRAL-SPLICE-SEL-PENDING`

| Field | Value |
| :-- | :-- |
| Clause | §9-21-6-3-5-الف |
| Source location | PDF p. 468 / printed p. 448 (footer ۴۴۸) |
| Registry status | `VERIFY_PENDING`, `execution_allowed=False`, registered dependency `BG-DEV-SPLICE-WELDED-MECH-PENDING` |
| Classification | **EXTERNAL_DEPENDENCY** (execution stays blocked) |

### 10.1 Exact verified requirement (read verbatim from the JPG)

> «۹-۲۱-۶-۳-۵ وصله‌ی دورپیچ‌ها با یکی از روش‌های زیر انجام می‌شود
> الف- وصله‌ی جوشی یا مکانیکی مطابق بند ۹-۲۱-۴-۷.»

(The lap-splice alternative, (ب), is already executable as
`BG-TRANS-SPIRAL-SPLICE-LAP-SEL-001` and is untouched.)

### 10.2 Dependency audit for §9-21-4-7 / Chapter 10

Verified visually from PDF 461 / printed 441:

> «۹-۲۱-۴-۷-۳ جوش میلگردها در وصله‌های جوشی باید الزامات مبحث دهم مقررات ملی
> ساختمان را تامین نماید.»

Findings:

1. **§9-21-4-7** itself is *in-window* (PDF 460–461 / printed 440–441) and its
   sub-clauses (-1…-8) were read: welded splices mainly d_b ≥ 20 mm; mechanical
   splice load transfer by sleeve/coupler; cover provision; **≥ 1.25·f_y** tensile
   or compressive transfer (-4-7-6); staggering of adjacent splices (-7-7/-8).
2. **Executability: NO.** The rule that owns it — `BG-DEV-SPLICE-WELDED-MECH-PENDING`
   — is `VERIFY_PENDING` / `execution_allowed=False`, confirmed by direct registry
   query. Its `blocked_reason` records two causes: the Chapter 10 welding
   requirement at §9-21-4-7-3, and the mechanical-splice strength-transfer
   coefficient glyph that was not independently re-confirmed.
3. **Chapter 10 («مبحث دهم») is entirely absent from the committed evidence.**
   The clause text exists in-window; the referenced chapter does not. No page of
   it can be verified today.
4. **No sub-branch of §9-21-6-3-5-الف escapes §9-21-4-7.** The clause is a pure
   delegation ("مطابق بند ۹-۲۱-۴-۷"), so its determinism is exactly the
   determinism of the delegated clause.
5. The engine's gatekeeper enforces this transitively via the registered
   dependency edge (`BG-TRANS-SPIRAL-SPLICE-SEL-PENDING` → `BG-DEV-SPLICE-WELDED-MECH-PENDING`),
   returning `UNVERIFIED_RULE_BLOCKED`; no formula is executed.

### 10.3 Recommended next action

Remain blocked. Prerequisites: delivery + verification of the NBC Chapter 10
welding provisions (for §9-21-4-7-3) and independent re-confirmation of the
mechanical-splice strength-transfer glyph, after which §9-21-4-7 could be
promoted in its own stage — that promotion would still *not* automatically
promote blocker E (separate source-verification gate required).

---

## 11. Classification summary and implementation candidates

| Blocker | Clause | Classification | Implementation candidate in H.9 |
| :-- | :-- | :-- | :-- |
| A `BG-TRANS-TIE-ANCHOR-PENDING` | §9-21-6-1-3-ب | **KEEP_BLOCKED** — λ defined out of clause scope (SOURCE_VERIFICATION_REQUIRED) + two under-specified datums (GENUINE_GAP) + three boundary gaps (GENUINE_GAP) | **NONE** |
| B `BG-TRANS-WIRE-TIE-PENDING` | §9-21-6-1-5 | **SOURCE_VERIFICATION_REQUIRED** — printed numbers but an unauthorised interpretation of two datums is a prerequisite | **NONE** |
| C `BG-TRANS-TORSION-TIE-PENDING` | §9-21-6-1-6-ب & §9-21-6-2-7-ب | **KEEP_BLOCKED** — remaining route is §9-21-6-1-3-ب, which is blocker A | **NONE** |
| D `BG-TRANS-WIRE-SUBST-PENDING` | §9-21-6-2-3 | **EXTERNAL_DEPENDENCY** — §9-4-8 welded-wire specs out of window | **NONE** |
| E `BG-TRANS-SPIRAL-SPLICE-SEL-PENDING` | §9-21-6-3-5-الف | **EXTERNAL_DEPENDENCY** — §9-21-4-7 → NBC Chapter 10 not delivered | **NONE** |

**No implementation candidate exists.** Every remaining blocker is either gated
on source material that is absent from the committed evidence, or on an
authorised interpretation that governance forbids H.9 (and any audit stage) from
supplying. `IMPLEMENTATION_CANDIDATE` was therefore assigned to none of A–E.
BLOCKED was never converted to PASS; VERIFY_PENDING remains non-executable.

Genuine source gaps preserved verbatim (never interpolated): f_y = 280 MPa
exactly; d_b = 17 mm; d_b > 25 mm.

---

## 12. Metadata corrections

**None.** Each reviewed `RuleReference` field was compared against the source and
registry behaviour:

| Check | Result |
| :-- | :-- |
| A's clause field `Clause 9-21-6-1-3-ب` + print/PDF pages (443/463) | correct |
| A's `blocked_reason`: datum positional, λ not defined in §9-21-6, no outside-code substitution permitted | correct and **confirmed**; H.9 adds (does not contradict) that λ is *printed* in the formula and *defined elsewhere in-window only for the l_d calculation* |
| B's clause field and pages (444/464) | correct |
| C's clause field `9-21-6-1-6-ب & 9-21-6-2-7-ب` and pages (444–448/464–468) | correct; the §9-20-6 correction from Stage H.1 stands |
| D's clause field and pages (446/466) | correct |
| E's clause field and pages (448/468), dependency `BG-DEV-SPLICE-WELDED-MECH-PENDING` | correct |
| §9-21-6 count assertions in tests | unchanged and still satisfied (see §13) |

No metadata file was modified in H.9.

---

## 13. Gates, governance and no-implementation confirmation

| Gate | Result |
| :-- | :-- |
| `pytest` | **673 passed** (unchanged from the H.8 baseline) |
| `mypy --strict` | **clean, 23 source files** |
| `git diff --check` | clean |
| Registry duplicate/ID integrity | 121 unique IDs, no duplicates |
| Registry totals | **121 total / 63 executable / 48 blocked / 10 reference-executable** |
| §9-21-6 (predicate B) | **21 executable / 5 blocked** (unchanged) |
| Engine AST / import governance | unchanged; no new module, no reference-package import, no runtime file/PDF/OCR read |
| Executable-rule behaviour | unchanged — no evaluator, formula, constant or registry entry was touched |
| Files changed in the H.9 commit | `docs/PHASE2F_STAGE_H9_REMAINING_BLOCKER_AUDIT.md` **only** |

Exact-set and count assertions were not updated: no count changed.

---

## 14. Recommended next actions (for a future, non-H.9 stage)

1. **Source acquisition** (the only true unblocking path): obtain the NBC
   Chapter 9-4 pages containing §9-4-8 welded-wire steel specifications (unblocks
   D and, transitively, `BG-DEV-LAP-WIRE-DEFORMED-PENDING`) and the NBC Chapter 10
   welding provisions (unblocks E's dependency chain).
2. **Interpretation authorisation**: if branch (ب) of §9-21-6-1-3 or §9-21-6-1-5
   is ever to be implemented, obtain an authorised, documented interpretation of
   (i) the λ scope for anchorage detailing, (ii) the embedment-length end datum,
   (iii) the outer-hook compared quantity, and (iv) §9-21-6-1-5's measure datum.
   Until then, these stay BLOCKED — not assumed.
3. **No-regression rule**: any future promotion in this area must keep the four
   executable torsion-tie rules, the two §9-21-6-1-3 branches (الف, پ), the
   §9-21-6-1-4 U-tie rule, and the spiral lap-splice selection rule unchanged.

---

*H.9 is audit-only; no new executable rule is promoted in H.9.*
