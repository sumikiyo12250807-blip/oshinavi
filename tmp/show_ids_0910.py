# -*- coding: utf-8 -*-
"""指定idのURLと枠を並べる（照合で引っかかった子の実態を見るため）。"""
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
IDS = {int(x) for x in sys.argv[1].split(',')}

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
for e in json.loads(m.group(2)):
    if e['id'] not in IDS:
        continue
    print('== id=%s %s  date=%s  %s' % (e['id'], e['name'][:44], e['date'], e.get('dateLabel', '')[:60]))
    for k, v in (e.get('links') or {}).items():
        if v:
            print('   link.%-8s %s' % (k, v))
    for t in e.get('tickets') or []:
        print('   %-62s date=%s%s' % (t['type'][:62], t['date'],
                                      ('  ' + (t.get('url') or '')) if t.get('url') else ''))
