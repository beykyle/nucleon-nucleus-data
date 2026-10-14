# Notes from EXFOR: the uncorrected corpus records against their EXFOR entries

A summary of [exfor_crosscheck_generated.md](exfor_crosscheck_generated.md), which `scripts/exfor_crosscheck.py`
generated from the corpus records *as curated before the author-uncertainty corrections*
([../docs/AUTHOR_UNCERTAINTIES.md](../docs/AUTHOR_UNCERTAINTIES.md)). It covers the 37 EXFOR entries of
[INDEX.md](INDEX.md): every entry with at least one point resting only on a reader/digitisation uncertainty.
The corrections apply to the evaluated corpora only; the static KDUQ, CHUQ and Test keep the records described
here.

Source: the local X4 database (release X4-2025-12-31), the same entries the IAEA EXFOR website shows. The website
itself sits behind a browser challenge and can't be fetched from scripts, so the DOIs were reproduced from each
entry's REFERENCE codes through Crossref instead.

## 1. Bibliography and DOIs

- **All 31 entries whose REFERENCE code resolves to a DOI agree with [INDEX.md](INDEX.md).** Each DOI was accepted
  only when the Crossref journal title, volume and first page matched the EXFOR code. APS DOIs were constructed and
  checked.
- **No DOI from the REFERENCE code:**
  - F1173 (Izv. Akad. Nauk SSSR; English translation listed by EXFOR as (J,BAS,36,1956,1973)) and O0083 (J. Phys.
    Soc. Jpn. Suppl. 44, conference proceedings) have none.
  - The code lookup misses the four J. Phys. G entries O0169, O1103, O1104 and O1109; INDEX's verified DOIs stand.
- **Additional sources EXFOR lists:**
  - O0169: a thesis (T,WASSENAAR,1982);
  - O0580: preliminary reports (C,82KIEV; J,IZV,48,145; C,84ALMAAT; J,IZV,50,157) and an analysis (J,UFZ,32,815);
  - O1199: a companion paper (J,PR/C,21,844,1980), with data for O-18, N-15, C-12 and Ar-40 (entry O1198);
  - F1173: the English translation (Bull. Acad. Sci. USSR Phys. Ser. 36, 1956 (1973)).

## 2. What the uncorrected corpus used

- **The corpus reproduced EXFOR exactly.** For every record of these entries, the per-point uncertainty equals one
  EXFOR column, or two in quadrature, at 100 % of points. The one exception, F0733003 (90Zr(p,p) 25.05 MeV, sm3), is
  intentionally the authors' 3 % from ERR-ANALYS. The reader-only uncertainties therefore came from EXFOR's columns,
  not from a curation error.
- **Digitised curves dominate.** 135 of the 142 subentries are STATUS (CURVE), i.e. read off published figures by
  the EXFOR compilers; 7 are TABLE. Their only per-point uncertainty is often the compilers' data-point reader
  error (0.4–7 %), sometimes alongside author errors where the bars were legible.

## 3. EXFOR relabelled columns between releases (2019–2023)

Several entries were relabelled, and some re-digitised, by the compilers ("SD:" HISTORY records):
- `DATA-ERR → ERR-DIG` and `ANG-ERR → ANG-ERR-D` (reader uncertainty made explicit): O0079 (2022-10-25),
  O0083 (2019-05-07), O0091 (2022-10-26), O0246/O0253 (2022–2023), O0300 (2023-04-07), O0328 (2023-04-24), and
  others listed in the generated file.
- **Author errors moved with them:**
  - **O0328 (Fricke, 2023-04-24): `ERR-T → ERR-1`, and the data were re-digitised.** ERR-1 is "statistical errors
    and the uncertainty in background subtraction" (001 ERR-ANALYS), the authors' per-point error. The supplement's
    preference rule does not rank `ERR-1`, so every record built from the 2025 database took `ERR-DIG` (0.4 %)
    instead.
  - O0091 (2022-10-26): `ERR-T → DATA-ERR` for at least one subentry.
- **Consequence:** which column means "author" and which "reader" depends on the EXFOR release. The supplement's
  rule (ERR-T > DATA-ERR > ERR-S > ERR-DIG) was written against older releases, where `DATA-ERR` was often the
  *reader* uncertainty. The corrections therefore classify columns from each subentry's ERR-ANALYS text
  (`nn_corpora.author_errors.classify`), not from the label.

## 4. Specific records

- **O0178 (Doering (p,n), all 12 sets).**
  - `DATA-ERR` (7 %) is "Data-Point Reader Uncertainty", `ERR-T` is "reported by authors", and the data are
    digitised from Fig. 3.
  - The corpus used DATA-ERR ⊕ ERR-T, which is reader-only wherever ERR-T is blank: forward angles, 73.8°/75.8°, and
    161.9°/164.0° at 208Pb 45 MeV.
  - The three 25 MeV sets (48Ca, 90Zr, 120Sn) have no ERR-T at all.
  - Normalisation 10 % (`ERR-1`; `ERR-2` to `ERR-4` are its components).
- **O0328 (Fricke):** see §3.
- **F0733 (Van der Bijl):** only `ERR-DIG` in EXFOR; `sm3` uses the authors' 3 % from ERR-ANALYS.
- **Whole-set reader-only entries** (no author column at all): O0124, O0157, O0225, O0239, O0254, O0259, O0272,
  O0370, O0372, O0384, O0387, O0458, O0471, O0545, O0549, O1199; those held only by `kduq` (O0079, O0083, O0300,
  O0446, O0456, O0553) or `chuq` (O1103, O1104, O1109); and some subentries of O0169 and O0091. Their uncertainties can only come from
  the publications.
