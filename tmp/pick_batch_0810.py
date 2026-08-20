# -*- coding: utf-8 -*-
"""2026-08-10：発売前スイープ6ジャンルの候補139件から今日のバッチ(上限50)を選ぶ。
並べ方＝[[feedback_harvest_countdown_first]]「発売まで4日以上」を最優先（＝8/14以降に発売開始）。
同じアーティストの複数URLは1エントリにまとめる（[[feedback_tour_consolidate]]）。
出力＝build_pia_entries.py が食える [{"newid","artist","urls"}] 形式。
"""
import glob
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

LIMIT = 50
FAR = "2026/8/14"  # 今日(8/10)から4日以上先

rows = []
for p in sorted(glob.glob("tmp/presale_*_0810.json")):
    d = json.load(open(p, encoding="utf-8"))
    for r in d["new"]:
        r["lg"] = d["lg"]
        rows.append(r)
print("候補 合計 %d件" % len(rows))


def ymd(s):
    m = re.match(r"(\d{4})/(\d{1,2})/(\d{1,2})", s or "")
    return "%s-%02d-%02d" % (m.group(1), int(m.group(2)), int(m.group(3))) if m else ""


far, near = [], []
for r in rows:
    (far if ymd(r.get("rlsdate")) >= ymd(FAR) else near).append(r)
far.sort(key=lambda r: ymd(r["rlsdate"]))
near.sort(key=lambda r: (ymd(r.get("rlsdate")) or "9999", ymd(r.get("perfdate"))))
print("発売まで4日以上 %d件 / それ以外 %d件" % (len(far), len(near)))

# アーティストでまとめる（順番は最初に出てきた位置を維持）
order, groups = [], {}
for r in far + near:
    a = r["artist"]
    if a not in groups:
        groups[a] = []
        order.append(a)
    groups[a].append(r)

src = open("index.html", "rb").read().decode("utf-8")
nextid = max(int(x) for x in re.findall(r'"id": (\d+),', src)) + 1
print("次のid = %d" % nextid)

out, used = [], 0
for a in order:
    if used >= LIMIT:
        break
    urls = [x["url"] for x in groups[a]]
    out.append({"newid": nextid + len(out), "artist": a, "urls": urls})
    used += len(urls)

json.dump(out, open("tmp/cand_0810.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("→ tmp/cand_0810.json  エントリ%d件 / 公演%d件" % (len(out), used))
for e in out[:10]:
    print("  %d %s (%d URL)" % (e["newid"], e["artist"][:34], len(e["urls"])))
