# -*- coding: utf-8 -*-
"""id=833 FREEDOM NAGOYA 2026: 7/30公演・8/12公演の一般発売が「予定枚数終了」。
reconcile STALE(再現)→ぴあ実ページWebFetchで裏取り。売切枠は載せない([[feedback_oshinavi_concept]])。
他5枠(8/4・9/17一般／8/27・10/23先行／10/23 8/1発売)は生存のためエントリ維持。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--apply' not in sys.argv
DROP = ('一般発売（愛知 7/30公演）', '一般発売（愛知 8/12公演）')
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
for e in EVENTS:
    if e['id'] != 833: continue
    before = len(e['tickets'])
    e['tickets'] = [t for t in e['tickets'] if not any(d in (t.get('type') or '') for d in DROP)]
    e['verifiedAt'] = '2026-07-10'
    print(f"tickets {before} -> {len(e['tickets'])}")
    for t in e['tickets']: print('  ', t.get('type'))
if DRY:
    print("(DRY)")
else:
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open('index.html.bak_0710_fix833','w',encoding='utf-8').write(h)
    open('index.html','w',encoding='utf-8').write(h[:m.start()]+m.group(1)+new_arr+m.group(3)+h[m.end():])
    print("written")
