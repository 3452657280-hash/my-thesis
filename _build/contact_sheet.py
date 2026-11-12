"""把 _pages/page*.png 拼成若干张缩略图总览（每张 cols×rows 页），便于快速检查版面。
用法：python _build/contact_sheet.py _build/_pages [cols=4] [rows=3] [起始页=1] [结束页=末页]"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

d = Path(sys.argv[1])
cols = int(sys.argv[2]) if len(sys.argv) > 2 else 4
rows = int(sys.argv[3]) if len(sys.argv) > 3 else 3
pages = sorted(d.glob("page*.png"))
a = int(sys.argv[4]) if len(sys.argv) > 4 else 1
b = int(sys.argv[5]) if len(sys.argv) > 5 else len(pages)
pages = pages[a - 1:b]
tw = 420
per = cols * rows
for k in range(0, len(pages), per):
    chunk = pages[k:k + per]
    ims = [Image.open(p).convert("RGB") for p in chunk]
    th = int(ims[0].height * tw / ims[0].width)
    sheet = Image.new("RGB", (cols * (tw + 10) + 10, rows * (th + 30) + 10), "gray")
    dr = ImageDraw.Draw(sheet)
    for j, (p, im) in enumerate(zip(chunk, ims)):
        x = 10 + (j % cols) * (tw + 10)
        y = 10 + (j // cols) * (th + 30)
        sheet.paste(im.resize((tw, th)), (x, y + 20))
        dr.text((x, y + 2), p.stem, fill="white")
    out = d / f"sheet_{a + k:02d}.png"
    sheet.save(out)
    print(out.name)
