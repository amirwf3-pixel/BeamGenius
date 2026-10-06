# Phase 2F — Stage H.13: Mabhas 9 §9-4-8 Source-Evidence Verification

**Status: SOURCE-VERIFICATION ONLY — no rule is implemented or promoted in H.13.**

H.13 was scoped to resolve blocker **D** (`BG-TRANS-WIRE-SUBST-PENDING`) from the
supplied evidence file `BeamGenIus-H13-Mabhas9-9-4-8-evidence.pdf`, announced as
original Mabhas 9 pages PDF 86–89 / printed 66–69 covering §9-4-7 and §9-4-8.

**Outcome in one line:** the announced evidence file **never arrived** in this
environment, so §9-4-8 could **not** be inspected; **D stays blocked**. What *was*
achieved is a complete, controlled visual re-read of the committing clause
§9-21-6-2-3 from committed evidence, which **resolves a long-standing citation
discrepancy** and **pins the D dependency surface to exactly one clause**.

Baselines read first and treated as authoritative (not rewritten):
`docs/PHASE2F_STAGE_H10_PLAN.md`,
`docs/PHASE2F_STAGE_H11_SOURCE_ACQUISITION.md`,
`docs/PHASE2F_STAGE_H12_SOURCE_VERIFICATION.md`.

---

## 0. Blocking finding — the supplied evidence file is NOT present in this environment

### 0.1 Result

| Item | Finding |
| :-- | :-- |
| Is `BeamGenIus-H13-Mabhas9-9-4-8-evidence.pdf` present? | **NO** |
| Is `/home/user/uploads/` present? | **NO** — the announced directory does not exist |
| Direct attempt to open the announced path | **FAILED** — "File not found" |
| Was **any** PDF found anywhere on the accessible filesystem? | **NO — zero results** |
| Could §9-4-7 or §9-4-8 content be read? | **NO** |
| Could the edition/version of the supplied extract be confirmed from a file? | **NO — there is no file to inspect** |

### 0.2 Exact checks performed (all negative)

| Check | Method | Result |
| :-- | :-- | :-- |
| Filename search | `find / -iname "*H13*" -o -iname "*9-4-8-evidence*" -o -iname "*BeamGenIus*"` | Only the repository's own paths |
| PDF extension sweep | `find / -xdev -iname "*.pdf"` | **0 matches** |
| Content (magic-byte) sweep | Every file under `/home/user`, `/tmp`, `/code`, `/srv`, `/mnt`, `/media`, `/var/tmp` tested for leading bytes `%PDF` | **0 matches** |
| Common delivery paths | `/home/user/uploads`, `/tmp/arena-workspace`, `/code`, `/srv`, `/mnt`, `/media` | **All empty / non-existent** |
| Delayed-arrival re-check | Uploads check + full magic-byte sweep repeated after a 20 s wait | **Still absent** |
| Git object sweep | `git rev-list --objects --all` filtered for `9-4-8` / `h13` / `*pdf` | **0 matches** |

The accessible environment contains **no PDF of any kind**. For contrast, the
committed evidence set was re-verified intact this stage
(`phase2f-source-442-472/`, pages 442–472), so this is a source-delivery gap, not a
reading-capability limit.

### 0.3 The announced page mapping is at least internally consistent

Testing the announced metadata against the project's established page-mapping rule
(verified offset **PDF = printed + 20**, e.g. §9-21-6-1-3 printed 443 = PDF 463):

| Announced PDF page | Announced printed page | PDF − printed |
| :-- | :-- | :-- |
| 86 | 66 | 20 ✓ |
| 87 | 67 | 20 ✓ |
| 88 | 68 | 20 ✓ |
| 89 | 69 | 20 ✓ |

Consistent — which supports the plausibility of the announced extraction and
nothing more. A consistent page number is **not** evidence of clause content, and
H.13 treats it as such.

### 0.4 Consequence

H.13 could **not** perform Target 1 (§9-4-8 clause-by-clause findings), and could
not complete Target 2's comparison against §9-4-8. No guessed content was
substituted. Sections 1–2 record the absence precisely; Section 3 records the
substantial verification work that **was** possible on committed evidence.

---

## 1. Evidence identity

| Field | Record |
| :-- | :-- |
| Source filename (announced) | `BeamGenIus-H13-Mabhas9-9-4-8-evidence.pdf` |
| Announced content | Extracted original Mabhas 9 pages: PDF 86–89 / printed 66–69 |
| Announced coverage | §9-4-7 and §9-4-8 |
| **Actual availability in this environment** | **ABSENT — not readable (see §0)** |
| Edition/version confirmation | **NOT POSSIBLE** — no file to inspect |
| Relationship to the original Mabhas 9 source | **NOT VERIFIABLE** — no file |
| Governing source actually used | The committed evidence `df8067a:phase2f-source-442-472/` (pages 442–472 only) |

**Evidence added to the repository by H.13: NONE.** No §9-4-8 or §9-4-7 page could
be added to an H.13 evidence directory, because no page file was present. The
historical evidence directory `phase2f-source-442-472/` was **not** modified, and no
copyrighted material was added to Git.

---

## 2. §9-4-8 clause-by-clause findings

### 2.1 Required inspection list — status

| Required clause | Status |
| :-- | :-- |
| §9-4-8-1 | **NOT INSPECTED — source absent** |
| §9-4-8-2 | **NOT INSPECTED — source absent** |
| §9-4-8-3 | **NOT INSPECTED this stage** (recorded in earlier phases for a *different* clause — see §2.2) |
| §9-4-8-4 | **NOT INSPECTED this stage** (same caveat) |
| §9-4-8-5 | **NOT INSPECTED this stage** (same caveat) |
| §9-4-8-6 | **NOT INSPECTED — source absent** |
| §9-4-8-7 | **NOT INSPECTED — source absent.** This is the clause the stage brief flags as carrying the plain-wire / deformed-wire wording. **No wording of §9-4-8-7 is quoted, paraphrased, strengthened or weakened anywhere in this document — none could be read** |
| §9-4-8-8 | **NOT INSPECTED — source absent** |
| §9-4-8-9 | **NOT INSPECTED — source absent** |
| Tables referenced by §9-4-8 | **NOT INSPECTED — source absent** |
| Footnotes | **NOT INSPECTED — source absent** |

The nine questions the stage posed (permitted reinforcement types; welded-wire
limitations; steel grade / yield limits; wire diameter limits; table
classifications; transverse-reinforcement-specific conditions; welded-wire-specific
conditions; which conditions §9-21-6-2-3 actually requires; which are unrelated
Chapter 9-4 requirements) **cannot be answered from the available evidence.** They
are recorded as open rather than answered by assumption.

### 2.2 What is already on record about §9-4-8 — and its precise limitation

Earlier phases recorded numeric §9-4-8 fragments as verified **for the purposes of
other clauses**. These are the only §9-4-8 facts anywhere in the project:

| Recorded fact | Sub-clause | Recorded in | Evidence pages on record | Re-inspectable now? |
| :-- | :-- | :-- | :-- | :-- |
| E_s = 200,000 MPa | §9-4-8-4 | `docs/VERIFIED_RULES.md` (`BG-FLEX-STRAIN-LIMIT`), `docs/DESIGN_RULES.md` | PDF 16–18, 22, 41 / printed 107–109, 113, 132 | **No** — those images are not in the committed evidence set |
| f_yt ≤ 420 MPa | §9-4-8-5 | `docs/VERIFIED_RULES.md` (`BG-SHEAR-VS-001`) | PDF 89–90, 140, 142–144 / printed 68–69, 119, 121–123 | **No** — same limitation |
| f_y ≤ 550 MPa; f_yt ≤ 420 MPa; E_s | Table 9-4-4 | `BG-FLEX-STRAIN-LIMIT`, `BG-SHEAR-VS-001`, `BG-FLEX-RECT-SINGLY-001` | as above | **No** — same limitation |
| §9-4-8-3 … §9-4-8-5 cited together | §9-4-8-3…-5 | `docs/VERIFIED_RULES.md` (`BG-FLEX-RECT-SINGLY-001`) | PDF 16–18, 21–23, 41 / printed 107–109, 112–114, 132 | **No** — same limitation |

**Critical limitation, stated plainly:** these fragments were verified for *other*
clauses; their source images are **not** part of the committed evidence, so H.13
could not re-inspect them; and **none of them is known to be what §9-21-6-2-3
requires.** Treating them as the dependency surface would be exactly the
"implement the easiest sub-condition" path the stage brief forbids. H.13 therefore
does **not** claim the D dependency is satisfied by them.

---

## 3. §9-21-6-2-3 dependency analysis (verified this stage from committed evidence)

This is the substantive verification result of H.13.

### 3.1 Full re-read of the clause — method

**Source:** committed evidence `df8067a:phase2f-source-442-472/page-466.jpg`
(§9-21-6-2-3, PDF page 466 / printed page 446). The clause occupies three printed
lines. Each line was read visually from blinded, high-magnification crops, and the
digit convention was established by a **known-value control** before any citation
was accepted:

- **Control (calibration):** the clause's own heading, whose logical number is
  **9-21-6-2-3**, is printed with its digit groups in **reversed visual order**
  (printed left→right as `۳-۲-۶-۲۱-۹`).
- **Control (cross-check):** the independent historical record in
  `docs/PHASE2_SOURCE_VERIFICATION_MATRIX.md` (line 416) states that this clause
  requires **§9-21-6-2-1 and §9-4-8**.

### 3.2 Transcription of the verified lines

Line 1 (heading):

> «۹-۲۱-۶-۲-۳ استفاده از سیم آجدار یا شبکه‌ی آرماتور سیم جوش شده به عنوان جایگزین»

Line 2 (requirement, continues from line 1):

> «تنگ آجدار، با سطح مقطع معادل میلگرد آجدار با در نظر گرفتن الزامات ۹-۲۱-۶-۲-۱ و ۹-۴-۸»

Line 3 (operative word):

> «مجاز است.»

The two reference tokens were isolated and read at 1400 %–2200 % magnification, with
the vanishing line-junction between «آجدار» and «با» re-cropped separately to
confirm the line is continuous and unbroken.

### 3.3 Why the reference reading is robust

The printed reference token is a **three-digit-group** identifier whose middle group
is the distinctive `۴` glyph and whose two end glyphs are `۸` and `۹` in one order or
the other. Because the source reverses digit-group order when printing:

| Assumption about the reversal convention | Reading of the printed token | Logical clause |
| :-- | :-- | :-- |
| Reversal applies (as proven by the heading control) | `۸-۴-۹` | **§9-4-8** |
| Reversal does **not** apply | `۹-۴-۸` | **§9-4-8** |

**Both branches converge on §9-4-8.** The only alternative produced by the reversal
rule — §8-4-9 — is not a clause of this book, and the non-reversed reading of the
*other* token (`۱-۲-۶-۲۱-۹` → §1-2-6-21-9) is likewise not a clause. The reversed
reading of that token is **§9-21-6-2-1**, which is a real, registered, already
executable clause. The reading is therefore settled on both internal and
independent-record grounds.

### 3.4 Resolution of a documentation discrepancy (recorded correction)

The historical records disagreed about the first reference:

| Record | First reference recorded | Second reference recorded |
| :-- | :-- | :-- |
| `docs/PHASE2_SOURCE_VERIFICATION_MATRIX.md` (lines 416, 443, 508) | §9-21-6-2-1 | §9-4-8 |
| Registry `blocked_reason` for `BG-TRANS-WIRE-SUBST-PENDING` | — | §9-4-8 |
| `docs/PHASE2F_STAGE_H_SOURCE_VERIFICATION.md` (item 5) | «۱-۶-۲۱-۹» (read as §9-21-6-1) | «۱-۴-۸-۹» (read as §9-4-8-1) |

**The controlled re-read confirms the matrix/registry reading.** The
`PHASE2F_STAGE_H_SOURCE_VERIFICATION.md` entry dropped a digit group from each token
(«۱-۶-۲۱-۹» instead of «۱-۲-۶-۲۱-۹»; and a narrower «۹-۴-۸-۱» where the print carries
the three-group «۹-۴-۸»). That document is **not** rewritten — it is a historical
record — but downstream work must use the corrected reading:

> **§9-21-6-2-3 references §9-21-6-2-1 and §9-4-8. Nothing else.**

### 3.5 The clause as verified — engineering content

Established from the verified text itself, without interpretation:

1. **A permission, not an obligation.** The operative word is «مجاز است» ("is
   permitted").
2. **Two permitted substitute materials:** deformed wire («سیم آجدار») **or**
   welded-wire reinforcement mesh («شبکه‌ی آرماتور سیم جوش شده») — a disjunction.
3. **What they may replace:** a deformed tie («جایگزین تنگ آجدار»).
4. **The clause's own condition:** equivalent cross-sectional area («با سطح مقطع
   معادل میلگرد آجدار»). This is deterministic and self-contained.
5. **Two imposed external conditions:** «با در نظر گرفتن الزامات **۹-۲۱-۶-۲-۱** و
   **۹-۴-۸**».
6. **First imposed condition — §9-21-6-2-1:** the tie **spacing** rule, which is
   already source-verified and executable in the engine as
   `BG-TRANS-TIE-SPACING-001`. **Important:** the citation is to §9-21-6-2-1, **not**
   to the whole of §9-21-6-1 — so D does **not** inherit the blocked branches A
   (§9-21-6-1-3-ب) or B (§9-21-6-1-5).
7. **Second imposed condition — §9-4-8:** a Chapter 9-4 clause whose content is
   **unread** (§2.1). *What* it adds cannot be stated: not whether it is a material
   specification, a geometry restriction, a detailing rule, or a
   certification/document requirement; not whether it introduces a new engine input;
   not whether it can be evaluated from existing reinforcement inputs.

### 3.6 Dependency surface — pinned

| Component of the required condition | Status |
| :-- | :-- |
| Equivalent cross-sectional area of substitute vs. replaced bar | Deterministic; derivable from existing reinforcement inputs |
| Compliance with §9-21-6-2-1 (tie spacing) | **Already verified + executable** (`BG-TRANS-TIE-SPACING-001`) |
| Compliance with §9-4-8 | **UNREAD — the sole unresolved component** |
| Blocker A (§9-21-6-1-3-ب), Blocker B (§9-21-6-1-5) | **Not inherited by D** — the citation does not reach §9-21-6-1 |

**D's dependency surface is exactly one clause: §9-4-8.** The brief-asserted
description of §9-4-8 as «مشخصات مورد نیاز آرماتورها در طراحی» ("required
reinforcement specifications in design") is **reported in the brief but could not be
verified here**, and is not used as if read.

### 3.7 Direct answers to the stage's dependency questions

| Question | Answer from verified evidence |
| :-- | :-- |
| Does §9-21-6-2-3 simply require the substitution to satisfy §9-21-6-2-1? | **No** — the clause imposes **two** conditions; the second (§9-4-8) is unread |
| What exactly does «مطابق / با در نظر گرفتن …» add? | **UNKNOWN** — the referenced clause content is unavailable |
| Is the dependency purely material/specification eligibility? | **UNKNOWN** — not determinable without §9-4-8. It must not be *assumed* to be material-only |
| Does it require a new BeamGenius user input? | **UNKNOWN** |
| Can it be evaluated deterministically from existing inputs? | **NO — not determinable.** The part that *is* deterministic (equivalent area) is not the whole requirement |
| Does it require external certification/document data not modelled? | **UNKNOWN** |

Per the stage instruction "*do not assume that every §9-4-8 provision must become an
engine input; identify only the provisions actually necessary*" — H.13 identified
**no** provisions, because it could read **no** provisions.

---

## 4. D decision — `BG-TRANS-WIRE-SUBST-PENDING`

**Decision: `KEEP_BLOCKED`.**

| Gate condition (H.13 implementation gate) | Met? |
| :-- | :-- |
| §9-21-6-2-3 is verified | **Yes** — fully re-read this stage (§3) |
| §9-4-8 dependency is verified | **NO — evidence file absent; §9-4-8-1…-9 unread** |
| The exact relevant requirements are deterministic | **NO** — unknown |
| All required inputs exist, or a justified new input can be introduced | **NO — cannot be determined** |
| No external document is required for the evaluated branch | **NO — the external document is exactly what is missing** |
| No ambiguity remains | **NO** — the *content* of §9-4-8 is entirely unknown |
| RuleReference can be completed | **NO** — the §9-4-8 requirement text cannot be cited |
| Tests can be written without unsupported assumptions | **NO** |

The gate fails on six of eight conditions, so **D is not implemented**:

- No Rule ID was created.
- No registry entry was added or changed.
- `BG-TRANS-WIRE-SUBST-PENDING` stays `VERIFY_PENDING` / `execution_allowed=False`.
- **Nothing was implemented from the partially-verified §9-4-8 fragments** (§2.2),
  because whether they constitute the required dependency surface is precisely the
  unknown.
- The deterministic sub-condition ("equivalent area") was **deliberately not**
  implemented on its own: the clause is conjunctive, so a partial rule would produce
  false PASSes. No fake default, no foreign-code substitution, no "easiest
  sub-condition" shortcut was introduced.

**Exact missing dependency:** the readable content of **Mabhas 9 §9-4-8** (Chapter
9-4, printed page ≈68–69 / PDF ≈88–89 side of the book) — the single clause cited by
§9-21-6-2-3.

---

## 5. E status — `BG-TRANS-SPIRAL-SPLICE-SEL-PENDING`

| Field | Record |
| :-- | :-- |
| Previous state (H.10/H.12) | `EXTERNAL_DEPENDENCY` |
| Rule | §9-21-6-3-5-الف, PDF page **468** / printed page **448** (committed evidence) |
| Decision | **`EXTERNAL_DEPENDENCY` — unchanged. Not implemented.** |

**Naming precision confirmed from the source.** At §9-21-4-7-3 (PDF 461 / printed
441, re-read this stage from committed evidence):

> «۹-۲۱-۴-۷-۳ جوش میلگردها در وصله‌های جوشی باید الزامات مبحث دهم مقررات ملی ساختمان را تامین نماید.»

«مبحث دهم مقررات ملی ساختمان» = **the tenth Book of the National Building
Regulations** — i.e. **Mabhas 10 (Steel Structures)**, a **separate governing
document**, *not* a chapter of Mabhas 9. The earlier phases' shorthand "NBC Chapter
10" was correct in substance.

**Why the H.13 evidence file could not have helped E even if it had arrived:** it was
announced as **Mabhas 9** pages 86–89 (Chapter 9-4 material provisions). Mabhas 10 is
a different book and cannot be contained in it. Per the stage instruction, H.13 did
**not** search Mabhas 9 pages for Mabhas 10, did **not** fabricate Chapter 10
content, and did **not** substitute AISC / ACI / CSA or any other steel code.

**Exact remaining dependency:**

1. The **Mabhas 10 welding provisions** referenced by §9-21-4-7-3 — required to
   establish what eligibility a welded splice must satisfy. Not available in any
   accessible form.
2. Additionally, §9-21-4-7 would need its **own, separately gated promotion**
   (§9-21-4-7 is `VERIFY_PENDING` / non-executable as
   `BG-DEV-SPLICE-WELDED-MECH-PENDING`). Promoting §9-21-4-7 would still not
   auto-promote E.

The verified **1.25** strength-transfer coefficient of §9-21-4-7-6 («۱/۲۵») is
untouched; nothing in this stage contradicts the committed-window read.

---

## 6. A / B / C status

No new source evidence on A, B or C was introduced by H.13, and none of the three was
reopened.

| Blocker | Clause | Status | Reason (unchanged) |
| :-- | :-- | :-- | :-- |
| **A** `BG-TRANS-TIE-ANCHOR-PENDING` | §9-21-6-1-3-ب | **`KEEP_BLOCKED`** | λ applicability not established (λ is defined only at §9-21-3-1-6, scoped by its own wording to the l_d calculation; §9-21-6 cites §9-21-3 nowhere); the embedment end-referent and the outer-hook compared quantity are elided in print. **No λ imported, no datum invented, no noun inferred.** |
| **B** `BG-TRANS-WIRE-TIE-PENDING` | §9-21-6-1-5 | **`SOURCE_WORK_REQUIRED`** | The (الف) measure datum / direction is not printed (H.12's two admissible readings stand); the source does not resolve it. **No datum imported from §9-21-6-1-4.** |
| **C** `BG-TRANS-TORSION-TIE-PENDING` | §9-21-6-1-6-ب & §9-21-6-2-7-ب | **`KEEP_BLOCKED`** | Pure transitive dependency on A; the only uncovered OR route is §9-21-6-1-3-ب. |

The four already-executable torsion routes were re-verified present, `VERIFIED`,
`execution_allowed=True`, and **not** modified or duplicated:
`BG-TRANS-TORSION-TIE-135HOOK-001`,
`BG-TRANS-TORSION-TIE-SEISMIC-HOOK-001`,
`BG-TRANS-TORSION-TIE-STANDARD-HOOK-001`,
`BG-TRANS-TORSION-TIE-WIRE-ROUTE-001`.

---

## 7. Scope-control statement

H.13 remained limited to the five identified blocker families (A–E) and to the
source-evidence question for D that the stage was created to answer.

H.13 did **not**: continue any Drive investigation; redesign the engine, its
calculation architecture or its source hierarchy; introduce AI into any calculation
path; import a reference PDF at runtime or add any runtime file/PDF/OCR read; add
speculative formulas, defaults or inputs; implement only the easiest sub-condition of
a composite clause; broaden scope to unrelated Chapter 9-4 provisions or to Mabhas 10
content; start UI, report-generation, DXF or optimisation work; modify
`origin/main`; modify the committed historical evidence (`phase2f-source-442-472/`);
rewrite the historical audit documents (H.9–H.12 were read only); or add any
copyrighted material to Git.

**No unsupported engineering assumption was introduced.** Where the source was
absent, H.13 recorded the absence; where it was silent, H.13 recorded the silence.

---

## 8. Validation

| Gate | Result |
| :-- | :-- |
| `PYTHONPATH=src pytest` | **673 passed** (unchanged) |
| `PYTHONPATH=src mypy --strict` | **clean, 23 source files** |
| Registry | **121 total / 63 executable / 48 blocked / 10 reference-executable** (unchanged) |
| §9-21-6 (clause-prefix predicate) | **21 executable / 5 blocked** (unchanged) |
| Executable-rule behaviour | unchanged — no evaluator, formula, constant, registry entry or test was touched |
| Committed historical evidence | unmodified; `phase2f-source-442-472/` re-verified intact |
| `origin/main` | `df8067a`, unmodified |
| Files changed by H.13 | `docs/PHASE2F_STAGE_H13_SOURCE_EVIDENCE.md` **only** |

---

## 9. What must happen for D to progress

1. **Deliver the §9-4-8 pages so they are actually readable in this environment.**
   The announced artifact did not arrive. Any of the following would work, in
   descending order of usefulness: committing the extracted pages to the repository
   in a clearly named H.13 evidence directory (the pattern already proven with
   `phase2f-source-442-472/`); providing a fetchable public link; or attaching the
   file to the session.
2. **On arrival, read §9-4-8-1 … §9-4-8-9 visually** — in particular §9-4-8-7, whose
   plain-wire / deformed-wire wording must be transcribed exactly, never
   paraphrased stronger or weaker — and determine the **minimum** dependency surface
   rather than importing the whole of Chapter 9-4.
3. **Only then** decide whether existing inputs suffice and apply the H.13
   implementation gate. Because the dependency surface is now proven to be a single
   clause (§3.6), this should be a short, well-bounded exercise.
4. **For E**, Mabhas 10 pages are required — a separate governing document that no
   Mabhas 9 extract can supply.

---

*H.13 is source verification only; no rule is implemented or promoted in H.13, and no
source content is claimed that could not be read.*
