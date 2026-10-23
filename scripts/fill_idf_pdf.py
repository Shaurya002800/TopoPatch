"""Publish the rendered, self-contained IDF-B as the submission PDF."""
from pathlib import Path
from pypdf import PdfReader, PdfWriter

root = Path(__file__).resolve().parents[1]
source = root / 'artifacts_private/idf-b-unified/TopoPatch_IDF_B.pdf'
target = root / 'deliverables/TopoPatch_IDF_B_completed.pdf'
if not source.exists():
    raise SystemExit('Render the IDF-B DOCX before publishing the PDF.')
text = '\n'.join(page.extract_text() or '' for page in PdfReader(source).pages)
for number in range(1, 10):
    if f'{number} ' not in text:
        raise SystemExit(f'Missing section {number} in rendered PDF')
writer=PdfWriter()
for page in PdfReader(source).pages[:-1]:
    writer.add_page(page)
writer.add_page(PdfReader(root/'artifacts_private/vit-trl3-marked.pdf').pages[0])
with target.open('wb') as stream:
    writer.write(stream)
print(f'Published {len(PdfReader(target).pages)}-page IDF-B PDF')
