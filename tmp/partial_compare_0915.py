# -*- coding: utf-8 -*-
"""部分一致の要確認（split_built_0915 の👀部分）を、組み上がりの枠と既存エントリの枠で並べて見比べる（読むだけ・2026-09-15）。
使い方: python tmp/partial_compare_0915.py
出力: tmp/partial_compare_0915.txt
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
built = {b['id']: b for b in json.load(io.open('tmp/built_uk01_0915.json', encoding='utf-8'))}
cands = {c['newid']: c for c in json.load(io.open('tmp/cands_uk01_0915.json', encoding='utf-8'))}
src = io.open('index.html', encoding='utf-8').read()
ev = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))}
out = []
for l in io.open('tmp/split_built_0915.txt', encoding='utf-8').read().splitlines():
    if not l.startswith('👀部分'):
        continue
    nid = int(re.search(r'new(\d+)', l).group(1))
    ids = [int(x) for x in re.findall(r'\d+', l.split('～')[1].split(']')[0])]
    b = built[nid]
    out.append('=' * 70)
    out.append('new%s %s ｜ %s ｜ %s' % (nid, b.get('artist'), b.get('dateLabel'), (cands.get(nid) or {}).get('urls')))
    for t in b.get('tickets') or []:
        out.append('   新: %s ｜ %s' % (t.get('type'), t.get('url') or ''))
    for i in ids:
        e = ev[i]
        out.append(' 既存 id%s %s ｜ %s ｜ genre=%s ｜ pia=%s' % (i, e.get('name'), e.get('dateLabel'), e.get('genre'), (e.get('links') or {}).get('pia')))
        for t in e.get('tickets') or []:
            out.append('   既: %s ｜ %s%s' % (t.get('type'), t.get('url') or '', ' ［売切］' if t.get('soldout') else ''))
io.open('tmp/partial_compare_0915.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('%d件 → tmp/partial_compare_0915.txt' % sum(1 for x in out if x.startswith('new')))
