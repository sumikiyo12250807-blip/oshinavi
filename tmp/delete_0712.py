# -*- coding: utf-8 -*-
"""7/12 期限切れ削除（ユーザーOK済9件）。"""
import re, json, datetime, sys
sys.stdout.reconfigure(encoding='utf-8')
DEL = [2148, 61, 265, 461, 506, 2301, 412, 842, 2230]
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
E = json.loads(m.group(2))
before = len(E)
gone = [e for e in E if e['id'] in DEL]
E = [e for e in E if e['id'] not in DEL]
bak = f'index.html.bak_{datetime.date.today():%m%d}_morning_delete'
open(bak, 'w', encoding='utf-8').write(h)
new_arr = json.dumps(E, ensure_ascii=False, indent=2)
open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
for e in gone:
    print(f"  削除 id={e['id']} {e.get('artist','')[:30]}")
print(f"=== {before}→{len(E)} (削除{before-len(E)}件 / backup {bak}) ===")
