# -*- coding: utf-8 -*-
"""7/1 バッジ集約(修正2): 1721を[[feedback-tour-badge-split-by-saledate]]準拠で2枠に。
同一販売日は1バッジに公演日列挙(2次先着=両日7/3発売/一般=両日7/20発売)。backupは別名で原本保持。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

NEW = {
    1721: [
        {"type": "2次先着受付（長崎 10/10・10/11公演）7/3 10:00発売", "startDate": "2026-07-03", "date": "2026-07-03"},
        {"type": "一般発売（長崎 10/10・10/11公演）7/20 10:00発売", "startDate": "2026-07-20", "date": "2026-07-20"},
    ],
}
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
for e in EVENTS:
    if e['id'] in NEW:
        old = len(e.get('tickets', []))
        e['tickets'] = NEW[e['id']]
        print(f"id={e['id']} {e['artist'][:26]} 枠 {old} -> {len(NEW[e['id']])}")
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
open('index.html.bak_0701_badgefix2', 'w', encoding='utf-8').write(h)
open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print("written (backup: index.html.bak_0701_badgefix2)")
