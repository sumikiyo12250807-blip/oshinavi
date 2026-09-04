# -*- coding: utf-8 -*-
"""畳んだときに「画面に出る枠」が11本減る理由を調べる。
同じ (type, date, url) が別エントリにまたがって存在する＝本当の重複なのかを見る。"""
import json, re, io, unicodedata
from collections import defaultdict

TODAY = "2026-09-04"
html = io.open("index.html", encoding="utf-8", newline="").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", html, re.S).group(1))


def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    return re.sub(r"[\s　・／/＜＞<>「」『』（）()【】’'\"!！\-—]", "", s).lower()


def visible(t):
    if t.get("saleUntilSoldOut") or t.get("soldout"):
        return True
    sd, d = t.get("startDate"), (t.get("date") or "")
    return not ((not sd or sd <= TODAY) and d < TODAY)


g = defaultdict(list)
for e in events:
    if e.get("genre") == "new":
        continue
    k = norm(e.get("name"))
    if k:
        g[k].append(e)

buf = []
total_lost = 0
for k, es in g.items():
    if len(es) < 2:
        continue
    nm = " ".join(e.get("name") or "" for e in es)
    gens = set(e.get("genre") for e in es)
    if "sports" in gens or any(x in nm for x in ("オーケストラ", "交響楽団", "フィル")) \
       or re.search(r"[≪＜<【]", nm) or len(gens) > 1:
        continue
    seen, dup = set(), []
    for e in es:
        for t in e.get("tickets", []):
            key = (t.get("type"), t.get("date"), t.get("url") or "")
            if key in seen:
                dup.append((e.get("id"), t))
            else:
                seen.add(key)
    vis_dup = [d for d in dup if visible(d[1])]
    if vis_dup:
        total_lost += len(vis_dup)
        buf.append("=" * 70)
        buf.append("■ %s  %s" % (es[0].get("name"), ["id%s" % e.get("id") for e in es]))
        for eid, t in vis_dup:
            buf.append("   消える枠（id%s由来）: %s" % (eid, t.get("type")))
            buf.append("      〜%s  start=%s  url=%s" % (t.get("date"), t.get("startDate"),
                                                        (t.get("url") or "(なし)")[:70]))

io.open("tmp/fold_lost_0904.txt", "w", encoding="utf-8").write("\n".join(buf))
print("畳むと消える『画面に出る枠』= %d本" % total_lost)
print("WROTE tmp/fold_lost_0904.txt")
