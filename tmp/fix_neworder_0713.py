# -*- coding: utf-8 -*-
"""NEW_ORDER を genre:new の全件（投入順＝id昇順）に復旧する。
inject_built.py の上書きバグで87件分が飛んだぶんを直す。"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
E = json.loads(m.group(2))
newids = sorted(e['id'] for e in E if e.get('genre') == 'new')
cur = re.search(r'(NEW_ORDER\s*=\s*)\[([0-9,\s]*)\]', h)
before = [int(x) for x in re.findall(r'\d+', cur.group(2))]
no = '[' + ', '.join(str(i) for i in newids) + ']'
h2 = re.sub(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]', r'\g<1>' + no, h, count=1)
open('index.html', 'w', encoding='utf-8').write(h2)
print(f'NEW_ORDER {len(before)}件 → {len(newids)}件 (id{newids[0]}..{newids[-1]})')
missing = [i for i in newids if i not in before]
print(f'  復旧した(飛んでいた)id: {len(missing)}件')
