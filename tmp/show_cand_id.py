# -*- coding: utf-8 -*-
"""候補JSONから指定newidの中身を出す。"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
ids = [int(x) for x in sys.argv[1:]]
C = json.load(open('tmp/cand_0713_keep.json', encoding='utf-8'))
for c in C:
    if c.get('newid') in ids:
        print(json.dumps(c, ensure_ascii=False, indent=2))
