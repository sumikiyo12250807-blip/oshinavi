# -*- coding: utf-8 -*-
"""さだまさし(id1)に大阪12/2・12/3の先行枠を足す。**そのページのURLを焼き込む**。

ユーザーが楽天の特設ページ（/features/sada-tour-2026/）を持ってきて見つかった取りこぼし。
楽天側は10/3発売でまだ購入ページが立っていないので、いまはぴあのURLで載せる。
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
URL = 'https://ticket.pia.jp/pia/event.do?eventCd=2631142'

src = io.open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
e = next(x for x in events if x['id'] == 1)

built = json.load(io.open('tmp/built_sada_0910.json', encoding='utf-8'))
news = []
have = {t.get('type') for t in (e.get('tickets') or [])}
for b in built:
    for t in b['tickets']:
        if t['type'] in have:
            continue
        t = dict(t)
        t['url'] = t.get('url') or URL
        news.append(t)

if not news:
    print('足すものが無い')
    sys.exit(0)

e.setdefault('tickets', []).extend(news)
# 千秋楽が12/3に伸びる。会期のラベルも伸ばす（縮めない）
ds, y = [], None
for a, b2, c in re.findall(r'(?:(\d{4})年)?\s*(\d{1,2})月(\d{1,2})日', e.get('dateLabel') or ''):
    if a:
        y = int(a)
    if y:
        ds.append('%04d-%02d-%02d' % (y, int(b2), int(c)))
d0 = min(ds + [e['date']]) if ds else e['date']
d1 = max(ds + [e['date'], '2026-12-03'])
WD = '月火水木金土日'
import datetime


def jp(s):
    yy, mm2, dd = [int(x) for x in s.split('-')]
    return '%d年%d月%d日(%s)' % (yy, mm2, dd, WD[datetime.date(yy, mm2, dd).weekday()])


prefs = []
for t in e['tickets']:
    bm = re.search(r'（([^（）]*?)\s*(?:R\d+年\s*)?\d{1,2}/\d{1,2}', t.get('type') or '')
    if not bm:
        continue
    for p in re.split(r'[・/／]', bm.group(1)):
        p = p.strip()
        if p and p != '全国' and p not in prefs:
            prefs.append(p)
e['date'] = d1
if prefs:
    e['prefecture'] = '・'.join(prefs)
e['dateLabel'] = '%s〜%s %s' % (jp(d0), jp(d1), e.get('prefecture') or '')

for t in news:
    print('＋%s | %s | %s' % (t['type'], t['date'], t['url']))
print('date=%s / %s' % (e['date'], e['dateLabel']))

if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
arr = json.dumps(events, ensure_ascii=False, indent=2)
io.open('index.html', 'w', encoding='utf-8').write(
    src[:m.start()] + m.group(1) + arr + m.group(3) + src[m.end():])
print('書き込み完了')
