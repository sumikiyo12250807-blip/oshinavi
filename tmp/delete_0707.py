# -*- coding: utf-8 -*-
"""7/7 削除: ぴあ/楽天0枠を実ページ裏取り済の期限切れ19件。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DEL = {199,335,394,629,936,1192,1217,1231,1310,1457,1470,1507,1533,1566,1581,1582,1666,1670,1678}
DRY = '--apply' not in sys.argv
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
before = len(EVENTS)
kept = [e for e in EVENTS if e.get('id') not in DEL]
removed = [e['id'] for e in EVENTS if e.get('id') in DEL]
print(f"=== delete {len(removed)}/{len(DEL)} (before {before} -> after {len(kept)}) ===")
missing = DEL - set(removed)
if missing: print("!! not found:", sorted(missing))
if DRY:
    print("(DRY)")
else:
    new_arr = json.dumps(kept, ensure_ascii=False, indent=2)
    open('index.html.bak_0707_morning_delete','w',encoding='utf-8').write(h)
    open('index.html','w',encoding='utf-8').write(h[:m.start()]+m.group(1)+new_arr+m.group(3)+h[m.end():])
    print("written (backup: index.html.bak_0707_morning_delete)")
