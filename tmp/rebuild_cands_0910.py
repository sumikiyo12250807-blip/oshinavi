# -*- coding: utf-8 -*-
"""指定idの候補ファイルを作る（build_pia_entries に食わせる形）。

🚨1件につき1URLだけ渡す＝複数URLを渡すと2本目以降に ticket.url が付かない
  （[[feedback_build_pia_multiurl_loses_ticket_url]]）。
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
IDS = [int(x) for x in sys.argv[1].split(',')]
OUT = sys.argv[2]

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
by = {e['id']: e for e in json.loads(m.group(2))}

cands = []
for i in IDS:
    e = by[i]
    urls = []
    pu = (e.get('links') or {}).get('pia')
    if pu:
        urls.append(pu)
    for t in e.get('tickets') or []:
        u = t.get('url') or ''
        if 'pia.jp' in u and u not in urls:
            urls.append(u)
    cands.append({'newid': i, 'artist': e.get('artist') or e.get('name'), 'urls': urls})
    print('id=%s urls=%d' % (i, len(urls)))

json.dump(cands, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('→ %s' % OUT)
