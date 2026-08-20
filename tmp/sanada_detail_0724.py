# -*- coding: utf-8 -*-
"""真田ナオキの各e+ detail頁を機械パースし、公演日/会場/県/時刻/販売窓を確定する。"""
import re, sys, json, datetime
sys.path.insert(0, 'tools')
from eplus_harvest import fetch, parse_ld
from reconcile_eplus import parse_blocks
sys.stdout.reconfigure(encoding='utf-8')

urls = json.load(open('tmp/sanada_urls.json', encoding='utf-8'))

for u in urls:
    try:
        h = fetch(u)
    except Exception as ex:
        print(f'❌ {u} fetch失敗 {ex}'); continue
    lds = parse_ld(h) or []
    blocks = parse_blocks(h)
    # このdetail URLの当該公演＝URL末尾-P.. に対応するLD。まず全LDを出す。
    print(f'\n■ {u}')
    for e in lds:
        print(f'   公演: {e["name"]} | {e["date"]} {e.get("time","")} | {e["venue"]} | {e["pref"]}')
    for b in blocks:
        alive = b['status'] in ('open', 'before')
        print(f'   {"◎" if alive else "×"} [{b["status"]}] 受付 {b["sd"]} {b["st"]} 〜 {b["ed"]} {b["et"]}')
