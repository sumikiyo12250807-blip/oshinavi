# -*- coding: utf-8 -*-
"""8/18発売のX投稿4本ぶんの事実を、登録データからそのまま出す（Fableに渡す素材）。
数字・会場・日付は崩さない。ここに無いことは本文に書かせない。"""
import io, re, sys, json, datetime
sys.stdout.reconfigure(encoding='utf-8')

idx = io.open('index.html', encoding='utf-8').read()
EV = {e['id']: e for e in json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', idx, re.S).group(2))}

for eid in (4272, 4273, 4358, 4330, 2965):
    e = EV.get(eid)
    if not e:
        print('id%d 無し' % eid); continue
    print('=== id%d %s' % (eid, e.get('artist', '')))
    print('   name      : %s' % e.get('name', ''))
    print('   会場/県   : %s / %s' % (e.get('venue', ''), e.get('prefecture', '')))
    print('   公演日    : %s ／ %s' % (e.get('date', ''), e.get('dateLabel', '')))
    print('   ジャンル  : %s' % e.get('genre'))
    print('   ぴあURL   : %s' % ((e.get('links') or {}).get('pia', '')))
    for t in e.get('tickets') or []:
        print('   枠: %s | 開始 %s 〜 締切 %s' % (t.get('type'), t.get('startDate'), t.get('date')))
    print()

# まとめ用＝8/18に発売開始する件数と時刻の散らばり
TARGET, MD = '2026-08-18', '8/18'
rows = []
for e in EV.values():
    for t in e.get('tickets') or []:
        if t.get('soldout'):
            continue
        ty = t.get('type') or ''
        if t.get('startDate') == TARGET or re.search(r'%s\s*\d{1,2}:\d{2}\s*発売' % re.escape(MD), ty):
            m = re.search(r'%s\s*(\d{1,2}:\d{2})\s*発売' % re.escape(MD), ty)
            rows.append((m.group(1) if m else '(時刻不明)', e['id'], e.get('artist', '')[:30]))
            break
rows.sort(key=lambda r: (r[0] == '(時刻不明)', r[0]))
print('=== 8/18 発売開始 %d件・時刻の散らばり ===' % len(rows))
import collections
for tm, n in sorted(collections.Counter(r[0] for r in rows).items()):
    print('   %-10s %d件' % (tm, n))
print()
print('   一番早い: %s / 一番遅い: %s' % (rows[0][0], [r[0] for r in rows if r[0] != '(時刻不明)'][-1]))
