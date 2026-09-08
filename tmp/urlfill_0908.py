# -*- coding: utf-8 -*-
"""新着プール(NEW_ORDER)のエントリで、ticket.url が入っているか空かを数える。"""
import json, re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
src = open('index.html', encoding='utf-8').read()
i = src.index('const EVENTS'); j = src.index('[', i)
d = 0; k = j; ins = False; esc = False
while k < len(src):
    c = src[k]
    if ins:
        if esc: esc = False
        elif c == '\\': esc = True
        elif c == '"': ins = False
    else:
        if c == '"': ins = True
        elif c == '[': d += 1
        elif c == ']':
            d -= 1
            if d == 0: break
    k += 1
events = json.loads(src[j:k+1])
m = re.search(r'const NEW_ORDER = \[([^\]]*)\]', src)
new_ids = [int(x) for x in m.group(1).split(',')]
byid = {e['id']: e for e in events}
tot = filled = 0
empty_entries = []
for i2 in new_ids:
    e = byid.get(i2)
    if not e: continue
    ts = e.get('tickets', [])
    f = sum(1 for t in ts if t.get('url'))
    tot += len(ts); filled += f
    if ts and f == 0:
        empty_entries.append((i2, len(ts)))
with open('tmp/urlfill_0908.txt', 'w', encoding='utf-8') as f:
    f.write('新着プールの総枠数=%d / url入り=%d / url空=%d\n' % (tot, filled, tot - filled))
    f.write('全枠urlが空のエントリ数=%d\n' % len(empty_entries))
    f.write('%s\n' % empty_entries)
    # 全EVENTSでの比率も
    tot2 = filled2 = 0
    for e in events:
        for t in e.get('tickets', []):
            tot2 += 1
            if t.get('url'): filled2 += 1
    f.write('サイト全体: 総枠=%d / url入り=%d / url空=%d\n' % (tot2, filled2, tot2 - filled2))
print('ok')
