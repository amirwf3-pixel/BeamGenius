# Phase 2F — Stage H.15: INSO 11558 Source Acquisition, Verification & Promotion Audit

**Status: `KEEP BLOCKED`. The authoritative text of INSO/ISIRI 11558 could not be obtained.
`BG-TRANS-WIRE-SUBST-PENDING` remains `VERIFY_PENDING` / `execution_allowed=False`.
No engineering rule was implemented or promoted.**

H.14 established that the sole remaining dependency of Clause 9-21-6-2-3 is
**§9-4-8-7**, which requires plain wire, deformed wire and welded meshes to conform to
**Iranian National Standard No. 11558**. H.15 was scoped to acquire and verify that
standard, or to record its absence precisely.

**Result in one line:** the standard's *identity* is confirmed beyond reasonable doubt
from several independent sources, but its **authoritative text is not reachable from
this environment**, and the only sources offering the text are commercial resellers —
which the stage brief expressly forbids as a source of truth. D therefore stays
blocked.

This document records the acquisition effort, the verified identity, the dependency
map, the engineering analysis of *why* possession of the standard may still not be
sufficient, the two governance maintenance corrections applied, and the exact
evidence required to unblock.

---

## 0. Scope and method notes

**Web sources supplied by the user.** The stage brief refers to two web sources having
been placed at the project's disposal. **No such attachment arrived** with the H.15
instruction (no attachment block was present; `/home/user/uploads/` does not exist).
The brief itself states that such sources would be *secondary contextual sources only*
and that no numeric value, requirement, table, tolerance, chemical composition,
mechanical property or executable rule may be imported from them. Accordingly their
absence does not weaken the conclusion — but it is recorded so that no later stage
assumes they were read.

**Sandbox egress.** The sandbox has **no general internet egress**: direct `curl` to
`standard.isiri.gov.ir`, `www.inso.gov.ir` and even `www.google.com` all returned
**HTTP 000**. All retrieval below was performed through the tooling proxy
(`fetch_page` / `web_search`), and the failures recorded are proxy-level failures, not
sandbox-level ones.

**Evidence basis.** The only committed Mabhas 9 evidence available to this branch is
`phase2f-source-948/` (PDF 86–89 / printed 66–69 = §9-4-7 end, all of §9-4-8, and the
start of §9-4-9's environment). `phase2f-source-442-472/` lives on `origin/main`
(`df8067a`), read-only via `git show`.

---

## 1. Task 1 — Source acquisition effort (recorded, with every route tried)

| # | Route | Priority per brief | Action | Outcome |
| :-- | :-- | :-- | :-- | :-- |
| 1 | INSO official standards portal `standard.isiri.gov.ir` | **P1 (official)** | `fetch_page` on `/Standard/Search?q=11558`, `/Standard/Search?SearchType=1&StandardNo=11558`, `/`, and `http://` variant | **FAILED — "Failed to fetch page" on every path** |
| 2 | INSO home portal `www.inso.gov.ir` | **P1 (official)** | `fetch_page` on portal home and the standards/news sections | **REACHABLE but news-only** — no standards search or download endpoint exposed |
| 3 | INSO's own free-access announcement | **P1 (official)** | `web_search` and `fetch_page` of the INSO notice | Found: *«تمامی استانداردهای ملی ایران از طریق پورتال سازمان ملی استاندارد ایران به نشانی **standard.isiri.gov.ir** به صورت رایگان برای کاربران قابل دسترسی و دانلود می‌باشد»* — i.e. the official free route is exactly the portal that is **unreachable** here |
| 4 | Direct sandbox download | P1 | `curl` to the portal | **HTTP 000 — no egress** |
| 5 | ISIRI standards mirror path pattern (`dl.azmanco.com/standards/ISIRI/`) | P3 | `fetch_page` on the directory and on a `11558-*.pdf` pattern | **HTTP 404** — no such document at that path |
| 6 | General/English web search for the standard's text | P3 | multiple `web_search` queries | **Nothing relevant** — the standard is not indexed in accessible English-language sources |
| 7 | Persian search for the full text | P3 | multiple `web_search` queries | **Only commercial resellers and unverifiable excerpts** (see §1.1) |
| 8 | National Building Regulations' own reference-standards appendix (`پیوست 2`) | P2 (authoritative citation) | `web_search` + review of the appendix listing | **SUCCESS — identity confirmed** (§2) |

### 1.1 Commercial / unverifiable sources found — deliberately NOT used

These were encountered and are recorded **only** so that the record shows they were
seen and rejected:

| Source | What it offers | Why rejected |
| :-- | :-- | :-- |
| `gigapaper.ir` | Sells ISIRI standard PDFs (including for 11558) at a per-file price | Paid commercial reseller; brief prohibits commercial sites as source of truth |
| `faratest.com` | Reproduces technical excerpts it attributes to ISIRI 11558 (tensile table references, `Rm/Rp0.2 ≥ 1.03`, bend test to ISO 10065, 95 % acceptance wording, ISO 10544 as reference standard) | Equipment vendor's marketing page; **no document presented, no page/section citation, no way to authenticate** |
| `jdsharif-met.com` | Laboratory page describing ISIRI 11558 test scope and a table fragment (R0.2 = 500, Rm = 550, A5 = 12 %) | Commercial laboratory page; same defect |
| `karduk.com`, `ahanmelgar.com`, `ahangar.com` etc. | Paraphrase the standard's scope and rebar standards generally | Commercial/blog sources |

**None of the numeric values, tables, tolerances or properties quoted by any of the
above was imported into this document, into the registry, into the engine, or into any
rule.** They are not reproduced here as requirements. They appear in this table solely
as provenance for the "rejected" determination.

---

## 2. Task 2 — INSO 11558 identity (confirmed) and edition (not confirmed)

### 2.1 Identity — confirmed

| Field | Value | Basis |
| :-- | :-- | :-- |
| Standard number | **11558** | Multiple independent sources, incl. the National Building Regulations' Appendix 2 reference list |
| Persian title (established form) | **«میلگردهای سرد نوردیده مورد مصرف جهت تسلیح بتن و ساخت شبکه‌های جوش شده – ویژگی‌ها»** | Appendix 2 (`پیوست 2`) of the National Building Regulations, and the Tehran joist/block manufacturers' association standards list |
| Variant wording seen | «میلگردهای سرد نوردشده مورد مصرف تسلیح بتن و ساخت شبکه‌های جوش شده» | Commercial sources (longer/shorter form of the same title) |
| English rendering (project's own translation) | "Cold-reduced (cold-rolled) steel bars/wire for use in the reinforcement of concrete and the manufacture of welded mesh — Specifications" | Translated from the Persian title above; **not** an official English title read from the standard |
| Issuing body | **INSO / ISIRI** — Organization (formerly Institute) of Standards and Industrial Research of Iran | Established institution identity |
| Revision / edition | **NOT ESTABLISHED** | No authoritative source reached gave a revision number or year |
| Publication year | **NOT ESTABLISHED** | — |
| Validity status (in force / superseded) | **NOT ESTABLISHED** | — |
| Relationship to Mabhas 9 | Mabhas 9 §9-4-8-7 mandates conformity to it; Mabhas 9 (1399, 5th ed.) cites it **without a year**, so the reference is to the standard as in force | Verified in H.14 from `phase2f-source-948/` |
| Scope | **Product specification for cold-reduced (cold-worked) steel bars/wire used to reinforce concrete, and for welded mesh made from such wire.** Confirmed as covering both the wire and the welded-mesh product family | Title itself + the fact that Mabhas 9 §9-4-8-7 applies it to plain wire, deformed wire and welded mesh alike |
| Covers plain wire? | Yes (title's «میلگردهای سرد نوردیده» + §9-4-8-7's explicit scope) | — |
| Covers deformed wire? | Yes | — |
| Covers welded wire mesh? | Yes — «ساخت شبکه‌های جوش شده» is in the title | — |
| Reference international standard | Reported by several secondary sources as **ISO 10544** (cold-reduced steel wire for the reinforcement of concrete and the manufacture of welded fabric) | **Secondary only — recorded as context, never as a substitute (Task 7)** |

### 2.2 What is NOT established, and will not be guessed

- Revision number and year of the edition in force.
- Whether the version currently in force differs from the version in force when
  Mabhas 9 (1399) was published.
- Validity status.
- Any clause number, table number, grade designation, property value, tolerance or
  acceptance criterion inside the standard.

**No title, number, year or edition was completed by inference.** Where a value could
not be sourced authoritatively it is recorded as **NOT ESTABLISHED**.

### 2.3 Premise check — a correction to the stage brief

The brief states that the INSO 11558 dependency "was seen in §9-4-8-7 **and also** in
§9-4-9-2-1-2 / Table 9-4-1 of the available evidence", quoting:

> «S500C = سیم‌های ساده و یا آج‌دار [2]» with footnote «[2] شکل آج مطابق استاندارد ملی ایران شماره 11558»

**This text is not present in any evidence available to this project, and it was not
verified.** Concretely:

| Check | Result |
| :-- | :-- |
| Committed evidence on this branch | `phase2f-source-948/` only — pages PDF 86–89 / printed 66–69 |
| What those pages cover | End of §9-4-7, **all of §9-4-8** (§9-4-8-1 … §9-4-8-9 + Tables 9-4-4, 9-4-5), and the start of §9-4-9's subject matter |
| Table 9-4-1 | **Not in the delivered range** — Table 9-4-1 precedes §9-4-7/§9-4-8 in the chapter (the delivered range's own §9-4-8-5 refers forward to Tables 9-4-4/9-4-5, and §9-4-8-9 cites "جدول ۹-۴-۳") |
| §9-4-9-2-1-2 | **Not in the delivered range** — §9-4-9 begins after printed p. 69 |
| Search of all committed evidence text | Zero hits for `جدول 9-4-1` / `9-4-1` / `9-4-9-2` |

**Consequence:** the `S500C` designation and the Table 9-4-1 footnote wording are
recorded here as **user-asserted / UNVERIFIED — not read from source**. They were
**not** used as basis for any determination, and the `S500C` grade is **not** treated
as a Mabhas 9-defined admissibility class. If a future stage needs Table 9-4-1, those
pages must be supplied as evidence in the same way `phase2f-source-948/` was.

This matters for Task 5: the grade-class question ("are all INSO 11558 grades usable,
or only some classes?") currently has **no verified Mabhas 9 anchor at all**, because
the one table that allegedly links a grade to a wire-type class has not been read.

---

## 3. Task 3 — Relevant requirements

**Not extractable.** Since neither the standard's text nor its table structure could
be obtained, **no requirement was extracted**. Specifically, none of the following
could be established, and none was assumed:

plain wire requirements · deformed wire requirements · welded mesh requirements ·
mechanical properties · yield strength · tensile strength · elongation/ductility ·
diameter limits · dimensional tolerances · rib geometry / deformation requirements ·
welding & welded-mesh requirements · identification/marking · conformity/acceptance
criteria · classes/grades · `S500C` or any other grade named by Mabhas 9 · any
requirement needed to decide whether a wire or mesh may substitute for a tie.

The brief's instruction — *"extract only requirements that actually exist in the
source"* — resolves to **extracting nothing**, because no source was obtained.

---

## 4. Task 4 — Dependency map (verified parts marked)

```
§9-21-6-2-3  (Mabhas 9, printed p. 446 / PDF p. 466 — VERIFIED, H.13)
│
├─ (1) equal cross-sectional area, self-contained
│        → DETERMINISTIC from existing area inputs
│
├─ (2) «الزامات ۹-۲۱-۶-۲-۱»
│        └→ §9-21-6-2-1 tie spacing
│              └→ BG-TRANS-TIE-SPACING-001
│                    → VERIFIED / execution_allowed=True  ✓ RESOLVED
│
└─ (3) «الزامات ۹-۴-۸»   (Mabhas 9, printed pp. 66–69 / PDF 86–89 — VERIFIED, H.14)
         ├─ §9-4-8-1  deformed mandatory; plain only in spirals   → DETERMINISTIC
         ├─ §9-4-8-2  yield-stress measurement methods            → not an engine input
         ├─ §9-4-8-3  constitutive law (Eqs 9-4-1/-2)             → already implemented
         ├─ §9-4-8-4  Es = 200,000 MPa                            → already verified
         ├─ §9-4-8-5  yield cap per Table 9-4-4 / 9-4-5           → DETERMINISTIC
         ├─ §9-4-8-6  type eligibility per Table 9-4-4 / 9-4-5    → AMBIGUOUS for mesh (§6)
         ├─ §9-4-8-7 ─────────────────────────────────────────────┐
         │      conformity to INSO 11558                          │  ★ THE BLOCKER
         │        └→ INSO / ISIRI 11558                           │
         │             identity: CONFIRMED (§2.1)                 │
         │             text:     NOT OBTAINED (§1)                │
         │             edition:  NOT ESTABLISHED (§2.2)           │
         ├─ §9-4-8-8  deformed-wire diameter 1.5–16 mm            → DETERMINISTIC
         └─ §9-4-8-9  longitudinal bars, special seismic systems   → out of scope for D;
                      truncated at printed p. 69                   → incomplete
```

**Which parts of INSO 11558 would be needed for deterministic execution?** — This
question **cannot be answered** without the standard's structure. What *can* be said
from the dependency chain is that §9-4-8-7 is a *blanket conformity* reference: it
does not itself name a clause, table or property of 11558. Determining which of the
brief's 17 candidate requirement categories is actually load-bearing therefore
requires reading 11558 itself. Any claim about "which sections are needed" made
without the document would be invention.

---

## 5. Task 5 — The decisive engineering question: would the standard alone make D deterministic?

This is the most important finding of H.15, and it is independent of the acquisition
failure.

**§9-4-8-7 is a product-conformity requirement, not a design requirement.** It says
that the *material supplied* shall conform to a manufacturing standard. That is
categorically different from the rest of §9-4-8, which supplies numeric design values
(E_s, yield caps, diameter windows) that BeamGenius can evaluate from typed inputs.

If the standard's full text were in hand tomorrow, BeamGenius could encode from it:
numeric caps, diameter windows, property minima — i.e. **checks on values the caller
supplies**. But the clause's own predicate is "*the material conforms to INSO 11558*",
and a specific batch of wire conforms (or does not) according to a **mill certificate /
type test report** established by the producer, not derivable inside a design engine.

So D's remaining dependency is **two-layered**:

| Layer | Nature | Status after H.15 |
| :-- | :-- | :-- |
| **L1** | The **text** of INSO 11558 — needed to know which numeric checks exist and which grades/diameters/rib geometries it defines | **NOT OBTAINED** |
| **L2** | A **decision about how conformity is established in BeamGenius** — either (a) the engine performs numeric conformance checks on caller-supplied measured properties, or (b) the engine accepts a caller assertion of product certification, or (c) product conformity is declared out of the engine's scope by an explicit, recorded project decision | **NOT MADE — and this is a governance/scope decision, not a source-acquisition task** |

**This is a substantive correction to the framing of the blocker.** H.14 recorded the
blocker as "an external document this project cannot read". H.15 shows that even a
readable document would not by itself produce a deterministic rule: layer L2 must be
decided, and option (b) — a caller self-declaration — would make the rule *executable
but not self-verifying*, which the project's governance (a registry reference is not
proof of verification; VERIFY_PENDING never emits PASS) does not permit without an
explicit decision.

Applying the brief's own Task 5 checklist, with the standard unavailable:

| Question | Answer |
| :-- | :-- |
| Which wires are admissible? | **UNDETERMINABLE** (L1) — Mabhas 9 gives §9-4-8-1 + §9-4-8-8's 1.5–16 mm window, but the grade/class space is defined by 11558 |
| Which welded meshes are admissible? | **UNDETERMINABLE** (L1) + **AMBIGUOUS** (§6) |
| All 11558-conforming wires usable, or only some classes/grades? | **UNDETERMINABLE** — and the Mabhas 9 side of this question (Table 9-4-1 / S500C) is itself **unverified** (§2.3) |
| Diameter limits? | §9-4-8-8 verified (1.5–16 mm for deformed wire); any 11558-specific diameter series **UNDETERMINABLE** |
| Grade / f_y limits? | §9-4-8-5 + Table 9-4-4 verified (420 MPa for shear ties); grade classes **UNDETERMINABLE** |
| Is welded mesh admissible at all, or only a specific kind? | **AMBIGUOUS — see §6** |
| Extra requirements for the tie application? | Not identified — requires L1 |
| Is equivalence only A_s, or more? | **More than A_s** — §9-21-6-2-3's own condition is area equivalence, but §9-4-8 adds material-conformity conditions layered on top; the clause cannot be reduced to an area check without a FALSE PASS |
| Additional spacing / welding / geometry / anchorage requirements? | **UNDETERMINABLE** (L1); note §9-4-8-8 already redirects >16 mm deformed wire to §9-21-3-7 as plain wire |

**Consequence:** the "partial implementation" temptation is rejected again, and now on
two independent grounds — the document is missing, **and** the conformity predicate
has no modelled input.

---

## 6. Task 6 — The welded-mesh ambiguity (still unresolved)

H.14 found (and re-verified at 500 % on printed p. 68) that:

1. §9-21-6-2-3 **expressly permits** «شبکه‌ی آرماتور سیم جوش شده» (welded wire mesh) as
   a tie substitute; but
2. §9-4-8-6 requires the **type** of reinforcement used to follow **Table 9-4-4**, and
   the table's shear/tie row (`خاموت‌ها، پست‌ها، تنگ‌ها`) lists only deformed bars and
   deformed wires, with **remarks cell `-`**; and
3. the only mesh permission printed in Table 9-4-4 — footnote [۲]
   «استفاده از شبکه‌های آجدار جوشی نیز مجاز است» — sits on the **flexure/axial
   «سایر موارد»** row, not on the shear tie row.

**Does INSO 11558 resolve this? No — and it could not, even if obtained.** The
standard's scope is **manufacturing**: it specifies what a cold-reduced wire or welded
mesh must be in order to be a conforming product (its title includes «ساخت شبکه‌های
جوش شده»). Its scope does **not** govern *when a welded mesh may structurally replace a
tie inside a reinforced-concrete member* — that is a design-admissibility question, and
it lives in Mabhas 9's own hierarchy (Table 9-4-4 and §9-21-6-2-3).

So the ambiguity is a **Mabhas 9-internal** question, and the brief's instruction is
explicit: *"do not resolve this ambiguity automatically with INSO 11558."* The two
admissible readings identified in H.14 §4.2 stand:

- **Reading 1** — §9-21-6-2-3's express permission governs; the mesh substitute needs
  only the general material conditions (§9-4-8-1 deformed, §9-4-8-7 conformity).
- **Reading 2** — §9-4-8-6 makes Table 9-4-4's type list mandatory, and the shear/tie
  row carries no mesh permission, so a mesh-for-tie substitution is not admitted by
  that row.

The two readings have materially different PASS/FAIL consequences. **The ambiguity
remains UNRESOLVED and is recorded as such.** Nothing was chosen.

---

## 7. Task 7 — No substitute standard accepted

During acquisition, the following comparable/related standards were encountered:

| Standard | Relationship | Disposition |
| :-- | :-- | :-- |
| **ISO 10544** | Reported by several secondary sources as the international reference standard underlying ISIRI 11558 (cold-reduced steel wire for concrete reinforcement / welded fabric) | **Context only. NOT a substitute.** Not read, not used, no value imported |
| **BS 4482:1985** | British counterpart, "cold reduced steel wire for the reinforcement of concrete" — surfaced in English-language search | **Context only. NOT a substitute.** Withdrawn per its own catalogue entry; not read |
| **ISO 10065 / ISO 6892** | Test-method standards cited by secondary sources as the bend/tensile test references within 11558 | **Context only.** Not read, not used |
| **ASTM A185 / A82 / A496, GB/T 1499.3, IS 1566/432, JGJ 114, DIN EN 10080** | Other national/regional welded-wire or reinforcement standards surfaced incidentally | **Context only. NOT substitutes.** Not read, no value imported |
| **ISIRI/INSO 3132, 1-21056** | The two *other* Iranian standards Mabhas 9 §9-4-7-1 cites for welding operations | Different dependency (welding process, not wire product). **Not used here**; recorded as separately verified-available source for a future stage |

**No value, table, tolerance, composition, property or rule from any of these entered
BeamGenius.** Per the brief: if INSO 11558 is unavailable, the rule stays BLOCKED even
where an equivalent foreign standard exists. It does.

---

## 8. Task 8 / 10 — Governance audit and corrections applied

### 8.1 Issue A — spurious `§9-21-6-2-2` dependency — **CORRECTED**

The registry entry's `description` read:

> "…subject to Clauses **9-21-6-2-1, 9-21-6-2-2** and National Building Regulations
> Clause 9-4-8 (**welded-wire steel**)."

Two defects, both verified:

1. **`§9-21-6-2-2` is not a dependency.** H.13's controlled visual read of §9-21-6-2-3
   (committed page-466 JPG, digit-order calibrated against a known-value control) found
   the clause cites **§9-21-6-2-1 and §9-4-8 only**. §9-21-6-2-2 is the *minimum tie
   diameter* rule and is not referenced by §9-21-6-2-3.
2. **"welded-wire steel" mis-describes §9-4-8.** §9-4-8 is the general reinforcement
   specification clause (deformed requirement, constitutive law, E_s, yield caps, type
   eligibility, wire/mesh conformity, diameter window, seismic longitudinal
   reinforcement) — not a welded-wire-steel clause.

**Applied:** the `description` was corrected to state the true citation and to record
the correction; the `blocked_reason` was rewritten to reflect the *actual* current
blocker (§9-4-8-7 → INSO 11558 unavailable; mesh/tie ambiguity), replacing the stale
claim that §9-4-8's pages are "out of the verified window" — which H.14 falsified.
**Status and `execution_allowed` are unchanged** (`VERIFY_PENDING`, `False`).

### 8.2 Issue B — documentation still showing §9-4-8 as unavailable — **CORRECTED**

Six stale statements were corrected across two files:

| File | Line (pre-edit) | Stale claim | Correction |
| :-- | :-- | :-- | :-- |
| `docs/PHASE2_SOURCE_VERIFICATION_MATRIX.md` | 194 | "Chapter 9-4 … incl. 9-4-8 … — pages not delivered" | §9-4-8 delivered + visually verified (H.14); residual INSO 11558 dependency |
| same | 339 | "…incl. 9-4-8 … — pages not delivered" | same |
| same | 371 | "…(incl. 9-4-8) out of window (VERIFY_PENDING)" | §9-4-8 verified; residual is §9-4-8-7 → INSO 11558 |
| same | 416 | "**§9-4-8 (out of window)**" | §9-4-8 verified (H.14); residual INSO 11558 + mesh/tie ambiguity |
| same | 443 | "…incl. 9-4-8 … — pages not delivered" | same |
| same | 508 | "depends on NBC Clause 9-4-8 welded-wire steel (out of window)" | blocked on INSO 11558 via §9-4-8-7 + mesh ambiguity |
| `docs/VERIFIED_RULES.md` | 1896 | `BG-DEV-LAP-WIRE-DEFORMED-PENDING` "9-4-8 out of window" | §9-4-8 verified; residual INSO 11558 |
| same | 2096 | `BG-TRANS-WIRE-SUBST-PENDING` "9-4-8 … out of window" | corrected as above; points to H.14/H.15 docs |

Historical audit documents (**H.9–H.14**) were **not** rewritten — they remain accurate
records of the state at their own dates.

**These are documentation/metadata corrections only.** No rule status, no
`execution_allowed` flag, no formula, no test and no engine behaviour was changed.

---

## 9. Task 11 — Scope discipline

H.15 did **not** touch: UI, frontend, reports, DXF, Excel, optimisation, beam flexural
design, beam shear design, any unrelated detailing rule, any existing executable rule,
or any engine code. No Google Drive investigation. No ACI/CSA/EC/ASTM substitution. No
AI in any calculation path. No runtime file/PDF/OCR dependency. `origin/main`
(`df8067a`) untouched; no history rewrite.

---

## 10. Task 12 — Validation

| Gate | Result |
| :-- | :-- |
| `PYTHONPATH=src pytest` | **673 passed** |
| `PYTHONPATH=src mypy --strict` | **clean — 23 source files** |
| `git diff --check` | clean |
| Registry | **121 total / 63 executable / 48 blocked / 10 reference** — unchanged |
| Duplicate Rule IDs | **0** |
| §9-21-6 (clause-prefix predicate) | **21 executable / 5 blocked** — unchanged |
| `BG-TRANS-WIRE-SUBST-PENDING` | `execution_allowed=False`, `VERIFY_PENDING` — unchanged |

---

## 11. H.15 decision — `KEEP BLOCKED`

`BG-TRANS-WIRE-SUBST-PENDING` stays:

```text
status            = VERIFY_PENDING
execution_allowed = false
```

**Precise reasons (each independently sufficient):**

1. **The authoritative text of INSO/ISIRI 11558 could not be obtained.** The official
   free-access portal named by INSO itself (`standard.isiri.gov.ir`) is unreachable
   from this environment on every path attempted; the INSO portal that *is* reachable
   exposes no standards search or download. The only sources presenting the text are
   commercial resellers and vendor pages with unverifiable, unattributable excerpts —
   expressly inadmissible.
2. **The edition/year is unestablished**, so even a text would need provenance work to
   confirm it matches the version Mabhas 9 (1399) invokes.
3. **§9-4-8-7's conformity predicate has no modelled input** (§5). Even with the text,
   a deterministic rule needs a project decision on how material conformity is
   established. Until that exists, implementing D would require either a FALSE PASS or
   a caller self-declaration treated as verification — neither is governance-compliant.
4. **The welded-mesh/tie ambiguity remains unresolved** (§6) and is a Mabhas 9-internal
   question that INSO 11558 does not answer.
5. **The alleged second Mabhas 9 anchor (Table 9-4-1 / S500C) is unverified** (§2.3) —
   so the grade-class admissibility question has no verified Mabhas 9 basis at all.

No partial rule, no area-equivalence-only PASS path, and no external-standard
substitution was created.

---

## 12. Exact evidence required to unblock

**L1 — standard text.** Any one of:

1. **The INSO/ISIRI 11558 document itself** supplied the way `phase2f-source-948/` was:
   images or PDF committed into the repository (e.g. `phase2f-source-11558/`) with the
   **edition/revision year visible on the cover page**, so the version can be pinned.
   This is the strongly preferred route — it was the only route that actually worked
   for §9-4-8.
2. A **fetchable, publicly accessible URL** to the official INSO document that the
   tooling proxy can retrieve (`standard.isiri.gov.ir` is unreachable now; a direct
   document link on a reachable host would work).
3. Files attached to the session, **provided they actually materialise** — three prior
   attachments (H.12, H.13, H.15) did not arrive, so this route should be verified
   before it is relied upon.

**L2 — scope decision (project owner).** An explicit, recorded determination of one of:

- **(a)** BeamGenius evaluates §9-4-8-7 numerically — i.e. the engine checks
  caller-supplied measured wire/mesh properties against the standard's limits; or
- **(b)** BeamGenius accepts a caller-supplied conformity/certification reference and
  the rule is documented as *executable but not self-verifying*; or
- **(c)** §9-4-8-7 product conformity is declared **outside the engine's scope** by
  explicit decision — in which case D's remaining conditions (§9-4-8-1 deformed, §9-4-8-5
  yield cap, §9-4-8-8 diameter window, area equivalence, §9-21-6-2-1 spacing) become
  candidates for promotion, **with the mesh/tie ambiguity (§6) still to be settled**.

**L3 — optional, for completeness.** Table 9-4-1 / §9-4-9-2-1-2 pages, if the grade-class
(S500C) linkage is to be modelled; and printed p. 70 to close §9-4-8-9.

**Without L1 *and* L2, `BG-TRANS-WIRE-SUBST-PENDING` must remain `VERIFY_PENDING` with
`execution_allowed = false`.**

---

## 13. URLs and sources consulted (recorded per Task 8)

**Official / institutional (Priority 1–2)**

- `https://standard.isiri.gov.ir/` — official free standards portal named by INSO →
  **unreachable** (all paths)
- `https://standard.isiri.gov.ir/Standard/Search?q=11558` → **unreachable**
- `https://standard.isiri.gov.ir/Standard/Search?SearchType=1&StandardNo=11558` → **unreachable**
- `http://standard.isiri.gov.ir/` → **unreachable**
- `https://www.inso.gov.ir/portal/home/` → reachable; news/home only, no standards search
- INSO notice *«تمامی استانداردهای ملی به صورت رایگان در دسترس عموم قرار دارد»* → confirms
  `standard.isiri.gov.ir` as the official free route (the one that is unreachable)
- `https://www.banatarh.com/regulations/chapter/528796/پیوست-2-:-استانداردهای-مرجع/` —
  National Building Regulations **Appendix 2 (reference standards)** → **primary
  identity confirmation** for the title
- `http://sjbp.ir/…/استانداردها` — Tehran joist & block manufacturers' association
  standards list → corroborates the title

**Mirrors / aggregators (Priority 3)**

- `https://dl.azmanco.com/standards/ISIRI/` → **404** (no such path)
- `https://civil808.com/sites/default/files/m9-chenges.pdf` — Mabhas 9 (1399)
  change-log document → read for edition context; no 11558 content
- `https://fa.wikipedia.org/wiki/میلگرد` — general Iranian rebar standards context

**Commercial / vendor (encountered, REJECTED as source of truth)**

- `https://www.gigapaper.ir/…` — paid ISIRI PDF reseller (**not purchased, not used**)
- `http://faratest.com/…` — equipment vendor page with unattributed 11558 excerpts
- `https://jdsharif-met.com/…` — laboratory page with unattributed 11558 excerpts
- `https://karduk.com/…`, `https://ahangar.com/…`, `https://ahanmelgar.com/…`,
  `https://sivanland.com/…`, `https://fardadfoolad.ir/…`, `https://modiranahan.com/…` —
  commercial/blog restatements of rebar standards

**International (context only — no substitution)**

- `https://knowledge.bsigroup.com/…` — BS 4482:1985 catalogue entry (withdrawn)
- Several welded-wire-mesh supplier/standards pages (ASTM A185/A82, GB/T 1499.3,
  IS 1566/432, JGJ 114, DIN EN 10080) surfaced incidentally in search — **none used**

---

## 14. Files changed by H.15

| File | Change | Why |
| :-- | :-- | :-- |
| `docs/PHASE2F_STAGE_H15_INSO_11558.md` | **new** | This H.15 record |
| `src/beamgenius/registry/catalog.py` | `description` + `blocked_reason` of `BG-TRANS-WIRE-SUBST-PENDING` corrected | Issue A — spurious `9-21-6-2-2` removed; "welded-wire steel" mis-description fixed; stale "out of window" reason replaced with the real blocker. **No status/count change** |
| `docs/PHASE2_SOURCE_VERIFICATION_MATRIX.md` | 6 stale §9-4-8 statements corrected | Issue B — matrix still claimed §9-4-8 was undelivered |
| `docs/VERIFIED_RULES.md` | 2 stale §9-4-8 statements corrected | Issue B — same |

**No rule ID was added, removed, promoted or deprecated. No engineering behaviour
changed.**

---

*H.15 is an acquisition and dependency audit. The standard's identity is confirmed; its
authoritative text is not available; and even with the text, a project-level decision
would be required before `BG-TRANS-WIRE-SUBST-PENDING` could become deterministic.
Absence of authoritative evidence means **BLOCKED**.*
