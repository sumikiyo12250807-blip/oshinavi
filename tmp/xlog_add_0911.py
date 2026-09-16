# -*- coding: utf-8 -*-
"""9/11 にブラウザで測ったXフォロワー実数を tools/x_log.json の artists.data に足す（同名は上書きしない）。"""
import io, json
P = 'tools/x_log.json'
d = json.load(io.open(P, encoding='utf-8'))
ADD = [
    ('水瀬いのり', '@inoriminase', 863000, '水瀬いのりinfo（本人とスタッフの公式）'),
    ('UVERworld', '@UVERworld_dR2', 527500, 'UVERworld_Staff_（スタッフ公式）'),
    ('羽多野渉', '@hatano_official', 314700, '羽多野渉 公式'),
    ('モーニング娘。', '@MorningMusumeMg', 237300, 'モーニング娘。\'26 公式'),
    ('Juice=Juice', '@JuiceJuice_uf', 185600, ''),
    ('アンジュルム', '@angerme_upfront', 157800, ''),
    ('東京スカパラダイスオーケストラ', '@tokyoskaj', 116500, 'TOKYO SKA PARADISE ORCHESTRA'),
    ('ねぐせ。', '@neguseofficial_', 113100, ''),
    ('ヤングスキニー', '@yang_skinny', 106400, ''),
    ('川崎鷹也', '@kawasaki_takaya', 86500, ''),
    ('Girls2', '@Girls2_official', 49100, 'Girls²'),
    ('レミオロメン', '@remioromen_oa', 21000, 'レミオロメン オフィシャルアカウント'),
]
have = {a.get('name') for a in d['artists']['data']}
n = 0
for name, h, f, note in ADD:
    if name in have:
        continue
    d['artists']['data'].append({'name': name, 'handle': h, 'followers': f,
                                 'note': ('2026-09-11 ブラウザ実測。' + note).strip()})
    n += 1
d['artists']['measured'] = '2026-09-11'
json.dump(d, io.open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('足した %d組' % n)
