# First live collection findings

Collected: 2026-10-09T18:17:49.516555+00:00 (UTC). Market: India. Five role queries, up to two pages of 50 results each.

Latest sample: **409 distinct provider IDs**. These are search-result records, not a verified count of active analyst vacancies.

| Skill | Snippet mentions | Share of sample |
|---|---:|---:|
| Power BI | 40 | 9.8% |
| SQL | 39 | 9.5% |
| Python | 20 | 4.9% |
| Tableau | 15 | 3.7% |
| Excel | 13 | 3.2% |
| Azure | 5 | 1.2% |
| GenAI | 5 | 1.2% |
| AWS | 2 | 0.5% |
| Snowflake | 1 | 0.2% |

142 records (34.7%) include a non-predicted salary value.
328 records (80.2%) mention none of the ten tracked skills in their available text.
45 records repeat an identical nonempty description from another provider ID; identical descriptions do not prove the same vacancy.

## Interpretation
Power BI and SQL have the highest tracked mention counts in this collected sample. The low overall skill coverage reflects sparse/truncated descriptions and search coverage; it does not imply employers do not request those skills. Search results may include adjacent or unrelated roles. Full descriptions and a relevance review are needed before using these rates to choose learning priorities.

## Accuracy review
Reviewed eight snippets from the initial connection test and twelve skill-positive snippets from the wider collection. A real-text range bug (2 to 4 years) was corrected and regression-tested; extraction rules were versioned and the collection refreshed. Repeated syndicated snippets and short descriptions were observed. This focused review is not a measured precision/recall evaluation.

## Verification and next observations
All ten latest skill counts and their denominators agree with PostgreSQL. The five dbt models built and thirteen data tests passed on real records. Only one comparable observation uses the revised extraction rules, so a time trend cannot yet be claimed. Earlier observations remain preserved under their original rule version.

## Scheduling status
A daily 09:00 schedule was generated. macOS launchctl returned a bootstrap error, so the schedule is not active. Run the activation command in README from your own terminal to register it; no administrator command is recommended here.
