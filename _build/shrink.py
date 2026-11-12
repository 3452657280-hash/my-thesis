"""把 page*.png 压成灰度 JPEG（page*_s.jpg），便于逐页目检。用法：python _build/shrink.py _build/pages [宽度]"""
import sys
from pathlib import Path

from PIL import Image

out = Path(sys.argv[1])
width = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
for png in sorted(out.glob("page??.png")):
    im = Image.open(png).convert("L")
    h = int(im.height * width / im.width)
    dst = png.with_name(png.stem + "_s.jpg")
    im.resize((width, h), Image.LANCZOS).save(dst, quality=80, optimize=True)
    print(dst.name, dst.stat().st_size // 1024, "KB")
