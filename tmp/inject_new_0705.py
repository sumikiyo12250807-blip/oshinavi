# -*- coding: utf-8 -*-
"""7/5 新着50件(built_new_0705.json)をEVENTSに投入し、NEW_ORDERに新idを登録。
genre:"new"のまま(振り分けはユーザーOK後)。backup付き。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--apply' not in sys.argv

built = json.load(open('tmp/built_new_0705.json', encoding='utf-8'))
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

existing_ids = {e.get('id') for e in EVENTS}
add = [e for e in built if e.get('id') not in existing_ids]
dup = [e['id'] for e in built if e.get('id') in existing_ids]
new_ids = [e['id'] for e in add]

# 全部genre:newであることを確認
notnew = [e['id'] for e in add if e.get('genre') != 'new']
print(f"投入 {len(add)}件 / 既存衝突 {dup} / genre!=new {notnew}")
print(f"新id: {new_ids[0]}..{new_ids[-1]}" if new_ids else "新idなし")

EVENTS2 = EVENTS + add
new_arr = json.dumps(EVENTS2, ensure_ascii=False, indent=2)
# NEW_ORDER登録（id昇順）
no = '[' + ', '.join(str(i) for i in sorted(new_ids)) + ']'
h2, n = re.subn(r'const NEW_ORDER = \[\];', 'const NEW_ORDER = ' + no + ';', h)
assert n == 1, f'NEW_ORDER置換 n={n}'
h3 = h2[:m.start()] + m.group(1) + new_arr + m.group(3) + h2[m.end():]

if DRY:
    print("(DRY) NEW_ORDER置換OK")
else:
    open('index.html.bak_0705_newpool', 'w', encoding='utf-8').write(h)
    open('index.html', 'w', encoding='utf-8').write(h3)
    print(f"written (backup: index.html.bak_0705_newpool) NEW_ORDER {len(new_ids)}件")
