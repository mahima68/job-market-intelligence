select j.* from {{ ref('stg_snapshot_jobs') }} j
left join {{ ref('stg_snapshots') }} s using (snapshot_id)
where s.snapshot_id is null
