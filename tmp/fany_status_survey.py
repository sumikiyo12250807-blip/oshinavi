# -*- coding: utf-8 -*-
"""FANYのハーベスト結果から、売り状態の文言・公演の形・県の入り方を全部数える。
ビルダーを書く前に**実データの語彙**を確かめるため（推測で対応表を作らない）。

  python tmp/fany_status_survey.py tmp/fany_0921.json
"""
import collections
import io
import json
import re
import sys

path = sys.argv[1] if len(sys.argv) > 1 else 'tmp/fany_0921.json'
d = json.load(open(path, encoding='utf-8'))
perfs = d['performances']

st = collections.Counter()
style = collections.Counter()
pair = collections.Counter()
cls = collections.Counter()
pref = collections.Counter()
name_of_pref = collections.Counter()
nosale = 0
sales_n = collections.Counter()
end_missing = 0
start_missing = 0
dest = collections.Counter()

for p in perfs:
    cls[p.get('class')] += 1
    ss = p.get('performance_sales') or []
    sales_n[len(ss)] += 1
    if not ss:
        nosale += 1
    for s in ss:
        st[s.get('display_sales_status')] += 1
        style[s.get('display_sales_style')] += 1
        pair[(s.get('display_sales_status'), s.get('display_sales_style'))] += 1
        pref[s.get('prefecture_code')] += 1
        if not s.get('sales_end_datetime_raw'):
            end_missing += 1
        if not s.get('sales_start_datetime_raw'):
            start_missing += 1
        u = s.get('destination_url') or ''
        m = re.match(r'https?://[^/]+/([a-z_]+)/', u)
        dest[m.group(1) if m else u[:40]] += 1
    v = p.get('venue_name') or ''
    m = re.search(r'[（(]([^（）()]+[都道府県])[）)]', v)
    name_of_pref[m.group(1) if m else '（県が無い）'] += 1

out = io.open('tmp/fany_status_survey.txt', 'w', encoding='utf-8')
out.write('%s  公演 %d件 / 総枠 %d枠\n' % (path, len(perfs), sum(st.values())))
out.write('引いた範囲 %s  総件数の申告 %s\n\n' % (d.get('range'), d.get('total_reported')))
out.write('=== 売り状態の文言（display_sales_status）===\n')
for k, n in st.most_common():
    out.write('  %-24s %6d枠\n' % (k, n))
out.write('\n=== アイコン（display_sales_style）===\n')
for k, n in style.most_common():
    out.write('  %-26s %6d枠\n' % (k, n))
out.write('\n=== 文言×アイコンの組み合わせ ===\n')
for (a, b), n in pair.most_common():
    out.write('  %-24s %-26s %6d枠\n' % (a, b, n))
out.write('\n=== 公演の形（class）===  01=単日\n')
for k, n in cls.most_common():
    out.write('  %-6s %6d件\n' % (k, n))
out.write('\n枠が0の公演 %d件 / 受付開始が空 %d枠 / 受付終了が空 %d枠\n'
          % (nosale, start_missing, end_missing))
out.write('\n=== 1公演あたりの枠数 ===\n')
for k, n in sorted(sales_n.items()):
    out.write('  %2d枠 … %5d件\n' % (k, n))
out.write('\n=== 申込の飛び先の形 ===\n')
for k, n in dest.most_common(10):
    out.write('  %-20s %6d枠\n' % (k, n))
out.write('\n=== 会場名に入っている県（上位20）===\n')
for k, n in name_of_pref.most_common(20):
    out.write('  %-10s %5d件\n' % (k, n))
out.write('\n=== prefecture_code（上位20）===\n')
for k, n in pref.most_common(20):
    out.write('  %-4s %6d枠\n' % (k, n))
out.write('\n=== ジャンル別の公演数（売り場の申告）===\n')
for k, n in sorted((d.get('genre_counts') or {}).items()):
    out.write('  genre=%s %6d件\n' % (k, n))
out.write('\n取れなかった要求 %d個\n' % len(d.get('missed_offsets') or []))
out.write('\n=== 期間もの（class != 01）の例 5件 ===\n')
for p in [x for x in perfs if x.get('class') != '01'][:5]:
    out.write('  %s / %s / %s 〜 %s / class=%s\n'
              % ((p.get('name') or '')[:30], p.get('venue_name'),
                 p.get('valid_period_start_date'), p.get('valid_period_finish_date'),
                 p.get('class')))
out.write('\n=== 単日の例 3件（日付の書き方）===\n')
for p in perfs[:3]:
    out.write('  %r\n' % p.get('performance_date'))
out.close()
print('wrote tmp/fany_status_survey.txt')
