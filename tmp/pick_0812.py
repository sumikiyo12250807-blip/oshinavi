# -*- coding: utf-8 -*-
"""2026-08-12 朝バッチ：音楽最優先で50公演を選ぶ。
順番＝①音楽(lg=01) → ②足りない分を他ジャンルから。各グループ内は「発売まで4日以上」を先に
（[[feedback_harvest_countdown_first]]）。既に index.html が持つ eventCd は除外。
"""
import glob
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

LIMIT = 50
FAR = "2026-08-16"          # today+4
PAT = "tmp/presale_*_0812.json"

src = open("index.html", "rb").read().decode("utf-8")
have = set(re.findall(r"event(?:Bundle)?Cd=([0-9a-zA-Z]+)", src))

music, other, seen = [], [], set()
for p in sorted(glob.glob(PAT)):
    lg = re.search(r"presale_(\d\d)_", p).group(1)
    for r in json.load(open(p, encoding="utf-8"))["new"]:
        m = re.search(r"event(?:Bundle)?Cd=([0-9a-zA-Z]+)", r["url"])
        cd = m.group(1) if m else ""
        if not cd or cd in seen or cd in have:
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
print("候補：音楽 %d件 / その他 %d件" % (len(music), len(other)))

order, groups = [], {}
for r in ordered:
    a = r["artist"]
    if a not in groups:
        groups[a] = []
        order.append(a)
    groups[a].append(r)

nextid = max(int(x) for x in re.findall(r'"id": (\d+),', src)) + 1
out, used, nmusic = [], 0, 0
music_urls = set(r["url"] for r in music)
for a in order:
    if used >= LIMIT:
        break
    urls = [x["url"] for x in groups[a]]
    out.append({"newid": nextid + len(out), "artist": a, "urls": urls})
    used += len(urls)
    nmusic += sum(1 for u in urls if u in music_urls)

json.dump(out, open("tmp/cand_0812.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("→ エントリ%d件 / 公演%d件（うち音楽%d件）/ id %d〜" % (len(out), used, nmusic, nextid))
for c in out:
    print("  %d %s (%d本)" % (c["newid"], c["artist"], len(c["urls"])))
