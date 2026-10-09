with ranked as (
    select snapshot_id, country,
           row_number() over (partition by country order by collected_at desc, snapshot_id desc) as rn
    from {{ ref('stg_snapshots') }}
)
select s.country, j.payload->>'location' as location, count(*) as postings,
       count(*) filter (where (j.payload->>'salary_min' is not null or j.payload->>'salary_max' is not null)
                        and coalesce((j.payload->>'salary_is_predicted')::integer,0)=0)
           as salary_disclosed_postings
from ranked s
join {{ ref('stg_snapshot_jobs') }} j using (snapshot_id)
where s.rn=1
group by s.country, j.payload->>'location'
