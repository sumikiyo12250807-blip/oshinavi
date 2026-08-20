# -*- coding: utf-8 -*-
"""収集候補の中身をジャンル別に一覧。特にsportsはNPBレギュラー戦除外ルールがあるので目視する。"""
import json, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
C = json.load(open('tmp/cand_0713.json', encoding='utf-8'))
by = collections.defaultdict(list)
for c in C:
    by[c.get('genre') or c.get('_lg') or '?'].append(c)
for g, rows in sorted(by.items(), key=lambda x: -len(x[1])):
    print(f'\n=== {g} {len(rows)}件 ===')
    for c in rows:
        print(f"  {c.get('artist','')[:52]} | {c.get('venue','')[:22]} | 公演{c.get('date','')} | {c.get('urls') or c.get('url','')}")
