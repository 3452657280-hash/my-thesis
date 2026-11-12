"""第3、4章插图（PIL 绘制，风格与开题报告图1一致）。输出到 论文/fig/。

画布宽 1640 px（版心 14.5 cm），正文字号 34 px≈8.5 磅，注释 28 px≈7 磅。图名由正文给出，图内不写标题。
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parents[1] / "论文" / "fig"
OUT.mkdir(parents=True, exist_ok=True)
FONT = "C:/Windows/Fonts/simhei.ttf"
F = ImageFont.truetype(FONT, 34)
FS = ImageFont.truetype(FONT, 28)
BLUE, LIGHT = (31, 78, 121), (232, 240, 249)
GREEN, GREEN_L = (46, 125, 50), (232, 245, 233)
ORANGE, ORANGE_L = (196, 98, 16), (255, 243, 224)
PURPLE, PURPLE_L = (94, 53, 177), (237, 231, 246)
GRAY, TEXT = (90, 90, 90), (20, 20, 20)
GAP = 8


class Canvas:
    def __init__(self, w, h):
        self.img = Image.new("RGB", (w, h), "white")
        self.d = ImageDraw.Draw(self.img)

    def box(self, x, y, w, h, lines, fill=LIGHT, outline=BLUE, sub=None, font=F, radius=14, shape="round"):
        d = self.d
        if shape == "diamond":
            d.polygon([(x + w / 2, y), (x + w, y + h / 2), (x + w / 2, y + h), (x, y + h / 2)], fill=fill, outline=outline, width=4)
        elif shape == "ellipse":
            d.ellipse([x, y, x + w, y + h], fill=fill, outline=outline, width=4)
        else:
            d.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=fill, outline=outline, width=4)
        items = [(t, font, TEXT) for t in lines] + ([(sub, FS, GRAY)] if sub else [])
        total = sum(f.size for _, f, _ in items) + GAP * (len(items) - 1)
        ty = y + (h - total) / 2
        for t, f, c in items:
            tw = d.textlength(t, font=f)
            assert tw <= w - 12, f"文字超出方框：{t}"
            d.text((x + (w - tw) / 2, ty), t, font=f, fill=c)
            ty += f.size + GAP

    def arrow(self, pts, color=GRAY, width=4, head=True, dash=False):
        d = self.d
        if dash:
            for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
                n = max(1, int(math.hypot(x2 - x1, y2 - y1) // 18))
                for i in range(0, n, 2):
                    a, b = i / n, min(1, (i + 1) / n)
                    d.line([(x1 + (x2 - x1) * a, y1 + (y2 - y1) * a), (x1 + (x2 - x1) * b, y1 + (y2 - y1) * b)], fill=color, width=width)
        else:
            d.line(pts, fill=color, width=width, joint="curve")
        if head:
            (x1, y1), (x2, y2) = pts[-2], pts[-1]
            ang, L = math.atan2(y2 - y1, x2 - x1), 20
            d.polygon([(x2, y2), (x2 - L * math.cos(ang - 0.4), y2 - L * math.sin(ang - 0.4)),
                       (x2 - L * math.cos(ang + 0.4), y2 - L * math.sin(ang + 0.4))], fill=color)

    def text(self, x, y, t, font=FS, color=GRAY, center=False):
        if center:
            x -= self.d.textlength(t, font=font) / 2
        self.d.text((x, y), t, font=font, fill=color)

    def frame(self, x, y, w, h, title, color):
        self.d.rounded_rectangle([x, y, x + w, y + h], radius=16, outline=color, width=3)
        self.d.text((x + 16, y + 10), title, font=F, fill=color)

    def save(self, name):
        self.img.save(OUT / name, dpi=(300, 300))
        print("saved", name, self.img.size)


def actor(c, x, y, name):
    d = c.d
    d.ellipse([x - 22, y, x + 22, y + 44], outline=TEXT, width=4)
    d.line([(x, y + 44), (x, y + 120)], fill=TEXT, width=4)
    d.line([(x - 45, y + 70), (x + 45, y + 70)], fill=TEXT, width=4)
    d.line([(x, y + 120), (x - 35, y + 175)], fill=TEXT, width=4)
    d.line([(x, y + 120), (x + 35, y + 175)], fill=TEXT, width=4)
    for i, t in enumerate(name.split("\n")):
        c.text(x, y + 185 + i * 36, t, font=F, color=TEXT, center=True)


# ------------------------------------------------------------------ 图3.1 业务流程
def fig_business():
    c = Canvas(1640, 760)
    c.frame(20, 12, 1600, 400, "故障排查（每次故障）", BLUE)
    c.box(50, 150, 220, 110, ["设备故障", "停机"], ORANGE_L, ORANGE)
    c.box(330, 150, 260, 110, ["输入故障描述", "（可带设备号）"])
    c.box(650, 70, 300, 90, ["① 知识图谱子图"])
    c.box(650, 175, 300, 90, ["② 相似历史记录"])
    c.box(650, 280, 300, 90, ["③ 排查决策树"], ORANGE_L, ORANGE)
    c.box(1020, 150, 260, 110, ["按分支逐项", "排查处理"])
    c.box(1340, 150, 250, 110, ["故障排除", "登记维修记录"], GREEN_L, GREEN)
    c.arrow([(270, 205), (330, 205)])
    for yy in (115, 220, 325):
        c.arrow([(590, 205), (620, 205), (620, yy), (650, yy)])
    for yy in (115, 220, 325):
        c.arrow([(950, yy), (985, yy), (985, 205), (1020, 205)], head=yy == 220)
    c.arrow([(1280, 205), (1340, 205)])
    c.arrow([(1150, 260), (1150, 360), (460, 360), (460, 260)], dash=True)
    c.text(805, 368, "未解决：继续追问或换分支", center=True)
    c.frame(20, 430, 1600, 315, "知识积累（定期批量）", GREEN)
    c.box(1340, 520, 250, 110, ["新增维修记录", "（CSV/Excel）"], GREEN_L, GREEN)
    c.box(1020, 520, 260, 110, ["向量化写入", "Qdrant"], GREEN_L, GREEN)
    c.box(650, 520, 300, 110, ["大模型抽取六元组", "专家复核、规范化"], GREEN_L, GREEN)
    c.box(330, 520, 260, 110, ["导入", "Neo4j 知识图谱"], GREEN_L, GREEN)
    c.arrow([(1465, 260), (1465, 520)], color=GREEN)
    c.arrow([(1340, 575), (1280, 575)], color=GREEN)
    c.arrow([(1340, 600), (1310, 600), (1310, 660), (800, 660), (800, 630)], color=GREEN)
    c.arrow([(650, 575), (590, 575)], color=GREEN)
    c.arrow([(460, 520), (460, 470), (180, 470), (180, 262)], color=GREEN, dash=True)
    c.text(195, 690, "知识库更新后，下一次诊断即可使用", color=GREEN)
    c.save("图3-1_业务流程.png")


# ------------------------------------------------------------------ 图3.2 用例图
def fig_usecase():
    c = Canvas(1640, 1080)
    c.d.rounded_rectangle([300, 20, 1330, 1060], radius=20, outline=BLUE, width=3)
    c.text(815, 32, "产线故障诊断系统", font=F, color=BLUE, center=True)
    actor(c, 130, 120, "维修工程师")
    actor(c, 130, 470, "知识工程师")
    actor(c, 130, 790, "管理员")
    actor(c, 1500, 330, "大模型服务")
    # 继承：知识工程师→维修工程师，管理员→知识工程师（空心三角）
    for (x, y1, y2) in ((130, 470, 380), (130, 790, 700)):
        c.d.line([(x, y1 - 8), (x, y2 + 30)], fill=TEXT, width=3)
        c.d.polygon([(x, y2), (x - 14, y2 + 28), (x + 14, y2 + 28)], outline=TEXT, fill="white", width=3)
    uc = [
        ("故障问答与追问", 80), ("查看知识图谱子图", 160), ("查看相似记录并溯源", 240),
        ("获取排查决策树", 320), ("导出报告、收藏流程图", 400),
        ("编辑节点与关系", 500), ("合并同义实体", 580),
        ("导入维修数据", 680), ("回滚图谱修改", 760), ("配置大模型与提示词", 840), ("设置诊断数据源", 920),
    ]
    pos = {}
    for name, y in uc:
        c.box(520, y, 520, 64, [name], LIGHT, BLUE, shape="ellipse")
        pos[name] = y + 32
    for name, _ in uc[:5]:
        c.arrow([(200, 230), (520, pos[name])], color=TEXT, width=3, head=False)
    for name in ("编辑节点与关系", "合并同义实体"):
        c.arrow([(200, 580), (520, pos[name])], color=TEXT, width=3, head=False)
    for name, _ in uc[7:]:
        c.arrow([(200, 900), (520, pos[name])], color=TEXT, width=3, head=False)
    c.arrow([(1040, pos["获取排查决策树"]), (1430, 440)], color=TEXT, width=3, head=False)
    c.text(1485, 1000, "注：空心三角表示角色继承", center=True)
    c.save("图3-2_用例图.png")


# ------------------------------------------------------------------ 图4.1 系统架构
def fig_arch():
    c = Canvas(1640, 1060)
    layers = [
        ("表示层（React + Vite）", 20, PURPLE, PURPLE_L,
         ["诊断对话页", "数据管理页", "流程图库", "系统设置页"], "Cytoscape.js 图谱 · Mermaid 流程图 · Tailwind CSS"),
        ("接口层（FastAPI）", 255, BLUE, LIGHT,
         ["SSE 流式诊断", "REST 图谱接口", "数据集接口", "设置接口"], "会话管理 · 分阶段推送"),
        ("业务层", 490, ORANGE, ORANGE_L,
         ["统一检索", "决策树生成", "图谱管理", "数据导入", "配置管理"], "字面+向量加权排序 · 联网探测 · 规则兜底 · 变更日志与回滚"),
    ]
    for title, y, col, fill, items, note in layers:
        c.frame(20, y, 1600, 215, title, col)
        n = len(items)
        w = (1540 - 30 * (n - 1)) / n
        for i, t in enumerate(items):
            c.box(50 + i * (w + 30), y + 62, w, 90, [t], fill, col)
        c.text(820, y + 168, note, center=True)
    c.frame(20, 725, 1180, 320, "数据层（本地部署）", GREEN)
    for i, (t, s) in enumerate([("Neo4j", "故障知识图谱"), ("Qdrant", "记录向量 1024维"),
                                ("SQLite", "会话 / 消息 / 流程图"), ("配置与日志文件", "开关 / 提示词 / 变更日志")]):
        c.box(50 + (i % 2) * 570, 790 + (i // 2) * 120, 540, 100, [t], GREEN_L, GREEN, sub=s)
    c.frame(1230, 725, 390, 320, "外部服务", GRAY)
    c.box(1260, 790, 330, 100, ["大模型服务"], (245, 245, 245), GRAY, sub="企业网关 / Ollama")
    c.box(1260, 910, 330, 100, ["嵌入/精排模型"], (245, 245, 245), GRAY, sub="bge-m3（本地）")
    for x in (420, 820, 1220):
        c.arrow([(x, 235), (x, 255)])
        c.arrow([(x, 470), (x, 490)])
    c.arrow([(600, 705), (600, 725)])
    c.arrow([(1420, 705), (1420, 725)], dash=True)
    c.text(1395, 712, "仅决策树生成联网", color=ORANGE, center=True)
    c.save("图4-1_系统架构.png")


# ------------------------------------------------------------------ 图4.2 功能模块
def fig_modules():
    c = Canvas(1640, 820)
    c.box(570, 20, 500, 90, ["产线故障诊断系统"], ORANGE_L, ORANGE)
    mods = [
        ("故障诊断", ["故障问答", "追问", "分阶段返回"]),
        ("统一检索", ["问句解析", "混合打分排序", "图谱子图构建", "相似记录整理"]),
        ("决策树生成", ["联网探测", "大模型生成", "格式校验", "规则兜底"]),
        ("知识图谱管理", ["统计与浏览", "节点关系编辑", "同义实体合并", "修改回滚"]),
        ("数据导入", ["记录向量化", "链路表导入导出"]),
        ("配置管理", ["大模型配置", "提示词版本", "数据源开关", "界面语言"]),
        ("会话与结果", ["历史会话", "流程图收藏", "报告导出"]),
    ]
    n, w, gap = len(mods), 200, 33
    x0 = (1640 - n * w - (n - 1) * gap) / 2
    c.d.line([(820, 110), (820, 150)], fill=GRAY, width=4)
    c.d.line([(x0 + w / 2, 150), (x0 + (n - 1) * (w + gap) + w / 2, 150)], fill=GRAY, width=4)
    for i, (m, subs) in enumerate(mods):
        x = x0 + i * (w + gap)
        c.arrow([(x + w / 2, 150), (x + w / 2, 190)])
        c.box(x, 190, w, 80, [m], LIGHT, BLUE, font=FS)
        c.d.line([(x + 20, 270), (x + 20, 300 + 100 * (len(subs) - 1) + 40)], fill=GRAY, width=3)
        for j, s in enumerate(subs):
            y = 300 + 100 * j
            c.d.line([(x + 20, y + 40), (x + 40, y + 40)], fill=GRAY, width=3)
            c.box(x + 40, y, w - 40, 80, [s[:5], s[5:]] if len(s) > 5 else [s], (250, 250, 250), GRAY, font=FS)
    c.save("图4-2_功能模块.png")


# ------------------------------------------------------------------ 图4.3 本体
def fig_ontology():
    c = Canvas(1640, 640)
    names = [("区域", "Area", (23, 167, 229)), ("设备", "Equipment", (17, 201, 174)), ("部件", "Component", (205, 195, 58)),
             ("故障现象", "Problem", (255, 66, 8)), ("原因", "Cause", (255, 133, 10)), ("处理措施", "Solution", (72, 38, 175))]
    rels = ["INCLUDE", "HAS_PART", "HAS_FAULT", "CAUSED_BY", "SOLVED_BY"]
    w, gap, y = 205, 62, 150
    xs = [30 + i * (w + gap) for i in range(6)]
    for (cn, en, col), x in zip(names, xs):
        light = tuple(int(v + (255 - v) * 0.82) for v in col)
        c.box(x, y, w, 120, [cn], light, col, sub=en, shape="ellipse")
    for i, r in enumerate(rels):
        x1, x2 = xs[i] + w, xs[i + 1]
        c.arrow([(x1 + 2, y + 60), (x2 - 2, y + 60)], color=TEXT, width=3)
        c.text((x1 + x2) / 2, y + 18, r, font=ImageFont.truetype(FONT, 20), color=TEXT, center=True)
    c.arrow([(xs[1] + w / 2, y + 120), (xs[1] + w / 2, y + 190), (xs[3] + w / 2, y + 190), (xs[3] + w / 2, y + 120)], color=TEXT, width=3, dash=True)
    c.text(xs[1] + w / 2 + 20, y + 196, "HAS_FAULT（记录中看不出部件时）")
    c.text(30, 30, "关系属性：source_row（年份#行号）、year —— 每条记录一组边，用于溯源与单条链路高亮", color=TEXT)
    c.text(30, 70, "节点属性：name（唯一，MERGE 去重）；设备另有 brand / model / sn / process / line / segment", color=TEXT)
    c.d.rounded_rectangle([30, 430, 1610, 620], radius=14, outline=GRAY, width=2)
    c.text(50, 575, "辅助分类层", font=F, color=GRAY)
    c.text(50, 445, "与 QRQC 共用受控词表", color=GRAY)
    c.text(50, 480, "不参与诊断检索", color=GRAY)
    c.box(xs[2], 505, w, 80, ["部件大类"], (245, 245, 245), GRAY, sub=None)
    c.box(xs[3] + 120, 505, w, 80, ["故障模式大类"], (245, 245, 245), GRAY, font=FS)
    c.box(xs[5], 505, w, 80, ["对策大类"], (245, 245, 245), GRAY)
    for sx, tx in ((xs[2] + w / 2 + 70, xs[2] + w / 2 + 70), (xs[3] + w / 2, xs[3] + 120 + w / 2),
                   (xs[4] + w / 2, xs[3] + 120 + w / 2), (xs[5] + w / 2, xs[5] + w / 2)):
        c.arrow([(sx, y + 122), (tx, 505)], dash=True, width=2)
    c.text(xs[0] + 20, 525, "IS_A（虚线）", color=GRAY)
    c.save("图4-3_本体.png")


# ------------------------------------------------------------------ 图4.4 诊断流程
def fig_flow():
    c = Canvas(1640, 1500)
    cx, w = 560, 640
    x = cx - w / 2

    def b(y, lines, h=90, **k):
        c.box(x, y, w, h, lines, **k)
        return y + h

    b(20, ["接收问句"], 80, fill=GREEN_L, outline=GREEN, shape="ellipse")
    c.box(x + 60, 140, w - 120, 130, ["是否追问？"], shape="diamond")
    c.arrow([(cx, 100), (cx, 140)])
    c.box(1140, 160, 450, 90, ["复用本会话检索结果", "大模型回答"])
    c.arrow([(cx + w / 2 - 60, 205), (1140, 205)])
    c.text(900, 170, "是")
    c.arrow([(cx, 270), (cx, 310)])
    c.text(cx + 12, 274, "否")
    b(310, ["统一检索：解析设备", "字面×0.65 + 向量×0.35 排序"], 110)
    c.arrow([(cx, 420), (cx, 460)])
    b(460, ["选出图谱链路、整理相似记录", "生成规则决策树（备用）"], 110)
    c.arrow([(cx, 570), (cx, 610)])
    b(610, ["推送 diagnosis_kg、diagnosis_records"], 80, fill=PURPLE_L, outline=PURPLE)
    c.arrow([(cx, 690), (cx, 730)])
    c.box(x + 30, 730, w - 60, 150, ["只用规则", "或无检索结果？"], shape="diamond")
    c.arrow([(cx, 880), (cx, 920)])
    c.text(cx + 12, 884, "否")
    c.box(x + 30, 920, w - 60, 150, ["大模型服务", "3 秒内可连通？"], shape="diamond")
    c.arrow([(cx, 1070), (cx, 1110)])
    c.text(cx + 12, 1074, "是")
    b(1110, ["调用大模型生成决策树", "（超时 45 秒）"], 100, fill=ORANGE_L, outline=ORANGE)
    c.arrow([(cx, 1210), (cx, 1250)])
    c.box(x + 60, 1250, w - 120, 120, ["校验通过？"], shape="diamond")
    rx = 1140
    c.box(rx, 1000, 450, 110, ["采用规则决策树", "记录改用原因"])
    c.arrow([(cx + w / 2 - 30, 805), (rx + 225, 805), (rx + 225, 1000)])
    c.text(870, 770, "是")
    c.arrow([(cx + w / 2 - 30, 995), (rx, 1055)])
    c.text(905, 1040, "否 / 模拟断网")
    c.arrow([(cx + w / 2 - 60, 1310), (rx + 225, 1310), (rx + 225, 1110)])
    c.text(900, 1275, "否 / 超时")
    c.box(x - 40, 1400, w + 80, 90, ["分支按成本排序，推送 diagnosis_flowchart", "保存会话，推送 done"], PURPLE_L, PURPLE)
    c.arrow([(cx, 1370), (cx, 1400)])
    c.text(cx + 12, 1372, "是")
    c.arrow([(rx + 225, 1110), (rx + 225, 1445), (x + w + 40, 1445)], head=True)
    c.save("图4-4_诊断流程.png")


if __name__ == "__main__":
    fig_business()
    fig_usecase()
    fig_arch()
    fig_modules()
    fig_ontology()
    fig_flow()
