# Phase 2F — Stage H.17: Remaining §9-21-6 Blocker Audit

**Stage type: AUDIT ONLY. No rule was promoted, no rule status was changed, no
evaluator, registry, test or documentation value was modified — the only artifact of
this stage is this record.**

The five remaining blocked `§9-21-6` sentinels were re-audited against the question:
*can any of them now be fully resolved using sources already available to BeamGenius?*

**Answer: NO — all five remain correctly blocked.** Three of the five, however, had
their blocking reasons **sharpened or corrected** in this stage (the corrections are
recorded in §7 and change no status). No partial rule was created anywhere.

---

## 1. Scope, method and evidence basis

### 1.1 What this stage did and did not do

| | |
| :-- | :-- |
| Did | Re-read the actual source pages for each blocker's clause at full resolution (3.0×–5.2× page-native pixels); re-derived each blocking cause; re-checked the dependency edges in the live registry; re-ran the λ citation sweep with positive controls; re-checked the engine's input model against each clause's required quantities. |
| Did not | Re-open the completed H.14 (§9-4-8) or H.16 (ISIRI 11558) work; re-acquire any source; change any rule, evaluator, test or registry value; implement any partial rule. |

### 1.2 Evidence basis (read-only)

- **Mabhas 9 (1399, 5th ed., ATNasr PDF) pages**: the committed evidence scan
  `phase2f-source-442-472/` held on **`origin/main` @ `df8067a`** (31 JPG + 31 OCR TXT,
  intact and unmodified — verified by `git ls-tree`). Pages were extracted **read-only**
  into the git-ignored `working/h17/` directory and read as images. `origin/main` was
  not written to, and no evidence page was added to this branch.
- **Canonical page offset for this scan: PDF = printed + 20** (footer-confirmed).
- **ISIRI 11558** evidence package `phase2f-source-11558/` (this branch, unchanged;
  SHA-256 `4c1c1a478ab8a39b6a19cabc63eac63afbaf2f31c4a7c3eaf55549c9d039916c`).
- **OCR text layer used for navigation only** (citation sweeps, page location). Every
  value, noun and datum asserted below was read from the page image.
- **Mostofinejad Vol. 1 (reference material)**: checked and found **not engaged** by any
  of the five clauses. The reference module
  (`src/beamgenius/reference/mostofinejad_ch5.py`) covers Vol. 1 Chapter 5 flexural
  equations only (`Eq. 5-46 … 5-61`); it contains no tie, stirrup, spiral, anchorage or
  splice content. Nothing in it could lawfully bear on these blockers even if it did
  (reference material never substitutes for Mabhas 9).

### 1.3 Governance rules applied

Only fully verified deterministic branches may become executable; ambiguous source
requirement = BLOCKED; missing required input = BLOCKED; an unrepresentable required
condition = BLOCKED; no interpolation across printed boundaries; no import of a datum
from a sister clause, a figure, another chapter or a foreign standard; no partial rule
that can PASS while a required condition is unresolved; BLOCKED never becomes PASS.

---

## 2. Baseline at stage start

| Gate | Value |
| :-- | :-- |
| HEAD | `8fc1dc9` (H.16) |
| Registry | **121 total / 63 executable / 48 blocked / 10 reference** |
| §9-21-6 | **21 executable / 5 blocked** |
| Duplicate Rule IDs | 0 |
| `origin/main` | `df8067a750ffc7984c9dc5d80220ad9013503aa6` |

The five blocked §9-21-6 sentinels (all `VERIFY_PENDING`, `execution_allowed=False`):

| | Rule ID | Clause |
| :-- | :-- | :-- |
| A | `BG-TRANS-TIE-ANCHOR-PENDING` | §9-21-6-1-3(ب) |
| B | `BG-TRANS-WIRE-TIE-PENDING` | §9-21-6-1-5 |
| C | `BG-TRANS-TORSION-TIE-PENDING` | §9-21-6-1-6(ب) & §9-21-6-2-7(ب), residual route |
| D | `BG-TRANS-WIRE-SUBST-PENDING` | §9-21-6-2-3 (via §9-4-8-7 → ISIRI 11558) |
| E | `BG-TRANS-SPIRAL-SPLICE-SEL-PENDING` | §9-21-6-3-5(الف) |

---

## 3. Blocker A — `BG-TRANS-TIE-ANCHOR-PENDING`

### 3.1 The clause (printed p. 443 / PDF p. 463, re-read this stage)

> «ب- در میلگردهای به قطر ۱۸ تا ۲۵ میلی‌متر و تنش تسلیم بیش از ۲۸۰ مگاپاسکال، وجود
> قلاب استاندارد پیرامون میلگرد طولی، به علاوه‌ی طول مدفون بین وسط ارتفاع مقطع و
> انتهای بیرونی قلاب، بیش‌تر یا مساوی `0.17 f_y/(λ√f_c) · d_b`»

Branches (الف) (`d_b ≤ 16 mm` any `f_y`, or `d_b` 18–25 mm with `f_y < 280 MPa`) and
(پ) (joists, `d_b ≤ 12 mm`) are already executable as
`BG-TRANS-TIE-ANCHOR-STD-HOOK-001` and `BG-TRANS-TIE-ANCHOR-JOIST-STD-HOOK-001` and are
untouched.

### 3.2 Audit answers

| # | Question | Answer |
| :-- | :-- | :-- |
| 1 | Governing clause | §9-21-6-1-3(ب) |
| 2 | Source available | Yes — page-463 JPG, printed 443, footer-confirmed |
| 3 | Clause completely source-verified? | **Yes** — complete on the page; re-read this stage at 3.4×–5.2× |
| 4 | Every quantity/reference/datum defined? | **NO** — see 3.3 |
| 5 | All dependencies resolved? | `λ` undefined in-clause, §9-21-3 never cited |
| 6 | Required inputs in the engine model? | `d_b`, `f_y`, `f'_c` exist; **λ has no in-clause basis** |
| 7 | Deterministic PASS/FAIL/BLOCKED possible? | **NO** |
| 8 | Exact block reason | λ applicability not established + three printed boundary gaps |
| 9 | New source acquisition required? | **Yes** — see §10 |
| 10 | Safe to implement now? | **NO** |

### 3.3 The two independent blockers

**(i) λ applicability — fatal, unchanged.** The formula contains `λ`. The only `λ`
definition in the entire delivered window is `§9-21-3-1-6` (printed p. 425 / PDF p. 445),
read verbatim this stage:

> «۹-۲۱-۳-۱-۶ در محاسبه طول گیرایی، λ ضریب بتن سبک برای بتن سبک ۰/۷۵ و برای بتن معمولی
> ۱/۰ در نظر گرفته می‌شود.»

That clause scopes itself to «در محاسبه طول گیرایی» — **the development-length
calculation** — and `§9-21-6` **never cites §9-21-3 anywhere**. A citation sweep over the
OCR of PDF pp. 463–470 (both digit orders, i.e. `۹-۲۱-۳…` and the RTL-reversed
`۳-۲۱-۹…`) returns **zero** hits, while the **positive controls on the same pages do
fire**: `§9-21-4` forms appear (PDF 468) and `§9-21-6-1-3` / `§9-21-6-1-4` forms appear
(PDF 464, 468). The zero is therefore meaningful, not an OCR artifact. Adopting
`§9-21-3-1-6`'s λ inside §9-21-6-1-3(ب) would be an **outside-clause substitution**,
which the standing rules prohibit.

**(ii) Three printed boundary gaps — unchanged, never interpolated.**
`f_y = 280 MPa` exactly lies in neither (الف) (`< 280`) nor (ب) (`> 280`);
`d_b = 17 mm` lies between the printed `≤ 16 mm` and `18–25 mm`; `d_b > 25 mm` is
assigned to no branch.

### 3.4 A refined reading recorded this stage (supersedes one earlier finding)

The earlier stages (H.10 §8.1, restated in H.12 §95 and H.13 §349) recorded that “the
embedment end-referent and the outer-hook compared quantity are elided in print”.
**The direct re-read does not support that for the referent**: the (ب) sentence spans the
line break, ending the first line with «… و انتهای» and opening the next line with
«بیرونی قلاب بیش‌تر یا مساوی `0.17f_y/λ√f_c·d_b`». The text as printed therefore gives
both measurement endpoints — the **mid-depth of the section** and the **outer part of the
hook** — and states the `≥ 0.17 f_y/(λ√f_c)·d_b` requirement on that embedded length.

**This refinement changes no status.** λ applicability (§3.3-i) and the three boundary
gaps (§3.3-ii) are each independently fatal, and the clause's chapeau («مهار میلگرد و سیم
آجدار در خاموت باید منطبق بر شرایط زیر باشد») makes (ب) a conjunctive bundle — hook +
embedment length + the λ-dependent quantity — so **no partial rule may PASS**.

**Classification: `AMBIGUITY`** (source does not determine the required interpretation:
λ scope) **+ genuine printed boundary gaps.**

---

## 4. Blocker B — `BG-TRANS-WIRE-TIE-PENDING`

### 4.1 The clause (printed p. 444 / PDF p. 464, re-read this stage)

> «۹-۲۱-۶-۱-۵ مهار دو انتهای خاموت متشکل از سیم جوش شده با تنها یک ساق، توسط دو سیم
> طولی با فاصله‌ی حداقل ۵۰ میلی‌متر از یک‌دیگر، با تامین شرایط زیر مجاز است.
> الف- وجود حداقل یک سیم طولی داخلی، با فاصله‌ی بیش‌تر از یک چهارم عمق موثر و ۵۰
> میلی‌متر از نصف عمق موثر مقطع، هر کدام بزرگ‌تر است.
> ب- سیم طولی خارجی در وجه کششی باید از نزدیک‌ترین میلگردهای طولی اصلی خمشی، به وجه
> کششی نزدیک‌تر باشد.»

### 4.2 Audit answers

| # | Question | Answer |
| :-- | :-- | :-- |
| 1 | Governing clause | §9-21-6-1-5 |
| 2 | Source available | Yes — page-464 JPG, printed 444, footer-confirmed |
| 3 | Clause completely source-verified? | **Yes** — complete on the page |
| 4 | Every quantity/reference/datum defined? | **NO** — (الف)'s datum and (ب)'s comparison |
| 5 | All dependencies resolved? | No dependency edge registered; the gap is internal to the clause |
| 6 | Required inputs in the engine model? | `d` exists; the **measurement datum** does not |
| 7 | Deterministic PASS/FAIL/BLOCKED possible? | **NO** |
| 8 | Exact block reason | (الف)'s “whichever is greater” comparison has no determinable datum; (ب) carries no governing number |
| 9 | New source acquisition required? | **No new document** — an authorised reading of the datum is required |
| 10 | Safe to implement now? | **NO** |

### 4.3 Findings

- **The chapeau is conjunctive.** «… با تامین شرایط زیر مجاز است» requires **both** (الف)
  and (ب). A rule covering only one of them could therefore never legitimately PASS —
  any such partial rule is prohibited by the standing rules regardless of the datum
  question.
- **(الف) is elliptical.** The printed string admits, and does not disambiguate between,
  two readings: (i) a distance **greater than `max(¼d, 50 mm)` measured from the
  mid-depth of the section** («نصف عمق موثر مقطع»), or (ii) a distance greater than `¼d`
  from one datum **and** 50 mm from the mid-depth. Which datum the 50 mm term attaches to
  is not stated. Choosing between them would be converting ambiguity into an assumption.
- **(ب) has no governing number** — it is a purely relative comparison (“closer to the
  tension face than the nearest main flexural longitudinal bars”). It is *representable*
  with caller-supplied positions only if (الف) were also determinable.
- **No datum may be imported from the sister clause or the figure.** §9-21-6-1-4 does
  carry the datum «از وجه فشاری» («from the compression face»), but §9-21-6-1-5 does not
  inherit it and does not cite it. Figure 9-21-1 (printed p. 445 / PDF p. 465), whose
  callouts are «۵۰ mm» and «حداکثر l/4», is the figure **for §9-21-6-1-4** — its caption
  («مهار در ناحیه‌ی فشاری خاموت U شکل متشکل از شبکه‌ی سیمی ساده‌ی جوش شده») and its
  dimensions match (الف)/(ب) of **-1-4**, and §9-21-6-1-5 does not cite it. No geometry
  was read from it.
- **Boundary unchanged:** the 50 mm minimum wire-to-wire spacing and the two lengths exist
  as printed numbers; only the datum of the comparison is undetermined.

**Classification: `AMBIGUITY`.**

---

## 5. Blocker C — `BG-TRANS-TORSION-TIE-PENDING`

### 5.1 The clauses (PDF pp. 464 and 468, both re-read this stage)

> §9-21-6-1-6-ب (PDF 464): «… مهار را می‌توان با لحاظ نمودن الزامات ۹-۲۱-۶-۱-۳-الف یا ب،
> و یا ۹-۲۱-۶-۱-۴ تامین نمود.»

> §9-21-6-2-7-ب (PDF 468): «… باید الزامات بندهای ۹-۲۱-۶-۱-۳-الف یا ب، یا ۹-۲۱-۶-۱-۴
> تامین گردد.»

### 5.2 Is C genuinely transitive on A?

**Yes — verified this stage, not assumed.** The delegation is an **OR of three
alternatives**:

| Alternative | State |
| :-- | :-- |
| §9-21-6-1-3(الف) | **Executable** — `BG-TRANS-TIE-ANCHOR-STD-HOOK-001` |
| §9-21-6-1-3(**ب**) | **Blocked — this is blocker A** |
| §9-21-6-1-4 | **Executable** — `BG-TRANS-TORSION-TIE-WIRE-ROUTE-001` (route rule, H.7) |

Two of the three alternatives are already executable as route-level rules. The residual
uncovered alternative is exactly A's branch, which inherits every one of A's blocking
causes (λ scope + the three boundary gaps). Under the project's OR-delegation semantics
(implementing one OR route never promotes the whole clause — the rule H.7 established
and H.9/H.10/H.13 upheld), the sentinel remains required for that residual.

**Was it “kept blocked by habit”?** No — the alternative was tested: an *aggregator* rule
(“PASS if any implemented route passes, else BLOCKED”) was considered and rejected,
because it would add **zero verified capability** (its PASS is the OR of PASSes already
obtainable from the two route rules) while adding a new executable surface. Creating it
would be inventing work, not adding verification.

### 5.3 Audit answers

| # | Question | Answer |
| :-- | :-- | :-- |
| 1 | Governing clause | §9-21-6-1-6(ب) and §9-21-6-2-7(ب) |
| 2 | Source available | Yes — PDF pp. 464 and 468 |
| 3 | Clause completely source-verified? | **Yes** — both (ب) clauses are complete on their pages |
| 4 | Every quantity/reference/datum defined? | Only via the delegates; the -1-3(ب) delegate is not |
| 5 | All dependencies resolved? | **No** — residual alternative = A |
| 6 | Required inputs in the engine model? | Same as A for the residual route |
| 7 | Deterministic PASS/FAIL/BLOCKED possible? | Only per-route (already achieved); not for the clause as a whole |
| 8 | Exact block reason | Transitively on A |
| 9 | New source acquisition required? | Only what A requires |
| 10 | Safe to implement now? | **NO** |

**Classification: `TRANSITIVE_BLOCKER` (on A).**

---

## 6. Blocker D — `BG-TRANS-WIRE-SUBST-PENDING`

### 6.1 Audit answers

| # | Question | Answer |
| :-- | :-- | :-- |
| 1 | Governing clause | §9-21-6-2-3 (via §9-21-6-2-1 and §9-4-8, i.e. §9-4-8-7 → ISIRI 11558) |
| 2 | Source available | Yes — Mabhas 9 PDF p. 466 (H.13) + §9-4-8 pages (H.14) + **ISIRI 11558, 19 pages, obtained and verified in full (H.16)** |
| 3 | Clause completely source-verified? | **Yes** — the Mabhas 9 clause and the entire external standard are verified |
| 4 | Every quantity/reference/datum defined? | The standard is complete; the **conformity predicate** is not design-evaluable |
| 5 | All dependencies resolved? | **No** — see 6.2 |
| 6 | Required inputs in the engine model? | **None can carry the requirement** |
| 7 | Deterministic PASS/FAIL/BLOCKED possible? | **NO** |
| 8 | Exact block reason | Conformity to 11558 = ISO 10144 third-party certification **or** 15/60-sample lot statistics on a ≤50 t consignment; plus the 500 MPa ↔ 420 MPa rating mismatch; plus the standard contains no welded-fabric requirement, so the Mabhas 9 mesh-vs-tie ambiguity stands |
| 9 | New source acquisition required? | **No** — the document is in hand; a **governance decision** is required |
| 10 | Safe to implement now? | **NO** |

### 6.2 Consistency check performed (no re-verification attempted)

H.16 was **not re-opened**. The audit only checked whether a concrete error exists in the
H.16 decision; the three load-bearing claims were cross-checked for consistency with the
retained evidence package (`phase2f-source-11558/`, PDF SHA-256 unchanged):

1. ISIRI 11558 defines a single rating `R_p0.2 = 500 N/mm²`, `R_m = 550 N/mm²`,
   `A_5.65 = 12 %` — while the Mabhas 9 Table 9-4-4 shear/tie row caps design yield at
   **420 MPa**, and the standard provides no class-to-application mapping.
2. Clause 11 offers exactly two conformity routes: **(الف)** third-party supervision per
   **ISO 10144:1991**, or **(ب)** consignment testing accepted statistically
   (`m₁₅ − 2.33·s₁₅ ≥ f_k`, escalating to 60 samples).
3. «جوش» (welded) occurs only in the document's title — there is **no** welded-fabric
   normative content.

**No error found. D remains blocked exactly as H.16 concluded.**

**Classification: `EXTERNAL_DEPENDENCY` + `INPUT_MODEL_GAP`** (secondary: `SCOPE_GAP`,
`AMBIGUITY`).

---

## 7. Blocker E — `BG-TRANS-SPIRAL-SPLICE-SEL-PENDING`

### 7.1 The clause (printed p. 448 / PDF p. 468, re-read this stage)

> «۹-۲۱-۶-۳-۵ وصله‌ی دورپیچ‌ها با یکی از روش‌های زیر انجام می‌شود
> الف- وصله‌ی جوشی یا مکانیکی مطابق بند ۹-۲۱-۴-۷.»

The lap alternative, (ب), is already executable as
`BG-TRANS-SPIRAL-SPLICE-LAP-SEL-001` and is untouched.

### 7.2 **Correction recorded this stage: the blanket Chapter 10 attribution is too broad**

The registered reason reads “the (الف) welded/mechanical-splice branch depends on Clause
9-21-4-7, which is itself blocked via NBC Chapter 10 welding requirements”. The direct
re-read shows Chapter 10's scope is **welded splices only** (printed p. 441 / PDF p. 461):

> «۹-۲۱-۴-۷-۳ **جوش میلگردها در وصله‌های جوشی** باید الزامات مبحث دهم مقررات ملی ساختمان
> را تامین نماید.»

So the dependency splits:

| Sub-branch of §9-21-6-3-5(الف) | Chapter 10? | State |
| :-- | :-- | :-- |
| **Welded** splice | **Yes** — §9-21-4-7-3 | Genuinely blocked: NBC Chapter 10 pages are not in any evidence package |
| **Mechanical** splice | **No** | Not blocked by Chapter 10; blocked by its own residues — see 7.3 |

This does **not** make E resolvable, but it is the precise dependency structure and
supersedes the blanket statement.

### 7.3 Why the mechanical sub-branch still cannot execute

Read at full resolution this stage from printed p. 441 / PDF p. 461:

- **§9-21-4-7-4** — mechanical splices transfer force «از طریق غلاف اتکایی، کوپلر، غلاف
  کوپل کننده و غیره»: descriptive; **no predicate** to evaluate.
- **§9-21-4-7-5** — «برای تامین پوشش بتنی کافی روی میلگرد، اثر افزایش ابعاد میلگرد ناشی
  از وصله‌ی مکانیکی باید در نظر گرفته شود»: a **qualitative obligation** with no
  measurable predicate and no stated governing diameter. Operationalising it as a cover
  check would be an interpretation (and the cover rule's own diameter classes would need
  a governing diameter the clause does not supply).
- **§9-21-4-7-6** — «وصله‌ی مکانیکی یا جوشی باید قادر به انتقال تنشی حداقل برابر با ۱/۲۵
  برابر تنش تسلیم میلگرد در کشش و یا فشار باشد» (1.25·f_y, **re-confirmed visually this
  stage**): a performance requirement on a **proprietary device**, testable only against
  a declared manufacturer capacity. Structurally this is the same class of problem as D —
  an executable rule here would rest on a caller-supplied assertion of device capacity.
- **§9-21-4-7-7 / -7-8** — staggering not required except in tension members (arch ties,
  members delivering load to a higher support, truss tension members), where adjacent
  splices must be staggered **750 mm**: representable with a caller-supplied
  `is_tension_member`.
- **Pure-delegation semantics**: §9-21-6-3-5(الف) adds nothing of its own, so its
  determinism equals the delegated clause's. The delegate is owned by a **separate**
  sentinel, `BG-DEV-SPLICE-WELDED-MECH-PENDING` (outside the five), which remains
  `VERIFY_PENDING`; promoting a route rule here would either duplicate the delegate's
  content (contrary to the delegation pattern) or promote a rule outside this task's
  scope.

### 7.4 Audit answers

| # | Question | Answer |
| :-- | :-- | :-- |
| 1 | Governing clause | §9-21-6-3-5(الف) → §9-21-4-7 |
| 2 | Source available | Yes — PDF pp. 460–461 (§9-21-4-7-1…-8) and PDF p. 468 (the delegating clause) |
| 3 | Clause completely source-verified? | **Yes** for the in-window text; **NBC Chapter 10 pages are absent** |
| 4 | Every quantity/reference/datum defined? | **NO** — (mechanical) no diameter for the cover effect; capacity is declared, not derivable; (welded) Chapter 10 absent |
| 5 | All dependencies resolved? | **No** |
| 6 | Required inputs in the engine model? | Splice type and staggering are representable; the device capacity and the -7-5 predicate are not |
| 7 | Deterministic PASS/FAIL/BLOCKED possible? | **NO** |
| 8 | Exact block reason | Welded sub-branch: NBC Chapter 10 not delivered. Mechanical sub-branch: qualitative §9-21-4-7-5 + declared-capacity §9-21-4-7-6 + separate owning sentinel |
| 9 | New source acquisition required? | **Yes for the welded route** (Chapter 10); **no** for the mechanical route — that needs a project decision |
| 10 | Safe to implement now? | **NO** |

**Classification: `EXTERNAL_DEPENDENCY` (welded) + `AMBIGUITY` / `INPUT_MODEL_GAP`
(mechanical).**

---

## 8. Classification summary

| | Blocker | Classification | New source needed? | Implementable now? |
| :-- | :-- | :-- | :-- | :-- |
| A | `BG-TRANS-TIE-ANCHOR-PENDING` | `AMBIGUITY` (+ printed boundary gaps) | Yes (λ applicability evidence) | **No** |
| B | `BG-TRANS-WIRE-TIE-PENDING` | `AMBIGUITY` | No — needs an authorised reading | **No** |
| C | `BG-TRANS-TORSION-TIE-PENDING` | `TRANSITIVE_BLOCKER` (on A) | Only what A needs | **No** |
| D | `BG-TRANS-WIRE-SUBST-PENDING` | `EXTERNAL_DEPENDENCY` + `INPUT_MODEL_GAP` | No — needs a governance decision | **No** |
| E | `BG-TRANS-SPIRAL-SPLICE-SEL-PENDING` | `EXTERNAL_DEPENDENCY` (welded) + `AMBIGUITY`/`INPUT_MODEL_GAP` (mechanical) | Yes for welded; no for mechanical | **No** |

**Zero of the five satisfies all eight selection criteria** (no unresolved external source;
no unresolved ambiguity; no missing critical datum; no unsupported assumption; representable
in the engine; complete deterministic PASS/FAIL/BLOCKED; traceable evidence; narrow scope).
Per the stage rule, the audit stops here: **nothing is implemented.**

---

## 9. Determinism and false-PASS analysis

| Property | State |
| :-- | :-- |
| All five sentinels | `VERIFY_PENDING`, `execution_allowed=False` — unchanged |
| Can any of the five return PASS? | **No** — none is executable |
| Is there any partial rule that could PASS on one branch? | **No** — none was created (A, B and E each present conjunctive bundles; C's residual route is A; D has no evaluable branch) |
| Transitive enforcement | `BG-TRANS-SPIRAL-SPLICE-SEL-PENDING` → `BG-DEV-SPLICE-WELDED-MECH-PENDING` is registered and the gatekeeper traverses dependencies recursively (`_find_blocked_transitive_dependency`), returning a blocked trace step |
| Effect of this stage on behaviour | **None** — documentation only |

---

## 10. What exact evidence would unlock each blocker

| | Unlocking requirement |
| :-- | :-- |
| **A** | Source establishing that the `λ` in §9-21-6-1-3(ب) is governed by §9-21-3-1-6 (i.e. an edition/print of Mabhas 9 in which §9-21-6 cites §9-21-3, or equivalent authoritative errata), **and** a resolution of the three printed boundaries (`f_y = 280`, `d_b = 17 mm`, `d_b > 25 mm`). Neither is present in the delivered window. |
| **B** | An authorised reading of §9-21-6-1-5(الف)'s datum (which distance is measured from the mid-depth of the section), or an edition/figure that fixes it for **-1-5** specifically. Note the chapeau is conjunctive, so (ب) alone can never yield PASS. |
| **C** | Whatever unlocks A — nothing more. (The two other OR alternatives are already executable as route rules.) |
| **D** | A project-level decision among the three options recorded in H.16 §9: (1) certificate-based conformity declared executable-but-not-self-verifying; (2) lot-test-data-based conformity on caller-supplied statistics; (3) an explicit scope determination that product conformity is outside the engine's remit. Additionally required for any wire/mesh branch: the 500 MPa ↔ 420 MPa application mapping and the Mabhas 9 Table 9-4-4 mesh-vs-tie ambiguity. |
| **E** | *Welded route:* the NBC Chapter 10 pages (absent from every evidence package). *Mechanical route:* promotion of the delegate §9-21-4-7 mechanical branch under its own §4 gate, **plus** a project decision on §9-21-4-7-5's operationalisation and on accepting a declared device transfer capacity for §9-21-4-7-6. |

---

## 11. Which blocker should be attacked next

**Nearest term: E, mechanical sub-branch** — because it is the only residual that needs
**no new external document**. It is gated on two decisions and one separate promotion:

1. promote the §9-21-4-7 mechanical branch (owner: `BG-DEV-SPLICE-WELDED-MECH-PENDING`)
   under its own dependency gate;
2. decide how §9-21-4-7-5 is represented (which diameter governs the cover effect, and
   whether a cover check is the intended operationalisation);
3. decide whether a declared device transfer capacity may be accepted for §9-21-4-7-6.

**Ordered after that:** **B** (needs one authorised datum reading; the cheapest
source-only candidate), **D** (already fully sourced — gated only on a governance
decision, see §10), **A** (needs evidence not present in the delivered window), **C**
(follows A).

---

## 12. What this stage changed

| Category | Change |
| :-- | :-- |
| Rule statuses | **None** |
| Registry / catalog | **None** |
| Evaluators / engine | **None** |
| Tests | **None** |
| Rule ID set, counts, dependency edges | **None** |
| Documentation | This record (`docs/PHASE2F_STAGE_H17_REMAINING_BLOCKER_AUDIT.md`) |
| Corrections recorded | (i) A's embedment referent is present in the print across the line break — supersedes the “elided referent” finding; (ii) E's Chapter 10 dependency is welded-only, not blanket; (iii) the §9-21-3 citation sweep now carries positive controls. **No status follows from any of the three.** |

Recommended, deliberately **not** performed here (behaviour-neutral metadata refresh, to
be done only alongside a stage that already touches the registry): narrow
`BG-TRANS-SPIRAL-SPLICE-SEL-PENDING`'s `blocked_reason` to the welded sub-branch and add
the mechanical residues recorded in §7.3.

---

## 13. Validation of the unchanged system

| Gate | Result |
| :-- | :-- |
| `PYTHONPATH=src pytest` | **673 passed** |
| `PYTHONPATH=src mypy --strict` | **clean — 23 source files** |
| Registry | **121 total / 63 executable / 48 blocked / 10 reference** — unchanged |
| Duplicate Rule IDs | **0** |
| §9-21-6 predicate | **21 executable / 5 blocked** — unchanged |
| The five sentinels | all `VERIFY_PENDING`, `execution_allowed=False` — unchanged |
| ISIRI 11558 PDF SHA-256 | `4c1c…916c` — unchanged |
| `git diff --check` | clean |
| `origin/main` | `df8067a750ffc7984c9dc5d80220ad9013503aa6` — untouched |

---

*H.17 re-audited all five remaining §9-21-6 blockers against their actual source pages.
None can be fully resolved today. The stage therefore implements nothing — governance
over feature count — and records, per blocker, the precise cause and the exact evidence
that would unlock it.*
