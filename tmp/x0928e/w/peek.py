# -*- coding: utf-8 -*-
"""候補の名前一致先の既存エントリを見る（読むだけ）"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
src = io.open('index.html', encoding='utf-8', newline='').read()
ev = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))}
extra = {25264: [], 25272: []}
for c in json.load(open('tmp/x0928e/w/cands.json', encoding='utf-8')):
    ids = c['name_exact_ids']
    if not ids:
        continue
    print('== %d %s %s' % (c['newid'], c['artist'], c['urls'][0]))
    for i in ids:
        e = ev[i]
        print('   id%d [%s] %s / %s | %s | %s | %s | pia=%s' % (i, e.get('genre'), e.get('artist'), (e.get('name') or '')[:50], e.get('venue'), e.get('dateLabel'), e.get('date'), (e.get('links') or {}).get('pia')))
        for t in (e.get('tickets') or [])[:6]:
            print('        %s | %s' % ((t.get('type') or '')[:70], t.get('date')))
