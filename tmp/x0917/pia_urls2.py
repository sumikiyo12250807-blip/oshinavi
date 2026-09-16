# -*- coding: utf-8 -*-
"""MISSING/STALE が出たエントリのぴあの飛び先を全部出す（2026-09-16 夜）。
pia_statustext.py は「URL」を受け取る道具＝OSHINAVI の id を渡しても意味が無い（502に見えるだけ）。
使い方: python tmp/x0917/pia_urls2.py 3117 4118 4960 3879
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
ids = [int(x) for x in sys.argv[1:]] or [3117, 4118, 4960, 3879]
src = io.open('index.html', encoding='utf-8').read()
ev = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))}

urls = []
for i in ids:
    e = ev[i]
    card = (e.get('links') or {}).get('pia')
    print('id%-6d %s' % (i, card or '(card url なし)'))
    if card:
        urls.append(card)
    for t in (e.get('tickets') or []):
        u = t.get('url')
        if u and u not in urls:
            urls.append(u)
            print('        %s ｜ %s' % (t.get('type')[:46], u))
io.open('tmp/x0917/urls2.txt', 'w', encoding='utf-8').write('\n'.join(urls) + '\n')
print('\nurls=%d -> tmp/x0917/urls2.txt' % len(urls))
