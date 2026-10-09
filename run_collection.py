"""Collect, optionally export and transform, with a local overlap lock."""
import argparse
import fcntl
import os
from pathlib import Path
import subprocess
import sys
import pipeline


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode',choices=['demo','live'],default='live')
    parser.add_argument('--warehouse',action='store_true',help='Also export PostgreSQL and run dbt build.')
    args=parser.parse_args()
    pipeline.load_env()
    if args.mode=='live' and not all(os.environ.get(k) for k in ['ADZUNA_APP_ID','ADZUNA_APP_KEY']):
        parser.error('Configure ADZUNA_APP_ID and ADZUNA_APP_KEY in .env first.')
    if args.warehouse and args.mode!='live':
        parser.error('Warehouse export is only supported for live collections.')
    root=Path(__file__).resolve().parent
    (root/'data').mkdir(exist_ok=True)
    with (root/'data'/'collection.lock').open('w') as lock:
        try:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:
            raise SystemExit('Another collection is running; skipped.')
        subprocess.run([sys.executable,str(root/'pipeline.py'),'--mode',args.mode],check=True,cwd=root)
        if args.warehouse:
            subprocess.run([sys.executable,str(root/'export_postgres.py')],check=True,cwd=root)
            subprocess.run([str(Path(sys.executable).parent/'dbt'),'build','--profiles-dir','.','--no-send-anonymous-usage-stats'],check=True,cwd=root/'dbt')

if __name__=='__main__':
    try:
        main()
    except (RuntimeError,subprocess.CalledProcessError):
        raise SystemExit('Collection or warehouse step failed. See the preceding safe status message.') from None
