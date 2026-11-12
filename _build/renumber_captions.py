"""图表、公式编号改为学校规范的“章-序号”样式：表4.1→表4-1，图3.1→图3-1，\\tag{2.1}→\\tag{2-1}。
只改 论文/0*.md；可重复运行（已改过的不会再变）。"""
import re
from pathlib import Path

PAPER = Path(__file__).resolve().parent.parent / "论文"
PAT = [
    (re.compile(r"([表图])(\d+)\.(\d+|x)"), r"\1\2-\3"),
    (re.compile(r"\\tag\{(\d+)\.(\d+)\}"), r"\\tag{\1-\2}"),
    (re.compile(r"式（(\d+)\.(\d+)）"), r"式（\1-\2）"),
]
for f in sorted(PAPER.glob("0*.md")):
    s = f.read_text(encoding="utf-8")
    n_total = 0
    for pat, rep in PAT:
        s, n = pat.subn(rep, s)
        n_total += n
    if n_total:
        f.write_text(s, encoding="utf-8")
    print(f.name, n_total)
