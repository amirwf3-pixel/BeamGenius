# H.24.1 Source / Evidence Recovery Audit

**BeamGenius — access / provenance recovery audit for the H.24 source targets**

**Audit type: RECOVERY / PROVENANCE ONLY — no implementation, no promotion, no status change,
no H.22 reopen, no new engineering assumption, no external acquisition.**

---

## 1. Baseline

| Item | Value |
| :-- | :-- |
| Branch | `arena/b9cd291a-beamgenius` |
| HEAD at audit entry | **`f22ff45`** (stale-boot artifact, 8th occurrence) |
| Recovery applied | `git fetch origin --prune` → `git reset --mixed origin/arena/b9cd291a-beamgenius` → `git checkout HEAD -- .` (non-destructive; no `--hard`, no amend, no rebase, no force-push) |
| HEAD after recovery | **`8813be6`** (H.24 complete) |
| H.24 entry baseline (spec) | `9cf67f4` — **a verified ancestor of current HEAD** (`9cf67f4 → be0c310 → 8813be6`) |
| `origin/main` | **`df8067a750ffc7984c9dc5d80220ad9013503aa6`** — untouched |
| Working tree | clean (tracked) |
| Remote refs (4) | `HEAD` → `df8067a` · `refs/heads/main` → `df8067a` · `refs/heads/arena/b9cd291a-beamgenius` → `8813be6` · `refs/heads/arena/01a0fdd7-beamgenius` → `f22ff45` |
| Tags / stashes | none / none |
| Registry | 121 total / 63 executable / 48 blocked / 10 reference — unchanged; §9-21-6 21/5; duplicate IDs 0 |

> **Note on the spec baseline.** The stage brief specifies `9cf67f4`. That is the H.24 *entry*
> point; H.24 itself produced `be0c310` + `8813be6`, and the stage was completed and pushed.
> No reset was performed to `9cf67f4`, because doing so would discard completed, pushed stage
> work. `9cf67f4` is confirmed an ancestor of `8813be6`.

### 1.1 Environment-state recovery performed (disclosed)

While establishing the baseline, the clone was found to be **shallow** (§4.1). A
non-destructive **`git fetch --unshallow origin`** was executed to make the *complete* project
history searchable. Effects, stated exhaustively:

| Aspect | Effect |
| :-- | :-- |
| Commits available | 35 → **59** |
| Objects available | 352 → **563** |
| `.git` size | 9.3 MB → **9.6 MB** |
| `.git/shallow` | **removed** (clone is no longer shallow) |
| Branches moved | **none** |
| Commits created/rewritten/deleted | **none** |
| Remote written to | **none** |
| `origin/main` | **untouched** |

This is a local read-only deepening of the existing remote's own history. It is the enabling
step for the entire audit and is itself a finding: **H.24 could not see 24 of the project's
59 commits.**

---

## 2. H.24 Assumption Being Audited

H.24 recorded, in `docs/PHASE2G_H24_FLEXURAL_AS_SOURCE_VERIFICATION.md` §3:

> "the only source artifacts in this environment are `phase2f-source-11558/ISIRI-11558.pdf` …
> `phase2f-source-948/` … and `origin/main`'s `phase2f-source-442-472/` window."

and

> "The repository's own source PDF (`references/mabhas9/source/…ATNasr…pdf`, a **Windows path**
> named in the matrix) | **NO — never committed; a different machine**"

The stage brief asserts H.24 "incorrectly concluded that the required Mabhas 9 and Mostofinejad
source material was absent from the environment", and that "the project previously had the
original scanned/image-based PDFs and their OCR/extracted/evidence artifacts".

**This audit tests both propositions separately**, because they are not the same claim:

- **Claim 1 (existence):** the sources existed and were used in earlier stages.
- **Claim 2 (recoverability):** they can be recovered from the repository/history without user
  intervention.

---

## 3. Current Tree Search

Complete search of the present tree — not only `src/` and `docs/`.

| Search | Command / scope | Result |
| :-- | :-- | :-- |
| Every tracked path | `git ls-files` | 8 files under `phase2f-source-11558/` + `phase2f-source-948/`; **no** `references/`, `ocr/`, `extracted/`, `verification/`, `working/` |
| Any `*.pdf` | filesystem-wide `find / -iname "*.pdf"` | **exactly one**: `phase2f-source-11558/ISIRI-11558.pdf` |
| Mabhas / Mostofinejad names | `find` `*mabhas*`, `*mostofinejad*`, `*مبحث*`, `*مستوفی*` | **no source files** — only code/doc filenames |
| Source directories | `find` for `references`, `ocr`, `extracted`, `verification`, `working` | **none exist anywhere on the filesystem** |
| Other clones / repos | `find / -name .git -type d` | **exactly one**: `/home/user/BeamGenius/.git` |
| Attachment / upload / session storage | `find` for `*attach*`, `*upload*`, `Unselected*`, `*session*`; `ls /home/user /mnt /media /opt /srv` | **none** — `/home/user` contains only `BeamGenius`; no `.arena`, no `/home/user/uploads/` |
| Manifests | `phase2f-source-*/README.md`, `VERIFICATION-NOTE.md`, `.gitignore`, `.gitattributes`, `README.md` | present; **no `.gitattributes`, no LFS** |

**Result: the current tree holds three committed evidence items and nothing else.** The
`references/`, `ocr/`, `extracted/`, `verification/`, `working/` trees — which the documentation
treats as the location of the working source material — have **never been checked out here and
do not exist on this filesystem**.

---

## 4. Git History Search

### 4.1 Blocking discovery — the clone was shallow

```
.git/shallow (before recovery):
  df8067a750ffc7984c9dc5d80220ad9013503aa6
  f22ff45a0638bb48b08eaed49306bc8fcabcc691
```

Both boundary commits **record parents that were not present locally**:

| Shallow commit | Recorded parent | Parent present locally (pre-fetch)? |
| :-- | :-- | :-- |
| `f22ff45` (feat(detailing): … development length rules) | `024c9d62f5110ae552cb5d3385e999fd68301b6a` | **NO** |
| `df8067a` (chore: add temporary Phase 2F source evidence pages 442-472) | `07f2ba1924828d2485f378cff813827d68bacd9e` | **NO** |

Consequently `git log --all`, `git rev-list --all`, `git rev-list --objects --all`, and any
`git log --all --name-status` search executed **before** the unshallow fetch could only ever
traverse **35 of 59 commits** — silently, with no error. Every history-based conclusion drawn
in H.24 was drawn inside that truncated window.

After `git fetch --unshallow origin`: **59 commits**, `47329eb` (2026-10-01, *Initial commit*)
through `8813be6`, covering the project's entire lifetime.

### 4.2 Complete history searches (post-recovery)

| Search | Result |
| :-- | :-- |
| `git log --all --diff-filter=A --name-only` for `*.pdf *.jpg *.jpeg *.png *.tif *.tiff *.txt *.bmp *.webp` | **3 add-commits only** (§7) |
| All unique paths ever added, full history | 152 paths — every one is source code, tests, docs, or the three evidence packages |
| `git log --all --diff-filter=D` (deletions) | **1 deletion**, unrelated: `tests/test_mabhas9_detailing_phase2e.py` (`c1400a4`). **No evidence file was ever deleted.** |
| `git log --all --diff-filter=R` (renames) | **2 renames**, byte-identical (`R100`): the §9-4-8 PNGs into `phase2f-source-948/` (`3e34d0c`); the ISIRI PDF into `phase2f-source-11558/` (`f7176f3`) |
| `git fsck --lost-found --dangling` | **completely empty** — no dangling commit, tree, or blob, before *and* after unshallow |
| All blobs > 200 kB | 30 blobs, **all** are `phase2f-source-442-472` JPGs (341–485 kB each) |
| Object counts | `count: 52 · in-pack: 544 · packs: 3 · size-pack: 9177 kB` |

**There is no deleted-file recovery path, because no evidence file was ever added and then
removed, and the object database contains no unreachable objects.**

### 4.3 Source-material-specific history searches

| Pattern searched across every commit | Finding |
| :-- | :-- |
| `Mabhas9-v5.0-1399-ATNasr.ir.pdf` | **46 references** — all in documentation, naming the **user's Windows path** `D:\BeamGenius\references\mabhas9\source\Mabhas9-v5.0-1399-ATNasr.ir.pdf`. **Never a committed object.** |
| `BeamGenIus-H13-Mabhas9-9-4-8-evidence.pdf` | 63 references — all recording that the announced file **did not arrive** (`PHASE2F_STAGE_H13_SOURCE_EVIDENCE.md`: "Is `BeamGenIus-H13-Mabhas9-9-4-8-evidence.pdf` present? **NO**"). |
| `civil808.com/…/m9-chenges.pdf` | 17 references — an **external web URL** cited in `PHASE2F_STAGE_H15_INSO_11558.md` as "Mabhas 9 (1399) change-log document". Not a repository artifact. |
| `RULE_BG_DETAIL_BUNDLE_001.pdf` | 37 references — a **test-fixture string** (`tests/test_mabhas9_detailing_bundle.py:129`), not a file. |
| Any `Mostofinejad*.pdf` / Mostofinejad source filename | **ZERO.** The Mostofinejad source document is **never named anywhere in the entire history.** |
| `D:\…` Windows paths | 2 distinct: `D:\BeamGenius\references\mabhas9\source\Mabhas9-v5.0-1399-ATNasr.ir.pdf` and `D:\BeamGenius\project\docs\DESIGN_RULES.md` |

---

## 5. Branch / Remote Search

| Ref | Tip | Contains any Mabhas 9 flexure or Mostofinejad source? |
| :-- | :-- | :-- |
| `refs/heads/arena/b9cd291a-beamgenius` (checked out) | `8813be6` | **NO** |
| `refs/heads/main` (local) | `df8067a` | **NO** |
| `refs/heads/main` (origin) | `df8067a` | **NO** |
| **`refs/heads/arena/01a0fdd7-beamgenius`** (origin, previously unlisted) | `f22ff45` | **NO** — at the same commit our branch started from; no unique objects |
| `origin/HEAD` | `df8067a` | **NO** |
| Tags | none exist | — |
| Stashes | none exist | — |
| Reachability | `df8067a` is **not** an ancestor of HEAD; `143ea2f`, `3e34d0c`, `a385d88`, `f7176f3` **are** ancestors of HEAD | — |

`df8067a` carries the `phase2f-source-442-472/` window (PDF 442–472) and is reachable read-only
via `git show origin/main:phase2f-source-442-472/page-NNN.jpg`. It is **not** tracked on our
branch (`git ls-files | grep 442-472` → 0).

**No branch, tag, or remote ref anywhere holds the target pages.**

---

## 6. Ignore / Tracking Analysis

| Mechanism | Finding |
| :-- | :-- |
| `.gitignore` | **Exactly one version in all history** — added `5198190` (*chore: add project gitignore*, **2026-10-02**, day 2 of the project) and **never modified since**. Contents (5 lines): `references/`, `ocr/`, `extracted/`, `verification/`, `working/` |
| `.git/info/exclude` | default template only — no project rules |
| `.gitattributes` | **absent** |
| Git LFS | **absent** — no filter, no tracked pointer files anywhere |
| Repository policy | the `.gitignore` **is** the policy: the working source tree was deliberately kept out of Git from day 2 |

**Mandatory distinction (per brief), applied:**

| State | Verdict for the H.24 target material |
| :-- | :-- |
| Not currently checked out | **no** — the paths do not exist at all |
| Never existed in Git | **YES** — confirmed by full-history all-paths enumeration + `fsck` |
| Exists only in local environment | **no** — confirmed by filesystem-wide search |
| Exists in Git history | **no** |
| Exists in another branch | **no** |

The `.gitignore` explains the mechanism precisely: `references/` (the source PDF root),
`ocr/`, `extracted/`, `verification/`, and `working/` (the per-stage crop directories such as
`working/h19`…`working/h22`) were **intentionally excluded from Git**. Source material was
therefore **local-only by design**, and any part of it not re-committed as a
`phase2f-source-*` evidence package was lost when the originating session ended.

---

## 7. Previously Used Evidence

Complete inventory of every source artifact **ever committed** to this repository.

### 7.1 `phase2f-source-442-472/`

| Field | Value |
| :-- | :-- |
| **PATH** | `phase2f-source-442-472/page-442.{jpg,txt}` … `page-472.{jpg,txt}` (31 + 31 = 62 files) |
| **COMMIT** | `df8067a` — *chore: add temporary Phase 2F source evidence pages 442-472* |
| **BRANCH** | `origin/main` only (**not** on `arena/b9cd291a-beamgenius`) |
| **TYPE** | page-image scans (`.jpg`) + Persian OCR text (`.txt`) |
| **SOURCE** | Mabhas 9 (1399, 5th ed., ATNasr PDF) |
| **PAGES** | PDF **442–472** = printed **422–452** (footers verified: 460→۴۴۰, 465→۴۴۵, 468→۴۴۸, 469→۴۴۹, 471→۴۵۱, 472→۴۵۲) |
| **OCR / IMAGE / PDF** | image **and** OCR |
| **CURRENTLY ACCESSIBLE** | **YES** — read-only via `git show origin/main:phase2f-source-442-472/page-NNN.jpg` |
| **PREVIOUSLY USED BY** | H.11–H.22 (§9-21-6 / §9-21-4 verification) |
| **CHECKSUM** | not recorded upstream; computed this audit — `page-442.jpg` `67258e54fcf428258e4db661eb580ae763fc82f07e682abd880636e34d212928`; `page-462.jpg` `8874cb49ba5dacc8db8c1526d9b260dd0b80aa35800570f91b30798d3d19ed7c`; `page-472.jpg` `957e68825c3d579fd9d7a850dbcf4dad7536fdaa1544989629b7d00c74530b88` |

### 7.2 `phase2f-source-948/`

| Field | Value |
| :-- | :-- |
| **PATH** | `phase2f-source-948/README.md`, `p086_printed066.png`, `p087_printed067.png`, `p088_printed068.png`, `p089_printed069.png` |
| **COMMIT** | added `143ea2f` (*Add files via upload*, 2026-10-07); relocated to package by `3e34d0c` (`R100`) |
| **BRANCH** | `arena/b9cd291a-beamgenius` (ancestor of HEAD) |
| **TYPE** | page-image captures (`.png`) + identity README |
| **SOURCE** | Mabhas 9, 1399, 5th edition |
| **PAGES** | PDF **86–89** = printed **66–69** (offset **+20**), §9-4-7/§9-4-8 |
| **OCR / IMAGE / PDF** | **image only** — README states "These are evidence images only; no OCR or reconstructed text is included" |
| **CURRENTLY ACCESSIBLE** | **YES** |
| **PREVIOUSLY USED BY** | H.14 (blocker D source dependency) |
| **CHECKSUM** | `p086` `42740749ee41d456b22342c2ff36849e59d73d654cef6df84b648ebb42e84c93` · `p087` `a484810d8e50da13b5e8e4f33174656d18be3636833a9fcda1b2af5e788bdfda` · `p088` `fddebd0552344858437670811d1d7bb63895a3ef340295548c803a17cf708b6b` · `p089` `e2e7fe3e08d8a71b4be8cb6989db19c6bd88e0d4767e57ad55284bd0023d11c3` |

### 7.3 `phase2f-source-11558/`

| Field | Value |
| :-- | :-- |
| **PATH** | `phase2f-source-11558/ISIRI-11558.pdf`, `README.md`, `VERIFICATION-NOTE.md` |
| **COMMIT** | added `a385d88` (*Add files via upload*); relocated by `f7176f3` (`R100`) |
| **BRANCH** | `arena/b9cd291a-beamgenius` |
| **TYPE** | original source **PDF** (19 pages) + identity/integrity README + verification note |
| **SOURCE** | ISIRI 11558, 1st edition (1387) |
| **PAGES** | 19 |
| **OCR / IMAGE / PDF** | **PDF** (authoritative original, byte-for-byte) |
| **CURRENTLY ACCESSIBLE** | **YES** |
| **PREVIOUSLY USED BY** | H.15, H.16 (external dependency of §9-4-8-7) |
| **CHECKSUM** | **recorded AND re-verified this audit** — SHA-256 `4c1c1a478ab8a39b6a19cabc63eac63afbaf2f31c4a7c3eaf55549c9d039916c` (matches `README.md`) |

### 7.4 Evidence that does **not** exist

| Artifact | Status |
| :-- | :-- |
| OCR text of any Mabhas 9 page outside PDF 442–472 | **does not exist** — the only `.txt` OCR in the repository is the 442–472 set |
| OCR text of any Mostofinejad page | **does not exist** |
| Any page image of Mabhas 9 printed 107–114, 132, 199 | **does not exist** |
| Any page image of Mostofinejad printed 200–205 | **does not exist** |
| The full `Mabhas9-v5.0-1399-ATNasr.ir.pdf` | **does not exist in this environment** |

---

## 8. Mabhas 9 Target Recovery

### 8.1 Recorded mapping for the H.24 targets (from `docs/PHASE2_SOURCE_VERIFICATION_MATRIX.md`)

| Rule | Clauses | Recorded PDF pp. | Recorded printed pp. | Implied offset |
| :-- | :-- | :-- | :-- | :-- |
| `BG-FLEX-PHI-FACTOR` | `9-7-4-1`..`9-7-4-4`, Table `9-7-2`, Eqs. `(9-7-10-الف/ب)` | 16–18 | 107–109 | **−91** |
| `BG-FLEX-STRAIN-LIMIT` | `9-8-2-2-2`, `9-8-2-2-3`, `9-7-4-2`, `9-11-2-3` | 16–18, 22, 41 | 107–109, 113, 132 | **−91** |
| `BG-FLEX-STRESS-BLOCK` | `9-8-2-2-6`, `9-8-2-2-7`, `(9-8-2)`, `(9-8-3-الف)`, `(9-8-3-ب)`, `(9-8-4)` | 22–23 | 113–114 | **−91** |
| `BG-FLEX-RECT-SINGLY-001` | `9-8-1-4` Eq. `(9-8-1-الف)`, `9-8-2-1-1`, `9-8-2-2-1`..`9-8-2-2-8`, `9-11-2-3` | 16–18, 21–23, 41 | 107–109, 112–114, 132 | **−91** |
| `BG-FLEX-TBEAM-B-EFF-001` | `9-6-3-3-1`, Table `9-6-1`, `9-6-3-3-2`, `9-11-2-5` | 12–13, 41 | 103–104, 132 | **−91** |
| `BG-FLEX-MIN-001` | `9-11-5-1-1`, `9-11-5-1-2`, `9-11-5-1-3` | 220 | 199 | **+21** |

### 8.2 Two mutually exclusive page attributions for the same printed pages — **recorded, not resolved**

The `−91` block (all of Phase 2B) and the `+21` attribution (`BG-FLEX-MIN-001`, Phase 1) cannot
both describe one continuous document. Cross-checks against the independently footer-verified
packages give:

| Evidence set | Offset |
| :-- | :-- |
| `phase2f-source-948/` (PDF 86–89 ↔ printed 66–69) | **+20** |
| Phase 2E cover captures (PDF 92–93 ↔ printed 71–72, recorded as "+21 edition-wide") | +21 |
| `BG-FLEX-MIN-001` (PDF 220 ↔ printed 199) | +21 |
| `phase2f-source-442-472/` (footer-verified, PDF 442–472 ↔ printed 422–452) | **+20** |
| Phase 2F corrigendum commit `024c9d6` (*PDF-offset corrigenda (+21→+20)*) | +20 |
| Phase 2B flexure set | **−91** |

The `+20`/`+21` pair is a one-page drift that the project already corrected once. The **`−91`
flexure attribution is of a different order entirely** and is inconsistent with every
footer-verified package — i.e. the Phase 2B flexure verification was performed against a
**rendition whose pagination differs from the ATNasr PDF**, or the attribution is erroneous.

Per the stage brief, **no offset is guessed and no attribution is "fixed" here.** The recovery
target remains the **printed** pages, with any PDF mapping to be re-established by footer
inspection on the acquired document.

### 8.3 Recovery result — Mabhas 9

| Question | Answer |
| :-- | :-- |
| Is the full Mabhas 9 source PDF in this environment? | **NO** |
| Is it recoverable from any branch/history/ref? | **NO** — never committed (full-history enumeration + `fsck` prove it) |
| Do committed page images exist for printed 107–114, 132, 199? | **NO** |
| Does committed OCR exist for those pages? | **NO** |
| Is the *engineering content* for those pages recoverable from the repo? | **YES** — clause/equation inventory in the matrix §3/§4 and `VERIFIED_RULES.md`; the executable implementations of the resistance model and `BG-FLEX-MIN-001` are in the engine |
| Is that sufficient for H.24's visual-verification gate? | **NO** — recorded text is not visual evidence |

---

## 9. Mostofinejad Target Recovery

| Question | Answer |
| :-- | :-- |
| Is any Mostofinejad source file in this environment? | **NO** |
| Is a Mostofinejad source filename recorded anywhere in history? | **NO — zero occurrences.** The document's identity is recorded only bibliographically: *Davood Mostofinejad, "Reinforced Concrete Structures", Vol. 1* |
| Are Mostofinejad page images committed? | **NO** |
| Is Mostofinejad OCR committed? | **NO** |
| How was Mostofinejad previously verified? | `MOSTOFINEJAD_FORMULA_REGISTRY.md` states `VERIFIED_SOURCE` = "visually verified against **supplied** Mostofinejad page images" — i.e. **in-session user-supplied captures, never committed** |
| What is recorded for the H.24 targets? | (5-46) and (5-47) on **PDF p. 211 / printed p. 200** (offset **+11**); Examples 5-5 & 5-6 on **PDF pp. 212–216 / printed pp. 201–205** |
| Is the *engineering methodology* recoverable from the repo? | **YES** — `docs/MOSTOFINEJAD_FORMULA_REGISTRY.md` (BG-MOST-5-46 … 5-62), `src/beamgenius/reference/mostofinejad_ch5.py` (`evaluate_mostofinejad_eq_5_46_kn`, `evaluate_mostofinejad_eq_5_47_bd2`, `solve_required_as`), `tests/test_reference_mostofinejad_examples.py` |
| Is that sufficient for H.24's visual-verification gate? | **NO** |

---

## 10. Provenance Chain

```
[NEVER IN GIT — user's own machine]
   D:\BeamGenius\references\mabhas9\source\Mabhas9-v5.0-1399-ATNasr.ir.pdf
   D:\BeamGenius\references\...\{ocr,extracted,verification,working}\
        │   (46 documented references; .gitignore'd from 2026-10-02, commit 5198190)
        │
        │   delivery = in-session user-supplied page captures
        │   (announced sandbox paths such as /home/user/uploads/ —
        │    H.13 recorded that this path did NOT exist)
        ▼
[VISUAL INSPECTION BY THE STAGE]
   renders/crops under working/h7 … working/h22   (git-ignored, ephemeral, GONE)
        │
        │   only when a stage chose to commit a package:
        ▼
[COMMITTED — the only surviving evidence]
   143ea2f ──► phase2f-source-948/         PDF 86–89   = printed 66–69   (image only)
   a385d88 ──► phase2f-source-11558/       ISIRI 11558 PDF, 19 pp.        (original PDF)
   df8067a ──► phase2f-source-442-472/     PDF 442–472 = printed 422–452  (image + OCR)
                    └── on origin/main only

[NOT DELIVERED / NOT COMMITTED]
   BeamGenIus-H13-Mabhas9-9-4-8-evidence.pdf  (announced; H.13: "present? NO")
   Mabhas 9 printed 107–114, 132, 199         (no package ever created)
   Mostofinejad printed 200–205               (no package ever created)
```

**Why the target pages have no package:** the flexure verification was **Phase 2B, 2026-10-02**
(commits `d1c6bab`, `0e503d8`) — six days *before* `phase2f-source-948` (`143ea2f`,
2026-10-07), i.e. **before the evidence-package convention existed**. The earliest committed
page-image package is `df8067a` (2026-10-05). Phase 2B's evidence was inspected live and never
committed; the session that held it has ended.

---

## 11. H.24 Correction

The stage brief's premise is tested on its two separable claims.

| Claim | Verdict |
| :-- | :-- |
| "H.24 incorrectly concluded that the required source material was **absent from the environment**" | **NOT SUPPORTED.** H.24's conclusion is **confirmed correct** — re-verified after recovering the complete history. The material is absent and is not recoverable from the repository. |
| "The project previously had the original scanned/image-based PDFs and their OCR/extracted/evidence artifacts" | **SUPPORTED, with a precise scope.** The project *used* the original sources (from the user's Windows tree, via in-session captures). But they were **never in Git** — by explicit `.gitignore` design — and the OCR/extracted artifacts existed only for PDF 442–472 (committed) and locally/ephemerally elsewhere (gone). |

**What H.24 genuinely got wrong — method, not conclusion** (§8 of the brief → answer **B, partially correct**):

1. **Shallow-clone blindness (material).** H.24 searched "all branches" and "the entire
   history" without detecting `.git/shallow`. It therefore walked 35 of 59 commits and could not
   distinguish *"never committed"* from *"not fetched"*. This is the one defect that made the
   negative finding **unprovable** as H.24 stated it.
2. **No all-paths-ever enumeration.** H.24 did not run `git rev-list --objects --all` or
   `git fsck`, the two commands that actually establish "never existed in Git".
3. **Under-reported provenance.** H.24 called the missing source "a Windows path named in the
   matrix". The repository records its **exact identity in 46 places**:
   `D:\BeamGenius\references\mabhas9\source\Mabhas9-v5.0-1399-ATNasr.ir.pdf`. H.24 should have
   named it, and should have named the Mostofinejad source as *never recorded at all*.
4. **Missed a fourth ref.** `refs/heads/arena/01a0fdd7-beamgenius` was not enumerated (it holds
   no unique objects, so the conclusion is unaffected).
5. **Missed `phase2f-source-948`'s README offset datum** (PDF 86–89 ↔ printed 66–69 = **+20**),
   a fourth independent offset lineage.

**What H.24 got right and this audit preserves:** the absence of the target pages; the
non-committal of the source PDFs; the `0.59` vs `α₀(f'c)` model-divergence finding; the
existence and jurisdiction-limiting of `solve_required_as`; and the refusal to manufacture
evidence.

**Corrected statement for the record:**

> The H.24 target pages (Mabhas 9 printed 107–114, 132, 199; Mostofinejad printed 200–205) are
> **absent from this environment and were never committed to this repository** — proven against
> the complete 59-commit history, all 4 remote refs, all 563 objects, and a filesystem-wide
> search. Their original location is the user's Windows tree
> `D:\BeamGenius\references\mabhas9\source\Mabhas9-v5.0-1399-ATNasr.ir.pdf` (Mabhas 9) and an
> unnamed local copy of Mostofinejad Vol. 1. They cannot be recovered without user-supplied
> page captures.

---

## 12. Recovery Case

| Case | Definition | Applies? |
| :-- | :-- | :-- |
| **A** | Original source PDF accessible in current tree | **NO** |
| **B** | Original source PDF exists in Git history / another branch, recoverable without external acquisition | **NO** — never committed; `fsck` clean; no branch holds it |
| **C** | PDF not in Git, but the exact previously generated OCR/evidence package is accessible and contains sufficient page-image evidence for visual verification | **NO for the targets** — three packages exist and are accessible, but **none covers printed 107–114, 132, 199 or printed 200–205** |
| **D** | Only OCR text exists; no visual evidence | **NO** — visual evidence exists for *other* pages; for the targets, neither OCR nor image exists |
| **E** | Neither source nor adequate evidence exists in the repository/history | **YES — for the H.24 target material** |

### **RECOVERY CASE: E**

with the qualification that the repository is **not** empty of evidence — it holds three
independent, checksum-verified evidence packages covering §9-4-8, §9-21-6 and ISIRI 11558. The
failure is specific and bounded: **the two page-ranges H.24 needs were never packaged.**

**No recovery action was performed on the repository** (nothing to restore, and §11 of the
brief forbids structural improvisation). The unshallow fetch (§1.1) is the only environment
change; it altered no branch, no commit and no remote.

---

## 13. Recommended Next Action

**Action 1 — required (one artifact set).**
Supply page-image captures of **Mabhas 9 (1399, 5th ed., ATNasr PDF) printed pp. 107–114, 132,
199** (companion range: **Mostofinejad Vol. 1 printed pp. 200–205**), as a committed
`phase2f-source-*` evidence package built to the existing convention
(`phase2f-source-948/README.md` pattern: identity note + page images, printed-page filenames,
no reconstruction). On arrival, run the H.24 gate again — gates 1–7 should then be resolvable.

> This is a *deliberate* request, not a reflex one: the entire tree, complete history, all
> remote refs, all objects, and every existing evidence package have now been searched
> (§§3–9). There is no existing OCR and no existing image for these pages to re-use.

**Action 2 — replace the acquisition target by *printed* page, not PDF page.**
Do not request, and do not trust, any PDF page number for the flexural substrate until footers
are read on the delivered document: the repository currently records **−91** for the Phase 2B
flexure set and **+21** for `BG-FLEX-MIN-001` for the same printed pages (§8.2).

**Action 3 — standing environment hygiene (prevents recurrence).**
Any future stage that must search history should first run:

```
git rev-parse --is-shallow-repository        # must print: false
git fetch --unshallow origin                 # if it prints true
git fsck --dangling                          # expect empty
git rev-list --objects --all | wc -l         # expect 563
```

Recorded here because the shallow clone silently truncated 41 % of this project's history and
H.24 reported "searched all history" on that basis.

**Not part of this stage** (unchanged): the §9-21-5-6 citation defect, the
`rebar/catalog.py` rationale defect, the five frozen H.22 blockers, bundle integration, rebar
selection, end-to-end orchestration, and any implementation of `BG-FLEX-RECT-REQ-AS-001`.
`BG-FLEX-RECT-REQ-AS-001` remains **not registered**, `VERIFY_PENDING`, `execution_allowed=False`.

---

## Appendix — Recovery-command reference

| Purpose | Command |
| :-- | :-- |
| Read the 442–472 evidence (no checkout needed) | `git show origin/main:phase2f-source-442-472/page-462.jpg > /tmp/p462.jpg` |
| Recover the H.24 stage work if booted stale | `git fetch origin && git reset --mixed origin/arena/b9cd291a-beamgenius && git checkout HEAD -- .` |
| Detect shallow truncation | `git rev-parse --is-shallow-repository` |
| Prove "never existed in Git" | `git rev-list --objects --all`, `git fsck --dangling`, `git count-objects -v` |
| Verify ISIRI 11558 integrity | `sha256sum phase2f-source-11558/ISIRI-11558.pdf` → `4c1c1a47…d039916c` |
```
