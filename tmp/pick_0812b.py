# -*- coding: utf-8 -*-
"""2026-08-12 朝バッチ・補充分：売切skip 6件で 50→40 になった分を埋める。
既に tmp/cand_0812.json に入れた URL は除外し、続きの候補から12公演ぶん選ぶ。
並びの流儀は pick_0812.py と同じ（音楽優先・発売まで4日以上を先に）。
"""
import glob
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

LIMIT = 12
FAR = "2026-08-16"
PAT = "tmp/presale_*_0812.json"
NEXTID = 4165

src = open("index.html", "rb").read().decode("utf-8")
have = set(re.findall(r"event(?:Bundle)?Cd=([0-9a-zA-Z]+)", src))
prev = json.load(open("tmp/cand_0812.json", encoding="utf-8"))
used_urls = set(u for c in prev for u in c["urls"])
used_artists = set(c["artist"] for c in prev)

music, other, seen = [], [], set()
for p in sorted(glob.glob(PAT)):
    lg = re.search(r"presale_(\d\d)_", p).group(1)
    for r in json.load(open(p, encoding="utf-8"))["new"]:
        m = re.search(r"event(?:Bundle)?Cd=([0-9a-zA-Z]+)", r["url"])
        cd = m.group(1) if m else ""
        if not cd or cd in seen or cd in have:
            continue
        if r["url"] in used_urls or r["artist"] in used_artists:
            continue
        seen.add(cd)
        (music if lg == "01" else other).append(r)


def ymd(s):
    m = re.match(r"(\d{4})/(\d{1,2})/(\d{1,2})", s or "")
    return "%s-%02d-%02d" % (m.group(1), int(m.group(2)), int(m.group(3))) if m else ""


def sort_far_first(rows):
    far = sorted([r for r in rows if ymd(r.get("rlsdate")) >= FAR], key=lambda r: ymd(r["rlsdate"]))
    near = sorted([r for r in rows if ymd(r.get("rlsdate")) < FAR],
                  key=lambda r: (ymd(r.get("rlsdate")) or "9999", ymd(r.get("perfdate"))))
    return far + near


ordered = sort_far_first(music) + sort_far_first(other)
print("残り候補：音楽 %d件 / その他 %d件" % (len(music), len(other)))

order, groups = [], {}
for r in ordered:
    a = r["artist"]
    if a not in groups:
        groups[a] = []
        order.append(a)
    groups[a].append(r)

out, used = [], 0
for a in order:
    if used >= LIMIT:
        break
    urls = [x["url"] for x in groups[a]]
    out.append({"newid": NEXTID + len(out), "artist": a, "urls": urls})
    used += len(urls)

json.dump(out, open("tmp/cand_0812b.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("→ エントリ%d件 / 公演%d件 / id %d〜" % (len(out), used, NEXTID))
for c in out:
    print("  %d %s (%d本)" % (c["newid"], c["artist"], len(c["urls"])))
