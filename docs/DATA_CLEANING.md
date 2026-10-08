# Data cleaning: no data point may rest on reader (digitisation) uncertainty alone

Living document. Edit in place across sessions: status checklist, decisions and open questions at the end.
Branch: `reader-errors`. Started 2026-10-08. Paper worklist: `papers/INDEX.md` (PDFs are never committed: this is
a public repo).

## Context
- **Trigger.** The 208Pb 45 MeV (p,n) set (Doering, O0178015) decides the 208Pb model comparison (Phase 0). Its last
  two points (161.9°, 164.0°) carry only EXFOR's 7 % "data-point reader uncertainty" (DATA-ERR), because the authors'
  error (ERR-T) is blank there. They pull 9–11σ.
- **Audit** (`elm/sm3/paper/phase0/audit_reader_errors.py` for now, moving to `scripts/` in step 4; all 4 corpora, every record auditable):
  - 37 EXFOR entries have points whose only error is reader or digitisation uncertainty;
  - sm3: all 12 Doering (p,n) sets and Fricke 120Sn(p,p) 40 MeV (0.4 %!);
  - ELM: 78 records;
  - KDUQ and CHUQ: elastic and analyzing powers (CHUQ has no (p,n), as the audit confirms).
  - Two kinds:
    - **partial:** author errors exist for some points of a set;
    - **whole-set:** EXFOR carries no author errors, typically curves digitised without bars.
- **Goal.** Every point carries an author-based uncertainty (reported, interpolated by a fixed rule, or taken from the
  original publication). Reader/digitisation uncertainty is added in quadrature, never used alone. The corpora are
  rebuilt, and a test enforces this from now on. This blocks Phase 1 of `sm3/paper/CAMPAIGN.md` (Gate A, Q1).

## Decisions (Kyle, 2026-10-08)
1. **Partial sets, fill rule.** Author relative errors missing at a point are filled as follows; the total error is
   then author ⊕ reader in quadrature.
   - interior gaps: linear interpolation in angle between the nearest points with author errors;
   - backward (low cross section) end: the max of the last two author relative errors, and ≥ 100 %;
   - forward (high cross section) end, blank because the bar is smaller than the symbol: keep the reader value as
     an upper bound.
2. **Doering normalisation stays 10 %.** ERR-1 is the authors' estimate of the absolute-scale uncertainty; ERR-2 to
   ERR-4 are its components.
3. **Scope:** all corpora (elm, kduq, chuq, sm3). CHUQ has no (p,n), so it only gets elastic/Ay fixes.
4. **Papers:** I read what is openly accessible. Kyle supplies the rest (list below).

## Sources found so far
- **Doering thesis, open access:** R. R. Doering, MSU PhD 1974, https://d.lib.msu.edu/etd/18018 (PDF
  `/etd/18018/OBJ/download`, 10.7 MB; doi:10.25335/8r9s-9621).
  - Its Table 5 tabulates the angular distributions with errors.
  - It goes into the paper library for reference only: per Kyle, Doering is treated like any partial record and is
    not re-digitised. EXFOR's O0178 is digitised from Fig. 3 (STATUS CURVE).
- APS / Elsevier / JPSJ / J. Phys. G / Phys. Lett. papers are paywalled from here (APS abstract only).

## Steps

### 0. Living document and branch (done)
- This file and the `reader-errors` branch. Nothing is pushed without approval.

### 1. Paper list first, then stop and wait for Kyle's compilation
- **Deliverable:** `nucleon_nucleus_data/papers/INDEX.md`, the committed list of every source publication behind the
  audited records (the 37 entries plus the Doering thesis). Per entry:
  - citation;
  - **DOI link** (resolved through the Crossref API, checked to point at the right paper);
  - EXFOR entry link (https://www-nds.iaea.org/EXFOR/<entry>);
  - corpora and records using it; partial or whole-set; priority (sm3 > ELM > KDUQ/CHUQ-only);
  - open-access link where one exists (Doering thesis: https://d.lib.msu.edu/etd/18018);
  - a status column (PDF present / extracted / value used).
- `.gitignore`: `papers/*.pdf`, `papers/**/*.pdf`. **The repo is public, so copyrighted PDFs are never committed.**
  Only the index is tracked.
- **Then stop.** Kyle assembles a PDF manuscript compilation and places it in `nucleon_nucleus_data` (location as he
  chooses, git-ignored). Steps 2–5 start only after that, except step 2's partial-set fill rule, which needs no
  papers. Whether to start it before the compilation arrives is Kyle's call.

### 2. Partial sets: the fill rule in the curation pipeline
- **New module `nn_corpora/author_errors.py`:**
  - `classify(entry, subentry, labels)`: reader vs author vs common-systematic columns from the ERR-ANALYS text of the
    subentry and of subentry 001 (logic from `audit_reader_errors.py`: "reader|reading|digiti[sz]" or ERR-DIG);
  - `fill_missing(angles, author_rel, reader_rel)`: decision 1's rule, returning per-point total relative errors
    and a provenance tag (reported / interpolated / backward-extrapolated / forward-reader-bound).
- **Hook it into the pipelines after parsing, before `finalize`:**
  - `elm_curate.py` (next to `apply_uncertainty_patches`, reusing its note/`result.repaired` pattern);
  - the KDUQ/CHUQ builder (`corpus.py`).
- It applies to every record with partial reader-only points:
  - **all 12 Doering O0178 sets, treated like any other partial record** (no re-digitisation);
  - O0328 (Fricke, 6 subentries), the O0169 and O0091 partials, O0211, F1173, O0382, O0552, O0580.
  The per-point provenance goes into the record's notes.
- **Doering's three whole-set records** (25 MeV on 48Ca, 90Zr and 120Sn: O0178008, O0178011, O0178014) have no
  ERR-T at any point, so the fill rule has nothing to interpolate from. Their author errors come from the thesis
  Table 5 (open access; errors only, values stay EXFOR's), as for any whole-set record (step 3).
- **For Doering's partial records this gives:**
  - forward points stay at the 7 % reader bound;
  - 73.8°/75.8° (208Pb 45 MeV) get interpolated author errors;
  - 161.9°/164.0° get ≥ 100 % (max(220 %, 90 %) = 220 %).

### 3. Whole-set reader-only entries: author-stated uncertainties from the papers
- **New registry `AUTHOR_UNCERTAINTIES` in `nn_corpora/author_errors.py`:** subentry → relative or absolute
  per-point error (or a by-angle table), with a citation (page/table/figure/sentence). Applied like
  `UncertaintyPatch`, but as author ⊕ reader.
- **Extraction from each paper, in order of preference:**
  1. a tabulated error;
  2. a quoted relative/statistical error in the text;
  3. error bars read from the figure (noted as such).
- **If a paper gives nothing:** a documented default (open question Q2), flagged `author-unknown`.
- **Priority:**
  - ELM entries (they enter the ELM rebuild);
  - KDUQ/CHUQ-only entries afterwards (Ay errors are absolute).

### 4. Enforcement, rebuild, diff
- Move the audit into the repo as `scripts/audit_reader_errors.py`, and add `tests/test_reader_errors.py`: every
  record in every corpus has an author-based error at every point, unless whitelisted with a reason.
- Rebuild `data/elm`, `data/kduq`, `data/chuq`, `data/sm3` and the manifests, with a diff report: per record, how
  many points changed and the old → new relative errors.
- Run the repo tests. Commit on the branch; merge/push after Kyle's review.

### 5. Downstream
- **sm3:** the corpus changes, so every sm3 calibration must be rebuilt. Re-verify solver settings (data errors don't
  change the settings, but problems are rebuilt).
- **Phase 0 check:** rerun 208Pb lane and locw (balanced) on the new corpus. Does the +9.7 locw preference survive?
  Re-run `loo_screen.py`.
- **Records:** update `CAMPAIGN.md` (Gate A Q1 closed, decision log) and HIGHLIGHTS (data-cleaning note).
- **ELM:** the 2×2 and ELM rebuild inherit the cleaned corpus.

## Open questions (to resolve in DATA_CLEANING.md)
- **Q1.** ~~Doering: thesis tabulation or fill?~~ Fill, like any partial record (Kyle, 2026-10-08).
- **Q2.** Default for whole-set entries whose paper states no uncertainty (dσ/dΩ: e.g. 5 % relative; Ay: e.g. 0.03
  absolute), or read the bars off the figures?
- **Q3.** Whitelisting: any records we knowingly leave on reader errors (e.g. tiny contribution) with a reason?
- **Q4.** ~~Public or private repo?~~ Public: PDFs are git-ignored; only `papers/INDEX.md` is committed (Kyle,
  2026-10-08).

## Verification
- `tests/test_reader_errors.py` passes on all rebuilt corpora: no point without an author-based error unless
  whitelisted.
- Unit tests for `fill_missing` (interior interpolation, backward ≥ 100 %, forward reader bound) and for `classify`
  on O0178, O0328 and F0733.
- Diff report reviewed. The 208Pb 45 MeV record (O0178015) has 161.9° and 164.0° at ≥ 100 % error.
- `papers/INDEX.md` lists every audited entry with a working DOI link. `git status` shows no PDF tracked.
- After the rebuild: rerun the sm3 208Pb lane/locw pair and `loo_screen.py`.

## Status

- [x] Step 0: living document, branch `reader-errors`.
- [x] Step 1: `papers/INDEX.md` (37 entries: 35 DOIs verified through Crossref, 2 without DOI), `.gitignore` for
      PDFs.
- [x] EXFOR cross-check: `scripts/exfor_crosscheck.py` → `papers/exfor_crosscheck_generated.md`, summary in `papers/notes_from_exfor.md`. DOIs agree; the corpus reproduces EXFOR; O0328's 2023 relabel (ERR-T → ERR-1) is why Fricke falls back to 0.4 %.
- [x] Kyle's PDF compilation received (33 PDFs, renamed by entry; Doering thesis downloaded). O0157's file is the wrong paper (Moonen 1993); F1173, O0083, O0372 and O0446 are not in it.
- [x] Extraction of author uncertainties from the papers: `docs/ERROR_EXTRACTION.md` (summary, questions Q1–Q6) and `docs/extraction/extract_G*.md` (page/table/figure quotes).
- [x] Kyle reviewed ERROR_EXTRACTION.md (Q1–Q6, 2026-10-08; see the decision log).
- [ ] Doering Table 5 transcription (two independent transcriptions, reconciled).
- [ ] Kyle: case-by-case decisions on docs/FLAGGED_DATASETS.md.
- [ ] Step 2: fill rule (partial records). Needs no papers; start on Kyle's go.
- [ ] Step 3: whole-set records from the papers (Doering 25 MeV ×3 from the thesis Table 5).
- [ ] Step 4: enforcement test, rebuild, diff report, commit.
- [ ] Step 5: downstream (sm3 rebuild, 208Pb lane/locw rerun, CAMPAIGN.md, HIGHLIGHTS).

## Decision log

| date | decision | by |
|---|---|---|
| 2026-10-08 | Fill rule for partial records: interpolate interior gaps; backward end ≥ 100 %; forward end keeps the reader bound | Kyle |
| 2026-10-08 | Doering normalisation stays 10 % (ERR-1 is the authors' total absolute-scale estimate) | Kyle |
| 2026-10-08 | Doering treated like any partial record; no re-digitisation (whole-set 25 MeV records take their errors from the thesis) | Kyle (whole-set note: Claude) |
| 2026-10-08 | Public repo: PDFs git-ignored, only `papers/INDEX.md` committed | Kyle |
| 2026-10-08 | Doering O0178: replace the EXFOR digitised values AND errors with the thesis Table 5 tabulation (all 12 sets); the EXFOR points absent from Table 5 (e.g. 208Pb 45 MeV 161.9°/164.0°) are dropped (supersedes "no re-digitisation") | Kyle |
| 2026-10-08 | Drop ELM's CURVE duplicates of Fulmer 61.4 MeV (O0211004/007/008/009); keep the tables (012/015/016/017) | Kyle |
| 2026-10-08 | "Not stated" entries: per-paper proposals (ERROR_EXTRACTION.md), not a uniform default | Kyle |
| 2026-10-08 | Apply the author-stated normalisation errors where they differ from the corpus default | Kyle |
| 2026-10-08 | Records without a good author source of errors are flagged (docs/FLAGGED_DATASETS.md); Kyle decides case by case (drop, or uniform fallback) | Kyle |
| 2026-10-08 | Error-column meaning is taken from each subentry's ERR-ANALYS text, not the label: EXFOR relabelled columns between releases (e.g. O0328 ERR-T → ERR-1) | Claude (from the EXFOR cross-check) |
