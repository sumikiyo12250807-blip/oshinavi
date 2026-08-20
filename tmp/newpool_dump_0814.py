# -*- coding: utf-8 -*-
"""新着50件を目視レビュー用に1行ずつ出す（ユーザーが新着タブで見るのと同じ観点）。"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
h = open('index.html', encoding='utf-8', newline='').read()
EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
order = [int(x) for x in re.findall(r'\d+', re.search(r'NEW_ORDER\s*=\s*\[([0-9,\s]*)\]', h).group(1))]
by = {e['id']: e for e in EV}
for i, eid in enumerate(order, 1):
    e = by.get(eid)
    if not e:
        continue
    print('%2d. id%-5s [%s] %s' % (i, eid, e.get('genre'), e.get('name')))
    print('     %s ／ %s' % (e.get('venue'), e.get('dateLabel')))
    for t in e.get('tickets') or []:
        print('     ・%s' % t.get('type'))
