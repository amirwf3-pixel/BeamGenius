# ISIRI 11558 — Source Evidence

Authoritative source document retained for BeamGenius engineering source verification.

## Standard identity

| Field | Value |
| :-- | :-- |
| Standard number | **ISIRI 11558** (Iranian National Standard No. 11558) |
| Designation on cover | «استاندارد ملی ایران ۱۱۵۵۸» / "ISIRI 11558" |
| Persian title | «میلگردهای سرد نوردیده مورد مصرف جهت تسلیح بتن و ساخت شبکه های جوش شده - ویژگی ها» |
| English title (as printed on the cover) | "Cold-reduced steel wire for the reinforcement of concrete and the manufacture of welded fabric" |
| Edition | **1st edition** — cover reads "1st. edition" / «چاپ اول» |
| Issuing body | مؤسسه استاندارد و تحقیقات صنعتی ایران — Institute of Standards and Industrial Research of Iran (ISIRI) |
| ICS classification | ICS: 91.080.40 ; 77.140.15 |
| Reference source (printed in the foreword) | ISO 10544:1992, *Cold reduced steel wire for the reinforcement of concrete and the manufacture of welded fabric* |

## Approval information available in the document

The foreword (پیش‌گفتار) records that the standard:

- was prepared and drafted by the relevant technical commission of the Institute;
- was **approved at the 419th meeting of the National Standards Committee for Mechanics and Metallurgy** (کمیتهٔ ملی استاندارد مکانیک و فلزشناسی);
- is dated **۱۳۸۷/۱۲/۲۴** (24 Esfand 1387, Persian calendar);
- is published as a National Standard of Iran pursuant to Clause 3, paragraph 1 of the Law amending the rules and regulations of the Institute (approved Bahman 1371).

The document carries no separate amendment or revision history beyond the 1st edition; the foreword is the standard ISIRI boilerplate stating that national standards are revised as needed and that the latest revision should always be used.

## Purpose

This package exists solely as **source evidence for BeamGenius verification** of the external dependency imposed by **Mabhas 9 (1399, 5th ed.) §9-4-8-7**:

> «سیم‌های ساده و آجدار و شبکه‌های جوشی ساخته شده از سیم‌های ساده و آجدار باید مطابق استاندارد ملی ایران به شماره ۱۱۵۵۸ باشند.»

which in turn is invoked by **§9-21-6-2-3** (wire / welded-mesh substitute for a deformed tie) — the dependency of the blocked rule `BG-TRANS-WIRE-SUBST-PENDING`.

This is an **authoritative source supplied for source verification**. It is the governing external document only because Mabhas 9 explicitly cites it. It is not a substitute for Mabhas 9, and nothing outside this document may be substituted for it.

## File integrity

| Field | Value |
| :-- | :-- |
| File | `ISIRI-11558.pdf` |
| Size | 251,461 bytes |
| Page count | **19** |
| PDF version | 1.4 |
| SHA-256 | `4c1c1a478ab8a39b6a19cabc63eac63afbaf2f31c4a7c3eaf55549c9d039916c` |

The PDF is retained as the **exact original source**, moved byte-for-byte into this directory (git records it as a 100 % rename). It must not be re-encoded, re-saved, redacted or regenerated.

## Governance notes

- **The PDF remains the authoritative source.** No OCR output, extracted text, transcription or reconstructed wording is a substitute for the PDF, and none may be used as the basis of a verification determination.
- Text extraction from this file is used for **navigation and search only**; every requirement relied upon must be confirmed by **visual inspection** of the page image.
- The document is a copyrighted national standard retained in a private repository strictly for engineering source verification of the dependency Mabhas 9 imposes.

## Document map (1st edition)

| Section | Subject | Printed page |
| :-- | :-- | :-- |
| 1 | هدف و دامنه کاربرد — Scope and field of application | 1 |
| 2 | مراجع الزامی — Normative references | 1 |
| 3 | اصطلاحات و تعاریف — Terms and definitions | 1 |
| 4 | جدول قطرهای توصیه شده و مقادیر جرم لازم — Recommended diameters and masses | 3 |
| 5 | شکل — Example: ribbed wire with three rows of ribs | 3 |
| 6 | ابعاد، مقادیر جرم و رواداریها — Dimensions, mass and tolerances | 5 |
| 7 | هندسه میلگردهای شیاردار و آجدار — Geometry of indented/ribbed wires | 5 |
| 8 | شکل — Example: indented wire with three rows of indentations | 6 |
| 9 | جدول ترکیب شیمیایی — Chemical composition table | 6 |
| 10 | جدول مقاومت مشخصه — Characteristic strength table | 6 |
| 11 | ترکیب شیمیایی — Chemical composition | 7 |
| 12 | جداول قطر فک مورد استفاده در آزمون‌های خمش و بازخمش — Mandrel diameters for bend/rebend tests | 8 |
| 13 | مشخصات مکانیکی — Mechanical properties | 8 |
| 14 | آزمون خواص مکانیکی — Mechanical property testing | 9 |
| 15 | شناسه گذاری — Identification marking | 9 |
| 16 | نشانه گذاری — Marking | 10 |
| 17 | صدور گواهینامه و بازرسی — Certification and inspection | 10 |
| 18 | گزارش نتایج آزمون — Test result reporting | 12 |
| 19 | پیوست الف (اطلاعاتی) — Annex A (informative) | 13 |

**Package contents checked:** the delivered PDF contains exactly the numbered pages 1–۱۳; the foreword is printed on page «ز» (the PDF's 6th sheet), which follows the TOC sheet «و» — the «ز» designation appearing in the table of contents corresponds to that foreword sheet, not to a missing content page.

## Related repository evidence

| Path | Contents |
| :-- | :-- |
| `phase2f-source-948/` | Mabhas 9 §9-4-8 evidence pages (PDF 86–89 / printed 66–69) — **unrelated package, unchanged** |
| `phase2f-source-948/README.md` | Identity note for the §9-4-8 evidence set |
