"""核对英文参考文献：Crossref（DOI/卷期页）+ Semantic Scholar（arXiv 是否已正式发表）+ dblp。
用法：python -X utf8 _build/verify_refs.py > _build/verify_refs.txt
"""
import json
import time
import urllib.parse
import urllib.request

UA = {"User-Agent": "thesis-ref-check/1.0 (mailto:none@example.com)"}

REFS = {
    2: "A survey on hallucination in large language models: principles, taxonomy, challenges, and open questions",
    3: "Retrieval-augmented generation for knowledge-intensive NLP tasks",
    4: "Unifying large language models and knowledge graphs: a roadmap",
    12: "Fault cause identification across manufacturing lines through ontology-guided and process-aware FMEA graph learning with LLMs",
    13: "Dense passage retrieval for open-domain question answering",
    14: "M3-Embedding: multi-linguality, multi-functionality, multi-granularity text embeddings through self-knowledge distillation",
    15: "Retrieval-augmented generation for large language models: a survey",
    17: "Reciprocal rank fusion outperforms condorcet and individual rank learning methods",
    18: "From local to global: a graph RAG approach to query-focused summarization",
    19: "Graph retrieval-augmented generation: a survey",
    25: "Knowledge graph enhanced retrieval-augmented generation for failure mode and effects analysis",
    26: "Knowledge management for automobile failure analysis using graph RAG",
    27: "Qwen3 technical report",
}


def get(url, tries=3):
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            err = e
            time.sleep(3 * (k + 1))
    return {"_error": str(err)}


def crossref(title):
    q = urllib.parse.quote(title)
    d = get(f"https://api.crossref.org/works?query.bibliographic={q}&rows=3"
            "&select=DOI,title,author,container-title,volume,issue,page,article-number,published,type")
    out = []
    for it in d.get("message", {}).get("items", []):
        authors = ", ".join(f"{a.get('family','')} {a.get('given','')}" for a in it.get("author", [])[:3])
        y = (it.get("published") or {}).get("date-parts", [[None]])[0][0]
        out.append(f"  CR: {(it.get('title') or [''])[0][:90]} | {authors} | "
                   f"{(it.get('container-title') or [''])[0]} | {y} | vol={it.get('volume')} "
                   f"no={it.get('issue')} pp={it.get('page')} art={it.get('article-number')} | "
                   f"doi={it.get('DOI')} | {it.get('type')}")
    return out or [f"  CR: none {d.get('_error','')}"]


def s2(title):
    q = urllib.parse.quote(title)
    d = get("https://api.semanticscholar.org/graph/v1/paper/search/match?query=" + q +
            "&fields=title,venue,year,journal,publicationVenue,externalIds,publicationTypes")
    out = []
    for it in d.get("data", [])[:1]:
        j = it.get("journal") or {}
        out.append(f"  S2: {it.get('title','')[:90]} | venue={it.get('venue')} | year={it.get('year')} | "
                   f"journal={j.get('name')} vol={j.get('volume')} pp={j.get('pages')} | "
                   f"ids={ {k: v for k, v in (it.get('externalIds') or {}).items() if k in ('DOI', 'ArXiv', 'DBLP')} }")
    return out or [f"  S2: none {d.get('_error','')}"]


def dblp(title):
    q = urllib.parse.quote(title)
    d = get(f"https://dblp.org/search/publ/api?q={q}&format=json&h=3")
    hits = (d.get("result", {}).get("hits", {}) or {}).get("hit", [])
    out = []
    for h in hits:
        i = h.get("info", {})
        out.append(f"  DBLP: {i.get('title','')[:90]} | {i.get('venue')} | {i.get('year')} | "
                   f"vol={i.get('volume')} no={i.get('number')} pp={i.get('pages')} | doi={i.get('doi')} | {i.get('type')}")
    return out or [f"  DBLP: none {d.get('_error','')}"]


for n, t in REFS.items():
    print(f"[{n}] {t}")
    for line in crossref(t) + s2(t) + dblp(t):
        print(line)
    print(flush=True)
    time.sleep(1.5)
