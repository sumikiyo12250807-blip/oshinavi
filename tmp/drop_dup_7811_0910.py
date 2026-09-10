# -*- coding: utf-8 -*-
"""投入した id7811 STARフェス を外す（既存 id4384 と同じ販売窓＝二重登録）。

🚨消したidは NEW_ORDER からも外す（[[feedback_new_order_array]]）。
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
DROP = 7819

src = io.open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
before = len(events)
events = [e for e in events if e['id'] != DROP]
print('EVENTS %d → %d' % (before, len(events)))

out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2) + m.group(3) + src[m.end():]

mo = re.search(r'(  const NEW_ORDER = )(\[[^\]]*\])(;)', out, re.S)
arr = json.loads(mo.group(2))
arr2 = [i for i in arr if i != DROP]
print('NEW_ORDER %d → %d' % (len(arr), len(arr2)))
out = out[:mo.start()] + mo.group(1) + json.dumps(arr2) + mo.group(3) + out[mo.end():]

if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
io.open('index.html', 'w', encoding='utf-8').write(out)

# 突合（genre:new と NEW_ORDER が一致するか）
h = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
pool = {e['id'] for e in ev if e.get('genre') == 'new'}
no = set(json.loads(re.search(r'const NEW_ORDER = (\[[^\]]*\])', h, re.S).group(1)))
print('新着プール %d / NEW_ORDER %d / 差 %s %s'
      % (len(pool), len(no), sorted(pool - no)[:5], sorted(no - pool)[:5]))
print('書き込み完了')
