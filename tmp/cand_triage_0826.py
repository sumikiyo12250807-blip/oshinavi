# -*- coding: utf-8 -*-
"""新着候補を「同名の既存あり（＝統合行き）」と「本当に新規」に割る。通信なし。

なぜ＝同名既存を投入すると同じツアーが2エントリに割れる（feedback_tour_consolidate）。
完全一致だけだと「アンジュルム 2026秋 風林火山・弐」のように公演名にアーティスト名が
含まれる型を見逃すので、部分一致も見る（feedback_harvest_dedup_check / 8/21の反省）。
"""
import json
import re
import sys
import unicodedata
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")


def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    return re.sub(r"[\s　・/／'’\"”!！?？\-–—~〜＜＞<>【】「」『』（）()]", "", s).lower()


src = open("index.html", encoding="utf-8").read()
m = re.search(r"const EVENTS = (\[.*?\]);\n", src, re.S)
events = json.loads(m.group(1))
by_norm = defaultdict(list)
for e in events:
    by_norm[norm(e.get("artist"))].append(e)

rows = json.load(open("tmp/ps_merge_0826.json", encoding="utf-8"))
exact, partial, fresh = [], [], []
for r in rows:
    a = norm(r.get("artist"))
    if a in by_norm:
        exact.append((r, by_norm[a][:2]))
        continue
    hits = []
    for k, v in by_norm.items():
        if not k:
            continue
        if (k in a or a in k) and min(len(k), len(a)) >= 5:
            hits.extend(v)
    (partial if hits else fresh).append((r, hits[:3]))

print("=== 新着候補 %d件の仕分け ===" % len(rows))
print("  ⚠️同名の既存あり（統合へ回す）    %d件" % len(exact))
print("  ⚠️部分一致（要目視・誤検知混じり） %d件" % len(partial))
print("  ✅本当に新規（投入候補）          %d件" % len(fresh))
print("")
print("=== ✅本当に新規 %d件（発売まで4日以上を先頭）===" % len(fresh))
for r, _ in fresh:
    print("  発売%-12s(%s) | %-8s | %-30s | %s" % (
        r.get("rls") or "不明",
        ("あと%d日" % r["days"]) if r.get("days") is not None else "-",
        {"01": "音楽", "02": "演劇", "03": "スポーツ", "04": "映画",
         "05": "アート", "06": "イベント", "07": "クラシック"}[r["lg"]],
        (r.get("artist") or "")[:30], r.get("url")))

for label, group in (("⚠️同名の既存あり（統合へ）", exact), ("⚠️部分一致（要目視）", partial)):
    print("")
    print("=" * 70)
    print(label)
    for r, hits in group:
        ids = " ".join("id%d(%s)" % (e["id"], (e.get("artist") or "")[:14]) for e in hits)
        print("  %-30s %s" % ((r.get("artist") or "")[:30], ids))
        print("      %s" % r.get("url"))

json.dump([r for r, _ in fresh], open("tmp/cand_fresh_0826.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump([r for r, _ in exact], open("tmp/cand_samename_0826.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
