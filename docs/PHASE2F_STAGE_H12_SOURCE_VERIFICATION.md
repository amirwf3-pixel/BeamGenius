# Phase 2F — Stage H.12: Source Verification of the Remaining Transverse-Reinforcement Blockers

**Status: DOCUMENTATION / SOURCE-VERIFICATION ONLY — no rule is implemented or promoted in H.12.**

H.12 was scoped as source verification of A–E against the complete Mabhas 9 PDF said
to have been supplied to this task environment
(`Mabhas9-v5.0-1399-ATNasr.ir.pdf`). This document records **what was actually
possible**, including a blocking environmental finding that must be resolved before
A–E can be settled on full-book evidence. No access is claimed that was not
demonstrated, and no source page is cited that could not be inspected.

Baselines read first and treated as authoritative (not overwritten or
reinterpreted): `docs/PHASE2F_STAGE_H10_PLAN.md`,
`docs/PHASE2F_STAGE_H11_SOURCE_ACQUISITION.md`,
`docs/PHASE2F_STAGE_H9_REMAINING_BLOCKER_AUDIT.md`.

---

## 0. Environment finding — the supplied PDF is NOT present in this environment

This section is placed first because every downstream target depends on it and
because it must not be buried.

### 0.1 Result

| Item | Finding |
| :-- | :-- |
| Is `Mabhas9-v5.0-1399-ATNasr.ir.pdf` present in the task environment? | **NO** |
| Was any PDF found anywhere on the accessible filesystem? | **NO — zero results** |
| Was the full-book source readable? | **NO** |
| Could the PDF identity/version be confirmed? | **NO** — `Mabhas 9 / 1399 / v5.0 / 5th edition` could **not** be confirmed from a file, because no file exists to confirm it from |
| Could PDF page numbers be mapped to printed page numbers from the supplied book? | **NO** — mapping remains valid only for the committed evidence window (canonical offset **PDF = printed + 20**, verified for pages 442–472) |

### 0.2 Exact checks performed (all negative)

| Check | Method | Result |
| :-- | :-- | :-- |
| Filename search | `find / -iname "*Mabhas*" -o -iname "*مبحث*" -o -iname "*.pdf"` | **0 matches** |
| Version/fragment search | `find / -iname "*v5.0*" -o -iname "*ATNasr*" -o -iname "*1399*"` | Only incidental system hits: a git object **hash** containing the digits `1399` and `/usr/lib/.../gconv/IBM1399.so` (an iconv module). **No document.** |
| Extension sweep | `find / -xdev -iname "*.pdf" -o -iname "*.djvu" -o -iname "*.epub"` | **0 matches** |
| Large-file sweep | `find / -xdev -type f -size +200k` (excluding system directories) | Only systemd journal logs and `dpkg.status` — **no book file** |
| Common delivery locations | `/code`, `/mnt`, `/media`, `/srv`, `/tmp/arena-workspace`, `/home/user` | **All empty** except `/home/user/BeamGenius` (the repository) |
| Repository blobs | `git rev-list --objects --all \| git cat-file --batch-check` filtered to blobs > 100 KB | **All such blobs are the 31 committed evidence JPGs** of `phase2f-source-442-472/` (largest: `page-464.jpg`, 485,079 B). **No PDF blob.** Total objects across all refs: 241 |
| All refs | `git for-each-ref` | Only `main` (`df8067a`) and `arena/b9cd291a-beamgenius` (`b261c8c`) — **no branch, tag or ref delivers a book file** |
| Recent-file sweep | `find / -type f -mmin -360` (excluding repo/system) | No delivered document |

The sandbox is healthy (`ENV_ID` present, **20 GB free** on `/`), so this is not a
disk-space or capacity failure. **No attachment or upload of the PDF reached this
session.**

### 0.3 Consequence — and what is NOT claimed

Because the full book is absent, this stage **cannot**:

- confirm the edition/version of a supplied copy (there is none to inspect);
- re-verify §9-21-6 pages against a full-book copy;
- reach **§9-4-8** (NBC Chapter 9-4) or **NBC Chapter 10**, which are outside the
  committed window and exist in no other accessible form.

**What is claimed:** the committed evidence at `df8067a:phase2f-source-442-472/`
remains the only authoritative visual source available, and it was re-verified
intact this stage (62 files; pages 442–472; the pages this stage depends on were
spot-checked: `page-463` 436,074 B, `page-464` 485,079 B, `page-465` 347,867 B).

To proceed, the document must actually reach this environment — for example by
committing it to the repository, exposing it as a fetchable public link, or
attaching it to the session. Until then, D and E cannot be source-verified **at
all**, and A and B can only be re-examined within the committed window.

---

## 1. Scope of verification actually performed in H.12

Within the committed window, H.12 performed **new** verification work on the two
clauses that are fully inside it and that carry the unresolved questions:

| Clause | Page (PDF / printed) | Work performed |
| :-- | :-- | :-- |
| §9-21-6-1-3-ب | 463 / 443 | Re-read the branch in full context; re-read the formula line; re-checked page boundaries and the absence of a continuation |
| §9-21-6-1-5, §9-21-6-1-4 (as the same-page comparison), Figure 9-21-1 | 464 / 444, 465 / 445 | Re-read both clauses' preambles and sub-clauses verbatim; verified what each clause does and does not name; re-checked the figure's caption and ownership |

Nothing was implemented, and no blocked state was changed.

---

## 2. Target A — `BG-TRANS-TIE-ANCHOR-PENDING`, §9-21-6-1-3-ب

| Field | Record |
| :-- | :-- |
| Previous state (H.10/H.9) | `KEEP_BLOCKED` |
| Exact source location | §9-21-6-1-3-ب, PDF page **463** / printed page **443** (footer ۴۴۳) — committed evidence |
| Visually verified wording | «ب- در میلگردهای به قطر ۱۸ تا ۲۵ میلی‌متر و تنش تسلیم بیش از ۲۸۰ مگاپاسکال، وجود قلاب استاندارد پیرامون میلگرد طولی به علاوه‌ی طول مدفون بین وسط ارتفاع مقطع و انتهای … و بیرونی قلاب بیشتر یا مساوی ۰.۱۷f_y/(λ√f_c)·d_b» |
| Relevant formula / requirement | Standard hook around the longitudinal bar **plus** an embedment length **plus** a minimum bend requirement: outer aspect of the hook ≥ `0.17·f_y/(λ·√f′c)·d_b`, for `d_b` 18–25 mm and `f_y` > 280 MPa |
| Resolved ambiguity this stage | **NONE.** Two structural facts were re-confirmed at high magnification rather than resolved: (i) the embedment phrase terminates at «انتهای» and the next printed element is the formula line — the clause is **complete on page 463**, and page 464 opens a new numbered clause (§9-21-6-1-4), so nothing was lost to a page break; (ii) line 3 begins at the right margin with «بیرونی» — **no preceding noun exists** on that line or the preceding one, so the compared quantity is genuinely unnamed in print |
| Remaining ambiguity | **(1) λ applicability** — λ is printed, but its only definition in the window is §9-21-3-1-6, scoped by its own wording to «در محاسبه طول گیرایی»; §9-21-6 cites §9-21-3 nowhere. **(2) Embedment-end datum** — the referent after «انتهای» is absent. **(3) Outer-hook quantity** — the noun is absent and no measurement datum is given |
| Dependency | None registered. Would require an explicit λ rule for this clause |
| Implementation decision | **`KEEP_BLOCKED` — no implementation** |
| Rule ID | **None** |
| Tests added | None |
| Final status | **`KEEP_BLOCKED`, unchanged.** Nothing was imported from §9-21-3, no datum was invented, and no noun was inferred from engineering convention |

Boundary gaps carried forward verbatim (never interpolated): `f_y` = 280 MPa
exactly, `d_b` = 17 mm, `d_b` > 25 mm.

---

## 3. Target B — `BG-TRANS-WIRE-TIE-PENDING`, §9-21-6-1-5

| Field | Record |
| :-- | :-- |
| Previous state (H.10) | `SOURCE_WORK_REQUIRED` |
| Exact source location | §9-21-6-1-5, PDF page **464** / printed page **444** (footer ۴۴۴) — committed evidence |
| Visually verified wording | Preamble: «۹-۲۱-۶-۱-۵ مهار دو انتهای خاموت متشکل از سیم جوش شده با تنها یک ساق، توسط دو سیم طولی با فاصله‌ی حداقل ۵۰ میلی‌متر از یک‌دیگر، با تامین شرایط زیر مجاز است.» — الف: «وجود حداقل یک سیم طولی داخلی، با فاصله‌ی بیش‌تر از یک چهارم عمق موثر و ۵۰ میلی‌متر از نصف عمق موثر مقطع، هر کدام بزرگ‌تر است.» — ب: «سیم طولی خارجی در وجه کششی باید از نزدیک‌ترین میلگردهای طولی اصلی خمشی، به وجه کششی نزدیک‌تر باشد.» |
| Relevant formula / requirement | Single-leg welded-wire tie end anchorage via two longitudinal wires ≥ 50 mm apart, subject to (الف) an internal longitudinal wire at a distance greater than "one quarter of the effective depth **and** 50 mm from half the effective depth of the section, whichever is greater", and (ب) the outer longitudinal wire on the tension face being closer to the tension face than the nearest main flexural longitudinal bars |

### 3.1 What the clause DOES determine (verified this stage)

| Question posed by H.12 | Finding |
| :-- | :-- |
| What does `d` mean in this clause? | **Stated:** «عمق موثر» = **effective depth** (both terms of (الف) use «عمق موثر»). No definition of the effective depth is given *in this clause*, but the term is the clause's own wording and is used consistently |
| What is the 50 mm comparison relative to (preamble)? | **Stated:** «فاصله‌ی حداقل ۵۰ میلی‌متر از یک‌دیگر» — the minimum **spacing between the two longitudinal wires** |
| Which wires are being positioned? | **Stated:** (الف) «حداقل یک سیم طولی **داخلی**» (at least one **internal** longitudinal wire); (ب) «سیم طولی **خارجی** در وجه کششی» (the **outer** longitudinal wire **on the tension face**) |
| Is the (ب) comparison operationally testable? | **Yes, given explicit inputs** — it is a two-value comparison: distance of the outer wire from the tension face **<** distance of the nearest main flexural longitudinal bar from the tension face. No interpretation is required if both caller-measured values are supplied |

### 3.2 What the clause does NOT determine (the blocking ambiguity)

**The (الف) measure datum.** «با فاصله‌ی بیش‌تر از یک چهارم عمق موثر و ۵۰ میلی‌متر
از نصف عمق موثر مقطع، هر کدام بزرگ‌تر است.»

The source does not state from which line the distance is measured for the
**one-quarter effective depth** term, and it does not state the measurement
*datum or direction* for the **50 mm from half the effective depth** term. More than
one materially different reading is admissible against this wording, and they
produce different engineering outcomes. For example (recorded as admissible
readings — **not** as an interpretation adopted by this stage):

- **Reading R1** — both terms share an (elided) datum at a face; the internal wire
  must be more than `max(d_eff/4, 50 mm)` from that face.
- **Reading R2** — the datum is the mid-depth line «نصف عمق موثر مقطع»; the wire
  must be more than `max(d_eff/4, 50 mm)` from the **mid-depth line**.

The clause text selects neither. **H.12 does not choose between them.**

**Decisive same-page comparison (new this stage).** The adjacent clause
§9-21-6-1-4, on the **same printed page**, governs the same quantity class and
demonstrably names what §9-21-6-1-5 omits:

| Element | §9-21-6-1-4 (PDF 464) | §9-21-6-1-5 (PDF 464) |
| :-- | :-- | :-- |
| Location of the wires | **Named:** «در طول عضو در **قسمت فوقانی** خاموت U شکل» (*in the upper part of the U-stirrup*) — verified at 4.5× | **Not named** |
| Datum for the ¼·d_eff term | **Named:** «کم‌تر از یک چهارم عمق موثر **از وجه فشاری**» (*from the compression face*) — verified at 5× | **Not named** |

Because the same document writes the datum and the location when it means them,
the omission in §9-21-6-1-5 is a **genuine omission in print**, not a reading
artifact. Importing §9-21-6-1-4's datum into §9-21-6-1-5 is reading a requirement
out of a *different* clause and is not permitted — and H.12 did not do it.

**Figure check (re-confirmed).** §9-21-6-1-5 cites no figure. Figure 9-21-1
(PDF 465) is captioned «شکل ۹-۲۱-۱ مهار در ناحیه‌ی **فشاری** خاموت U شکل متشکل از
شبکه‌ی سیمی ساده‌ای جوش شده» — a **compression-zone** figure belonging to the
§9-21-6-1-4 provisions (whose preamble is the clause that cites it). It cannot
supply a datum for the tension-face clause §9-21-6-1-5.

### 3.3 Why no partial implementation was made

The clause is **conjunctive**: «با تامین شرایط **زیر** مجاز است» requires the
conditions that follow. Sub-clause (ب) alone is deterministic given explicit
inputs, but implementing (ب) while (الف) is unresolved would let the engine return
**PASS on a half-evaluated requirement** — a false PASS on a composite clause. The
governance rule "BLOCKED never becomes PASS" forbids it, and the H.12 objective
explicitly rejects adding rules to reduce the blocked count. **No partial rule was
implemented and no new sentinel was created.**

| Field | Record |
| :-- | :-- |
| Resolved ambiguity | Preamble spacing, wire roles, and the meaning of `d` (effective depth) — **these are now precisely recorded** |
| Remaining ambiguity | The (الف) measure datum/direction (two admissible readings, source selects neither) |
| Dependency | None registered |
| Implementation decision | **`SOURCE_WORK_REQUIRED` — no implementation** |
| Rule ID | **None proposed** (no promotable rule exists) |
| Tests added | None |
| Final status | **`SOURCE_WORK_REQUIRED`, unchanged** — now with a formally enumerated, reproducible reason |

---

## 4. Target C — `BG-TRANS-TORSION-TIE-PENDING` (remaining route)

| Field | Record |
| :-- | :-- |
| Previous state (H.10) | `KEEP_BLOCKED` (transitive on A) |
| Exact source location | §9-21-6-1-6-ب (PDF **464** / printed **444**) and §9-21-6-2-7-ب (PDF **468** / printed **448**) — committed evidence |
| Visually verified wording | Both clauses offer the same OR alternatives: «الزامات ۹-۲۱-۶-۱-۳-الف یا ب، و یا ۹-۲۱-۶-۱-۴ تامین نمود» / «…الف یا ب، یا ۹-۲۱-۶-۱-۴ تامین گردد» |
| Relevant requirement | The (ب) anchorage obligation is discharged by (§9-21-6-1-3-الف **or** §9-21-6-1-3-ب) **or** §9-21-6-1-4 |
| Resolved ambiguity | None required — C contains no source question of its own |
| Remaining ambiguity | The **only** unimplemented OR route is §9-21-6-1-3-ب, i.e. blocker A |
| Dependency | **A** (pure transitive dependency) |
| Implementation decision | **`KEEP_BLOCKED` — no implementation.** Per the H.12 scope, C is revisited only if A becomes deterministically executable |
| Rule ID | **None** |
| Tests added | None |
| Final status | **`KEEP_BLOCKED`, unchanged** |

**No duplication or regression.** The four executable torsion routes were verified
untouched and still executable with unchanged registered dependencies:
`BG-TRANS-TORSION-TIE-135HOOK-001` (no deps),
`BG-TRANS-TORSION-TIE-SEISMIC-HOOK-001` (→ `BG-TRANS-SEISMIC-HOOK-001`),
`BG-TRANS-TORSION-TIE-STANDARD-HOOK-001` (→ `BG-TRANS-STANDARD-HOOK-001`),
`BG-TRANS-TORSION-TIE-WIRE-ROUTE-001` (→ `BG-TRANS-WIRE-TIE-UTIE-001`).

---

## 5. Target D — `BG-TRANS-WIRE-SUBST-PENDING`, §9-21-6-2-3 → §9-4-8

| Field | Record |
| :-- | :-- |
| Previous state (H.10/H.11) | `EXTERNAL_DEPENDENCY` |
| Exact source location of the rule | §9-21-6-2-3, PDF page **466** / printed page **446** — committed evidence |
| Visually verified wording | «۹-۲۱-۶-۲-۳ استفاده از سیم آجدار یا شبکه‌ی آرماتور سیم جوش شده به عنوان جایگزین تنگ آجدار، با سطح مقطع معادل میلگرد آجدار در نظر گرفتن الزامات ۹-۲۱-۶-۲-۱ و ۹-۴-۸ مجاز است.» |
| Relevant requirement | A deformed wire or welded-wire mesh may substitute for a deformed tie with **equivalent cross-sectional area**, subject to **§9-21-6-2-1** and **§9-4-8** |
| Dependency status | **§9-21-6-2-1** — verified + executable (`BG-TRANS-TIE-SPACING-001`, PDF 466 / printed 446). **§9-4-8** — **still NOT available**: it lies in NBC Chapter 9-4, outside the committed window (442–472), and the full book that was to supply it **is not present in this environment** (§0) |
| Resolved ambiguity | The rule's own scope ("equivalent cross-sectional area") is deterministic and already verified |
| Remaining ambiguity | **The content of §9-4-8 is unknown.** Nothing is known about which welded-wire properties it imposes (material properties, geometry, detailing or certification) because the clause has never been read. H.12 therefore **cannot** determine the minimum dependency surface, and **did not guess it** |
| Dependency | §9-4-8 (NBC Chapter 9-4) — **unavailable** |
| Implementation decision | **`EXTERNAL_DEPENDENCY` — no implementation** |
| Rule ID | **None** |
| Tests added | None |
| Final status | **`EXTERNAL_DEPENDENCY`, unchanged** — blocked strictly on source unavailability, not on engineering difficulty |

No fake default was created for the substitution, and nothing was substituted from
another code.

---

## 6. Target E — `BG-TRANS-SPIRAL-SPLICE-SEL-PENDING`, §9-21-6-3-5-الف → §9-21-4-7 → NBC Chapter 10

| Field | Record |
| :-- | :-- |
| Previous state (H.10/H.11) | `EXTERNAL_DEPENDENCY` |
| Exact source location of the rule | §9-21-6-3-5-الف, PDF page **468** / printed page **448** — committed evidence |
| Visually verified wording | «۹-۲۱-۶-۳-۵ وصله‌ی دورپیچ‌ها با یکی از روش‌های زیر انجام می‌شود — الف- وصله‌ی جوشی یا مکانیکی مطابق بند ۹-۲۱-۴-۷.» |
| Relevant requirement | The welded/mechanical spiral-splice route is a **pure delegation** to Clause §9-21-4-7; the lap route (ب) is already executable as `BG-TRANS-SPIRAL-SPLICE-LAP-SEL-001` and is untouched |
| Dependency status | **§9-21-4-7** is inside the committed window (PDF 460–461 / printed 440–441) and its sub-clauses -7-1…-7-8 were read in H.10. It remains non-executable as `BG-DEV-SPLICE-WELDED-MECH-PENDING` (`VERIFY_PENDING`, `execution_allowed=False`). Its blocking cause **§9-21-4-7-3** requires «الزامات مبحث دهم مقررات ملی ساختمان» = **NBC Chapter 10**, whose pages are (i) outside the committed window and (ii) **absent from this environment** (§0) |
| Resolved ambiguity | None available to resolve. The delegation's determinism is exactly the determinism of §9-21-4-7 |
| Remaining ambiguity | **The content of the Chapter 10 welding provisions is unknown** — nothing is known about what eligibility they impose, so the minimum dependency surface cannot be determined and was not guessed |
| Dependency | **NBC Chapter 10** — **unavailable**; and §9-21-4-7 would additionally require its own, separately gated promotion |
| Implementation decision | **`EXTERNAL_DEPENDENCY` — no implementation.** Per the H.12 scope, welded/mechanical splice engineering was not implemented merely because some source text exists |
| Rule ID | **None** |
| Tests added | None |
| Final status | **`EXTERNAL_DEPENDENCY`, unchanged** |

**Coefficient preservation.** The verified `1.25` strength-transfer coefficient of
§9-21-4-7-6 («۱/۲۵») recorded in H.10 is **unaltered**, as required. It was not
re-inspected against a full-book copy this stage (no copy available), and no
evidence contradicts the committed-window read.

---

## 7. Summary of A–E

| Blocker | Clause | PDF p. / printed p. | Previous state | H.12 decision | Rule ID | Tests |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| **A** `BG-TRANS-TIE-ANCHOR-PENDING` | §9-21-6-1-3-ب | 463 / 443 | `KEEP_BLOCKED` | **`KEEP_BLOCKED`** | — | — |
| **B** `BG-TRANS-WIRE-TIE-PENDING` | §9-21-6-1-5 | 464 / 444 | `SOURCE_WORK_REQUIRED` | **`SOURCE_WORK_REQUIRED`** | — | — |
| **C** `BG-TRANS-TORSION-TIE-PENDING` | §9-21-6-1-6-ب & §9-21-6-2-7-ب | 464, 468 / 444, 448 | `KEEP_BLOCKED` | **`KEEP_BLOCKED`** (via A) | — | — |
| **D** `BG-TRANS-WIRE-SUBST-PENDING` | §9-21-6-2-3 → §9-4-8 | 466 / 446 | `EXTERNAL_DEPENDENCY` | **`EXTERNAL_DEPENDENCY`** | — | — |
| **E** `BG-TRANS-SPIRAL-SPLICE-SEL-PENDING` | §9-21-6-3-5-الف → §9-21-4-7 → Ch. 10 | 468 / 448 | `EXTERNAL_DEPENDENCY` | **`EXTERNAL_DEPENDENCY`** | — | — |

**Rules implemented in H.12: NONE.** The registry is unchanged.

---

## 8. Scope-control statement

H.12 remained limited to the five identified blocker families — the §9-21-6 tie
anchor (A), welded-wire tie positioning (B), torsion-tie remaining route (C),
welded-wire substitution (D), and spiral-splice selection (E) — plus the source
availability investigation that those targets depend on.

Specifically, H.12 did **not**:

- continue or extend the Google Drive investigation beyond the single environmental
  presence check required to establish whether the supplied source was reachable;
- redesign the engine, its calculation architecture, or its source hierarchy;
- introduce AI into any calculation path;
- import any reference PDF at runtime, or add any runtime file/PDF/OCR read;
- add speculative engineering formulas, speculative defaults, or invented inputs;
- broaden scope to unrelated Chapter 9 provisions, to Chapter 9-4 or Chapter 10
  content beyond the specific dependency questions asked;
- start UI, report-generation, DXF, or optimisation work;
- modify `origin/main`, the historical source evidence, or any historical audit
  document (H.9, H.10, H.11 were read only);
- alter the four already-executable torsion routes or any other executable rule;
- reduce the blocked-rule count by assumption.

**No unsupported engineering assumption was introduced anywhere in H.12.** Where
the source was silent, H.12 recorded the silence; where the source was
unavailable, H.12 recorded the unavailability.

---

## 9. Validation

| Gate | Result |
| :-- | :-- |
| `PYTHONPATH=src pytest` | **673 passed** (unchanged) |
| `PYTHONPATH=src mypy --strict` | **clean, 23 source files** |
| Registry | **121 total / 63 executable / 48 blocked / 10 reference-executable** (unchanged) |
| §9-21-6 (clause-prefix predicate) | **21 executable / 5 blocked** (unchanged) |
| Engine AST / import governance | unchanged — no new module, no reference-package import, no runtime file read |
| Executable-rule behaviour | unchanged — no evaluator, formula, constant, registry entry or test touched |
| Historical source evidence | unmodified; `phase2f-source-442-472/` re-verified intact |
| `origin/main` | `df8067a`, unmodified |
| Files changed by H.12 | `docs/PHASE2F_STAGE_H12_SOURCE_VERIFICATION.md` **only** |

---

## 10. What must happen next (actionable)

1. **Deliver the book file.** H.12 could not verify a document that is not present.
   Any of these would make the full-book verification possible: committing the PDF
   to the repository, exposing it as a fetchable public link, or attaching it to
   the session. Once present, the H.11 §3.4 readability test (open → identify page
   numbers → distinguish printed from PDF page numbers → compare the known page
   §9-21-6-1-3-ب at printed 443 / PDF 463 against the committed evidence) should be
   run **before** any engineering decision is taken from it.
2. **§9-4-8 pages** — required to settle D; and **NBC Chapter 10 pages** — required
   to settle E's dependency chain. Both are outside the committed window; neither
   is reachable today.
3. **A and B** — both are blocked on *text-level* elisions inside pages that are
   already available. A full-book copy can **confirm** but cannot by itself repair
   an elision in print; only the source itself (or an authorised interpretation)
   can resolve them. Neither was forced.

---

*H.12 is source verification only; no rule is implemented or promoted in H.12, and no source access is claimed that was not demonstrated.*
