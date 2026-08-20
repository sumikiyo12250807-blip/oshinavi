# -*- coding: utf-8 -*-
"""削除ゲート用の候補一覧を index.html から機械抽出する（URL捏造禁止＝登録値のみ）。"""
import re, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

h = open('index.html', encoding='utf-8', newline='').read()
EVENTS = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
byid = {e['id']: e for e in EVENTS}

GROUPS = [
    ('A. 公演が終わった（8/13まで）', [902, 1031, 1183, 1773, 2526, 2691]),
    ('B. ぴあ0枠・予定枚数終了の表示なし', [459, 557, 914, 977, 980, 1256, 1342, 1586, 1750, 1775,
                                     1807, 2139, 2374, 2687, 2753, 3150, 3452, 3476, 3505, 3653,
                                     3693, 3725, 4078, 4091, 4096, 4097, 4129, 4141]),
    ('C. 抽選結果発表前＝削除禁止（保留）', [1554, 2206, 2748, 3473, 3691, 4030, 4079, 4083, 4089,
                                     4127, 4130, 4134, 4155, 4173, 4175]),
    ('D. ぴあURL無し＝機械照合できない（別ルート確認要）', [85, 1037, 1619, 3022, 3032, 3082, 3088, 3236]),
]

for title, ids in GROUPS:
    print('\n## %s （%d件）' % (title, len(ids)))
    for i in ids:
        e = byid.get(i)
        if not e:
            print('- id=%d **見つからない**' % i); continue
        links = e.get('links') or {}
        pia = links.get('pia') or ''
        others = [k for k, v in links.items() if k != 'pia' and v]
        if not pia:
            for t in (e.get('tickets') or []):
                u = t.get('url') or ''
                if u:
                    pia = u; break
        name = (e.get('name') or e.get('artist') or '')[:44]
        print('- %d %s / %s @%s (%s)%s' % (
            i, e.get('artist', '')[:22], name, e.get('prefecture', ''), e.get('date', ''),
            ' ※他社リンク:' + ','.join(others) if others else ''))
        print('  %s' % (pia or '（URL無し）'))
