# -*- coding: utf-8 -*-
"""明日の当日発売の「発売時刻」を機械で一覧にする（2026-09-16 夜に翌朝のぶんを先に作る）。

なぜ前の晩に作るか＝朝の便で1日の予定を立てたら**同じターンで時刻を全部アラームに入れる**決まりで、
その材料（最も遅い当日発売＝昼の便をいつ回すか／午後〜夜の発売が何時か）が朝いちばんに要る。
時計は叩かない限り存在しない（feedback_noon_heal_missed_twice）。

判定＝tickets の type にある「M/D HH:MM発売」の M/D が明日のもの。
使い方: python tmp/x0917/tomorrow_times.py [YYYY-MM-DD]
出力: tmp/x0917/tomorrow_times.txt
"""
import collections
import datetime
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

if len(sys.argv) > 1:
    d = datetime.date(*[int(x) for x in sys.argv[1].split('-')])
else:
    d = datetime.date.today() + datetime.timedelta(days=1)
md = '%d/%d' % (d.month, d.day)
pat = re.compile(re.escape(md) + r' (\d{1,2}):(\d{2})発売')

src = io.open('index.html', encoding='utf-8').read()
events = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))

bytime = collections.defaultdict(list)
for e in events:
    for t in (e.get('tickets') or []):
        m = pat.search(t.get('type') or '')
        if not m:
            continue
        key = '%02d:%02d' % (int(m.group(1)), int(m.group(2)))
        bytime[key].append((e['id'], (e.get('artist') or e.get('name') or '')[:34]))

out = ['=== %s（%s）発売の枠 ===' % (d.isoformat(), '月火水木金土日'[d.weekday()])]
total = 0
for k in sorted(bytime):
    rows = bytime[k]
    total += len(rows)
    out.append('%s  %d枠' % (k, len(rows)))
    for i, name in rows[:6]:
        out.append('        id%-6d %s' % (i, name))
    if len(rows) > 6:
        out.append('        … 他 %d枠' % (len(rows) - 6))
out.append('')
out.append('合計 %d枠 / 時刻 %d種類' % (total, len(bytime)))
if bytime:
    last = sorted(bytime)[-1]
    out.append('いちばん遅い当日発売＝%s ＝昼の便はこの時刻より後に回す（15時を過ぎるなら別便で拾う）' % last)
io.open('tmp/x0917/tomorrow_times.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('wrote tmp/x0917/tomorrow_times.txt (%d lines / %d枠)' % (len(out), total))
