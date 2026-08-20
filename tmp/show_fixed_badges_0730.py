# -*- coding: utf-8 -*-
"""席種ラベルを戻した3件の現在のバッジを確認"""
import io, json, re

raw = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[.*?\]);', raw, re.S)
M = {e['id']: e for e in json.loads(m.group(1))}
out = []
for eid in (2805, 3347, 3348, 3457):
    ev = M[eid]
    out.append('=== id=%d %s' % (eid, ev.get('artist')))
    for t in ev.get('tickets', []):
        out.append('   %s  (date=%s)' % (t.get('type'), t.get('date')))
    out.append('')
io.open('tmp/out_fixed_badges.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote tmp/out_fixed_badges.txt')
