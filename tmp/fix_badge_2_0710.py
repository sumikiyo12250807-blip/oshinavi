# -*- coding: utf-8 -*-
"""記号掃除でおかしくなった2件を手直し。
id=269 「手数料無料★一般発売」→ 中の★も落として「手数料無料 一般発売」
id=2260「一般発売島根公演」→ 県は括弧内にあり重複。「一般発売」に戻す。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--apply' not in sys.argv
FIX = {
    269:  ('手数料無料★一般発売（東京 9/12〜9/26公演）〜9/26 18:00',
           '手数料無料 一般発売（東京 9/12〜9/26公演）〜9/26 18:00'),
    2260: ('一般発売島根公演（島根 7/25公演）〜7/21 23:59',
           '一般発売（島根 7/25公演）〜7/21 23:59'),
}
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
n = 0
for e in EVENTS:
    if e['id'] not in FIX: continue
    old, new = FIX[e['id']]
    for t in e.get('tickets', []):
        if t.get('type') == old:
            t['type'] = new; n += 1
            print(f"  id={e['id']} {old}  ->  {new}")
print(f'=== {n}件 ===')
if DRY:
    print('(DRY)')
elif n:
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open('index.html.bak_0710_badge2','w',encoding='utf-8').write(h)
    open('index.html','w',encoding='utf-8').write(h[:m.start()]+m.group(1)+new_arr+m.group(3)+h[m.end():])
    print('written')
