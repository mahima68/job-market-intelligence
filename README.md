# Job Market Intelligence Platform

An analytics portfolio project combining API collection, deduplicated storage, immutable observations, transparent skill extraction, PostgreSQL/dbt models and an interactive dashboard.

[Open the public synthetic demo](https://mahima68.github.io/job-market-intelligence/) · [Real aggregate findings](LIVE_FINDINGS.md) · [Skill evaluation](evaluation/README.md) · [Portfolio explanation](PORTFOLIO.md)

## Current evidence

- Two comparable live India collections: 409 distinct provider IDs on 9 October and 413 on 29 October 2026. Two samples do not establish a sustained market trend.
- PostgreSQL/dbt integration verified on the original collection: five models and thirteen data checks. The new observation has not been revalidated in PostgreSQL.
- Reproducible 40-record AI-reviewed skill-mention agreement check: 40 matching label sets, 16 true positives, zero false positives/negatives. Only five skills have positive support. This is not an independent human audit or proof of perfect accuracy.
- Daily Codex follow-up active at 09:00 Asia/Kolkata; first scheduled successful execution pending. macOS launchd activation failed. Avoid activating both schedules.

The public demo contains 80 fictional postings and four simulated weekly observations. Real API records, credentials, databases and live dashboards stay local. Public hosting publishes only the existing synthetic HTML file.

## Run the demonstration

Python 3.10+ is required; the local pipeline needs no third-party packages.

    python pipeline.py --mode demo --demo-history
    python -m unittest discover -s tests -v
    node tests/test_dashboard.cjs

Open dashboard-demo.html. Filter roles and locations, search companies, inspect skills and experience, compare simulated observations and export CSV. The --demo-history option replaces demonstration snapshots; use it only in demo mode. Normal collections append observations.

## Connect live collection

Register for an Adzuna developer account, copy .env.example to .env and enter credentials locally. Never commit credentials. The environment loader accepts literal KEY=value settings and does not execute shell expressions. Existing environment variables take precedence.

    python pipeline.py --mode live --country in --query 'Data Analyst' --pages 1 --per-page 20
    python run_collection.py --mode live

The runner collects five configured roles with at most two pages of 50 results each; verify provider quota. It uses a local overlap lock. Failed API collections roll back their transaction and cannot publish a partial snapshot. Warehouse failures return a failing exit status while preserving the completed collection.

## PostgreSQL and dbt

Install requirements-optional.txt in a virtual environment. Configure DATABASE_URL and PG settings in .env to point to the same dedicated database. Keep demo and live databases separate.

    python export_postgres.py --mode live
    cp dbt/profiles.yml.example dbt/profiles.yml
    python run_collection.py --mode live --warehouse

The runner loads .env before dbt. For manual dbt invocation, export PG variables in the terminal; dbt does not itself read this project's .env. Five models cover current records, snapshots, observation records, latest locations and skill rates. Requirements-tested.txt records the original validated versions.

## Evaluate skill mentions

    python evaluate_skills.py --database /path/to/live.sqlite

The evaluator replays published labels against the original private immutable snapshot. See evaluation/ for sampling, labels, measured results and limitations. No job-description text is published.

## Data model and interpretation

Jobs are keyed by country/provider ID. Query associations retain provenance. Snapshots preserve per-observation payloads, extracted skills and configuration hashes. Dashboard counts use the latest successful snapshot; comparisons include only observations with matching country, queries, page limits and extraction-rule version. Changing settings begins a separate series. Missing adverts do not prove closure.

Skill rate is distinct postings mentioning a configured skill divided by observed postings. Repeated mentions count once. Extraction is deterministic keyword matching, not a trained NLP model. Description snippets may omit requirements. Experience is the first explicit years phrase and may refer to a particular skill; unknown stays unknown. Salary values retain provider units and country context, with predicted values labelled and excluded from disclosure counts. No salary normalization or seniority inference is attempted. Different provider IDs may represent the same syndicated vacancy.

The data is a query search sample, not a census. Two observations cannot establish market-wide trends or causality. The public synthetic demo does not represent real demand. No Snowflake deployment, resume matching or statistically inferred trends are claimed.

## Project material

- LIVE_FINDINGS.md: real aggregate observations and verification scope.
- PORTFOLIO.md: case study and interview explanation.
- VALIDATION.md: original verification evidence.
- evaluation/: new measured extraction agreement check.
- tests/: pipeline, evaluator and dashboard checks.
- make_schedule.py: optional local macOS schedule generator; launchd remains inactive here.
- .github/workflows/pages.yml: allowlisted synthetic demo hosting.
