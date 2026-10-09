select snapshot_id, job_id, payload::jsonb as payload
from {{ source('raw', 'snapshot_jobs') }}
