# -*- coding: utf-8 -*-
"""新着プール(genre:"new")を「ぴあ由来／e+ほか由来」×「下書きジャンルの有無」で仕分ける。

振り分けの決まり：
 - ぴあ由来は `_genre` をそのまま `genre` に移す（自分で再分類しない）
 - ぴあ以外（e+/楽天/ローチケ）は**振り分けだけユーザー確認後**＝プールに残す
 - `_piaSub` が空／「その他」系で下書きが付いていない件は相談に回す
"""
import io, re, json, collections

h = io.open("index.html", encoding="utf-8", newline="").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))
pool = [e for e in EV if e.get("genre") == "new"]

pia, other, nogenre_pia, nogenre_other = [], [], [], []
for e in pool:
    L = e.get("links") or {}
    is_pia = bool(L.get("pia"))
    g = e.get("_genre")
    if is_pia:
        (pia if g else nogenre_pia).append(e)
    else:
        (other if g else nogenre_other).append(e)

cnt = collections.Counter(e.get("_genre") for e in pia)

with io.open("tmp/pool_triage_0907.txt", "w", encoding="utf-8") as f:
    f.write("=== 新着プール %d件 ===\n" % len(pool))
    f.write("  ぴあ由来・下書きあり  %3d件 ← 今日振り分ける\n" % len(pia))
    f.write("  ぴあ由来・下書きなし  %3d件 ← 相談\n" % len(nogenre_pia))
    f.write("  ぴあ以外・下書きあり  %3d件 ← ユーザーが新着タブで見てからなので残す\n" % len(other))
    f.write("  ぴあ以外・下書きなし  %3d件 ← 同上＋ジャンル未定\n\n" % len(nogenre_other))

    f.write("--- 振り分ける %d件（ぴあ由来）ジャンル内訳 ---\n" % len(pia))
    for g, c in cnt.most_common():
        f.write("  %-10s %d件\n" % (g, c))

    f.write("\n--- 振り分ける %d件の一覧 ---\n" % len(pia))
    for e in sorted(pia, key=lambda x: x["id"]):
        f.write("  id=%-6s %-10s %-42s %s\n"
                % (e["id"], e["_genre"], (e.get("name") or "")[:42],
                   (e.get("_piaSub") or "-")))

    if nogenre_pia:
        f.write("\n--- ⚠️相談: ぴあ由来なのに下書きが無い %d件 ---\n" % len(nogenre_pia))
        for e in sorted(nogenre_pia, key=lambda x: x["id"]):
            f.write("  id=%-6s %-42s piaSub=%s\n     %s\n"
                    % (e["id"], (e.get("name") or "")[:42], e.get("_piaSub"),
                       (e.get("links") or {}).get("pia") or ""))

    f.write("\n--- 残す（ぴあ以外）%d件 ---\n" % (len(other) + len(nogenre_other)))
    for e in sorted(other + nogenre_other, key=lambda x: x["id"]):
        L = e.get("links") or {}
        src = "e+" if L.get("eplus") else ("楽天" if L.get("rakuten") else ("ローチケ" if L.get("lawson") else "?"))
        f.write("  id=%-6s [%s] %-10s %s\n"
                % (e["id"], src, e.get("_genre") or "未定", (e.get("name") or "")[:44]))

print("プール%d = ぴあ%d(+下書き無%d) / ぴあ以外%d(+下書き無%d)"
      % (len(pool), len(pia), len(nogenre_pia), len(other), len(nogenre_other)))
