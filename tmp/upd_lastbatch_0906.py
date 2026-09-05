# -*- coding: utf-8 -*-
"""9/6朝に投入したバッチを .claude/state/last_batch.json に記録する（翌朝の再チェック用）。"""
import json
import io

P = ".claude/state/last_batch.json"
d = json.load(io.open(P, encoding="utf-8"))
d["batches"].append({
    "date": "2026-09-06",
    "slot": "morning",
    "id_from": 7025,
    "id_to": 7098,
    "count": 74,
    "source": "ぴあ 発売前スイープ 7ジャンル全部（音楽22/演劇11/クラシック10/スポーツ17/映画7/アート0/イベント11）",
    "assigned": False,
    "rechecked": False,
    "note": ("9/5に未スイープだったスポーツ・映画・アート・イベントを含めて7ジャンル全部を回した。"
             "ページ到達率は全ジャンル最終ページまで到達（件数比では見ない＝feedback_newpool_presale_ratio_gate）。"
             "未掲載78件→URL重複を潰して77件→発売日不明3件（FTISLAND／優里／カマタマーレ讃岐）を見送って74件を構築・投入。"
             "🚨統合待ち34件＝tmp/samename_map_0906.txt。"
             "「同じ公演なのにぴあのeventCdが別」型（7025/6073・7032/6601・7034/5729・7036/3129・7040/5052・"
             "7049/4195・7050/3905・7051/3750・7054/6414・7055/945・7058/5408・7059/5409・7060/6452・"
             "7061/4850・7063/3818・7064/4716・7041/4052 など）と、"
             "「同じツアーの別公演」型（7027柴田聡子・7028SHERBETS・7029syrup16g・7031SCANDAL・"
             "7035人間椅子・7039みゆな・7042〜7044WILD BLUE・7046ジャズ大名）に分かれる。"
             "既存側もすでに分裂している（syrup16g 5526/5527/5528、SCANDAL 6284/6285/6286）ので、"
             "統合は昼の便で1件ずつ実ページを見てから。")
})
json.dump(d, io.open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("記録した: 2026-09-06 morning 7025..7098 (74件)")
