import tempfile
import unittest
from pathlib import Path
from topopatch.public_eval import load_scifact, score

class PublicDatasetTests(unittest.TestCase):
    @unittest.skipUnless(Path('data/scifact.zip').exists(),'dataset not downloaded')
    def test_deterministic_roles_and_corpus(self):
        a=load_scifact('data/scifact.zip',42,80,12)
        b=load_scifact('data/scifact.zip',42,80,12)
        self.assertEqual(a,b)
        self.assertEqual(len(a['documents']),80)
        ids={d['id'] for d in a['documents']}
        self.assertTrue(all(set(rel)<=ids for rel in a['qrels'].values()))
    def test_ndcg_bounds(self):
        self.assertEqual(score(['a'],{'a'}),1.0)
        self.assertEqual(score(['b'],{'a'}),0.0)
        self.assertGreater(score(['a','b'],{'a'}),score(['b','a'],{'a'}))
