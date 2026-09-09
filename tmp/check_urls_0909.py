# -*- coding: utf-8 -*-
"""救済した25エントリで、ticket.url が抜けている枠が無いか点検する。
🚨build_pia_entries に複数URLを渡すと2本目以降に url が付かない（過去の実害）。"""
import io, re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

ids = [b['id'] for b in json.load(io.open('tmp/zero_built_0909.json', encoding='utf-8'))]
h = io.open('index.html', encoding='utf-8', newline='').read()
by = {e['id']: e for e in json.loads(re.search(r'const EVENTS = (\[.*?\]);\r?\n', h, re.S).group(1))}

bad = 0
for i in ids:
    for t in by[i].get('tickets', []):
        if not (t.get('url') or '').strip():
            bad += 1
            print('  🚨url無し id%-6d %s' % (i, (t.get('type') or '')[:60]))
print('url が抜けている枠 %d（対象 %d エントリ）' % (bad, len(ids)))
