# -*- coding: utf-8 -*-
"""投入したバッチを .claude/state/last_batch.json に記録する（翌朝の再チェックで使う）。"""
import json, io

PATH = ".claude/state/last_batch.json"
d = json.load(io.open(PATH, encoding="utf-8"))

rec = {
    "date": "2026-09-04",
    "slot": "morning",
    "id_from": 6501,
    "id_to": 6550,
    "count": 50,
    "source": "ぴあ 発売前スイープ rlsStatus=0102(48)+0202(2)・fresh 67件から選定",
    "assigned": False,
    "rechecked": False,
    "note": ("全件が発売前（もう売っているものは0件）。発売まで4日以上が37件・4日未満が13件。"
             "ジャンル内訳 音楽16/演劇11/クラシック13/イベント6/スポーツ2/アート1/映画1。"
             "選定時にアーティストごと1件ずつ回して偏りを防いだ（50件とも別アーティスト）。"
             "🚨triageの同名判定は既存エントリしか見ないので、新着プールと同名の4件を別に保留した"
             "（藤原大祐・fripSide＝既存プールのツアーへ統合／ぼくのドラゴン＝重複／"
             "千葉ロッテ〈ワイドシート〉＝座席種違いで新規投入の候補）。tmp/newbatch_held_0904.json")
}
d["batches"].append(rec)
json.dump(d, io.open(PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("APPENDED batches=%d" % len(d["batches"]))
