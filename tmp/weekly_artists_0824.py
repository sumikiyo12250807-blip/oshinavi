# -*- coding: utf-8 -*-
"""記事の主役を選ぶための素材。
🚨読者は「今週何件」ではなく「自分の推しの名前があるか」を見に来る（2026-08-20 ユーザー指摘）。
だから **アーティスト単位** で、この週にまとめて発売になるものを並べる。
 ・この週(8/24〜8/30)に発売が始まる枠の数
 ・会場数（ツアーの規模）
 ・発売日
"""
import re, io, json, sys, datetime, collections
sys.stdout.reconfigure(encoding='utf-8')

FROM, TO = '2026-08-24', '2026-08-30'
WD = '月火水木金土日'
h = io.open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))

GL = {'jpop': 'J-POP', 'rock': 'ロック', 'kpop': 'K-POP', 'anime': 'アニメ', 'idol': 'アイドル',
      'classic': 'クラシック', 'yougaku': '洋楽', 'jazz': 'ジャズ', 'enka': '演歌・歌謡',
      'dento': '伝統芸能', 'owarai': 'お笑い・落語', 'engeki': '演劇', 'musical': 'ミュージカル',
      'sports': 'スポーツ', 'fes': 'フェス', 'kids': 'キッズ', 'art': 'アート', 'new': '新着',
      'hanabi': '花火', 'dinnershow': 'ディナーショー', 'chanson': 'シャンソン', 'musicetc': 'その他音楽',
      '2.5ji': '2.5次元', 'seiyuu': '声優', 'kaidan': '怪談', 'fanevent': 'ファンイベント',
      'youtuber': 'YouTuber', 'vtuber': 'VTuber', 'hiphop': 'ヒップホップ', 'gourmet': 'グルメ',
      'aisatsu': '舞台挨拶'}

rows = []
for e in EVENTS:
    ts = [t for t in (e.get('tickets') or [])
          if t.get('startDate') and FROM <= t['startDate'] <= TO and not t.get('soldout')]
    if not ts:
        continue
    v = e.get('venue') or ''
    nven = v.count('／') + 1 if v.startswith('全国ツアー（') else 1
    days = sorted({t['startDate'] for t in ts})
    rows.append({
        'id': e['id'], 'artist': e.get('artist'), 'genre': GL.get(e.get('genre'), e.get('genre')),
        'slots': len(ts), 'venues': nven, 'days': days, 'last': e.get('date'),
        'pia': (e.get('links') or {}).get('pia') or '',
        'types': [t.get('type') for t in ts],
    })

out = []
P = out.append
P('=== 8/24(月)〜8/30(日) に発売が始まるもの：アーティスト単位 ===')
P('')
P('【この週に発売になる枠が多い順（＝まとめて一斉発売になるアーティスト）】')
for r in sorted(rows, key=lambda r: (-r['slots'], -r['venues']))[:30]:
    d = '・'.join('%s(%s)' % (x[5:].replace('-', '/'), WD[datetime.date.fromisoformat(x).weekday()])
                 for x in r['days'])
    P('  %2d枠 %2d会場 [%-8s] id%-5s %-34s 発売 %s' % (
        r['slots'], r['venues'], r['genre'], r['id'], (r['artist'] or '')[:34], d))
P('')
P('【会場数の多いツアー（規模の大きい順）】')
for r in sorted(rows, key=lambda r: -r['venues'])[:20]:
    if r['venues'] < 3:
        continue
    P('  %2d会場 %2d枠 [%-8s] id%-5s %-34s 千秋楽 %s' % (
        r['venues'], r['slots'], r['genre'], r['id'], (r['artist'] or '')[:34], r['last']))
P('')
P('【ジャンル別の一覧（音楽系だけ・名前が読者の入口になるので全部出す）】')
by = collections.defaultdict(list)
for r in rows:
    by[r['genre']].append(r)
for g in ('J-POP', 'ロック', 'K-POP', 'アイドル', 'アニメ', '演歌・歌謡', '洋楽', 'ジャズ'):
    if g not in by:
        continue
    P('◆ %s（%d件）' % (g, len(by[g])))
    for r in sorted(by[g], key=lambda r: (-r['slots'], -r['venues'])):
        P('   %2d枠 %2d会場 id%-5s %s' % (r['slots'], r['venues'], r['id'], r['artist']))
P('')
P('【舞台・演芸系】')
for g in ('ミュージカル', '演劇', 'お笑い・落語', '伝統芸能', 'クラシック'):
    if g not in by:
        continue
    P('◆ %s（%d件）' % (g, len(by[g])))
    for r in sorted(by[g], key=lambda r: (-r['slots'], -r['venues']))[:12]:
        P('   %2d枠 %2d会場 id%-5s %s' % (r['slots'], r['venues'], r['id'], r['artist']))

io.open('tmp/weekly_artists_0824.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('エントリ', len(rows), '件')
