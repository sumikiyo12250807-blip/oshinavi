# -*- coding: utf-8 -*-
"""7/9 期限切れ削除19件。二段構え(reconcile ぴあ0一致)＋957公演終了＋138/887 WebFetch裏取り済。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DEL = {138,157,402,878,957,1316,1320,1326,1330,1448,1588,1589,1646,1662,1687,1732,1846,1897,887}
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
    open('index.html.bak_0709_morning_delete','w',encoding='utf-8').write(h)
    open('index.html','w',encoding='utf-8').write(h[:m.start()]+m.group(1)+new_arr+m.group(3)+h[m.end():])
    print("written (backup: index.html.bak_0709_morning_delete)")
