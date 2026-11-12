import sys
from docx import Document
from docx.oxml.ns import qn

doc = Document(sys.argv[1])
body = doc.element.body
print("body children:", len(body))
for i, p in enumerate(doc.paragraphs):
    ppr = p._p.pPr
    flags = []
    if ppr is not None:
        if ppr.find(qn("w:sectPr")) is not None:
            flags.append("SECTPR")
        if ppr.find(qn("w:pBdr")) is not None:
            flags.append("BORDER")
        if ppr.find(qn("w:framePr")) is not None:
            flags.append("FRAME")
    if any(br.get(qn("w:type")) == "page" for br in p._p.iter(qn("w:br"))):
        flags.append("PAGEBREAK")
    if p._p.find(".//" + qn("w:lastRenderedPageBreak")) is not None:
        flags.append("lrpb")
    ul = [r.text for r in p.runs if r.underline]
    if flags or ul:
        print(i, flags, "underlined:", ul[:6])
for si, s in enumerate(doc.sections):
    print(f"section {si}: page {s.page_width.cm:.2f}x{s.page_height.cm:.2f} "
          f"margins L{s.left_margin.cm:.2f} R{s.right_margin.cm:.2f} "
          f"T{s.top_margin.cm:.2f} B{s.bottom_margin.cm:.2f} start={s.start_type}")
    print("   header paras:", [p.text for p in s.header.paragraphs],
          "footer paras:", [p.text for p in s.footer.paragraphs],
          "footer xml has PAGE:", "PAGE" in s.footer._element.xml)
print(doc.paragraphs[24]._p.xml[:1500])
