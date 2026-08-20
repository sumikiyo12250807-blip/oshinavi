# -*- coding: utf-8 -*-
"""Xのアナリティクス公式エクスポート（150投稿・2026-07-08〜08-20）を分析する。

  ・投稿時刻は CSV に無いが、Xの投稿ID（Snowflake）から復元できる
      timestamp_ms = (id >> 22) + 1288834974657   → +9h で JST
  ・CSV の Date 列は UTC 日付なので、JST に直してから曜日・日付を数える
  ・URL Clicks 列がある＝**本文リンクのクリックが投稿ごとに取れる**
"""
import csv, io, sys, datetime, statistics as st, collections, re
sys.stdout.reconfigure(encoding='utf-8')

SRC = 'tmp/x_content_3m_0820.csv'
OUT = 'tmp/x_analysis2_0820.txt'
EPOCH = 1288834974657
JST = datetime.timezone(datetime.timedelta(hours=9))

rows = []
for r in csv.DictReader(io.open(SRC, encoding='utf-8-sig')):
    try:
        pid = int(r['Post id'])
    except (TypeError, ValueError):
        continue
    ts = datetime.datetime.fromtimestamp(((pid >> 22) + EPOCH) / 1000.0, tz=JST)
    txt = r.get('Post text') or ''
    r['_dt'] = ts
    r['_hour'] = ts.hour
    r['_date'] = ts.strftime('%Y-%m-%d')
    r['_wd'] = '月火水木金土日'[ts.weekday()]
    r['_len'] = len(txt)
    r['_text'] = txt
    for k in ('Impressions', 'Likes', 'Engagements', 'Bookmarks', 'Shares', 'New follows',
              'Replies', 'Reposts', 'Profile visits', 'Detail Expands', 'URL Clicks'):
        try:
            r[k] = int(r.get(k) or 0)
        except ValueError:
            r[k] = 0
    rows.append(r)

rows.sort(key=lambda r: r['_dt'])
TODAY = datetime.datetime.now(JST).date()
# 伸びは3〜4日続くので、直近3日以内の投稿は「暫定」として傾向の判定から外す
def settled(r):
    return (TODAY - r['_dt'].date()).days >= 3

S = [r for r in rows if settled(r)]
out = []
P = out.append

P('=== Xアナリティクス公式エクスポート %d投稿（%s 〜 %s・JST） ===' % (
    len(rows), rows[0]['_dt'].strftime('%m/%d %H:%M'), rows[-1]['_dt'].strftime('%m/%d %H:%M')))
P('※伸びは3〜4日続くので、判定に使うのは投稿から3日以上たった %d件。直近 %d件は暫定値。' % (
    len(S), len(rows) - len(S)))
P('')

tot = lambda sel, k: sum(r[k] for r in sel)
P('【全体】 インプ計 %d / エンゲージ計 %d / **URLクリック計 %d** / ❤%d / RT%d / 返信%d / プロフ%d / 詳細%d' % (
    tot(rows, 'Impressions'), tot(rows, 'Engagements'), tot(rows, 'URL Clicks'),
    tot(rows, 'Likes'), tot(rows, 'Reposts'), tot(rows, 'Replies'),
    tot(rows, 'Profile visits'), tot(rows, 'Detail Expands')))
P('')

def block(title, keyfn, sel, minn=1):
    P('【%s】' % title)
    g = collections.defaultdict(list)
    for r in sel:
        g[keyfn(r)].append(r)
    P('  %-12s %4s %8s %8s %8s %10s %10s' % ('区分', '本数', 'インプ中央', 'インプ平均', 'インプ最大', 'エンゲ率', 'URLクリック'))
    for k in sorted(g):
        v = g[k]
        if len(v) < minn:
            continue
        imp = [r['Impressions'] for r in v]
        ti = sum(imp) or 1
        P('  %-12s %4d %8.0f %8.0f %8d %9.2f%% %6d (%.2f%%)' % (
            str(k), len(v), st.median(imp), sum(imp) / len(v), max(imp),
            100.0 * tot(v, 'Engagements') / ti, tot(v, 'URL Clicks'),
            100.0 * tot(v, 'URL Clicks') / ti))
    P('')


block('投稿時刻（JST・1時間刻み）', lambda r: '%02d時台' % r['_hour'], S)
block('時間帯（まとめ）', lambda r: ('朝 5-9時' if 5 <= r['_hour'] < 10 else
                              '昼 10-16時' if 10 <= r['_hour'] < 17 else
                              '夕 17-19時' if 17 <= r['_hour'] < 20 else
                              '夜 20-23時' if 20 <= r['_hour'] < 24 else '深夜 0-4時'), S)
block('曜日', lambda r: r['_wd'], S)
block('本文の長さ', lambda r: ('~200字' if r['_len'] < 200 else
                          '200-299字' if r['_len'] < 300 else
                          '300-399字' if r['_len'] < 400 else '400字以上'), S)
block('投稿日', lambda r: r['_date'], S)

P('【URLクリックが取れた投稿（実数の多い順）】')
cl = [r for r in rows if r['URL Clicks'] > 0]
P('  URLクリックが1以上の投稿は %d/%d本' % (len(cl), len(rows)))
for r in sorted(cl, key=lambda r: -r['URL Clicks'])[:20]:
    P('  %s %s(%s) imp%5d eng%3d **URL%2d** (%.2f%%) %s' % (
        r['_dt'].strftime('%m/%d %H:%M'), r['_wd'], '暫定' if not settled(r) else '確定',
        r['Impressions'], r['Engagements'], r['URL Clicks'],
        100.0 * r['URL Clicks'] / max(r['Impressions'], 1),
        re.sub(r'\s+', ' ', r['_text'])[:46]))
P('')

P('【インプレッション上位15（確定分のみ）】')
for r in sorted(S, key=lambda r: -r['Impressions'])[:15]:
    P('  %s %s imp%5d eng%3d URL%2d ❤%d RT%d %s' % (
        r['_dt'].strftime('%m/%d %H:%M'), r['_wd'], r['Impressions'], r['Engagements'],
        r['URL Clicks'], r['Likes'], r['Reposts'], re.sub(r'\s+', ' ', r['_text'])[:44]))
P('')

P('【エンゲージ率上位15（インプ50以上・確定分）】')
tbl = [(100.0 * r['Engagements'] / r['Impressions'], r) for r in S if r['Impressions'] >= 50]
for rate, r in sorted(tbl, key=lambda x: -x[0])[:15]:
    P('  %5.2f%% %s imp%5d eng%3d URL%2d %s' % (
        rate, r['_dt'].strftime('%m/%d %H:%M'), r['Impressions'], r['Engagements'],
        r['URL Clicks'], re.sub(r'\s+', ' ', r['_text'])[:44]))

io.open(OUT, 'w', encoding='utf-8').write('\n'.join(out))
print('wrote', OUT, len(out), 'lines')
