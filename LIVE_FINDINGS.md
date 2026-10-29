# Live collection findings

Updated 29 October 2026. India; five role queries; up to two pages of 50 results per query. Two comparable real observations use extraction rule version 2. These are search samples, not vacancy censuses.

| Observation (UTC) | Distinct provider IDs |
|---|---:|
| 2026-10-09T18:17:49.516555+00:00 | 409 |
| 2026-10-29T12:35:41.087406+00:00 | 413 |

| Skill | 9 October mentions | 29 October mentions |
|---|---:|---:|
| SQL | 39 | 40 |
| Power BI | 40 | 38 |
| Python | 20 | 21 |
| Tableau | 15 | 14 |
| Excel | 13 | 14 |
| Azure | 5 | 11 |
| GenAI | 5 | 6 |
| AWS | 2 | 2 |
| Snowflake | 1 | 2 |
| dbt | 0 | 0 |

## Interpretation

SQL and Power BI remain the most frequently mentioned tracked skills. Counts use different denominators: 409 and 413. Two observations do not establish a sustained trend. Results depend on query wording, ranking, truncated descriptions and provider coverage. An absent mention does not mean a skill is unnecessary; adverts with different IDs may be duplicates. Search results may include unrelated roles.

## Extraction evaluation

A deterministic sample of 40 distinct title-plus-description strings from the original collection was annotated by Codex AI before replaying the extractor. All 40 label sets matched: 16 true-positive skill mentions, zero false positives and zero false negatives. Only SQL, Excel, Power BI, Python and Tableau have positive support. This is a small AI-reviewed agreement check, not an independent human audit or evidence of perfect real-world accuracy. See [evaluation methodology](evaluation/README.md), [labels](evaluation/annotations.json) and [measured results](evaluation/results.json).

## Verification

The original collection's ten skill counts and denominators reconciled with PostgreSQL; five dbt models and thirteen dbt checks passed. That verification applies to the earlier collection. The new observation has not been revalidated in PostgreSQL. Observations remain preserved under their original extraction-rule versions.

## Scheduling

The macOS launchd activation failed again on 29 October. An active Codex daily follow-up now requests collection at 09:00 Asia/Kolkata and will report a milestone after seven observations on distinct dates. Its first scheduled successful execution is pending. Raw records, live dashboards and credentials stay local. The [public interactive demo](https://mahima68.github.io/job-market-intelligence/) uses fictional postings and simulated weeks.
