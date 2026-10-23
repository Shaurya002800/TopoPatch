"""Reproducible functional proof of the local migration control sequence.

Produces a fresh JSON trace. It is a proof of exercised behaviour on the authored
40-document fixture, not a patentability or retrieval-generalization test.
"""
import json
import sqlite3
import tempfile
from pathlib import Path
from topopatch.demo import fixture
from topopatch.engine import Engine, MigrationError

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts_private/prototype-proof-trace.json'

def compact(e):
    s = e.status()
    return {'epoch':s['epoch'], 'active_b':s['active_b'],
            'charged_b_document_encodings':s['charged_b_document_encodings'],
            'writes':s['logical_index_writes'], 'snapshot':e.snapshot(),
            'protected':e.evaluate()['constraints']}

def main():
    proof={'fixture':{'documents':len(fixture()['documents']),
                      'protected_queries':len(fixture()['protected_queries'])},
           'scope':'Authored lexical fixture; exact local search and SQLite. Not a production or unseen-query guarantee.'}
    with tempfile.TemporaryDirectory(prefix='topopatch-proof-') as directory:
        db=Path(directory)/'trace.sqlite'
        e=Engine(db);e.initialize(fixture())
        initial=compact(e)
        proposal=e.propose()
        unsafe=next(w for w in proposal['witnesses'] if w['ids']==['car-guide'])
        safe=proposal['recommended']
        assert unsafe['safe'] is False and safe['safe'] is True
        assert safe['ids']==['password-policy']
        before_unsafe=e.snapshot()
        try:
            e.commit(unsafe['preview_id'])
            raise AssertionError('Unsafe action committed')
        except MigrationError as exc:
            unsafe_error=str(exc)
        assert e.snapshot()==before_unsafe
        precommit=compact(e)
        saved=json.loads(e.db.execute('SELECT payload FROM previews WHERE id=?',(safe['preview_id'],)).fetchone()[0])
        predicted=e.search('password account policy',saved['ids'],saved['vectors'])[:5]
        manifest=e.commit(safe['preview_id'])
        actual=e.search('password account policy')[:5]
        assert predicted==actual
        committed=compact(e)
        assert committed['active_b']==1 and committed['epoch']==1
        assert all(q['pass'] for q in committed['protected'])
        e.db.close()
        reopened=Engine(db)
        persisted=compact(reopened)
        assert persisted['snapshot']==committed['snapshot']
        reopened.rollback()
        rolled=compact(reopened)
        assert rolled['active_b']==0 and rolled['epoch']==2
        assert rolled['charged_b_document_encodings']==committed['charged_b_document_encodings']
        reopened.db.close()
        proof['sequence']={'initial':initial,
                           'candidate_status':proposal['envelope']['status'],
                           'witnesses_checked':len(proposal['witnesses']),
                           'unsafe':{'ids':unsafe['ids'],'effects':unsafe['effects'],
                                     'barrier_pass':unsafe['safe'],'commit_error':unsafe_error,
                                     'membership_unchanged':True},
                           'before_commit':precommit,
                           'safe':{'ids':safe['ids'],'effects':safe['effects'],
                                   'barrier_pass':safe['safe'],'preview_id':safe['preview_id']},
                           'prediction_matches_committed_top5':predicted==actual,
                           'commit':{'epoch':manifest['epoch'],'state':committed},
                           'restart_persists_snapshot':persisted['snapshot']==committed['snapshot'],
                           'rollback':rolled}
        strict=Engine(require_bounded_evidence=True);strict.initialize(fixture())
        try:
            strict.propose()
            raise AssertionError('Strict heuristic proposal accepted')
        except MigrationError as exc:
            strict_error=str(exc)
        proof['strict_heuristic']={'rejected':True,'reason':strict_error,
                                   'active_b':strict.status()['active_b']}
        strict.db.close()
        exhaustive=Engine(require_bounded_evidence=True,exhaustive_evidence=True)
        exhaustive.initialize(fixture())
        admitted=exhaustive.propose()['recommended']
        assert admitted and admitted['safe']
        exhaustive.commit(admitted['preview_id'])
        exstate=compact(exhaustive)
        assert exstate['charged_b_document_encodings']==40
        proof['strict_exhaustive']={'commit_passed':True,'charged_b_documents':40,
                                    'active_b':exstate['active_b'],'epoch':exstate['epoch'],
                                    'protected':exstate['protected']}
        exhaustive.db.close()
        fail=Engine();fail.initialize(fixture())
        pass_action=fail.propose()['recommended']
        earlier=fail.snapshot()
        fail.db.execute("CREATE TRIGGER injected_failure BEFORE UPDATE OF active ON docs BEGIN SELECT RAISE(ABORT,'injected write failure'); END")
        try:
            fail.commit(pass_action['preview_id'])
            raise AssertionError('Injected write failure did not fail')
        except sqlite3.IntegrityError as exc:
            injected_error=str(exc)
        assert fail.snapshot()==earlier and fail.status()['active_b']==0
        proof['write_failure']={'transaction_rolled_back':True,
                                'membership_unchanged':True,'reason':injected_error}
        fail.db.close()
    OUT.write_text(json.dumps(proof,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'output':str(OUT),'proof_checks':{
        'unsafe_rejected':True,'prediction_matches_commit':True,
        'restart_persists':True,'rollback_restores':True,
        'strict_heuristic_rejected':True,'strict_exhaustive_commit':True,
        'injected_write_rolled_back':True}},indent=2))

if __name__=='__main__':main()
