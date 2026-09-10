# -*- coding: utf-8 -*-
"""名前タイル12組の行を、登録データから機械で作る（9/13の記事）。

形＝前号(tmp/pickup0906/tiles.txt)と同じ「名前 | id | 発売日(曜) 時刻 | 都道府県」。
🚨窓＝2026-09-14〜2026-09-20 に**発売が始まる**枠だけを見る。
🚨数字は記憶で書かない＝index.html の登録データを数える
   （[[feedback_article_factcheck_before_publish]]）。
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

FROM, TO = '2026-09-14', '2026-09-20'
WD = '月火水木金土日'

# 主役5組（厚く書く）／深掘り1組
LEAD = [7324, 4845, 4802, 3568, 4898]
DEEP = [4898]
# 名前タイル12組
TILES = [2159, 1, 729, 549, 1634, 5717, 4538, 4490, 4793, 5201, 5526, 523]

h = io.open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
by = {e['id']: e for e in EVENTS}


def win_slots(e):
    return [t for t in (e.get('tickets') or [])
            if t.get('startDate') and FROM <= t['startDate'] <= TO and not t.get('soldout')]


def jd(d):
    import datetime
    return '%d/%d(%s)' % (int(d[5:7]), int(d[8:10]),
                          WD[datetime.date.fromisoformat(d).weekday()])


def times(slots):
    """券種名の末尾に出る「M/D HH:MM発売」から時刻だけ拾う（バッジに必ず時刻を入れる決まり）。"""
    ts = set()
    for t in slots:
        m = re.search(r'(\d{1,2}:\d{2})\s*発売', t.get('type') or '')
        if m:
            ts.add(m.group(1))
    return ','.join(sorted(ts))


out = io.open('tmp/pickup_tiles_0914.txt', 'w', encoding='utf-8')
w = out.write

w('# 9/13(日)の記事の素材（窓 %s〜%s に発売が始まる枠だけ）\n\n' % (FROM, TO))

w('## 名前タイル12組（文章は書かない・この行がそのまま出る）\n\n')
for i in TILES:
    e = by[i]
    s = win_slots(e)
    days = '/'.join(jd(d) for d in sorted({t['startDate'] for t in s}))
    w('%-22s | id%-5d | %s %s | %s\n'
      % ((e.get('artist') or e.get('name'))[:22], i, days, times(s),
         e.get('prefecture') or ''))
    for t in s:
        w('        ・%s\n' % t.get('type'))

w('\n\n## 主役5組＋深掘り（窓内で発売が始まる枠を全部）\n\n')
for i in LEAD:
    e = by[i]
    s = win_slots(e)
    w('### id=%d %s%s\n' % (i, e.get('artist') or e.get('name'),
                            '  ★深掘り' if i in DEEP else ''))
    w('   会期 : %s\n' % e.get('dateLabel'))
    w('   会場 : %s\n' % e.get('venue'))
    w('   窓内で発売が始まる枠 %d件 / このエントリの全枠 %d件\n'
      % (len(s), len(e.get('tickets') or [])))
    for t in s:
        w('     ・%s\n' % t.get('type'))
    w('\n')

out.close()
print('→ tmp/pickup_tiles_0914.txt')
