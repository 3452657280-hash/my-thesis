"""逐段列出模板前 62 段的 run（文字、下划线、字号、字体），以及文本框批注，供排版脚本定位。"""
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parent.parent
d = Document(str(ROOT / "_build" / "template_shuxie.docx"))
for i, p in enumerate(d.paragraphs[:62]):
    if not p.text.strip() and not p._p.xpath(".//w:txbxContent"):
        continue
    print(f"--- {i} style={p.style.name} align={p.alignment}")
    for j, r in enumerate(p.runs):
        rf = r._element.rPr.find(qn("w:rFonts")) if r._element.rPr is not None else None
        east = rf.get(qn("w:eastAsia")) if rf is not None else None
        print(f"   {j}: {r.text!r} u={r.underline} sz={r.font.size.pt if r.font.size else None} b={r.font.bold} east={east}")
    for tb in p._p.xpath(".//w:txbxContent"):
        print("   [TEXTBOX]", "".join(t.text or "" for t in tb.iter(qn("w:t")))[:80])
for i in (126, 128, 129, 143, 146, 147, 157, 162, 181, 183, 192, 194, 205):
    p = d.paragraphs[i]
    pf = p.paragraph_format
    sz = [r.font.size.pt if r.font.size else None for r in p.runs]
    print(i, p.style.name, repr(p.text[:20]), "align", p.alignment, "indent", pf.first_line_indent, "sz", sz,
          "pagebreak", bool(p._p.xpath(".//w:br[@w:type='page']")) or pf.page_break_before)
