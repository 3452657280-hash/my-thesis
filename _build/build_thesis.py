r"""把 论文/*.md 填进学校毕业论文模板（_build/template_shuxie.docx），输出 docx。

用法：<项目 venv>\\Scripts\\python.exe -X utf8 _build/build_thesis.py
然后：powershell -File _build/word_update.ps1 _build/_thesis.docx _build/_pages   （更新目录与页码、导出每页预览）
      copy /y _build\_thesis.docx 论文_基于知识图谱增强大模型的产线故障诊断系统.docx

- 封面、原创性申明、授权书、页眉页脚和分节沿用模板；删除模板里的黄色格式批注文本框。
- 摘要页、目录（TOC 域）、正文、参考文献、致谢、附录按《编写格式规范》排版：
  章标题小三黑体居中、另起一页；节标题四号黑体；条标题小四黑体；正文小四宋体、英文 Times New Roman、
  1.35 倍行距、首行缩进 2 字符；表名在表上、图名在图下，五号宋体加粗居中；公式居中、编号右对齐。
- 公式：LaTeX → MathML（latex2mathml，装在 _build/_pylib）→ OMML（Office 自带 MML2OMML.XSL），Word 中可编辑。
- 正文里的【…】是待补内容，黄色高亮，便于定稿前逐个处理。
"""
import copy
import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX
from docx.image.image import Image as DocxImage
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from lxml import etree

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE / "_pylib"))
sys.path.insert(0, str(HERE))
import build_kaiti as bk  # noqa: E402  复用字体、三线表、列宽等工具
from latex2mathml.converter import convert as latex_to_mathml  # noqa: E402

TEMPLATE = HERE / "template_shuxie.docx"
PAPER = ROOT / "论文"
OUT = ROOT / "论文_基于知识图谱增强大模型的产线故障诊断系统.docx"
MML2OMML = Path(r"C:\Program Files (x86)\Microsoft Office\root\Office16\MML2OMML.XSL")

TITLE = "基于知识图谱增强大模型的产线故障诊断系统"
TITLE_EN = "Production Line Fault Diagnosis System Based on Knowledge Graph Enhanced Large Language Model"
YEARS = "（2023—2027年）"
# 封面各行的带下划线字段，按出现顺序填写；None 表示保留模板原样（空白）
COVER = {
    15: ["信息学科部", "计算机系"],
    16: ["软件工程", "软件工程234班"],
    17: ["王禹博", "7023123210"],
    18: ["邓伦丹", "【职称】"],
}
CHAPTERS = ["01_第1章_绪论.md", "02_第2章_相关技术.md", "03_第3章_需求分析.md", "04_第4章_总体设计.md",
            "05_第5章_关键技术与实现.md", "06_第6章_测试与实验.md", "07_第7章_总结与展望.md"]
N_REFS = 0  # 运行时按参考文献表设定，用于区分 [12] 这类引用和 [0,1] 这类区间

BODY_PT, SMALL_PT = bk.BODY_PT, bk.SMALL_PT
set_run_font, set_spacing = bk.set_run_font, bk.set_spacing

# ---------------------------------------------------------------- 行内格式
TOKEN_RE = re.compile(r"(\*\*.+?\*\*|\[\d+(?:[,，\-–]\d+)*\]|<sub>.+?</sub>|<sup>.+?</sup>|【[^】]*】)")


def _is_cite(tok):
    nums = [int(x) for x in re.findall(r"\d+", tok)]
    return all(1 <= n <= N_REFS for n in nums) and not tok.startswith("[0")


def add_inline(p, text, size=BODY_PT, bold=False, cite_superscript=True):
    text = re.sub(r"`([^`]+)`", r"\1", text)
    for part in TOKEN_RE.split(text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            add_inline(p, part[2:-2], size=size, bold=True, cite_superscript=cite_superscript)
        elif re.fullmatch(r"\[\d+(?:[,，\-–]\d+)*\]", part) and cite_superscript and _is_cite(part):
            set_run_font(p.add_run(part), size=size, bold=bold, superscript=True)
        elif part.startswith("<sub>"):
            set_run_font(p.add_run(part[5:-6]), size=size, bold=bold, subscript=True)
        elif part.startswith("<sup>"):
            set_run_font(p.add_run(part[5:-6]), size=size, bold=bold, superscript=True)
        elif part.startswith("【"):
            r = p.add_run(part)
            set_run_font(r, size=size, bold=bold)
            r.font.highlight_color = WD_COLOR_INDEX.YELLOW
        else:
            set_run_font(p.add_run(part), size=size, bold=bold)


bk.add_inline = add_inline  # 让 build_kaiti 里的表格单元格、正文都走这一版


# ---------------------------------------------------------------- 公式
_XSLT = etree.XSLT(etree.parse(str(MML2OMML)))


def latex_to_omml(latex):
    mml = etree.fromstring(latex_to_mathml(latex).encode("utf-8"))
    omml = _XSLT(mml).getroot()
    return omml  # m:oMath


def no_numbering(p):
    ppr = p._p.get_or_add_pPr()
    num = OxmlElement("w:numPr")
    for tag, val in (("w:ilvl", "0"), ("w:numId", "0")):
        el = OxmlElement(tag)
        el.set(qn("w:val"), val)
        num.append(el)
    ppr.append(num)


def set_outline(p, level):
    """level 0/1/2 进目录；9 = 正文级别（不进目录）。"""
    ppr = p._p.get_or_add_pPr()
    for old in ppr.findall(qn("w:outlineLvl")):
        ppr.remove(old)
    el = OxmlElement("w:outlineLvl")
    el.set(qn("w:val"), str(level))
    # 按 schema 顺序放在 rPr/sectPr/pPrChange 之前，否则 Word 会忽略（封面标题因此曾混进目录）
    after = next((c for c in ppr if c.tag in (qn("w:rPr"), qn("w:sectPr"), qn("w:pPrChange"))), None)
    if after is not None:
        after.addprevious(el)
    else:
        ppr.append(el)


class Writer(bk.Writer):
    first_chapter = True  # 正文第一章前已有分节符（下一页），不再加分页，避免空白页

    def heading(self, text, level, page_break=False):
        if level == 1 and self.first_chapter:
            page_break, self.first_chapter = False, False
        p = self.paragraph()
        p.style = self.doc.styles[f"Heading {level}"]
        no_numbering(p)
        size, align = {1: (15, WD_ALIGN_PARAGRAPH.CENTER), 2: (14, WD_ALIGN_PARAGRAPH.LEFT),
                       3: (BODY_PT, WD_ALIGN_PARAGRAPH.LEFT)}[level]
        set_spacing(p, first_indent=False, align=align)
        pf = p.paragraph_format
        pf.first_line_indent = Pt(0)
        pf.left_indent = Pt(0)
        pf.keep_with_next = True
        pf.page_break_before = page_break
        if level == 1:  # 章标题上下留一点空，便于阅读（模板示例亦如此）
            pf.space_before = Pt(12)
            pf.space_after = Pt(12)
        r = p.add_run(text)
        set_run_font(r, size=size, east="黑体", bold=False)
        r.font.color.rgb = RGBColor(0, 0, 0)
        set_outline(p, level - 1)
        return p

    def body(self, text):
        p = self.paragraph()
        set_spacing(p)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        add_inline(p, text)
        return p

    def code(self, line):
        p = self.paragraph()
        set_spacing(p, first_indent=False, line=1.0)
        p.paragraph_format.left_indent = Pt(BODY_PT * 2)
        set_run_font(p.add_run(line), size=SMALL_PT, west="Consolas")
        return p

    def equation(self, latex, number):
        p = self.paragraph()
        set_spacing(p, first_indent=False)
        pf = p.paragraph_format
        pf.tab_stops.add_tab_stop(Cm(bk.TEXT_WIDTH_CM / 2), alignment=1)
        pf.tab_stops.add_tab_stop(Cm(bk.TEXT_WIDTH_CM - 0.05), alignment=2)
        set_run_font(p.add_run("\t"))
        try:
            p._p.append(latex_to_omml(latex))
        except Exception as e:  # 转换失败时退回纯文本，提示人工处理
            print("  ! 公式转换失败，保留源码：", latex, e)
            r = p.add_run(latex)
            set_run_font(r)
            r.font.highlight_color = WD_COLOR_INDEX.YELLOW
        set_run_font(p.add_run(f"\t（{number}）"))
        return p

    def sub_caption(self, text, keep_with_next=False):
        p = self.paragraph()
        set_spacing(p, first_indent=False, align=WD_ALIGN_PARAGRAPH.CENTER)
        p.paragraph_format.keep_with_next = keep_with_next
        set_run_font(p.add_run(text), size=SMALL_PT)
        return p

    def figure(self, path, width_cm=None):
        img = DocxImage.from_file(str(path))
        w_cm = width_cm or 14.0
        h_cm = w_cm * img.px_height / img.px_width
        if h_cm > 18.0:  # 太高的图按高度缩，保证与图名同页
            w_cm = 18.0 * img.px_width / img.px_height
        return self.image(path, width_cm=w_cm)


# ---------------------------------------------------------------- Markdown → docx
def read_md(name):
    s = (PAPER / name).read_text(encoding="utf-8")
    return re.sub(r"<!--.*?-->", "", s, flags=re.S).splitlines()


def render(w, lines, base_dir=PAPER):
    i, n = 0, len(lines)
    pending_caption = None
    while i < n:
        raw = lines[i].rstrip()
        line = raw.strip()
        if not line:
            i += 1
            continue
        if raw.startswith("# "):
            w.heading(line[2:].strip(), 1, page_break=True)
        elif raw.startswith("## "):
            w.heading(line[3:].strip(), 2)
        elif raw.startswith("### "):
            w.heading(line[4:].strip(), 3)
        elif line.startswith("```"):
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                w.code(lines[i].rstrip())
                i += 1
        elif line.startswith("!["):
            m = re.match(r'!\[(.*?)\]\((\S+?)(?:\s+"w=([\d.]+)")?\)', line)  # "w=10.5"：指定图宽（cm）
            w.figure(base_dir / m.group(2), width_cm=float(m.group(3)) if m.group(3) else None)
            if m.group(1):  # 子图小标题（a）…：五号不加粗；最后一张子图与其后的总图名同页
                nxt = next((ln.strip() for ln in lines[i + 1:] if ln.strip()), "")
                w.sub_caption(m.group(1), keep_with_next=bool(re.match(r"^图\d+-\d+\s", nxt)))
        elif re.match(r"^图\d+-\d+\s", line):
            w.caption(line, before_table=False)
        elif re.match(r"^表\d+-\d+\s", line):
            pending_caption = line
        elif line.startswith("|"):
            block = []
            while i < n and lines[i].strip().startswith("|"):
                block.append(lines[i].strip())
                i += 1
            rows = [[c.strip() for c in r.strip("|").split("|")] for r in block]
            if pending_caption:
                w.caption(pending_caption)
                pending_caption = None
            w.md_table(rows[0], rows[2:])
            continue
        elif line.startswith("$$"):
            m = re.search(r"\\tag\{([^}]*)\}", line)
            num = m.group(1) if m else ""
            latex = re.sub(r"\\tag\{[^}]*\}", "", line.strip("$")).strip()
            w.equation(latex, num)
        elif re.match(r"^\[\d+\]", line):
            w.reference(line)
        elif re.match(r"^\d+\.\s", line):
            k, rest = line.split(".", 1)
            w.body(f"（{k}）{rest.strip()}")
        else:
            w.body(line)
        i += 1


# ---------------------------------------------------------------- 模板前置部分
def display_width(s):
    return sum(1 if ord(ch) < 128 else 2 for ch in s)


def underline_groups(par):
    groups, cur = [], []
    for r in par.runs:
        if r.underline:
            cur.append(r)
        elif cur:
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    return groups


def fill_group(group, value):
    width = sum(display_width(r.text) for r in group)
    pad = max(2, width - display_width(value))
    left = pad // 2
    group[0].text = " " * left + value + " " * (pad - left)
    for r in group[1:]:
        r.text = ""


def set_par_text(par, text, size, east="宋体", bold=False, west="Times New Roman"):
    for r in list(par.runs):
        r._element.getparent().remove(r._element)
    set_run_font(par.add_run(text), size=size, bold=bold, east=east, west=west)


def remove_par(par):
    par._p.getparent().remove(par._p)


def abstract_paras(lines):
    """返回 (正文段落列表, 关键词行)"""
    body, kw = [], ""
    for ln in lines:
        s = ln.strip()
        if not s:
            continue
        if s.startswith("**关键词**") or s.startswith("**Keywords**"):
            kw = re.sub(r"^\*\*(.+?)\*\*[:：]\s*", "", s)
        else:
            body.append(s)
    return body, kw


def fill_abstract_page(doc, paras, md_lines):
    zh_start = md_lines.index("# 摘要")
    en_start = md_lines.index("# Abstract")
    zh_body, zh_kw = abstract_paras(md_lines[zh_start + 1:en_start])
    en_body, en_kw = abstract_paras(md_lines[en_start + 1:])

    set_par_text(paras[43], TITLE, size=16, east="黑体", bold=True)
    # 中文摘要：46 段改成第一段，其余段插在其后；47 删除
    def body_par(par, text, west="Times New Roman"):
        for r in list(par.runs):
            r._element.getparent().remove(r._element)
        set_spacing(par)
        par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        add_inline(par, text)

    body_par(paras[46], zh_body[0])
    anchor = paras[46]
    for t in zh_body[1:]:
        new = copy.deepcopy(paras[46]._p)
        anchor._p.addnext(new)
        from docx.text.paragraph import Paragraph
        anchor = Paragraph(new, paras[46]._parent)
        body_par(anchor, t)
    remove_par(paras[47])
    kw = paras[49]
    for r in list(kw.runs):
        r._element.getparent().remove(r._element)
    set_spacing(kw, first_indent=False)
    set_run_font(kw.add_run("关键词："), bold=True)
    set_run_font(kw.add_run(zh_kw))

    set_par_text(paras[51], TITLE_EN, size=16, bold=True)
    remove_par(paras[52])
    body_par(paras[55], en_body[0])
    anchor = paras[55]
    for t in en_body[1:]:
        new = copy.deepcopy(paras[55]._p)
        anchor._p.addnext(new)
        from docx.text.paragraph import Paragraph
        anchor = Paragraph(new, paras[55]._parent)
        body_par(anchor, t)
    remove_par(paras[56])
    kw = paras[58]
    for r in list(kw.runs):
        r._element.getparent().remove(r._element)
    set_spacing(kw, first_indent=False)
    set_run_font(kw.add_run("Keywords: "), bold=True)
    set_run_font(kw.add_run(en_kw))
    set_outline(paras[45], 0)  # 摘要、Abstract 进目录
    set_outline(paras[54], 0)


def toc_field(par):
    """在“目录”段落后放一个 TOC 域；打开 Word 后由 word_update.ps1 更新。"""
    p = OxmlElement("w:p")
    par._p.addnext(p)

    def run(child):
        r = OxmlElement("w:r")
        r.append(child)
        p.append(r)

    fc = OxmlElement("w:fldChar")
    fc.set(qn("w:fldCharType"), "begin")
    run(fc)
    it = OxmlElement("w:instrText")
    it.set(qn("xml:space"), "preserve")
    it.text = ' TOC \\o "1-3" \\h \\z \\u '
    run(it)
    fc = OxmlElement("w:fldChar")
    fc.set(qn("w:fldCharType"), "separate")
    run(fc)
    t = OxmlElement("w:t")
    t.text = "（目录：在 Word 中右键→更新域）"
    run(t)
    fc = OxmlElement("w:fldChar")
    fc.set(qn("w:fldCharType"), "end")
    run(fc)


def main():
    global N_REFS
    doc = Document(str(TEMPLATE))
    paras = doc.paragraphs
    body = doc.element.body

    # 1) 封面
    set_par_text(paras[6], YEARS, size=14)
    paras[6].alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_groups = underline_groups(paras[10])
    fill_group(title_groups[0], TITLE)
    for g in underline_groups(paras[11]):
        for r in g:
            r.text = ""
    for idx, values in COVER.items():
        for g, v in zip(underline_groups(paras[idx]), values):
            if v is not None:
                fill_group(g, v)
    # 封面 “THESIS OF BACHELOR” 用了 Heading 2 样式，Word 不允许改内置标题的大纲级别，它会混进目录；
    # 换成外观相同、大纲级别为正文的自定义样式
    h2 = paras[5].style
    cover = doc.styles.add_style("Cover Title", WD_STYLE_TYPE.PARAGRAPH)
    cover.base_style = h2.base_style
    for tag in ("w:pPr", "w:rPr"):
        src = h2.element.find(qn(tag))
        if src is not None:
            old = cover.element.find(qn(tag))
            if old is not None:
                cover.element.remove(old)
            cover.element.append(copy.deepcopy(src))
    for el in cover.element.iter(qn("w:outlineLvl")):
        el.getparent().remove(el)
    paras[5].style = cover

    # 2) 删除模板批注文本框
    for r in body.xpath(".//w:r[.//w:txbxContent][not(ancestor::w:txbxContent)]"):
        note = "".join(t.text or "" for t in r.iter(qn("w:t")))
        print("remove template note:", note[:30])
        r.getparent().remove(r)

    # 3) 摘要页
    fill_abstract_page(doc, paras, read_md("00_摘要.md"))

    # 4) 目录：删掉示例条目，换成 TOC 域
    toc_title = paras[61]
    for p in paras[62:]:
        if p.style.name.startswith("toc"):
            remove_par(p)
    toc_field(toc_title)

    # 5) 正文：找到目录节的结束段落，删除其后全部示例内容；最后一节用模板“正文第一节”的设置（阿拉伯页码从 1 起）
    sect_pars = [p for p in body.iterchildren(qn("w:p"))
                 if p.find(qn("w:pPr")) is not None and p.find(qn("w:pPr")).find(qn("w:sectPr")) is not None]
    order = {el: k for k, el in enumerate(body.iterchildren())}
    toc_end = next(p for p in sect_pars if order[p] > order[toc_title._p])
    body_sect = copy.deepcopy(sect_pars[sect_pars.index(toc_end) + 1].find(qn("w:pPr")).find(qn("w:sectPr")))
    pg = body_sect.find(qn("w:pgNumType"))
    if pg is None:
        pg = OxmlElement("w:pgNumType")
        body_sect.append(pg)
    pg.set(qn("w:fmt"), "decimal")
    pg.set(qn("w:start"), "1")
    final = body.find(qn("w:sectPr"))
    for el in list(toc_end.itersiblings()):
        if el is not final:
            body.remove(el)
    body.replace(final, body_sect)

    from docx.text.paragraph import Paragraph
    w = Writer(doc, Paragraph(toc_end, toc_title._parent))

    ref_lines = read_md("08_参考文献.md")
    N_REFS = sum(1 for ln in ref_lines if re.match(r"^\[\d+\]", ln.strip()))
    for name in CHAPTERS:
        print("render", name)
        render(w, read_md(name))
    # 参考文献
    p = w.heading("参考文献", 1, page_break=True)
    for r in p.runs:
        r.font.bold = True
    render(w, [ln for ln in ref_lines if not ln.startswith("# ")])
    # 致谢
    w.heading("致谢", 1, page_break=True)
    w.body("【待写：致谢（另起一页，小四宋体，1.35倍行距，首行缩进两字符）】")
    # 附录
    render(w, read_md("09_附录.md"))

    doc.save(str(OUT))
    doc.save(str(HERE / "_thesis.docx"))  # ASCII 路径副本，供 word_update.ps1 更新目录后再拷回
    print("saved:", OUT, "refs:", N_REFS)


if __name__ == "__main__":
    main()
