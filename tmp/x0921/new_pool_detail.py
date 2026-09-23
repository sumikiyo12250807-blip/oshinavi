# -*- coding: utf-8 -*-
"""新着で9/22〜9/24に発売が始まる31件の中身（公演名・会場・公演日・枠・URL）を出す（読むだけ・9/21夜）。
X投稿に足す行を作るためと、取りこぼし点検の名前を決めるため。"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
DAYS = ['2026-09-22', '2026-09-23', '2026-09-24']
h = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
for e in ev:
    if e.get('genre') != 'new' or e['id'] == 17332:
        continue
    ts = [t for t in e.get('tickets') or [] if t.get('startDate') in DAYS and not t.get('soldout')]
    if not ts:
        continue
    L = {k: v for k, v in (e.get('links') or {}).items() if v}
    print('id%s | %s | artist=%s | %s | %s | %s' % (e['id'], e.get('name'), e.get('artist'), e.get('prefecture'),
                                                   e.get('venue'), e.get('dateLabel')))
    for t in ts:
        print('     %s | %s' % (t.get('startDate'), t.get('type')))
    print('     links=%s' % L)
