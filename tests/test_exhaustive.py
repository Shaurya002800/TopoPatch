import unittest
from topopatch.engine import Engine, MigrationError
from topopatch.demo import fixture

class ExhaustiveEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.e=Engine(require_bounded_evidence=True,exhaustive_evidence=True)
        self.e.initialize(fixture())
    def tearDown(self): self.e.db.close()
    def test_coverage_charged_and_safe_commit(self):
        p=self.e.propose()
        self.assertEqual(p['envelope']['status'],'RESOLVED_EXHAUSTIVE')
        self.assertEqual(self.e.get('charged_b'),40)
        self.e.commit(p['recommended']['preview_id'])
        self.assertTrue(self.e.evaluate()['pass'])
    def test_source_update_invalidates_coverage(self):
        self.e.envelope();self.e.update_source('car-guide','changed')
        p=self.e.preview(['password-policy'])
        with self.assertRaisesRegex(MigrationError,'unbounded'):self.e.commit(p['id'])
    def test_policy_change_invalidates_preview(self):
        self.e.envelope();p=self.e.preview(['password-policy'])
        with self.e.db:self.e.put('progress_gate',{'queries':[{'text':'password','relevant':['password-policy']}],'minimum_ndcg_at_10':0})
        with self.assertRaisesRegex(MigrationError,'Stale'):self.e.commit(p['id'])
