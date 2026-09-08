# -*- coding: utf-8 -*-
"""受付中の未掲載から今回のバッチを選ぶ。
ジャンル優先順＝①音楽 ②演劇/クラシック ③その他（feedback_harvest_genre_priority）。
🚨締切が近いものも落とさない（2026-09-07にユーザーが締切4日先の縛りを外した）。
🚨同名の既存があるものは投入せず統合行きに回す。
使い方: python tmp/sweep0101_pick_0909.py [件数(既定120)]
"""
import glob, io, json, re, sys, collections
sys.stdout.reconfigure(encoding="utf-8")

N = int(sys.argv[1]) if len(sys.argv) > 1 else 120
ORDER = ["01", "02", "07", "06", "03", "04", "05"]   # 音楽→演劇→クラシック→イベント→スポーツ→映画→アート
JP = {"01": "音楽", "02": "演劇", "07": "クラシック", "06": "イベント",
      "03": "スポーツ", "04": "映画", "05": "アート"}

by_lg = collections.defaultdict(dict)
for p in sorted(glob.glob("tmp/sweep0101_0909/*.json")):
    lg = re.search(r"/(\d\d)_", p.replace("\\", "/")).group(1)
    d = json.load(io.open(p, encoding="utf-8"))
    for c in d.get("new") or []:
        m = re.search(r"eventCd=(\w+)", c["url"])
        by_lg[lg].setdefault(m.group(1) if m else c["url"], c)

seen = set()
picked, hold = [], []
for lg in ORDER:
    for cd, c in by_lg[lg].items():
        if cd in seen:
            continue
        seen.add(cd)
        (hold if c.get("name_in_db") else picked).append((lg, cd, c))
print("未掲載 %d件 ＝ 新規候補 %d / 統合行き %d" % (len(seen), len(picked), len(hold)))
c2 = collections.Counter(JP[lg] for lg, _, _ in picked)
print("新規候補のジャンル内訳: %s" % dict(c2))

batch = picked[:N]
print("\n今回のバッチ %d件: %s" % (len(batch), dict(collections.Counter(JP[lg] for lg, _, _ in batch))))
json.dump([{"artist": c["artist"], "urls": [c["url"]], "eventCd": cd}
           for lg, cd, c in batch],
          io.open("tmp/cand0101_0909.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump([{"eventCd": cd, "artist": c["artist"], "url": c["url"], "lg": lg}
           for lg, cd, c in hold],
          io.open("tmp/merge0101_0909.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump([{"eventCd": cd, "artist": c["artist"], "url": c["url"], "lg": lg}
           for lg, cd, c in picked[N:]],
          io.open("tmp/rest0101_0909.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("→ tmp/cand0101_0909.json（今回）/ tmp/merge0101_0909.json（統合行き）/ tmp/rest0101_0909.json（残り %d件）"
      % len(picked[N:]))
