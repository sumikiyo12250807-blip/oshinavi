# -*- coding: utf-8 -*-
"""残り隠れ枠7件の中身（type/date/startDate/URL）を見る。"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDS = [1806, 2457, 3210, 3211, 3399, 3434, 3438]
h = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[.*?\]);\s*\n', h, re.S)
byid = {e['id']: e for e in json.loads(m.group(1))}
out = []
for i in IDS:
    e = byid[i]
    out.append('id=%d %s | date=%s | pia=%s' % (i, e.get('name'), e.get('date'),
                                                (e.get('links') or {}).get('pia')))
    for t in e.get('tickets') or []:
        out.append('    %s | date=%s start=%s url=%s' % (t.get('type'), t.get('date'),
                                                         t.get('startDate'), t.get('url')))
open(os.path.join(ROOT, 'tmp', 'hidden_0804.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('wrote tmp/hidden_0804.txt lines=%d' % len(out))
