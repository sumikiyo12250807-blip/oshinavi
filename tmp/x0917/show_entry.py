# -*- coding: utf-8 -*-
"""エントリの枠を化けない形で書き出す（2026-09-16 夜・Bash越しの日本語は読まない決まりのため）。
使い方: python tmp/x0917/show_entry.py 4118 4960 > (出力は tmp/x0917/show_entry.txt にも書く)
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
ids = [int(x) for x in sys.argv[1:]]
src = io.open('index.html', encoding='utf-8').read()
ev = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))}

out = []
for i in ids:
    e = ev.get(i)
    if not e:
        out.append('id%-6d ない' % i)
        continue
    out.append('id%-6d %s ｜ %s ｜ 枠%d' % (i, e.get('artist'), e.get('genre'), len(e.get('tickets') or [])))
    for t in (e.get('tickets') or []):
        mark = ' [売切]' if t.get('soldout') else (' [販売終了]' if t.get('saleEnded') else '')
        out.append('        %s%s ｜ %s' % (t.get('type'), mark, (t.get('url') or '')[-30:]))
io.open('tmp/x0917/show_entry.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('wrote tmp/x0917/show_entry.txt (%d lines)' % len(out))
