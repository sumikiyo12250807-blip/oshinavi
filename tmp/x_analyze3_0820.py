# -*- coding: utf-8 -*-
"""Xエクスポートの追加分析。文脈（告知の型）と時間帯を切り分ける。"""
import csv, io, sys, datetime, statistics as st, collections, re
sys.stdout.reconfigure(encoding='utf-8')

EPOCH = 1288834974657
JST = datetime.timezone(datetime.timedelta(hours=9))
rows = []
for r in csv.DictReader(io.open('tmp/x_content_3m_0820.csv', encoding='utf-8-sig')):
    try:
        pid = int(r['Post id'])
    except (TypeError, ValueError):
        continue
    ts = datetime.datetime.fromtimestamp(((pid >> 22) + EPOCH) / 1000.0, tz=JST)
    t = r.get('Post text') or ''
    r['_dt'], r['_hour'], r['_text'] = ts, ts.hour, t
    for k in ('Impressions', 'Engagements', 'URL Clicks', 'Likes', 'Reposts', 'Replies',
              'Profile visits', 'Detail Expands'):
        try:
            r[k] = int(r.get(k) or 0)
        except ValueError:
            r[k] = 0
    # 告知の型
    if '"本日発売"' in t or '“本日発売”' in t or '本日発売"ピックアップ' in t:
        kind = '本日発売'
    elif '"明日発売"' in t or '明日発売"ピックアップ' in t:
        kind = '明日発売'
    elif 'ピックアップ' in t and re.search(r'"\d+/?\d*日?発売"', t):
        kind = 'N日後発売'
    elif '締切' in t or 'まで' in t[:40]:
        kind = '締切/リマインド'
    else:
        kind = 'その他'
    r['_kind'] = kind
    r['_tag'] = t.count('#')
    r['_url'] = ('oshinavi.jp' in t) or ('t.co' in t)
    rows.append(r)

rows.sort(key=lambda r: r['_dt'])
TODAY = datetime.datetime.now(JST).date()
S = [r for r in rows if (TODAY - r['_dt'].date()).days >= 3]

out = []
P = out.append
tot = lambda sel, k: sum(r[k] for r in sel)


def block(title, keyfn, sel):
    P('【%s】' % title)
    g = collections.defaultdict(list)
    for r in sel:
        g[keyfn(r)].append(r)
    P('  %-16s %4s %8s %8s %9s %10s' % ('区分', '本数', 'インプ中央', 'インプ平均', 'エンゲ率', 'URLクリック'))
    for k in sorted(g, key=lambda k: -len(g[k])):
        v = g[k]
        imp = [r['Impressions'] for r in v]
        ti = sum(imp) or 1
        P('  %-16s %4d %8.0f %8.0f %8.2f%% %6d (%.2f%%)' % (
            str(k), len(v), st.median(imp), sum(imp) / len(v),
            100.0 * tot(v, 'Engagements') / ti, tot(v, 'URL Clicks'),
            100.0 * tot(v, 'URL Clicks') / ti))
    P('')


P('=== 追加分析（確定分 %d件・投稿から3日以上） ===' % len(S))
P('')
block('告知の型', lambda r: r['_kind'], S)
block('本文にURLがあるか', lambda r: 'URLあり' if r['_url'] else 'URLなし', S)
block('ハッシュタグの数', lambda r: '#%d個' % min(r['_tag'], 4), S)

P('【時間帯 × 告知の型（本数3以上のみ）】')
g = collections.defaultdict(list)
for r in S:
    band = ('朝5-9' if 5 <= r['_hour'] < 10 else '昼10-16' if 10 <= r['_hour'] < 17
            else '夕17-19' if 17 <= r['_hour'] < 20 else '夜20-23')
    g[(band, r['_kind'])].append(r)
P('  %-10s %-10s %4s %8s %9s %10s' % ('時間帯', '型', '本数', 'インプ中央', 'エンゲ率', 'URLクリック'))
for k in sorted(g, key=lambda k: -len(g[k])):
    v = g[k]
    if len(v) < 3:
        continue
    imp = [r['Impressions'] for r in v]
    ti = sum(imp) or 1
    P('  %-10s %-10s %4d %8.0f %8.2f%% %6d (%.2f%%)' % (
        k[0], k[1], len(v), st.median(imp),
        100.0 * tot(v, 'Engagements') / ti, tot(v, 'URL Clicks'),
        100.0 * tot(v, 'URL Clicks') / ti))
P('')

P('【本文の実長さの分布（CSVのPost text基準）】')
ls = sorted(len(r['_text']) for r in S)
P('  最短%d / 中央%d / 平均%.0f / 最長%d字' % (ls[0], ls[len(ls) // 2], sum(ls) / len(ls), ls[-1]))
P('  ※CSVの Post text はURLがt.coに置換されるので、実投稿の字数とは少しずれる')
P('')

P('【1本あたりの平均（確定分）】')
P('  インプ %.0f / エンゲージ %.2f / URLクリック %.2f / プロフ訪問 %.2f' % (
    tot(S, 'Impressions') / len(S), tot(S, 'Engagements') / len(S),
    tot(S, 'URL Clicks') / len(S), tot(S, 'Profile visits') / len(S)))
P('  URLクリックが1本でも出た投稿の割合 %.0f%%' % (
    100.0 * sum(1 for r in S if r['URL Clicks']) / len(S)))
P('')

P('【日別・URLクリック合計（サイトへの送客の実数）】')
d = collections.defaultdict(int)
di = collections.defaultdict(int)
for r in rows:
    d[r['_dt'].strftime('%m/%d')] += r['URL Clicks']
    di[r['_dt'].strftime('%m/%d')] += r['Impressions']
for k in sorted(d):
    if di[k]:
        P('  %s  imp%5d  URL%3d' % (k, di[k], d[k]))

io.open('tmp/x_analysis3_0820.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('ok')
