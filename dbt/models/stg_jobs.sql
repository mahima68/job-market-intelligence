select id, country, trim(title) as title, company, location, description,
       created::timestamptz as posted_at,
       first_seen::timestamptz as first_seen_at,
       last_seen::timestamptz as last_seen_at,
       salary_min, salary_max, salary_is_predicted = 1 as is_predicted_salary,
       redirect_url
from {{ source('raw', 'jobs') }}
