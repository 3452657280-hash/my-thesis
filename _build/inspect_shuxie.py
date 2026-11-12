"""查看毕业论文模板的分节、页码、页脚结构（排版脚本的依据）。"""
import importlib.util as u
import os
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parent.parent
d = Document(str(ROOT / "_build" / "template_shuxie.docx"))
body = d.element.body
for i, el in enumerate(body.iterchildren()):
    if el.tag != qn("w:p"):
        continue
    ppr = el.find(qn("w:pPr"))
    s = ppr.find(qn("w:sectPr")) if ppr is not None else None
    if s is None:
        continue
    txt = "".join(t.text or "" for t in el.iter(qn("w:t")))[:30]
    pg = s.find(qn("w:pgNumType"))
    t = s.find(qn("w:type"))
    print(i, "SECT", repr(txt), "pgNum", None if pg is None else dict(pg.attrib),
          "type", None if t is None else t.get(qn("w:val")))
s = body.find(qn("w:sectPr"))
pg = s.find(qn("w:pgNumType"))
print("final", None if pg is None else dict(pg.attrib))
for k, sec in enumerate(d.sections):
    print(k, "footer PAGE fields:", sum(p._p.xml.count("PAGE") for p in sec.footer.paragraphs),
          "linked", sec.footer.is_linked_to_previous, sec.header.is_linked_to_previous)
st = {s.name for s in d.styles}
for name in ("Heading 1", "Heading 2", "Heading 3", "标题2", "标题3", "论文正文", "toc 1", "toc 2", "toc 3"):
    print(name, name in st)
print("latex2mathml", u.find_spec("latex2mathml") is not None)
for p in (r"C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL",
          r"C:\Program Files (x86)\Microsoft Office\root\Office16\MML2OMML.XSL"):
    print(p, os.path.exists(p))
