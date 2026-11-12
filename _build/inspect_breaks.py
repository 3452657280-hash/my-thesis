"""列出文档中所有分页符、分节符和“段前分页”，以及它们前后的段落文本。"""
import sys

from docx import Document
from docx.oxml.ns import qn

doc = Document(sys.argv[1])
body = doc.element.body
items = list(body.iterchildren())
for i, el in enumerate(items):
    tag = el.tag.split('}')[1]
    if tag != "p":
        continue
    text = "".join(t.text or "" for t in el.iter(qn("w:t")))
    marks = []
    if el.find(".//" + qn("w:sectPr")) is not None:
        marks.append("SECTION")
    for br in el.iter(qn("w:br")):
        if br.get(qn("w:type")) == "page":
            marks.append("PAGEBREAK")
    ppr = el.find(qn("w:pPr"))
    if ppr is not None and ppr.find(qn("w:pageBreakBefore")) is not None:
        marks.append("BREAK_BEFORE")
    if marks:
        prev = ""
        for j in range(i - 1, -1, -1):
            if items[j].tag.endswith("}p"):
                prev = "".join(t.text or "" for t in items[j].iter(qn("w:t")))
                if prev.strip():
                    break
        print(f"#{i} {marks} text={text[:30]!r} prev={prev[:30]!r}")
