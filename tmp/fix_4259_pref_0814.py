# -*- coding: utf-8 -*-
"""id4259（台北開催）の「全国」表記を「台湾」に直す。
「全国」は日本の全国ツアーの意味で使っているので、海外公演に付くと嘘になる
（memory: feedback_no_fake_info / 県名が取れない時だけ全国＝reference_pia_tickets_tool）。"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = json.loads(m.group(2))

for e in EV:
    if e.get('id') != 4259:
        continue
    before = json.dumps({k: e.get(k) for k in ('prefecture', 'venue', 'dateLabel')},
                        ensure_ascii=False)
    e['prefecture'] = '台湾'
    e['dateLabel'] = (e.get('dateLabel') or '').replace(' 全国 ', ' 台湾 ')
    for t in e.get('tickets') or []:
        t['type'] = (t.get('type') or '').replace('（全国 ', '（台湾 ')
    print('旧:', before)
    print('新:', json.dumps({k: e.get(k) for k in ('prefecture', 'venue', 'dateLabel')},
                            ensure_ascii=False))
    for t in e.get('tickets') or []:
        print('   枠:', t.get('type'))

new_arr = json.dumps(EV, ensure_ascii=False, indent=2).replace('\n', NL)
open('index.html.bak_0814_4259', 'w', encoding='utf-8', newline='').write(h)
open('index.html', 'w', encoding='utf-8', newline='').write(
    h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print('→ 適用')
