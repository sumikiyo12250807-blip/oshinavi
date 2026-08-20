# -*- coding: utf-8 -*-
"""id567 鈴木実貴子ズ: 7/30公演が終わり残るのは12/3公演のみ。
ev.date が 7/30 のままだと画面から消える（reconcile ❌QC-EVDATE）ので千秋楽を12/3へ。
dateLabel も終わった7/30を落として12/3単独にする。"""
import re, json, datetime, sys
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
E = json.loads(m.group(2))

hit = 0
for e in E:
    if e['id'] != 567:
        continue
    before = (e['date'], e['dateLabel'])
    e['date'] = '2026-12-03'
    e['dateLabel'] = '2026年12月3日(木) 開催'
    print('id=567 date: %s -> %s' % (before[0], e['date']))
    print('id=567 dateLabel: %s -> %s' % (before[1], e['dateLabel']))
    print('tickets:', json.dumps(e['tickets'], ensure_ascii=False))
    hit += 1

if hit != 1:
    print('!! 対象が %d 件。中止' % hit); sys.exit(1)

bak = 'index.html.bak_%s_fix567' % datetime.date.today().strftime('%m%d')
open(bak, 'w', encoding='utf-8').write(h)
new_arr = json.dumps(E, ensure_ascii=False, indent=2)
open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print('=== 適用 (backup: %s) ===' % bak)
