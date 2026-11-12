"""打印封面段落（题目与各字段）的 run 文本、下划线、字号和字体，用于对齐下划线长度。"""
import sys

from docx import Document
from docx.oxml.ns import qn

path = sys.argv[1]
doc = Document(path)
for i in range(8, 23):
    p = doc.paragraphs[i]
    print(f"--- para {i} align={p.alignment} text={p.text!r}")
    for j, r in enumerate(p.runs):
        rpr = r._element.rPr
        fonts = rpr.find(qn("w:rFonts")) if rpr is not None else None
        fdesc = {k.split('}')[1]: v for k, v in fonts.attrib.items()} if fonts is not None else {}
        sz = r.font.size.pt if r.font.size else None
        print(f"   run{j}: {r.text!r} u={r.underline} sz={sz} fonts={fdesc}")
