# Validation evidence

Verified on 9 October 2026 (Asia/Kolkata).

| Area | Result |
|---|---|
| Python automated tests | 13 passed |
| PostgreSQL/dbt build | 5 models built; 13 data tests passed |
| Python vs PostgreSQL reconciliation | All 40 observation/skill rows match counts and denominators |
| Repeat warehouse export | 80 unique job records retained |
| Immutable history | Historical skills survive later record updates |
| Configuration changes | Different settings are excluded from a comparison series |
| API errors | Mocked authentication and rate-limit behavior verified; credentials not printed |
| Failed collection | Partial SQLite writes and snapshots roll back |
| Browser role filter | Data Analyst filter returns 16 postings |
| Browser empty search | Zero postings and explicit empty state |
| Browser trend | Filtered Python change correctly shows 18.8 percentage points in simulated data |
| Browser CSV download | 80 rows; 80 unique IDs |
| Browser console | No errors or warnings observed |
| Mobile layout | No document-level horizontal overflow observed at narrow viewport |
| Scheduled execution | Configuration ready; macOS rejected registration, schedule inactive |
| Live Adzuna access | Passed: 409 distinct provider IDs across five role queries |
| Live extraction accuracy | Focused snippet review performed; range bug fixed. Precision/recall not measured |

Warehouse validation used a separate database named `job_market_portfolio_test_20261009` with synthetic records, leaving existing project databases untouched. Browser screenshots are saved in `screenshots/`. Exact installed package versions are in `requirements-tested.txt`.

No real hiring-demand conclusion or salary recommendation is supported by the demonstration dataset.

## Live verification

Five models and thirteen dbt data checks passed on real records. All ten latest skill counts and observation denominators match Python. The persistent project database is `job_market_intelligence_live_20261009`. See LIVE_FINDINGS.md for sample coverage and snippet limitations.
