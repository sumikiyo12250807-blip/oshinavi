# -*- coding: utf-8 -*-
"""reconcile_eplus のFAIL行(id/tインデックス)を index.html の実チケットに突き合わせ、
「今も画面に出ている枠か(date>=today)」で仕分けする。画面に出ていない枠は嘘にならない＝後回し。
"""
import re, json, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
byid = {e['id']: e for e in json.loads(m.group(2))}

rows = []
for path in ('tmp/recon_eplus_0815.txt', 'tmp/recon_eplus_retry_0815.txt'):
    try:
        txt = open(path, encoding='utf-8').read()
    except FileNotFoundError:
        continue
    for mm in re.finditer(r'id(\d+) t(\d+) \[([^\]]+)\]', txt):
        rows.append((int(mm.group(1)), int(mm.group(2)), mm.group(3)))

seen, live, dead = set(), [], []
for eid, ti, kind in rows:
    key = (eid, ti, kind)
    if key in seen:
        continue
    seen.add(key)
    e = byid.get(eid)
    if not e or ti >= len(e['tickets']):
        continue
    t = e['tickets'][ti]
    rec = (eid, e['name'][:34], kind, t.get('type', '')[:44], t.get('date'), t.get('url') or '')
    (live if (t.get('date') or '') >= TODAY else dead).append(rec)

print('=== 画面に出ている枠のFAIL（嘘になる・要対応） %d ===' % len(live))
for r in sorted(live):
    print('  id%-5d %-34s [%s] %s | %s' % (r[0], r[1], r[2], r[3], r[4]))
print()
print('=== すでに画面から消えている枠のFAIL（無害・掃除は後回し） %d ===' % len(dead))
cnt = {}
for r in dead:
    cnt[r[2]] = cnt.get(r[2], 0) + 1
print('   内訳:', cnt)
