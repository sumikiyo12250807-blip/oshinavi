# -*- coding: utf-8 -*-
"""Jリーグ5件のnewidを既存の最大id+1から振り直してbuild入力にする。"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
E = json.loads(m.group(2))
maxid = max(e['id'] for e in E)
J = json.load(open('tmp/cand_0713_jleague.json', encoding='utf-8'))
for n, c in enumerate(J, 1):
    c['newid'] = maxid + n
    print(f"  id{c['newid']} {c['artist']}")
json.dump(J, open('tmp/cand_jleague_ready.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'=== 既存最大id={maxid} → {len(J)}件を id{maxid+1}..{maxid+len(J)} で build ===')
