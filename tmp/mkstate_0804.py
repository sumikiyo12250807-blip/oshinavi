# -*- coding: utf-8 -*-
"""朝の変換用: reconcileでMISSINGが出たエントリを grow_from_audit で作り直すための state を作る。
既存の登録URLをそのまま new_urls として渡す（ぴあ側に枠が増えている型）。"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDS = [int(x) for x in sys.argv[1].split(',')]

h = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[.*?\]);\s*\n', h, re.S)
EVENTS = json.loads(m.group(1))
byid = {e['id']: e for e in EVENTS}

cnt = {}
for e in EVENTS:
    a = (e.get('artist') or '').strip()
    cnt[a] = cnt.get(a, 0) + 1

results = {}
report = []
for i in IDS:
    e = byid[i]
    a = (e.get('artist') or '').strip()
    urls = []
    for u in [(e.get('links') or {}).get('pia')] + [t.get('url') for t in (e.get('tickets') or [])]:
        if u and 't.pia.jp' in u and u not in urls:
            urls.append(u)
    report.append('id=%d artist_count=%d urls=%d' % (i, cnt.get(a, 0), len(urls)))
    if cnt.get(a, 0) != 1:
        report.append('  SKIP: artist name not unique')
        continue
    results[a] = {'missing': [{'url': u, 'own_name': True, 'rlsdate': ''} for u in urls]}

out = os.path.join(ROOT, 'tmp', 'state_0804.json')
json.dump({'results': results}, open(out, 'w', encoding='utf-8'), ensure_ascii=False)
print('\n'.join(report))
print('wrote %s  groups=%d' % (out, len(results)))
