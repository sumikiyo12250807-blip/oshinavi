# -*- coding: utf-8 -*-
"""2026-08-10 第2バッチ：発売前スイープの残り候補から次の50公演を選ぶ。
第1バッチで投入済みの eventCd は index.html を見て除外する（[[feedback_harvest_dedup_check]]）。
並べ方は第1バッチと同じ＝「発売まで4日以上」を最優先（[[feedback_harvest_countdown_first]]）。
"""
import glob
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

LIMIT = 50
FAR = "2026-08-14"

src = open("index.html", "rb").read().decode("utf-8")
have = set(re.findall(r"event(?:Bundle)?Cd=([0-9a-zA-Z]+)", src))
print("index.html が持つ eventCd: %d種" % len(have))

rows = []
for p in sorted(glob.glob("tmp/presale_*_0810.json")):
    d = json.load(open(p, encoding="utf-8"))
    for r in d["new"]:
        m = re.search(r"event(?:Bundle)?Cd=([0-9a-zA-Z]+)", r["url"])
        r["cd"] = m.group(1) if m else ""
        rows.append(r)
print("スイープ候補 合計 %d件" % len(rows))

rest = [r for r in rows if r["cd"] and r["cd"] not in have]
print("うち未登録（第1バッチ投入分を除いた残り） %d件" % len(rest))


def ymd(s):
    m = re.match(r"(\d{4})/(\d{1,2})/(\d{1,2})", s or "")
    return "%s-%02d-%02d" % (m.group(1), int(m.group(2)), int(m.group(3))) if m else ""


far = [r for r in rest if ymd(r.get("rlsdate")) >= FAR]
near = [r for r in rest if ymd(r.get("rlsdate")) < FAR]
far.sort(key=lambda r: ymd(r["rlsdate"]))
near.sort(key=lambda r: (ymd(r.get("rlsdate")) or "9999", ymd(r.get("perfdate"))))
print("発売まで4日以上 %d件 / それ以外 %d件" % (len(far), len(near)))

order, groups = [], {}
for r in far + near:
    a = r["artist"]
    if a not in groups:
        groups[a] = []
        order.append(a)
    groups[a].append(r)

nextid = max(int(x) for x in re.findall(r'"id": (\d+),', src)) + 1
out, used = [], 0
for a in order:
    if used >= LIMIT:
        break
    urls = [x["url"] for x in groups[a]]
    out.append({"newid": nextid + len(out), "artist": a, "urls": urls})
    used += len(urls)

json.dump(out, open("tmp/cand2_0810.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("→ tmp/cand2_0810.json  エントリ%d件 / 公演%d件（id %d〜）" % (len(out), used, nextid))
print("次バッチ以降に残るもの: %d公演" % (len(rest) - used))
