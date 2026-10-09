with dictionary(skill) as (
    values ('SQL'),('Excel'),('Power BI'),('Python'),('Tableau'),
           ('AWS'),('Azure'),('Snowflake'),('dbt'),('GenAI')
)
select s.snapshot_id, s.collected_at, s.country, s.config_key, d.skill,
       count(j.job_id) as postings,
       count(j.job_id) filter (where j.payload->'skills' ? d.skill) as skill_mentions,
       100.0 * count(j.job_id) filter (where j.payload->'skills' ? d.skill)
           / nullif(count(j.job_id), 0) as mention_pct
from {{ ref('stg_snapshots') }} s
cross join dictionary d
left join {{ ref('stg_snapshot_jobs') }} j using (snapshot_id)
group by s.snapshot_id, s.collected_at, s.country, s.config_key, d.skill
