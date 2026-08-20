# -*- coding: utf-8 -*-
"""7/10 期限切れ削除22件（ユーザーOK「削除」）。
二段構え= reconcile ぴあ0一致 ⇄ build_pia_entries 再パースで買える枠ゼロ、が完全一致。
非ぴあ2件は個別裏取り: 217=e+生HTML「受付は全て終了しました」/ 1200=ぴあ全枠販売終了。
374/841/2259 は隠れ枠ヒールで全枠 予定枚数終了と判明した子。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DEL = {217, 326, 372, 374, 449, 499, 555, 610, 841, 853, 860, 1142,
       1200, 1240, 1322, 1385, 1485, 1508, 1521, 1671, 2162, 2259}
DRY = '--apply' not in sys.argv
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
before = len(EVENTS)
kept = [e for e in EVENTS if e.get('id') not in DEL]
removed = [(e['id'], e.get('artist', '')) for e in EVENTS if e.get('id') in DEL]
for i, a in removed:
    print(f'  - {a}')
print(f"=== delete {len(removed)}/{len(DEL)} (before {before} -> after {len(kept)}) ===")
missing = DEL - set(i for i, _ in removed)
if missing: print("!! not found:", sorted(missing))
if DRY:
    print("(DRY)")
else:
    new_arr = json.dumps(kept, ensure_ascii=False, indent=2)
    open('index.html.bak_0710_morning_delete','w',encoding='utf-8').write(h)
    open('index.html','w',encoding='utf-8').write(h[:m.start()]+m.group(1)+new_arr+m.group(3)+h[m.end():])
    print("written (backup: index.html.bak_0710_morning_delete)")
