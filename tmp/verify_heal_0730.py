# -*- coding: utf-8 -*-
"""ヒール後の4件が「本日発売 〜M/D」の形（startDate=今日＋締切が入っている）になったか確認。"""
import json
import re

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
byid = {e['id']: e for e in EVENTS}
out = []
for i in (2800, 2870, 2918, 3419):
    e = byid[i]
    out.append(f"id={i} {(e.get('artist') or '')[:44]}")
    for t in e.get('tickets') or []:
        if (t.get('startDate') or '') == '2026-07-30':
            out.append(f"    {t.get('type')}")
            out.append(f"        date={t.get('date')} startDate={t.get('startDate')}  → 発売日と締切が別＝OK"
                       if t.get('date') != t.get('startDate') else
                       f"        date={t.get('date')} startDate={t.get('startDate')}  → 🚨まだ単日形")
open('tmp/verify_heal_0730.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote tmp/verify_heal_0730.txt')
