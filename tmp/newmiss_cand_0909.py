# -*- coding: utf-8 -*-
"""新着プールで MISSING が出た3件を build_pia_entries の入力にする。"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

IDS = [7543, 7560, 7680]
h = io.open('index.html', encoding='utf-8', newline='').read()
by = {e['id']: e for e in json.loads(re.search(r'const EVENTS = (\[.*?\]);\r?\n', h, re.S).group(1))}

cands = []
for i in IDS:
    e = by[i]
    pia = (e.get('links') or {}).get('pia')
    print('id%-6d %s\n    %s' % (i, e.get('name', '')[:40], pia))
    cands.append({'newid': i, 'artist': e.get('artist', ''), 'urls': [pia]})
json.dump(cands, io.open('tmp/newmiss_cand_0909.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('→ tmp/newmiss_cand_0909.json')
