# Phase 2F — Stage H.10: Resolution Plan for the Remaining Transverse-Reinforcement Blockers

**Status: DECISION / SOURCE-VERIFICATION ONLY — no rule is implemented or promoted in H.10.**

This document is the H.10 deliverable required by the stage scope: it decides, for
each of the five remaining §9-21-6 blockers (A–E), whether the blocker can be made
deterministic from **explicitly applicable, visually verified Mabhas 9 requirements**
alone — and it records the source evidence that settles each question.

H.10 inherits the H.9 audit (`docs/PHASE2F_STAGE_H9_REMAINING_BLOCKER_AUDIT.md`)
as the authoritative decision baseline and does not contradict it. Where H.10 adds
new evidence, that evidence is stated with the exact page and the crop
magnification used to read it.

---

## 1. Baseline

| Item | Value |
| :-- | :-- |
| Branch | `arena/b9cd291a-beamgenius` |
| H.9 commit (baseline) | `ccdc9f1` |
| `origin/main` | `df8067a` (untouched) |
| Source evidence | `df8067a:phase2f-source-442-472/` (committed; PDF 442–472 only) |
| Registry at entry | 121 total / 63 executable / 48 blocked / 10 reference-executable |
| §9-21-6 at entry | 21 executable / 5 blocked (predicate: clause field starts with `Clause`/`Clauses` `9-21-6`) |

Environment note: the sandbox resets between turns, so the source pages were
re-extracted from the committed evidence commit `df8067a` (never from a local
modification) and the repository was returned to `ccdc9f1` non-destructively.

---

## 2. Source evidence examined in H.10

All quotations are from the committed `.jpg` page images. OCR was navigation only.

| PDF page | Printed page | Content read this stage | Magnification |
| :-- | :-- | :-- | :-- |
| 445 | 425 | §9-21-3-1-6 — the **only** λ definition in the delivered window, with its scope wording | 4.5× |
| 460 | 440 | §9-21-4-7-1, -7-2, §9-21-4-5-1/-5-2, §9-21-4-6 heading | 4× |
| 461 | 441 | §9-21-4-7-3, -7-4, -7-5, -7-6, -7-7, -7-8 | 4×–7× |
| 463 | 443 | §9-21-6-1-3 (الف / ب / پ) — the whole branch (ب) sentence re-read | 4×–**16×** |
| 464 | 444 | §9-21-6-1-3 (پ), §9-21-6-1-4 (الف / ب), §9-21-6-1-5 (head / الف / ب), §9-21-6-1-6 | 4×–7× |
| 465 | 445 | Figure 9-21-1 (four panels) and its caption | 2.2×–4.5× |
| 466 | 446 | §9-21-6-2-3 | 4× |
| 468 | 448 | §9-21-6-3-5-الف, §9-21-6-2-7-ب | 4.5× |

---

## 3. A — `BG-TRANS-TIE-ANCHOR-PENDING`, §9-21-6-1-3-ب

### 3.1 Question

Can the branch be made deterministic using only explicitly applicable verified
Mabhas 9 requirements — specifically, can the **embedment-length datum**, the
**outer-hook comparison quantity**, and the **λ applicability** be resolved from
the governing source without importing assumptions from another clause?

### 3.2 Verbatim source (PDF 463 / printed 443)

> «ب- در میلگردهای به قطر ۱۸ تا ۲۵ میلی‌متر و تنش تسلیم بیش از ۲۸۰ مگاپاسکال،
> وجود قلاب استاندارد پیرامون میلگرد طولی به علاوه‌ی طول مدفون بین وسط ارتفاع
> مقطع و انتهای … و بیرونی قلاب بیشتر یا مساوی ۰.۱۷f_y/(λ√f_c)·d_b»

### 3.3 λ — evidence and verdict

| Check requested by the scope | Result |
| :-- | :-- |
| Is λ printed in the clause? | **YES** — the formula line was re-read at 16× on the `0.17` decimal point; the denominator is unambiguously `λ√f_c` |
| Where is λ defined? | **§9-21-3-1-6 only** (PDF 445 / printed 425): «۹-۲۱-۳-۱-۶ در محاسبه طول گیرایی، λ ضریب بتن سبک برای بتن سبک ۰/۷۵ و برای بتن معمولی ۱/۰ در نظر گرفته می‌شود.» |
| What is that definition's scope wording? | «در محاسبه طول گیرایی» — *in the development-length (l_d) calculation*. The definition is self-scoped to §9-21-3's l_d computation. |
| Does §9-21-6-1-3-ب explicitly invoke it? | **NO.** §9-21-6 cites §9-21-3 **nowhere**: a token search for any §9-21-3 citation form (including the deeper `9-21-3-1-6` form) over the OCR of **all pages 463–470** returns **0 hits**; the visual reads of pages 463 and 464 show only §9-21-6-internal clause numbers. |
| Verdict | **Applicability NOT established.** Adopting §9-21-3-1-6's λ inside this clause is an outside-clause substitution. Blocked. |

H.10 explicitly does **not** repeat the error of treating the existence of a
symbol elsewhere as proof that it applies here. The symbol exists; its
applicability to this clause does not.

### 3.4 Embedment-length datum — evidence and verdict

The requirement reads «طول مدفون بین وسط ارتفاع مقطع و انتهای …» — an embedment
length measured *between the mid-height of the section and the end of [ … ]*.

Checked: **is the missing referent lost to a page break?** No.

- The branch (ب) text is **complete on PDF 463**: it occupies three printed lines
  (the clause number line, the continuation line ending at «انتهای», and the
  formula line), and the next clause (پ) begins on the same page (y ≈ 2577 of
  3505).
- PDF 464 begins with a **new numbered clause, §9-21-6-1-4**, not with a
  continuation of (ب).

Therefore the ellipsis is intrinsic to the printed text: no continuation exists
on the following page that H.10 could have missed.

**Verdict: datum NOT resolved. Blocked.**

### 3.5 Outer-hook comparison quantity — evidence and verdict

The formula is compared against «بیرونی قلاب» ("the outer [ … ] of the hook") with
«بیشتر یا مساوی» (greater than or equal to). The compared physical quantity is
**not named** — no noun follows «بیرونی», and the clause does not state which
measurement of the hook is being bounded (nor its measurement datum).

H.10 performed no dimensional or analogical repair of this elision. (Recorded
explicitly: no analogy to the §9-21-3 hook-length equations is claimed, and no
ACI/other-code interpretation was consulted or substituted.)

**Verdict: quantity NOT resolved. Blocked.**

### 3.6 H.10 decision for A

Three independent obstacles, each individually fatal, none resolvable from
explicitly applicable verified source: **λ applicability (cannot be established
from §9-21-6), embedment datum (intrinsic elision), outer-hook quantity (intrinsic
elision)** — plus the three verbatim boundary gaps (f_y = 280 MPa exactly;
d_b = 17 mm; d_b > 25 mm).

**Decision: `KEEP_BLOCKED`.** No candidate. No Rule ID proposed.

---

## 4. B — `BG-TRANS-WIRE-TIE-PENDING`, §9-21-6-1-5

### 4.1 Question

Can the positioning requirements be represented with explicit geometric inputs and
deterministic checks?

### 4.2 Verbatim source (PDF 464 / printed 444)

> «۹-۲۱-۶-۱-۵ مهار دو انتهای خاموت متشکل از سیم جوش شده با تنها یک ساق، توسط دو
> سیم طولی با فاصله‌ی حداقل ۵۰ میلی‌متر از یک‌دیگر، با تامین شرایط زیر مجاز است.
> الف- وجود حداقل یک سیم طولی داخلی، با فاصله‌ی بیش‌تر از یک چهارم عمق موثر و
> ۵۰ میلی‌متر از نصف عمق موثر مقطع، هر کدام بزرگ‌تر است.
> ب- سیم طولی خارجی در وجه کششی باید از نزدیک‌ترین میلگردهای طولی اصلی خمشی، به
> وجه کششی نزدیک‌تر باشد.»

### 4.3 Precision note (transcription hazard)

The number **50 mm appears twice in this single clause with two different
meanings**: (i) the minimum spacing *between the two longitudinal wires*
(precondition); (ii) the «۵۰ میلی‌متر از نصف عمق موثر مقطع» term inside
sub-clause (الف). Any future transcription must keep them distinct.

### 4.4 Decisive new evidence — the sister clause names its datum

The immediately adjacent clause on the **same page**, §9-21-6-1-4-ب, addresses the
same quantity *class* (¼ of the effective depth) and prints its datum explicitly
(verified at 5×):

> «ب- وجود یک سیم طولی واقع در فاصله‌ای کمتر از یک چهارم عمق موثر **از وجه فشاری**،
> و سیم طولی دوم …»   (§9-21-6-1-4-ب)

By contrast, the §9-21-6-1-5-الف term reads «فاصله‌ی بیش‌تر از یک چهارم عمق
موثر» with **no face named** (verified at 7×).

This contrast settles the H.9 finding: the absence of the datum in §9-21-6-1-5 is a
**genuine omission in the printed clause**, not a reading artifact — the same
document writes «از وجه فشاری» when it means it. Importing §9-21-6-1-4's datum into
§9-21-6-1-5 would be reading a requirement out of a *different* clause, which the
governance forbids.

### 4.5 Figure check

Figure 9-21-1's caption (PDF 465, verified at 4.5×) reads:

> «شکل ۹-۲۱-۱ مهار در ناحیه‌ی فشاری خاموت U شکل متشکل از شبکه‌ی سیمی ساده‌ای جوش
> شده»

The figure is **explicitly a compression-zone figure** and belongs to the
§9-21-6-1-4 provisions (it is cited by §9-21-6-1-4's own preamble). §9-21-6-1-5
governs the wire on the **tension face** («وجه کششی» in its sub-clause ب) and cites
no figure. **No geometry for B can be read from Figure 9-21-1.**

### 4.6 Determinism verdict

| Requirement element | Deterministic? |
| :-- | :-- |
| Precondition: single-leg welded-wire tie; two longitudinal wires ≥ 50 mm apart | **Yes** (printed) |
| (الف) term 1: «> ¼ · d_eff» | **No** — no datum face printed |
| (الف) term 2: «50 mm from half the effective depth» | Partially — the «نصف عمق موثر» line is a positional datum, but the required measurement direction/face is not stated |
| (الف) «هر کدام بزرگ‌تر است» (whichever is greater) comparison | **Not evaluable** while term 1 is datum-less |
| (ب) outer wire closer to the tension face than the nearest main longitudinal bar | **No** — purely relative comparison, no governing number, no measurement procedure |

**Decision: `SOURCE_WORK_REQUIRED`.** The clause cannot be made deterministic from
the verified text alone. An authorised interpretation (or new authoritative source
material) is the prerequisite; H.10 does not supply one.

**Rule ID: NOT proposed.** Per the H.10 implementation policy, a Rule ID proposal
would imply a promotable rule; there is none. For planning completeness only — and
explicitly **not authorised, not a candidate** — the input shape a future stage
would need if the datums were ever authorised is: `delta_eff_depth_ratio`-style
explicit caller-measured distances (the idiom already used by
`BG-TRANS-WIRE-TIE-UTIE-001`), `wire_spacing_mm`, and two position values with
their faces. No formula may be executed from the present text.

---

## 5. C — `BG-TRANS-TORSION-TIE-PENDING` (remaining route only)

### 5.1 Question

Would resolving A completely resolve the remaining route?

### 5.2 Answer: yes — C has no independent work

Both (ب) clauses of §9-21-6-1-6 and §9-21-6-2-7 offer the OR alternatives
(§9-21-6-1-3-الف **or** §9-21-6-1-3-ب) **or** §9-21-6-1-4. Verified state of each:

| OR route | Status |
| :-- | :-- |
| §9-21-6-1-3-الف | Executable — `BG-TRANS-TIE-ANCHOR-STD-HOOK-001` |
| §9-21-6-1-4 | Executable — `BG-TRANS-TORSION-TIE-WIRE-ROUTE-001` (U-tie geometry delegated to `BG-TRANS-WIRE-TIE-UTIE-001`) |
| **§9-21-6-1-3-ب** | **Unimplemented — this is blocker A and the only uncovered route** |

C is therefore a **pure dependent of A**: it contains no source question of its
own, no separate datum, and no independent implementation work. If A is ever
resolved by authoritative source material, C's remaining route resolves with it
(under a separate promotion gate); until then C is blocked.

### 5.3 No-duplication confirmation (registry-verified this stage)

The four executable torsion rules were confirmed registered, `VERIFIED`,
`execution_allowed=True`, and present in the executable set — and were **not**
read-modified, duplicated, or regressed by H.10:

- `BG-TRANS-TORSION-TIE-135HOOK-001` (deps: none)
- `BG-TRANS-TORSION-TIE-SEISMIC-HOOK-001` (deps: `BG-TRANS-SEISMIC-HOOK-001`)
- `BG-TRANS-TORSION-TIE-STANDARD-HOOK-001` (deps: `BG-TRANS-STANDARD-HOOK-001`)
- `BG-TRANS-TORSION-TIE-WIRE-ROUTE-001` (deps: `BG-TRANS-WIRE-TIE-UTIE-001`)

**Decision: `KEEP_BLOCKED`** (transitively via A). No new rule.

---

## 6. D — `BG-TRANS-WIRE-SUBST-PENDING`, §9-21-6-2-3

### 6.1 Verbatim source (PDF 466 / printed 446)

> «۹-۲۱-۶-۲-۳ استفاده از سیم آجدار یا شبکه‌ی آرماتور سیم جوش شده به عنوان جایگزین
> تنگ آجدار، با سطح مقطع معادل میلگرد آجدار در نظر گرفتن الزامات ۹-۲۱-۶-۲-۱ و
> ۹-۴-۸ مجاز است.»

### 6.2 Exactly what is missing

| Named dependency | Status |
| :-- | :-- |
| §9-21-6-2-1 (tie spacing) | **Verified + executable** — `BG-TRANS-TIE-SPACING-001` (PDF 466 / printed 446) |
| **§9-4-8** (NBC Chapter 9-4, welded-wire steel specifications) | **Not delivered and not verified** |

Evidence for the §9-4-8 gap (verified this stage, not inferred from filenames):

1. A token search for any §9-4-8 citation form over the OCR of **all 31 committed
   pages (442–472)** returns **0 hits** — the sub-clause is not cited anywhere in
   the delivered window either.
2. No page of National Building Regulations **Chapter 9-4** exists in the
   committed evidence set; the window is PDF 442–472 / printed 442–450 only.
3. The numeric fragments §9-4-8-4 (E_s) and §9-4-8-5 (f_yt ≤ 420 MPa) that appear
   in `BG-FLEX-STRAIN-LIMIT` and `BG-SHEAR-VS-001` are verified from **their own**
   evidence pages for **their own** purposes. They do not verify the welded-wire
   steel specification that §9-21-6-2-3 requires, and a registry reference is not
   proof of verification.

**Exactly what is missing:** the welded-wire (mesh) steel material-specification
provisions of Chapter 9-4 §9-4-8 — i.e. the material requirements the substitution
must satisfy when a deformed wire or welded-wire mesh replaces a deformed tie.
Nothing may be substituted from another code, and no requirement may be inferred.

**Decision: `EXTERNAL_DEPENDENCY`** (= `NEEDS_NEW_SOURCE_EVIDENCE`). The unblocking
artifact is the NBC Chapter 9-4 page set containing §9-4-8. No candidate.

---

## 7. E — `BG-TRANS-SPIRAL-SPLICE-SEL-PENDING`, §9-21-6-3-5-الف

### 7.1 Verbatim source (PDF 468 / printed 448)

> «۹-۲۱-۶-۳-۵ وصله‌ی دورپیچ‌ها با یکی از روش‌های زیر انجام می‌شود
> الف- وصله‌ی جوشی یا مکانیکی مطابق بند ۹-۲۱-۴-۷.»

### 7.2 Exactly what is missing

The clause is a pure delegation to **§9-21-4-7**. H.10 read §9-21-4-7's sub-clauses
directly (PDF 460–461 / printed 440–441):

| Sub-clause | Content read | Governing evidence needed |
| :-- | :-- | :-- |
| -7-1 (PDF 460) | use of welded splices mainly for bars with diameter **20 mm** and above | in-window |
| -7-2 (PDF 460) | in welded splices for large-diameter bars, direct butt connection with penetration welding is preferred | in-window |
| **-7-3 (PDF 461)** | «جوش میلگردها در وصله‌های جوشی باید الزامات **مبحث دهم مقررات ملی ساختمان** را تامین نماید.» | **NBC Chapter 10 — NOT delivered** |
| -7-4 (PDF 461) | mechanical splices transfer force via sleeve / coupler / etc. | in-window |
| -7-5 (PDF 461) | adequate cover on the bar accounting for the bar-size increase caused by the mechanical splice | in-window |
| -7-6 (PDF 461) | «وصله‌ی مکانیکی یا جوشی باید قادر به انتقال تنشی حداقل برابر با **۱/۲۵** برابر تنش تسلیم میلگرد در کشش و یا فشار باشد.» — coefficient read at 7×; the «۱/۲۵» notation is 1.25 (the document's slash-with-no-leading-zero decimal convention for values ≥ 1, cf. «۰/۱۷» = 0.17 and «۰/۴۵» = 0.45 in the same evidence) | in-window |
| -7-7 (PDF 461) | adjacent bars spliced at the same section shall be staggered with a **750 mm** spacing along the splice | in-window |
| -7-8 (PDF 461) | [staggering] not required except in the tension members of §9-21-4-7-8 (arch ties / members delivering load to supports) | in-window |

**Finding of note:** the -7-6 coefficient is now **independently re-confirmed from
the page image as 1.25** (consistent with the value already recorded in the
project's documentation). This resolves one of the two blocking reasons carried by
the owning sentinel `BG-DEV-SPLICE-WELDED-MECH-PENDING`. **It does not unblock
anything:** the §9-21-4-7-3 → NBC Chapter 10 dependency remains completely
unsatisfied, and no page of Chapter 10 exists in the committed evidence.

Policy note: H.10 is a documentation-only stage. The owning sentinel's
`blocked_reason` string still carries the now-stale clause "the mechanical-splice
strength-transfer coefficient glyph was not independently re-confirmed".
**No registry file was modified.** Refreshing that reason string is recorded here
as an optional, behaviour-neutral future metadata action — it is deliberately
**not** performed in H.10, and it would not change the blocked status in any case.

### 7.3 Exactly what is missing (summary)

1. The **NBC Chapter 10** welding provisions referenced by §9-21-4-7-3 (pages not
   delivered; absent from the committed evidence).
2. A subsequent, separately gated promotion of §9-21-4-7 itself — which, even if
   achieved, would **not** automatically promote blocker E (separate source gate
   required, per the standing promotion policy).

**Decision: `EXTERNAL_DEPENDENCY`** (= `NEEDS_NEW_SOURCE_EVIDENCE`). No candidate.
No welded/mechanical splice selection is implemented.

---

## 8. H.10 decision matrix

| Blocker | Source status | Dependency status | Deterministic? | Candidate? | H.10 decision |
| :-- | :-- | :-- | :-- | :-- | :-- |
| **A** `BG-TRANS-TIE-ANCHOR-PENDING` (§9-21-6-1-3-ب, PDF 463) | Visually verified verbatim; clause complete on the page. λ printed (16×) but defined only at §9-21-3-1-6 (PDF 445) with l_d-scoped wording; §9-21-6 cites §9-21-3 nowhere. Embedment end-referent and outer-hook quantity both elided in print. | No registered deps. Would require §9-21-3-1-6 applicability — **not established**. | **No** | **No** | **`KEEP_BLOCKED`** |
| **B** `BG-TRANS-WIRE-TIE-PENDING` (§9-21-6-1-5, PDF 464) | Visually verified verbatim. Printed numbers: 50 mm (twice, distinct meanings), ¼·d_eff. The ¼·d_eff term carries **no datum face**, proven by the sister clause §9-21-6-1-4-ب on the same page printing «از وجه فشاری»; (ب) is a purely relative comparison. Figure 9-21-1 is a compression-zone figure for -1-4, not for -1-5. | No registered deps. | **No** | **No** (Rule ID deliberately withheld) | **`SOURCE_WORK_REQUIRED`** |
| **C** `BG-TRANS-TORSION-TIE-PENDING` (§9-21-6-1-6-ب & §9-21-6-2-7-ب, PDF 464/468) | Visually verified. OR routes: -1-3-الف ✔ executable, -1-4 ✔ executable, **-1-3-ب = blocker A**. | **Transitive on A** (pure dependent; no independent source question). | **No** | **No** | **`KEEP_BLOCKED`** |
| **D** `BG-TRANS-WIRE-SUBST-PENDING` (§9-21-6-2-3, PDF 466) | Visually verified verbatim. Own scope ("equivalent cross-sectional area") is deterministic. | §9-21-6-2-1 ✔ verified+executable; **§9-4-8 NOT delivered / not verified** (0 citations in the whole window; no Chapter 9-4 page). | **No** | **No** | **`EXTERNAL_DEPENDENCY`** (needs new source evidence) |
| **E** `BG-TRANS-SPIRAL-SPLICE-SEL-PENDING` (§9-21-6-3-5-الف, PDF 468) | Visually verified verbatim. Pure delegation to §9-21-4-7. | §9-21-4-7 sub-clauses read in-window (incl. re-confirmed 1.25 at -7-6); **§9-21-4-7-3 → NBC Chapter 10 NOT delivered**; owning sentinel `BG-DEV-SPLICE-WELDED-MECH-PENDING` non-executable. | **No** | **No** | **`EXTERNAL_DEPENDENCY`** (needs new source evidence) |

No `PROMOTE_TO_IMPLEMENTATION` decision was reachable: no blocker passes all eight
conditions of §9 below.

---

## 9. Implementation-policy gate (H.10 §6 policy applied to A–E)

A rule may be implemented only if **all** of the following hold. Status per blocker:

| Condition | A | B | C | D | E |
| :-- | :-: | :-: | :-: | :-: | :-: |
| 1. Governing Mabhas 9 text visually verified | ✔ | ✔ | ✔ | ✔ | ✔ |
| 2. Every required datum explicit | ✘ | ✘ | ✘ | ✘ | ✘ |
| 3. All dependencies verified | ✘ | ✔ | ✘ | ✘ | ✘ |
| 4. Applicability deterministic | ✘ | ✘ | ✘ | ✘ | ✘ |
| 5. No missing geometry/parameter | ✘ | ✘ | ✘ | ✘ | ✘ |
| 6. RuleReference can be completed | — | — | — | — | — |
| 7. Tests can cover boundary conditions | — | — | — | — | — |
| 8. No assumption required | ✘ | ✘ | ✘ | ✘ | ✘ |

**Result: no implementation in H.10.** The blocked-rule count is not reduced and
must not be reduced by assumption.

---

## 10. Validation of this stage (documentation-only)

| Gate | Result |
| :-- | :-- |
| `PYTHONPATH=src pytest` | **673 passed** (unchanged) |
| `PYTHONPATH=src mypy --strict` | **clean, 23 source files** |
| Registry | **121 total / 63 executable / 48 blocked / 10 reference-executable** |
| §9-21-6 (clause-prefix predicate) | **21 executable / 5 blocked** |
| Files changed by H.10 | `docs/PHASE2F_STAGE_H10_PLAN.md` **only** |
| Engineering behaviour | unchanged — no evaluator, formula, constant, registry entry or test was touched |
| Four executable torsion rules | verified present, `VERIFIED`, `execution_allowed=True`, not duplicated or modified |

---

## 11. Recommended subsequent actions (outside H.10)

1. **New source evidence (the only real unblocking path):**
   - NBC **Chapter 9-4** pages containing **§9-4-8** welded-wire steel
     specifications → would allow D (and `BG-DEV-LAP-WIRE-DEFORMED-PENDING`) to be
     re-evaluated.
   - NBC **Chapter 10** welding provisions → prerequisite for §9-21-4-7-3 and
     therefore for E's dependency chain.
2. **Authorised interpretation (only if the project ever chooses to pursue it):**
   for A — the λ scope for anchorage detailing, the embedment end datum, and the
   outer-hook quantity; for B — the datum face for the ¼·d_eff term and the
   measurement definition for the (ب) comparison. Until such authorisation exists,
   A stays `KEEP_BLOCKED` and B stays `SOURCE_WORK_REQUIRED`.
3. **Optional, behaviour-neutral metadata refresh** of the
   `BG-DEV-SPLICE-WELDED-MECH-PENDING` blocked-reason string (the 1.25 coefficient
   is now independently re-confirmed). Not performed in H.10; changes no status.
4. **No-regression rule:** any future promotion in this area must keep the four
   executable torsion rules, the two §9-21-6-1-3 branches (الف, پ), the
   §9-21-6-1-4 U-tie rule, and the spiral lap-splice selection rule unchanged.

---

*H.10 is decision-and-source-verification only; no rule is implemented or promoted in H.10.*
