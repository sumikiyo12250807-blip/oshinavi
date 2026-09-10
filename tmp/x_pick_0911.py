# -*- coding: utf-8 -*-
"""明日(2026-09-11)発売の枠を機械抽出して、ジャンル別に並べる（夜のX投稿の候補出し）。

台本＝X_SCRIPT.md
 ・主役枠3本＝翌日発売のうち Xフォロワーが多い上位3組
 ・まとめ枠＝残り全部をジャンル別（1投稿＝1ジャンル・そのジャンルは1件も削らない）
 ・2〜3日後は5件くらい（**箱の大きさで選ぶ**）＋「他にも◯件以上」（10の位で切り下げ）
"""
import collections
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

TOMORROW = '2026-09-11'
D2 = '2026-09-12'
D3 = '2026-09-13'

h = io.open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))


def rows_for(day):
    out = []
    for e in EVENTS:
        if e.get('genre') == 'new':
            continue          # 新着プールは振り分け前なので出さない
        for t in e.get('tickets') or []:
            if t.get('startDate') == day and not t.get('soldout'):
                out.append((e, t))
    return out


def timeof(t):
    m = re.search(r'(\d{1,2}):(\d{2})', t.get('type') or '')
    return '%02d:%02d' % (int(m.group(1)), int(m.group(2))) if m else '--:--'


def senko(t):
    ty = t.get('type') or ''
    return any(w in ty for w in ('先行', 'プレリザーブ', 'プリセール', 'プレリク', 'プレオーダー',
                                 '先着先行', '抽選'))


for day, label in ((TOMORROW, '明日'), (D2, '2日後'), (D3, '3日後')):
    rs = rows_for(day)
    byg = collections.defaultdict(list)
    for e, t in rs:
        byg[e.get('genre') or '-'].append((e, t))
    print('')
    print('=' * 74)
    print('=== %s %s 発売の枠 %d本 / %dジャンル ===' % (label, day, len(rs), len(byg)))
    for g in sorted(byg, key=lambda x: -len(byg[x])):
        print('')
        print('--- %s : %d本 ---' % (g, len(byg[g])))
        for e, t in sorted(byg[g], key=lambda x: timeof(x[1])):
            print('  %s %-30s／%-8s %s id=%d' % (
                timeof(t), (e.get('artist') or '')[:30], (e.get('prefecture') or '')[:8],
                '（先行）' if senko(t) else '', e['id']))
            print('        %-52s @%s' % ((t.get('type') or '')[:52], (e.get('venue') or '')[:34]))
