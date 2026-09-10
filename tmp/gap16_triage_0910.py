# -*- coding: utf-8 -*-
"""「載っているが、その週に発売が始まる枠が無い」16件を、叩く前にローカルで精査する。

部分一致の誤爆（「潤」など）を落として、本当に取りに行くべきものだけ残す。
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
TODAY = '2026-09-10'

CAND = [
    ('9/14週', '清水ミチコ', [1308]),
    ('9/14週', '松平健 マツケンサンバコンサート2026', [2213]),
    ('9/14週', '昭和歌野郎ライブ2026', [2017]),
    ('9/14週', '森山直太朗', [4960]),
    ('9/14週', 'NEE', [4329, 4390, 4413]),
    ('9/14週', 'GENERATIONS from EXILE TRIBE', [3568]),
    ('9/14週', '森高千里', [2990]),
    ('9/14週', 'フォレスタ', [1640, 7384]),
    ('9/21週', '一青窈', [5717]),
    ('9/21週', 'esq', [4173]),
    ('9/21週', 'ウルフルズ', [4951, 5043]),
    ('9/21週', '宇都宮隆', [3471]),
    ('9/21週', '潤', [615, 2291, 4119, 5160]),
    ('9/21週', 'ロージークロニクル', [3742]),
    ('9/21週', "モーニング娘。'26", [3422]),
    ('9/21週', 'アンジュルム', [4490, 7708]),
]

h = io.open('index.html', encoding='utf-8').read()
ev = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))}


def alive(t):
    """いま画面に出ている枠か"""
    if t.get('saleUntilSoldOut') or t.get('soldout'):
        return True
    sd, d = t.get('startDate'), t.get('date')
    return not ((not sd or sd <= TODAY) and (d or '9999') < TODAY)


real, noise = [], []
for wk, nm, ids in CAND:
    for i in ids:
        e = ev.get(i)
        if not e:
            continue
        # 名前が本当にその組か（誤爆よけ）＝アーティスト名にきちんと入っているか
        exact = nm in (e.get('artist') or '') or nm in (e.get('name') or '')
        ts = e.get('tickets') or []
        live = [t for t in ts if alive(t)]
        kinds = set()
        for t in ts:
            ty = t.get('type') or ''
            kinds.add('一般' if '一般' in ty else ('先行' if any(
                w in ty for w in ('先行', 'プレリザーブ', 'プリセール', 'プレリク', '先着先行')) else 'その他'))
        row = (wk, nm, i, (e.get('name') or '')[:30], e.get('date'), len(ts), len(live),
               '/'.join(sorted(kinds)))
        (real if exact else noise).append(row)

print('■ 見に行く価値がありそう（名前がエントリと一致）%d件' % len(real))
print('  %-6s %-24s %-6s %-30s %-11s %s' % ('週', '名前', 'id', '公演名', '公演日', '全枠/生枠 種別'))
for wk, nm, i, name, date, n, nl, kinds in real:
    flag = '🚨' if nl == 0 else ('⚠️ ' if '一般' not in kinds else '  ')
    print('%s%-6s %-24s id%-5d %-30s %-11s %2d/%2d %s'
          % (flag, wk, nm[:24], i, name, date, n, nl, kinds))

print()
print('■ 部分一致の誤爆らしい（名前がエントリに無い）%d件' % len(noise))
for wk, nm, i, name, date, n, nl, kinds in noise:
    print('   %-6s %-14s id%-5d %-32s %s' % (wk, nm[:14], i, name, date))
