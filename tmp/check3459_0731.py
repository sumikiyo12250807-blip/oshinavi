# -*- coding: utf-8 -*-
"""削除候補 3459 と、残った隠れ枠2つの実態を出す。"""
import json, re, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')
today = datetime.date.today().isoformat()
h = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

e = next(x for x in EVENTS if x['id'] == 3459)
print('id=3459 %s' % e['name'])
print('   %s / %s / genre=%s' % (e['prefecture'], e['dateLabel'], e['genre']))
print('   pia=%s' % e['links'].get('pia'))
for t in e['tickets']:
    print('   - %s | date=%s start=%s' % (t['type'], t['date'], t.get('startDate', '-')))

print('\n--- 残っている隠れ枠(startDate==date<=today) ---')
for x in EVENTS:
    for t in x.get('tickets') or []:
        sd, d = t.get('startDate'), t.get('date')
        if sd and sd == d and d <= today:
            print('  id=%d %s | %s' % (x['id'], x['name'][:34], t['type']))
