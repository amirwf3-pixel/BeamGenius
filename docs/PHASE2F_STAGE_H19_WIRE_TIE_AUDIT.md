# Phase 2F — Stage H.19: Targeted Audit of Blocker B

**`BG-TRANS-WIRE-TIE-PENDING` — §9-21-6-1-5**

**DECISION: `REMAINS BLOCKED — SOURCE AMBIGUITY` (outcome D, with a C-type secondary).** No
rule was promoted, no evaluator was written, no registry value, status, count or
`execution_allowed` flag was changed. The only artifact of this stage is this record.

This stage performed a targeted re-audit of **blocker B only**, as directed. It did not
reopen H.17/H.18, did not touch A, C, D or E, and did not broaden scope. H.17's
conclusion is **upheld**, and the reason has been **sharpened**: the blocking cause is not
only an unspecified 50 mm datum — it is a **lexical gap** in the printed clause, provable
by direct comparison with the sibling clause's printed vocabulary.

---

## 1. Scope

| | |
| :-- | :-- |
| Target rule | `BG-TRANS-WIRE-TIE-PENDING` |
| Governing clause | §9-21-6-1-5 (printed p. 444 / PDF p. 464) |
| Objective | Determine whether B can now be fully promoted, or must remain blocked |
| Method | Full-resolution visual inspection of the source pages; grammatical/datum analysis; sibling-clause control; engine input-model check; promotion gate |
| Out of scope (untouched) | A, C, D, E; H.14/H.16; UI, reports, DXF, optimisation; unrelated rules |

---

## 2. Environment / baseline

| Item | Value |
| :-- | :-- |
| HEAD at stage start | **`940490d`** (H.18) — confirmed by `git rev-parse HEAD` |
| Working tree | clean (no tracked modifications) after environment recovery |
| Branch | `arena/b9cd291a-beamgenius` |
| `origin/main` | **`df8067a750ffc7984c9dc5d80220ad9013503aa6`** — unmodified, never checked out |
| Evidence package | `phase2f-source-442-472/` on `origin/main` @ `df8067a` (31 JPG + 31 TXT) — read **read-only** into the git-ignored `working/h19/` |
| Tooling | `/tmp/bgvenv` rebuilt once (Pillow + pytest + mypy) |
| Baseline gates | `pytest` **673 passed** · `mypy --strict` clean (23 files) · registry **121 / 63 exec / 48 blocked / 10 ref** · duplicate IDs **0** · §9-21-6 **21 exec / 5 blocked** |

No reset (`--hard`), rebase, force-push or `origin/main` write was performed.

---

## 3. Exact source evidence

Page identification, all footer-confirmed on the rendered images:

| PDF page | Printed page | Content |
| :-- | :-- | :-- |
| 463 | ۴۴۳ | §9-21-6-1-1 (tie extent), §9-21-6-1-2, §9-21-6-1-3 (chapeau + الف/ب/پ) |
| **464** | **۴۴۴** | **§9-21-6-1-4, §9-21-6-1-5, §9-21-6-1-6** ← the target page |
| 465 | ۴۴۵ | **Figure 9-21-1** + caption; §9-21-6-1-7, §9-21-6-1-8 |
| 466 | ۴۴۶ | §9-21-6-2 (…), §9-21-6-2-3 region |

### 3.1 §9-21-6-1-5 — verbatim (PDF 464 / printed 444, read at 2.2×–3.6×)

> «۹-۲۱-۶-۱-۵ مهار دو انتهای خاموت متشکل از سیم جوش شده با تنها یک ساق، توسط دو
> سیم طولی با فاصلهی حداقل ۵۰ میلیمتر از یکدیگر، با تامین شرایط زیر مجاز است.
>
> الف- وجود حداقل یک سیم طولی داخلی، با فاصلهی بیشتر از یک چهارم عمق موثر و ۵۰
> میلیمتر از نصف عمق موثر مقطع، هر کدام بزرگتر است.
>
> ب- سیم طولی خارجی در وجه کششی باید از نزدیکترین میلگردهای طولی اصلی خمشی، به
> وجه کششی نزدیکتر باشد.»

### 3.2 §9-21-6-1-4 — verbatim (same page, the control clause)

> «۹-۲۱-۶-۱-۴ مهار هر یک از ساقهای شبکهی آرماتور سیمی جوش شدهی تشکیلدهندهی
> یک خاموت U شکل، باید منطبق بر **یکی از** شرایط زیر باشد **(شکل ۹-۲۱-۱)**.
>
> الف- وجود دو سیم طولی به فاصلهی ۵۰ میلیمتر از هم در طول عضو در قسمت فوقانی خاموت
> U شکل.
>
> ب- وجود یک سیم طولی واقع در فاصلهای کمتر از یک چهارم عمق موثر **از وجه فشاری**، و سیم
> طولی دوم نزدیکتر از سیم اول **به وجه فشاری** و به فاصلهای بیش از ۵۰ میلیمتر از سیم اول.
> قرارگیری سیم دوم روی ساق خاموت یا روی قلاب با حداقل قطر خم برابر با هشت برابر قطر خاموت
> مجاز است.»

### 3.3 §9-21-6-1-6 chapeau — verbatim (same page)

> «۹-۲۱-۶-۱-۶ خاموتهایی که به منظور پیچش یا یکپارچگی عضو بکار میروند، باید به صورت
> خاموت بسته و عمود بر امتداد طولی عضو باشند. …»

### 3.4 Figure 9-21-1 — PDF 465 / printed ۴۴۵

Caption, read verbatim:

> «شکل ۹-۲۱-۱ مهار در ناحیهی فشاری خاموت U شکل متشکل از شبکهی سیمی سادهی جوش شده»

(Figure 9-21-1 — *Anchorage in the compression zone of a U-shaped stirrup made of welded
plain wire mesh*.)

The figure contains **four panels** with these callouts, all read from the image:

| Panel | Callouts visible |
| :-- | :-- |
| top-left | leader label «۹-۲۱-۶-۱-۱»; dimension «۵۰ mm»; an unlabelled top-depth arrow («بند») |
| top-right | «۵۰ mm»; «حداکثر l/4» (maximum l/4) |
| bottom-left | «حداکثر l/4»; «حداقل قطر خم ۸ برابر قطر سیم» (minimum bend diameter 8× wire dia) |
| bottom-right | «حداکثر l/4» |

**No panel carries a «۹-۲۱-۶-۱-۵» label.** The only clause number printed inside the
figure is «۹-۲۱-۶-۱-۱» (on the top-left panel).

---

## 4. Visual verification record

| Item | PDF | Printed | Clause | Verified content | Figure/table ref | Paragraph boundaries |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| 1 | 464 | 444 | §9-21-6-1-4 | chapeau + الف + ب, complete | chapeau cites «(شکل ۹-۲۱-۱)» | chapeau ends at «زیر باشد»; الف/ب are separate paragraphs |
| 2 | 464 | 444 | §9-21-6-1-5 | chapeau + الف + ب, complete | **none** | chapeau is 2 lines ending «مجاز است.»; الف is 2 lines; ب is 2 lines, terminating «نزدیکتر باشد.» |
| 3 | 464 | 444 | §9-21-6-1-6 | chapeau + الف + ب, complete | references §9-21-6-1-3-الف/ب and §9-21-6-1-4 | separate clause block |
| 4 | 465 | 445 | Figure 9-21-1 | caption + 4 panels + callouts | self | — |

**Punctuation/conjunction notes that affect interpretation:**

- §9-21-6-1-5 chapeau: «… از یکدیگر، **با تامین شرایط زیر** مجاز است.» — the phrase is
  «با تامین شرایط زیر» ("by satisfying the conditions below"), **not** «با تامین یکی از
  شرایط زیر» ("by satisfying one of the conditions below").
- §9-21-6-1-5(الف): «… عمق موثر **و** ۵۰ میلیمتر از نصف عمق موثر مقطع، **هر کدام
  بزرگتر است**.» — the conjunction is «و» (and), and the closing idiom is
  «هر کدام بزرگتر است» (whichever is greater).
- §9-21-6-1-5(ب): «… به وجه کششی نزدیکتر باشد.» — a comparative with a terminal «باشد»
  (must be); no number, no distance, no measurement basis.
- §9-21-6-1-4 chapeau: «… **منطبق بر یکی از** شرایط زیر باشد (شکل ۹-۲۱-۱).»
- §9-21-6-1-4(ب): «… **از وجه فشاری**» and «… **به وجه فشاری**» — two explicit datums.

OCR was used only for navigation (locating clauses, running sweeps). Every wording above
was read from the page images.

---

## 5. §9-21-6-1-5 grammatical / datum analysis

### 5.1 Structural anatomy of the clause

```
§9-21-6-1-5
├── CHAPEau : «مهار دو انتهای خاموت متشکل از سیم جوش شده با تنها یک ساق،
│             توسط دو سیم طولی با فاصلهی حداقل ۵۰ میلیمتر از یکدیگر،
│             با تامین شرایط زیر مجاز است.»
│             → SCOPE: single-leg welded-wire tie, two longitudinal wires ≥50 mm apart
│             → GATE : «با تامین شرایط زیر» — CONJUNCTIVE
├── (الف)   : «وجود حداقل یک سیم طولی داخلی، با فاصلهی بیشتر از یک چهارم عمق
│             موثر و ۵۰ میلیمتر از نصف عمق موثر مقطع، هر کدام بزرگتر است.»
└── (ب)     : «سیم طولی خارجی در وجه کششی باید از نزدیکترین میلگردهای طولی اصلی
              خمشی، به وجه کششی نزدیکتر باشد.»
```

### 5.2 The questions, answered

| # | Question | Answer |
| :-- | :-- | :-- |
| 1 | Grammatical structure of branch (الف) | A single noun phrase — *existence of at least one internal longitudinal wire* — qualified by **one** prepositional phrase «با فاصلهی بیشتر از …» whose complement is a two-member series joined by «و»: «[یک چهارم عمق موثر] **و** [۵۰ میلیمتر از نصف عمق موثر مقطع]»، closed by the max idiom «هر کدام بزرگتر است» |
| 2 | What does the 50 mm condition modify? | *Grammatically* it is the second member of the max() series. *Semantically* it is **incomplete**: the printed string is «۵۰ میلیمتر **از** نصف عمق موثر مقطع» — "50 mm **from** half the effective depth of the section". But «از» is a from-preposition and here takes as its complement a **magnitude** («نصف عمق موثر» = d/2), not a physical face or centreline. Nothing in the clause states what this 50 mm is measured **to** or **from what physical reference** |
| 3 | Is the datum explicitly stated? | **NO.** The clause names exactly one geometric referent in this branch: «نصف عمق موثر مقطع». It never names a face (neither tension nor compression), a centreline, a tie bend, or a hook as a measurement reference |
| 4 | Grammatical continuation that resolves it? | **None.** The construction «[length A] و [50 mm از [magnitude B]]، هر کدام بزرگتر است» has no parallel elsewhere in the delivered window that would fix the missing term (see §5.3) |
| 5 | Internal references to compression face / tension face / section face / centreline / tie bend / hook? | The clause contains **«وجه کششی» (tension face) — but only in branch (ب)**, never in (الف). No compression face, no centreline, no tie-bend or hook datum appears in (الف) at all |
| 6 | Does Figure 9-21-1 apply to -1-5? | **NO** — see §7 |
| 7 | Does -1-5 cite Figure 9-21-1? | **NO** — see §7 |
| 8 | Does any cross-reference elsewhere in §9-21-6 resolve it? | **NO** — sweep of PDF 463–472 for every citation form of §9-21-6-1-5: **zero occurrences** |
| 9 | May the figure be used as an interpretive aid without an explicit cross-reference? | **NO — and doing so would be exactly the prohibited import.** See §8 |

### 5.3 The lexical evidence (this stage's new, decisive finding)

A sweep of the entire delivered window (PDF 442–472) shows how the document's own printed
vocabulary behaves:

| Printed term | Where it appears | Datum attached? |
| :-- | :-- | :-- |
| «عمق موثر» (effective depth) | printed 443 (§9-21-6-1-1), printed 444 (three times) | — (no definition clause in the window; no «عبارت است از» for it) |
| «یک چهارم عمق موثر» (quarter effective depth) | **exactly twice in the whole window**: §9-21-6-1-4(ب) and §9-21-6-1-5(الف) | §9-21-6-1-4(ب): **«از وجه فشاری» / «به وجه فشاری»** — explicit ✓ · §9-21-6-1-5(الف): **nothing** ✗ |
| «نصف عمق موثر» (half effective depth) | **exactly once**: §9-21-6-1-5(الف) | **nothing** ✗ |
| «هر کدام بزرگتر است» (whichever is greater) | **exactly twice**: §9-21-6-1-5(الف) and §9-21-6-2-4-1-الف | §9-21-6-2-4-1-الف: «حداقل ۱/۳۳ برابر اندازهی بزرگترین سنگدانه و ۲۵ میلیمتر…» — both members carry their own terms ✓ · §9-21-6-1-5(الف): the second member's reference is incomplete ✗ |

**Consequence.** The document *does* use explicit measurement datums when it intends
them — twice, in the immediately preceding clause, using the very same phrase «یک چهارم
عمق موثر». The omission in §9-21-6-1-5(الف) is therefore not a stylistic shorthand of the
code; it is a **gap in the clause text**, and the neighbouring clause's vocabulary
demonstrates that the drafter knew the term to attach. Selecting the datum by inference
would be precisely the "engineering convention as a substitute for missing code text"
that governance forbids.

**Two admissible readings remain, and they are not equivalent.** Semantically, «۵۰ mm
**from** d/2» can only mean that the 50 mm is measured from *the level located at half the
effective depth* (the section's mid-depth) — one endpoint of the measurement is clear. But
the **subject** of the check is not: the phrase "an internal longitudinal wire **at a
distance greater than** [¼d] **and** [50 mm from the mid-depth]" does not say *which
distance* the two values are compared against — the wire's distance from the **tension
face**, from the **compression face**, from the **mid-depth line**, a clear **spacing**
between wires, or an **embedment depth** over the U-tie. Because the clause supplies no
"distance from X" term, the **left-hand quantity of the comparison is undefined**, and with
it the entire "whichever is greater" test is undefined. Both a governing dimension and a
governing quantity are missing; neither may be supplied by the evaluator.

---

## 6. Branch (الف) analysis

| Aspect | Finding |
| :-- | :-- |
| Printed numbers | 50 mm (two occurrences: chapeau wire-to-wire spacing — complete and testable; and (الف)'s second max() member — incomplete) |
| Max() idiom | present and recognised («هر کدام بزرگتر است») |
| Governing quantity of the max() | **MISSING** — no "distance from ⟨reference⟩" term for the wire |
| Second member's reference | **MISSING** — «۵۰ mm از نصف عمق موثر» names a magnitude, not a physical datum |
| Representable in the engine? | `effective_depth_mm` exists (used by the sibling -1-4 evaluator). But **no input can express "the distance of the internal wire from ⟨unspecified datum⟩"**, because the required datum is not stated. A new input would have no source-defined meaning |
| Verdict | **AMBIGUOUS → BLOCKED.** Any evaluator would have to choose the datum; that choice is an unsupported assumption |

---

## 7. Branch (ب) analysis

**Verbatim (PDF 464, read at 3.4×):**

> «ب- سیم طولی خارجی در وجه کششی باید از نزدیکترین میلگردهای طولی اصلی خمشی، به
> وجه کششی نزدیکتر باشد.»

| Aspect | Finding |
| :-- | :-- |
| Is it quantitative? | **NO** — checked explicitly and independently this stage. No number, no distance, no ratio, no fraction appears anywhere in branch (ب). Its only numerals are in the *clause number* |
| Could OCR have obscured a quantity? | **No.** The branch was re-read at 3.4× on the page image; the text is complete across exactly two printed lines, terminating with «نزدیکتر باشد.» |
| Datum | It names two datums in the *comparison*: «در وجه کششی» (at the tension face) and «به وجه کششی» (to the tension face) — so this branch's geometry **is** sourced. What is absent is any **governing value** |
| Nature of the condition | **Genuinely relative/positional**: the outer longitudinal wire must be nearer the tension face than the nearest main flexural longitudinal bars. It is a strict inequality between two *provided* positions, with no threshold |
| Representable? | Yes in principle — the domain layer already validates `centroid_from_tension_face_mm` for bar groups (`domain/models.py`, `domain/validation.py`), and equivalently a wire's distance from the tension face could be supplied. This branch is a *comparison of two provided values*, not a numeric limit |
| Verdict | **Unambiguous as printed**, but **insufficient alone** — see §8 |

**H.17's branch-(ب) conclusion is confirmed correct**, and this stage strengthens it: the
branch is not merely "numberless", it is *legitimately* numberless (a positional rule),
and its geometry is fully sourced. It is (الف) that defects.

---

## 8. Figure 9-21-1 applicability analysis

| Question | Finding (visual, PDF 465) |
| :-- | :-- |
| What does Figure 9-21-1 illustrate? | «مهار در ناحیهی فشاری خاموت U شکل متشکل از شبکهی سیمی سادهی جوش شده» — anchorage **in the compression zone** of a U-shaped stirrup: four panels showing U-tie legs with longitudinal wires, callouts «۵۰ mm», «حداکثر l/4», «حداقل قطر خم ۸ برابر قطر سیم» |
| Is its geometry explicitly limited to -1-4? | **Indicatively yes.** §9-21-6-1-4's chapeau is the **only** place in the region that cites it: «… منطبق بر یکی از شرایط زیر باشد (شکل ۹-۲۱-۱)». The figure's «حداکثر l/4» callout corresponds to -1-4's «یک چهارم عمق موثر **از وجه فشاری**», and its «۸ برابر قطر سیم» callout corresponds verbatim to -1-4(ب)'s «قطر خم برابر با هشت برابر قطر خاموت» |
| Does §9-21-6-1-5 cite it? | **NO.** Its chapeau ends «… با تامین شرایط زیر مجاز است.» with no parenthetical and no figure reference. Sweep of PDF 463–472: the string «۹-۲۱-۱» (i.e. "9-21-1") occurs only inside §9-21-6-1-4's citation; §9-21-6-1-5 is never cited by anything in the window |
| Does any panel label -1-5? | **NO.** The only clause number printed inside the figure is «۹-۲۱-۶-۱-۱» (top-left panel). The figure additionally relates to §9-21-6-1-1, further confirming it is not drafted for -1-5 |
| May it be used as an interpretive aid anyway? | **NO — this is a source-governance question, and the answer is no.** Using it would require the engine (or this audit) to (i) transfer a figure attached to a **different clause** into -1-5, and (ii) read the missing datum out of a drawing whose callouts match -1-4's *compression-face* geometry — i.e. to import the -1-4 requirement. That is exactly the import the standing rules prohibit. It would also not be enough: even the figure's «۵۰ mm» callouts do not uniquely fix the missing "distance from X" term in -1-5(الف) |

---

## 9. §9-21-6-1-4 control comparison

| Aspect | §9-21-6-1-4 (control) | §9-21-6-1-5 (target) |
| :-- | :-- | :-- |
| Chapeau gate | «**منطبق بر یکی از** شرایط زیر باشد» — explicitly **disjunctive (OR)** | «**با تامین شرایط زیر** مجاز است» — no "یکی از"; **conjunctive (AND)** |
| Figure citation | **(شکل ۹-۲۱-۱)** ✓ | **none** |
| Explicit measurement datums | **two**: «از وجه فشاری», «به وجه فشاری» | **none** in (الف); tension face named only in (ب) |
| Geometry (ب) | quarter-depth wire from compression face + second wire closer to the compression face and >50 mm from the first; on leg or hook with bend ≥ 8× wire dia | outer wire nearer the tension face than the nearest main flexural bars |
| Governed by a figure | yes (self-cited) | no |
| Executable | **yes** — `BG-TRANS-WIRE-TIE-UTIE-001` (H.5) | **no** |

**Conclusion:** -1-4's geometry is explicitly scoped to -1-4 — by its own figure citation,
by its explicit datums, and by its disjunctive chapeau. **Nothing in the source permits
its geometry to be reused by -1-5, and adjacent subject matter is not a transferable
entitlement.** The two clauses are not merged, and no -1-4 requirement was carried across.

---

## 10. Engine input-model analysis

| Check | Finding |
| :-- | :-- |
| Rule entry | `BG-TRANS-WIRE-TIE-PENDING` — `VERIFY_PENDING`, `execution_allowed=False`, `dependencies=()`, printed 444 / PDF 464, description scoped to §9-21-6-1-5 only |
| Existing tie/hook evaluators | 21 executable §9-21-6 rules; the closest structural precedent is `evaluate_wire_tie_utie` (-1-4), which takes `wire_spacing_mm`, `wires_in_upper_part_of_utie`, `effective_depth_mm`, `wire1_dist_from_compression_mm`, `wire2_dist_from_compression_mm`, `wire1_to_wire2_spacing_mm`, `wire2_on_hook`, `bend_diameter_mm`, `tie_wire_diameter_mm` |
| Geometric inputs | `wire_spacing_mm` (chapeau 50 mm) and `effective_depth_mm` (d) exist and would cover the *comparable* quantities |
| Cover inputs | `BG-DETAIL-COVER-001` provides `provided_cover_mm` and a member/reinforcement classification — **not** a distance-from-face for an internal wire |
| Spacing inputs | available (clear spacing, c/c spacing) — but the clause does not request a spacing in (الف) |
| Distance-from-face inputs | the domain models `centroid_from_tension_face_mm` for **bar groups** (`domain/models.py` L29–36, validated in `domain/validation.py`); the same *kind* of quantity could be introduced for wires — but see the blocking row below |
| Can the current model express every source-required input **without a new unsupported assumption**? | **NO.** The required input for (الف) is "the distance of the internal longitudinal wire from **⟨datum⟩**" — and **the source never states ⟨datum⟩**. A new field would therefore have to carry a meaning the source does not define. Adding it would be inventing a requirement, not modelling one |
| New input needed? | **Yes, and it is not source-definable.** This is the C-type component of the decision: an `INPUT_MODEL_GAP` that is *caused by* the D-type source ambiguity and cannot be closed from the engine side |

---

## 11. Promotion gate results

| # | Condition | Result |
| :-- | :-- | :-- |
| 1 | Exact source wording visually verified | **PASS** — §9-21-6-1-5, -1-4, -1-6 and Figure 9-21-1 read at 2.2×–3.6×; footers ۴۴۴/۴۴۵ confirmed |
| 2 | Applicability unambiguous | **PASS** — single-leg welded-wire tie with two longitudinal wires ≥50 mm apart |
| 3 | **Branch (الف) datum unambiguous** | **FAIL** — the governing quantity of the max() comparison and the 50 mm reference are both absent from the print |
| 4 | Branch (ب) unambiguous | **PASS** — relative positional rule; both datums named; no number needed |
| 5 | Conjunctive/alternative logic resolved | **PASS** — conjunctive: «با تامین شرایط زیر مجاز است» (vs -1-4's «منطبق بر یکی از شرایط زیر باشد») |
| 6 | Every required input exists or is source-definable | **FAIL** — an input for "distance from ⟨unspecified datum⟩" is neither existing nor source-definable |
| 7 | No external standard required | **PASS** |
| 8 | No product-declared property required | **PASS** |
| 9 | No unsupported geometric assumption required | **FAIL** — the datum would have to be assumed (or imported from -1-4 / Figure 9-21-1) |
| 10 | Deterministic evaluator that cannot emit false PASS | **FAIL** — no evaluator can be written over undefined quantities |
| 11 | Every outcome traceable to the source clause | **FAIL** — a PASS would trace to an interpretation, not to the clause text |

**Gate result: 6 of 11 conditions FAIL or are unreachable ⇒ the rule must remain blocked.**

---

## 12. Final decision

**Outcome `D` — `REMAINS BLOCKED — SOURCE AMBIGUITY`** (with a **C-type** secondary:
`SOURCE–INPUT MODEL GAP`).

**`FULLY RESOLVED` is not reached.** The promotion gate cannot be satisfied, so under the
governing rule — *if ANY condition fails, KEEP THE RULE BLOCKED* — no evaluator was
written, `execution_allowed` was not changed, and no registry count moved. In particular,
**no partial evaluator was created**: because the chapeau is conjunctive, a rule
implementing only branch (ب) (or only the chapeau's 50 mm wire-to-wire spacing) could
return **PASS for a tie that satisfies neither (الف) nor (ب)** — a false PASS. That is
explicitly prohibited, and the standing sentinel is what guarantees it cannot happen.

### 12.1 What this stage resolved (and did not)

| | |
| :-- | :-- |
| **Resolved** | (i) The clause is **conjunctive**, proven by the printed chapeau contrast with -1-4's «یکی از». (ii) Branch (ب) is **not** numberless-by-defect — it is a positional rule with both datums named; its H.17 verdict is confirmed independently. (iii) Branch (الف)'s defect has been **localised to two missing terms**, and the document's own usage of the identical phrase «یک چهارم عمق موثر» in the immediately preceding clause (with explicit «از وجه فشاری») proves the omission is a text gap, not the code's intended shorthand. (iv) Figure 9-21-1 is cited only by -1-4, panels labelled only for -1-1, and may not be imported. (v) §9-21-6-1-5 is never cited anywhere in the window. |
| **Not resolved** | The **datum and the governed quantity** of branch (الف)'s max() comparison. Neither the clause text, nor any cross-reference, nor the figure supplies them. |
| **H.17 status** | **Upheld**, with a sharper and now source-demonstrated reason. |

---

## 13. Exact residual blocker

**Primary (D — source ambiguity).** §9-21-6-1-5(الف), as printed on p. 444, requires
«فاصلهی بیشتر از [یک چهارم عمق موثر] و [۵۰ میلیمتر از نصف عمق موثر مقطع]، هر کدام
بزرگتر است» while never stating (a) **from what reference the wire distance is measured**
(tension face? compression face? mid-depth? a spacing? an embedment depth?), nor (b) a
physical referent for the **50 mm** term, whose complement «نصف عمق موثر مقطع» is a
magnitude rather than a datum. Without (a) the left-hand side of the "whichever is
greater" comparison is undefined; without (b) the right-hand member is undefined. The
clause offers no cross-reference, and the document nowhere else resolves the construction.

**Secondary (C — input-model gap, caused by the primary).** No engine input expresses
"distance of the internal longitudinal wire from ⟨datum⟩", and none can be added with a
source-defined meaning while the datum is unstated.

**What would unlock it (nothing less suffices):**

1. An edition, erratum, corrigendum or authoritative annex of Mabhas 9 in which
   §9-21-6-1-5(الف) states the measurement datum and the governed quantity explicitly; **or**
2. an official clarification from the code owner (or the standard's drafting body) that
   fixes the datum; **or**
3. an explicit, recorded project-level decision that this clause is outside the engine's
   remit.
   Adjacency to -1-4, similarity of subject matter, the figure's callouts, and engineering
   convention are **not** admissible substitutes, and Mostofinejad (non-governing
   reference material) cannot resolve a Mabhas 9 ambiguity.

---

## 14. Files changed

| File | Change |
| :-- | :-- |
| `docs/PHASE2F_STAGE_H19_WIRE_TIE_AUDIT.md` | **this record (new)** |
| — | **Nothing else** — no registry, evaluator, test, catalog or other documentation value was modified |

A behaviour-neutral refresh of B's `blocked_reason` text (which currently describes the
wording as ambiguous without recording the *lexical* proof, the conjunctive-gate finding
or the figure-scope analysis) remains **recommended and deliberately deferred**; it is not
required to reach this stage's conclusion and would not change any status.

---

## 15. Tests / gates

| Gate | Result |
| :-- | :-- |
| `PYTHONPATH=src pytest` | **673 passed** |
| `PYTHONPATH=src mypy --strict` | **clean — 23 source files** |
| Registry | **121 total / 63 executable / 48 blocked / 10 reference** — unchanged |
| Duplicate Rule IDs | **0** |
| §9-21-6 | **21 executable / 5 blocked** — unchanged |
| `BG-TRANS-WIRE-TIE-PENDING` | `VERIFY_PENDING`, `execution_allowed=False`, `dependencies=()` — unchanged |
| `git diff --check` | **clean** |
| ISIRI 11558 PDF SHA-256 | `4c1c1a478ab8a39b6a19cabc63eac63afbaf2f31c4a7c3eaf55549c9d039916c` — unchanged |

**Deltas: none.** No count changed anywhere.

---

## 16. Commit SHA

**Baseline at stage start: `940490d`** (H.18).

This stage's commit — the one introducing this file — is recorded in the follow-up
one-line commit below it. The SHA is backfilled in a second, content-only commit (never
by amending or rewriting history) so that the value printed here is a **true, verifiable
hash** rather than a placeholder. No history rewrite, no rebase, no force-push was used;
both commits are ordinary fast-forward commits on `arena/b9cd291a-beamgenius`.

---

## 17. Confirmation — `origin/main`

`origin/main` remains at **`df8067a750ffc7984c9dc5d80220ad9013503aa6`**, unmodified. It was
read only (`git ls-tree`, `git show` to the git-ignored `working/h19/`). No reset, rebase,
force-push, history rewrite or branch switch was performed. All work is on
`arena/b9cd291a-beamgenius`.

---

```
DECISION:            REMAINS BLOCKED — SOURCE AMBIGUITY (outcome D; C-type secondary)
RULE:                BG-TRANS-WIRE-TIE-PENDING
STATUS:              VERIFY_PENDING
EXECUTION_ALLOWED:   False
CLASSIFICATION:      SOURCE_AMBIGUITY (primary) + INPUT_MODEL_GAP (secondary)
PRIMARY BLOCKER:     §9-21-6-1-5(الف) — the measurement datum of the wire distance
                     and the physical referent of the "50 mm from half the effective
                     depth" term are both absent from the printed clause; the
                     "whichever is greater" comparison therefore has an undefined
                     left-hand quantity and an undefined right-hand member.
IMPLEMENTATION:      NOT PERFORMED — promotion gate failed (6 of 11 conditions).
                     No partial evaluator created (the chapeau is conjunctive, so a
                     partial rule could emit a false PASS).
REGISTRY DELTA:      none (121 / 63 / 48 / 10; §9-21-6 still 21 exec / 5 blocked)
TEST RESULT:         673 passed
MYPY RESULT:         Success: no issues found in 23 source files
ORIGIN/MAIN:         df8067a750ffc7984c9dc5d80220ad9013503aa6 — untouched
```
