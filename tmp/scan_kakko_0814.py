# -*- coding: utf-8 -*-
"""〈〉化けバッジ（一般発売〈11【13（金）公演〉】型）がDB全体に何件あるか。"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
h = open('index.html', encoding='utf-8', newline='').read()
EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
hits = []
for e in EV:
    for t in e.get('tickets') or []:
        ty = t.get('type') or ''
        if '〈' in ty or '〉' in ty:
            hits.append((e['id'], e.get('genre'), e.get('name'), ty))
print('〈〉を含むバッジ', len(hits), '件 /', len({r[0] for r in hits}), 'エントリ')
for r in hits:
    print('  id%-5s [%s] %s' % (r[0], r[1], r[3]))
    print('        ', (r[2] or '')[:50])
