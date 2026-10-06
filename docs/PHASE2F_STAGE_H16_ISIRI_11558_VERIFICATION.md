# Phase 2F — Stage H.16: ISIRI 11558 Verification and Wire-Substitution Decision

**Decision: `KEEP BLOCKED`.** `BG-TRANS-WIRE-SUBST-PENDING` remains
`VERIFY_PENDING` / `execution_allowed=False`. **No rule was promoted, and no partial
rule was created.**

The ISIRI 11558 document was obtained, visually verified in full, and analysed against
Mabhas 9 §9-21-6-2-3. The verification shows that **the external standard does not
close the dependency** — and that it could not, because what §9-4-8-7 demands is a
*product-conformity* determination whose only acceptance routes are third-party
certification against yet another external standard (ISO 10144:1991) or statistical
consignment testing of 15–60 specimens per 50-tonne lot. Neither is representable as a
deterministic engineering input. A second, independent obstacle was also found: the
standard's rating scale (**500 MPa**) does not match the Mabhas 9 shear-tie row's
admissible scale (**≤ 420 MPa**).

Baselines read first: `PHASE2F_STAGE_H13_*` (citation analysis), `H14_*` (§9-4-8
findings), `H15_*` (INSO acquisition audit). Historical documents are **not** rewritten.

---

## 1. Source identity and provenance

| Field | Value |
| :-- | :-- |
| Standard | **ISIRI 11558**, 1st edition («چاپ اول») |
| Persian title | «میلگردهای سرد نوردیده مورد مصرف جهت تسلیح بتن و ساخت شبکه های جوش شده – ویژگی ها» |
| English title (cover) | "Cold-reduced steel wire for the reinforcement of concrete and the manufacture of welded fabric" |
| Issuer | مؤسسه استاندارد و تحقیقات صنعتی ایران (Institute of Standards and Industrial Research of Iran) |
| Approval | Approved at the **419th meeting** of the National Standards Committee for Mechanics and Metallurgy; dated **۱۳۸۷/۱۲/۲۴** |
| Source standard | **ISO 10544:1992** |
| ICS | 91.080.40 ; 77.140.15 |
| Pages | **19** (cover, institute intro, commission ج/د, TOC و, foreword ز, content ۱–۱۳, Annex A) |
| SHA-256 | `4c1c1a478ab8a39b6a19cabc63eac63afbaf2f31c4a7c3eaf55549c9d039916c` |
| Evidence location | `phase2f-source-11558/ISIRI-11558.pdf` (+ `README.md`, `VERIFICATION-NOTE.md`) |

Verification method: every statement below was read from **rendered page images**
(2.2×–5×). The embedded text layer was used for **navigation only**. Full clause-by-clause
transcription is in `phase2f-source-11558/VERIFICATION-NOTE.md`.

**Note on completeness:** the delivered content pages are exactly ۱–۱۳ with no gap, and
the front matter is continuous. One **internal print discrepancy** was found and is
recorded rather than resolved (§3).

---

## 2. What ISIRI 11558 establishes

### 2.1 Product definition and rating

- **Scope (Clause 1):** cold-worked (cold-reduced) steel wire for use in reinforced
  concrete **or welded parts**, defined **at characteristic strength 500 N/mm²**;
  production by die-drawing or rolling at the manufacturer's discretion; for coiled
  product the standard applies to the **straightened** product; wire made from plate or
  railway rails is excluded.
- **Types:** smooth (ساده, defined as wire *lacking bonding property*), indented
  (شیاردار), ribbed (آجدار). **No other wire type is defined.**
- **Rating:** `R_p0.2 = 500 N/mm²`, `R_m = 550 N/mm²`, `A_5.65 = 12 %` (Table 3). This is
  the **only** strength class in the document.

### 2.2 Numeric requirements available from the standard

| Requirement | Value / rule | Clause |
| :-- | :-- | :-- |
| Nominal diameter range | 4–16 mm | 4 |
| Recommended diameters (Table 1) | 5, 6, 7, 8, 9, 10, 12 mm only | Table 1 |
| Mass / nominal areas | given for the 5–12 mm range | Table 1 |
| Tolerances | middle sizes ≤ next-larger table size; **±5 % for 12–16 mm** | 4 |
| Ribbed-wire rib geometry | ≥ 2 rib rows, spacing ≤ 0.8d, `f_r` 0.036–0.056 by range | 5-1 |
| Indented-wire geometry | ≥ 2 indentation rows, `f_p` 0.007–0.014 by range | 5-2 |
| Chemical composition | C, Si, Mn, P, S, N, C_eq maxima (Table 2) | 6 |
| Tensile properties | 95 %/95 % rule and `R_m/R_p0.2 ≥ 1.03` per sample | 7-1 |
| Bend test | 160°–180° over Table 4 mandrels | 8-2 |
| Rebend test | 90° then 20° over Table 5 mandrels | 8-3 |
| Bend/rebend acceptance | no visible crack or fracture | 7-2, 7-3 |

### 2.3 What the standard does **not** contain

Verified by full-document reading and content search:

- **No welded-fabric clause.** «جوش» (weld/welded) occurs only in the document's *title*
  (cover, commission page, foreword) — never in a normative clause, table or footnote.
  There is **no** weld-shear requirement, no mesh geometry/spacing requirement, no
  mesh-specific test, certification or marking requirement. The standard specifies
  individual wires and applies to them as products **used in** welded fabric; the
  fabric itself is unspecified.
- **No 420 MPa rating.** The standard's only scale is 500 MPa.
- **No dimensional or property values for diameters 13–16 mm** outside the bend-test
  mandrel tables (see §3).
- **No service/structure-related requirement of any kind** — nothing about using wire as
  transverse reinforcement, ties, stirrups, spacing, anchorage, or substitution.

### 2.4 Conformity and certification requirements — the decisive section

Clause 11 provides exactly two acceptance routes:

> «صدور گواهی و بازرسی میلگرد تسلیح بصورت زیر انجام شود: الف- روش برنامه ریزی شده تحت نظارت شخص ثالث مطابق با استاندارد ISO 10144 / ب- روش آزمون محموله»

**(الف) Planned scheme under third-party supervision per ISO 10144** — i.e. conformity
is established by a *third-party certification scheme defined in another external
standard* (ISO 10144:1991), which is not in this repository, not supplied, and not
obtainable here.

**(ب) Consignment (lot) testing** — the consignment is divided into lots of **max 50 t**;
each lot has **all** mechanical properties determined; and acceptance is **statistical**:

- 15 specimens from the lot; lot acceptable only when `m₁₅ − 2.33 × s₁₅ ≥ f_k`
  (k = 2.33, n = 15, 1−α = 0.90, p = 0.95);
- if not satisfied and `K′ = (m₁₅ − f_k)/s₁₅ ≥ 2`, a further 45 specimens may be tested
  (n = 60) with `m₆₀ − 1.93 × s₆₀ > f_k`;
- qualitative rule: more than two non-conforming results of 15 → further sampling;
  more than two of 60 → lot rejected.

Additionally:

- **Producer/seller agreement escapes.** Clause 7-1 permits **Table 5 values** to be used
  as the accepted minima «در صورت توافق تولید کننده و خریدار»; Table 3 footnote 1 permits
  **A_gt** to replace A_5.65 «در صورت توافق فروشنده و خریدار». So some acceptance values
  are not unconditionally fixed by the standard.
- **Documentation:** clause 11-4 requires a producer's compliance report; clause 12
  requires a test report naming production method, identification marking, number of
  bundles, testing organization (where needed), test date, lot weight and results.

---

## 3. Internal discrepancy recorded (not resolved, not guessed)

Clause 4 states the nominal diameter shall be **between 4 and 16 mm** and that the
recommended nominal diameters are given in **«جدول شماره یک»** (Table 1). Table 1 is
titled «قطرهای توصیه شده و مقادیر جرم لازم» and lists **only 5, 6, 7, 8, 9, 10, 12 mm**.

Consequently **nominal areas, required masses and tolerances for 13, 14, 15 and 16 mm are
not established by the supplied print**, even though clauses 5-1/5-2 band up to 16 mm and
Tables 4/5 carry parenthesised 14/16 mm mandrels. **This is recorded as a print
inconsistency. It was not resolved by inference**, and it independently means the
standard does not fully define its own stated diameter range.

---

## 4. The dependency, re-examined

```
§9-21-6-2-3   (Mabhas 9, printed p. 446 — VERIFIED, H.13)
│   «… استفاده از سیم آجدار یا شبکهی آرماتور سیم جوش شده به عنوان جایگزین تنگ آجدار،
│     با سطح مقطع معادل میلگرد آجدار با در نظر گرفتن الزامات ۹-۲۱-۶-۲-۱ و ۹-۴-۸ مجاز است»
│
├─ (1) equal cross-sectional area ............................ DETERMINISTIC
│
├─ (2) §9-21-6-2-1 tie spacing
│        └→ BG-TRANS-TIE-SPACING-001 ........................ RESOLVED (executable)
│
└─ (3) §9-4-8   (verified H.14, printed pp. 66–69)
         ├─ -1  deformed mandatory; plain only in spirals .... DETERMINISTIC
         ├─ -3/-4  constitutive law; E_s = 200 000 MPa ....... already implemented
         ├─ -5  yield cap per Table 9-4-4 / 9-4-5 ............ DETERMINISTIC
         ├─ -6  type eligibility per Table 9-4-4 ............. AMBIGUOUS for mesh (§6.4)
         ├─ -7  conformity to ISIRI 11558
         │        └→ ISIRI 11558   [H.16: OBTAINED + VERIFIED]
         │              ├─ rating 500 MPa  ≠  420 MPa shear-tie row .... §6.2
         │              ├─ conformity = ISO 10144 3rd party OR 15/60-sample
         │              │  lot statistics on ≤50 t consignments ........ §6.1
         │              ├─ no welded-fabric normative content ......... §6.3
         │              └─ producer/buyer agreement escapes ........... §6.5
         ├─ -8  deformed-wire diameter window 1.5–16 mm ...... DETERMINISTIC
         └─ -9  longitudinal bars, special seismic systems ... out of scope for D
```

---

## 5. The ruling question

> Can BeamGenius determine, from **engineering inputs**, that a given deformed wire or
> welded mesh **conforms to ISIRI 11558** — and therefore satisfies §9-4-8-7 — so that the
> substitution of §9-21-6-2-3 may be declared admissible (PASS)?

**No.** Four independent reasons, each sufficient on its own.

### 5.1 Conformity is not an engineering-input proposition (category: `EXTERNAL_DEPENDENCY` + `INPUT_MODEL_GAP`)

ISIRI 11558 does not define conformity as a property a designer can evaluate. It defines
conformity as one of:

- **third-party certification under ISO 10144:1991** — an external certification scheme,
  itself an external standard unavailable here; or
- **statistical consignment testing**: `m₁₅ − 2.33 s₁₅ ≥ f_k` over 15 specimens from a
  ≤ 50-tonne lot, escalating to 60 specimens.

Neither can be modelled as a design input. The first is a certificate; the second is a
*lot-acceptance statistic* requiring 15–60 tested specimens, their mean, their standard
deviation and the lot's identity. There is no design-time datum — no nominal diameter,
no area, no yield value, no geometry — that establishes 11558 conformity. A rule that
accepted "conforms = true" as a caller-supplied boolean would be accepting an
**unverifiable assertion** as verification, which the project's governance forbids
(a registry reference is not proof of verification; VERIFY_PENDING never emits PASS).

### 5.2 Rating-scale mismatch (category: `INPUT_MODEL_GAP`)

Mabhas 9 §9-4-8-5 + Table 9-4-4 (verified, printed p. 68) cap the design yield of shear
**ties** at **420 MPa**, and the shear/tie row admits «همه ردههای آجدار».

ISIRI 11558's entire product line is rated at **`R_p0.2` = 500 N/mm²**. The standard
contains **no 420 MPa class and no class-selection clause**. Nothing in it tells a
designer which of its wires may be used where in a structure — that is a *design* code's
job, and Mabhas 9 does it via its own tables.

Therefore: even a perfectly conforming 11558 wire is a **500 MPa-class wire**, and
whether such a wire is admissible in a 420 MPa-capped tie application is **not answered
by 11558**. The standard cannot discharge this half of the question.

### 5.3 Welded fabric is outside the normative scope (category: `SCOPE_GAP` + `AMBIGUITY`)

§9-21-6-2-3 expressly permits «شبکهی آرماتور سیم جوش شده» (welded wire mesh). §9-4-8-7
requires welded meshes «ساخته شده از سیمهای ساده و آجدار» to conform to 11558.

But ISIRI 11558 contains **no welded-fabric requirement at all**: «جوش» appears only in
the title. The standard does not specify weld strength, mesh geometry, wire spacing,
mesh testing, mesh certification or mesh marking. It specifies **individual wires**, and
its title merely identifies welded fabric as an application of them.

Consequently, for the mesh branch:

- 11558 adds nothing beyond the individual-wire requirements (which are subject to
  §5.1 and §5.2 exactly as above); and
- the **Mabhas 9-internal ambiguity identified in H.14 §4.2 remains fully open**:
  §9-4-8-6 routes type eligibility to Table 9-4-4, whose shear/tie row carries no mesh
  permission, while footnote [۲] (welded **ribbed** mesh permitted) sits on the
  flexure/axial «سایر موارد» row.

The standard therefore **cannot** resolve the mesh question — and the brief explicitly
required that it not be used to do so.

### 5.4 Acceptance values are partly agreement-dependent (category: `AMBIGUITY`)

Clause 7-1 allows Table 5 values as accepted minima «در صورت توافق تولید کننده و
خریدار»; Table 3 footnote 1 allows `A_gt` in place of `A_5.65` «در صورت توافق فروشنده و
خریدار». An engine cannot represent "whatever the buyer and producer agreed", and a rule
built on Table 3 alone would silently assume the default branch. That is a
representation of an assumption the source does not authorise unconditionally.

### 5.5 Aggregate

| Question required for D | Answer after H.16 |
| :-- | :-- |
| Which wires are admissible? | Mabhas 9 side: deformed only (§9-4-8-1), 1.5–16 mm (§9-4-8-8). 11558 side: **not determinable** — conformity requires third-party certification or 15/60-sample lot testing; and the 500 MPa rating does not answer the 420 MPa-tie admissibility question |
| Which welded meshes are admissible? | **Not determinable** — 11558 has no fabric requirements; the Mabhas 9 Table 9-4-4 ambiguity stands |
| Are all conforming wires usable, or only some classes? | **Not determinable** — 11558 has a single 500 MPa class and no application mapping |
| Diameter limits? | Mabhas 9 gives 1.5–16 mm; 11558's Table 1 gives 5–12 mm with **no property/mass/tolerance values for 13–16 mm**, contradicting its own stated 4–16 mm range (§3) |
| Grade / f_y limits? | Mabhas 9 gives 420 MPa for shear ties; 11558 defines only 500 MPa — no bridge exists |
| Is mesh admissible at all, or only a specific type? | **AMBIGUOUS (Mabhas 9-internal)** |
| Extra requirements for the tie application? | Not defined by 11558 — it is silent on application |
| Is equivalence only A_s, or more? | More than A_s — §9-4-8 layers material conformity on top, but that layer is not evaluable (§5.1) |
| Additional spacing / welding / geometry / anchorage requirements? | Spacing via §9-21-6-2-1 (resolved). 11558 imposes **no** welding requirement. Anchorage is not part of §9-21-6-2-3 |

### 5.6 Dependency categories (as requested)

| Category | Applies? | Detail |
| :-- | :-- | :-- |
| `SOURCE_VERIFICATION` | **Resolved** | ISIRI 11558 obtained and visually verified in full (H.16). §9-4-8 verified in H.14 |
| `EXTERNAL_DEPENDENCY` | **YES — primary** | §9-4-8-7 conformity routes through **ISO 10144:1991** third-party certification (and ISO 10544:1992 as the origin standard); neither is available |
| `INPUT_MODEL_GAP` | **YES — primary** | Conformity is lot-statistical (m−2.33s over 15, or 60, specimens on a ≤50 t consignment) or certificate-based. No design input can carry it. Additionally the 500 MPa rating does not map onto the 420 MPa tie cap |
| `AMBIGUITY` | **YES — secondary** | Mesh-vs-tie admissibility (Mabhas 9 Table 9-4-4); producer/buyer agreement escapes in 11558 clauses 7-1 and Table 3 fn. 1; the 13–16 mm dimensional discrepancy in 11558 itself |
| `SCOPE_GAP` | **YES — secondary** | ISIRI 11558 contains no welded-fabric normative content |

---

## 6. Engineering decision

```text
KEEP BLOCKED
```

`BG-TRANS-WIRE-SUBST-PENDING`:

```text
status            = VERIFY_PENDING
execution_allowed = false
```

**Exact reason.** §9-21-6-2-3's conjunctive condition includes compliance with §9-4-8,
and §9-4-8-7 requires conformity to ISIRI 11558. ISIRI 11558 has now been read in full
and it defines conformity as either third-party certification under **ISO 10144:1991** or
**statistical acceptance of 15–60 tested specimens per ≤50-tonne consignment**. Neither
is representable by BeamGenius inputs, and the standard further rates its product only at
**500 MPa** while the Mabhas 9 shear-tie row caps design yield at **420 MPa**, with no
class-to-application mapping in the standard. Accordingly the conjunctive requirement
**cannot be evaluated deterministically**, and no branch — wire or mesh — may be made
executable. A rule covering only the deterministic parts (area equivalence, deformed-only,
1.5–16 mm, 420 MPa cap, spacing) would emit **PASS for material of unknown conformity**:
a false PASS, which is prohibited.

**No partial rule was created.** **No area-equivalence-only PASS path exists.** The
existing executable rule `BG-TRANS-TIE-SPACING-001` remains untouched and continues to
serve §9-21-6-2-1 independently.

### 6.1 Behavioural guarantee

| Situation | Engine behaviour |
| :-- | :-- |
| Any caller asks for a wire/mesh-for-tie substitution verdict | **BLOCKED** (rule is non-executable) |
| Any caller supplies partial data | **BLOCKED** |
| Conformity claimed by the caller | **cannot produce PASS** — no evaluator exists |
| Any other existing rule | unaffected |

---

## 7. Preserved governance

- A (`BG-TRANS-TIE-ANCHOR-PENDING`), B (`BG-TRANS-WIRE-TIE-PENDING`),
  C (`BG-TRANS-TORSION-TIE-PENDING`), E (`BG-TRANS-SPIRAL-SPLICE-SEL-PENDING`) — all
  unchanged, none reopened.
- The dependency does **not** reach §9-21-6-1-3(ب) or §9-21-6-1-5; A and B were not
  reintroduced into D.
- The four executable torsion routes, all hook/spacing/development-length/lap-splice
  rules: untouched.
- No ACI / CSA / Eurocode / ASTM / ISO substitution was made. ISO 10544:1992 and
  ISO 10144:1991 are recorded as the standard's own references — **citations of the
  source**, not substitutes for it, and neither was read.
- No UI / report / DXF / Excel / optimisation work. No engine code, evaluator, formula or
  test changed. No runtime file/PDF/OCR dependency added.
- `origin/main` untouched.

---

## 8. Validation

| Gate | Result |
| :-- | :-- |
| `PYTHONPATH=src pytest` | **673 passed** |
| `PYTHONPATH=src mypy --strict` | **clean — 23 source files** |
| Registry | **121 total / 63 executable / 48 blocked / 10 reference** — unchanged |
| Duplicate Rule IDs | **0** |
| §9-21-6 predicate | **21 executable / 5 blocked** — unchanged |
| `BG-TRANS-WIRE-SUBST-PENDING` | `execution_allowed=False`, `VERIFY_PENDING` — unchanged |
| PDF SHA-256 | `4c1c1a478ab8a39b6a19cabc63eac63afbaf2f31c4a7c3eaf55549c9d039916c` — unchanged after all work |
| `phase2f-source-948/` | contains **no** ISIRI 11558 PDF — restored to the §9-4-8 package only |
| `phase2f-source-11558/` | exactly `ISIRI-11558.pdf`, `README.md`, `VERIFICATION-NOTE.md` |
| `git diff --check` | clean |

---

## 9. What would be required to change this decision

The blocker is now **not** a missing document — the document is in hand and verified.
Unblocking requires a **project-level decision** that one of the following is acceptable
as BeamGenius's representation of §9-4-8-7:

1. **Certificate-based conformity** — accept a caller-supplied reference to an ISO 10144
   certification and document the rule as *executable but not self-verifying*; this
   requires an explicit governance decision because it cannot fail closed on false input.
2. **Lot-test-data-based conformity** — accept caller-supplied lot statistics
   (n, mean, s for the relevant property) and evaluate `m − 2.33s ≥ f_k` / `m − 1.93s > f_k`
   as a check on *data provided*, again executable-but-not-self-verifying.
3. **Explicit scope determination** that §9-4-8-7 product conformity is outside the
   engine's remit, recorded as such.

Additionally, **any** wire or mesh branch still requires resolution of:

4. the **500 MPa ↔ 420 MPa** mapping question (which 11558 wire class may serve a
   shear-tie application capped at 420 MPa by Mabhas 9 Table 9-4-4); and
5. the **mesh admissibility ambiguity** in Mabhas 9 Table 9-4-4 (§5.3).

Until at least (1), (2) or (3) is decided **and** (4)–(5) are resolved, the rule must
remain non-executable. Absence of an evaluable basis means **BLOCKED**.

---

*H.16 obtained and verified the external standard Mabhas 9 requires. The verification
shows the dependency is not a numeric gap that a document could fill, but a
product-conformity and certification question the engine cannot self-determine.
`BG-TRANS-WIRE-SUBST-PENDING` stays blocked, and no false PASS is possible.*
