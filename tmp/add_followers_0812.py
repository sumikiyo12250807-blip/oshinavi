# -*- coding: utf-8 -*-
"""8/12に取得したXフォロワー実数を tools/x_log.json に追記する。"""
import json
import os

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools', 'x_log.json')

NEW = [
    {"name": "CANDY TUNE【Official】", "handle": "@CANDY_TUNE_", "followers": 200000,
     "note": "2026-07に20万人達成を公式報告(RBB TODAY)。2026-08-12取得"},
    {"name": "山寺宏一", "handle": "@yamachanoha", "followers": 583895,
     "note": "x-ranker 男性声優ランキング。ボイスシネマ声優口演ライブ2026の出演者。2026-08-12取得"},
    {"name": "キュウソネコカミ", "handle": "@KYUSO_NEKOKAMI", "followers": 280900,
     "note": "280.9K。8/11に『換算が食い違う』として不採用にしたが、再検索でも280.9Kで一致したので採用。2026-08-12取得"},
    {"name": "RISE OFFICIAL", "handle": "@RISE_2003", "followers": 58000,
     "note": "キックボクシング興行。Instagram 54K。2026-08-12取得"},
    {"name": "cinema staff", "handle": "@cinemastaff_", "followers": 44100,
     "note": "2026-08-12取得"},
    {"name": "CNBLUE JAPAN OFFICIAL", "handle": "@cnblue_japan", "followers": 34500,
     "note": "日本公式。Instagram @cnblue_official_jp は127K。本体@official_CNBLUEは未取得。2026-08-12取得"},
    {"name": "DEZERT", "handle": "@DEZERT_OFFICIAL", "followers": 23200,
     "note": "2026-08-12取得"},
    {"name": "PompadollS", "handle": "@PompadollS", "followers": 15000,
     "note": "⚠️別ソースで10.9Kの表示あり=概数。2026-08-12取得"},
    {"name": "ザ・シスターズハイ", "handle": "@TheSistersHigh", "followers": 10200,
     "note": "Instagram 8,252。2026-08-12取得"},
    {"name": "jo0ji_crew兄", "handle": "@jo0ji_info", "followers": 5833,
     "note": "情報垢。本人@jo0ji3は未取得。2026-08-12取得"},
    {"name": "秘密の小梅ちゃんクラブ", "handle": None, "followers": None,
     "note": "🚨X公式アカウントを特定できず(2026-08-12・1回)"},
    {"name": "林原めぐみ 公式", "handle": "@MHayashibara_PR", "followers": None,
     "note": "🚨フォロワー数を取得できず(2026-08-12・1回)"},
]

with open(P, 'r', encoding='utf-8') as f:
    log = json.load(f)

data = log['artists']['data']
have = {d.get('name') for d in data}
added = 0
for n in NEW:
    if n['name'] in have:
        for d in data:
            if d.get('name') == n['name']:
                d.update(n)
        print('update %s' % n['name'])
    else:
        data.append(n)
        added += 1
log['artists']['measured'] = '2026-08-12'

with open(P, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(log, f, ensure_ascii=False, indent=1)
print('added %d / total %d' % (added, len(data)))
