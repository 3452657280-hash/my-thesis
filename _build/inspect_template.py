import sys
from docx import Document

path = sys.argv[1]
doc = Document(path)
print("sections:", len(doc.sections))
for i, p in enumerate(doc.paragraphs):
    runs = [(r.text, r.font.name, r.font.size.pt if r.font.size else None, r.bold) for r in p.runs]
    print(f"P{i:03d} style={p.style.name!r} align={p.alignment} text={p.text!r}")
    for r in runs:
        if r[0].strip():
            print("      run:", r)
print("tables:", len(doc.tables))
for ti, t in enumerate(doc.tables):
    print(f"T{ti} rows={len(t.rows)} cols={len(t.columns)}")
    for ri, row in enumerate(t.rows):
        for ci, cell in enumerate(row.cells):
            txt = cell.text.replace("\n", "\\n")
            print(f"   [{ri},{ci}] {txt[:80]!r} paras={len(cell.paragraphs)}")
