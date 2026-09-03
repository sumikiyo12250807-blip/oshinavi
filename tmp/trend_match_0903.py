# -*- coding: utf-8 -*-
"""トレンドの名前を index.html の在庫に当てて、「いま買える枠」があるものを探す。
memory feedback_x_trend_match_inventory＝トレンド8位までに在庫があれば1本投稿する。
🚨トレンドの話題自体には触れない（憶測は嘘になる）。ここは在庫の有無を見るだけ。
"""
import re, json, sys, io, datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
TODAY = '2026-09-03'

TRENDS = ['ミックファイア', '素のまんま', '麻布十番まつり', 'メタノール',
          'ラオス国籍', 'ノーベル化学賞', 'A-RISE', 'およ家']

src = open('index.html', encoding='utf-8', newline='').read()
EVENTS = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S).group(2))


def visible(t):
    if t.get('saleUntilSoldOut') or t.get('soldout'):
        return True
    sd, d = t.get('startDate'), t.get('date')
    return not ((not sd or sd <= TODAY) and (d or '') < TODAY)


for kw in TRENDS:
    hits = []
    for e in EVENTS:
        blob = (e.get('name') or '') + (e.get('title') or '') + (e.get('artist') or '')
        if kw not in blob:
            continue
        live = [t for t in e.get('tickets', []) if visible(t) and not t.get('soldout')]
        if live:
            hits.append((e, live))
    if hits:
        print('■ 「%s」… 在庫あり %d件' % (kw, len(hits)))
        for e, live in hits[:4]:
            print('   id%d %s ／%s 公演%s' % (e['id'], (e.get('name') or '')[:40],
                                            e.get('prefecture'), e.get('date')))
            for t in live[:3]:
                print('        - %s' % t.get('type'))
    else:
        print('□ 「%s」… 在庫なし' % kw)
