# Table reconstruction map

The exact manuscript §§7–8 is awaiting author input. These labels describe the source result tables and do not invent manuscript table numbers.

| Available result | Recomputed output | Public input | Check |
|---|---|---|---|
| C0–C4 means, SDs, F1–F7 rates, seven score dimensions | outputs/stats.json | data/judgments.jsonl | All fields compared to reference/stats.json |
| Four ladder comparisons, H1/H2 win rates and CIs, Wilcoxon, Holm | outputs/stats.json; outputs/tables_main.md | judgments + pairwise | All numeric fields compared |
| J2 Fleiss κ, ICC, flags, undecidable counts | outputs/consensus.json | per-model judgments | Exact numerical reference comparison |
| S4 held-out win rate, CI, agreement, Cohen κ, five errors | outputs/heldout/heldout_report.json | all held-out + pairwise votes | All numerical fields compared; model alias discrepancy disclosed |
| C2/C3 branch comparisons | outputs/tables_supplement.json | pairwise + session index | All branch reference fields compared |
| C4 F1 branch/persona/pattern counts | outputs/tables_supplement.json | judgments + numeric event records | Counts checked; full-population regex extraction is not rerun |
| GPT empty rationale / separate annotation counts | outputs/tables_supplement.json | per-model judgments + annotations | 918 original empty fields retained |
| S6 classification/mapping coverage | outputs/tables_supplement.json | code-only mapping records | 234 rows, 54 behavior rows, 52 directly linked |
| GEPA learning metrics | outputs/tables_supplement.json | numeric learning records | Original 192 records compared |
| Mean coverage by condition | outputs/tables_supplement.json | judgments | Recalculated directly |

The full-population F1 event extraction and original feedback classification cannot be independently repeated from excluded full transcripts/feedback. Numeric event and mapping records enable aggregation checks; this restriction is intentional under the release scope. C4 generation, optimization, new model judging and P5 human ratings are not reproduced by this package.
