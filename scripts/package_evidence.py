from pathlib import Path
import hashlib,json,zipfile
root=Path(__file__).resolve().parents[1]
files=[root/'README.md',root/'pyproject.toml']
for folder,patterns in {'topopatch':['*.py','web/*'],'tests':['*.py'],'web':['*'],'scripts':['*.py'],'doc':['*.docx','*.pdf'],'docs_private':['*.md'],'data':['*.zip'],'artifacts_private':['*.json','*.jpg','test-results.txt','wheel-build.txt','wheels/*.whl'],'deliverables':['*.docx','*.pdf','*.md','*.png']}.items():
 for pat in patterns:files.extend(p for p in (root/folder).glob(pat) if p.is_file())
files=sorted(set(files));manifest={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
mp=root/'deliverables/SHA256_MANIFEST.json';mp.write_text(json.dumps(manifest,indent=2)+'\n')
out=root/'deliverables/TopoPatch_project_and_evidence.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 for p in files+[mp]:z.write(p,p.relative_to(root))
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 for name,h in manifest.items():assert hashlib.sha256(z.read(name)).hexdigest()==h
print(f'Verified {len(manifest)} files; archive {out.stat().st_size:,} bytes')
