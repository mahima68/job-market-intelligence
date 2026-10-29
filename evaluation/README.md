# Skill mention evaluation

Task: identify explicit mentions of ten configured technologies in the available title and description, including company context. This does not classify whether a technology is required, optional or used by the employer.

The original 409-record private collection was ordered by provider ID, deduplicated by exact title-plus-description text and sampled with Python random.Random(20261029).sample(..., 40). Codex AI reviewed the full available text and supplied expected labels before running the extractor. Labels are not independently human-reviewed. No extraction rules were tuned on this sample.

Results: 40/40 exact label sets; micro precision and recall 1.00 across 16 positive mentions. Support: SQL 4, Excel 2, Power BI 5, Python 2, Tableau 3. AWS, Azure, Snowflake, dbt and GenAI have no positive support; their precision/recall are undefined, not perfect. This small, negative-heavy sample cannot establish general performance or full-description recall.

Replay with: python evaluate_skills.py --database /path/to/live.sqlite

The evaluator reads the original immutable snapshot dated 2026-10-09T18:17:49.516555+00:00 and refuses missing records. Optional text fingerprints are checked when supplied. Published annotations contain provider IDs and labels; raw job descriptions, contact details, databases and credentials stay private. Results contain aggregate counts.

Independent human adjudication and a larger sample with rare skills are the next validation steps. These labels should not become a tuning benchmark without a new holdout. The synthetic public dashboard is separate from this real-text evaluation.
