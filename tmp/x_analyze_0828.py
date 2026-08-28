# -*- coding: utf-8 -*-
"""X実測の再分析（2026-08-28）。
🚨判定は投稿から3日以上たった分だけ（伸びは3〜4日続く＝feedback_x_ctr_observations）。
投稿時刻は Post id（Snowflake）から復元する。"""
import csv, io, sys, datetime, collections, statistics, re
sys.stdout.reconfigure(encoding='utf-8')

EPOCH = 1288834974657  # Twitter snowflake epoch (ms)
def post_dt(pid):
    ms = (int(pid) >> 22) + EPOCH
    return datetime.datetime.utcfromtimestamp(ms / 1000.0) + datetime.timedelta(hours=9)

rows = []
for r in csv.DictReader(io.open('tmp/x_content_0828.csv', encoding='utf-8-sig')):
    try:
        dt = post_dt(r['Post id'])
    except Exception:
        continue
    def n(k):
        v = (r.get(k) or '0').replace(',', '').strip()
        try:
            return int(float(v))
        except Exception:
            return 0
    rows.append({
        'dt': dt, 'text': r.get('Post text') or '',
        'imp': n('Impressions'), 'eng': n('Engagements'), 'like': n('Likes'),
        'rt': n('Reposts'), 'url': n('URL Clicks'), 'prof': n('Profile visits'),
        'det': n('Detail Expands'), 'book': n('Bookmarks'),
    })
rows.sort(key=lambda x: x['dt'])
TODAY = datetime.datetime(2026, 8, 28, 20, 45)
mature = [r for r in rows if (TODAY - r['dt']).days >= 3]
print('全%d件 / 3日以上たった判定対象 %d件' % (len(rows), len(mature)))
print('期間 %s 〜 %s' % (rows[0]['dt'].strftime('%m/%d'), rows[-1]['dt'].strftime('%m/%d')))
print()

def med(v):
    return statistics.median(v) if v else 0

# ① 週ごとの推移（リーチが本当に伸びているか）
print('=== ① 週ごとの推移（中央値）===')
byw = collections.defaultdict(list)
for r in mature:
    k = r['dt'].isocalendar()[:2]
    byw[k].append(r)
for k in sorted(byw):
    g = byw[k]
    d0 = min(x['dt'] for x in g).strftime('%m/%d')
    print('  %s〜 (%2d本)  imp中央値%6.0f  最大%6d  URLクリック中央値%4.1f  RT合計%3d' % (
        d0, len(g), med([x['imp'] for x in g]), max(x['imp'] for x in g),
        med([x['url'] for x in g]), sum(x['rt'] for x in g)))
print()

# ② 時間帯別
print('=== ② 投稿時間帯 別（3日以上経過分）===')
byh = collections.defaultdict(list)
for r in mature:
    byh[r['dt'].hour].append(r)
for h in sorted(byh):
    g = byh[h]
    print('  %2d時台 (%2d本) imp中央値%6.0f  URLクリック中央値%4.1f  合計URL%4d' % (
        h, len(g), med([x['imp'] for x in g]), med([x['url'] for x in g]), sum(x['url'] for x in g)))
print()

# ③ 本文の長さ別
print('=== ③ 本文の長さ 別 ===')
def bucket(n):
    if n < 200: return '1) 〜199字'
    if n < 300: return '2) 200-299字'
    if n < 400: return '3) 300-399字'
    if n < 600: return '4) 400-599字'
    return '5) 600字以上'
byl = collections.defaultdict(list)
for r in mature:
    byl[bucket(len(r['text']))].append(r)
for k in sorted(byl):
    g = byl[k]
    print('  %-12s (%2d本) imp中央値%6.0f  URLクリック中央値%4.1f' % (
        k, len(g), med([x['imp'] for x in g]), med([x['url'] for x in g])))
print()

# ④ 伸びた投稿トップ10
print('=== ④ インプレッション上位10（3日以上経過分）===')
for r in sorted(mature, key=lambda x: -x['imp'])[:10]:
    head = r['text'].split('\n')[0][:34]
    print('  %s %02d:%02d imp%6d RT%3d いいね%3d URL%3d ｜ %s' % (
        r['dt'].strftime('%m/%d'), r['dt'].hour, r['dt'].minute,
        r['imp'], r['rt'], r['like'], r['url'], head))
print()

# ⑤ RTの効果
print('=== ⑤ RTがついた投稿とつかない投稿 ===')
a = [r for r in mature if r['rt'] > 0]
b = [r for r in mature if r['rt'] == 0]
print('  RTあり %2d本  imp中央値%6.0f' % (len(a), med([x['imp'] for x in a])))
print('  RTなし %2d本  imp中央値%6.0f' % (len(b), med([x['imp'] for x in b])))
