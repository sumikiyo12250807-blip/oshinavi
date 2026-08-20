# -*- coding: utf-8 -*-
"""券種違いで表示文言だけ増える枠を意図集約（[[feedback_tour_badge_split_by_saledate]] nobinobi方式）。
2331 nobinobi 2026 : 48券種(駐車券付き/枚数セット)が全部 7/15 0:00発売 → DAY1/2DAY通し/DAY2 の3枠に
2323 TREASURE05X   : 4券種が全部 7/11 12:00発売・同一会期 → 1枠に
reconcile が「登録<ぴあ」と出すのは意図集約のノイズ。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--apply' not in sys.argv

NEW = {
    2331: [
        {'type': 'DAY1-1日券（神奈川 11/7公演）7/15 0:00発売',        'startDate': '2026-07-15', 'date': '2026-07-15'},
        {'type': '2DAY通し券（神奈川 11/7〜11/8公演）7/15 0:00発売', 'startDate': '2026-07-15', 'date': '2026-07-15'},
        {'type': 'DAY2-1日券（神奈川 11/8公演）7/15 0:00発売',        'startDate': '2026-07-15', 'date': '2026-07-15'},
    ],
    2323: [
        {'type': '一般発売（愛知 8/8〜9/13公演）7/11 12:00発売', 'startDate': '2026-07-11', 'date': '2026-07-11'},
    ],
}
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
for e in EVENTS:
    if e['id'] not in NEW: continue
    print(f"id={e['id']} {e['artist']}: {len(e['tickets'])}枠 -> {len(NEW[e['id']])}枠")
    for t in NEW[e['id']]: print('   ', t['type'])
    e['tickets'] = NEW[e['id']]
if DRY:
    print('(DRY)')
else:
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open('index.html.bak_0710_consolidate','w',encoding='utf-8').write(h)
    open('index.html','w',encoding='utf-8').write(h[:m.start()]+m.group(1)+new_arr+m.group(3)+h[m.end():])
    print('written')
