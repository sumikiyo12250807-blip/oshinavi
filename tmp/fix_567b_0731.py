# -*- coding: utf-8 -*-
"""id567 dateLabel の語尾を慣例（県名）に戻す。"""
import re, json, datetime, sys
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
E = json.loads(m.group(2))

hit = 0
for e in E:
    if e['id'] != 567:
        continue
    if e['dateLabel'] != '2026年12月3日(木) 開催':
        print('!! 想定外の値:', e['dateLabel']); sys.exit(1)
    e['dateLabel'] = '2026年12月3日(木) 東京'
    print('id=567 dateLabel ->', e['dateLabel'])
    hit += 1

if hit != 1:
    print('!! 対象が %d 件。中止' % hit); sys.exit(1)

new_arr = json.dumps(E, ensure_ascii=False, indent=2)
open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print('=== 適用 ===')
