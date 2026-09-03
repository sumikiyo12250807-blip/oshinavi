# -*- coding: utf-8 -*-
"""サイト全体で「同じエントリに同じ枠が2つ以上ある」ものを洗い出す。
今朝 3735/3752/5516 で見つけた二重登録の全数調査。

3群に分ける：
  A url無しとurl有りのペア（＝buildでurlが落ちた版が残っている。消してよい）
  B url が完全に同じ重複（＝正真正銘の重複。消してよい）
  C url が違う重複（＝別の売り場かもしれない。触らない＝要確認）
"""
import json, re, io
from collections import defaultdict

html = io.open("index.html", encoding="utf-8", newline="").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", html, re.S).group(1))

A, B, C = [], [], []
for e in events:
    g = defaultdict(list)
    for t in e.get("tickets", []):
        g[(t.get("type"), t.get("date"))].append(t)
    for k, ts in g.items():
        if len(ts) < 2:
            continue
        urls = [t.get("url") or "" for t in ts]
        uniq = set(urls)
        rec = (e.get("id"), e.get("name"), k[0], k[1], urls)
        if "" in uniq and len(uniq - {""}) == 1:
            A.append(rec)
        elif len(uniq) == 1:
            B.append(rec)
        else:
            C.append(rec)

buf = []
for tag, g in (("A url無し+url有りのペア（消してよい）", A),
               ("B urlも同じ完全重複（消してよい）", B),
               ("C urlが違う＝別の売り場かも（触らない・要確認）", C)):
    buf.append("=" * 74)
    buf.append("【%s】 %d件" % (tag, len(g)))
    for eid, name, ty, dt, urls in g:
        buf.append("  id=%-5s %s" % (eid, (name or "")[:46]))
        buf.append("        %s | 〜%s | 枠%d" % (ty, dt, len(urls)))
        for u in urls:
            buf.append("          %s" % (u or "(url無)"))
io.open("tmp/dup_all_0904.txt", "w", encoding="utf-8").write("\n".join(buf))

print("A_nourl_pair=%d  B_exact_dup=%d  C_diff_url=%d" % (len(A), len(B), len(C)))
print("A_IDS=" + ",".join(str(r[0]) for r in A))
print("B_IDS=" + ",".join(str(r[0]) for r in B))
print("C_IDS=" + ",".join(str(r[0]) for r in C))
