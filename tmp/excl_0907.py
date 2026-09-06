# -*- coding: utf-8 -*-
"""今日の振り分けから外すidを出す。
 ① ぴあ以外（e+/楽天/ローチケ）由来 … 振り分けはユーザーが新着タブで実物を見てから
 ② 7092 吉良花火クルーズ … ぴあの区分は「イベント/アミューズメント」→kids だが
    中身は花火鑑賞で、同じバッチに hanabi 行きの花火大会がいる。相談に回す
"""
import io, re, json

h = io.open("index.html", encoding="utf-8", newline="").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))
pool = [e for e in EV if e.get("genre") == "new"]

nonpia = [e["id"] for e in pool if not (e.get("links") or {}).get("pia")]
skip = sorted(set(nonpia) | {7092})
assign = [e["id"] for e in pool if e["id"] not in skip]

io.open("tmp/excl_0907.txt", "w", encoding="utf-8").write(",".join(str(x) for x in skip))
print("プール%d / 振り分け%d / 除外%d（ぴあ以外%d + 相談1）"
      % (len(pool), len(assign), len(skip), len(nonpia)))
