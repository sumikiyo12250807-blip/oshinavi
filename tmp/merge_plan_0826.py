# -*- coding: utf-8 -*-
"""統合待ちを「既存エントリ1件＝1作業」の形にまとめる。通信なし。

統合のやり方（feedback_bundle_full_rederive）＝そのエントリに紐づく**全URL**を
build_pia_entries に渡してゼロから再導出する。だから作業単位は「既存id」であって、
ぴあの公演1本ずつではない。ここでは id ごとに「足すべきURL」を束ねて出す。
"""
import json
import re
import sys
import unicodedata
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")


def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    return re.sub(r"[\s　・/／'’\"”!！?？\-–—~〜]", "", s).lower()


src = open("index.html", encoding="utf-8").read()
m = re.search(r"const EVENTS = (\[.*?\]);\n", src, re.S)
events = json.loads(m.group(1))
by_norm = defaultdict(list)
for e in events:
    by_norm[norm(e.get("artist"))].append(e)

rows = json.load(open("tmp/merge_0825.json", encoding="utf-8"))
plan = defaultdict(list)
for r in rows:
    hits = by_norm.get(norm(r.get("artist")))
    if not hits:
        continue
    # 同名が複数あるときは「公演日がいちばん近い」ものに寄せる（ツアーの本体を狙う）
    tgt = sorted(hits, key=lambda e: e.get("date") or "")[-1]
    plan[tgt["id"]].append(r)

todo = {str(k): [r["url"] for r in v] for k, v in plan.items()}
json.dump(todo, open("tmp/merge_todo_0826.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("=== 統合作業 %d件（既存エントリ単位）→ tmp/merge_todo_0826.json ===" % len(plan))
print("")
for eid in sorted(plan):
    ev = next(e for e in events if e["id"] == eid)
    rs = plan[eid]
    print("■ id=%d %s（今%d枠・genre=%s・千秋楽%s）" % (
        eid, ev.get("artist"), len(ev.get("tickets") or []), ev.get("genre"), ev.get("date")))
    print("    今のURL: %s" % ((ev.get("links") or {}).get("pia")))
    for r in rs:
        print("    ＋%s %s %s" % (
            (r.get("saletype") or "")[:8], (r.get("perfdate") or "")[:30], (r.get("venue") or "")[:34]))
        print("      %s" % r.get("url"))
    print("")
