"""核对中文期刊文献：用 Crossref（多数中文核心期刊注册了 DOI）按题名检索，打印作者/刊名/卷期页。"""
import json
import time
import urllib.parse
import urllib.request

UA = {"User-Agent": "thesis-ref-check/1.0 (mailto:none@example.com)"}
REFS = {
    1: "制造领域知识图谱的应用研究现状与前沿",
    5: "基于元学习的设备故障知识图谱构建及推理方法",
    6: "面向设备点检故障根因分析的因果知识建模方法",
    7: "基于知识图谱的风电机组诊断系统构建与应用",
    8: "基于知识图谱的商用飞机维修方案推荐系统集成建模",
    9: "面向知识图谱构建的设备故障文本实体识别方法",
    10: "矿井提升系统的故障实体关系抽取研究",
    11: "基于大语言模型的实体关系抽取综述",
    16: "基于大型语言模型的检索增强生成综述",
    20: "大语言模型增强的知识图谱问答研究进展综述",
    21: "大语言模型融合知识图谱的问答系统研究",
    22: "融合知识图谱和大模型的高校科研管理问答系统设计",
    23: "知识图谱与大模型融合驱动的航空电子装备故障诊断",
    24: "大模型指令微调驱动的电力故障抢修方案智能生成",
}


def get(url):
    for k in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            err = e
            time.sleep(3 * (k + 1))
    return {"_error": str(err)}


for n, t in REFS.items():
    d = get("https://api.crossref.org/works?rows=5&query.bibliographic=" + urllib.parse.quote(t) +
            "&select=DOI,title,author,container-title,volume,issue,page,published")
    print(f"[{n}] {t}")
    found = False
    for it in d.get("message", {}).get("items", []):
        title = (it.get("title") or [""])[0]
        if t[:8] not in title and title[:8] not in t:
            continue
        found = True
        au = ", ".join(f"{a.get('family','')}{a.get('given','')}" for a in it.get("author", [])[:3])
        y = (it.get("published") or {}).get("date-parts", [[None]])[0][0]
        print(f"   {title} | {au} | {(it.get('container-title') or [''])[0]} | {y} | "
              f"vol={it.get('volume')} no={it.get('issue')} pp={it.get('page')} | doi={it.get('DOI')}")
    if not found:
        print("   Crossref 未找到", d.get("_error", ""))
    time.sleep(1.2)
