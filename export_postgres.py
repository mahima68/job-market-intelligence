"""Load a collection and its immutable snapshots into a dedicated PostgreSQL database."""
import argparse
import os
from pathlib import Path
import sqlite3
import pipeline


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode',choices=['live','demo'],default='live')
    args=parser.parse_args()
    pipeline.load_env()
    path=Path(__file__).resolve().parent/'data'/f'{args.mode}.sqlite'
    if not path.exists():
        parser.error('Run ingestion for the selected mode first.')
    if not os.environ.get('DATABASE_URL'):
        parser.error('Set DATABASE_URL to a dedicated project database. Do not mix demo and live exports.')
    import psycopg
    try:
        with sqlite3.connect(path) as source, psycopg.connect(os.environ['DATABASE_URL'],connect_timeout=10) as target:
            target.execute('CREATE SCHEMA IF NOT EXISTS raw')
            target.execute('CREATE TABLE IF NOT EXISTS raw.collection_mode (mode TEXT PRIMARY KEY)')
            prior=target.execute('SELECT mode FROM raw.collection_mode').fetchone()
            if prior and prior[0]!=args.mode:
                raise RuntimeError('This database already contains a different mode. Use a separate database.')
            target.execute('INSERT INTO raw.collection_mode VALUES (%s) ON CONFLICT DO NOTHING',(args.mode,))
            target.execute('''CREATE TABLE IF NOT EXISTS raw.jobs (
              id TEXT PRIMARY KEY,country TEXT,title TEXT,company TEXT,location TEXT,
              description TEXT,created TEXT,salary_min DOUBLE PRECISION,salary_max DOUBLE PRECISION,
              salary_is_predicted INTEGER,redirect_url TEXT,first_seen TEXT,last_seen TEXT,raw_json TEXT)''')
            for row in source.execute('SELECT * FROM jobs'):
                target.execute('''INSERT INTO raw.jobs VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT(id) DO UPDATE SET title=excluded.title,company=excluded.company,
                location=excluded.location,description=excluded.description,created=excluded.created,
                salary_min=excluded.salary_min,salary_max=excluded.salary_max,
                salary_is_predicted=excluded.salary_is_predicted,redirect_url=excluded.redirect_url,
                first_seen=excluded.first_seen,last_seen=excluded.last_seen,raw_json=excluded.raw_json''',row)
            target.execute('''CREATE TABLE IF NOT EXISTS raw.snapshots (
                snapshot_id TEXT PRIMARY KEY,collected_at TEXT,country TEXT,config_key TEXT,config_json TEXT)''')
            target.execute('''CREATE TABLE IF NOT EXISTS raw.snapshot_jobs (
                snapshot_id TEXT REFERENCES raw.snapshots(snapshot_id),job_id TEXT,payload TEXT,
                PRIMARY KEY(snapshot_id,job_id))''')
            for row in source.execute('SELECT * FROM snapshots'):
                target.execute('INSERT INTO raw.snapshots VALUES (%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING',row)
            for row in source.execute('SELECT * FROM snapshot_jobs'):
                target.execute('INSERT INTO raw.snapshot_jobs VALUES (%s,%s,%s) ON CONFLICT DO NOTHING',row)
    except psycopg.Error:
        raise RuntimeError('PostgreSQL export failed. Check connection settings and permissions; credentials are not printed.') from None
    print(f'Loaded {args.mode} postings and snapshots into PostgreSQL.')

if __name__=='__main__':
    try:
        main()
    except RuntimeError as error:
        raise SystemExit(str(error)) from None
