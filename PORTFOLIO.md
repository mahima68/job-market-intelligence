# Job Market Intelligence — portfolio case study

## Problem
Analyst job descriptions contain scattered information about skills, experience and salary disclosure. This project turns repeatable job searches into a transparent, inspectable dataset and dashboard that can support a candidate's learning priorities.

## Delivered workflow
Collect up to five role searches through a paginated API, deduplicate by provider ID and country, keep raw records and immutable observations, extract ten skill categories, and report filtered mention frequencies and changes. PostgreSQL and dbt expose the same metrics as SQL models for downstream analytics.

## Demonstration results — entirely synthetic
The latest fictional dataset contains 80 unique postings across five cities. Python is mentioned in 50 postings (62.5%). In the first simulated observation it appears in 34 of 80 postings (42.5%). The simulated change is 20.0 percentage points. This pattern was deliberately introduced to test the trend calculation; it is **not evidence about real hiring demand**.

## Engineering decisions
Use SQLite to make the application runnable without database setup, then export to PostgreSQL for dbt validation. Preserve observation payloads rather than overwriting historical skill counts. Compare only matching collection configurations. Keep unknown experience and salary values explicit. Separate synthetic and real databases. Use deterministic extraction so every counted skill can be explained from the underlying text.

## Verification
13 Python tests passed. Five PostgreSQL/dbt models built and 13 data tests passed. Every snapshot/skill count was reconciled between Python and PostgreSQL. Re-export preserved 80 unique posting records. Browser checks covered role filtering, no-result behavior, skill trends, CSV export and mobile layout.

## Interview explanation
“I built a job-market analytics pipeline with paginated API ingestion, duplicate handling, immutable snapshots, PostgreSQL and dbt transformations. The dashboard compares skill mention rates using consistent sampling settings. I validated synthetic and live collections against PostgreSQL. The first live sample contains 409 provider IDs; snippet coverage and role relevance limit the interpretation, and meaningful trends require observations over time.”

## Honest resume wording
Built a job-market analytics pipeline using Python, REST API integration, SQL, PostgreSQL and dbt; implemented deduplication, historical snapshots, skill extraction and an interactive dashboard, with automated data-quality tests and reconciliation of Python and warehouse metrics.

## Before claiming real findings
The first live collection and a focused snippet review are complete. Gather multiple comparable observations and measure extraction accuracy before making stronger conclusions. State dates, queries, sample sizes and coverage limitations alongside every conclusion.
