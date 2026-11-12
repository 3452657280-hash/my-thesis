"""开题报告图1：系统技术路线（PIL 绘制）。

按版心宽 14.5 cm 设计：画布宽 1640 px，正文字号 34 px ≈ 8.5 磅，注释 28 px ≈ 7 磅。
图名放在图下方（由 build_kaiti.py 添加），图内不再重复标题。
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent / "fig_tech_route.png"
W, H = 1640, 905
FONT = "C:/Windows/Fonts/simhei.ttf"
f_box = ImageFont.truetype(FONT, 34)
f_small = ImageFont.truetype(FONT, 28)

BLUE, LIGHT = (31, 78, 121), (232, 240, 249)
GREEN, GREEN_L = (46, 125, 50), (232, 245, 233)
ORANGE, ORANGE_L = (196, 98, 16), (255, 243, 224)
GRAY, TEXT = (90, 90, 90), (20, 20, 20)
GAP = 10

img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)


def box(x, y, w, h, lines, fill=LIGHT, outline=BLUE, sub=None):
    d.rounded_rectangle([x, y, x + w, y + h], radius=16, fill=fill, outline=outline, width=4)
    items = [(t, f_box, TEXT) for t in lines]
    if sub:
        items.append((sub, f_small, GRAY))
    total = sum(f.size for _, f, _ in items) + GAP * (len(items) - 1)
    ty = y + (h - total) / 2
    for text, font, color in items:
        tw = d.textlength(text, font=font)
        assert tw <= w - 16, f"文字超出方框：{text}"
        d.text((x + (w - tw) / 2, ty), text, font=font, fill=color)
        ty += font.size + GAP


def arrow(points, color=GRAY):
    d.line(points, fill=color, width=5, joint="curve")
    (x1, y1), (x2, y2) = points[-2], points[-1]
    ang = math.atan2(y2 - y1, x2 - x1)
    L = 22
    p1 = (x2 - L * math.cos(ang - 0.4), y2 - L * math.sin(ang - 0.4))
    p2 = (x2 - L * math.cos(ang + 0.4), y2 - L * math.sin(ang + 0.4))
    d.polygon([(x2, y2), p1, p2], fill=color)


def note(x, y, text):
    d.text((x, y), text, font=f_small, fill=GRAY)


# ---------------------------------------------------------------- 知识构建阶段（预先批量完成）
d.rounded_rectangle([20, 12, W - 20, 312], radius=18, outline=GREEN, width=3)
d.text((40, 24), "知识构建阶段（预先批量完成）", font=f_box, fill=GREEN)
box(50, 76, 250, 150, ["设备维修记录", "（CSV/Excel）"], GREEN_L, GREEN)
box(360, 76, 230, 150, ["数据清洗与", "字段映射"], GREEN_L, GREEN)
box(650, 76, 340, 150, ["大模型六元组抽取", "专家复核", "实体规范化"], GREEN_L, GREEN)
box(1060, 76, 540, 70, ["Neo4j 故障知识图谱"], GREEN_L, GREEN)
box(1060, 156, 540, 70, ["Qdrant 向量库（bge-m3）"], GREEN_L, GREEN)
arrow([(300, 151), (360, 151)])
arrow([(590, 151), (650, 151)])
arrow([(990, 126), (1060, 111)])
arrow([(475, 226), (475, 262), (1330, 262), (1330, 226)])
label = "记录文本向量化"
note((475 + 1330) / 2 - d.textlength(label, font=f_small) / 2, 270, label)

# ---------------------------------------------------------------- 故障诊断阶段（每次提问）
d.rounded_rectangle([20, 330, W - 20, 890], radius=18, outline=BLUE, width=3)
d.text((40, 342), "故障诊断阶段（每次提问）", font=f_box, fill=BLUE)
box(50, 551, 250, 118, ["用户故障问句", "（设备+现象）"])
box(370, 400, 470, 146, ["① 知识图谱子图检索", "设备/部件识别 + Cypher"], sub="数据源：Neo4j")
box(370, 640, 470, 146, ["② 相似记录检索", "混合召回 + 交叉编码器精排"], sub="数据源：Qdrant")
box(950, 420, 320, 130, ["③a 大模型决策树", "融合图谱+记录"], ORANGE_L, ORANGE)
box(950, 670, 320, 130, ["③b 规则决策树", "原因分组+成本排序"], LIGHT, BLUE)
box(1340, 551, 260, 118, ["按原因分支的", "排查流程图"], ORANGE_L, ORANGE)
arrow([(300, 593), (370, 473)])
arrow([(300, 627), (370, 713)])
# ①② 的证据汇合后送入两种生成方式
d.line([(840, 473), (895, 473)], fill=GRAY, width=5)
d.line([(840, 713), (895, 713)], fill=GRAY, width=5)
d.line([(895, 473), (895, 735)], fill=GRAY, width=5)
arrow([(895, 485), (950, 485)])
arrow([(895, 735), (950, 735)])
arrow([(1270, 485), (1305, 485), (1305, 593), (1340, 593)])
arrow([(1270, 735), (1305, 735), (1305, 627), (1340, 627)])
note(958, 380, "有网络时")
note(958, 808, "无网络时")
note(380, 552, "→ 前端展示：知识图谱")
note(380, 792, "→ 前端展示：相似记录表")
note(1345, 680, "→ 前端展示")
note(40, 850, "注：两种方式输出的都是排查决策树；①②和③b 在本地运行，不需要联网。")

img.save(OUT, dpi=(300, 300))
print("saved", OUT.name, img.size)
