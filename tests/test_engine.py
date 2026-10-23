import json
import tempfile
import unittest
from pathlib import Path
from topopatch.demo import fixture
from topopatch.engine import Engine, MigrationError
from topopatch.benchmark import run

class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.e=Engine(); self.e.initialize(fixture())
    def tearDown(self): self.e.db.close()
    def test_initial_constraints(self): self.assertTrue(self.e.evaluate()['pass'])
    def test_cache_charges_once(self):
        self.e.materialize(['car-guide']); self.e.materialize(['car-guide'])
        self.assertEqual(self.e.get('charged_b'),1)
    def test_preview_is_non_durable(self):
        before=self.e.snapshot(); self.e.preview(['car-guide'])
        self.assertEqual(before,self.e.snapshot()); self.assertEqual(self.e.status()['active_b'],0)
    def test_safe_preview_commit_parity_and_rollback(self):
        p=self.e.propose()['recommended']; self.assertIsNotNone(p)
        payload=json.loads(self.e.db.execute('SELECT payload FROM previews WHERE id=?',(p['preview_id'],)).fetchone()[0])
        before=self.e.search('car fix engine',payload['ids'],payload['vectors'])
        self.e.commit(p['preview_id'])
        self.assertEqual(before,self.e.search('car fix engine'))
        self.assertTrue(self.e.evaluate()['pass'])
        self.e.rollback(); self.assertEqual(self.e.status()['active_b'],0)
    def test_unsafe_commit_rejected(self):
        rejected=[w for w in self.e.propose()['witnesses'] if not w['safe']]
        self.assertTrue(rejected,'Fixture must expose an unsafe migration')
        before=self.e.snapshot()
        with self.assertRaisesRegex(MigrationError,'Unsafe'): self.e.commit(rejected[0]['preview_id'])
        self.assertEqual(before,self.e.snapshot())
    def test_stale_source_rejected(self):
        p=self.e.preview(['car-guide']); self.e.update_source('car-guide','new content')
        with self.assertRaisesRegex(MigrationError,'Stale'): self.e.commit(p['id'])
    def test_stale_epoch_rejected(self):
        p=self.e.propose()['recommended']; self.e.commit(p['preview_id'])
        with self.assertRaisesRegex(MigrationError,'Stale'): self.e.commit(p['preview_id'])
    def test_invalid_objects(self):
        with self.assertRaises(MigrationError): self.e.preview(['missing'])
        with self.assertRaises(MigrationError): self.e.preview([])
    def test_dimension_and_dedup(self):
        p=self.e.preview(['car-guide']); result=self.e.search('car',p['ids'],p['vectors'])
        self.assertEqual(len(result),len({r['id'] for r in result}))
        self.assertNotEqual(self.e.a.dimension,self.e.b.dimension)
    def test_envelope_not_certified(self):
        e=self.e.envelope(2); self.assertFalse(e['full_b_guarantee'])
        self.assertEqual(e['status'],'HEURISTIC_UNBOUNDED')
    def test_fallback_validates_query(self):
        self.e.fallback('q-policy')
        q=fixture()['protected_queries'][-1]
        self.assertEqual(self.e.serve(q['text'],'q-policy'),self.e.search(q['text'],legacy=True))
        with self.assertRaises(MigrationError): self.e.serve('different','q-policy')
        self.e.update_source('password-policy','replacement text')
        self.assertEqual(self.e.get('fallback'),[])
    def test_restart_persists(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'state.sqlite'; e=Engine(path); e.initialize(fixture())
            p=e.propose()['recommended']; e.commit(p['preview_id']); snapshot=e.snapshot(); e.db.close()
            reopened=Engine(path); self.assertEqual(snapshot,reopened.snapshot()); self.assertTrue(reopened.evaluate()['pass']); reopened.db.close()
    def test_benchmark_separate_ledger(self):
        with tempfile.TemporaryDirectory() as d:
            report=run(fixture(),Path(d)/'report.json')
            self.assertEqual(report['evaluation_only_b_document_encodings'],40)
            self.assertLessEqual(report['baselines']['topopatch']['charged_b_documents'],40)
            self.assertEqual(report['baselines']['topopatch']['protected_violations'],0)

if __name__=='__main__': unittest.main()

class AdditionalTests(unittest.TestCase):
    def test_transaction_failure_rolls_back(self):
        import sqlite3
        e=Engine();e.initialize(fixture());p=e.propose()['recommended'];before=e.snapshot()
        e.db.execute("CREATE TRIGGER fail_commit BEFORE UPDATE OF active ON docs BEGIN SELECT RAISE(ABORT,'injected write failure'); END")
        with self.assertRaises(sqlite3.IntegrityError): e.commit(p['preview_id'])
        self.assertEqual(before,e.snapshot());self.assertEqual(e.get('writes'),0)
    def test_tampered_evidence_denied(self):
        e=Engine();e.initialize(fixture());p=e.propose()['recommended']
        raw=json.loads(e.db.execute('SELECT payload FROM previews WHERE id=?',(p['preview_id'],)).fetchone()[0])
        raw['vectors'][p['ids'][0]][0]+=0.5
        with e.db:e.db.execute('UPDATE previews SET payload=? WHERE id=?',(json.dumps(raw),p['preview_id']))
        with self.assertRaisesRegex(MigrationError,'integrity'): e.commit(p['preview_id'])
    def test_full_trajectory_completes(self):
        from topopatch.trajectory import migrate
        r=migrate(fixture());self.assertTrue(r['complete'])
        self.assertEqual(r['evidence']['status']['charged_b_document_encodings'],40)
        self.assertTrue(all(e['payload']['barrier']['pass'] for e in r['evidence']['events'] if e['kind']=='commit'))
    def test_stale_across_connections(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'shared.sqlite';a=Engine(path);a.initialize(fixture());p=a.propose()['recommended']
            b=Engine(path);b.update_source('car-guide','changed source')
            with self.assertRaisesRegex(MigrationError,'Stale'):a.commit(p['preview_id'])
            a.db.close();b.db.close()

class StrictEvidenceTests(unittest.TestCase):
    def test_unbounded_proposal_and_commit_fail_closed(self):
        e=Engine(require_bounded_evidence=True);e.initialize(fixture())
        with self.assertRaisesRegex(MigrationError,'unbounded'): e.propose()
        p=e.preview(['password-policy'])
        with self.assertRaisesRegex(MigrationError,'unbounded'): e.commit(p['id'])
        self.assertEqual(e.status()['active_b'],0)
