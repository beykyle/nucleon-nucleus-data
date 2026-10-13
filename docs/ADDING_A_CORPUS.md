# Adding a corpus

A new corpus is added as a **tabulated corpus**: a list of EXFOR subentries and scattering energies, one table per
sector. It is curated by the same pipeline as KDUQ, CHUQ and Test:
- retrieval from the local EXFOR database;
- the overall-uncertainty rule (`nn_corpora.errors`);
- unit and frame conventions (`nn_corpora.munge`);
- serialisation (`nn_corpora.serialize`).

Like those corpora it is **static**: it holds the data as the table and these rules give them. It can also have an
**evaluated copy**, `<name>_evaluated`, carrying the author-based uncertainties of
[AUTHOR_UNCERTAINTIES.md](AUTHOR_UNCERTAINTIES.md).

The short version:

```bash
source scripts/setup_exfor_db.sh 2025
uv run python scripts/new_corpus.py NAME --sectors proton_elastic proton_ay   # 1. scaffold
#   register NAME in src/nn_corpora/spec.py (TABULATED)                       # 1. register
#   fill spec/NAME_<sector>.csv                                               # 2. the tables
uv run python scripts/curate_corpus.py NAME --allow-unresolved                # 3. first build
uv run python scripts/refresh_known_missing.py --corpus NAME                  # 4. after review
uv run python scripts/curate_corpus.py NAME                                   # 3. checked build
uv run python scripts/apply_author_errors.py                                  # 6. evaluated copy
uv run python scripts/build_manifests.py                                      # 7. manifests
uv run pytest tests/                                                          # 7. checks
```

## 1. Scaffold and register

```bash
uv run python scripts/new_corpus.py NAME --sectors SECTOR [SECTOR ...]
```

This writes an empty table, header only, for each sector: `spec/NAME_<sector>.csv`. It never overwrites a table.
The name must be lower-case letters and digits, and not an existing corpus (`elm`, `sm3`, a tabulated corpus) or
end in `evaluated`; it becomes the directory `data/NAME/`.

Then register the corpus in `TABULATED` in [src/nn_corpora/spec.py](../src/nn_corpora/spec.py). The script prints
the entry to paste:

```python
TabulatedCorpus(
    "NAME", "Title",
    "One paragraph: what the corpus is and where its table comes from.",  # notebook header
    "The publication or source of the table",
    evaluated_copy=True),  # False: no NAME_evaluated
```

- **`evaluated_copy=True`** (the default) builds `NAME_evaluated` alongside: the same records with the
  author-uncertainty corrections applied (§6). `NAME` itself is never corrected. Use the static corpus to
  reproduce an analysis that used the table as published, and the evaluated copy for the best available
  uncertainties.
- **`from_supplement`** is only for the corpora transcribed from `supplement_experimentalCorpora.pdf`, which the
  tests check against that PDF. Leave it `False`.

The tests fail if a table in `spec/` belongs to no registered corpus, or a registered corpus has no table
([tests/test_corpus_registry.py](../tests/test_corpus_registry.py)).

## 2. The tables

One row per data set and energy. The columns, in this order:

| column | meaning |
|---|---|
| `corpus`, `sector` | the corpus name and the sector, the same as the file name |
| `projectile` | `neutron` or `proton`, as the sector says |
| `target_A`, `target_Z` | the target; `target_A = 0` for a natural-abundance target (EXFOR's convention) |
| `target_label` | `<A><Symbol>`, e.g. `208Pb`, or `nat<Symbol>`, e.g. `natNi`; it must agree with A and Z |
| `energy_mev` | the incident (lab) energy in MeV, as the source gives it; EXFOR's energy is matched within a tolerance |
| `energy_hi_mev` | only in the range sectors (`neutron_total`, `proton_reaction`): the upper end of the energy range; blank elsewhere |
| `subentry` | the 8-character EXFOR subentry, e.g. `O0142011`; blank for a data set the source lists but EXFOR does not have |
| `pointer` | the EXFOR pointer, where one subentry holds several quantities (`S`, `A`, `1`, `2`); usually blank |
| `pdf_page` | a page in the source document, if useful; may be blank |

The sectors:

| sector | quantity | stored as |
|---|---|---|
| `neutron_elastic` | dσ/dΩ | b/sr against c.m. angle |
| `neutron_ay` | analysing power | dimensionless, against c.m. angle |
| `neutron_total` | σ_tot | b against lab energy, trimmed to the tabulated range and thinned to one point per MeV |
| `proton_elastic` | dσ/dΩ | ratio to Rutherford against c.m. angle; absolute data are divided by the Rutherford cross section |
| `proton_ay` | analysing power | dimensionless, against c.m. angle |
| `proton_reaction` | σ_R | b against lab energy, trimmed to the tabulated range |

`spec.validate_sector` checks every table, and `curate_corpus.py` refuses to build from a malformed one. It checks:
- the header;
- that `corpus`, `sector` and `projectile` agree with the file;
- that targets are physical and labelled consistently;
- energies, ranges only in the range sectors, subentry and pointer formats, and duplicate rows.

A subentry that EXFOR has since renumbered is substituted automatically when the same entry has an unambiguous
match at the same energy. The substitution is recorded in the record's `notes`.

## 3. Build and inspect

```bash
uv run python scripts/curate_corpus.py NAME [--sector SECTOR ...] [--allow-unresolved]
```

For each sector this:
1. validates the table;
2. retrieves and cleans it (`nn_corpora.corpus.curate`);
3. prints a summary and the rows that did not resolve;
4. writes `data/NAME/<sector>/`.

It ends with the commands still to run.

To inspect the data by eye, generate the sector notebooks and run them. Each plots every data set, one figure per
target:

```bash
uv run python scripts/generate_notebooks.py --corpus NAME
uv run pytest --nbmake notebooks/NAME/
```

A notebook does what `curate_corpus.py` does, plus the plots, and writes the same files.

## 4. Account for every row

Every row must either produce data or be listed, with a reason, in
[spec/known_missing.csv](../spec/known_missing.csv). A row that stops resolving later (EXFOR revised, a code change)
then fails the build instead of disappearing quietly.

A first build usually has unresolved rows, so run it with `--allow-unresolved`, and read why each row failed:

| category | meaning | what to do |
|---|---|---|
| `absent-from-exfor` | the table marks it as not in EXFOR (blank subentry) | nothing |
| `x4i3-parse-failure` | the entry is not in x4i3's index (often a malformed number in the `.x4` file) | check the subentry is right; otherwise it stays missing |
| `subentry-withdrawn` | EXFOR has renumbered or removed the subentry | find the current subentry and correct the table |
| `energy-not-found` | no measurement at that energy within tolerance | check the energy against EXFOR |
| `uncertainty-unresolved` | several error columns, and the preference rule can't choose | an override (§5) |
| `dropped-in-cleaning` | retrieved, but no usable uncertainties, too few angles, or the wrong observable | nothing, or an override |

When every remaining row is understood, record them and rebuild with the check on:

```bash
uv run python scripts/refresh_known_missing.py --corpus NAME   # replaces only NAME's rows
uv run python scripts/curate_corpus.py NAME
```

## 5. Error columns the rule can't resolve

The overall uncertainty of each point is chosen by the label preference `ERR-T`, `±DATA-ERR`, `DATA-ERR`,
`ERR-S`, `ERR-DIG`, `ERR-SYS` ([src/nn_corpora/errors.py](../src/nn_corpora/errors.py)). Where it can't choose, or
chooses wrongly for the static corpus, add an `Override` for `(NAME, sector, entry or subentry)` in
[src/nn_corpora/overrides.py](../src/nn_corpora/overrides.py), citing the entry's ERR-ANALYS text or the
publication. An override can name the error columns (`parsing_kwargs`), rescale the data (`scale_by`) or drop it
(`drop`).

## 6. The evaluated copy

```bash
uv run python scripts/apply_author_errors.py
uv run python scripts/audit_reader_errors.py NAME_evaluated
```

`apply_author_errors.py` rebuilds every evaluated copy, including `data/NAME_evaluated`, from its static corpus. The
existing corrections apply wherever the new corpus shares their EXFOR entries. The audit then lists any record that
still rests on EXFOR's data-point reader (digitisation) uncertainty alone, or whose error is below the authors' error
in EXFOR. The slow tests require the audit to come back clean:

```bash
uv run pytest tests/test_reader_errors.py -m slow
```

For each record the audit lists, find the authors' statement of their uncertainty (the publication, or the entry's
ERR-ANALYS). Then add a rule in [src/nn_corpora/author_errors.py](../src/nn_corpora/author_errors.py) that matches
what that statement gives:

| the source gives | add |
|---|---|
| an uncertainty in the text | a `PER_PAPER` rule |
| error columns that EXFOR mislabels | a `COLUMNS` (or `COMMON`) entry |
| a normalisation | a `NORM` / `NORM_AY` entry |
| nothing usable | the subentry in `DROP_FLAGGED` |

Document each rule in [AUTHOR_UNCERTAINTIES.md](AUTHOR_UNCERTAINTIES.md), and quote its source in
[AUTHOR_UNCERTAINTY_SOURCES.md](AUTHOR_UNCERTAINTY_SOURCES.md). The rules apply to every evaluated corpus holding
the subentry, so check the diff report as well:

```bash
uv run python scripts/apply_author_errors.py --report docs/AUTHOR_ERRORS_DIFF.md
```

## 7. Manifests, README and tests

```bash
uv run python scripts/build_manifests.py
uv run pytest tests/
```

- `build_manifests.py` writes `data/NAME/manifest.json`, with the EXFOR database version and, for a tabulated corpus,
  the coverage of each sector.
- The tests pick the new corpus up without changes:
  - every record is validated, and every table row is resolved or allowlisted
    ([tests/test_data_integrity.py](../tests/test_data_integrity.py));
  - the evaluated copy is checked against its static corpus ([tests/test_reader_errors.py](../tests/test_reader_errors.py)).
- Add the corpus to the tables at the top of the [README](../README.md): what it is, and its sectors with their
  counts from the manifest.
