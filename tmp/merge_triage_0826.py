# -*- coding: utf-8 -*-
"""統合待ちリスト（tmp/merge_0825.json）を「確度」で仕分ける。通信なし。

なぜ必要か：
  部分一致で拾っているので誤検知が混じる（「Gacharic Spin」が「char」に、「SHE'S」が「the shes gone」に）。
  1件ずつ実ページを見る前に、機械で「完全一致＝ほぼ確実」と「部分一致だけ＝要目視」に割っておく。
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

# 既存の正規化名 → [(id, artist)]
by_norm = defaultdict(list)
for e in events:
    by_norm[norm(e.get("artist"))].append((e["id"], e.get("artist")))

rows = json.load(open("tmp/merge_0825.json", encoding="utf-8"))
exact, partial, none = [], [], []
for r in rows:
    a = norm(r.get("artist"))
    if not a:
        none.append((r, []))
        continue
    if a in by_norm:
        exact.append((r, by_norm[a]))
        continue
    # 部分一致（短すぎる名前は誤検知の温床なので長さも見る）
    hits = []
    for k, v in by_norm.items():
        if not k:
            continue
        if (k in a or a in k) and min(len(k), len(a)) >= 4:
            hits.extend(v)
    (partial if hits else none).append((r, hits[:4]))

print("=== 統合待ち %d件の仕分け ===" % len(rows))
print("  ✅完全一致（同じ名前の既存がある＝ほぼツアー分裂） %d件" % len(exact))
print("  ⚠️部分一致だけ（誤検知の可能性・要目視）           %d件" % len(partial))
print("  🆕既存に無い（＝新規に載せる候補）                 %d件" % len(none))

for label, group in (("✅完全一致", exact), ("⚠️部分一致だけ", partial), ("🆕既存に無い", none)):
    print("")
    print("=" * 70)
    print(label)
    for r, hits in group:
        ids = " ".join("id%d(%s)" % (i, (a or "")[:16]) for i, a in hits)
        print("  %-26s %-10s %-22s %s" % (
            (r.get("artist") or "")[:26], r.get("saletype") or "", (r.get("perfdate") or "")[:22], ids))
        print("      %s" % r.get("url"))
