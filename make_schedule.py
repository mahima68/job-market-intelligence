"""Generate a daily macOS launchd schedule inside this project; no activation."""
import argparse
from pathlib import Path
import plistlib
import sys

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--hour',type=int,default=9)
parser.add_argument('--minute',type=int,default=0)
parser.add_argument('--warehouse',action='store_true')
args=parser.parse_args()
if not 0<=args.hour<=23 or not 0<=args.minute<=59:
    parser.error('Use hour 0–23 and minute 0–59.')
root=Path(__file__).resolve().parent
(root/'logs').mkdir(exist_ok=True)
arguments=[sys.executable,str(root/'run_collection.py'),'--mode','live']
if args.warehouse:
    arguments.append('--warehouse')
config={'Label':'local.job-market-intelligence','ProgramArguments':arguments,
        'WorkingDirectory':str(root),'StartCalendarInterval':{'Hour':args.hour,'Minute':args.minute},
        'StandardOutPath':str(root/'logs'/'collection.log'),
        'StandardErrorPath':str(root/'logs'/'collection-error.log'),
        'ProcessType':'Background'}
path=root/'daily-collection.plist'
path.write_bytes(plistlib.dumps(config))
print(f'Created {path.name}; not activated. Runs at {args.hour:02}:{args.minute:02} in the computer’s local time zone.')
