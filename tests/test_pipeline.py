import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pipeline as p

class PipelineTests(unittest.TestCase):
    def test_skill_boundaries_and_aliases(self):
        self.assertEqual(p.skills('MySQL, PowerBI, AWS, LLMs and dbt.'),['SQL','Power BI','AWS','dbt','GenAI'])
        self.assertEqual(p.skills('excellent tableauish nosql pythonic'),[])
    def test_unknown_experience(self):
        self.assertIsNone(p.experience('Experienced analyst'))
        self.assertEqual(p.experience('Requires 2–4 years'),2)
        self.assertEqual(p.experience('Requires 2 to 4 years'),2)
    def test_idempotent_ingestion_and_first_seen(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(p,'ROOT',Path(tmp)):
            (Path(tmp)/'data').mkdir()
            with p.connect('demo') as db:
                job=p.demo()[0]
                p.save(db,[job],'in','Data Analyst','2026-01-01')
                p.save(db,[job],'in','BI Analyst','2026-01-02')
                self.assertEqual(db.execute('SELECT COUNT(*) FROM jobs').fetchone()[0],1)
                row=db.execute('SELECT first_seen,last_seen FROM jobs').fetchone()
                self.assertEqual(tuple(row),('2026-01-01','2026-01-02'))
                self.assertEqual(db.execute('SELECT COUNT(*) FROM job_queries').fetchone()[0],2)
                job['description']='Python only';job['title']='Analyst'
                p.save(db,[job],'in','Data Analyst','2026-01-03')
                self.assertEqual([r[0] for r in db.execute('SELECT skill FROM job_skills')],['Python'])
    def test_retry_and_safe_error(self):
        import urllib.error
        error=urllib.error.HTTPError('https://secret-url',401,'Unauthorized',{},None)
        with patch.dict(p.os.environ,{'ADZUNA_APP_ID':'secret-id','ADZUNA_APP_KEY':'secret-key'}), patch.object(p.urllib.request,'urlopen',side_effect=error):
            with self.assertRaisesRegex(RuntimeError,'HTTP 401') as caught:
                p.fetch('in','Analyst',1,20)
            self.assertNotIn('secret',str(caught.exception))
    def test_demo_is_deterministic(self):
        self.assertEqual(p.demo(),p.demo())


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        (self.root/'data').mkdir()
        (self.root/'dashboard-template.html').write_text('<script type="application/json">__DATA__</script>')
        self.patcher=patch.object(p,'ROOT',self.root);self.patcher.start()
        self.db=p.connect('demo')
        self.config=dict(queries=['Data Analyst'],pages=1,per_page=20)
    def tearDown(self):
        self.db.close();self.patcher.stop();self.tmp.cleanup()
    def observe(self,postings,stamp='2026-01-01T00:00:00+00:00',config=None):
        p.save(self.db,postings,'in','Data Analyst',stamp)
        return p.snapshot(self.db,postings,'in',stamp,config or self.config)
    def test_snapshot_preserves_old_skills(self):
        import json
        job=p.demo()[0];job['title']='Analyst';job['description']='SQL'
        key=self.observe([job,job])
        job['description']='Python';self.observe([job],'2026-01-02T00:00:00+00:00')
        prior=json.loads(self.db.execute('SELECT payload FROM snapshot_jobs WHERE snapshot_id=?',(key,)).fetchone()[0])
        self.assertEqual(prior['skills'],['SQL'])
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM snapshot_jobs WHERE snapshot_id=?',(key,)).fetchone()[0],1)
    def test_latest_sample_excludes_old_postings_and_config(self):
        import json
        self.observe(p.demo()[:3])
        self.observe(p.demo()[3:4],'2026-01-02T00:00:00+00:00',dict(self.config,pages=2))
        _,total=p.report(self.db,'demo','in')
        data=json.loads((self.root/'data'/'demo-analytics.json').read_text())
        self.assertEqual(total,1);self.assertEqual(len(data['history']),1)
    def test_empty_collection_is_not_previous_collection(self):
        self.observe(p.demo()[:3]);self.observe([],'2026-01-02T00:00:00+00:00')
        self.assertEqual(p.report(self.db,'demo','in')[1],0)
    def test_script_content_is_escaped(self):
        job=p.demo()[0];job['title']='</script><script>alert(1)</script>'
        self.observe([job]);path,_=p.report(self.db,'demo','in')
        self.assertNotIn('alert(1)</script>',path.read_text())
    def test_failure_rolls_back_partial_collection(self):
        with self.assertRaises(RuntimeError):
            with self.db:
                self.observe(p.demo()[:2])
                raise RuntimeError('API failure')
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM snapshots').fetchone()[0],0)
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM jobs').fetchone()[0],0)
    def test_string_predicted_flag_and_null_fields(self):
        job=p.demo()[0];job.update(company=None,location=None,description=None,salary_is_predicted='1')
        self.observe([job])
        row=self.db.execute('SELECT company,location,salary_is_predicted FROM jobs').fetchone()
        self.assertEqual(tuple(row),('Unknown','Unknown',1))
    def test_retry_rate_limit_then_success(self):
        import io
        import urllib.error
        error=urllib.error.HTTPError('https://private',429,'Rate limited',{},None)
        with patch.dict(p.os.environ,{'ADZUNA_APP_ID':'test','ADZUNA_APP_KEY':'test'}), patch.object(p.urllib.request,'urlopen',side_effect=[error,io.StringIO('{"results": []}')]) as call,patch.object(p.time,'sleep'):
            self.assertEqual(p.fetch('in','Analyst',1,20),[])
            self.assertEqual(call.call_count,2)
    def test_env_is_literal_and_does_not_override(self):
        (self.root/'.env').write_text("ADZUNA_APP_ID='$(do-not-execute)'\nADZUNA_APP_KEY=file-value\n")
        with patch.dict(p.os.environ,{'ADZUNA_APP_KEY':'environment-value'},clear=True):
            p.load_env()
            self.assertEqual(p.os.environ['ADZUNA_APP_ID'],'$(do-not-execute)')
            self.assertEqual(p.os.environ['ADZUNA_APP_KEY'],'environment-value')

if __name__=='__main__':unittest.main()
