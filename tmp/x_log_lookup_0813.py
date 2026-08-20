# -*- coding: utf-8 -*-
"""x_log.json に既にフォロワー実数がある候補を引く（再検索を減らす）"""
import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')

d = json.load(io.open('tools/x_log.json', encoding='utf-8'))
a = d['artists']
print('artists keys:', list(a.keys()))
items = a.get('items') or a
if isinstance(items, list):
    for x in items:
        print(json.dumps(x, ensure_ascii=False))
else:
    for k, v in items.items():
        print(k, json.dumps(v, ensure_ascii=False))
