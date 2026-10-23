"""Replace the supplied PDF's two old screenshot pages with fresh verifiable evidence."""
from pathlib import Path
from io import BytesIO
import json, hashlib
from PIL import Image
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'artifacts_private/proof-2026-10-17'
OUT=ROOT/'output/pdf';OUT.mkdir(parents=True,exist_ok=True)
SOURCE=BASE/'source-disclosure.pdf'
report=json.loads((BASE/'browser-report.json').read_text());assert report['complete']
assert 'Ran 30 tests' in (BASE/'test-results.txt').read_text() and '\nOK\n' in (BASE/'test-results.txt').read_text()
W,H=841.89,595.28
buf=BytesIO();c=canvas.Canvas(buf,pagesize=(W,H))
style=ParagraphStyle('body',fontName='Helvetica',fontSize=10,leading=14,textColor='#263c34')
def text(s,x,y,width=745):
 p=Paragraph(s,style);_,h=p.wrap(width,1000);p.drawOn(c,x,y-h);return y-h
page_no=0
def header(title,subtitle):
 global page_no
 page_no+=1;c.setFillColorRGB(.075,.235,.196);c.rect(0,H-78,W,78,fill=1,stroke=0)
 c.setFillColorRGB(1,1,1);c.setFont('Helvetica-Bold',19);c.drawString(42,H-35,title)
 c.setFont('Helvetica',10);c.drawString(42,H-57,subtitle)
 c.setFillColorRGB(.2,.3,.25)
def footer():
 c.setFont('Helvetica',8);c.drawString(42,24,'TopoPatch | Fresh prototype proof | 17 October 2026 | Authored lexical fixture unless stated')
 c.showPage()
header('Prototype proof - fresh verification record','Current rerun supersedes the two older screenshot figures; earlier experiment text remains historical.')
y=H-100
for s in [
 '<b>30 automated tests passed; '+str(len(report['checks']))+' browser/API workflow checks passed.</b> The flow used new SQLite databases, a real headless Chromium browser and the project HTTP server. Screenshots are actual captures, not simulated interfaces.',
 '<b>Measured flow:</b> 0 target-active objects / epoch 0; discovery charges 14 target vectors; car-guide fails q-policy (rank 2, maximum 1) and direct HTTP commit is refused; password-policy commits with all four checks passing; actual server restart preserves epoch 1 and one target-active object; rollback reaches epoch 2 and zero target-active objects while retaining 14 charged encodings.',
 '<b>Strengthening implemented:</b> rollback now acquires BEGIN IMMEDIATE before reading the latest commit and checking its epoch. A regression test attempts a second-connection write during that check and verifies it is locked out. An injected rollback write failure preserves the snapshot and event history. This addresses the rollback race noted in the earlier technical discussion, within the tested local SQLite scope.',
 '<b>Admission now visible:</b> preview responses expose the evidence-policy decision separately from protected-query rank checks. Strict mode disables the commit button for unbounded evidence even when ranks pass. Exhaustive strict mode computes all 40 target vectors and commits the actual recommended four-document bundle.',
 '<b>Evidence:</b> browser-report.json, per-step JSON exports, the browser-downloaded evidence file, prototype-proof-trace.json, test-results.txt, benchmark.json and trajectory.json are bundled with source and full-resolution screenshots. SHA-256 hashes identify the packaged bytes; they are not signatures or priority certification.',
 '<b>Interpretation:</b> these results support the demonstrated admission-control and recovery mechanism. The fixture benchmark remains 0.80 full-B top-5 overlap versus 0.95 for legacy A. The full trajectory migrates all 40 objects and charges all 40 target vectors. Better general retrieval quality, total compute savings and patentability are not established.'
]: y=text(s,42,y)-15
footer()
figures=[
 ('01-initial','1. Fresh experiment','Epoch 0; active target vectors 0; charged target document encodings 0. All four declared query rules pass.','01-initial.json',True),
 ('02-analysis','2. Candidate discovery','14 candidates: one admissible singleton and 13 rejected singletons. Discovery has charged 14 vectors while active membership remains zero.','browser-report.json',False),
 ('03-unsafe-preview','3. Unsafe action refused','car-guide pushes q-policy to rank 2 (maximum 1). Commit is disabled. A separate direct HTTP commit attempt also returns 400; membership remains unchanged.','browser-report.json / prototype-proof-trace.json',False),
 ('04-safe-preview','4. Passing action inspected','password-policy passes all four declared rules. The evidence ID binds the preview. The engine proof checks that predicted and committed top-five results match.','prototype-proof-trace.json',False),
 ('05-committed','5. Durable commit','Epoch 1; one active target object; 14 target encodings charged; all four protected rules pass. The browser evidence download independently contains this state.','05-committed.json / 06-browser-download.json',True),
 ('06-live-search','6. Search the committed state','The real search form returns password-policy first for password account policy. This demonstrates serving against the committed mixed membership.','browser-report.json',False),
 ('07-restarted','7. Persistence after server restart','The server process was stopped and restarted with the same SQLite file. The reloaded browser still reports epoch 1 and one active target object.','browser-report.json',True),
 ('08-fallback','8. Validated legacy fallback','The q-policy fallback is visibly active. The API accepts its registered query text and rejects a mismatched query ID/text combination.','browser-report.json',False),
 ('09-rollback','9. Rollback with cost retained','Epoch 2; zero active target objects; 14 encodings remain charged. Reusing the pre-rollback preview is refused as stale.','09-rolled-back.json / browser-report.json',True),
 ('10-strict-refusal','10. Fail-closed evidence policy','Separate fresh strict-mode run: password-policy passes rank checks, but unbounded candidate evidence blocks durable commit and disables the button.','browser-report.json / tests/test_hardening.py',False),
 ('11-exhaustive','11. Exhaustive strict admission','Separate fresh exhaustive run: all 40 target vectors are charged. The recommended protected-object bundle commits four objects with all declared checks passing.','11-exhaustive.json',True),
]
for name,title,caption,evidence,crop in figures:
 header(title,'Actual local browser capture | '+('Overview crop; full image retained in evidence package' if crop else ('Preview detail crop; full image retained in evidence package' if name in ('03-unsafe-preview','04-safe-preview') else 'Workbench or retrieval panel capture')))
 im=Image.open(BASE/'screenshots'/f'{name}.png')
 if crop:im=im.crop((270,400,1400,1068))
 if name in ('03-unsafe-preview','04-safe-preview'):im=im.crop((0,520,im.width,im.height))
 width,height=im.size;scale=min(750/width,378/height)
 dw,dh=width*scale,height*scale
 c.drawImage(ImageReader(im),(W-dw)/2,H-91-dh,width=dw,height=dh)
 text(caption,42,112)
 c.setFont('Helvetica',8);c.drawString(42,49,'Evidence: '+evidence)
 footer()
# Fresh public-data measurements are deliberately separate from the pictured fixture.
header('Additional reruns and scope','Neural target and public SciFact sample | Distinct from the browser fixture')
y=H-105
neural=json.loads((BASE/'neural-benchmark.json').read_text())
n=neural['baselines']['topopatch']
y=text(f"<b>Neural target fixture:</b> lexical A to cached MiniLM-L6 B. Full-B top-5 overlap {n['full_b_top5_overlap']:.2f}; protected violations {n['protected_violations']}; migrated objects {n['active_b']}; charged target document encodings {n['charged_b_documents']}. A separate evaluator encodes all 40 target documents.",42,y)-20
for name in ['scifact-rrf','scifact-continuity']:
 p=BASE/(name+'.json')
 if p.exists():
  r=json.loads(p.read_text());m=r['measures']
  y=text(f"<b>{name}:</b> 160-document relevance-aware sample, seed 42. Held-out nDCG@10: legacy {m['legacy_ndcg_at_10']:.4f}; selective {m['selective_ndcg_at_10']:.4f}; full B {m['full_b_ndcg_at_10']:.4f}. Protected violations: {m['protected_violations']}; migrated objects: {m['migrated_objects']}; charged target document encodings: {m['charged_b_document_encodings']}; separate evaluation-only target encodings: {m['evaluation_only_b_document_encodings']}.",42,y)-20
  y=text('Splits: '+', '.join(f'{k} {len(v)}' for k,v in r['splits'].items())+'. Full split IDs, model identities, selected actions and event history are in '+name+'.json.',42,y)-20
y=text('<b>How to interpret the rerun:</b> the existing public-data method and seed were rerun without tuning to the observed held-out scores. This is reproducibility evidence on a previously inspected small sample, not independent confirmation or a full BEIR benchmark. Historical numerical tables earlier in the disclosure use their recorded earlier splits and settings; compare the corresponding JSON rather than treating them as the same experiment.',42,y)-20
text('<b>Next evidentiary gap:</b> the prototype still needs a demonstrated quality/cost advantage on independent data with fair total-work baselines. Passing registered query checks alone does not establish that advantage. No novelty or patentability assessment was performed in this engineering rerun.',42,y)
footer();c.save();buf.seek(0)
original=PdfReader(SOURCE);assert len(original.pages)==17
assert 'Figure 4' in original.pages[12].extract_text() and 'Figure 5' in original.pages[13].extract_text()
writer=PdfWriter()
for page in list(original.pages[:12])+list(PdfReader(buf).pages)+list(original.pages[14:]):writer.add_page(page)
# Replace each page number in its existing footer area; keep original document content.
for i,page in enumerate(writer.pages):
 w,h=float(page.mediabox.width),float(page.mediabox.height)
 overlay=BytesIO();oc=canvas.Canvas(overlay,pagesize=(w,h))
 oc.setFillColorRGB(1,1,1);oc.rect(w-130,12,110,43,fill=1,stroke=0)
 oc.setFillColorRGB(.2,.2,.2);oc.setFont('Helvetica',8);oc.drawRightString(w-30,24,f'Page {i+1}');oc.save();overlay.seek(0)
 page.merge_page(PdfReader(overlay).pages[0])
writer.add_metadata({'/Title':'TopoPatch IDF-B - verified prototype proof, 17 October 2026','/Subject':'Fresh screenshots and reproducible engineering evidence; historical disclosure retained'})
target=OUT/'TopoPatch_IDF_B_verified_proof.pdf'
with target.open('wb') as f:writer.write(f)
print(target, len(writer.pages),'pages')
