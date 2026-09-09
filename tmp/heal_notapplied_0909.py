# -*- coding: utf-8 -*-
"""convert のうち index.html に反映されなかったもの（＝安全弁でブロック）を洗い出す。"""
import io, re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

rows = json.load(io.open('tmp/heal_stale.json', encoding='utf-8'))
h = io.open('index.html', encoding='utf-8', newline='').read()
cur = {e['id']: e for e in json.loads(re.search(r'const EVENTS = (\[.*?\]);\r?\n', h, re.S).group(1))}

r0 = [r for r in rows if r.get('status') == 'convert'][0]
print('convert 行のキー:', list(r0.keys()))

def sig(tks):
    # 適用時に startDate は元の発売日が引き継がれる（carry_start_dates）ので比較から外す
    return sorted((t.get('type', ''), t.get('date'), t.get('url', '')) for t in tks or [])

applied, blocked = [], []
for r in rows:
    if r.get('status') != 'convert':
        continue
    eid = r.get('id')
    newt = r.get('tickets') or r.get('new_tickets') or r.get('built', {}).get('tickets')
    e = cur.get(eid)
    if e is None or newt is None:
        blocked.append((eid, r.get('name', ''), 'データ無し'))
        continue
    (applied if sig(newt) == sig(e.get('tickets')) else blocked).append((eid, r.get('name', ''), ''))

print(f'\nconvert {len(applied)+len(blocked)}件 → 反映済み {len(applied)} / 未反映 {len(blocked)}')
print('\n=== 未反映（安全弁でブロック）===')
for eid, name, note in blocked:
    print('  id=%-6s %s %s' % (eid, (name or '')[:44], note))
