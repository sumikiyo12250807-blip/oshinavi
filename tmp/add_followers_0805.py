# -*- coding: utf-8 -*-
"""2026-08-05 にWebSearchで取得したフォロワー実数を tools/x_log.json の artists.data へ追記する。
既に同名があれば上書きしない（一度取ったら再調査不要の原則）。"""
import json, sys

sys.stdout.reconfigure(encoding='utf-8')
P = 'tools/x_log.json'
d = json.load(open(P, encoding='utf-8'))
data = d['artists']['data']
have = {x['name'] for x in data}

NEW = [
    {"name": "Stray Kids Japan Official", "handle": "@Stray_Kids_JP", "followers": 2700000,
     "note": "日本公式。韓国/国際本体@Stray_Kidsは未取得(さらに大きいはず)。2026-08-05取得"},
    {"name": "莉犬くん＠すとぷり", "handle": "@rinu_nico", "followers": 900000,
     "note": "本人垢。すとぷり公式@StPri_infoは未取得。2026-08-05取得"},
    {"name": "水瀬いのりinfo", "handle": "@inoriminase", "followers": 800230,
     "note": "オフィシャル情報垢。2026-08-05取得"},
    {"name": "SiM_Official", "handle": "@SiM_Official", "followers": 289000,
     "note": "ranking.netのバンド100位内には未掲載＝同サイトは網羅でない。2026-08-05取得"},
    {"name": "スキマスイッチ公式", "handle": "@sukima_official", "followers": 105582,
     "note": "ranking.net バンド61位。2026-08-05取得"},
    {"name": "つばきファクトリー", "handle": "@tsubakifac_uf", "followers": 90000,
     "note": "ハロプロ。2026-08-05取得"},
    {"name": "Cornelius", "handle": "@corneliusjapan", "followers": 81817, "note": "2026-08-05取得"},
    {"name": "GANG PARADE official", "handle": "@GANG_PARADE", "followers": 49600,
     "note": "2026年に解散を発表。2026-08-05取得"},
    {"name": "オレンジスパイニクラブ", "handle": "@orangespinycrab", "followers": 35691,
     "note": "ranking.net バンド93位。2026-08-05取得"},
    {"name": "あたらよ - Atarayo", "handle": "@Atarayo_band", "followers": 24000, "note": "2026-08-05取得"},
    {"name": "菊池桃子", "handle": "@momoko_kikuchi_", "followers": None,
     "note": "🚨検索でフォロワー数を取得できず(2026-08-05・1回)"},
    {"name": "松平健", "handle": None, "followers": None,
     "note": "🚨X公式アカウントもフォロワー数も取得できず(2026-08-05・1回)"},
    {"name": "春風亭一之輔", "handle": None, "followers": None,
     "note": "🚨@1happy1242はニッポン放送の番組垢＝本人垢でない。数値未取得(2026-08-05)"},
    {"name": "Dannie May(公式)", "handle": "@DannieMay_info", "followers": None,
     "note": "🚨フォロワー数を取得できず(2026-08-05・1回)。ranking.netバンド100位内に無し"},
]

added = 0
for x in NEW:
    if x['name'] in have:
        print('skip(既存):', x['name']); continue
    data.append(x); added += 1
    print('add:', x['name'], x['followers'])

d['artists']['measured'] = '2026-08-05'
json.dump(d, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('=== %d件 追記 / artists.data = %d件 ===' % (added, len(data)))
