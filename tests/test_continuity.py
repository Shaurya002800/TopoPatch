import unittest
from topopatch.demo import fixture
from topopatch.engine import Engine

class ContinuityTests(unittest.TestCase):
    def test_endpoints_and_preview_parity(self):
        e=Engine(fusion='continuity');e.initialize(fixture())
        query='car fix engine'
        self.assertEqual(e.search(query),e.search(query,legacy=True))
        p=e.preview(['password-policy'])
        self.assertTrue(p['barrier']['pass'])
        preview=e.search(query,p['ids'],p['vectors'])
        e.commit(p['id'])
        self.assertEqual(preview,e.search(query))
        self.assertEqual(e.status()['fusion'],'continuity')
        remaining=[r['id'] for r in e.rows() if r['active']=='A']
        vectors=e.materialize(remaining)
        mixed=e.search(query,remaining,vectors)
        q=e.b.encode(query)
        from topopatch.models import similarity
        target=sorted(((r['id'],similarity(q,vectors.get(r['id']) or __import__('json').loads(r['b']))) for r in e.rows()),key=lambda x:(-x[1],x[0]))
        self.assertEqual([r['id'] for r in mixed],[id for id,_ in target])
        e.db.close()

class ProgressGateTests(unittest.TestCase):
    def test_progress_gate_rejects_regression(self):
        e=Engine();e.initialize(fixture())
        query='automobile repair engine'
        top=e.search(query)[0]['id']
        e.put('progress_gate',{'queries':[{'id':'progress','text':query,'relevant':[top]}], 'minimum_ndcg_at_10':1.0})
        e.db.commit()
        self.assertTrue(e.evaluate()['progress_pass'])
        for id in [r['id'] for r in e.rows() if r['active']=='A']:
            p=e.preview([id])
            if not p['barrier']['progress_pass']:
                with self.assertRaisesRegex(Exception,'Unsafe'):e.commit(p['id'])
                e.db.close()
                return
        e.db.close()
        self.fail('Fixture did not create a progress regression')
