# Pre-publication review

Two check passes completed before any GitHub upload.

| Check | Pass 1 | Pass 2 |
|---|---|---|
| Python automated tests (13) | Passed | Passed |
| Dashboard behavior (filters, empty state, trends, CSV safety/export) | Passed | Passed |
| PostgreSQL/dbt (5 models and 13 data tests) | Passed | Passed |
| Credential and publication-file scan | Passed | Passed |

Corrections: CSV formula protection now handles leading whitespace; custom schedule times are reported correctly; outdated documentation and local-machine paths were removed. Dashboard regression checks and GitHub CI were added.

Publication includes source, synthetic demo assets, screenshots and aggregate live findings. It excludes .env, live payloads/dashboards, databases, generated dbt output and local database profiles.

Limitations: daily schedule registration remains inactive on the development computer; real historical trends require more observations; keyword extraction precision and recall have not been measured.

GitHub upload is pending a repository destination and visibility choice.
