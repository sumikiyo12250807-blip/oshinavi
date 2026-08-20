# -*- coding: utf-8 -*-
"""venue の空カッコ「全国ツアー（）」→「全国ツアー」。
ぴあ側に会場名が載っていない複数県ツアーは会場を埋められないので、
せめて空のカッコを出さない（表示品質）。会場が判明したら別途埋める。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--apply' not in sys.argv
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
n = 0
for e in EVENTS:
    v = e.get('venue') or ''
    if '（）' not in v: continue
    new = v.replace('（）', '').strip()
    if new != v:
        print(f"  id={e['id']:<5} {e['artist'][:24]:<26} {v}  ->  {new}")
        e['venue'] = new; n += 1
print(f'=== {n}件 ===')
if DRY:
    print('(DRY)')
elif n:
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open('index.html.bak_0710_paren','w',encoding='utf-8').write(h)
    open('index.html','w',encoding='utf-8').write(h[:m.start()]+m.group(1)+new_arr+m.group(3)+h[m.end():])
    print('written')
