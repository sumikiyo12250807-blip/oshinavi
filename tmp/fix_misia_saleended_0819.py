# -*- coding: utf-8 -*-
"""id=3899 MISIA（宮城 8/28公演）。
これまで「予定枚数終了」で出していたが、ぴあの実文言が今日「販売終了」に変わっていた
（tools/pia_tickets.py の statustext で確認：state=受付終了 / statustext=販売終了）。
[[feedback_saleended_vs_soldout]] に従い soldout は残したまま saleEnded を足してバッジ文言だけ切り替える。
"""
import json, re, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

n = 0
for e in EVENTS:
    if e['id'] != 3899:
        continue
    for t in e.get('tickets') or []:
        if t.get('soldout') and not t.get('saleEnded'):
            t['saleEnded'] = True
            t['saleEndedSince'] = '2026-08-19'
            n += 1
            print('id=3899', t['type'], '→ 販売終了バッジへ')

if n:
    shutil.copyfile('index.html', 'index.html.bak_0819_misia')
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print('=== %d枠 更新 ===' % n)
