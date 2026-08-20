# -*- coding: utf-8 -*-
"""真田ナオキのe+ base頁から全-P公演を列挙し、各公演の日付/会場/県/販売窓を確定。"""
import re, sys, json, datetime
sys.path.insert(0, 'tools')
from eplus_harvest import fetch, parse_ld
from reconcile_eplus import parse_blocks
sys.stdout.reconfigure(encoding='utf-8')

BASES = ['3489620001', '4534110001', '4549640001', '4549290001']
seen_urls = []
for base in BASES:
    h = fetch('https://eplus.jp/sf/detail/' + base)
    for m in re.finditer(base + r'-P\w+', h):
        u = 'https://eplus.jp/sf/detail/' + m.group(0)
        if u not in seen_urls:
            seen_urls.append(u)

print(f'全base から detail URL {len(seen_urls)}件')
rows = []
for u in seen_urls:
    try:
        h = fetch(u)
    except Exception as ex:
        print(f'❌ {u} {ex}'); continue
    lds = parse_ld(h) or []
    blocks = parse_blocks(h)
    alive = [b for b in blocks if b['status'] in ('open', 'before')]
    if not lds:
        continue
    e = lds[0]
    st = '／'.join(f'[{b["status"]}]{b["sd"]}{b["st"]}〜{b["ed"]}{b["et"]}' for b in alive) or '×売枠なし'
    print(f'  {e["date"]} {e.get("time",""):>5} | {e["pref"]:<4} | {e["venue"][:24]:<24} | {e["name"][:24]} | {st}')
    print(f'        {u}')
