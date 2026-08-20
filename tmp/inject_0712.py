# -*- coding: utf-8 -*-
"""7/12 新着100件(built_0712.json)をEVENTS末尾に投入・NEW_ORDER更新。"""
import re, json, datetime, sys
sys.stdout.reconfigure(encoding='utf-8')
built = json.load(open('tmp/built_0712.json', encoding='utf-8'))
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
E = json.loads(m.group(2))
exist = {e['id'] for e in E}
add = [e for e in built if e['id'] not in exist]
assert len(add) == len(built), f'id重複! built{len(built)} add{len(add)}'
E += add
bak = f'index.html.bak_{datetime.date.today():%m%d}_newpool'
open(bak, 'w', encoding='utf-8').write(h)
new_arr = json.dumps(E, ensure_ascii=False, indent=2)
h2 = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]
new_ids = sorted(e['id'] for e in add)
no_new = '[' + ', '.join(str(i) for i in new_ids) + ']'
h2, n = re.subn(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]', r'\g<1>' + no_new, h2, count=1)
assert n == 1, f'NEW_ORDER置換={n}'
open('index.html', 'w', encoding='utf-8').write(h2)
print(f'投入 {len(add)}件 id{new_ids[0]}..{new_ids[-1]} / NEW_ORDER {len(new_ids)}件 / EVENTS {len(E)}件 (backup {bak})')
