# -*- coding: utf-8 -*-
"""8/3のキーワード監査で残った取りこぼしURLについて、
 ①そのeventCdが今の index.html に登録済みか ②同じアーティスト名の既存エントリがあるか
を機械で照合して出す（育成に回すか新規エントリにするかの判断材料）。"""
import io
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LEFT = [
    ('横山幸雄', 'b2669175', 'ジャパン・アーツ スペシャル・ガラ・コンサート 10/25 サントリーホール'),
    ('横山幸雄', 'b2667789', '千住真理子(vl)／横山幸雄(p) 11/22 J:COMホール八王子'),
    ('横山幸雄', 'b2667996', '横山幸雄 ベートーヴェン・プラス Vol.12 9/6 東京オペラシティ'),
    ('横山幸雄', '2619583', '横山幸雄(p) 9/26 アイザック小杉文化ホール'),
    ('横山幸雄', '2607741', '横山幸雄 華麗なる4大ピアノ協奏曲の響宴 9/13 アクロス福岡'),
    ('横山幸雄', '2613845', '横山幸雄 ドラマティック・コンチェルト! 10/31 ザ・シンフォニーホール'),
    ('メジューエワ', 'b2666178', 'ベートーヴェン全曲＋ディアベリ 9/13 浜離宮朝日ホール'),
    ('メジューエワ', '2617259', 'イリーナ・メジューエワ(p) 10/23 京都コンサートホール'),
    ('メジューエワ', '2612630', 'イリーナメジューエワピアノリサイタル 10/11 ホクト文化ホール'),
    ('新浜レオン', '2629321', '新浜レオン 8/16 六本木ヒルズアリーナ'),
    ('宮本笑里', 'b2669751', '猪居亜美＆宮本笑里 CLASSIC×ROCK 8/8 浜離宮朝日ホール'),
    ('中田カウス', '2614357', '漫才のDENDO in米沢 8/22'),
    ('中田カウス', '2613761', '漫才のDENDO in富田林 8/23'),
    ('爆生', '2614973', '爆生!!お笑い in 大宮 8/30'),
    ('立川寸志', 'b2669879', '新宿末廣亭8月余一会 8/31'),
    ('立川寸志', '2614626', '立川寸志 十八番を仕込む会 No.13-15 8/8'),
    ('大須演芸場', '2613490', '第60回あきつ落語会 春風亭一花独演会 その6 8/22'),
    ('ラフィンノーズ', 'b2669353', 'SHINJUKU LOFT 50th ROCK OF AGES 10/6'),
]

h = io.open(os.path.join(ROOT, 'index.html'), encoding='utf-8', newline='').read()
EVENTS = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))

cd_owner = {}
for e in EVENTS:
    blob = json.dumps(e, ensure_ascii=False)
    for cd in set(re.findall(r'event(?:Bundle)?Cd=([0-9a-zA-Z]+)', blob)):
        cd_owner.setdefault(cd, []).append(e['id'])

out = []
for kw, cd, title in LEFT:
    owner = cd_owner.get(cd)
    hits = [(e['id'], e.get('artist'), e.get('date'), e.get('genre'))
            for e in EVENTS if kw in (e.get('artist') or '') or kw in (e.get('name') or '')]
    out.append('%-8s | cd=%-9s | %s' % (kw, cd, title))
    out.append('    登録済み? %s' % ('YES id=%s' % owner if owner else 'いいえ（未登録）'))
    if hits:
        for i, a, d, g in hits[:6]:
            out.append('    既存エントリ id=%d [%s] %s (%s)' % (i, g, a, d))
    else:
        out.append('    既存エントリ なし')
io.open(os.path.join(ROOT, 'tmp', 'left_audit_0804.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('wrote tmp/left_audit_0804.txt  items=%d' % len(LEFT))
