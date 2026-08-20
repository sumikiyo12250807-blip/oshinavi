# -*- coding: utf-8 -*-
"""7/5 期限切れ削除 19件（ユーザーOK「その他は削除」）。
id5は販売中で除外・1430/1582は抽選結果発表前で保留。売切/受付終了/公演終了の19件を除去。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--apply' not in sys.argv
DEL = {82, 253, 97, 249, 339, 537, 684, 715, 724, 830,
       1104, 1152, 1177, 1363, 1433, 1746, 1760, 1820, 1874}
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
before = len(EVENTS)
removed = [e for e in EVENTS if e.get('id') in DEL]
kept = [e for e in EVENTS if e.get('id') not in DEL]
for e in removed:
    print(f"  削除 id={e['id']} {e.get('artist','')[:26]}")
print(f"=== {before} -> {len(kept)} ({len(removed)}件削除) ===")
missing = DEL - {e.get('id') for e in removed}
if missing:
    print(f"!! 見つからないid: {sorted(missing)}")
if DRY:
    print("(DRY)")
else:
    new_arr = json.dumps(kept, ensure_ascii=False, indent=2)
    open('index.html.bak_0705_morning_delete', 'w', encoding='utf-8').write(h)
    open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
    print("written (backup: index.html.bak_0705_morning_delete)")
