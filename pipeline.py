"""Job Market Intelligence: dependency-free ingestion and dashboard pipeline."""
import argparse
import collections
import datetime as dt
import hashlib
import socket
import uuid
import itertools
import json
import os
from pathlib import Path
import random
import re
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parent
RULE_VERSION = '2'
ROLES = ['Data Analyst', 'Business Analyst', 'Product Analyst', 'BI Analyst', 'E-commerce Analyst']
PATTERNS = {
    'SQL': r'\b(?:sql|postgresql|mysql|t-sql)\b',
    'Excel': r'\bexcel\b', 'Power BI': r'\bpower\s*bi\b',
    'Python': r'\bpython\b', 'Tableau': r'\btableau\b',
    'AWS': r'\b(?:aws|amazon web services)\b',
    'Azure': r'\bazure\b', 'Snowflake': r'\bsnowflake\b',
    'dbt': r'\bdbt\b', 'GenAI': r'\b(?:genai|generative ai|llms?|large language models?)\b',
}

def load_env():
    """Read literal KEY=value settings; never execute shell expressions."""
    path = ROOT / '.env'
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        key, separator, value = line.partition('=')
        if not separator or not re.fullmatch(r'[A-Z][A-Z0-9_]*', key.strip()):
            raise RuntimeError('Invalid .env format. Use one KEY=value setting per line.')
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        os.environ.setdefault(key.strip(), value)

def skills(text):
    return [name for name, pattern in PATTERNS.items() if re.search(pattern, text, re.I)]

def experience(text):
    match = re.search(r'\b(\d{1,2})(?:\s*(?:[-–]|to)\s*\d{1,2})?\s*\+?\s*years?\b', text, re.I)
    return int(match.group(1)) if match else None

def connect(mode):
    db = sqlite3.connect(ROOT / 'data' / f'{mode}.sqlite')
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    db.execute('PRAGMA busy_timeout=30000')
    db.executescript('''
    CREATE TABLE IF NOT EXISTS jobs (
      id TEXT PRIMARY KEY, country TEXT NOT NULL, title TEXT NOT NULL,
      company TEXT, location TEXT, description TEXT, created TEXT,
      salary_min REAL, salary_max REAL, salary_is_predicted INTEGER,
      redirect_url TEXT, first_seen TEXT NOT NULL, last_seen TEXT NOT NULL,
      raw_json TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS job_queries (
      job_id TEXT REFERENCES jobs(id), query TEXT, PRIMARY KEY(job_id,query));
    CREATE TABLE IF NOT EXISTS runs (
      run_id INTEGER PRIMARY KEY, collected_at TEXT, country TEXT, query TEXT,
      pages INTEGER, received INTEGER);
    CREATE TABLE IF NOT EXISTS job_skills (
      job_id TEXT REFERENCES jobs(id), skill TEXT, PRIMARY KEY(job_id,skill));
    CREATE TABLE IF NOT EXISTS snapshots (
      snapshot_id TEXT PRIMARY KEY, collected_at TEXT NOT NULL,
      country TEXT NOT NULL, config_key TEXT NOT NULL, config_json TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS snapshot_jobs (
      snapshot_id TEXT REFERENCES snapshots(snapshot_id), job_id TEXT,
      payload TEXT NOT NULL, PRIMARY KEY(snapshot_id, job_id));
    ''')
    return db

def save(db, postings, country, query, stamp):
    for job in postings:
        if not job.get('id') or not job.get('title'):
            continue
        key = country + ':' + str(job['id'])
        values = (key,country,job['title'],(job.get('company') or {}).get('display_name','Unknown'),
          (job.get('location') or {}).get('display_name','Unknown'),(job.get('description') or ''),
          job.get('created'),job.get('salary_min'),job.get('salary_max'),
          int(str(job.get('salary_is_predicted',0)) == '1'),job.get('redirect_url',''),stamp,stamp,json.dumps(job))
        db.execute('''INSERT INTO jobs VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
          ON CONFLICT(id) DO UPDATE SET title=excluded.title, company=excluded.company,
          location=excluded.location, description=excluded.description, created=excluded.created,
          salary_min=excluded.salary_min, salary_max=excluded.salary_max,
          salary_is_predicted=excluded.salary_is_predicted, redirect_url=excluded.redirect_url,
          last_seen=excluded.last_seen,raw_json=excluded.raw_json''',values)
        db.execute('INSERT OR IGNORE INTO job_queries VALUES (?,?)',(key,query))
        db.execute('DELETE FROM job_skills WHERE job_id=?',(key,))
        for skill in skills(job['title']+' '+(job.get('description') or '')):
            db.execute('INSERT INTO job_skills VALUES (?,?)',(key,skill))

def fetch(country, query, page, per_page):
    params = urllib.parse.urlencode(dict(app_id=os.environ['ADZUNA_APP_ID'],
      app_key=os.environ['ADZUNA_APP_KEY'],what=query,results_per_page=per_page,
      **{'content-type':'application/json'}))
    request = urllib.request.Request(f'https://api.adzuna.com/v1/api/jobs/{country}/search/{page}?{params}',
      headers={'Accept':'application/json','User-Agent':'JobMarketIntelligence/1.0'})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = json.load(response)
            if not isinstance(payload,dict) or not isinstance(payload.get('results'),list):
                raise RuntimeError('The API response did not contain a results list.')
            return payload['results']
        except (ValueError, UnicodeDecodeError):
            raise RuntimeError('Adzuna returned invalid JSON.') from None
        except urllib.error.HTTPError as error:
            if error.code not in (429,500,502,503,504) or attempt == 3:
                raise RuntimeError(f'Adzuna returned HTTP {error.code}. Check credentials, country and quota.') from None
            time.sleep(min(30,2**attempt*2))
        except (urllib.error.URLError, TimeoutError, socket.timeout):
            if attempt == 3:
                raise RuntimeError('Could not reach Adzuna. Check your network connection.') from None
            time.sleep(2**attempt)

def demo():
    rng = random.Random(42)
    rows=[]
    for i in range(80):
        role=ROLES[i%len(ROLES)]
        chosen=rng.sample(list(PATTERNS),rng.randint(2,6))
        minimum = rng.choice([None,400000,600000,900000,1200000])
        rows.append(dict(id=f'demo-{i:03}',title=role,company={'display_name':f'Example Company {i%12+1}'},
          location={'display_name':rng.choice(['Bengaluru','Mumbai','Delhi NCR','Hyderabad','Pune'])},
          description=f'Synthetic example. Requires {rng.randint(1,6)} years of experience. Skills: '+', '.join(chosen),
          created=(dt.datetime(2026,9,1,tzinfo=dt.timezone.utc)+dt.timedelta(days=i%30)).isoformat(),
          salary_min=minimum,salary_max=minimum*1.4 if minimum else None,salary_is_predicted=0))
    return rows

def snapshot(db, postings, country, stamp, config):
    """Store immutable observation records, deduplicated within this collection."""
    config = dict(config, country=country, rule_version=RULE_VERSION)
    config_json = json.dumps(config, sort_keys=True)
    config_key = hashlib.sha256(config_json.encode()).hexdigest()
    snapshot_id = uuid.uuid4().hex
    db.execute('INSERT INTO snapshots VALUES (?,?,?,?,?)',
               (snapshot_id, stamp, country, config_key, config_json))
    unique = {}
    for job in postings:
        if not job.get('id') or not job.get('title'):
            continue
        key = country + ':' + str(job['id'])
        current = dict(db.execute('SELECT * FROM jobs WHERE id=?', (key,)).fetchone())
        current.pop('raw_json')
        current['skills'] = skills(current['title']+' '+current['description'])
        current['experience_min_years'] = experience(current['description'])
        unique[key] = current
    db.executemany('INSERT INTO snapshot_jobs VALUES (?,?,?)',
                   [(snapshot_id, key, json.dumps(value)) for key, value in unique.items()])
    return snapshot_id


def report(db, mode, country):
    latest = db.execute('SELECT * FROM snapshots WHERE country=? ORDER BY collected_at DESC, rowid DESC LIMIT 1',
                        (country,)).fetchone()
    if latest is None:
        raise RuntimeError('No completed collection is available.')
    history=[]
    for snap in db.execute('SELECT * FROM snapshots WHERE config_key=? ORDER BY collected_at,rowid',
                           (latest['config_key'],)):
        observed=[json.loads(r[0]) for r in db.execute(
            'SELECT payload FROM snapshot_jobs WHERE snapshot_id=? ORDER BY job_id', (snap['snapshot_id'],))]
        history.append(dict(snapshot_id=snap['snapshot_id'],collected_at=snap['collected_at'],jobs=observed))
    rows=history[-1]['jobs']
    counts=collections.Counter(s for row in rows for s in row['skills'])
    pairs=collections.Counter(pair for row in rows for pair in itertools.combinations(sorted(row['skills']),2))
    payload=dict(mode=mode,country=country,jobs=rows,history=history,config=json.loads(latest['config_json']),
      skill_counts=dict(counts),skill_pairs=[dict(skills=list(pair),count=n) for pair,n in pairs.most_common(15)],
      generated_at=dt.datetime.now(dt.timezone.utc).isoformat())
    out=ROOT/'data'/f'{mode}-analytics.json'
    out.write_text(json.dumps(payload,indent=2))
    encoded=json.dumps(payload).replace('<','\\u003c')
    template=(ROOT/'dashboard-template.html').read_text()
    target=ROOT/f'dashboard-{mode}.html'
    temporary=target.with_suffix('.html.tmp')
    temporary.write_text(template.replace('__DATA__',encoded))
    temporary.replace(target)
    return target,len(rows)


def seed_history(db, country, stamp):
    config=dict(queries=sorted(ROLES),pages=2,per_page=50)
    # Demonstration weeks are simulated observations, never historical API data.
    for week in range(4):
        observation=(dt.datetime.fromisoformat(stamp)-dt.timedelta(weeks=3-week)).isoformat()
        postings=demo()
        for index,job in enumerate(postings):
            if index < week*8 and 'Python' not in skills(job['description']):
                job['description'] += ', Python'
        save(db,postings,country,'Synthetic demonstration',observation)
        snapshot(db,postings,country,observation,config)


def main():
    load_env()
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--demo-history',action='store_true',help='Seed four synthetic weekly snapshots in demo mode.')
    parser.add_argument('--mode',choices=['demo','live'],default='demo')
    parser.add_argument('--country',default='in')
    parser.add_argument('--pages',type=int,default=2)
    parser.add_argument('--per-page',type=int,default=50)
    parser.add_argument('--query',action='append',help='Repeat to collect multiple role queries.')
    args=parser.parse_args()
    if args.pages<1 or not 1<=args.per_page<=50:
        parser.error('pages must be positive; per-page must be between 1 and 50.')
    if not re.fullmatch('[a-z]{2}',args.country):
        parser.error('country must be a two-letter lowercase country code.')
    if args.mode=='live' and not all(os.environ.get(k) for k in ['ADZUNA_APP_ID','ADZUNA_APP_KEY']):
        parser.error('Set ADZUNA_APP_ID and ADZUNA_APP_KEY in your environment first.')
    if args.demo_history and args.mode!='demo':
        parser.error('--demo-history is only valid in demo mode.')
    (ROOT/'data').mkdir(exist_ok=True)
    stamp=dt.datetime.now(dt.timezone.utc).isoformat()
    with connect(args.mode) as db:
        if args.mode=='demo':
            if args.demo_history:
                db.execute('DELETE FROM snapshot_jobs')
                db.execute('DELETE FROM snapshots')
                seed_history(db,args.country,stamp)
            else:
                postings=demo()
                save(db,postings,args.country,'Synthetic demonstration',stamp)
                snapshot(db,postings,args.country,stamp,dict(queries=sorted(ROLES),pages=2,per_page=50))
        else:
            all_postings=[]
            for query in args.query or ROLES:
                received=0
                pages=0
                for page in range(1,args.pages+1):
                    postings=fetch(args.country,query,page,args.per_page)
                    save(db,postings,args.country,query,stamp)
                    all_postings.extend(postings)
                    received+=len(postings)
                    pages+=1
                    if len(postings)<args.per_page:
                        break
                    time.sleep(1)
                db.execute('INSERT INTO runs(collected_at,country,query,pages,received) VALUES (?,?,?,?,?)',
                  (stamp,args.country,query,pages,received))
            snapshot(db,all_postings,args.country,stamp,
                     dict(queries=sorted(set(args.query or ROLES)),pages=args.pages,per_page=args.per_page))
    with connect(args.mode) as db:
        path,total=report(db,args.mode,args.country)
    print(f'Created {path.name} with {total} unique postings ({args.mode}, {args.country}).')

if __name__=='__main__':
    try:
        main()
    except RuntimeError as error:
        raise SystemExit(str(error)) from None
