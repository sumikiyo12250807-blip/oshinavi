# -*- coding: utf-8 -*-
"""9/3朝に投入したバッチを .claude/state/last_batch.json に記録する。
翌朝の「前日分の再チェック」で使う（記録漏れが2回あったので必ず書く）。
"""
import json, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
P = '.claude/state/last_batch.json'
d = json.load(open(P, encoding='utf-8'))

d['batches'].append({
    "date": "2026-09-03",
    "slot": "morning",
    "id_from": 6394,
    "id_to": 6468,
    "count": 58,
    "source": "ぴあ 発売前 rlsStatus=0102(先着)＋0202(抽選) を7ジャンル総ざらい（14バケツ）",
    "assigned": False,
    "rechecked": False,
    "note": ("今日の流入＝未掲載175件（URL重複除去後）。内訳＝同名既存95（統合行き・未処理）／"
             "本日発売2（隠れ枠になるので除外＝AKIHIDE 11/14・11/15）／発売日が取れない3（保留）／"
             "本当に新規75。75件をビルドして全件成立（skip 0・94枠）。"
             "🚨緩い部分一致で既存とぶつかった17件は投入せず保留し、別エージェントに"
             "「同じ興行か別物か」を実ページで調べさせた（tmp/_newbuilt_hold_0903.json）。"
             "残り58件（68枠）を投入。投入前ゲート＝ビルド75件成立(skip 0)／check_badges OK／"
             "check_order 違反0／CRLF bare-LF 0／NEW_ORDERとgenre:newが68件で一致。"
             "翌朝(9/4)に①独立再照合②別エージェントの客観チェック→振り分け。"
             "🚨新着プールには9/2から持ち越したe+の保留10件が入ったまま（学園祭ゲストの出演確定待ち）。")
})
json.dump(d, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('last_batch.json に 2026-09-03 morning を追記した（全%d件）' % len(d['batches']))
