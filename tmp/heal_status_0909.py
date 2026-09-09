# -*- coding: utf-8 -*-
"""ヒールの結果jsonのstatus内訳と、index.htmlに残っている隠れ枠を数える。"""
import io, re, json, collections, sys
sys.stdout.reconfigure(encoding='utf-8')

TODAY = "2026-09-09"

d = json.load(io.open('tmp/heal_stale.json', encoding='utf-8'))
rows = d if isinstance(d, list) else d.get('rows') or d.get('items') or []
if isinstance(d, dict) and not rows:
    print('keys:', list(d.keys())[:20])
c = collections.Counter(r.get('status') for r in rows)
print('=== heal_stale.json の status 内訳 ===')
for k, v in c.most_common():
    print(f'  {k:>12} {v}')

h = io.open('index.html', encoding='utf-8', newline='').read()
evs = json.loads(re.search(r'const EVENTS = (\[.*?\]);\r?\n', h, re.S).group(1))
hidden = []
for e in evs:
    for t in e.get('tickets', []):
        sd, dt = t.get('startDate'), t.get('date')
        if sd and dt and sd == dt and dt <= TODAY and not t.get('soldout') and not t.get('saleUntilSoldOut'):
            hidden.append((e['id'], e.get('name', '')[:32], t.get('type', '')[:44], dt))
print(f'\n=== 残っている隠れ枠 (startDate==date かつ date<=today) = {len(hidden)}枠 ===')
todays = [x for x in hidden if x[3] == TODAY]
print(f'  うち今日発売ぶん {len(todays)}枠 / 昨日以前 {len(hidden)-len(todays)}枠')
for r in hidden[:25]:
    print('   id=%-6s %s | %s | %s' % r)
