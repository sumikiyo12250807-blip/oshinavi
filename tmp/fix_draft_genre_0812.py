# -*- coding: utf-8 -*-
"""2026-08-12：投入前に、ぴあがカテゴリを返さず名前fallbackで engeki/fes に倒れた9件の
下書きジャンルを直す（[[project_vendor_genre_autoassign]]＝人が判断するのは _piaSub 空/その他だけ）。

根拠:
  4129 トップガン マーヴェリック シネマコンサート … オーケストラ生演奏付き上映 → classic
  4130 福山雅治                                   … J-POP        → jpop
  4142 Hi-Fi Un!corn                              … 日韓合同のK-POPボーイバンド(2023デビュー) → kpop
  4144 Age Factory                                … 日本のロックバンド → rock
  4152 DEZERT                                     … 日本のロックバンド → rock
  4153 高尾奏音／櫻井陽菜                          … 声優のバースデーイベント(公式 kanon-takao.com) → seiyuu
  4159 わーすた                                   … アイドルグループ → idol
  4163 fav me 中本こまり生誕祭2026                 … アイドルの生誕祭 → idol
  4167 Ken Yokoyama                               … 日本のパンクロック → rock
"""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

FIX = {
    4129: "classic",
    4130: "jpop",
    4142: "kpop",
    4144: "rock",
    4152: "rock",
    4153: "seiyuu",
    4159: "idol",
    4163: "idol",
    4167: "rock",
}

rows = json.load(open("tmp/all_new_0812.json", encoding="utf-8-sig"))
n = 0
for e in rows:
    if e["id"] in FIX:
        print("  id=%d %s → %s | %s" % (e["id"], e["_genre"], FIX[e["id"]], e["name"][:30]))
        e["_genre"] = FIX[e["id"]]
        n += 1
assert n == len(FIX), "直せなかったidがある（%d/%d）" % (n, len(FIX))

json.dump(rows, open("tmp/all_new_0812.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
import collections
print("下書き内訳:", dict(collections.Counter(e["_genre"] for e in rows)))
