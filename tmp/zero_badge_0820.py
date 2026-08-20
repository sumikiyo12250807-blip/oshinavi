# -*- coding: utf-8 -*-
"""🚨「カードは出るのにバッジが1枚も無い」エントリを洗い出す。

ユーザー発見（2026-08-20）＝BALLISTIK BOYZ × TOWER RECORDS CAFE(3570) が
販売期間6つとも終了していて、画面に出る枠が0だった。
＝**情報だけあって買えない**状態。OSHINAVI の方針（買えるものだけ載せる）に反する。

index.html renderCard の非表示ルールをそのまま当てる:
    (!startDate || startDate <= today) && date < today   → その枠は描かれない
soldout / saleEnded が付いた枠は別扱いなので、それも数える。
"""
import re, io, json, sys, datetime, collections
sys.stdout.reconfigure(encoding='utf-8')

TODAY = datetime.date.today().isoformat()
h = io.open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))

zero, marked = [], []
for e in EVENTS:
    if e.get('verified') is not True:
        continue
    ts = e.get('tickets') or []
    vis = 0
    has_mark = False
    for t in ts:
        sd, d = t.get('startDate'), t.get('date') or ''
        hidden = (not sd or sd <= TODAY) and d < TODAY
        if t.get('soldout') or t.get('saleEnded'):
            has_mark = True
        if not hidden:
            vis += 1
    if vis == 0:
        row = (e['id'], e.get('artist'), e.get('genre'), e.get('date'), len(ts),
               (e.get('links') or {}).get('pia') or (e.get('links') or {}).get('eplus') or '')
        (marked if has_mark else zero).append(row)

out = []
P = out.append
P('=== 画面に出る枠が0のエントリ（today=%s）===' % TODAY)
P('')
P('【🚨 印も無い＝ただ買えないだけ %d件】' % len(zero))
for i, a, g, d, n, u in sorted(zero, key=lambda r: r[3]):
    P('  id%-5s [%-9s] %-38s 公演日%s 枠%d' % (i, g, (a or '')[:38], d, n))
    P('        %s' % u)
P('')
P('【予定枚数終了/販売終了の印あり＝方針どおり残すもの %d件】' % len(marked))
for i, a, g, d, n, u in sorted(marked, key=lambda r: r[3])[:20]:
    P('  id%-5s [%-9s] %-38s 公演日%s 枠%d' % (i, g, (a or '')[:38], d, n))

io.open('tmp/zero_badge_0820.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('印なしで枠0:', len(zero), '件 / 印ありで枠0:', len(marked), '件')
