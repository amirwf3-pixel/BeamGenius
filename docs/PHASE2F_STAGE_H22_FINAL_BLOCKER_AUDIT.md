# Phase 2F — Stage H.22: Final Dependency / Evidence Audit for the Five Remaining
# Transverse-Reinforcement Blockers

**H.22 DECISION: `ALL FIVE REMAIN BLOCKED — NO NEW EVIDENCE RESOLVES ANY OF THEM`.**
This is a **successful** outcome: the purpose of H.22 was to establish whether the five
blockers are genuinely exhausted under currently available evidence.

**Result: they are — with one exception that sharpens a reopen condition rather than
resolving it** (see §5, the evidence-window boundary finding).

Documentation only. **No evaluator, no status, no count and no `execution_allowed` flag was
changed.**

---

## 1. Scope

| | |
| :-- | :-- |
| Purpose | Determine whether the five remaining transverse-reinforcement blockers have any **new, already-available, source-authorised** evidence that can legitimately resolve them |
| Blockers in scope | A `BG-TRANS-TIE-ANCHOR-PENDING` · B `BG-TRANS-WIRE-TIE-PENDING` · C `BG-TRANS-TORSION-TIE-PENDING` · D `BG-TRANS-WIRE-SUBST-PENDING` · E `BG-TRANS-SPIRAL-SPLICE-SEL-PENDING` |
| Method | Repository-wide evidence inventory; **complete window page-map** (all 31 pages); delta audits per blocker; targeted source-bridge sweeps; dependency-graph construction; freeze-readiness classification |
| Not done (by instruction) | No repetition of H.17–H.21 audits; no new interpretations; no implementation; no scope broadening |
| Standing baseline | H.17–H.21 conclusions are treated as the **current verified baseline**, subject only to genuinely new evidence |

**Evidence-class labels used throughout:** `VERIFIED FACT` · `EXISTING PRIOR FINDING` ·
`NEW FINDING` · `INFERENCE` · `REQUIRED FUTURE EVIDENCE`.

---

## 2. Baseline

| Item | Value |
| :-- | :-- |
| HEAD at stage start | **`36c387b`** (local HEAD was stale at `f22ff45`; recovered without `--hard`, without rewriting history) |
| Previous H.21 stage commit | **`67e3edd`** — present in the chain |
| Working tree | clean |
| Branch | `arena/b9cd291a-beamgenius` |
| `origin/main` | **`df8067a750ffc7984c9dc5d80220ad9013503aa6`** — untouched |
| `pytest` | **673 passed** |
| `mypy --strict` | **clean — 23 source files** |
| Registry | **121 / 63 executable / 48 blocked / 10 reference** |
| Duplicate Rule IDs | **0** |
| §9-21-6 | **21 executable / 5 blocked** |
| All five sentinels | `VERIFY_PENDING`, `execution_allowed=False` — confirmed by registry read |

**No baseline discrepancy. Stage proceeded.**

---

## 3. Existing blocker matrix (from H.17–H.21, not reinterpreted)

| | Rule | Source clause(s) | Primary blocker | Secondary blocker | Status |
| :-- | :-- | :-- | :-- | :-- | :-- |
| **A** | `BG-TRANS-TIE-ANCHOR-PENDING` | §9-21-6-1-3(ب) — printed 443 / PDF 463 | **λ applicability** not established (H.20) | unprimed `f_c` undefined; `f_y = 280` gap; `16 < d_b < 18`; `d_b > 25` | `VERIFY_PENDING` |
| **B** | `BG-TRANS-WIRE-TIE-PENDING` | §9-21-6-1-5 — printed 444 / PDF 464 | **(الف) datum + governed quantity absent** (H.19) | figure not applicable; clause never cited | `VERIFY_PENDING` |
| **C** | `BG-TRANS-TORSION-TIE-PENDING` | §9-21-6-1-6(ب) & §9-21-6-2-7(ب) | **`TRANSITIVE_BLOCKER` on A** (H.17) | — | `VERIFY_PENDING` |
| **D** | `BG-TRANS-WIRE-SUBST-PENDING` | §9-21-6-2-3 → §9-4-8-7 → ISIRI 11558 | **`EXTERNAL_DEPENDENCY`** + conformity not design-evaluable (H.16/H.17) | `INPUT_MODEL_GAP`; 500↔420 mismatch; no welded-fabric content in 11558 | `VERIFY_PENDING` |
| **E** | `BG-TRANS-SPIRAL-SPLICE-SEL-PENDING` | §9-21-6-3-5(الف) → §9-21-4-7 | **§9-21-4-7-5 cover obligation `AMBIGUITY`** (H.21) | -7-6 capacity `INPUT_MODEL_GAP`; -7-3 → NBC Ch. 10 `EXTERNAL_DEPENDENCY` | `VERIFY_PENDING` |

**What would be required to resolve each** (carried forward, unreinterpreted): A — a
source-defined λ meaning/applicability or a symbols clause; B — a governing datum and
comparison quantity in, or cross-referenced by, §9-21-6-1-5(الف); C — anything that
resolves A's residual route; D — a source-defined conformity predicate representable as a
design input, or a governance decision; E — a quantified basis for -7-5 plus a
source-supported device-capacity route plus NBC Chapter 10.

---

## 4. New-evidence search methodology

### 4.1 Complete evidence inventory

| Evidence set | Location | Size | Coverage |
| :-- | :-- | :-- | :-- |
| `phase2f-source-442-472/` | **`origin/main` @ `df8067a` only** | 62 files (31 JPG + 31 TXT) | Mabhas 9 **printed pp. 422–452 / PDF 442–472** |
| `phase2f-source-11558/` | branch | 3 files (PDF + README + VERIFICATION-NOTE) | ISIRI 11558, 19 pages, 1st ed. |
| `phase2f-source-948/` | branch | 5 files (README + 4 PNG) | Mabhas 9 **printed pp. 66–69 / PDF 86–89** (§9-4-8) |
| `docs/` | branch | 21 files | 16 stage/audit records + 2 governance docs + matrix |

**Provenance finding (`NEW FINDING`).** `phase2f-source-442-472/` is **not present in our
worktree and not tracked on our branch**; it exists only on **`origin/main` @ `df8067a`**.
Every page read in this stage (and in H.17–H.21) was obtained **read-only** via
`git show origin/main:...` into the git-ignored `working/h22/`. **`origin/main` was not
written, checked out, merged or rebuilt.** The `working/`, `references/`, `ocr/`,
`extracted/` and `verification/` directories are git-ignored; no committed evidence exists
under them.

**No other evidence images exist** anywhere in the repository: a sweep for `.jpg/.jpeg/.png/.pdf`
outside the three evidence directories returns **zero** files.

### 4.2 Full window page-map (all 31 pages read)

Every page in PDF 442–472 was extracted and its opening headings inspected, producing a
complete clause map. This is the first stage to map **all 31 pages** rather than the
blocker-local pages.

| PDF | Printed | Content (navigation map) |
| :-- | :-- | :-- |
| 442–443 | 422–423 | §9-21-2-2-2/-2-2-3 hooks; Table 9-21-1/9-21-2 |
| 444–445 | 424–425 | §9-21-2-2-4/-2-2-6; **§9-21-3 heading «طول گیرایی»**, -1-1…-1-6 (**λ**), Eq. (9-21-1) |
| 446–450 | 426–430 | §9-21-3-2/-3 (Tables 9-21-3…9-21-5, Eq. 9-21-2) |
| 451–452 | 431–432 | §9-21-3-4 headed bars, Table 9-21-6 |
| 453–455 | 433–435 | §9-21-3-5 mechanical anchorage (Eq. 9-21-4), §9-21-3-6 wire mesh (Eq. 9-21-5) |
| 456–459 | 436–439 | §9-21-3-7/-8, §9-21-4-1/-2/-3/-4 (**-4-4-2 at p459**) |
| 460–462 | 440–442 | §9-21-4-4-2/-5 → **§9-21-4-7 (chapeau, -7-1…-7-8)**; §9-21-5 bar bundles |
| 463–465 | 443–445 | §9-21-6-1-1…-1-6, **Figure 9-21-1** |
| 466–470 | 446–450 | §9-21-6-2 (spacing, wire substitution), **-2-7 torsion ties**, §9-21-6-3 spirals, -3-5/-3-6 |
| **471–472** | **451–452** | **§9-22 «مدارک طرح، الزامات ساخت و نظارت» — previously uninspected (see §4.3)** |

### 4.3 Genuinely new pages found — `§9-22` (PDF 471–472)

**`NEW FINDING`.** Chapter **§9-22** occupies the last two pages of the window and was
**never inspected or cited in any prior stage** (H.17 documented only PDF 464/468; H.18/H.21
worked within §9-21-4-7; H.20 within §9-21-3/-6). Both pages were **visually read at full
resolution** this stage.

**Verified content:**

- **§9-22-1 گستره** — scope: the chapter covers «مواردی … که مهندس طراح باید، در حد کاربرد، در
  مدارک طرح ارائه دهد»: (الف) design information with drawings and technical
  specifications; (ب) technical-executive requirements for the contractor («الزامات
  اجرائی»); (پ) supervision details.
- **§9-22-2 مبانی طراحی / -2-1 اطلاعات طراحی** — (الف) names/years of the by-laws, national
  regulations **and other supplementary documents used in design**; (ب) design loads;
  (پ) work delegated to the contractor.
- **§9-22-3 اطلاعات طراحی اعضای سازه** — (الف) member dimensions, positions and their
  relationships; (ب) construction material specifications.
- **§9-22-4 الزامات اجرایی مصالح و مخلوط بتن / -4-1 سیمان** — cement selection grouped by
  two recognised methods (Iranian practice vs. US-referenced practice), with Tables 9-22-1
  and 9-22-2; «در این مبحث استفاده از گروهبندی در هر دو روش، به شرط رعایت
  استانداردهای آنها، مجاز میباشد».

**Blocker-relevance test — the decisive measurement.** A term sweep over both pages:

| Term | Count on pp. 471–472 |
| :-- | :-- |
| مکانیکی (mechanical) · کوپلر (coupler) · پوشش (cover) · وصله (splice) · گیرایی (development) · جوش (welding) · شبکه (mesh) · ظرفیت (capacity) · خاموت (tie) · ۱۱۵۵۸ · λ | **0 each** |

**`VERIFIED FACT`: §9-22 is administrative (design documents, construction requirements,
supervision) and contains no provision bearing on any of the five blockers. It resolves
nothing.**

### 4.4 Evidence-window boundary (`NEW FINDING`)

The delivered Mabhas 9 window is **printed pp. 422–452 / PDF 442–472**. Verified boundaries:

- **The window begins mid-chapter**: PDF 442 opens with **§9-21-2-2-2**, i.e. inside
  §9-21-2. **§9-21-1 (chapter general provisions) and the §9-21 chapter opening lie BEFORE
  the window** (printed pp. ≈418–421 / PDF ≈438–441) and were **never delivered or
  inspected**.
- **The window ends mid-chapter**: PDF 472 ends inside **§9-22-4-1** (cement grouping).
- A sweep of the whole window for a symbols/notation clause («علائم», «نماد») returns
  **NONE**; a sweep for the §9-21-1 chapter-general identifier returns **NONE**.

**Consequence for A.** H.20's conclusion — "λ has exactly one definition in the window and
no symbols clause exists" — is now **precisely bounded**: it holds **within the delivered
window**, while the chapter opening (a plausible location for a global notation clause) was
never acquired. This is **not** a resolution and does **not** unblock A (missing evidence is
never a resolution, and no such clause has been seen). It **sharpens A's reopen condition**
into an actionable source-acquisition item: **acquire printed pp. ≈418–421 / PDF ≈438–441**.

---

## 5. A — delta audit

`BG-TRANS-TIE-ANCHOR-PENDING` · §9-21-6-1-3(ب)

| # | Question | Answer | Class |
| :-- | :-- | :-- | :-- |
| 1 | NEW source evidence establishing λ applicability to §9-21-6? | **None found.** The complete 31-page window map adds no λ-bearing clause beyond §9-21-3-1-6. §9-22 (the only uninspected pages) contains no λ | `VERIFIED FACT` |
| 2 | A global Mabhas symbol definition previously missed? | **None within the window.** `NEW FINDING`: the chapter opening is **outside** the window — see §4.4. This is an evidence gap, not a definition | `NEW FINDING` |
| 3 | Explicit cross-reference §9-21-6 → §9-21-3? | **None.** Re-confirmed by the full-page map: no §9-21-6 page cites §9-21-3 | `EXISTING PRIOR FINDING` (re-confirmed) |
| 4 | Another clause legally extending λ to this calculation? | **None found** in the window | `VERIFIED FACT` |
| 5 | Is `f_c` (unprimed) defined in the relevant context? | **No.** The window defines no such symbol; the unprimed `f_c` remains undefined | `EXISTING PRIOR FINDING` |
| 6 | Are the boundary gaps resolved elsewhere by an explicit source rule? | **No.** `NEW FINDING` (negative): the only other printed **420 MPa** tie/splice boundary in the window is §9-21-4-4-2 (p459, lap length for plain welded mesh) and it **does not cross-reference** §9-21-6-1-3 — so it cannot supply A's 280 MPa / diameter-gap boundaries. The gaps stand | `NEW FINDING` |

**A: NO NEW EVIDENCE RESOLVES IT REMAINS BLOCKED.**

---

## 6. B — delta audit

`BG-TRANS-WIRE-TIE-PENDING` · §9-21-6-1-5

| # | Question | Answer | Class |
| :-- | :-- | :-- | :-- |
| 1 | Is -1-5(الف) clarified elsewhere? | **No.** No page in the window restates or explains it | `VERIFIED FACT` |
| 2 | Another figure explicitly assigned to -1-5? | **No.** Visual identification (H.19) established **Figure 9-21-1 is the only numbered figure** in the window; its caption scopes it to compression-zone anchorage and it is cited **only** by -1-4. §9-22 contains no figure | `EXISTING PRIOR FINDING` (re-confirmed) |
| 3 | Later cross-reference defining the datum? | **No.** -1-5 is never cited by any clause in the window; §9-21-6-1-6(ب) cites -1-3(الف/ب) and -1-4 but **not** -1-5 | `EXISTING PRIOR FINDING` (re-confirmed) |
| 4 | A general geometric convention explicitly adopted by Mabhas 9? | **No such adoption exists in the window** — and the chapter opening is outside it (§4.4), so the negative is bounded identically | `NEW FINDING` (bounded negative) |
| 5 | Is the phrase repeated elsewhere **with** a datum? | **Yes — and this is precisely the problem, not the solution.** «یک چهارم عمق موثر» appears exactly twice: -1-4(ب) **with** explicit «از وجه فشاری», and -1-5(الف) **without**. The document attaches the datum when it intends it. The contrast confirms the omission is a text gap | `EXISTING PRIOR FINDING` (re-confirmed) |

**B: NO NEW EVIDENCE RESOLVES IT REMAINS BLOCKED.** The omission is not reinterpreted as
shorthand.

---

## 7. C — delta audit

`BG-TRANS-TORSION-TIE-PENDING` · §9-21-6-1-6(ب) & §9-21-6-2-7(ب)

| # | Question | Answer | Class |
| :-- | :-- | :-- | :-- |
| 1 | An explicit source alternative **in** §9-21-6-1-6(ب)? | The clause's (ب) is an OR: §9-21-6-1-3(الف) **or** (ب), **or** §9-21-6-1-4 | `EXISTING PRIOR FINDING` |
| 2 | An independent route in §9-21-6-2-7(ب)? | Re-read this stage at PDF 467–468 (printed 447–448): **§9-21-6-2-7(ب)** reaches the same delegation («الزامات بندهای ۹-۲۱-۶-۱-۳-الف یا ب، یا ۹-۲۱-۶-۱-۴»). §9-21-6-2-7(الف) — an independent direct option — is **already executable** as `BG-TRANS-TORSION-TIE-STANDARD-HOOK-001` | `VERIFIED FACT` (matches H.17 §5.1) |
| 3 | A cross-reference that **bypasses** §9-21-6-1-3(ب)? | **No.** No clause in the window provides a fourth alternative | `VERIFIED FACT` |
| 4 | An already-verified evaluator capable of satisfying C without A? | **Two route rules exist** (`…TIE-ANCHOR-STD-HOOK-001`, `…TIE-WIRE-ROUTE-001`, plus `…STANDARD-HOOK-001`), but they implement **other** alternatives. Under the project's OR-delegation semantics (established H.7, upheld H.9/H.10/H.13/H.17), implementing some OR routes never promotes the whole clause; the residual alternative **is** A's branch and inherits every one of A's blocking causes. An aggregator rule was already considered and rejected in H.17 as adding zero verified capability | `EXISTING PRIOR FINDING` |

**C: NO NEW EVIDENCE. REMAINS BLOCKED as `TRANSITIVE_BLOCKER` (on A).** C has **no**
independent complete route that eliminates A's dependency. Not duplicated from A's audit.

---

## 8. D — delta audit

`BG-TRANS-WIRE-SUBST-PENDING` · §9-21-6-2-3

**Newly performed this stage: a full-resolution visual read of D's own clause** (PDF 466 /
printed 446, 3.4×), which had previously been handled largely through its OCR layer:

> «۹-۲۱-۶-۲-۳ استفاده از سیم آجدار یا شبکهی آرماتور سیم جوش شده به عنوان جایگزین تنگ
> آجدار، با سطح مقطع معادل میلگرد آجدار با در نظر گرفتن الزامات ۹-۲۱-۶-۲-۱ و ۹-۴-۸»

| Finding | Class |
| :-- | :-- |
| The clause's cross-reference reads **«الزامات ۹-۲۱-۶-۲-۱ و ۹-۴-۸»** — i.e. **§9-21-6-2-1 and §9-4-8**. This **visually resolves** an OCR digit-order ambiguity (OCR rendered it «۸-۴-۹») and **confirms the registered dependency edge** D → §9-4-8 (and thence §9-4-8-7 → ISIRI 11558) | `NEW FINDING` |
| The structure is **conjunctive**: equivalent cross-sectional area **AND** «الزامات ۹-۲۱-۶-۲-۱» (the closed-hoop spacing/diameter provisions, themselves deterministic) **AND** the requirements of §9-4-8 (which carry the non-evaluable conformity predicate) | `NEW FINDING` |
| Therefore a rule implementing only the deterministic parts would be a **partial rule over a conjunction** → potential **false PASS** for material of unknown conformity. Prohibited | `INFERENCE` (from verified text) |

| # | Question (delta) | Answer | Class |
| :-- | :-- | :-- | :-- |
| 1 | Mapping from 11558's 500 MPa to Mabhas' shear-tie design yield? | **None found.** Nothing in the window maps them. `NEW FINDING`: the only other printed 420 MPa boundary in the window is §9-21-4-4-2 (p459 — welded **plain-wire-mesh lap** splices, split at 420 MPa); it is in a different clause family and **does not cross-reference** §9-21-6-2-3 or ISIRI 11558, so it is **not a bridge**. 500 MPa characteristic ≠ 420 MPa design yield | `NEW FINDING` |
| 2 | Applicability of 11558 wire to this specific substitution? | Not established by any clause in the window | `EXISTING PRIOR FINDING` |
| 3 | Welded-mesh conformity requirements? | **None in 11558** (H.16: «جوش» appears only in the title); none added by §9-22 | `EXISTING PRIOR FINDING` |
| 4 | Required certification/testing input? | 11558 offers only third-party certification (ISO 10144:1991) or lot statistics (m₁₅ − 2.33s₁₅ ≥ f_k, ≤50 t consignment) — **neither representable as a design input** | `EXISTING PRIOR FINDING` |
| 5 | Source-defined route to establish compliance? | **None that is design-evaluable** | `EXISTING PRIOR FINDING` |

**D: NO NEW EVIDENCE RESOLVES IT REMAINS BLOCKED.** D's conclusion is unchanged; its
dependency edge is now **visually confirmed** rather than OCR-inferred.

---

## 9. E — delta audit

`BG-TRANS-SPIRAL-SPLICE-SEL-PENDING` · §9-21-6-3-5(الف)

| # | Question (delta) | Answer | Class |
| :-- | :-- | :-- | :-- |
| 1 | Source defining mechanical splice/coupler dimensions? | **None.** The window-wide sweep (re-run on all 31 pages) returns no coupler/dimension content | `VERIFIED FACT` |
| 2 | Effective/enlarged diameter? | **None** — no «قطر خارجی», «قطر موثر» or «قطر معادل» anywhere in the window | `VERIFIED FACT` |
| 3 | Cover adjustment? | **None.** §9-22 is administrative and contains no cover provision; **no clause in the window quantifies «افزایش ابعاد»** | `NEW FINDING` (negative, from the new page-map) |
| 4 | Mechanical splice capacity verification? | **None.** §9-22 adds no capacity, testing or qualification route; the only window clauses containing «آزمایش» (p445, p453) are inside §9-21-3 and concern headed/mechanical **anchorage**, not splices | `NEW FINDING` (negative) |
| 5 | Device qualification / testing / certification? | **None** — no «گواهی», «تصدیق», «تاییدیه», «سازنده» or «کارخانه» in the window | `VERIFIED FACT` |
| 6 | Explicit external-standard bridge? | Only **«مبحث دهم مقررات ملی ساختمان»** (NBC Ch. 10) via §9-21-4-7-3, **welded-only**, pages not in any evidence package. **The window's other «استاندارد» hits are «قلاب استاندارد» (standard hook) or generic standard grouping language — not external-standard bridges for the mechanical route** | `EXISTING PRIOR FINDING` (re-confirmed) |

**E: NO NEW EVIDENCE RESOLVES IT REMAINS BLOCKED.** No external standard was searched for,
acquired or substituted.

---

## 10. Dependency graph

```
                    A  BG-TRANS-TIE-ANCHOR-PENDING  (§9-21-6-1-3-ب)
                    │   root causes: λ applicability · unprimed f_c ·
                    │                f_y=280 · 16<d_b<18 · d_b>25
                    │
                    └──► C  BG-TRANS-TORSION-TIE-PENDING
                            (§9-21-6-1-6-ب / -2-7-ب delegating to -1-3-ب)
                            TRANSITIVE — no independent fourth route exists

    B  BG-TRANS-WIRE-TIE-PENDING  (§9-21-6-1-5)                 INDEPENDENT
       root cause: datum + governed quantity absent from (الف)

    D  BG-TRANS-WIRE-SUBST-PENDING  (§9-21-6-2-3)
       │   conjunctive: equivalent area AND §9-21-6-2-1 AND §9-4-8
       └──► §9-4-8-7 ──► ISIRI 11558  (verified; conformity not design-evaluable)
                                                                    INDEPENDENT

    E  BG-TRANS-SPIRAL-SPLICE-SEL-PENDING  (§9-21-6-3-5-الف)
       └──► BG-DEV-SPLICE-WELDED-MECH-PENDING  (§9-21-4-7-1..8)
              ├── welded  ──► §9-21-4-7-3 ──► NBC Chapter 10  (EXTERNAL, not delivered)
              └── mech.   ──► §9-21-4-7-5 (AMBIGUITY) + §9-21-4-7-6 (INPUT_MODEL_GAP)
                                                                    INDEPENDENT
```

| Edge | Verified? | Auto-resolution? |
| :-- | :-- | :-- |
| A → C | YES (source-based OR-delegation; H.17 §5.1, re-confirmed §7 above) | **Resolving A would clear C's residual route** — but C additionally requires that no *other* blocker applies to it, and the aggregator question was already settled in H.17 |
| D → §9-4-8-7 → ISIRI 11558 | YES — **visually confirmed this stage** (was OCR-inferred) | No |
| E → §9-21-4-7 → {-7-3, -7-5, -7-6} | YES (explicit «مطابق بند ۹-۲۱-۴-۷») | No — three independent sub-causes |
| B | N/A — independent | No |

**Answer to the cross-blocker question:** **resolving no single blocker automatically
resolves any other**, except that A's resolution would remove C's *transitive* cause (C
would then still require its own confirmation that the residual route is the only one
outstanding — a step that H.17 already analysed and that is not automatic). No child has
been treated as resolved by its parent.

---

## 11. Freeze-readiness classification

| | Blocker | Classification | Justification |
| :-- | :-- | :-- | :-- |
| **A** | `BG-TRANS-TIE-ANCHOR-PENDING` | **A — FULLY AUDITED / READY TO FREEZE** (with an **E-component** in its reopen condition) | Exact clause, exact missing information (λ applicability; unprimed `f_c`; three printed boundary gaps), documented non-executability, no available evidence resolves it, no safe partial implementation. Reopening requires **genuinely new source** (chapter opening / a symbols clause / a cross-reference) |
| **B** | `BG-TRANS-WIRE-TIE-PENDING` | **A — FULLY AUDITED / READY TO FREEZE** | Same reasoning; reopening requires a new governing datum/quantity or a newly identified figure/traceability to -1-5 |
| **C** | `BG-TRANS-TORSION-TIE-PENDING` | **A — FULLY AUDITED / READY TO FREEZE (transitively)** | Its cause is fully characterised and correctly attributed to A; no independent route exists; the aggregator option was analysed and rejected |
| **D** | `BG-TRANS-WIRE-SUBST-PENDING` | **E — EXTERNAL SOURCE ACQUISITION REQUIRED** (secondary: **D — INPUT MODEL WORK**, plus a governance decision) | The external standard **is** in hand and verified; what is missing is a **source-defined, design-evaluable conformity predicate** — i.e. either a governance decision on how to treat the certification/lot-statistics predicate, or additional source that maps 11558 to Mabhas' application. **No further source audit is possible** |
| **E** | `BG-TRANS-SPIRAL-SPLICE-SEL-PENDING` | **E — EXTERNAL SOURCE ACQUISITION REQUIRED** (secondary: **D — INPUT MODEL WORK**) | NBC Chapter 10 is not delivered (welded branch); -7-5 needs a quantified basis that no available source contains; -7-6 needs a source-supported capacity route plus an engine input |

**None of the five is `B — MORE SOURCE AUDIT REQUIRED`** (that would mean an unexamined
source remains) and **none is `C — IMPLEMENTATION POSSIBLE`**.

**Not used to hide uncertainty:** each classification above is supported by the explicit
negatives in §5–§9, each of which was measured across the **complete 31-page window plus
the two external evidence sets**, not sampled.

---

## 12. Remaining external dependencies

| Dependency | Owning blocker | Status | Note |
| :-- | :-- | :-- | :-- |
| **NBC Chapter 10** (مبحث دهم مقررات ملی ساختمان) — welding | E (welded route, §9-21-4-7-3) | **Not delivered** | Explicitly cited by Mabhas 9; cannot be substituted |
| **ISIRI 11558** | D | **Delivered and verified** (SHA-256 unchanged) | The dependency is *not* the document — it is the absence of a design-evaluable conformity predicate |
| **ISO 10144:1991** | D (via 11558 Clause 11) | Not delivered | Referenced only *inside* 11558 as a third-party supervision route; the engine has no such input |
| **Mabhas 9 printed pp. ≈418–421 / PDF ≈438–441** (chapter opening) | A (and by transitivity C) | **Not delivered — `NEW FINDING`** | The only unexplored location for a global symbols clause. Acquiring it is a reopen condition |
| Mabhas 9 pages **after** printed 452 | none of the five | Not needed | §9-22 continues beyond the window but is administrative (§4.3) |

---

## 13. Remaining input-model gaps

| Missing input | Needed by | Source-defined? |
| :-- | :-- | :-- |
| distance of the internal longitudinal wire from ⟨datum⟩ | B (الف) | **No — the datum itself is unstated** |
| λ (value and applicability) | A | **No — applicability not established; value conditional on a weight class the clause never mentions** |
| `f_c` (unprimed) meaning | A | **No — symbol undefined in clause and window** |
| outer hook end / embedment geometry | A | Representable **only** with caller-supplied hook geometry; no default may be created |
| splice/device capacity (tension & compression) | E (-7-6) | **No — and capacity may never be inferred from bar f_y** |
| coupler/sleeve dimension, enlarged diameter | E (-7-5) | **No — no value, ratio, datum or basis printed** |
| splice location / member-type classification / 750 mm data | E (-7-7/-8) | Number is deterministic; applicability is conditional and exempted |
| conformity/lot-testing predicate | D | **No — 11558 Clause 11 routes are not design inputs** |

**No input was added.** Per the standing rule, inputs are added only when source
verification proves the rule can otherwise be **fully** executed.

---

## 14. Remaining source ambiguities

1. **A — λ applicability** (§9-21-6-1-3(ب) uses λ; λ is defined only at §9-21-3-1-6, scoped
   «در محاسبه طول گیرایی»; §9-21-6 cites §9-21-3 nowhere; the chapter opening is outside the
   delivered window).
2. **A — unprimed `f_c`** (the affected clause prints `√f_c`; Eq. 9-21-1 prints `√f′_c`;
   nothing in the window defines the unprimed symbol).
3. **A — three printed boundary gaps** (`f_y = 280` exactly; `16 < d_b < 18`; `d_b > 25`).
4. **B — §9-21-6-1-5(الف)** — both the **datum** and the **governed quantity** of the
   «whichever is greater» comparison are absent from the print.
5. **E — §9-21-4-7-5** — «پوشش بتنی کافی» with no threshold, no datum, no measurement basis,
   no cross-reference; «افزایش ابعاد» occurs only there in the window.

---

## 15. Exact conditions required to reopen each blocker

| | Reopen condition (all are **genuinely new source/input material**, not inference) |
| :-- | :-- |
| **A** | (i) acquire Mabhas 9 **printed pp. ≈418–421 / PDF ≈438–441** (chapter opening) and find either a **global symbols/notation clause** defining λ, or (ii) a delivered clause explicitly making §9-21-3-1-6 apply outside its scope, or (iii) a delivered clause defining the unprimed `f_c`, or (iv) a delivered rule resolving the three boundary gaps. **Any one of these, plus a full 12-condition promotion gate.** |
| **B** | (i) a delivered figure explicitly assigned to §9-21-6-1-5, or (ii) a delivered clause supplying the datum **and** the governed quantity for (الف), or (iii) an erratum/corrigendum of the printed clause. **Reinterpreting the omission as shorthand is explicitly excluded.** |
| **C** | **A's** reopen condition (its cause is transitive) — plus an explicit statement that the residual route is the only one outstanding. No independent route exists to reopen. |
| **D** | A **governance decision** on how to represent the 11558 conformity predicate (certification vs lot statistics), **or** newly delivered source that maps 11558's rating to the Mabhas 9 application and/or supplies welded-fabric requirements. The external document itself is already in hand. |
| **E** | (i) a delivered, verified **NBC Chapter 10** (welded branch); **and** (ii) source quantifying §9-21-4-7-5 (enlargement value and/or measurement datum + threshold); **and** (iii) a source-supported route to establish device capacity together with an engine input for it; **or** a recorded project-level decision that the mechanical-splice route is outside the engine's remit. |

---

## 16. Implementation decision

**DOCUMENTATION ONLY — no implementation.** Step 11 permits implementation **only** if a
blocker is completely resolved by new evidence found during H.22. **No blocker was
resolved** (§5–§9), and the sole genuinely new pages (§9-22) resolve nothing (§4.3).

Consequently: no evaluator, no RuleReference change, no `docs/VERIFIED_RULES.md` change, no
matrix change, no test change, no registry promotion, **no partial execution path**, and no
reduction of the blocker count. The five sentinels remain `VERIFY_PENDING` with
`execution_allowed=False`.

---

## 17. Validation

| Gate | Result |
| :-- | :-- |
| `PYTHONPATH=src pytest` | **673 passed** |
| `PYTHONPATH=src mypy --strict` | **clean — 23 source files** |
| Registry consistency | **121 / 63 executable / 48 blocked / 10 reference** — unchanged |
| Duplicate Rule IDs | **0** |
| §9-21-6 | **21 executable / 5 blocked** — unchanged |
| All five sentinels | `VERIFY_PENDING`, `execution_allowed=False` — unchanged |
| `git diff --check` | clean |
| Unrelated changes | none — a single new document |

**Deltas: none.**

---

## 18. Commit SHA

**Baseline at stage start: `36c387b`.**
**This stage's commit (introduces this file): `ad1ecba`.**

The value above is the true hash of the commit that introduced this document; it was
backfilled by a **separate content-only follow-up commit**. No amend, no rebase, no
force-push and no history rewrite was used — both commits are ordinary fast-forward commits
on `arena/b9cd291a-beamgenius`.

---

## 19. origin/main status

`origin/main` remains at **`df8067a750ffc7984c9dc5d80220ad9013503aa6`**, unmodified. All 31
evidence pages were read **read-only** (`git show origin/main:…` into git-ignored
`working/h22/`). No reset, rebase, force-push, history rewrite, merge or branch switch
occurred. All work is on `arena/b9cd291a-beamgenius`.

---

```
H.22 DECISION:            ALL FIVE REMAIN BLOCKED — no new evidence resolves any of them.
                          This is a SUCCESSFUL H.22 outcome: the blockers are genuinely
                          exhausted under currently available repository evidence.

PURPOSE:                  Determine whether any new, already-available, source-authorised
                          evidence can legitimately resolve the five blockers.
                          Answer: NO.

NEW EVIDENCE FOUND:       (1) §9-22 «مدارک طرح، الزامات ساخت و نظارت» (PDF 471–472 /
                          printed 451–452) — a chapter NEVER inspected before; visually
                          read in full; administrative content; ZERO blocker-relevant terms
                          (mechanical/coupler/cover/splice/λ/mesh/welded/capacity/tie all
                          count 0). Resolves nothing.
                          (2) §9-21-6-2-3's cross-reference visually verified as
                          «الزامات ۹-۲۱-۶-۲-۱ و ۹-۴-۸» — resolves an OCR digit-order
                          ambiguity and CONFIRMS D's dependency edge; the requirement is
                          conjunctive (equivalent area AND -6-2-1 AND §9-4-8).
                          (3) §9-21-4-4-2 (p459) carries another printed 420 MPa boundary
                          (welded plain-mesh laps) but does NOT cross-reference D — not a
                          bridge.
                          (4) EVIDENCE-WINDOW BOUNDARY: the window is printed pp. 422–452,
                          starting MID-§9-21-2; §9-21-1 and the chapter opening (a plausible
                          home for a global symbols clause) were NEVER delivered. Bounds
                          A's negative precisely and sharpens its reopen condition.

A:  STATUS:               VERIFY_PENDING / execution_allowed=False (unchanged)
    PRIMARY BLOCKER:      λ applicability not established
    NEW EVIDENCE:         NONE that resolves it; the chapter opening is outside the window
    RESOLVED:             NO
    REOPEN CONDITION:     acquire printed pp. ≈418–421 / PDF ≈438–441 (or a delivered
                          cross-reference / unprimed-f_c definition / boundary resolution)

B:  STATUS:               VERIFY_PENDING / execution_allowed=False (unchanged)
    PRIMARY BLOCKER:      datum + governed quantity absent from §9-21-6-1-5(الف)
    NEW EVIDENCE:         NONE (no figure assigned to -1-5; no citation of -1-5 anywhere)
    RESOLVED:             NO
    REOPEN CONDITION:     a figure/traceability to -1-5, a clause supplying both the datum
                          and the quantity, or an erratum

C:  STATUS:               VERIFY_PENDING / execution_allowed=False (unchanged)
    PRIMARY BLOCKER:      TRANSITIVE on A (no independent fourth route)
    NEW EVIDENCE:         NONE (both (ب) clauses re-confirmed verbatim)
    RESOLVED:             NO
    REOPEN CONDITION:     A's condition (plus confirmation the residual route is the only
                          one outstanding)

D:  STATUS:               VERIFY_PENDING / execution_allowed=False (unchanged)
    PRIMARY BLOCKER:      EXTERNAL_DEPENDENCY + conformity not design-evaluable
    NEW EVIDENCE:         the dependency edge is now VISUALLY CONFIRMED (was OCR-inferred);
                          no bridge to the 500↔420 mapping
    RESOLVED:             NO
    REOPEN CONDITION:     a governance decision on the conformity predicate, or new source
                          mapping 11558 to the Mabhas 9 application

E:  STATUS:               VERIFY_PENDING / execution_allowed=False (unchanged)
    PRIMARY BLOCKER:      §9-21-4-7-5 cover obligation AMBIGUITY
    NEW EVIDENCE:         NONE (§9-22 adds no capacity/cover/qualification content)
    RESOLVED:             NO
    REOPEN CONDITION:     NBC Chapter 10 + a quantified -7-5 basis + a source-supported
                          device-capacity route, or a project-level scope decision

DEPENDENCY GRAPH:         A → C (transitive) · D → §9-4-8-7 → ISIRI 11558 · B independent ·
                          E → §9-21-4-7 → {-7-3 Ch.10, -7-5, -7-6}.
                          No blocker's resolution automatically resolves another (A's
                          resolution would clear C's cause but C still needs its own
                          confirmation).

FREEZE READINESS:         A → A (fully audited / ready to freeze; E-component recorded)
                          B → A (fully audited / ready to freeze)
                          C → A (fully audited / ready to freeze, transitively)
                          D → E (external source acquisition) + D (input model) + governance
                          E → E (external source acquisition) + D (input model)
                          None is "more source audit required"; none is implementable.

IMPLEMENTATION:           NOT PERFORMED — documentation only (no blocker was resolved).
REGISTRY:                 121 / 63 executable / 48 blocked / 10 reference — UNCHANGED
                          (§9-21-6: 21 executable / 5 blocked — unchanged)
PYTEST:                   673 passed
MYPY:                     Success: no issues found in 23 source files
DOCUMENT:                 docs/PHASE2F_STAGE_H22_FINAL_BLOCKER_AUDIT.md
COMMIT:                   see §18
ORIGIN/MAIN:              df8067a750ffc7984c9dc5d80220ad9013503aa6 — untouched
```
