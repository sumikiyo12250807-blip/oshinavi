# -*- coding: utf-8 -*-
"""受付中スイープの結果をまとめる＝ページ到達率と未掲載件数。
🚨到達率は「件数比」でなく **最終ページまで行ったか** で見る（feedback_newpool_presale_ratio_gate）。"""
import glob, io, json, re, sys, collections
sys.stdout.reconfigure(encoding="utf-8")

tot_new, buckets, bad = 0, 0, []
new_urls = {}
for p in sorted(glob.glob("tmp/sweep0101_0909/*.json")):
    d = json.load(io.open(p, encoding="utf-8"))
    buckets += 1
    reached = (d.get("fetched_pages") or 0) > (d.get("pages") or 0)
    if not reached and (d.get("pages") or 0) > 0:
        bad.append((p, d.get("total"), d.get("pages"), d.get("fetched_pages")))
    if (d.get("total") or 0) >= 1000:
        bad.append((p + " 🚨1000件の頭打ち", d.get("total"), d.get("pages"), d.get("fetched_pages")))
    for c in d.get("new") or []:
        m = re.search(r"eventCd=(\w+)", c["url"])
        new_urls.setdefault(m.group(1) if m else c["url"], c)
        tot_new += 1
print("バケツ %d本 / 最終ページまで行かなかった or 頭打ち: %d本" % (buckets, len(bad)))
for b in bad:
    print("   %s total=%s pages=%s fetched=%s" % b)
print("未掲載（重複前）%d件 → URL重複を潰して %d件" % (tot_new, len(new_urls)))
c = collections.Counter()
for k, v in new_urls.items():
    c["発売日あり" if v.get("rlsdate") else "発売日なし"] += 1
    c["同名の既存あり" if v.get("name_in_db") else "同名なし"] += 1
for k in ("発売日あり", "発売日なし", "同名の既存あり", "同名なし"):
    print("   %-12s %d" % (k, c[k]))
json.dump([{"url": v["url"], "artist": v["artist"], "rlsdate": v.get("rlsdate"),
            "perfdate": v.get("perfdate"), "venue": v.get("venue"),
            "pref": v.get("pref"), "name_in_db": v.get("name_in_db")}
           for v in new_urls.values()],
          io.open("tmp/sweep0101_new_0909.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("→ tmp/sweep0101_new_0909.json")
