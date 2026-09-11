# -*- coding: utf-8 -*-
"""9/14(月)に発売が始まる音楽（jpop/rock/yougaku）の枠を、振り分け済みと新着プール（振り分け前）に分けて全部出す（読むだけ）。"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
D = '2026-09-14'
src = open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
MUSIC = {'jpop', 'rock', 'yougaku'}
for e in ev:
    g = e.get('genre')
    gg = e.get('_genre') if g == 'new' else g
    if gg not in MUSIC:
        continue
    for t in e.get('tickets') or []:
        if t.get('startDate') == D:
            print('%s id%s [%s] %s | %s%s' % ('新着(振り分け前)' if g == 'new' else '振り分け済み', e['id'], gg,
                  e.get('name'), t.get('type'), ' SOLD' if t.get('soldout') else ''))
