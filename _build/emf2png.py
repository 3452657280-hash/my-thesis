"""把 word_pages.ps1 导出的 page*.emf 转成 PNG（Pillow 在 Windows 上可直接光栅化 EMF）。"""
import sys
from pathlib import Path

from PIL import Image

out = Path(sys.argv[1])
width = int(sys.argv[2]) if len(sys.argv) > 2 else 1100
for emf in sorted(out.glob("page*.emf")):
    im = Image.open(emf)
    im.load(dpi=144)
    im = im.convert("RGB")
    h = int(im.height * width / im.width)
    im.resize((width, h), Image.LANCZOS).save(emf.with_suffix(".png"))
    print(emf.with_suffix(".png").name, im.size)
