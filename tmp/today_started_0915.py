# -*- coding: utf-8 -*-
"""「〆切日に発売時刻がくっつく」型を探す（読むだけ・2026-09-15 朝）。today_started_0914.py と同じ中身で、出力の名前だけ今日にした。
条件＝ startDate が今日以前 かつ date > 今日 かつ 券種名が「M/D HH:MM発売」で終わる（かつ売り切れでない）。
使い方: python tmp/today_started_0915.py
出力: tmp/today_started_ids_0915.txt（発売時刻を過ぎた枠を持つid）
"""
import datetime
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
now = datetime.datetime.now()
TODAY = now.date().isoformat()
src = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
past, later = {}, {}
for e in ev:
    for t in e.get('tickets') or []:
        sd = t.get('startDate') or ''
        if t.get('soldout') or not sd or sd > TODAY or not (t.get('date') or '') > TODAY:
            continue
        m = re.search(r'(\d{1,2}):(\d{2})発売$', t.get('type') or '')
        if not m:
            continue
        hhmm = (int(m.group(1)), int(m.group(2)))
        started = sd < TODAY or hhmm <= (now.hour, now.minute)
        bucket = past if started else later
        url = t.get('url') or e.get('url') or ''
        bucket.setdefault(e['id'], []).append('%s（発売 %s／締切 %s）%s' % (t.get('type'), sd, t.get('date'), ' [e+]' if 'eplus' in url else ''))
print('発売時刻を過ぎた枠を持つエントリ %d件 ／ 発売時刻がまだ先のエントリ %d件' % (len(past), len(later)))
for i, ts in sorted(past.items()):
    print('  id%s: %s' % (i, ' ／ '.join(ts[:3]) + (' ほか%d枠' % (len(ts) - 3) if len(ts) > 3 else '')))
io.open('tmp/today_started_ids_0915.txt', 'w', encoding='utf-8').write(','.join(str(i) for i in sorted(past)))
