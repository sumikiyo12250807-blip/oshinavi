# -*- coding: utf-8 -*-
"""組み直し結果から、既存と表記がゆれているだけの枠を外す（id5044 打首獄門同好会の「2027/1/16（土）公演」＝既存「2027／1／16（土）公演」）。"""
import io, json, sys
sys.stdout.reconfigure(encoding='utf-8')
P = 'tmp/built_missA_0911.json'
d = json.load(io.open(P, encoding='utf-8-sig'))
for b in d:
    if b['id'] == 5044:
        before = len(b['tickets'])
        b['tickets'] = [t for t in b['tickets'] if not t['type'].startswith('2027/1/16（土）公演')]
        print('5044: %d → %d枠' % (before, len(b['tickets'])))
json.dump(d, io.open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
