# -*- coding: utf-8 -*-
"""選定した新着候補を build_pia_entries.py の入力形式に変換する（2026-08-24 朝）。

pick_0824.json（ハーベスタの生形式）→ [{"newid":int,"artist":str,"urls":[url]}]
newid は index.html の最大id+1 から連番。
"""
import io
import json
import re

pick = json.load(io.open('tmp/pick_0824.json', encoding='utf-8'))
h = io.open('index.html', encoding='utf-8', newline='').read()
EVENTS = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
nid = max(e['id'] for e in EVENTS) + 1

cand = []
for it in pick:
    cand.append({'newid': nid, 'artist': it['artist'], 'urls': [it['url']]})
    nid += 1

json.dump(cand, io.open('tmp/cand_0824.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('候補 %d件 / id %d〜%d' % (len(cand), cand[0]['newid'], cand[-1]['newid']))
