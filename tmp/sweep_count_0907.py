# -*- coding: utf-8 -*-
"""スイープで出た未掲載候補を1本にまとめて、重複を落とす。
🚨 投入前に「発売前が何件・もう売っている枠が何件」と、ページ到達率を数えて報告する
   （feedback_newpool_presale_ratio_gate）。
"""
import io, os, json, glob, re

files = sorted(glob.glob("tmp/presale_0907_*.json"))
seen, rows = set(), []
per_file = []

for p in files:
    try:
        d = json.load(io.open(p, encoding="utf-8"))
    except Exception as ex:
        per_file.append((p, "読めない: %s" % ex, 0))
        continue
    meta = ""
    if isinstance(d, dict):
        # 到達率＝fetched_pages が pages を超えていれば最後まで見た
        meta = "total=%s pages=%s fetched=%s parsed=%s 同名既存=%s" % (
            d.get("total"), d.get("pages"), d.get("fetched_pages"),
            d.get("parsed"), d.get("new_name_in_db"))
        d = d.get("new") or []
    n_new = 0
    for c in d:
        cd = c.get("url") or json.dumps(c, ensure_ascii=False)[:60]
        if cd in seen:
            continue
        seen.add(cd)
        rows.append((os.path.basename(p), c))
        n_new += 1
    per_file.append((os.path.basename(p), "%s / 候補%d" % (meta, len(d)), n_new))

with io.open("tmp/sweep_count_0907.txt", "w", encoding="utf-8") as f:
    f.write("=== スイープの未掲載候補（ファイル別）===\n")
    for name, tot, uniq in per_file:
        f.write("  %-34s 候補%-4s うち新規%s\n" % (name, tot, uniq))
    f.write("\n重複を落とした合計: %d件\n\n" % len(rows))
    f.write("=== 一覧 ===\n")
    for name, c in rows:
        f.write("  [%s] 発売%s | %s | %s | %s\n"
                % (name.replace("presale_0907_", "").replace(".json", ""),
                   c.get("saleStart") or c.get("rlsDate") or "-",
                   (c.get("name") or c.get("title") or "")[:44],
                   c.get("showDate") or c.get("date") or "-",
                   (c.get("url") or "")[:66]))

print("候補ファイル%d / 重複除去後 %d件" % (len(files), len(rows)))
