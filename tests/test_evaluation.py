import hashlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
import evaluate_skills


class EvaluationTests(unittest.TestCase):
    def test_scoring_and_missing_support(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'sample.sqlite'
            text = 'Analyst SQL and Python'
            with sqlite3.connect(path) as db:
                db.execute('CREATE TABLE snapshots(snapshot_id TEXT, collected_at TEXT)')
                db.execute('CREATE TABLE snapshot_jobs(snapshot_id TEXT, job_id TEXT, payload TEXT)')
                db.execute('INSERT INTO snapshots VALUES (?,?)', ('one', 'original'))
                db.execute('INSERT INTO snapshot_jobs VALUES (?,?,?)', ('one', 'id', json.dumps(dict(title='Analyst', description='SQL and Python'))))
            annotations = dict(reviewer='test', source_observation='original', records=[dict(id='id', text_sha256=hashlib.sha256(text.encode()).hexdigest(), expected=['SQL', 'Excel'])])
            result = evaluate_skills.evaluate(path, annotations)
            self.assertEqual(result['micro'], dict(tp=1, fp=1, fn=1, precision=.5, recall=.5))
            self.assertIsNone(result['per_skill']['AWS']['recall'])
            self.assertEqual(result['exact_matches'], 0)
            annotations['records'][0]['text_sha256'] = 'changed'
            with self.assertRaisesRegex(ValueError, 'changed'):
                evaluate_skills.evaluate(path, annotations)
            annotations['records'][0]['id'] = 'missing'
            with self.assertRaisesRegex(ValueError, 'missing'):
                evaluate_skills.evaluate(path, annotations)
