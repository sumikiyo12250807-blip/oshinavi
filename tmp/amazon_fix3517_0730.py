# -*- coding: utf-8 -*-
"""id3517 Sky Jamboree(fes) を rewrite → drop に直す。
fesは個別「最新CD」を付けずジャンル共通の「フェスアイテム」ボタンに任せるのが正
（[[reference_amazon_affiliate]]）。同日 amazon_audit 本体にも fes→drop のガードを入れた。"""
import io, json

P = 'tmp/amazon_audit.json'
res = json.load(io.open(P, encoding='utf-8'))
for r in res:
    if r['id'] == 3517:
        r['action'] = 'drop'
        r['newkw'] = None
        r['why'] = 'fes wa kobetsu CD nashi (genre kyoutsuu button)'
        print('id3517 -> drop')
json.dump(res, io.open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('actions:', [(r['id'], r['action'], r.get('newkw')) for r in res])
