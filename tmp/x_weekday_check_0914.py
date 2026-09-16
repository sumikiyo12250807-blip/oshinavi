# -*- coding: utf-8 -*-
"""「木曜が強い」は1本の跳ねた投稿（8/27 マツケン・76クリック）のせいではないかを、CSVから直接数え直す（読むだけ）。
決まり（project_x_improvement_loop）＝判定は投稿の2日後／母数15本未満は判定しない／全体と「外れ値1本を外した後」が
同じ向きの時だけ結論にする。x_analyze.py の「外れ値1本を外した」は中央インプだけなので、クリックは自分で外して並べる。
日付と時刻は Post id（Snowflake）から復元する（CSVの Date はUTC）。
使い方: python tmp/x_weekday_check_0914.py <csv>
出力: tmp/x_weekday_check_0914.txt
"""
import csv
import datetime
import io
import sys

sys.stdout.reconfigure(encoding='utf-8')
SRC = sys.argv[1] if len(sys.argv) > 1 else 'tmp/x_content_0914.csv'
TODAY = datetime.date.today()
WD = '月火水木金土日'
rows = []
for r in csv.DictReader(io.open(SRC, encoding='utf-8-sig')):
    pid = int(r['Post id'])
    ts = datetime.datetime.utcfromtimestamp(((pid >> 22) + 1288834974657) / 1000) + datetime.timedelta(hours=9)
    if (TODAY - ts.date()).days < 2:
        continue
    rows.append((ts, int(r['URL Clicks'] or 0), int(r['Impressions'] or 0), (r['Post text'] or '')[:28]))

out = ['2日たった投稿 %d本（%s まで）' % (len(rows), max(r[0] for r in rows).strftime('%m/%d')), '',
       '| 曜日 | 本数 | クリック計 | 1本あたり | いちばん多い1本 | その1本を外した1本あたり |', '|---|---|---|---|---|---|']
for w in range(7):
    g = sorted([r for r in rows if r[0].weekday() == w], key=lambda r: -r[1])
    if not g:
        continue
    tot = sum(r[1] for r in g)
    top = g[0]
    rest = (tot - top[1]) / (len(g) - 1) if len(g) > 1 else 0
    out.append('| %s | %d | %d | %.2f | %s %d clk「%s」 | %.2f |' % (
        WD[w], len(g), tot, tot / len(g), top[0].strftime('%m/%d'), top[1], top[3], rest))
io.open('tmp/x_weekday_check_0914.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('→ tmp/x_weekday_check_0914.txt')
