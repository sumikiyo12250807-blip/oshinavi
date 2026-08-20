# -*- coding: utf-8 -*-
"""週1記事「今週のピックアップ」第1弾の素材を機械で集める。
対象＝2026-08-24(月)〜08-30(日)に発売が始まる枠を持つエントリ。
出すもの：①日別の件数 ②ジャンル別 ③会場数の多い大型ツアー ④全件リスト"""
import re, io, json, sys, collections
sys.stdout.reconfigure(encoding='utf-8')

FROM, TO = '2026-08-24', '2026-08-30'
h = io.open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))

GL = {'jpop': 'J-POP', 'rock': 'ロック', 'kpop': 'K-POP', 'hiphop': 'ヒップホップ',
      'anime': 'アニメ・アニソン', 'idol': 'アイドル', 'classic': 'クラシック',
      'yougaku': '洋楽', 'jazz': 'ジャズ', 'enka': '演歌・歌謡', 'chanson': 'シャンソン',
      'dento': '伝統芸能', 'owarai': 'お笑い・落語', 'engeki': '演劇', 'musical': 'ミュージカル',
      '2.5ji': '2.5次元', 'seiyuu': '声優', 'sports': 'スポーツ', 'fes': 'フェス',
      'kids': 'キッズ', 'art': 'アート・展示', 'hanabi': '花火', 'youtuber': 'YouTuber',
      'vtuber': 'VTuber', 'dinnershow': 'ディナーショー', 'kaidan': '怪談',
      'fanevent': 'ファンイベント', 'musicetc': 'その他音楽', 'gourmet': 'グルメ',
      'aisatsu': '舞台挨拶', 'new': '新着'}

hits = []
for e in EVENTS:
    ts = [t for t in (e.get('tickets') or [])
          if t.get('startDate') and FROM <= t['startDate'] <= TO and not t.get('soldout')]
    if ts:
        hits.append((e, ts))

day = collections.Counter()
gen = collections.Counter()
for e, ts in hits:
    gen[e.get('genre')] += 1
    for t in ts:
        day[t['startDate']] += 1

out = []
P = out.append
P('=== 8/24(月)〜8/30(日) に発売が始まるもの ===')
P('エントリ %d件 / 枠 %d件' % (len(hits), sum(len(t) for _, t in hits)))
P('')
P('【日別（枠の数）】')
WD = '月火水木金土日'
import datetime
for d in sorted(day):
    dt = datetime.date.fromisoformat(d)
    P('  %s(%s)  %2d枠' % (d[5:].replace('-', '/'), WD[dt.weekday()], day[d]))
P('')
P('【ジャンル別（エントリ数）】')
for g, n in gen.most_common():
    P('  %-16s %2d件' % (GL.get(g, g), n))
P('')
P('【会場数の多いツアー（深掘り候補）】')
tours = []
for e, ts in hits:
    v = e.get('venue') or ''
    n = v.count('／') + 1 if v.startswith('全国ツアー（') else 1
    tours.append((n, e, ts))
for n, e, ts in sorted(tours, key=lambda x: -x[0])[:12]:
    if n < 2:
        continue
    P('  %2d会場 id%-5s [%s] %s（千秋楽 %s）' % (n, e['id'], GL.get(e.get('genre'), e.get('genre')),
                                          e.get('artist'), e.get('date')))
P('')
P('【全件（発売日順）】')
rows = []
for e, ts in hits:
    for t in ts:
        rows.append((t['startDate'], t.get('type', ''), e))
for d, ty, e in sorted(rows, key=lambda r: (r[0], e['id'])):
    dt = datetime.date.fromisoformat(d)
    P('  %s(%s) [%-12s] id%-5s %s' % (d[5:].replace('-', '/'), WD[dt.weekday()],
                                      GL.get(e.get('genre'), e.get('genre')), e['id'],
                                      (e.get('artist') or '')[:38]))
    P('           %s / %s' % (ty, (e.get('venue') or '')[:60]))

io.open('tmp/weekly_0824.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('エントリ', len(hits), '件 / 枠', sum(len(t) for _, t in hits))
