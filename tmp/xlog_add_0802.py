# -*- coding: utf-8 -*-
"""8/1夜投稿5本の実測(8/2 19:38 = 21〜23時間後)を x_log.json に追記
 ※リンクはセルフリプに貼ったため link_cl は計上されない(link=false扱い)
"""
import json, io

P = r'C:\Users\user\oshinavi\tools\x_log.json'
d = json.load(open(P, encoding='utf-8'))

NEW = [
    dict(posted="2026-08-01", title="アインシュタイン結成15周年記念ツアー", cat="お笑い(ライブ)",
         measured="2026-08-02", measured_h=22, imp=381, like=0, rt=0, reply=0,
         eng=2, detail_cl=0, profile=2, link_cl=None, link=False, tone="おねえ",
         followers=218000,
         note="本文にURLを書いた下書きだが、実投稿ではセルフリプにリンクを貼ったためリンククリック欄が出ない"),
    dict(posted="2026-08-01", title="天才ピアニスト×ヨネダ2000 あっちこっちカンパニ〜 愛知公演", cat="お笑い(ライブ)",
         measured="2026-08-02", measured_h=21, imp=292, like=0, rt=0, reply=0,
         eng=0, detail_cl=0, profile=0, link_cl=None, link=False, tone="おねえ",
         followers=31300, note="同上(セルフリプ)"),
    dict(posted="2026-08-01", title="THE FACT MUSIC AWARDS EXHIBITION - VISION FESTA", cat="展示(K-POP)",
         measured="2026-08-02", measured_h=23, imp=133, like=0, rt=0, reply=0,
         eng=0, detail_cl=0, profile=0, link_cl=None, link=False, tone="おねえ",
         followers=2500000, note="出演組のフォロワーは最大だが展示会=本人ファンダムのタグは回らず。同上(セルフリプ)"),
    dict(posted="2026-08-01", title="山里亮太の140 愛知公演〜逃げ上手の不如帰〜", cat="お笑い(トーク)",
         measured="2026-08-02", measured_h=23, imp=66, like=0, rt=0, reply=0,
         eng=0, detail_cl=0, profile=0, link_cl=None, link=False, tone="おねえ",
         followers=1533730, note="フォロワー153万で最下位級。テレビの人=Xのタグは回らない。同上(セルフリプ)"),
    dict(posted="2026-08-01", title="Omotenashi Stage『18TRIP』-R1ze&Ev3ns-", cat="2.5次元/ゲーム",
         measured="2026-08-02", measured_h=21, imp=51, like=0, rt=0, reply=0,
         eng=0, detail_cl=0, profile=0, link_cl=None, link=False, tone="おねえ",
         followers=150000, note="同上(セルフリプ)"),
]

have = {(p['posted'], p['title']) for p in d['posts']}
added = 0
for n in NEW:
    if (n['posted'], n['title']) not in have:
        d['posts'].append(n)
        added += 1

d['artists']['data'].extend([
    {"name": "マカロニえんぴつ 公式", "handle": "@macarock0616", "followers": 328000},
    {"name": "Little Glee Monster/リトグリ公式", "handle": "@LittleGleeMonst", "followers": 243000},
    {"name": "のん official", "handle": "@non_dayo_ne", "followers": 227000},
    {"name": "May'n", "handle": None, "followers": 222487},
    {"name": "KNOCK OUT(ノックアウト)公式", "handle": "@kb_knockout", "followers": 31300},
    {"name": "栗林みな実", "handle": "@minamiracle6_6", "followers": 24300},
    {"name": "日本体操協会", "handle": "@GymnasticsJapan", "followers": 17200},
    {"name": "フルカワユタカ", "handle": "@rckstr_furukawa", "followers": 9590,
     "note": "スタッフ垢@furukawa_yutakaは5,687"},
    {"name": "酒まつり【公式】", "handle": "@sakematsuri_", "followers": 1290,
     "note": "Instagram @sakematsuri.japan は4,191"},
])
d['artists']['measured'] = "2026-08-02"

json.dump(d, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('posts +%d (計%d) / artists 計%d' % (added, len(d['posts']), len(d['artists']['data'])))
