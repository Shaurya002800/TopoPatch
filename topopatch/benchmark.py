"""Independent full-B evaluation and equal migration-count baseline comparison."""
import json
import random
import time
from pathlib import Path
from .engine import Engine, digest
from .models import similarity

def run(fixture, output, model_a=None, model_b=None):
    start=time.perf_counter()
    e=Engine(model_a=model_a,model_b=model_b); e.initialize(fixture)
    proposal=e.propose()
    recommendation=proposal['recommended']
    before=e.evaluate()
    if recommendation: e.commit(recommendation['preview_id'])
    selected=[r['id'] for r in e.rows() if r['active']=='B']
    # The full-B reference is created independently AFTER the algorithm finishes.
    full_vectors={d['id']:e.b.encode(d['text']) for d in fixture['documents']}
    queries=fixture.get('progress_queries',[])
    def ranking(text):
        q=e.b.encode(text)
        return [id for id,score in sorted(((id,similarity(q,v)) for id,v in full_vectors.items()),key=lambda x:(-x[1],x[0]))]
    references={q:ranking(q) for q in queries}
    def metrics(engine):
        overlaps=[]
        for q in queries:
            k=min(5,len(full_vectors)); actual=[r['id'] for r in engine.search(q)[:k]]
            overlaps.append(len(set(actual)&set(references[q][:k]))/k)
        safety=engine.evaluate()
        return {'full_b_top5_overlap':sum(overlaps)/len(overlaps) if overlaps else None,
                'protected_violations':sum(not c['pass'] for c in safety['constraints']),
                'active_b':engine.status()['active_b'],'charged_b_documents':engine.status()['charged_b_document_encodings']}
    comparisons={'topopatch':metrics(e)}
    for label,ids in [('legacy',[]),('full_b',list(full_vectors)),('random_equal_migration_count',random.Random(42).sample(sorted(full_vectors),len(selected)))]:
        baseline=Engine(model_a=model_a,model_b=model_b); baseline.initialize(fixture)
        vectors=baseline.materialize(ids)
        with baseline.db:
            for id in ids: baseline.db.execute("UPDATE docs SET b=?,active='B' WHERE id=?",(json.dumps(vectors[id]),id))
        comparisons[label]=metrics(baseline)
    report={'experiment':'Authored functional fixture; model identities recorded in evidence',
            'seed':42,'corpus_hash':digest(fixture),'algorithm':e.export(),'baselines':comparisons,
            'initial_barrier':before,'proposal':proposal,
            'evaluation_only_b_document_encodings':len(full_vectors),
            'elapsed_seconds':time.perf_counter()-start,
            'limitations':['Candidate envelope is heuristic and unbounded.',
                'Safety applies only to declared queries in the exact mixed index.',
                'Baseline matches committed object count, not total discovery budget; no superiority claim.',
                'Retained legacy vectors allow fallback and add storage overhead.',
                'No ANN repair, external benchmark dataset, or statistical generalization claim. See model identities for encoder type.']}
    output=Path(output); output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2))
    return report
