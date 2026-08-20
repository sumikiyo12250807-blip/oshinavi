# -*- coding: utf-8 -*-
"""阪神統合で15件減った分を在庫から補充する候補を作る。

選定順は harvest_new と同じ思想＝「発売まで4日以上・遠い順」を最優先。
ただしジャンルは音楽(01)→演劇(02)→クラシック(07)の順に優先する
（[[feedback_harvest_countdown_first]]のジャンル優先度。今日はスポーツが50件を食っていた）。
既に tmp/cand_new.json で選んだURLは除外する。
"""
import json, io, re, sys, datetime, unicodedata

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WANT = 15
START_ID = 3859
TODAY = datetime.date(2026, 8, 6)
ORDER = ["music", "engeki", "classic"]


def eventcd(u):
    m = re.search(r"event(?:Bundle)?Cd=(\w+)", u or "")
    return m.group(1) if m else ""


def days_until(r):
    m = re.match(r"(\d{4})/(\d{1,2})/(\d{1,2})", r or "")
    if not m:
        return None
    return (datetime.date(*[int(x) for x in m.groups()]) - TODAY).days


used = set()
for c in json.load(open("tmp/cand_new.json", encoding="utf-8-sig")):
    for u in c["urls"]:
        used.add(eventcd(u))

picked = []
for tag in ORDER:
    rows = json.load(open("tmp/presale_%s03_0806.json" % tag, encoding="utf-8-sig"))["new"]
    cands = []
    for r in rows:
        cd = eventcd(r["url"])
        if not cd or cd in used:
            continue
        d = days_until(r.get("rlsdate"))
        if d is None or d < 4:      # 発売まで4日以上だけ
            continue
        cands.append((-d, r))       # 遠い順
    cands.sort(key=lambda x: (x[0], x[1]["artist"]))
    for _, r in cands:
        if len(picked) >= WANT:
            break
        used.add(eventcd(r["url"]))
        picked.append((tag, r))
    if len(picked) >= WANT:
        break

out = []
for i, (tag, r) in enumerate(picked):
    out.append({
        "newid": START_ID + i,
        "artist": r["artist"],
        "urls": [r["url"]],
        "_srcgenre": tag,
    })
json.dump(out, open("tmp/cand_refill_0806.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for tag, r in picked:
    print("  %-8s %s | 発売 %s" % (tag, r["artist"][:40], r.get("rlsdate")))
print("補充候補 %d件 → tmp/cand_refill_0806.json (id %d..%d)" % (
    len(out), START_ID, START_ID + len(out) - 1))
