# -*- coding: utf-8 -*-
"""id1149 いぎなり東北産の枠に startDate を入れる。
ぴあ statustext が「本日発売初日」＝今日(8/14)が発売初日。startDate が無いと renderCard が
「販売中」と出してしまい、「本日発売は一日中いちばん上」ルールから落ちる
（memory: feedback_display_order / feedback_harvest_today_sale_enddate）。
heal の carry_start_dates は元の枠に発売日が無いと引き継げないので、ここで手当てする。"""
import re, json, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

TODAY = datetime.date.today().isoformat()
h = open('index.html', encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = json.loads(m.group(2))
for e in EV:
    if e.get('id') != 1149:
        continue
    for t in e.get('tickets') or []:
        if t.get('startDate'):
            continue
        t['startDate'] = TODAY
        print('id1149 %s → startDate=%s / date=%s' % (t.get('type'), t['startDate'], t.get('date')))
new_arr = json.dumps(EV, ensure_ascii=False, indent=2).replace('\n', NL)
open('index.html.bak_0814_1149start', 'w', encoding='utf-8', newline='').write(h)
open('index.html', 'w', encoding='utf-8', newline='').write(
    h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print('→ 適用')
