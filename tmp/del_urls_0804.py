# -*- coding: utf-8 -*-
"""削除候補の確認用URLを index.html から機械抽出（捏造禁止）。"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDS = [491, 976, 1689, 1970, 2656, 2695, 1404, 1774, 2038, 2663, 2845, 3485]
h = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[.*?\]);\s*\n', h, re.S)
byid = {e['id']: e for e in json.loads(m.group(1))}
out = []
for i in IDS:
    e = byid[i]
    links = {k: v for k, v in (e.get('links') or {}).items() if v}
    turls = [t.get('url') for t in (e.get('tickets') or []) if t.get('url')]
    out.append('id=%d | %s | %s | %s' % (i, e.get('name'), e.get('venue'), e.get('date')))
    for k, v in links.items():
        out.append('    links.%s = %s' % (k, v))
    for u in turls:
        out.append('    ticket.url = %s' % u)
open(os.path.join(ROOT, 'tmp', 'del_urls_0804.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('wrote tmp/del_urls_0804.txt lines=%d' % len(out))
