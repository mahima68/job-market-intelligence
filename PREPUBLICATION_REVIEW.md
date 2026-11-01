# Historical pre-publication review

This records the original checks completed before publication. The repository is now public. These historical results are not a fresh verification of the current version.

| Check | Pass 1 | Pass 2 |
|---|---|---|
| Python automated tests (13) | Passed | Passed |
| Dashboard behavior (filters, empty state, trends, CSV safety/export) | Passed | Passed |
| PostgreSQL/dbt (5 models and 13 data tests) | Passed | Passed |
| Credential and publication-file scan | Passed | Passed |

Corrections: CSV formula protection now handles leading whitespace; custom schedule times are reported correctly; outdated documentation and local-machine paths were removed. Dashboard regression checks and GitHub CI were added.

Publication includes source, synthetic demo assets, screenshots and aggregate live findings. It excludes .env, live payloads/dashboards, databases, generated dbt output and local database profiles.

At the time of this review, local schedule registration was inactive and keyword extraction precision and recall had not been measured. See [the current README](README.md) for collection and scheduling evidence, and [the subsequent skill evaluation](evaluation/README.md) for its small AI-reviewed sample and limitations. More observations are still needed before claiming sustained market trends.

The public repository contains the source and sanitized portfolio materials; live credentials and raw API records remain excluded.
