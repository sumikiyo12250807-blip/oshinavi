# -*- coding: utf-8 -*-
"""新着プール50件の _genre 下書き一覧（振り分け前の目視用）"""
import sys, io, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

src = open('index.html', encoding='utf-8').read()
m = re.search(r'const EVENTS = (\[.*?\n\s*\]);', src, re.S)
events = json.loads(m.group(1))
new = sorted([e for e in events if e.get('genre') == 'new'], key=lambda e: e['id'])

for e in new:
    g = e.get('_genre') or '（空）'
    ex = e.get('_extraGenres') or []
    sub = e.get('_piaSub') or e.get('_srcgenre') or ''
    exs = ('+' + ','.join(ex)) if ex else ''
    print(f"{e['id']} | {g}{exs:12} | {sub:22} | {e['name'][:52]}")
