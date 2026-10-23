"""Exact mixed-state retrieval, immutable preview records and transactional commits.

Safety is exact ONLY for declared queries against current mixed-state vectors.
It does not certify unseen queries or equivalence to a complete target index.
"""
import hashlib
import itertools
import json
import sqlite3
import time
import re
from pathlib import Path
from .models import LexicalEncoder, similarity


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',',':')).encode()).hexdigest()

class MigrationError(ValueError):
    pass

class Engine:
    def __init__(self, path=':memory:', model_a=None, model_b=None, require_bounded_evidence=False, fusion='rrf', exhaustive_evidence=False):
        self.db = sqlite3.connect(str(path), check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.a, self.b = model_a or LexicalEncoder(), model_b or LexicalEncoder(True)
        self.query_cache = {}
        self.require_bounded_evidence = require_bounded_evidence
        self.exhaustive_evidence = exhaustive_evidence
        if fusion not in ('rrf','continuity'): raise MigrationError('Unknown fusion policy')
        self.fusion = fusion
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS state(key TEXT PRIMARY KEY,value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS docs(id TEXT PRIMARY KEY,text TEXT,version INTEGER,hash TEXT,a TEXT,b TEXT,active TEXT);
        CREATE TABLE IF NOT EXISTS cache(id TEXT,hash TEXT,vector TEXT,PRIMARY KEY(id,hash));
        CREATE TABLE IF NOT EXISTS previews(id TEXT PRIMARY KEY,payload TEXT);
        CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY AUTOINCREMENT,kind TEXT,payload TEXT,at REAL);
        ''')
        self.db.commit()
        saved_fusion=self.get('fusion')
        if saved_fusion and saved_fusion!=fusion: raise MigrationError('Fusion policy does not match persisted experiment')
        saved=self.get('model_pair')
        if saved and saved != [self.a.identity,self.b.identity]:
            raise MigrationError('Model pair does not match persisted experiment')

    def get(self,key,default=None):
        row=self.db.execute('SELECT value FROM state WHERE key=?',(key,)).fetchone()
        return json.loads(row[0]) if row else default

    def put(self,key,value):
        self.db.execute('INSERT OR REPLACE INTO state VALUES (?,?)',(key,json.dumps(value)))

    def event(self,kind,payload):
        self.db.execute('INSERT INTO events(kind,payload,at) VALUES (?,?,?)',(kind,json.dumps(payload),time.time()))

    def rows(self):
        return [dict(r) for r in self.db.execute('SELECT * FROM docs ORDER BY id')]

    def initialize(self, fixture):
        if self.rows(): raise MigrationError('Experiment already initialized; use a new database')
        docs=fixture['documents']; queries=fixture['protected_queries']
        ids=[d['id'] for d in docs]
        if not ids or len(ids)!=len(set(ids)): raise MigrationError('Document IDs must be unique and nonempty')
        if not queries: raise MigrationError('At least one protected query is required')
        if any(not isinstance(d['id'],str) or not d['id'] or not isinstance(d['text'],str) for d in docs):
            raise MigrationError('Documents require nonempty string IDs and text strings')
        qids=[q['id'] for q in queries]
        if len(set(qids))!=len(qids): raise MigrationError('Query IDs must be unique')
        for q in queries:
            if q['required'] not in ids or not 1<=q['max_rank']<=len(ids): raise MigrationError('Invalid protected constraint')
        with self.db:
            for d in docs:
                self.db.execute('INSERT INTO docs VALUES (?,?,?,?,?,?,?)',(d['id'],d['text'],1,digest(d['text']),json.dumps(self.a.encode(d['text'])),None,'A'))
            self.put('epoch',0); self.put('fixture',fixture); self.put('fallback',[])
            self.put('charged_b',0); self.put('query_b',0); self.put('writes',0)
            self.put('fixture_hash',digest(fixture)); self.put('model_pair',[self.a.identity,self.b.identity]); self.put('fusion',self.fusion)
            self.event('initialized',{'corpus_hash':digest(docs)})

    def snapshot(self):
        return digest({'epoch':self.get('epoch'), 'rows':[(r['id'],r['hash'],r['version'],r['active']) for r in self.rows()], 'models':self.get('model_pair'),'fusion':self.fusion, 'progress_gate':self.get('progress_gate')})

    def materialize(self, ids):
        rows={r['id']:r for r in self.rows()}
        if not set(ids)<=rows.keys(): raise MigrationError('Unknown object ID')
        vectors={}
        with self.db:
            for id in sorted(set(ids)):
                r=rows[id]
                cached=self.db.execute('SELECT vector FROM cache WHERE id=? AND hash=?',(id,r['hash'])).fetchone()
                if cached: vector=json.loads(cached[0])
                else:
                    vector=self.b.encode(r['text'])
                    self.db.execute('INSERT INTO cache VALUES (?,?,?)',(id,r['hash'],json.dumps(vector)))
                    self.put('charged_b',self.get('charged_b',0)+1)
                vectors[id]=vector
        return vectors

    def search(self,text, selected=(), vectors=None, legacy=False):
        selected=set(selected); vectors=vectors or {}
        if text not in self.query_cache:
            self.query_cache[text]=(self.a.encode(text),self.b.encode(text))
            was_in_transaction=self.db.in_transaction
            self.put('query_b',self.get('query_b',0)+1)
            if not was_in_transaction: self.db.commit()
        qa,qb=self.query_cache[text]
        groups={'A':[], 'B':[]}
        current_rows=self.rows()
        for r in current_rows:
            model='A' if legacy else ('B' if r['id'] in selected else r['active'])
            if self.fusion=='continuity' and not legacy:
                groups['A'].append((r['id'],similarity(qa,json.loads(r['a']))))
            vec=json.loads(r['a']) if model=='A' else vectors.get(r['id'],json.loads(r['b']) if r['b'] else None)
            if vec is None: raise MigrationError('Missing target vector')
            if self.fusion!='continuity' or model=='B' or legacy:
                groups[model].append((r['id'],similarity(qa if model=='A' else qb,vec)))
        fused={}
        target_ids={id for id,_ in groups['B']}
        target_fraction=len(target_ids)/len(current_rows) if current_rows else 0
        for space,results in groups.items():
            results.sort(key=lambda x:(-x[1],x[0]))
            weight=(1-target_fraction if space=='A' else target_fraction) if self.fusion=='continuity' and not legacy else 1.0
            for rank,(id,score) in enumerate(results,1): fused[id]=fused.get(id,0)+weight/(60+rank)
        return [{'id':id,'score':score} for id,score in sorted(fused.items(),key=lambda x:(-x[1],x[0] not in target_ids,x[0]))]


    def progress_score(self,selected=(),vectors=None):
        config=self.get('progress_gate')
        if not config: return None
        import math
        values=[]
        for q in config['queries']:
            rank=[r['id'] for r in self.search(q['text'],selected,vectors)[:10]]
            relevant=set(q['relevant'])
            dcg=sum(1/math.log2(i+2) for i,id in enumerate(rank) if id in relevant)
            ideal=sum(1/math.log2(i+2) for i in range(min(10,len(relevant))))
            values.append(dcg/ideal if ideal else 0.0)
        return sum(values)/len(values)

    def evaluate(self,selected=(),vectors=None):
        results=[]
        for q in self.get('fixture')['protected_queries']:
            ranking=self.search(q['text'],selected,vectors)
            rank=next(i+1 for i,r in enumerate(ranking) if r['id']==q['required'])
            results.append({'query_id':q['id'],'required':q['required'],'rank':rank,'max_rank':q['max_rank'],'pass':rank<=q['max_rank']})
        progress=self.progress_score(selected,vectors)
        config=self.get('progress_gate')
        progress_ok=progress is None or progress+1e-12>=config['minimum_ndcg_at_10']
        return {'pass':all(r['pass'] for r in results) and progress_ok,'constraints':results,'progress_ndcg_at_10':progress,'progress_pass':progress_ok,'mode':'exact_declared_queries_mixed_state',
                'scope':'No guarantee for unseen queries or full-B top-k equivalence'}

    def envelope(self,limit=8):
        if not isinstance(limit,int) or limit<1: raise MigrationError('Candidate limit must be positive')
        if self.exhaustive_evidence:
            rows=self.rows()
            self.materialize([r['id'] for r in rows])
            evidence={'ids':[r['id'] for r in rows if r['active']=='A'],
                      'target_coverage':1.0,'status':'RESOLVED_EXHAUSTIVE',
                      'full_b_guarantee':False,
                      'explanation':'Every current source has a target vector. Candidate coverage is complete; mixed retrieval is not guaranteed equivalent to full B. All target encodings are charged.'}
            with self.db: self.event('envelope',evidence)
            return evidence
        ids=set()
        for q in self.get('fixture')['protected_queries']:
            ids.update(r['id'] for r in self.search(q['text'])[:limit])
            terms=set(re.findall(r'[a-z0-9]+',q['text'].lower()))
            lexical=sorted(((r['id'],len(terms & set(re.findall(r'[a-z0-9]+',r['text'].lower())))) for r in self.rows()),key=lambda x:(-x[1],x[0]))
            ids.update(id for id,overlap in lexical[:limit] if overlap>0)
            ids.add(q['required'])
        active={r['id'] for r in self.rows() if r['active']=='B'}
        ids-=active
        self.materialize(ids)
        evidence={'ids':sorted(ids),'target_coverage':len(ids|active)/len(self.rows()),
                  'status':'HEURISTIC_UNBOUNDED','full_b_guarantee':False,
                  'explanation':'Legacy candidates do not bound unseen target-model competitors.'}
        with self.db: self.event('envelope',evidence)
        return evidence

    def preview(self,ids):
        initial_snapshot=self.snapshot()
        ids=sorted(set(ids)); rows={r['id']:r for r in self.rows()}
        if not ids or not set(ids)<=rows.keys(): raise MigrationError('Select existing objects')
        if any(rows[id]['active']=='B' for id in ids): raise MigrationError('Object already migrated')
        vectors=self.materialize(ids)
        payload={'ids':ids,'epoch':self.get('epoch'),'snapshot':self.snapshot(),'vectors':vectors,
                 'source_hashes':{id:rows[id]['hash'] for id in ids},'barrier':self.evaluate(ids,vectors)}
        if initial_snapshot!=self.snapshot(): raise MigrationError('Source changed during preview; retry')
        id=digest(payload)
        with self.db:
            self.db.execute('INSERT OR IGNORE INTO previews VALUES (?,?)',(id,json.dumps(payload)))
            self.event('preview',{'id':id,'ids':ids,'barrier':payload['barrier']})
        return {'id':id,**payload}

    def commit(self,id):
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            row=self.db.execute('SELECT payload FROM previews WHERE id=?',(id,)).fetchone()
            if not row: raise MigrationError('Unknown preview')
            p=json.loads(row[0])
            if p['snapshot']!=self.snapshot(): raise MigrationError('Stale preview: source or epoch changed')
            current={r['id']:r for r in self.rows()}
            if any(current[id]['hash']!=h for id,h in p['source_hashes'].items()):
                raise MigrationError('Stale source embedding')
            if digest(p)!=id: raise MigrationError('Preview evidence integrity failure')
            covered=self.db.execute('SELECT COUNT(*) FROM docs d JOIN cache c ON d.id=c.id AND d.hash=c.hash').fetchone()[0]==len(current)
            if self.require_bounded_evidence and not (self.exhaustive_evidence and covered):
                raise MigrationError('Candidate evidence unbounded; durable commit fails closed')
            check=self.evaluate(p['ids'],p['vectors'])
            if not check['pass']: raise MigrationError('Unsafe preview: commit denied')
            before={r['id']:r['active'] for r in self.rows()}
            for object_id in p['ids']:
                self.db.execute("UPDATE docs SET b=?,active='B' WHERE id=?",(json.dumps(p['vectors'][object_id]),object_id))
            epoch=self.get('epoch')+1; self.put('epoch',epoch)
            self.put('writes',self.get('writes')+len(p['ids']))
            manifest={'epoch':epoch,'preview_id':id,'ids':p['ids'],'before':before,'after_snapshot':self.snapshot(),'barrier':check}
            self.event('commit',manifest)
        return manifest

    def propose(self,limit=4,max_bundle=2):
        # Bounded exhaustive candidates; no claim of global minimum.
        envelope=self.envelope(limit)
        if self.require_bounded_evidence and envelope['status']!='RESOLVED_EXHAUSTIVE':
            raise MigrationError('Candidate evidence unbounded; protected migration fails closed')
        candidates=envelope['ids'][:24]
        base=self.evaluate(); base_ranks={r['query_id']:r['rank'] for r in base['constraints']}
        witnesses=[]; accepted=[]
        for size in range(1,min(max_bundle,2)+1):
            for ids in itertools.combinations(candidates,size):
                p=self.preview(ids)
                effects=[{'query_id':c['query_id'],'delta_rank':base_ranks[c['query_id']]-c['rank'],'pass':c['pass']} for c in p['barrier']['constraints']]
                witness={'preview_id':p['id'],'ids':list(ids),'effects':effects,'safe':p['barrier']['pass'],'cost_objects':size}
                witnesses.append(witness)
                if witness['safe']: accepted.append(witness)
            if accepted: break
        if not accepted:
            active={r['id'] for r in self.rows() if r['active']=='B'}
            expanded=sorted({q['required'] for q in self.get('fixture')['protected_queries']}-active)
            if expanded:
                p=self.preview(expanded)
                witness={'preview_id':p['id'],'ids':expanded,'effects':[{'query_id':c['query_id'],'delta_rank':base_ranks[c['query_id']]-c['rank'],'pass':c['pass']} for c in p['barrier']['constraints']], 'safe':p['barrier']['pass'],'cost_objects':len(expanded),'expansion':'protected-object bundle'}
                witnesses.append(witness)
                if witness['safe']: accepted.append(witness)
        accepted.sort(key=lambda w:(w['cost_objects'],-sum(e['delta_rank'] for e in w['effects']),w['ids']))
        result={'envelope':envelope,'witnesses':witnesses,'recommended':accepted[0] if accepted else None,
                'search_scope':{'candidate_cap':24,'max_bundle':min(max_bundle,2)},'optimality':'Minimum object count among enumerated actions only'}
        with self.db: self.event('proposal',result)
        return result

    def fallback(self,query_id):
        queries={q['id']:q for q in self.get('fixture')['protected_queries']}
        if query_id not in queries: raise MigrationError('Unknown protected query')
        q=queries[query_id]; result=self.search(q['text'],legacy=True)
        rank=next(i+1 for i,r in enumerate(result) if r['id']==q['required'])
        if rank>q['max_rank']: raise MigrationError('Legacy route does not satisfy this constraint')
        with self.db:
            self.put('fallback',sorted(set(self.get('fallback',[]))|{query_id}))
            self.event('fallback',{'query_id':query_id})
        return result

    def serve(self,text,query_id=None):
        if query_id:
            q=next((q for q in self.get('fixture')['protected_queries'] if q['id']==query_id),None)
            if not q or text!=q['text']: raise MigrationError('Query ID must match registered query text')
        return self.search(text,legacy=query_id in self.get('fallback',[]))

    def update_source(self,id,text):
        with self.db:
            if not self.db.execute('SELECT 1 FROM docs WHERE id=?',(id,)).fetchone(): raise MigrationError('Unknown object')
            self.db.execute("UPDATE docs SET text=?,version=version+1,hash=?,a=?,b=NULL,active='A' WHERE id=?",(text,digest(text),json.dumps(self.a.encode(text)),id))
            self.put('epoch',self.get('epoch')+1)
            self.put('fallback',[])  # Source changes invalidate previously validated legacy routes.
            self.event('source_update',{'id':id,'hash':digest(text),'reason':'Invalidates target representation'})

    def rollback(self):
        row=self.db.execute("SELECT payload FROM events WHERE kind='commit' ORDER BY seq DESC LIMIT 1").fetchone()
        if not row: raise MigrationError('No commit to roll back')
        commit=json.loads(row[0])
        if commit['epoch']!=self.get('epoch'): raise MigrationError('Rollback requires latest unchanged committed epoch')
        with self.db:
            for id,model in commit['before'].items(): self.db.execute('UPDATE docs SET active=? WHERE id=?',(model,id))
            self.put('epoch',self.get('epoch')+1)
            self.event('rollback',{'commit_epoch':commit['epoch'],'epoch':self.get('epoch')})
        return self.status()

    def status(self):
        rows=self.rows()
        return {'epoch':self.get('epoch'), 'documents':len(rows),'active_b':sum(r['active']=='B' for r in rows),
                'charged_b_document_encodings':self.get('charged_b',0),'b_query_encodings':self.get('query_b',0),
                'logical_index_writes':self.get('writes',0),'models':{'A':self.a.identity,'B':self.b.identity},
                'dimensions':{'A':self.a.dimension,'B':self.b.dimension},'fallback_queries':self.get('fallback',[]),
                'backend':'exact flat search; ANN topology work not measured','fusion':self.fusion,
                'evidence_policy':'exhaustive' if self.exhaustive_evidence else 'heuristic',
                'strict_evidence':self.require_bounded_evidence,
                'documents_detail':[{'id':r['id'],'text':r['text'],'active':r['active'],'version':r['version']} for r in rows]}

    def export(self):
        import platform
        return {'status':self.status(),'fixture':self.get('fixture'),'fixture_hash':self.get('fixture_hash'),
                'python':platform.python_version(),'platform':platform.platform(),
                'events':[{'seq':r['seq'],'kind':r['kind'],'payload':json.loads(r['payload']),'at':r['at']} for r in self.db.execute('SELECT * FROM events ORDER BY seq')]}
