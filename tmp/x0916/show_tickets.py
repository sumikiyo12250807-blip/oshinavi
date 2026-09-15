# -*- coding: utf-8 -*-
"""指定したエントリの tickets を番号つきで1行ずつ並べる（読むだけ・2026-09-15夜）。
使い方: python tmp/x0916/show_tickets.py 4164,3853,4293,4489
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
IDS = [int(x) for x in sys.argv[1].split(',') if x.strip()]
src = open('index.html', encoding='utf-8', newline='').read()
ev = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))}
for i in IDS:
    e = ev[i]
    print('■ id%s %s（枠%d）' % (i, e.get('name'), len(e.get('tickets') or [])))
    for k, t in enumerate(e.get('tickets') or []):
        print('  [%02d] %s ｜date=%s start=%s ｜%s%s ｜%s' % (
            k, t.get('type'), t.get('date'), t.get('startDate') or '-',
            '売切' if t.get('soldout') else '', ('(' + t.get('soldoutSince', '') + ')') if t.get('soldout') else '',
            (t.get('url') or '').replace('https://', '')))
