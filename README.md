# Five-branch AI career counseling: research artifact

Anonymous review edition · v0.2.2 · AI consensus-based assessment, before the P5 human audit.

This study compares five conditions (C0–C4) across five counseling branches, 150 synthetic personas and three seeds: 2,250 sessions. The release supports recalculation of the reported tables from stored AI judgments. It is not a deployed counseling service.

## Recalculate the paper tables

From a fresh clone:

```sh
make reproduce
```

Requires Git, Make, and Python 3.12+ (or `uv`, which can provision Python 3.12). The first run installs pinned NumPy/SciPy packages into a local `.venv`; this setup may download public dependencies. Statistical calculation then runs with network connections disabled and needs no API key, internal directory or original repository.

Results are written under `outputs/`: `tables_main.md`, `stats.json`, `consensus.json`, `heldout/heldout_report.json`, `tables_supplement.json`, and `verification.json`. The command recomputes and compares every numerical field in the released main-statistics, consensus and held-out reference tables. It fails on checksum or numerical mismatch. Pairwise bootstrap resamples `(persona, seed)` rows; it is not a cluster bootstrap grouping all three seeds of each persona. Pairwise intervals use 2,000 replicates; score-difference and held-out intervals use the original 1,000-replicate implementation.

The latest manuscript containing §§7–8 was not present in the supplied source tree. `TABLE_MAP.md` maps the available research results to outputs; exact manuscript section/table labels remain pending confirmation. Reproduction of the supplied results must not be represented as a completed comparison against an unseen manuscript.

## Included material

- Frozen rubric v2.2.1 release (internal rubric v2.2), judge prompt v1.6, response schemas/request templates, Korean and English rubric materials.
- 31 regression seeds and 10 canaries with English counterparts; persona schema and P/T/H persona sets. P personas are evaluation-only and must never be used by an optimizer; H is selection-only and T is training-only.
- Preregistration versions 1.0–1.5 and evaluation cards. Earlier statements remain historical; current interpretation is in `LIMITATIONS.md`.
- All 2,250 ensemble judgments (6,750 individual verdicts), 1,800 pairwise records and 450 held-out records including five errors. Identifying strings are redacted; numerical scores, failure flags, missingness, votes, order and join identifiers are preserved.
- Exactly 300 synthetic transcripts: two per condition × branch × behavior cell (150 cells), selected by deterministic hash ranking. This release sample is separate from the planned P5 human-audit sample.
- C3 core and five branch deltas from the experiment-start freeze, with identity/contact redaction only; C4 is represented by a descriptive diff summary.
- Offline consensus/statistics code, numeric F1 event records and code-only S6 mapping records. These contain no original feedback CSV or unselected transcript text.

C4 raw prompts, the other 1,950 full transcripts, original feedback CSVs and production/live-integration engine code are excluded. All verdict rationales are included as authorized; they can contain short redacted quotations, but do not constitute a full transcript release. See `RELEASE_SCOPE.md`.

## Anonymity checks and commits

`make reproduce` / `make setup` installs `.githooks/pre-commit` as this clone's hook path. Git does not transfer hook configuration when cloning, so run either command before committing. `make scan` checks the working files; the hook checks **every blob in the Git index** and blocks a commit unless findings are zero. It checks known organization/author/employer fingerprints, hosting domains, email addresses, internal paths, contact patterns, credentials, excluded paths and binary/archive payloads. Fingerprints avoid publishing the private identity denylist. No blanket exemption is made for a named README.

The scanner is a safeguard, not proof against contextual re-identification or unknown names. Source license/bibliography authors and model providers are not identities of this study. General public-service domains and bibliographic links are retained. No real author metadata is stored in this anonymous Git history.

## Citation and licenses

During anonymous review, cite **Anonymous authors (2026), Five-branch AI career counseling: research artifact, v0.2.2, accompanying submission**. No DOI or publication title is invented. `README.named.md` is a separately marked template pending confirmed author/affiliation/publication metadata; do not cite its placeholders or publish it as a finished named edition. A named release must be prepared separately from this blind-review history.

Code: Apache-2.0. Data, rubrics, prompts and documentation: CC BY 4.0. Full terms and scope are in `LICENSE` and `LICENSES/`.
