"""Package the current proof and source without mutable databases or old attempts."""
from pathlib import Path
import hashlib,json,zipfile
root=Path(__file__).resolve().parents[1]
files=[root/'README.md',root/'pyproject.toml',root/'deliverables/VERIFICATION_2026-10-17.md',root/'output/pdf/TopoPatch_IDF_B_verified_proof.pdf']
for folder,pattern in [('topopatch','**/*.py'),('topopatch/web','*'),('tests','*.py'),('web','*'),('data','*.zip')]:
 files.extend(p for p in (root/folder).glob(pattern) if p.is_file())
files.extend(root/'scripts'/name for name in ['capture_proof.cjs','prove_prototype.py','refresh_proof_pdf.py','package_verified_evidence.py'])
base=root/'artifacts_private/proof-2026-10-17'
files.extend(p for p in base.iterdir() if p.suffix in ('.json','.txt','.pdf'))
files.extend((base/'screenshots').glob('*.png'))
files=sorted(set(files))
manifest={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
mp=root/'deliverables/VERIFIED_SHA256_2026-10-17.json';mp.write_text(json.dumps(manifest,indent=2)+'\n')
output=root/'deliverables/TopoPatch_verified_evidence_2026-10-17.zip'
with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
 for p in files+[mp]:z.write(p,p.relative_to(root))
with zipfile.ZipFile(output) as z:
 assert z.testzip() is None
 for name,hash_ in manifest.items():assert hashlib.sha256(z.read(name)).hexdigest()==hash_
print(f'Archive verified: {len(manifest)} files, {output.stat().st_size:,} bytes')
