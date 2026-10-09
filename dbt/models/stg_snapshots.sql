select snapshot_id, collected_at::timestamptz as collected_at,
       country, config_key, config_json::jsonb as config
from {{ source('raw', 'snapshots') }}
