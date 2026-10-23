import argparse
import json
from pathlib import Path
from .demo import fixture

def main():
    p=argparse.ArgumentParser(description='TopoPatch local research prototype')
    sub=p.add_subparsers(dest='command',required=True)
    server=sub.add_parser('serve'); server.add_argument('--target-snapshot'); server.add_argument('--dataset'); server.add_argument('--port',type=int,default=8765); server.add_argument('--db',default='artifacts_private/demo.sqlite')
    server.add_argument('--fusion',choices=['rrf','continuity'],default='rrf')
    server.add_argument('--evidence',choices=['heuristic','strict','exhaustive'],default='heuristic')
    bench=sub.add_parser('benchmark'); bench.add_argument('--target-snapshot',help='Optional local Sentence Transformers model directory'); bench.add_argument('--dataset',help='JSON with documents, protected_queries, progress_queries'); bench.add_argument('--output',default='artifacts_private/benchmark.json')
    research=sub.add_parser('research'); research.add_argument('--seed',type=int,default=42); research.add_argument('--fusion',choices=['rrf','continuity'],default='rrf'); research.add_argument('--scifact-zip',default='data/scifact.zip'); research.add_argument('--model-a',required=True); research.add_argument('--model-b',required=True); research.add_argument('--output',default='artifacts_private/scifact-research.json'); research.add_argument('--corpus-limit',type=int,default=320); research.add_argument('--query-limit',type=int,default=36)
    args=p.parse_args()
    if args.command=='serve':
        from .server import serve
        Path(args.db).parent.mkdir(parents=True,exist_ok=True)
        target=None
        if args.target_snapshot:
            from .models import SentenceEncoder
            target=SentenceEncoder(args.target_snapshot)
        data=json.loads(Path(args.dataset).read_text()) if args.dataset else None
        serve(args.db,args.port,model_b=target,dataset=data,fusion=args.fusion,evidence=args.evidence)
    elif args.command=='research':
        from .public_eval import run
        report=run(args.scifact_zip,args.model_a,args.model_b,args.output,corpus_limit=args.corpus_limit,query_limit=args.query_limit,fusion=args.fusion,seed=args.seed)
        print(json.dumps({'output':args.output,'measures':report['measures'],'scope':report['scope']},indent=2))
    else:
        from .benchmark import run
        data=json.loads(Path(args.dataset).read_text()) if args.dataset else fixture()
        target=None
        if args.target_snapshot:
            from .models import SentenceEncoder
            target=SentenceEncoder(args.target_snapshot)
        report=run(data,args.output,model_b=target)
        print(json.dumps({'output':args.output,'baselines':report['baselines'],'evaluation_only_b_documents':report['evaluation_only_b_document_encodings']},indent=2))
if __name__=='__main__': main()
