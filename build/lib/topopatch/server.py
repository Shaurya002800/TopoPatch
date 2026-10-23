"""Loopback-only single-threaded demo server. Not a production deployment."""
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse
from .engine import Engine, MigrationError
from .demo import fixture

WEB=Path(__file__).resolve().parent/'web'

def serve(path,port,model_b=None,dataset=None,fusion="rrf",evidence="heuristic"):
    if evidence not in ("heuristic","strict","exhaustive"): raise MigrationError("Unknown evidence policy")
    engine=Engine(path,model_b=model_b,fusion=fusion,require_bounded_evidence=evidence!="heuristic",exhaustive_evidence=evidence=="exhaustive")
    if not engine.rows(): engine.initialize(dataset or fixture())
    class Handler(BaseHTTPRequestHandler):
        def send_json(self,data,status=200):
            raw=json.dumps(data).encode(); self.send_response(status)
            self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(raw)))
            self.send_header('Cache-Control','no-store'); self.end_headers(); self.wfile.write(raw)
        def do_GET(self):
            route=urlparse(self.path).path
            if route=='/api/state': return self.send_json({'status':engine.status(),'barrier':engine.evaluate(),'queries':engine.get('fixture')['protected_queries']})
            if route=='/api/export': return self.send_json(engine.export())
            files={'/':'index.html','/app.js':'app.js','/style.css':'style.css'}
            if route not in files: return self.send_json({'error':'Not found'},404)
            p=WEB/files[route]; raw=p.read_bytes(); self.send_response(200)
            self.send_header('Content-Type',{'html':'text/html','js':'text/javascript','css':'text/css'}[p.suffix[1:]])
            self.send_header('Content-Length',str(len(raw))); self.end_headers(); self.wfile.write(raw)
        def do_POST(self):
            # Reject cross-origin browser writes to local service.
            origin=self.headers.get('Origin')
            if origin and origin not in (f'http://127.0.0.1:{port}',f'http://localhost:{port}'):
                return self.send_json({'error':'Origin rejected'},403)
            if self.headers.get('Content-Type','').split(';')[0]!='application/json':
                return self.send_json({'error':'JSON required'},415)
            try:
                size=int(self.headers.get('Content-Length','0'))
                if size<0 or size>100000: raise MigrationError('Request too large')
                data=json.loads(self.rfile.read(size)); route=urlparse(self.path).path
                if route=='/api/propose': result=engine.propose()
                elif route=='/api/preview': result=engine.preview(data['ids'])
                elif route=='/api/commit': result=engine.commit(data['id'])
                elif route=='/api/rollback': result=engine.rollback()
                elif route=='/api/fallback': result=engine.fallback(data['query_id'])
                elif route=='/api/search': result=engine.serve(data['text'],data.get('query_id'))
                else: return self.send_json({'error':'Not found'},404)
                return self.send_json(result)
            except (ValueError,KeyError,TypeError) as exc: return self.send_json({'error':str(exc)},400)
        def log_message(self,*args): pass
    print(f'TopoPatch running at http://127.0.0.1:{port}',flush=True)
    HTTPServer(('127.0.0.1',port),Handler).serve_forever()
