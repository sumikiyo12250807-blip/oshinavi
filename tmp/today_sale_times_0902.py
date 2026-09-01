# -*- coding: utf-8 -*-
"""今日これから発売になる枠の「発売時刻」を数える。
昼のヒールを何時に回すかを決めるために使う（feedback_noon_heal_missed_twice）。"""
import re, json, sys, datetime, collections
sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today()
TD = TODAY.isoformat()
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = json.loads(m.group(2))
cnt = collections.Counter()
for e in EV:
    for t in (e.get('tickets') or []):
        if t.get('startDate') != TD:
            continue
        mm = re.search(r'(\d{1,2})/(\d{1,2})\s*(\d{1,2}):(\d{2})\s*発売', t.get('type') or '')
        if mm:
            cnt[f'{int(mm.group(3)):02d}:{mm.group(4)}'] += 1
        else:
            cnt['時刻なし'] += 1
print(f'=== 今日({TD})発売開始の枠 ===')
for k in sorted(cnt):
    print(f'  {k}  {cnt[k]}枠')
print(f'  合計 {sum(cnt.values())}枠')
