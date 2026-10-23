"""Public BEIR SciFact evaluation with disjoint query roles and a cost ledger.

This is an experimental harness, not a proof of safety for unseen queries.
"""
import csv
import hashlib
import json
import random
import zipfile
from pathlib import Path
from .engine import Engine, digest
from .models import SentenceEncoder, LexicalEncoder, similarity

def load_scifact(zip_path, seed=42, corpus_limit=320, query_limit=36):
    raw=Path(zip_path).read_bytes(); archive=zipfile.ZipFile(zip_path)
    def read_jsonl(name):
        key=next(n for n in archive.namelist() if n.endswith(name))
        return [json.loads(line) for line in archive.read(key).decode().splitlines() if line]
    corpus={str(d['_id']):d for d in read_jsonl('corpus.jsonl')}
    queries={str(q['_id']):q['text'] for q in read_jsonl('queries.jsonl')}
    qrel_path=next(n for n in archive.namelist() if n.endswith('qrels/test.tsv'))
    rows=list(csv.DictReader(archive.read(qrel_path).decode().splitlines(),delimiter='\t'))
    qrels={}
    for row in rows:
        if int(row['score'])>0: qrels.setdefault(row['query-id'],set()).add(row['corpus-id'])
    eligible=[q for q in sorted(qrels) if q in queries and qrels[q]<=corpus.keys()]
    rng=random.Random(seed); rng.shuffle(eligible); eligible=eligible[:query_limit]
    relevant=set().union(*(qrels[q] for q in eligible))
    if len(relevant)>corpus_limit: raise ValueError('Corpus limit smaller than relevant set')
    distractors=sorted(corpus.keys()-relevant);rng.shuffle(distractors)
    ids=sorted(relevant|set(distractors[:corpus_limit-len(relevant)]))
    docs=[{'id':id,'text':(corpus[id].get('title','')+' '+corpus[id].get('text','')).strip()} for id in ids]
    return {'documents':docs,'query_text':{q:queries[q] for q in eligible},'qrels':{q:sorted(qrels[q]) for q in eligible},
            'source':'BEIR SciFact test qrels; relevance-aware sampled corpus (not full benchmark)',
            'source_zip_sha256':hashlib.sha256(raw).hexdigest(),'seed':seed,'corpus_limit':len(docs)}

def score(ranking, relevant, k=10):
    import math
    dcg=sum((1/math.log2(i+2)) for i,id in enumerate(ranking[:k]) if id in relevant)
    ideal=sum(1/math.log2(i+2) for i in range(min(k,len(relevant))))
    return dcg/ideal if ideal else 0

def run(scifact_zip, model_a_path, model_b_path, output, seed=42, corpus_limit=320, query_limit=36, envelope_limit=12, fusion='rrf'):
    data=load_scifact(scifact_zip,seed,corpus_limit,query_limit)
    a=LexicalEncoder() if model_a_path=='lexical' else SentenceEncoder(model_a_path)
    b=SentenceEncoder(model_b_path)
    qids=list(data['query_text']); rng=random.Random(seed+1);rng.shuffle(qids)
    train=qids[:len(qids)//3];development=qids[len(qids)//3:2*len(qids)//3];heldout=qids[2*len(qids)//3:]
    fixture={'documents':data['documents'],
             'protected_queries':[{'id':q,'text':data['query_text'][q],'required':data['qrels'][q][0], 'max_rank':10} for q in train],
             'progress_queries':[data['query_text'][q] for q in heldout]}
    engine=Engine(model_a=a,model_b=b,fusion=fusion);engine.initialize(fixture)
    # Freeze each protected rank at the actual legacy rank; a migration may not worsen it.
    initial=[]
    for q in train:
        ranks=[r['id'] for r in engine.search(data['query_text'][q],legacy=True)]
        position=ranks.index(data['qrels'][q][0])+1
        initial.append({'id':q,'text':data['query_text'][q],'required':data['qrels'][q][0], 'max_rank':position})
    fixture['protected_queries']=initial
    engine.put('fixture',fixture);engine.put('fixture_hash',digest(fixture));engine.db.commit()
    progress_queries=[{'id':q,'text':data['query_text'][q],'relevant':data['qrels'][q]} for q in development]
    engine.put('progress_gate',{'queries':progress_queries,'minimum_ndcg_at_10':0.0});engine.db.commit()
    floor=engine.progress_score()
    engine.put('progress_gate',{'queries':progress_queries,'minimum_ndcg_at_10':floor});engine.db.commit()
    # Evaluation-only full target vectors are outside the algorithm cache and ledger.
    full={d['id']:b.encode(d['text']) for d in data['documents']}
    def evaluate_state():
        ranks={q:[r['id'] for r in engine.search(data['query_text'][q])[:10]] for q in heldout}
        return sum(score(ranks[q],set(data['qrels'][q])) for q in heldout)/len(heldout)
    legacy=evaluate_state()
    full_ranks={q:[id for id,_ in sorted(((id,similarity(b.encode(data['query_text'][q]),v)) for id,v in full.items()),key=lambda x:(-x[1],x[0]))[:10]] for q in heldout}
    full_ndcg=sum(score(full_ranks[q],set(data['qrels'][q])) for q in heldout)/len(heldout)
    envelope=engine.envelope(envelope_limit)
    # Ground-truth candidate recall on protected queries. Never passed to optimizer.
    misses=[]
    for q in train:
        vector=b.encode(data['query_text'][q]); ranks=sorted(((id,similarity(vector,v)) for id,v in full.items()),key=lambda x:(-x[1],x[0]))[:10]
        misses.append(sum(id not in envelope['ids'] for id,_ in ranks)/10)
    # Evaluate a bounded, cost-aware action search including a no-barrier contrast.
    proposal=engine.propose(limit=max(1,envelope_limit//3),max_bundle=2)
    safe=proposal['recommended']; rejected=next((w for w in proposal['witnesses'] if not w['safe']),None)
    if safe: engine.commit(safe['preview_id'])
    after=evaluate_state()
    result={'dataset':{k:v for k,v in data.items() if k not in ('documents','query_text','qrels')},
            'models':{'A':a.identity,'B':b.identity},'fusion':fusion,'splits':{'protected':train,'development':development,'heldout':heldout},
            'measures':{'legacy_ndcg_at_10':legacy,'selective_ndcg_at_10':after,'full_b_ndcg_at_10':full_ndcg,
                        'protected_violations':sum(not x['pass'] for x in engine.evaluate()['constraints']),
                        'development_ndcg_floor':floor,'development_ndcg_after':engine.progress_score(),
                        'candidate_envelope_full_b_top10_miss_fraction':sum(misses)/len(misses),
                        'charged_b_document_encodings':engine.status()['charged_b_document_encodings'],
                        'evaluation_only_b_document_encodings':len(full),'migrated_objects':engine.status()['active_b'],
                        'corpus_size':len(full),'barrier_rejected_candidates':sum(not w['safe'] for w in proposal['witnesses'])},
            'safe_action':safe,'unsafe_action_example':rejected,
            'scope':'Reduced SciFact corpus includes all relevant test documents for sampled queries; metrics are conditional on this sample, not BEIR leaderboard scores.',
            'evidence':engine.export()}
    path=Path(output);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(result,indent=2));return result
