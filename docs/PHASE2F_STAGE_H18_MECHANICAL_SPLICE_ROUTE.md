# Phase 2F — Stage H.18: Mechanical Sub-Branch of §9-21-6-3-5(الف)

**Decision: `PARTIALLY RESOLVED — REMAINS BLOCKED`.** No rule was promoted, no partial
rule was created, and no registry, evaluator, test or status value was changed. The only
artifact of this stage is this record.

The H.17 audit nominated the **mechanical** sub-branch of `BG-TRANS-SPIRAL-SPLICE-SEL-PENDING`
(§9-21-6-3-5(الف) → §9-21-4-7) as the one residual needing no new external document. This
stage investigated exactly that route, source-first, and found that it is **not** fully
deterministic: one governing provision of the delegated clause,
**§9-21-4-7-5**, cannot be represented without inventing both a governing dimension and a
numeric threshold. A second provision, **§9-21-4-7-6**, requires a product-capacity input
model that does not exist. Both are recorded precisely below.

---

## 1. Mechanical-splice dependency chain

Traced from the target clause to the acceptance predicate. Statuses read live from the
registry at `b4364d5`.

```
§9-21-6-3-5 (Printed p. 448 / PDF p. 468)          [BG-TRANS-SPIRAL-SPLICE-SEL-PENDING]
│   «۹-۲۱-۶-۳-۵ وصلهی دورپیچها با یکی از روشهای زیر انجام میشود
│    الف- وصلهی جوشی یا مکانیکی مطابق بند ۹-۲۱-۴-۷.»
│   (ب) lap route → ALREADY EXECUTABLE as BG-TRANS-SPIRAL-SPLICE-LAP-SEL-001
│
└─ (الف) pure delegation to §9-21-4-7            ← THE TARGET OF THIS STAGE
     │
     └─ §9-21-4-7 (Printed pp. 440–441 / PDF pp. 460–461)
          [BG-DEV-SPLICE-WELDED-MECH-PENDING — VERIFY_PENDING, execution_allowed=False,
           dependencies=(), depended on by EXACTLY ONE rule: this sentinel]
          │
          ├─ -7-1  welded splices mainly d_b ≥ 20 mm ................. WELDED ONLY — N/A
          ├─ -7-2  butt welding preferred for large bars ............. WELDED ONLY — N/A
          ├─ -7-3  «جوش میلگردها در وصلههای جوشی باید الزامات مبحث دهم
          │         مقررات ملی ساختمان را تامین نماید.»
          │        welding must satisfy NBC Chapter 10 .............. WELDED ONLY — N/A
          │        (NBC Ch. 10 pages absent from every evidence package)
          ├─ -7-4  mechanical splices transfer force via
          │         «غلاف اتکایی، کوپلر، غلاف کوپل کننده و غیره» .... NO PREDICATE
          ├─ -7-5  «برای تامین پوشش بتنی کافی روی میلگرد، اثر افزایش
          │         ابعاد میلگرد ناشی از وصلهی مکانیکی باید در نظر
          │         گرفته شود.» ..................................... ★ PRIMARY BLOCKER
          ├─ -7-6  splice must transfer ≥ 1.25·f_y in tension or
          │         compression ..................................... ★ SECONDARY (input gap)
          ├─ -7-7  staggering not required at every section .......... deterministic
          └─ -7-8  EXCEPT tension members: stagger 750 mm ............ deterministic
```

### 1.1 Edge-by-edge determination

| Edge | Governing clause | Source | Rule ID | Status | Required for the **mechanical** branch? | Independently executable? |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| §9-21-6-3-5(الف) → §9-21-4-7 | delegation, printed 448 / PDF 468 | verified this stage | `BG-TRANS-SPIRAL-SPLICE-SEL-PENDING` | `VERIFY_PENDING`, exec=False | this **is** the target | No |
| → -7-1 | printed 440 / PDF 460 | verified | (delegate) | blocked | **No** — welded only | — |
| → -7-2 | printed 440 / PDF 460 | verified | (delegate) | blocked | **No** — welded only | — |
| → -7-3 | printed 441 / PDF 461 | verified this stage | (delegate) | blocked | **No** — scope is «وصلههای جوشی» | — |
| → -7-4 | printed 441 / PDF 461 | verified this stage | (delegate) | blocked | **Yes** — but contains no predicate | — |
| → -7-5 | printed 441 / PDF 461 | verified this stage | (delegate) | blocked | **Yes** — and unresolvable (§4) | No |
| → -7-6 | printed 441 / PDF 461 | re-verified this stage | (delegate) | blocked | **Yes** — needs capacity input (§5) | No |
| → -7-7 / -7-8 | printed 441 / PDF 461 | re-verified this stage | (delegate) | blocked | **Yes** — deterministic | (not separable, see §7) |
| §9-21-4-1-1(ت) permission | printed 436 / PDF 456 | verified this stage | `BG-DEV-LAP-APPLIC-001` | **executable** | context (permission), not the predicate | Yes |
| Cover values (if they were the missing number) | §9-4-9-5-1 + Table 9-4-6 | verified (Phase 2E) | `BG-DETAIL-COVER-001` | **executable** | **not referenced by -7-5** | Yes |

**Dependency-declaration check:** the sentinel declares exactly one dependency
(`BG-DEV-SPLICE-WELDED-MECH-PENDING`). The trace finds **no missing edge** — every
provision of §9-21-4-7 lives inside the delegate, and no other clause is reachable from
the mechanical branch.

---

## 2. §9-21-4-7-4 — finding

**Exact printed wording** (printed p. 441 / PDF p. 461, read at 3.3×):

> «۹-۲۱-۴-۷-۴ در وصلههای مکانیکی انتقال نیرو از طریق غلاف اتکایی، کوپلر، غلاف کوپل
> کننده و غیره انجام میگیرد.»

| Question | Finding |
| :-- | :-- |
| Permission statement? | **Effectively yes** — it names the permitted force-transfer means. |
| Prerequisite? | **No.** It imposes nothing. |
| Requires a specific mechanical splice type? | **No** — it is an open list («و غیره» = "etc."). |
| Requires external product/system approval? | **No.** |
| Introduces a quantitative criterion? | **No** — no number appears. |
| Implicit dependency on another clause? | **None.** |
| Representable with current inputs? | Nothing to represent — **there is no predicate.** |

**Determination: descriptive. No rule may be built on it.** Manufacturing a predicate
here (e.g. an enumerated `coupler_type`) would invent a requirement the source does not
contain. It is recorded as **satisfied-by-nature** (a mechanical splice *is* one that
transfers force by these means); it gates nothing.

---

## 3. §9-21-4-7-5 — finding (**the primary blocker**)

**Exact printed wording** (printed p. 441 / PDF p. 461, read at 3.3×):

> «۹-۲۱-۴-۷-۵ برای تامین پوشش بتنی کافی روی میلگرد، اثر افزایش ابعاد میلگرد ناشی از
> وصلهی مکانیکی باید در نظر گرفته شود.»

| # | Question | Finding |
| :-- | :-- | :-- |
| 1 | Exact wording | As above, verified verbatim. |
| 2 | Establishes a numeric minimum? | **NO.** No mm value, no ratio, no table, no equation. |
| 3 | Refers to a specific diameter / device / cover / detailing condition? | It refers to *"the increase in bar dimensions caused by the mechanical splice"* — a **device-specific enlargement** — but gives **no value, no measurement basis, and no definition of that enlargement**. It also does not state which diameter the cover is measured over (bar or device). |
| 4 | Does another governing clause supply the missing numeric requirement? | **NO.** «افزایش ابعاد» (dimension increase) occurs **nowhere else in the entire delivered evidence window** (PDF pp. 442–472 sweep) — it appears only in this sentence. The clause carries **no cross-reference** to any cover clause or table, and §9-4-9-5-1 / Table 9-4-6 (already executable as `BG-DETAIL-COVER-001`) addresses bar cover generally and says nothing about splice-device enlargement. |
| 5 | Does BeamGenius already have the necessary cover input? | It has `provided_cover_mm` (`BG-DETAIL-COVER-001`), but the clause's requirement is not "cover ≥ X"; it is "the enlargement effect must be taken into account". Without a device dimension there is nothing to subtract, and the threshold is not stated. |
| 6 | Can it safely become PASS / FAIL / BLOCKED? | **BLOCKED only.** A PASS or FAIL would require inventing (a) a governing device dimension and (b) a numeric threshold — both prohibited. |

**Why this is not merely "qualitative wording to be tightened":** §9-21-4-7-5 is
addressed to the **designer** as an obligation ("must be taken into account"), unlike
§9-21-3-5-1, whose permission is expressly conditioned on procedural gates the engine can
encode (design-engineer approval + approved test results — the pattern that made
`BG-DEV-MECH-ANCHOR-001` promotable). Here there is no procedural gate to capture and no
datum to evaluate.

**Determination: `AMBIGUITY` (source does not determine the required interpretation) —
independently fatal to the route.**

---

## 4. §9-21-4-7-6 — finding

**Exact printed wording** (printed p. 441 / PDF p. 461, re-confirmed at 3.3×;
the «۱/۲۵» notation is the document's slash-with-no-leading-zero convention = **1.25**,
consistent with «۰/۱۷» = 0.17 and «۰/۴۵» = 0.45 in the same evidence):

> «۹-۲۱-۴-۷-۶ وصلهی مکانیکی یا جوشی باید قادر به انتقال تنشی حداقل برابر با ۱/۲۵ برابر
> تنش تسلیم میلگرد در کشش و یا فشار باشد.»

| Question | Finding |
| :-- | :-- |
| What is 1.25·f_y? | The **required transferred stress** of the splice: ≥ 1.25 × the bar's yield stress, in **tension or compression**. |
| Required strength / declared capacity / computable / external? | The *requirement* is computable (1.25·f_y from `f_y`). The **comparison target** is the splice's capacity — a **proprietary product property**. It is an `EXTERNAL_DEPENDENCY` expressed as an `INPUT_MODEL_GAP`. |
| Does BeamGenius have an input/model for it? | **NO.** Confirmed: the domain layer contains no splice/coupler/device/capacity model (grep over `domain/*.py` for coupler, splice_device, device, manufacturer, certificate, declared → **zero hits**; `enums.py` has no splice-device enum). |
| May capacity be inferred from the bar's f_y? | **No** — and this is exactly the standing prohibition: a PASS may never rest on inferring device capacity from the reinforcement bar's yield stress. |
| Is there a promotable precedent? | `BG-DEV-MECH-ANCHOR-001` (§9-21-3-5-1) *is* executable with caller-supplied `device_supplies_yield_capacity` / `designer_engineer_approved` / `approved_test_results_present` — but that clause **explicitly conditions permission** on the design engineer's approval and approved test results. **§9-21-4-7-6 states only a performance requirement** and provides no such procedural gate to encode. |

**Determination: `INPUT_MODEL_GAP` + `EXTERNAL_DEPENDENCY`.** Standing alone this would
need a deliberate, separately-justified input-model extension; it is **moot for this
stage's decision** because §9-21-4-7-5 already blocks the route.

---

## 5. Deterministic remainder and why it cannot be shipped as a partial rule

Verified this stage as genuinely deterministic:

| Provision | Content | Representable? |
| :-- | :-- | :-- |
| §9-21-4-7-7 | adjacent spliced bars need not be staggered at every section | yes |
| §9-21-4-7-8 | **except** in tension members (arch ties; a member transferring load to a higher chord; tension chords; cantilevers): adjacent splices staggered **≥ 750 mm** along the splice; **not required** in tension members such as diaphragm walls where many bars are spliced at staggered spacing | yes — with a caller-supplied tension-member class |
| §9-21-4-7-1/-7-2 | welded-splice recommendations | not applicable |
| §9-21-4-7-3 | Chapter 10 gate | **welded only — not applicable** (confirms H.17) |
| §9-21-4-1-1(ت) | mechanical splices are a permitted splice method | context only |

**A partial rule covering only the deterministic remainder is prohibited here.** The
route is **conjunctive**: §9-21-4-7 requires -7-4 *and* -7-5 *and* -7-6 *and* -7-7/-7-8
to hold simultaneously. A rule that checked staggering and the permission alone would
emit **PASS for a splice whose cover effect and capacity were never evaluated — a false
PASS**. No such rule was created, and none of the executable content above will be
exposed until every conjunct is evaluable.

---

## 6. Existing-delegate finding

| Question | Finding |
| :-- | :-- |
| Rule ID | `BG-DEV-SPLICE-WELDED-MECH-PENDING` |
| Clause | §9-21-4-7-1..-8 (printed 440–441 / PDF 460–461) |
| Status | `VERIFY_PENDING`, `execution_allowed=False`, `dependencies=()` |
| Why it is blocked (registered reason) | (i) §9-21-4-7-3 → NBC Chapter 10 out-of-window; (ii) *"the mechanical-splice strength-transfer coefficient glyph was not independently re-confirmed"* |
| Is the registered blocker genuinely applicable to **this** route? | **Partly, and the second limb is now stale.** Limb (i) binds the **welded** sub-branch only (H.17, re-confirmed here). Limb (ii) is **resolved** — the 1.25 coefficient was independently re-confirmed in H.10 and again visually in H.17 and this stage. |
| Can the blocker be resolved from existing source evidence? | **No** — removing the stale limbs does not make the clause executable: §9-21-4-7-5 and -7-6 remain. |
| Would promoting it affect unrelated rules? | It is depended on by **exactly one** rule (`BG-TRANS-SPIRAL-SPLICE-SEL-PENDING`), so blast radius is small — but promotion is not possible, so the question is moot. |
| Can it be safely promoted independently? | **No.** |

**The delegate was NOT changed.** Its status, dependency tuple and reason string are
untouched, per the instruction not to change it until its complete source/input
requirements are established.

---

## 7. Final decision

### **B — PARTIALLY RESOLVED BUT NOT EXECUTABLE** (with C-type classification of the residues)

| | |
| :-- | :-- |
| **Resolved this stage** | (1) §9-21-4-7-3 / NBC Chapter 10 is **welded-only** and is therefore **not** a blocker of the mechanical branch — the H.17 correction is confirmed and the chain is now traced edge-by-edge; (2) the delegation §9-21-6-3-5(الف) → §9-21-4-7 is complete and contains no other reachable dependency — the declared dependency tuple is not missing an edge; (3) §9-21-4-7-4 carries **no predicate**; (4) §9-21-4-7-7/-7-8 are deterministic (750 mm in tension members); (5) the 1.25·f_y coefficient is visually re-confirmed. |
| **Remaining blocker — primary** | **§9-21-4-7-5** — requires "the effect of the increase in bar dimensions caused by the mechanical splice" to be taken into account for cover, while stating **no numeric minimum**, defining **no device enlargement**, and **cross-referencing nothing**; the term occurs nowhere else in the delivered window. Classification: **`AMBIGUITY`** (unrepresentable without invention). |
| **Remaining blocker — secondary** | **§9-21-4-7-6** — 1.25·f_y is a requirement on a **proprietary device's** capacity; BeamGenius has no such input model, and the clause states no procedural gate (unlike §9-21-3-5-1). Classification: **`INPUT_MODEL_GAP` + `EXTERNAL_DEPENDENCY`**. |
| **Rule state** | `BG-TRANS-SPIRAL-SPLICE-SEL-PENDING` — unchanged: `VERIFY_PENDING`, `execution_allowed=False`, dependency on `BG-DEV-SPLICE-WELDED-MECH-PENDING` preserved. |
| **Welded sub-branch** | Remains blocked on NBC Chapter 10, untouched, as instructed. |
| **Partial rule created?** | **No.** |
| **False-PASS reachable?** | **No** — the route has no evaluator, so it can only return BLOCKED. |

### 7.1 What would unlock it

1. **For §9-21-4-7-5 (decisive):** an edition, erratum or authoritative commentary of
   Mabhas 9 that (a) gives the device-enlargement datum and (b) states the governing
   cover threshold for the enlarged section — or a project-level decision that this
   obligation is a designer responsibility outside the engine's remit (which would need
   to be recorded like H.16 §9's options for D).
2. **For §9-21-4-7-6:** a deliberate input-model extension accepting a declared splice
   capacity (and a governance decision on whether an unverified product declaration may
   ever yield PASS), or the same scope determination as (1).
3. Neither is available from the currently committed source set; accordingly the route
   is **not** the “no new document needed” candidate H.17 hoped for — the missing item is
   a source definition, not a project decision alone.

### 7.2 Recommended next target

**B is now the nearest-term candidate** (H.17 §11 ranked it second): it needs one
authorised reading of §9-21-6-1-5(الف)'s datum and nothing external. **A** still needs
evidence absent from the window; **C** follows A; **D** awaits a governance decision.

---

## 8. Files changed

| File | Change |
| :-- | :-- |
| `docs/PHASE2F_STAGE_H18_MECHANICAL_SPLICE_ROUTE.md` | **this record (new)** |
| — | **Nothing else.** No rule promoted, no status, dependency, reason string, evaluator, test or catalog value modified. |

A behaviour-neutral metadata refresh of the delegate's `blocked_reason` (stale limb (ii);
welded-only scope of limb (i)) and of E's reason remains **recommended and still
deliberately deferred** — it is not performed here because it would change diagnostic
text and is not required to reach this stage's conclusion.

---

## 9. Tests and gates

| Gate | Result |
| :-- | :-- |
| `PYTHONPATH=src pytest` | **673 passed** |
| `PYTHONPATH=src mypy --strict` | **clean — 23 source files** |
| Registry | **121 total / 63 executable / 48 blocked / 10 reference** — unchanged |
| Duplicate Rule IDs | **0** |
| §9-21-6 | **21 executable / 5 blocked** — unchanged |
| `BG-TRANS-SPIRAL-SPLICE-SEL-PENDING` | `execution_allowed=False`, `VERIFY_PENDING`, dependency preserved |
| ISIRI 11558 PDF SHA-256 | `4c1c…916c` — unchanged |
| `git diff --check` | clean |
| `origin/main` | `df8067a750ffc7984c9dc5d80220ad9013503aa6` — untouched |

**Deltas: none.** No count changed anywhere.

---

## 10. Evidence read this stage (all visually, OCR navigation only)

| PDF page | Printed | Content verified |
| :-- | :-- | :-- |
| 456 | 436 | §9-21-4-1-1: «وصلهی میلگردها به یکی از طرق زیر مجاز است: الف- پوششی؛ ب- اتکایی؛ پ- جوشی؛ **ت- مکانیکی**» (no approval gate attached) |
| 460 | 440 | §9-21-4-7 heading; -7-1 (welded mainly d_b ≥ 20 mm); -7-2 (butt welding preferred) |
| 461 | 441 | -7-3 (Chapter 10, **welded** only); **-7-4** (no predicate); **-7-5** (qualitative cover); **-7-6** (1.25·f_y); -7-7 / -7-8 (750 mm staggering in tension members); §9-21-5 boundary |
| 468 | 448 | §9-21-6-3-5 chapeau + (الف) delegation → §9-21-4-7 (footer ۴۴۸ confirmed) |

Sweeps (navigation): «مکانیکی» across PDF 442–472 → pages 445, 453, 456, 460, 461, 468
only (none of the others governs mechanical splices); «افزایش ابعاد» → **461 only**;
«کوپلر» / device dimensions → no numeric value anywhere.

---

*H.18 traced the mechanical-splice route to its predicate, confirmed the H.17 correction
that Chapter 10 binds only the welded sub-branch, and found that the route nevertheless
cannot execute: §9-21-4-7-5 states an obligation with no threshold and no datum, and
§9-21-4-7-6 requires a product property the engine cannot hold. Governance over feature
count — the branch stays blocked, and no false PASS is possible.*
