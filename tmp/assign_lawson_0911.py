# -*- coding: utf-8 -*-
"""ローチケ9件の下書きジャンルを入れ、今夜振り分ける11件以外を --exclude に並べる（2026-09-11 ユーザー「それでふりわけＯＫ」）。
振り分ける＝ローチケ 7819〜7827（ユーザーが新着タブで確認）／7810 楽天『星影の人』長野（「星影の人 見たよ」）／
           7813 FEST. INAZUMA 2026（ぴあ・朝の独立再導出済み・販売終了の印＝ユーザー選択「1で」）
使い方: python tmp/assign_lawson_0911.py [--apply]"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
G = {7819: 'jpop', 7820: 'chanson', 7821: 'enka', 7822: 'jpop', 7823: 'fes',
     7824: 'jazz', 7825: 'jpop', 7826: 'jpop', 7827: 'musicetc'}
OK = set(G) | {7810, 7813}
src = io.open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
ev = json.loads(m.group(2))
for e in ev:
    if e['id'] in G:
        e['_genre'] = G[e['id']]
    if e['id'] in OK:
        print('id%s %s → %s' % (e['id'], (e.get('name') or '')[:36], e.get('_genre')))
pool = [e['id'] for e in ev if e.get('genre') == 'new']
skip = sorted(set(pool) - OK)
print('新着 %d件 ／ 振り分ける %d件 ／ 残す %d件' % (len(pool), len(OK & set(pool)), len(skip)))
io.open('tmp/assign_lawson_exclude_0911.txt', 'w', encoding='utf-8').write(','.join(map(str, skip)))
if '--apply' in sys.argv:
    io.open('index.html', 'w', encoding='utf-8').write(src[:m.start()] + m.group(1) + json.dumps(ev, ensure_ascii=False, indent=2) + m.group(3) + src[m.end():])
    print('下書きジャンルを書き込み')
