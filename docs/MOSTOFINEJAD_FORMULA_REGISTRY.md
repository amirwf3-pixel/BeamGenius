# MOSTOFINEJAD_FORMULA_REGISTRY

**Project:** BeamGenius\
**Source:** Davood Mostofinejad, *Reinforced Concrete Structures*, Vol.
1\
**Purpose:** Source-verified formula registry for the BeamGenius
engineering calculation engine.

## Source Policy

-   Mostofinejad Vol. 1 = primary source for engineering methodology,
    formulas, calculation logic, and worked examples.
-   Mabhas 9 = governing Iranian code for mandatory requirements and
    compliance checks.
-   A formula here is not automatically an Iranian code rule.
-   Source-specific factors, limits, load combinations, and detailing
    requirements require Mabhas 9 reconciliation before becoming
    executable Iranian rules.
-   Unresolved equations must not be implemented.

## Status

-   `VERIFIED_SOURCE` --- visually verified against supplied
    Mostofinejad page images.
-   `UNRESOLVED` --- referenced/incomplete and not verified.
-   `CODE_REVIEW_REQUIRED` --- source formula verified, but Iranian-code
    applicability requires Mabhas 9 reconciliation.

------------------------------------------------------------------------

## BG-MOST-5-46

**Equation:** (5-46)\
**PDF page:** 211 \| **Printed page:** 200\
**Status:** `VERIFIED_SOURCE` \| **Category:** `METHODOLOGY`

\[ k_n=f'\_c`\omega`{=tex}(1-0.59`\omega`{=tex}) \]

Where:

-   (k_n): flexural resistance factor, MPa
-   (f'\_c): concrete compressive strength, MPa
-   (`\omega`{=tex}): mechanical reinforcement ratio
-   (`\omega`{=tex}=ho f_y/f'\_c)

**Context:** Calculates the nominal flexural capacity coefficient for a
rectangular section.

------------------------------------------------------------------------

## BG-MOST-5-47

**Equation:** (5-47)\
**PDF page:** 211 \| **Printed page:** 200\
**Status:** `VERIFIED_SOURCE` \| **Category:** `METHODOLOGY`

\[ bd\^2=rac{M_n}{k_n}=rac{M_u}{`\phi `{=tex}k_n} \]

Where (b,d) are section width/effective depth, (M_n,M_u) are
nominal/factored moments, and (`\phi`{=tex}) is the strength reduction
factor.

**Context:** Determines the section-size parameter (bd\^2).

------------------------------------------------------------------------

## BG-MOST-5-48A

**Equation:** (5-48-a)\
**PDF page:** 211 \| **Printed page:** 200\
**Status:** `VERIFIED_SOURCE` \| **Category:** `PRACTICAL_ESTIMATION`

\[ dpprox h-65 ext{ mm} \]

**Context:** Practical estimate for one layer of tension reinforcement.

**Implementation:** Initial estimate only; final (d) must be
recalculated from actual detailing.

------------------------------------------------------------------------

## BG-MOST-5-48B

**Equation:** (5-48-b)\
**PDF page:** 211 \| **Printed page:** 200\
**Status:** `VERIFIED_SOURCE` \| **Category:** `PRACTICAL_ESTIMATION`

\[ dpprox h-90 ext{ mm} \]

**Context:** Practical estimate for two layers of tension reinforcement.

**Implementation:** Initial estimate only; final (d) must be
recalculated from actual detailing.

------------------------------------------------------------------------

## BG-MOST-5-49

**Equation:** (5-49)\
**PDF page:** 218 \| **Printed page:** 207\
**Status:** `VERIFIED_SOURCE` \| **Category:** `CSA_LSD_METHODOLOGY`

\[ lpha_1=0.85-0.0015f'\_c`\ge0.67`{=tex} \]

**Context:** CSA A23.3-14 equivalent rectangular stress-block parameter.

**Restriction:** Not an Iranian code rule.

------------------------------------------------------------------------

## BG-MOST-5-50

**Equation:** (5-50)\
**PDF page:** 218 \| **Printed page:** 207\
**Status:** `VERIFIED_SOURCE` \| **Category:** `CSA_LSD_METHODOLOGY`

\[ eta_1=0.97-0.0025f'\_c`\ge0.67`{=tex} \]

**Context:** CSA A23.3-14 equivalent rectangular stress-block parameter.

**Restriction:** Not an Iranian code rule.

------------------------------------------------------------------------

## BG-MOST-5-51

**Equation:** (5-51)\
**PDF page:** 218 \| **Printed page:** 207\
**Status:** `VERIFIED_SOURCE` \| **Category:** `CSA_LSD_METHODOLOGY`\
**Review flag:** `SOURCE_NOTE_REQUIRES_REVIEW`

\[
c_b=rac{`\epsilon`{=tex}*{cu}}{`\epsilon`{=tex}*{cu}+`\epsilon`{=tex}\_y}d
=rac{700}{700+f_y}d \]

**Context:** Balanced-condition neutral-axis depth.

**Review note:** The supplied verification reports the source's
(700/(700+f_y)) form while also describing
(`\epsilon`{=tex}\_{cu}=0.003). The origin of the numerical factor 700
should be checked against the surrounding source text before independent
implementation.

------------------------------------------------------------------------

## BG-MOST-5-52

**Equation:** (5-52)\
**PDF page:** 218 \| **Printed page:** 207\
**Status:** `VERIFIED_SOURCE` \| **Category:** `CSA_LSD_METHODOLOGY`

\[ A\_{sb}=lpha_1eta_1bd rac{`\phi`{=tex}\_c}{`\phi`{=tex}\_s}
rac{f'\_c}{f_y} rac{700}{700+f_y} \]

Reported source factors:

-   (`\phi`{=tex}\_c=0.65) for precast
-   (`\phi`{=tex}\_c=0.70) for cast-in-place
-   (`\phi`{=tex}\_s=0.85)

**Restriction:** These are source-methodology values, not Mabhas 9
rules.

------------------------------------------------------------------------

## BG-MOST-5-53

**Equation:** (5-53)\
**PDF page:** 218 \| **Printed page:** 207\
**Status:** `VERIFIED_SOURCE` \| **Category:** `CSA_LSD_METHODOLOGY`

\[ ho_b=lpha_1eta_1 rac{`\phi`{=tex}\_c}{`\phi`{=tex}\_s}
rac{f'\_c}{f_y} rac{700}{700+f_y} \]

**Context:** Balanced reinforcement ratio. The supplied source
verification describes (ho\<ho_b) as tension-controlled and (ho\>ho_b)
as compression-controlled.

------------------------------------------------------------------------

## BG-MOST-5-54

**Equation:** (5-54)\
**PDF page:** 219 \| **Printed page:** 208\
**Status:** `VERIFIED_SOURCE` \| **Category:** `CSA_LSD_METHODOLOGY`

\[ a=rac{A_s`\phi`{=tex}\_s f_y}{lpha_1`\phi`{=tex}\_c f'\_c b} \]

**Context:** Stress-block depth for the source's tension-controlled
path.

------------------------------------------------------------------------

## BG-MOST-5-55

**Equation:** (5-55)\
**PDF page:** 219 \| **Printed page:** 208\
**Status:** `VERIFIED_SOURCE` \| **Category:** `CSA_LSD_METHODOLOGY`

\[ M_r=Tz=A_s`\phi`{=tex}\_s f_y`\left`{=tex}(d-rac a2ight) \]

**Context:** Resisting moment for the source's tension-controlled path.

------------------------------------------------------------------------

## BG-MOST-5-56

**Equation:** (5-56)\
**PDF page:** 219 \| **Printed page:** 208\
**Status:** `VERIFIED_SOURCE` \| **Category:** `CSA_LSD_METHODOLOGY`

\[ M_r=ho`\phi`{=tex}\_s f_ybd\^2 `\left`{=tex}(1-rac{ho`\phi`{=tex}\_s
f_y}{2lpha_1`\phi`{=tex}\_cf'\_c}ight) \]

**Context:** Alternative form of Eq. (5-55) using reinforcement ratio.

------------------------------------------------------------------------

## BG-MOST-5-57

**Equation:** (5-57)\
**PDF page:** 219 \| **Printed page:** 208\
**Status:** `VERIFIED_SOURCE` \| **Category:** `CSA_LSD_METHODOLOGY`

\[ a\^2+ rac{700`\phi`{=tex}\_sho}{lpha_1`\phi`{=tex}\_cf'\_c}d,a
-rac{700`\phi`{=tex}\_sho}{lpha_1`\phi`{=tex}\_cf'\_c}eta_1d\^2=0 \]

**Context:** Quadratic formulation for the source's
over-reinforced/compression-controlled path.

------------------------------------------------------------------------

## BG-MOST-5-58

**Equation:** (5-58)\
**PDF page:** 220 \| **Printed page:** 209\
**Status:** `VERIFIED_SOURCE` \| **Category:** `CSA_LSD_METHODOLOGY`

\[ lpha=rac{700`\phi`{=tex}\_sho d}{lpha_1`\phi`{=tex}\_cf'\_c} \]

**Context:** Temporary variable used to solve Eq. (5-57).

------------------------------------------------------------------------

## BG-MOST-5-59

**Equation:** (5-59)\
**PDF page:** 220 \| **Printed page:** 209\
**Status:** `VERIFIED_SOURCE` \| **Category:** `CSA_LSD_METHODOLOGY`

\[ a=rac12`\left`{=tex}(`\sqrt{lpha^2+4eta_1dlpha}`{=tex}-lphaight) \]

**Context:** Positive solution of the quadratic in Eq. (5-57).

------------------------------------------------------------------------

## BG-MOST-5-60

**Equation:** (5-60)\
**PDF page:** 220 \| **Printed page:** 209\
**Status:** `VERIFIED_SOURCE` \| **Category:** `CSA_LSD_METHODOLOGY`

\[ M_r=lpha_1`\phi`{=tex}\_cf'\_c ab`\left`{=tex}(d-rac a2ight) \]

**Context:** Resisting moment for the source's
over-reinforced/compression-controlled path.

------------------------------------------------------------------------

## BG-MOST-5-61

**Equation:** (5-61)\
**PDF page:** 220 \| **Printed page:** 209\
**Status:** `VERIFIED_SOURCE` \| **Category:** `DESIGN_CHECK`

\[ M_f`\le `{=tex}M_r \]

**Context:** Source limit-state flexural resistance check.

**Restriction:** The final Iranian-code resistance framework must come
from Mabhas 9.

------------------------------------------------------------------------

## BG-MOST-5-62

**Equation:** (5-62)\
**PDF page:** 220 \| **Printed page:** 209\
**Status:** `VERIFIED_SOURCE` \| **Category:** `CSA_LSD_METHODOLOGY`

\[ M_f=1.25M_D+1.5M_L`\ge`{=tex}1.4M_D \]

**Restriction:** Record as source methodology only. Do not hard-code as
an Iranian load combination.

------------------------------------------------------------------------

# Unresolved Equations

## Equation (5-44)

**Referenced:** PDF 211 / printed 200\
**Status:** `UNRESOLVED`

The equation itself is not visible in the supplied pages.

**Implementation:** prohibited until the source page containing the
equation is verified.

## Equation (5-45)

**Referenced:** PDF 211 / printed 200\
**Status:** `UNRESOLVED`

The equation itself is not visible in the supplied pages.

**Implementation:** prohibited until the source page containing the
equation is verified.

------------------------------------------------------------------------

# Registry Classification

  ------------------------------------------------------------------------
  ID                                 Eq. Category         BeamGenius use
  ---------------- --------------------- ---------------- ----------------
  BG-MOST-5-46                      5-46 Methodology      Source formula

  BG-MOST-5-47                      5-47 Methodology      Source formula

  BG-MOST-5-48A                   5-48-a Practical        Initial
                                         estimation       dimensioning
                                                          heuristic

  BG-MOST-5-48B                   5-48-b Practical        Initial
                                         estimation       dimensioning
                                                          heuristic

  BG-MOST-5-49                      5-49 CSA LSD          Separate
                                                          methodology only

  BG-MOST-5-50                      5-50 CSA LSD          Separate
                                                          methodology only

  BG-MOST-5-51                      5-51 CSA LSD          Review required

  BG-MOST-5-52                      5-52 CSA LSD          Separate
                                                          methodology only

  BG-MOST-5-53                      5-53 CSA LSD          Separate
                                                          methodology only

  BG-MOST-5-54                      5-54 CSA LSD          Separate
                                                          methodology only

  BG-MOST-5-55                      5-55 CSA LSD          Separate
                                                          methodology only

  BG-MOST-5-56                      5-56 CSA LSD          Separate
                                                          methodology only

  BG-MOST-5-57                      5-57 CSA LSD          Separate
                                                          methodology only

  BG-MOST-5-58                      5-58 CSA LSD          Separate
                                                          methodology only

  BG-MOST-5-59                      5-59 CSA LSD          Separate
                                                          methodology only

  BG-MOST-5-60                      5-60 CSA LSD          Separate
                                                          methodology only

  BG-MOST-5-61                      5-61 Design check     Methodology only

  BG-MOST-5-62                      5-62 CSA LSD          Not as Iranian
                                                          load combination
  ------------------------------------------------------------------------

------------------------------------------------------------------------

# Validation References

## Example 5-5

**PDF pages:** 212--213 \| **Printed:** 201--202

-   (b=400) mm
-   (h=500) mm
-   (M_u=240) kN·m
-   (f'\_c=35) MPa
-   (f_y=400) MPa
-   single reinforcement layer
-   source estimate (d=435) mm
-   reported (A_spprox1636) mm²
-   reported selection: (2`\Phi25`{=tex}+1`\Phi30`{=tex}pprox1689) mm²
-   reported alternative: (3`\Phi28`{=tex}pprox1847) mm²

Use as a regression/reference case for the Mostofinejad flexural
methodology.

## Example 5-6

**PDF pages:** 213--216 \| **Printed:** 202--205

-   (l=6.0) m
-   (DL=40) kN/m excluding self-weight
-   (LL=22) kN/m
-   (f'\_c=28) MPa
-   (f_y=350) MPa
-   refined (q_g=5.04) kN/m
-   refined (q_u=89.25) kN/m
-   refined (M\_{max}=401.6) kN·m
-   refined (A_s=2659) mm²
-   reported selection: (4`\Phi30`{=tex}=2827) mm²

Alternative case:

-   (b=300) mm
-   (h=550) mm
-   (d=485) mm
-   (A_spprox3056) mm²
-   (4`\Phi32`{=tex}=3217) mm²: reported spacing failure
-   (3`\Phi36`{=tex}=3054) mm²: reported spacing acceptance

Use as a regression/reference case for iterative section sizing and
reinforcement selection.

------------------------------------------------------------------------

# Explicit Non-Implementation List

Do not treat the following as finalized Iranian BeamGenius rules from
this registry alone:

1.  Equations (5-44) and (5-45)
2.  CSA A23.3-specific parameters in Equations (5-49)--(5-60)
3.  Source-specific (`\phi`{=tex}) factors
4.  Equation (5-62) load combination
5.  Source-specific reinforcement limits
6.  Source-specific cover/detailing requirements
7.  Practical heuristics as mandatory constraints
8.  Chapter 7 shear equations (7-21-a through 7-36) prior to visual source-page verification and Mabhas 9 reconciliation

------------------------------------------------------------------------

# Chapter 7 Shear Methodology Candidates (Pending Source-Page Verification & Mabhas 9 Reconciliation)

The following Mostofinejad Vol. 1 Chapter 7 equations have been identified for Phase 2 investigation. None of these equations may be copied into `src/beamgenius/engine/shear_mabhas9.py` or executed in production (`MABHAS_9_COMPLIANCE`). Even in `src/beamgenius/reference/`, each equation remains `UNRESOLVED` / `CODE_REVIEW_REQUIRED` until its exact Chapter 7 PDF page, printed page, and symbolic formula are visually verified against the Mostofinejad Vol. 1 source pages.

| Registry ID | Source Equation | Chapter | Status | Permitted Use |
| :--- | :--- | :--- | :--- | :--- |
| `BG-MOST-7-21A` | Eq. (7-21-a) | Ch. 7 (Shear) | `UNRESOLVED` / `CODE_REVIEW_REQUIRED` | Blocked pending visual source page verification & Mabhas 9 reconciliation |
| `BG-MOST-7-21B` | Eq. (7-21-b) | Ch. 7 (Shear) | `UNRESOLVED` / `CODE_REVIEW_REQUIRED` | Blocked pending visual source page verification & Mabhas 9 reconciliation |
| `BG-MOST-7-21C` | Eq. (7-21-c) | Ch. 7 (Shear) | `UNRESOLVED` / `CODE_REVIEW_REQUIRED` | Blocked pending visual source page verification & Mabhas 9 reconciliation |
| `BG-MOST-7-22` | Eq. (7-22) | Ch. 7 (Shear) | `UNRESOLVED` / `CODE_REVIEW_REQUIRED` | Blocked pending visual source page verification & Mabhas 9 reconciliation |
| `BG-MOST-7-23` | Eq. (7-23) | Ch. 7 (Shear) | `UNRESOLVED` / `CODE_REVIEW_REQUIRED` | Blocked pending visual source page verification & Mabhas 9 reconciliation |
| `BG-MOST-7-24` | Eq. (7-24) | Ch. 7 (Shear) | `UNRESOLVED` / `CODE_REVIEW_REQUIRED` | Blocked pending visual source page verification & Mabhas 9 reconciliation |
| `BG-MOST-7-25` | Eq. (7-25) | Ch. 7 (Shear) | `UNRESOLVED` / `CODE_REVIEW_REQUIRED` | Blocked pending visual source page verification & Mabhas 9 reconciliation |
| `BG-MOST-7-26` | Eq. (7-26) | Ch. 7 (Shear) | `UNRESOLVED` / `CODE_REVIEW_REQUIRED` | Blocked pending visual source page verification & Mabhas 9 reconciliation |
| `BG-MOST-7-27` | Eq. (7-27) | Ch. 7 (Shear) | `UNRESOLVED` / `CODE_REVIEW_REQUIRED` | Blocked pending visual source page verification & Mabhas 9 reconciliation |
| `BG-MOST-7-28` | Eq. (7-28) | Ch. 7 (Shear) | `UNRESOLVED` / `CODE_REVIEW_REQUIRED` | Blocked pending visual source page verification & Mabhas 9 reconciliation |
| `BG-MOST-7-29` | Eq. (7-29) | Ch. 7 (Shear) | `UNRESOLVED` / `CODE_REVIEW_REQUIRED` | Blocked pending visual source page verification & Mabhas 9 reconciliation |
| `BG-MOST-7-30` | Eq. (7-30) | Ch. 7 (Shear) | `UNRESOLVED` / `CODE_REVIEW_REQUIRED` | Blocked pending visual source page verification & Mabhas 9 reconciliation |
| `BG-MOST-7-31` | Eq. (7-31) | Ch. 7 (Shear) | `UNRESOLVED` / `CODE_REVIEW_REQUIRED` | Blocked pending visual source page verification & Mabhas 9 reconciliation |
| `BG-MOST-7-32` | Eq. (7-32) | Ch. 7 (Shear) | `UNRESOLVED` / `CODE_REVIEW_REQUIRED` | Blocked pending visual source page verification & Mabhas 9 reconciliation |
| `BG-MOST-7-33` | Eq. (7-33) | Ch. 7 (Shear) | `UNRESOLVED` / `CODE_REVIEW_REQUIRED` | Blocked pending visual source page verification & Mabhas 9 reconciliation |
| `BG-MOST-7-34` | Eq. (7-34) | Ch. 7 (Shear) | `UNRESOLVED` / `CODE_REVIEW_REQUIRED` | Blocked pending visual source page verification & Mabhas 9 reconciliation |
| `BG-MOST-7-35` | Eq. (7-35) | Ch. 7 (Shear) | `UNRESOLVED` / `CODE_REVIEW_REQUIRED` | Blocked pending visual source page verification & Mabhas 9 reconciliation |
| `BG-MOST-7-36` | Eq. (7-36) | Ch. 7 (Shear) | `UNRESOLVED` / `CODE_REVIEW_REQUIRED` | Blocked pending visual source page verification & Mabhas 9 reconciliation |

------------------------------------------------------------------------

# Integration Architecture

``` text
Mostofinejad Formula Registry
          ↓
Methodology Layer
          ↓
Engineering Calculation Engine
          ↓
Mabhas 9 Code Constraints
          ↓
Constructability / Detailing
          ↓
Feasible Design
```

A formula becomes an executable Iranian design rule only after the
required Mabhas 9 reconciliation and verification record has been
completed.
