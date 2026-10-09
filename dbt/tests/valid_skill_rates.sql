select * from {{ ref('mart_skill_trends') }}
where skill_mentions > postings or skill_mentions < 0 or mention_pct not between 0 and 100
