# -*- coding: utf-8 -*-
"""MISSINGが出た29エントリを build_pia_entries の入力にする（1エントリ1URL）。
🚨1候補に複数URLを渡すと2本目以降に ticket.url が付かない（feedback_build_pia_multiurl_loses_ticket_url）。"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

rows = json.load(io.open('tmp/missing_rows_0909.json', encoding='utf-8'))
h = io.open('index.html', encoding='utf-8', newline='').read()
by = {e['id']: e for e in json.loads(re.search(r'const EVENTS = (\[.*?\]);\r?\n', h, re.S).group(1))}

cands = []
for r in rows:
    e = by[r['id']]
    cands.append({'newid': r['id'], 'artist': e.get('artist', ''), 'urls': [r['pia']]})
json.dump(cands, io.open('tmp/zero_cand_0909.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('候補 %d件 → tmp/zero_cand_0909.json' % len(cands))
