# -*- coding: utf-8 -*-
"""今朝の未掲載のうち fresh（本当に新規）から、投入する50件を選ぶ。

優先順（[[feedback_harvest_genre_priority]]／[[feedback_harvest_countdown_first]]）:
  1. 発売まで4日以上あるもの（＝カウントダウンとして意味がある）を最優先
  2. ジャンル ①音楽(lg=01) ②演劇(02)/クラシック(07)/お笑い ③その他
  3. 同じアーティストに偏らないよう、名前ごとに1件ずつ回して選ぶ

出力＝build用の候補JSON（1エントリ1URL）。
"""
import json, io, re, datetime, unicodedata
from collections import defaultdict, Counter

TODAY = datetime.date(2026, 9, 4)
LIMIT = 50

tri = json.load(io.open("tmp/_triage_0904.json", encoding="utf-8"))
fresh = tri["fresh"]

# 🚨triage の同名判定は「既存エントリ(genre!=new)」しか見ていないので、
#   まだ振り分け前の新着プールと同名のものが素通りする。ここで落とす（重複投入を防ぐ）。
html = io.open("index.html", encoding="utf-8", newline="").read()
_events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", html, re.S).group(1))


def _norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    return re.sub(r"[\s　・／/＜＞<>「」『』（）()【】’'\"!！\-—]", "", s).lower()


_pool = [_norm(e.get("name")) for e in _events if e.get("genre") == "new"]
_before = len(fresh)
held = [it for it in fresh
        if any(p and (_norm(it.get("artist")).startswith(p) or p.startswith(_norm(it.get("artist"))))
               for p in _pool)]
fresh = [it for it in fresh if it not in held]
json.dump(held, io.open("tmp/newbatch_held_0904.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("プールと同名で保留=%d件（%d → %d）" % (len(held), _before, len(fresh)))


def rls(s):
    m = re.match(r"(\d{4})/(\d{1,2})/(\d{1,2})", s or "")
    return datetime.date(*(int(x) for x in m.groups())) if m else None


PRIO = {"01": 0, "02": 1, "07": 1, "06": 2, "03": 2, "04": 2, "05": 2}

rows = []
for it in fresh:
    d = rls(it.get("rlsdate"))
    if not d:
        continue
    days = (d - TODAY).days
    rows.append({
        "days": days,
        "far": 0 if days >= 4 else 1,          # 発売まで4日以上を先に
        "prio": PRIO.get(it.get("_lg"), 3),
        "artist": it.get("artist", ""),
        "it": it,
    })

# アーティストごとに束ねて、1件ずつ回して取る（同じ人で埋まらないように）
groups = defaultdict(list)
for r in rows:
    groups[r["artist"]].append(r)
for g in groups.values():
    g.sort(key=lambda r: (r["far"], r["prio"], r["days"]))

order = sorted(groups.keys(), key=lambda a: (groups[a][0]["far"], groups[a][0]["prio"], groups[a][0]["days"]))
picked, i = [], 0
while len(picked) < LIMIT:
    added = False
    for a in order:
        if i < len(groups[a]):
            picked.append(groups[a][i]); added = True
            if len(picked) >= LIMIT:
                break
    if not added:
        break
    i += 1

cand = []
for n, r in enumerate(picked, 1):
    cand.append({"newid": 6500 + n, "artist": r["artist"], "urls": [r["it"]["url"]]})
json.dump(cand, io.open("tmp/newbatch_cand_0904.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

buf = []
for r in picked:
    it = r["it"]
    buf.append("%s %s | 発売%s(あと%d日) | %s %s | %s" % (
        it.get("_lg"), (it.get("artist") or "")[:34], it.get("rlsdate"), r["days"],
        it.get("pref"), it.get("venue"), it.get("url")))
io.open("tmp/newbatch_list_0904.txt", "w", encoding="utf-8").write("\n".join(buf))

print("FRESH=%d  PICKED=%d" % (len(fresh), len(picked)))
print("発売まで4日以上=%d / 4日未満=%d" % (sum(1 for r in picked if r["far"] == 0),
                                          sum(1 for r in picked if r["far"] == 1)))
print("ジャンル(lg): %s" % dict(Counter(r["it"].get("_lg") for r in picked)))
print("ユニークなアーティスト数=%d" % len(set(r["artist"] for r in picked)))
print("WROTE tmp/newbatch_cand_0904.json / tmp/newbatch_list_0904.txt")
