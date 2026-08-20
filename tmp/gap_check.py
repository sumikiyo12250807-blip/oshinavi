# -*- coding: utf-8 -*-
"""楽天の締切(data-date)が「公演前日」の決め打ちではなく実データかを確認する。"""
import json, re, sys, datetime, collections
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = [e for e in json.loads(m.group(2)) if e.get('genre') == 'new' and (e.get('links') or {}).get('rakuten')]

def d(s):
    return datetime.date(*[int(x) for x in s.split('-')])

cnt = collections.Counter()
rows = []
for e in EV:
    for t in e['tickets']:
        gap = (d(e['date']) - d(t['date'])).days
        cnt[gap] += 1
        rows.append((gap, e['name'][:34], t['type'][:46], t['date'], e['date'], t.get('saleEndUnknown')))

print('=== 締切が公演日の何日前か（楽天 新着%d件・全枠）===' % len(EV))
for g in sorted(cnt):
    print('  %3d日前: %2d枠' % (g, cnt[g]))
print('\n=== 前日(1日前)でない枠 ===')
for gap, n, ty, td, ed, unk in sorted(rows):
    if gap != 1:
        print('  %3d日前 | %-34s | %s | 締切%s 公演%s%s' % (gap, n, ty, td, ed, ' ⚠️締切不明' if unk else ''))
