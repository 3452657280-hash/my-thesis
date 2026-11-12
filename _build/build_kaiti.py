"""把 01_开题报告.md 填进学校开题报告模板，输出 docx。

用法：python -X utf8 _build/build_kaiti.py
- 保留模板封面版式（下划线、字号、分节），只替换题目和封面字段；
- 六个一级标题沿用模板段落，正文按《编写格式规范》：小四宋体、1.35 倍行距、首行缩进 2 字符、
  英文和数字用 Times New Roman；表名五号宋体加粗、置于表上方；图名五号宋体加粗、置于图下方。
"""
import copy
import re
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "_build" / "template_kaiti.docx"
SOURCE = ROOT / "01_开题报告.md"
OUT = ROOT / "开题报告_基于知识图谱增强大模型的产线故障诊断系统.docx"

TITLE = "基于知识图谱增强大模型的产线故障诊断系统"
COVER = {  # 模板封面段落序号 -> 字段值（未知信息用“待填写”，交给用户补）
    14: "信息学科部",
    15: "软件工程",
    16: "软件工程234班",
    17: "7023123210",
    18: "王禹博",
    19: "邓伦丹",
}
HEADINGS = [24, 32, 40, 48, 55, 63]  # 模板中六个一级标题段落
FIELD_UNITS = 39  # 封面各字段下划线统一宽度（按半角计，汉字占 2）；各行标签都是 10 个单位，右端因此对齐

BODY_PT = 12   # 小四
SMALL_PT = 10.5  # 五号
TEXT_WIDTH_CM = 21.0 - 3.67 - 2.67  # A4 宽减去模板左右页边距
EM_CM = SMALL_PT / 72 * 2.54  # 表格五号字一个汉字的宽度
CELL_PAD_CM = 0.5  # 单元格左右边距（Word 默认各 0.19 cm）再留一点余量
DATE_RANGE_RE = re.compile(r"^\d{4}\.\d{2}\.\d{2}[—–-]\d{4}\.\d{2}\.\d{2}$")


# ---------------------------------------------------------------- 字体工具
def set_run_font(run, size=BODY_PT, bold=False, east="宋体", west="Times New Roman",
                 superscript=False, subscript=False):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = west
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    rfonts.set(qn("w:ascii"), west)
    rfonts.set(qn("w:hAnsi"), west)
    rfonts.set(qn("w:eastAsia"), east)
    rfonts.set(qn("w:cs"), west)
    if superscript:
        run.font.superscript = True
    if subscript:
        run.font.subscript = True


def set_spacing(p, first_indent=True, line=1.35, align=None):
    pf = p.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    pf.line_spacing = line
    if first_indent:
        pf.first_line_indent = Pt(BODY_PT * 2)
    if align is not None:
        p.alignment = align


TOKEN_RE = re.compile(r"(\*\*.+?\*\*|\[\d+(?:[,，\-–]\d+)*\]|<sub>.+?</sub>|<sup>.+?</sup>)")


def add_inline(p, text, size=BODY_PT, bold=False, cite_superscript=True):
    """解析 **粗体**、[n] 引用（上标）、<sub>/<sup>。"""
    for part in TOKEN_RE.split(text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            add_inline(p, part[2:-2], size=size, bold=True, cite_superscript=cite_superscript)
        elif re.fullmatch(r"\[\d+(?:[,，\-–]\d+)*\]", part) and cite_superscript:
            set_run_font(p.add_run(part), size=size, bold=bold, superscript=True)
        elif part.startswith("<sub>"):
            set_run_font(p.add_run(part[5:-6]), size=size, bold=bold, subscript=True)
        elif part.startswith("<sup>"):
            set_run_font(p.add_run(part[5:-6]), size=size, bold=bold, superscript=True)
        else:
            set_run_font(p.add_run(part), size=size, bold=bold)


# ---------------------------------------------------------------- 段落插入
class Writer:
    """在模板某段落之后顺序插入新块。"""

    def __init__(self, doc, anchor_par):
        self.doc = doc
        self.anchor = anchor_par._p

    def _place(self, element):
        self.anchor.addnext(element)
        self.anchor = element

    def paragraph(self):
        p = self.doc.add_paragraph()
        self._place(p._p)
        return p

    def table(self, rows, cols):
        t = self.doc.add_table(rows=rows, cols=cols)
        self._place(t._tbl)
        return t

    def body(self, text):
        p = self.paragraph()
        set_spacing(p)
        add_inline(p, text)
        return p

    def sub_heading(self, text):
        """（一）××：四号以下的二级标题，用小四黑体、顶格；与下一段同页。"""
        p = self.paragraph()
        set_spacing(p, first_indent=False)
        p.paragraph_format.keep_with_next = True
        set_run_font(p.add_run(text), size=BODY_PT, bold=False, east="黑体")
        return p

    def caption(self, text, before_table=True):
        """表名在表上方，需与表同页；图名在图下方，由图段落负责与之同页。"""
        p = self.paragraph()
        set_spacing(p, first_indent=False, align=WD_ALIGN_PARAGRAPH.CENTER)
        p.paragraph_format.keep_with_next = before_table
        set_run_font(p.add_run(text), size=SMALL_PT, bold=True)
        return p

    def image(self, path, width_cm=14.5):
        p = self.paragraph()
        set_spacing(p, first_indent=False, line=1.0, align=WD_ALIGN_PARAGRAPH.CENTER)
        p.paragraph_format.keep_with_next = True
        p.add_run().add_picture(str(path), width=Cm(width_cm))
        return p

    def formula(self, latex_like, number):
        """居中公式 + 右侧编号：用制表位实现（中间居中、右端右对齐）。"""
        p = self.paragraph()
        set_spacing(p, first_indent=False)
        pf = p.paragraph_format
        pf.tab_stops.add_tab_stop(Cm(TEXT_WIDTH_CM / 2), alignment=1)   # center
        pf.tab_stops.add_tab_stop(Cm(TEXT_WIDTH_CM - 0.1), alignment=2)  # right
        set_run_font(p.add_run("\t"))
        for kind, seg in latex_like:
            run = p.add_run(seg)
            set_run_font(run, subscript=(kind == "sub"))
            if kind == "ital":
                run.font.italic = True
        set_run_font(p.add_run(f"\t（{number}）"))
        return p

    def reference(self, text):
        p = self.paragraph()
        set_spacing(p, first_indent=False, align=WD_ALIGN_PARAGRAPH.LEFT)
        pf = p.paragraph_format
        m = re.match(r"(\[\d+\])\s*(.*)", text)
        label, rest = (m.group(1), m.group(2)) if m else ("", text)
        pf.left_indent = Pt(BODY_PT * 2.2)
        pf.first_line_indent = Pt(-BODY_PT * 2.2)
        set_run_font(p.add_run(label + " "))
        set_run_font(p.add_run(rest))
        return p

    def md_table(self, header, rows):
        t = self.table(1 + len(rows), len(header))
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        three_line(t)
        widths = column_widths(header, rows)
        # 长文本列左对齐，短列居中
        aligns = [WD_ALIGN_PARAGRAPH.LEFT if max(len(r[ci]) for r in rows) > 12
                  else WD_ALIGN_PARAGRAPH.CENTER for ci in range(len(header))]
        t.autofit = False
        for ci, h in enumerate(header):
            fill_cell(t.cell(0, ci), h, bold=True)
        for ri, row in enumerate(rows, start=1):
            for ci, val in enumerate(row):
                fill_cell(t.cell(ri, ci), val, align=aligns[ci])
        for ci, wcm in enumerate(widths):
            for cell in t.columns[ci].cells:
                cell.width = Cm(wcm)
        for gc, wcm in zip(t._tbl.tblGrid.findall(qn("w:gridCol")), widths):
            gc.set(qn("w:w"), str(round(wcm / 2.54 * 1440)))
        for row in t.rows:  # 单行不跨页断开（表格本身可以跨页，表头行重复）
            cant = OxmlElement("w:cantSplit")
            row._tr.get_or_add_trPr().insert(0, cant)
        # 表后空一行，避免紧贴下一段
        spacer = self.paragraph()
        set_spacing(spacer, first_indent=False, line=1.0)
        return t


def fill_cell(cell, text, bold=False, align=WD_ALIGN_PARAGRAPH.CENTER):
    cell.text = ""
    p = cell.paragraphs[0]
    set_spacing(p, first_indent=False, line=1.15, align=align)
    add_inline(p, text, size=SMALL_PT, bold=bold, cite_superscript=False)


def text_cm(s):
    """五号字下文本的大致宽度：汉字及全角符号 1 em，数字 0.5 em，句点逗号冒号 0.3 em，其余 ASCII 0.6 em。"""
    em = 0.0
    for ch in s:
        if ch.isdigit():
            em += 0.5
        elif ch in ".,:;":
            em += 0.3
        elif ord(ch) < 128:
            em += 0.6
        else:
            em += 1.0
    return em * EM_CM


def column_widths(header, rows):
    """短列和日期区间列按内容给足宽度、不折行；其余列按内容长度分摊剩余版心宽度。"""
    ncol = len(header)
    natural = [max(text_cm(header[ci]), *(text_cm(r[ci]) for r in rows)) + CELL_PAD_CM
               for ci in range(ncol)]
    nowrap = [natural[ci] <= 2.6 or all(DATE_RANGE_RE.match(r[ci]) for r in rows)
              for ci in range(ncol)]
    widths = [natural[ci] if nowrap[ci] else 0.0 for ci in range(ncol)]
    flex = [ci for ci in range(ncol) if not nowrap[ci]]
    rest = TEXT_WIDTH_CM - sum(widths)
    if flex and rest > 0:
        weight = {ci: min(natural[ci], 26 * EM_CM) for ci in flex}
        total = sum(weight.values())
        for ci in flex:
            widths[ci] = rest * weight[ci] / total
    else:  # 全是短列：等比例放大到版心宽度；或短列已超宽：等比例缩小
        scale = TEXT_WIDTH_CM / sum(widths)
        widths = [w * scale for w in widths]
    return widths


def three_line(table):
    """三线表：顶线、底线 1.5 磅，栏目线 0.75 磅，无竖线。"""
    tbl = table._tbl
    tblPr = tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge, sz in (("top", 12), ("bottom", 12), ("left", 0), ("right", 0),
                     ("insideH", 0), ("insideV", 0)):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single" if sz else "nil")
        if sz:
            el.set(qn("w:sz"), str(sz))
            el.set(qn("w:space"), "0")
            el.set(qn("w:color"), "000000")
        borders.append(el)
    look = tblPr.find(qn("w:tblLook"))  # 按 schema 顺序，tblBorders 须在 tblLayout/tblLook 之前
    layout = tblPr.find(qn("w:tblLayout"))
    anchor = layout if layout is not None else look
    if anchor is not None:
        anchor.addprevious(borders)
    else:
        tblPr.append(borders)
    for cell in table.rows[0].cells:
        tcPr = cell._tc.get_or_add_tcPr()
        tcb = OxmlElement("w:tcBorders")
        bottom = OxmlElement("w:bottom")
        bottom.set(qn("w:val"), "single")
        bottom.set(qn("w:sz"), "6")
        bottom.set(qn("w:space"), "0")
        bottom.set(qn("w:color"), "000000")
        tcb.append(bottom)
        tcPr.append(tcb)
    # 表头行跨页重复
    trPr = table.rows[0]._tr.get_or_add_trPr()
    th = OxmlElement("w:tblHeader")
    th.set(qn("w:val"), "true")
    trPr.append(th)


def display_width(s):
    """等宽估算：中文字符占 2，ASCII 占 1。"""
    return sum(1 if ord(ch) < 128 else 2 for ch in s)


# ---------------------------------------------------------------- Markdown 解析
def parse_sections(md):
    """按 '## ' 切成六部分，返回 [(标题, [行])]。"""
    parts, cur = [], None
    for line in md.splitlines():
        if line.startswith("## "):
            cur = (line[3:].strip(), [])
            parts.append(cur)
        elif cur is not None:
            cur[1].append(line)
    return parts


def render_section(w, lines):
    i, n = 0, len(lines)
    pending_caption = None
    while i < n:
        line = lines[i].rstrip()
        if not line.strip():
            i += 1
            continue
        if line.startswith("### "):
            w.sub_heading(line[4:].strip())
        elif line.startswith("!["):
            m = re.match(r"!\[(.*?)\]\((.*?)\)", line)
            w.image(ROOT / m.group(2))
            w.caption(m.group(1), before_table=False)
        elif re.match(r"^表\d+\s", line.strip()):
            pending_caption = line.strip()
        elif line.startswith("|"):
            block = []
            while i < n and lines[i].startswith("|"):
                block.append(lines[i])
                i += 1
            rows = [[c.strip() for c in r.strip().strip("|").split("|")] for r in block]
            header, body = rows[0], [r for r in rows[2:]]
            if pending_caption:
                w.caption(pending_caption)
                pending_caption = None
            w.md_table(header, body)
            continue
        elif line.startswith("$$"):
            m = re.search(r"\\tag\{(\d+)\}", line)
            num = m.group(1) if m else "1"
            segs = [("ital", "s"), ("n", " = "), ("ital", "α"), ("n", "·"), ("ital", "s"),
                    ("sub", "lex"), ("n", " + (1 − "), ("ital", "α"), ("n", ")·"),
                    ("ital", "s"), ("sub", "vec")]
            w.formula(segs, num)
        elif re.match(r"^\[\d+\]", line):
            w.reference(line)
        else:
            w.body(line.strip())
        i += 1


def main():
    doc = Document(str(TEMPLATE))
    paras = doc.paragraphs

    # 1) 题目：保留“题   目：”标签，替换下划线内容
    p = paras[10]
    runs = p.runs
    runs[3].text = TITLE
    for r in runs[4:9]:
        r.text = ""
    # 题目后补足下划线空格，使下划线长度与模板相近
    runs[9].text = " " * 8
    runs[10].text = ""

    # 2) 封面字段：带下划线的部分 = 左侧空格 + 值 + 右侧空格。
    #    整段替换为新值，并按原显示宽度补空格，保证各行下划线长度一致（模板批注要求）。
    for idx, value in COVER.items():
        rs = [r for r in paras[idx].runs if r.underline]
        pad = max(2, FIELD_UNITS - display_width(value))
        left = pad // 2
        rs[0].text = " " * left + value + " " * (pad - left)
        for r in rs[1:]:
            r.text = ""

    # 2b) 删除模板里的格式批注文本框（黄色提示框，提交前应删掉）
    for r in doc.element.body.xpath(".//w:r[.//w:txbxContent][not(ancestor::w:txbxContent)]"):
        note = "".join(t.text or "" for t in r.iter(qn("w:t")))
        print("remove template note:", note[:40])
        r.getparent().remove(r)

    # 3) 填表日期保留模板的 2026 年 11 月 16 日（开题阶段起始日）

    # 4) 六个部分：删掉标题之间的空段落，再插入正文
    md = SOURCE.read_text(encoding="utf-8")
    sections = parse_sections(md)
    sections = [s for s in sections if s[0][0] in "一二三四五六"]
    assert len(sections) == 6, [s[0] for s in sections]

    heading_pars = [paras[k] for k in HEADINGS]
    # 删除每个标题后的空段落（到下一个标题或文档末尾为止）
    body_paras = doc.paragraphs
    heading_elems = {hp._p for hp in heading_pars}
    started = False
    for par in list(body_paras):
        if par._p is heading_pars[0]._p:
            started = True
            continue
        if not started or par._p in heading_elems:
            continue
        if not par.text.strip() and par._p.pPr is not None and par._p.pPr.find(qn("w:sectPr")) is not None:
            continue  # 保留分节符
        if not par.text.strip():
            par._p.getparent().remove(par._p)

    for hp, (title, lines) in zip(heading_pars, sections):
        # 标题统一为四号黑体（模板为四号宋体常规，按格式规范改为黑体便于区分层级）
        for r in hp.runs:
            set_run_font(r, size=14, east="黑体")
        hp.paragraph_format.keep_with_next = True
        w = Writer(doc, hp)
        render_section(w, lines)

    doc.save(str(OUT))
    print("saved:", OUT)


if __name__ == "__main__":
    main()
