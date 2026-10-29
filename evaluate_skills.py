"""Replay AI-reviewed mention labels against a private SQLite collection."""
import argparse
import hashlib
import json
import sqlite3
from pathlib import Path
import pipeline


def evaluate(database, annotations):
    counts = {skill: dict(tp=0, fp=0, fn=0, support=0) for skill in pipeline.PATTERNS}
    exact = 0
    with sqlite3.connect(database) as db:
        for record in annotations['records']:
            saved = db.execute('SELECT payload FROM snapshot_jobs JOIN snapshots USING(snapshot_id) WHERE job_id=? AND collected_at=?', (record['id'], annotations['source_observation'])).fetchone()
            if saved is None:
                raise ValueError('Annotated record is missing; use the original collection.')
            payload = json.loads(saved[0])
            text = payload['title'] + ' ' + (payload['description'] or '')
            if record.get('text_sha256') and hashlib.sha256(text.encode()).hexdigest() != record['text_sha256']:
                raise ValueError('Annotated text changed; use the original collection.')
            expected, predicted = set(record['expected']), set(pipeline.skills(text))
            if not expected <= counts.keys():
                raise ValueError('Unknown annotation label.')
            exact += expected == predicted
            for skill, c in counts.items():
                c['tp'] += skill in expected and skill in predicted
                c['fp'] += skill not in expected and skill in predicted
                c['fn'] += skill in expected and skill not in predicted
                c['support'] += skill in expected
    total = {k: sum(c[k] for c in counts.values()) for k in ('tp', 'fp', 'fn')}
    def metrics(c):
        return dict(c, precision=c['tp'] / (c['tp'] + c['fp']) if c['tp'] + c['fp'] else None,
                    recall=c['tp'] / (c['tp'] + c['fn']) if c['tp'] + c['fn'] else None)
    return dict(records=len(annotations['records']), exact_matches=exact,
                reviewer=annotations['reviewer'], rule_version=pipeline.RULE_VERSION,
                micro=metrics(total), per_skill={s: metrics(c) for s, c in counts.items()})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', type=Path, required=True)
    parser.add_argument('--annotations', type=Path, default=Path(__file__).parent/'evaluation/annotations.json')
    parser.add_argument('--output', type=Path, default=Path(__file__).parent/'evaluation/results.json')
    args = parser.parse_args()
    if not args.database.is_file():
        parser.error('Collection database does not exist.')
    result = evaluate(args.database, json.loads(args.annotations.read_text()))
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result['micro']))
