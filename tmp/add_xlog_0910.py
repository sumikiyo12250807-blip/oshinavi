# -*- coding: utf-8 -*-
"""2026-09-10 に調べたフォロワー数を tools/x_log.json の artists に足す。

[[reference_x_follower_lookup]]＝取れた数値は貯める（同じ人が次に出たら再調査不要）。
🚨取れなかったものは「不明」と書く。埋めない・推測しない。
"""
import io
import json

p = 'tools/x_log.json'
d = json.load(io.open(p, encoding='utf-8'))
arts = d['artists']['data']
have = {a['name'] for a in arts}

NEW = [
    {'name': 'なとり', 'handle': '@Siritoriyowai_', 'followers': None,
     'note': '🚨Xのフォロワー数は取得できず(2026-09-10・2回検索)。'
             'Instagram 325K／TikTok 437.9K＝大物と判断してよい'},
    {'name': '野村萬斎', 'handle': '@mansai_gozaru', 'followers': None,
     'note': '🚨フォロワー数を取得できず(2026-09-10・1回)。'
             '@mansai_gozaru は主宰する狂言会「狂言ござる乃座」の公式'},
    {'name': '春風亭昇太', 'handle': '@syoten1erai', 'followers': None,
     'note': '🚨フォロワー数を取得できず(2026-09-10・1回)。ハンドルは検索で出た候補'},
]

added = 0
for x in NEW:
    if x['name'] in have:
        print('すでにある: %s' % x['name'])
        continue
    arts.append(x)
    print('足した: %s（%s）' % (x['name'], x['followers'] if x['followers'] else '数値は不明'))
    added += 1

if added:
    d['artists']['measured'] = '2026-09-10'
    io.open(p, 'w', encoding='utf-8').write(
        json.dumps(d, ensure_ascii=False, indent=1))
    print('tools/x_log.json を更新（artists %d件）' % len(arts))
else:
    print('足すものが無かった')
