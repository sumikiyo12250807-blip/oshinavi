# -*- coding: utf-8 -*-
"""監査結果の id3496 を drop → rewrite「白鳥の湖」に直す（実測20件・tmp/amazon_probe_ballet_0730.py）。
audit本体がハイフンで副題を切っていなかったのが原因＝同日 shorten() に恒久修正済み。"""
import io, json

P = 'tmp/amazon_audit.json'
res = json.load(io.open(P, encoding='utf-8'))
for r in res:
    if r['id'] == 3496:
        r['action'] = 'rewrite'
        r['newkw'] = '白鳥の湖'
        r['cd'] = False
        r['hit'] = 20
        r.setdefault('tried', []).append(['白鳥の湖', False, 20])
        print('id3496 -> rewrite kw=shirotori(hit20, CD-less)')
json.dump(res, io.open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('actions:', [(r['id'], r['action'], r.get('newkw')) for r in res])
