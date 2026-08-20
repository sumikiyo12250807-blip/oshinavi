# -*- coding: utf-8 -*-
"""7/6 新着50件(built_new_0706.json)をEVENTSに投入、NEW_ORDERに新idを追記。
既存NEW_ORDER(=保留アート2034/2035)は保持。genre:"new"のまま(振り分けOK後)。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--apply' not in sys.argv

built = json.load(open('tmp/built_new_0706.json', encoding='utf-8'))
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
existing = {e.get('id') for e in EVENTS}
add = [e for e in built if e.get('id') not in existing]
dup = [e['id'] for e in built if e.get('id') in existing]
new_ids = [e['id'] for e in add]
notnew = [e['id'] for e in add if e.get('genre') != 'new']
print(f"投入 {len(add)}件 / 既存衝突 {dup} / genre!=new {notnew}")
print(f"新id: {new_ids[0]}..{new_ids[-1]}" if new_ids else "なし")

EVENTS2 = EVENTS + add
new_arr = json.dumps(EVENTS2, ensure_ascii=False, indent=2)
mo = re.search(r'const NEW_ORDER = (\[[0-9,\s]*\]);', h)
cur = json.loads(mo.group(1))
for i in sorted(new_ids):
    if i not in cur:
        cur.append(i)
no = '[' + ', '.join(str(i) for i in cur) + ']'
h2 = h[:mo.start()] + 'const NEW_ORDER = ' + no + ';' + h[mo.end():]
h3 = h2[:m.start()] + m.group(1) + new_arr + m.group(3) + h2[m.end():]

if DRY:
    print(f"(DRY) NEW_ORDER {len(cur)}件になる: 先頭{cur[:4]}...")
else:
    open('index.html.bak_0706_newpool', 'w', encoding='utf-8').write(h)
    open('index.html', 'w', encoding='utf-8').write(h3)
    print(f"written (backup: index.html.bak_0706_newpool) NEW_ORDER {len(cur)}件")
