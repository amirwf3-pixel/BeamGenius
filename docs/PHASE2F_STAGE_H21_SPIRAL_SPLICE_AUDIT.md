# Phase 2F — Stage H.21: Targeted Audit of Blocker E

**`BG-TRANS-SPIRAL-SPLICE-SEL-PENDING` — §9-21-6-3-5(الف)**

**DECISION: `REMAINS BLOCKED — SOURCE AMBIGUITY` (outcome D; primary cause the
§9-21-4-7-5 cover obligation, secondary cause the §9-21-4-7-6 capacity-input gap and the
§9-21-4-7-3 → NBC Chapter 10 external dependency).**

**No rule was promoted**, no evaluator was written, no status, count or
`execution_allowed` flag was changed. One **authorised documentation correction** was made
(the stale coefficient claim on the delegate sentinel) — it changes no status, no count and
no execution behaviour.

This stage targeted **blocker E only**. H.18/H.19/H.20 were not reopened; A, B, C and D
were not modified; scope was not broadened.

---

## 1. Scope

| | |
| :-- | :-- |
| Target rule | `BG-TRANS-SPIRAL-SPLICE-SEL-PENDING` |
| Governing clause | §9-21-6-3-5(الف) (printed p. 448 / PDF p. 468) |
| Dependency under audit | §9-21-4-7 and its subclauses -7-1 … -7-8 (printed pp. 440–441 / PDF pp. 460–461) |
| Objective | Determine whether the welded/mechanical splice-selection route can be fully promoted |
| Method | Full-resolution visual inspection (3.2×–8×) of the source pages; subclause classification; cover/capacity analysis; external-standard sweep; engine input-model check; delegate audit; promotion gate |
| Out of scope (untouched) | A, B, C, D; UI, reports, DXF, optimisation; unrelated rules |

---

## 2. Baseline

| Item | Value |
| :-- | :-- |
| HEAD at stage start | **`3df5091`** (local HEAD was stale at `f22ff45`; recovered to `3df5091` without `--hard`, without rewriting history) |
| Commit chain confirmed | `0598116` (H.20) · `3df5091` (H.20 SHA backfill) |
| Working tree | clean |
| Branch | `arena/b9cd291a-beamgenius` |
| `origin/main` | **`df8067a750ffc7984c9dc5d80220ad9013503aa6`** — untouched |
| Evidence | `phase2f-source-442-472/` on `origin/main` @ `df8067a`, read **read-only** into git-ignored `working/h21/` |
| `pytest` | **673 passed** |
| `mypy --strict` | **clean — 23 source files** |
| Registry | **121 / 63 executable / 48 blocked / 10 reference** |
| Duplicate Rule IDs | **0** |
| §9-21-6 | **21 executable / 5 blocked** |

---

## 3. §9-21-6-3-5(الف) source verification

Read verbatim from PDF 468 / printed ۴۴۸ at 3.6× (footer-confirmed):

> «۹-۲۱-۶-۳-۵ وصلهی دورپیچها با **یکی از روشهای زیر** انجام میشود.
>
> **الف-** وصلهی **جوشی یا مکانیکی** مطابق بند ۹-۲۱-۴-۷.
>
> **ب-** وصلهی پوششی مطابق بند ۹-۲۱-۶-۳-۶ برای میلگردهای با تنش تسلیم کمتر یا مساوی ۴۲۰ مگاپاسکال.»

| # | Question | Finding |
| :-- | :-- | :-- |
| 1 | Exact chapeau | «وصلهی دورپیچها با یکی از روشهای زیر انجام میشود.» — an **explicit disjunction** («یکی از … زیر», one of the following) |
| 2 | Condition for the spiral/tie splice route | Branch (الف) requires the splice to be **welded or mechanical**, and to comply with **Clause 9-21-4-7** |
| 3 | OR or AND choice? | **OR at the selector level** — (الف) and (ب) are alternatives under «یکی از روشهای زیر». Branches (الف)-weld / (الف)-mech are also a stated OR («جوشی یا مکانیکی») |
| 4 | Cross-reference to §9-21-4-7 | **EXPLICIT** — «مطابق بند ۹-۲۱-۴-۷» (verified at 3.6×). The dependency edge `E → BG-DEV-SPLICE-WELDED-MECH-PENDING` is therefore **source-correct** |
| 5 | Conditions embedded in the wording previously overlooked? | **None.** (الف) is a bare delegation: it adds no condition, no threshold and no figure |
| 6 | Welded / mechanical / lap / selector? | It is a **selector among splice types** whose (الف) branch is a **welded-or-mechanical** route; the **lap** route is branch (ب), already promoted in Stage H.5 |

**Recorded source dependency:** §9-21-6-3-5(الف) → §9-21-4-7 (all of -7-1 … -7-8). The
clause's own boundary condition (f_y ≤ 420 MPa) belongs to branch (ب), **not** (الف).

---

## 4. §9-21-4-7 dependency trace

Chapeau, PDF 460 / printed ۴۴۰ (read at 4×):

> «۹-۲۱-۴-۷ وصلهی مکانیکی و جوشی میلگردهای آجدار در کشش و فشار»

The clause is a single block of eight subclauses spanning printed 440–441. **No subclause
is skipped and none carries an undeclared external edge except -7-3** (see §5).

| Subclause | Page | Content (verbatim gist) | Applies to |
| :-- | :-- | :-- | :-- |
| -7-1 | 440 | «استفاده از وصلههای جوشی عمدتا برای میلگردهای با قطر ۲۰ میلیمتر و بیشتر **توصیه میشود**» | **welded** |
| -7-2 | 440 | «در وصلههای جوشی برای میلگردهای با قطر زیاد، استفاده از اتصال سر به سر مستقیم با جوش نفوذی **ارجحیت دارد**» | **welded** |
| -7-3 | 441 | «جوش میلگردها در وصلههای جوشی باید الزامات **مبحث دهم** مقررات ملی ساختمان را تامین نماید» | **welded** |
| -7-4 | 441 | «در وصلههای مکانیکی انتقال نیرو از طریق غلاف اتکایی، **کوپلر**، غلاف کوپل کننده **و غیره** انجام میگیرد» | **mechanical** |
| -7-5 | 441 | «برای تامین **پوشش بتنی کافی** روی میلگرد، اثر **افزایش ابعاد میلگرد** ناشی از وصلهی مکانیکی باید در نظر گرفته شود» | **mechanical** |
| -7-6 | 441 | «وصلهی مکانیکی یا جوشی باید قادر به انتقال تنشی حداقل برابر با **۱/۲۵** برابر تنش تسلیم میلگرد در کشش و یا فشار باشد» | **both** |
| -7-7 | 441 | «یک در میان بودن میلگردهای با وصلهی مکانیکی یا جوشی در هر مقطع از عضو، به جز در اعضای کششی بند ۹-۲۱-۴-۷-۸ **الزامی نیست**» | **both** |
| -7-8 | 441 | «در اعضای کششی نظیر عضو کششی قوسها، عضو کششی که بار را به تکیهگاهی در تراز بالاتر منتقل میکند، و عضو کششی خرپاها، وصلهی جوشی یا مکانیکی در میلگردهای مجاور باید با فاصلهی **۷۵۰ میلیمتر** در امتداد وصله انجام شود. … در اعضای کششی نظیر دیوار مخازن دایروی … **الزامی نیست**» | **both**, conditional |

---

## 5. Subclause classification (7-1 … 7-8)

| Subclause | Classification |
| :-- | :-- |
| -7-1 | **Qualitative recommendation** — «توصیه میشود» (is recommended). Not a mandatory requirement |
| -7-2 | **Descriptive preference** — «ارجحیت دارد» (is preferred). Welded-only. Produces no predicate |
| -7-3 | **External certification/standard requirement** — **welded-only**; invokes **مبحث دهم** (NBC Chapter 10), whose pages are **not in the delivered evidence window**. See §9 |
| -7-4 | **Descriptive text** — an **open list** («و غیره») of force-transfer means. Imposes nothing; produces no predicate |
| -7-5 | **Qualitative obligation → `AMBIGUITY`** — see §6 |
| -7-6 | **Quantitative requirement with an undefined comparison target** — see §7 |
| -7-7 | **Exemption / permission** — «الزامی نیست». It **removes** an obligation; it is not itself a requirement |
| -7-8 | **Conditional quantitative requirement** — 750 mm, scoped to three named tension-member types, with an express exemption. See §8 |

**Correction to a previously recorded reading.** H.18's table row for -7-7 stated the
one-in-between/750 mm staggering as -7-7's content. The visual read this stage shows the
**750 mm figure is printed in -7-8**, while **-7-7 is the exemption clause** ("staggering
is **not** mandatory except per -7-8"). H.21's reading is the one recorded here; it is
taken from the page image at 3.6×–4.2× and does not change any conclusion, since both
subclauses were and remain inside the blocked delegate.

---

## 6. Detailed §9-21-4-7-5 analysis (the primary blocker)

**Exact printed wording** (PDF 461 / printed ۴۴۱, re-read this stage at 4.0×):

> «۹-۲۱-۴-۷-۵ برای تامین پوشش بتنی کافی روی میلگرد، اثر افزایش ابعاد میلگرد ناشی از
> وصلهی مکانیکی باید در نظر گرفته شود.»

| # | Question | Finding |
| :-- | :-- | :-- |
| 1 | Is «افزایش ابعاد میلگرد» quantitatively defined in the clause? | **NO.** No value, factor, ratio or formula |
| 2 | Minimum/maximum dimension specified? | **NO** |
| 3 | Diameter increase factor specified? | **NO** |
| 4 | Coupler/device diameter defined? | **NO.** The clause says the *effect of the increase* must be considered but never states what the increase is, nor what object it applies to |
| 5 | Measurement basis specified? | **NO.** It is not stated whether the cover is measured over the **bar**, the **sleeve**, or the **coupler**, nor from which surface |
| 6 | Direct cross-reference to a cover clause/table? | **NO.** The clause carries **no** cross-reference at all. (`BG-DETAIL-COVER-001` / §9-4-9-5-1 + Table 9-4-6 provides generic bar cover and is **not** referenced here) |
| 7 | Any equation/table/ratio? | **NO** |
| 8 | Is «کافی» tied to an explicit numerical code requirement? | **NO.** «کافی» (sufficient) is unquantified in this clause, and the clause names no other clause that would quantify it for this case |
| 9 | Can the requirement be evaluated from currently modelled inputs? | **NO.** `provided_cover_mm` exists, but the clause does not state a threshold to compare it against, nor a device dimension to subtract. There is nothing to evaluate |
| 10 | Is a proprietary coupler/device dimension required? | **YES** — the obligation is explicitly **device-specific** («ناشی از وصلهی مکانیکی») |

**Window-wide check (re-run this stage):** the phrase «افزایش ابعاد» occurs in **exactly
one** place in the whole delivered window (PDF 442–472) — this sentence. A sweep for
«قطر خارجی», «قطر موثر», «قطر معادل», «غلاف» and «کوپلر» (as OCR terms) returns **no
additional occurrences** anywhere in the window.

**Determination: `AMBIGUITY`.** The clause is addressed to the designer as an obligation
("must be taken into account") but supplies **neither a threshold nor a datum nor a
measurement basis**. Replacing «کافی» with a conventional cover value — or inventing a
coupler enlargement — is expressly prohibited and is **not** done here. This subclause is
**independently fatal** to the mechanical route.

---

## 7. Detailed §9-21-4-7-6 analysis

**Exact printed wording** (PDF 461 / printed ۴۴۱, re-read this stage at 4.2×):

> «۹-۲۱-۴-۷-۶ وصلهی مکانیکی یا جوشی باید قادر به انتقال تنشی حداقل برابر با ۱/۲۵ برابر
> تنش تسلیم میلگرد در کشش و یا فشار باشد.»

| Item | Finding |
| :-- | :-- |
| **A. Requirement numerically stated?** | **YES** — «حداقل برابر با ۱/۲۵ برابر تنش تسلیم میلگرد» = at least **1.25 × f_y**, in tension **or** compression |
| **B. Comparison target exists?** | **YES as a source concept** — the splice's own transferred stress (i.e. its **capacity**, a device/product property) |
| **C. BeamGenius input/model for actual splice capacity?** | **NO.** Grep over `src/beamgenius/` for `splice_capacity`, `device_capacity`, `mechanical_splice`, `splice_device`, `coupler`, `declared`, `manufacturer`, `certificate`: the only hits are two **informational strings** in `registry/catalog.py` (the delegate's own description). The domain layer has **no** splice model; `domain/enums.py` has **no** splice-device enum |
| **D. Source defines how capacity is established?** | **NO.** §9-21-4-7-6 states a performance requirement only. It names **no** test standard, **no** acceptance test, **no** certification route, **no** manufacturer-qualification procedure and **no** allowable-capacity table |
| Reference value 1.25 | DERIVABLE arithmetically from `yield_stress_mpa` (which exists) |
| Capacities (tension/compression) | **MISSING** — and the source does not say how to obtain them |

**The contrast that matters.** `BG-DEV-MECH-ANCHOR-001` (§9-21-3-5-1) *is* executable —
but only because that clause **explicitly conditions permission** on the design engineer's
approval and on approved test results, i.e. it ships its own procedural gate
(`device_supplies_yield_capacity`, `designer_engineer_approved`,
`approved_test_results_present`). **§9-21-4-7-6 ships no such gate.** A numeric factor with
an undefined capacity side is **not executable**, and inferring device capacity from the
bar's `f_y` is the standing prohibition.

**Determination: `INPUT_MODEL_GAP` (with an `EXTERNAL_DEPENDENCY` character).**

---

## 8. §9-21-4-7-7 / -7-8 analysis (the 750 mm rule)

**Verbatim (PDF 461 / printed ۴۴۱, read at 4.2× and 3.6×):**

> «۹-۲۱-۴-۷-۷ یک در میان بودن میلگردهای با وصلهی مکانیکی یا جوشی در هر مقطع از عضو،
> به جز در اعضای کششی بند ۹-۲۱-۴-۷-۸ الزامی نیست.
>
> ۹-۲۱-۴-۷-۸ در اعضای کششی نظیر عضو کششی قوسها، عضو کششی که بار را به تکیهگاهی در
> تراز بالاتر منتقل میکند، و عضو کششی خرپاها، وصلهی جوشی یا مکانیکی در میلگردهای
> مجاور باید با فاصلهی ۷۵۰ میلیمتر در امتداد وصله انجام شود. در نظر گرفتن این ضابطه در
> اعضای کششی نظیر دیوار مخازن دایروی، که تعداد زیادی میلگرد کششی به صورت یک در میان و
> با فاصلهی زیادی از هم وصله شدهاند، الزامی نیست.»

| Question | Finding |
| :-- | :-- |
| Is 750 mm universal? | **NO** |
| Mechanical-only or welded-only? | **NEITHER — BOTH** («وصلهی جوشی یا مکانیکی») |
| Conditional? | **YES** — it is scoped to three named tension-member types: arch/curved tension members, tension members delivering load to a support at a higher level, and truss tension members |
| Applicable only to specific configurations? | Yes, and it carries its own **exemption** (circular tank walls and similar), so it is **explicitly not mandatory** in that case |
| Independently computable from current geometry? | The **750 mm number itself** is trivially checkable **if** splice positions of adjacent bars and the member type are known. The number's *applicability* depends on member classification and on an exemption test, neither of which the current model represents |

**Determination: conditional requirement + exemption. Fully determined as source text —
but it is one condition inside a clause that is blocked elsewhere.** Per the standing rule,
**the whole rule is not promoted merely because this subcondition is deterministic.**

---

## 9. External-standard / source-bridge analysis (Step 10)

Targeted sweep over the **entire delivered window (PDF 442–472)**:

| Searched for | Occurrences in window |
| :-- | :-- |
| `کوپلر` (coupler) | none beyond -7-4 itself (OCR-mangled there; **visually confirmed** in the page image) |
| `غلاف` (sleeve) | none beyond -7-4 (same) |
| `ظرفیت` (capacity) | 2 hits — PDF 442 (hook-anchorage capacity) and PDF 452 (negative flexural capacity). **Neither relates to splices** |
| `گواهی` (certificate) | **none** |
| `تصدیق` (certification) | **none** |
| `تاییدیه` (approval document) | **none** |
| `سازنده` (manufacturer) | **none** |
| `کارخانه` (factory) | **none** |
| `قطر خارجی` (outside diameter) | **none** |
| `قطر موثر` (effective diameter) | **none** |
| `قطر معادل` (equivalent diameter) | **none** |
| `افزایش ابعاد` (dimension increase) | **1 — the -7-5 sentence itself** |
| `کاتالوگ` (catalogue) | **none** |
| `مبحث دهم` (NBC Ch. 10) | **1 — the -7-3 sentence itself** |
| `آزمایش` (testing) | 2 hits — PDF 445 and PDF 453, both inside **§9-21-3** (headed-bar/mechanical-anchorage provisions). **Not reachable from §9-21-4-7** |

**Conclusions:**

1. **No source bridge exists** from the mechanical splice route to coupler dimensions,
   splice capacity, certification, qualification, acceptance testing, manufacturer data,
   cover increase, or effective/equivalent diameter.
2. The **only** external standard invoked by §9-21-4-7 is **«مبحث دهم مقررات ملی ساختمان»
   (National Building Regulations, Chapter 10)** — referenced by **-7-3**, which is a
   **welded-only** provision. No page of Chapter 10 exists in the committed evidence, so it
   cannot be executed.
3. No external standard may be acquired or substituted to fill this gap.

---

## 10. Engine input-model audit (Step 11)

| Item | Classification |
| :-- | :-- |
| splice type | **MISSING** (no splice enum in `domain/enums.py`) |
| mechanical coupler/device type | **MISSING** |
| actual coupler outside diameter | **MISSING** — and not source-defined either (§6) |
| bar nominal diameter | **EXISTS** (`bar_diameter_mm`) |
| effective enlarged diameter | **MISSING** — no source definition exists to build it from |
| splice tensile capacity | **MISSING** |
| splice compression capacity | **MISSING** |
| bar `f_y` | **EXISTS** (`yield_stress_mpa`) |
| required 1.25·f_y capacity | **DERIVABLE** (arithmetic from `f_y`) |
| certification/qualification status | **MISSING** — no source basis in §9-21-4-7 |
| manufacturer/test evidence | **MISSING** — no source basis in §9-21-4-7 |
| splice location | **MISSING** (no splice model exists at all) |
| 750 mm staggering | **MISSING as input; the number is DERIVABLE** once splice positions and member type exist |
| cover on the bar | **EXISTS** (`provided_cover_mm`, `BG-DETAIL-COVER-001`) |

**`UNSUPPORTED ASSUMPTION` column:** the only way to make -7-5 or -7-6 executable today is
to invent a device dimension or a device capacity. Both are unsupported assumptions, and
both are prohibited. **No new input was added**, per the standing rule that inputs are only
added when source verification proves the rule can otherwise be fully executed.

---

## 11. Delegate audit (Step 12)

**Delegate:** `BG-DEV-SPLICE-WELDED-MECH-PENDING` — `VERIFY_PENDING`,
`execution_allowed=False`, `dependencies=()`, clause `9-21-4-7-1..-7-8`
(printed 440–441 / PDF 460–461). Target `E` declares exactly one dependency, on this
delegate — the edge verified correct in §3.

### 11.1 The stale claim

The delegate's `blocked_reason` (in `src/beamgenius/registry/catalog.py`) carried a second
reason:

> "… and the mechanical-splice strength-transfer coefficient glyph was not independently
> re-confirmed."

and the same stale wording appeared in `docs/VERIFIED_RULES.md`.

**H.21 evidence proving it stale.** The §9-21-4-7-6 coefficient was re-read this stage from
the page image at 4.2× and 7–8×: it is «۱/۲۵» — the document's slash-with-no-leading-zero
convention for values ≥ 1 (the same convention as «۰/۱۷» = 0.17 and «۰/۴۵» = 0.45 in the
same evidence) — i.e. **1.25**. This agrees with the independent re-confirmation already
recorded in Stage H.10 (`docs/PHASE2F_STAGE_H10_PLAN.md` §7.2), which explicitly noted the
sentinel's reason string had become stale and deferred the correction as an "optional,
behaviour-neutral future metadata action".

**Correction performed (the only non-documentary-creation edit in this stage):** the stale
clause was removed from the delegate's `blocked_reason` in `catalog.py` and from
`docs/VERIFIED_RULES.md`, and the reason now records that the coefficient was re-read as
the document's 1.25 notation.

**Proof of behaviour-neutrality:** no test asserts that string; the delegate's
`status`, `execution_allowed`, `dependencies`, `pdf_page`/`printed_page` and `rule_id` are
untouched; and every gate in §16 returns the identical baseline values.

### 11.2 Can H.21 narrow or remove the delegate's blocker? — **NO**

The delegate remains blocked for **three** independent, source-verified reasons:

1. **-7-3 → NBC Chapter 10** (welded route): `EXTERNAL_DEPENDENCY`, pages out of the
   verified window. Unchanged and unsatisfied.
2. **-7-5** (mechanical route): `AMBIGUITY` — cover obligation with no threshold, no datum
   and no measurement basis. Unchanged.
3. **-7-6** (both routes): `INPUT_MODEL_GAP` — required transferred stress is computable
   (1.25·f_y) but the device-capacity side has no engine model and the source defines no
   way to establish it. Unchanged.

Only the *stale documentation claim* was removable. **Execution status was not changed.**

---

## 12. Promotion gate

| # | Condition | Result |
| :-- | :-- | :-- |
| 1 | §9-21-6-3-5(الف) visually verified | **PASS** — chapeau + (الف) read at 3.6× |
| 2 | Mechanical-splice dependency exact and unambiguous | **PASS** — explicit «مطابق بند ۹-۲۱-۴-۷» |
| 3 | §9-21-4-7 requirements fully determined | **FAIL** — -7-3, -7-5 and -7-6 are each independently unresolved |
| 4 | **7-5 has a source-defined quantitative interpretation** | **FAIL** — no number, no datum, no basis, no cross-reference |
| 5 | Enlarged diameter / coupler dimension source-defined or a valid required input | **FAIL** — not source-defined; input would encode an invented value |
| 6 | **7-6 splice capacity deterministically verifiable** | **FAIL** — no capacity input/model exists |
| 7 | Method of establishing splice capacity source-supported | **FAIL** — the clause states a performance requirement only |
| 8 | No external standard required unless explicitly cited **and verified** | **FAIL** — §9-21-4-7-3 explicitly cites NBC Chapter 10, which is **not verified / not delivered** |
| 9 | 7-7/7-8 applicability fully determined | **PASS as source text** (conditional + exempted) — but not promotable in isolation |
| 10 | Every required input exists or is deterministically derivable | **FAIL** — device dimension, capacities, splice location, certification all missing |
| 11 | No unsupported assumption required | **FAIL** |
| 12 | Evaluator cannot emit false PASS | **FAIL** — no evaluator can be written over undefined quantities |

**Gate result: 8 of 12 conditions FAIL.** Under the governing rule, E must remain:
`VERIFY_PENDING`, `execution_allowed=False`. **No partial evaluator was created** — and
critically, promoting only the deterministic 750 mm staggering subcondition would be a
**partial promotion of a selector** that could report PASS while §9-21-4-7-5 and -7-6 were
unresolved: a false PASS. That is prohibited.

---

## 13. Final decision

**Outcome `D` — `REMAINS BLOCKED — SOURCE AMBIGUITY`.**

- **Primary: `SOURCE_AMBIGUITY`** — §9-21-4-7-5 obliges the designer to account for a
  device-driven bar-dimension increase in order to obtain sufficient concrete cover, while
  the clause supplies neither a threshold, nor a datum, nor a measurement basis, and
  carries no cross-reference to any cover clause or table.
- **Secondary: `SOURCE–INPUT MODEL GAP`** — §9-21-4-7-6's required transferred stress is
  computable, but the splice-capacity side has no engine representation and the source
  defines no method to establish it.
- **Tertiary: `EXTERNAL_DEPENDENCY`** — §9-21-4-7-3 (welded route) invokes NBC Chapter 10,
  which is out of the verified window and may not be substituted.

**`FULLY RESOLVED` is not reached** → **no implementation**: no evaluator, no RuleReference
change, no registry status change, no new execution path, no registry-count change.

---

## 14. Exact remaining blocker(s)

1. **§9-21-4-7-5 — cover obligation (primary).** «برای تامین پوشش بتنی کافی … اثر افزایش
   ابعاد میلگرد ناشی از وصلهی مکانیکی باید در نظر گرفته شود.» No numeric threshold, no
   datum, no measurement basis, no cross-reference; the enlargement value and the affected
   object are undefined. Not evaluable.
2. **§9-21-4-7-6 — capacity model (secondary).** Requirement = ≥ 1.25·f_y in tension or
   compression; the comparison target is the splice device's capacity, which the engine does
   not represent and the source does not define how to establish. Capacity may **never** be
   inferred from the bar's `f_y`.
3. **§9-21-4-7-3 — external dependency (tertiary, welded route).** NBC Chapter 10 welding
   compliance; those pages are not in the delivered evidence. No substitute standard may be
   used.
4. **§9-21-4-7-7/-7-8** are determinate as source text but conditional and exempted; they
   cannot carry the rule alone, and promoting them in isolation would create a partial
   selector.

**What would unlock it (nothing less):**

1. a delivered, verified copy of **NBC Chapter 10** (for the welded route); **and**
2. an edition, erratum or authoritative clarification of Mabhas 9 that gives §9-21-4-7-5 a
   **quantified basis** (enlargement value and/or measurement datum and threshold); **and**
3. a source-supported route to establish **splice-device capacity** (a clause-defined test,
   certification or qualification procedure) together with an engine input-for it;
   **or** a recorded project-level decision that the mechanical-splice route is outside the
   engine's remit.
   Engineering convention, a same-named symbol, neighbouring clauses, and non-governing
   reference material are **not** admissible substitutes.

---

## 15. Files changed

| File | Change | Nature |
| :-- | :-- | :-- |
| `docs/PHASE2F_STAGE_H21_SPIRAL_SPLICE_AUDIT.md` | **this record (new)** | new document |
| `src/beamgenius/registry/catalog.py` | delegate `blocked_reason`: stale coefficient clause removed (Step 12 correction) | **documentation text only** — status, `execution_allowed`, dependencies and all counts unchanged |
| `docs/VERIFIED_RULES.md` | same stale claim corrected | documentation |

**No other file changed.** No evaluator, no test, no status, no registry count.

---

## 16. Validation

| Gate | Result |
| :-- | :-- |
| `PYTHONPATH=src pytest` | **673 passed** |
| `PYTHONPATH=src mypy --strict` | **clean — 23 source files** |
| Registry consistency | **121 total / 63 executable / 48 blocked / 10 reference** — unchanged |
| Duplicate Rule IDs | **0** |
| §9-21-6 | **21 executable / 5 blocked** — unchanged |
| `BG-TRANS-SPIRAL-SPLICE-SEL-PENDING` | `VERIFY_PENDING`, `execution_allowed=False`, deps `('BG-DEV-SPLICE-WELDED-MECH-PENDING',)` — unchanged |
| `BG-DEV-SPLICE-WELDED-MECH-PENDING` | `VERIFY_PENDING`, `execution_allowed=False` — unchanged (reason text only) |
| `git diff --check` | clean |
| Unrelated changes | none |

**Deltas: none** (counting rules, statuses and execution flags). The only diff outside the
new document is **prose inside two existing strings/lines**.

---

## 17. Commit SHA

**Baseline at stage start: `3df5091`.**
**This stage's commit (introduces this file): `67e3edd`.**

The value above is the true hash of the commit that introduced this document; it was
backfilled by a **separate content-only follow-up commit**. No amend, no rebase, no
force-push and no history rewrite was used — both commits are ordinary fast-forward commits
on `arena/b9cd291a-beamgenius`.

---

## 18. origin/main status

`origin/main` remains at **`df8067a750ffc7984c9dc5d80220ad9013503aa6`**, unmodified. It was
read only (`git ls-tree`, `git show` into the git-ignored `working/h21/`). No reset, rebase,
force-push, history rewrite or branch switch occurred. All work is on
`arena/b9cd291a-beamgenius`.

---

```
DECISION:                 REMAINS BLOCKED — SOURCE AMBIGUITY (outcome D)
RULE:                     BG-TRANS-SPIRAL-SPLICE-SEL-PENDING
STATUS:                   VERIFY_PENDING
EXECUTION_ALLOWED:        False
PRIMARY CLASSIFICATION:   SOURCE_AMBIGUITY (9-21-4-7-5 cover obligation)
SECONDARY CLASSIFICATION: SOURCE-INPUT MODEL GAP (9-21-4-7-6 capacity) +
                          EXTERNAL_DEPENDENCY (9-21-4-7-3 → NBC Chapter 10)
§9-21-6-3-5(الف):         VISUALLY VERIFIED. Chapeau «وصلهی دورپیچها با یکی از روشهای
                          زیر انجام میشود» (explicit OR selector); (الف) = «وصلهی جوشی
                          یا مکانیکی مطابق بند ۹-۲۱-۴-۷» — the 9-21-4-7 cross-reference is
                          EXPLICIT, so the dependency edge is source-correct.
§9-21-4-7-5:              AMBIGUITY. «پوشش بتنی کافی… اثر افزایش ابعاد میلگرد ناشی از
                          وصلهی مکانیکی باید در نظر گرفته شود» — no number, no threshold,
                          no datum, no measurement basis, no cross-reference; «افزایش
                          ابعاد» occurs only here in the whole window. Not evaluable.
§9-21-4-7-6:              Requirement IS numeric (۱/۲۵ = 1.25, re-verified this stage at
                          4.2×/7–8×) but the comparison target (device capacity) has NO
                          engine model and the source defines NO way to establish it
                          (no test standard, no certification route, no qualification).
SPLICE CAPACITY:          MISSING. No tensile/compression capacity, splice type, device
                          type, certification or location in the domain model. 1.25·f_y is
                          DERIVABLE; the capacity side is not. Capacity may never be
                          inferred from bar f_y.
COUPLER / ENLARGED DIAMETER: NOT source-defined (no value, no factor, no basis) and NOT
                          modelled. Inventing either is prohibited.
750mm RULE:               CONDITIONAL + EXEMPTED, and printed in -7-8 (not -7-7, which is
                          the exemption clause). Scoped to arch ties / higher-level-support
                          tension members / truss tension members; expressly not mandatory
                          for circular tank walls. Deterministic as a number, but not
                          promotable in isolation.
ENGINE MODEL:             splice type, device type, coupler OD, enlarged diameter, both
                          capacities, certification, manufacturer evidence and splice
                          location are MISSING; provided_cover_mm exists; 750 mm and
                          1.25·f_y are DERIVABLE. No input added.
PRIMARY BLOCKER:          9-21-4-7-5 — cover obligation with no threshold, no datum and no
                          measurement basis (independently fatal to the mechanical route).
IMPLEMENTATION:           NOT PERFORMED — promotion gate failed 8 of 12 conditions. No
                          partial evaluator; promoting only the 750 mm subcondition would
                          be a partial promotion of a selector (false-PASS risk).
FILES CHANGED:            docs/PHASE2F_STAGE_H21_SPIRAL_SPLICE_AUDIT.md (new);
                          src/beamgenius/registry/catalog.py + docs/VERIFIED_RULES.md
                          (authorised stale-claim documentation correction ONLY)
PYTEST:                   673 passed
MYPY:                     Success: no issues found in 23 source files
REGISTRY:                 121 / 63 executable / 48 blocked / 10 reference — UNCHANGED
                          (§9-21-6: 21 executable / 5 blocked — unchanged)
COMMIT:                   see §17
ORIGIN/MAIN:              df8067a750ffc7984c9dc5d80220ad9013503aa6 — untouched
```
