# -*- coding: utf-8 -*-
"""Fableに渡す「その日の素材」を作る（2026-09-03夜ぶん＝明日9/4発売）。

・9/4（明日）＝そのジャンルの全件（1件も削らない）
・9/5, 9/6（2〜3日後）＝**箱の大きさ順に5件だけ**（台本の決まり／2026-09-01ユーザー指定）
   キャパの目安＝ドーム>アリーナ>◯◯ホール 大ホール>ホール>小ホール/ライブハウス
・件数の実数は投稿に書かない決まりなので、丸めた言い方も添える（18→「20件近く」等）
"""
import collections, datetime, json, re, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TOMORROW = '2026-09-04'
LATER = ['2026-09-05', '2026-09-06']
WD = '月火水木金土日'

GLABEL = {
    'jpop': 'J-POP', 'rock': 'ロック', 'kpop': 'K-POP', 'yougaku': '洋楽',
    'hiphop': 'HIP HOP', 'anime': 'アニソン', 'idol': 'アイドル',
    'youtuber': 'YouTuber', 'vtuber': 'VTuber', 'kids': 'キッズ',
    'classic': 'クラシック', 'jazz': 'ジャズ', 'enka': '演歌', 'dento': '伝統',
    'hougaku': '伝統', 'chanson': 'シャンソン', 'musicetc': '音楽そのほか',
    'kaidan': '怪談', 'engeki': '演劇', 'fes': 'フェス', 'sports': 'スポーツ',
    'hanabi': '花火大会', '2.5ji': '2.5次元', 'seiyuu': '声優', 'owarai': 'お笑い',
    'musical': 'ミュージカル', 'aisatsu': '舞台挨拶', 'dinnershow': 'ディナーショー',
    'art': 'アート', 'gourmet': 'グルメ', 'fanevent': 'ファンイベント',
    'douyou': '童謡・唱歌', 'circus': 'サーカス', 'magic': 'マジック',
    'gakusai': '学園祭', 'talkshow': 'トークショー', 'new': '新着',
}

# 投稿の束ね方（1投稿＝1ジャンル。小さいジャンルは「そのほか」に寄せる）
BUNDLE = {
    'classic': 'クラシック', 'jazz': 'クラシック',
    'jpop': 'JPOPなどの音楽', 'rock': 'JPOPなどの音楽', 'enka': 'JPOPなどの音楽',
    'yougaku': 'JPOPなどの音楽', 'kpop': 'JPOPなどの音楽', 'musicetc': 'JPOPなどの音楽',
    'idol': 'JPOPなどの音楽', 'anime': 'JPOPなどの音楽', 'fes': 'JPOPなどの音楽',
    'owarai': 'お笑い・落語',
    'engeki': '舞台・そのほか', 'musical': '舞台・そのほか', 'dento': '舞台・そのほか',
    'hougaku': '舞台・そのほか', 'kids': '舞台・そのほか', 'aisatsu': '舞台・そのほか',
    'art': '舞台・そのほか', 'sports': '舞台・そのほか', 'seiyuu': '舞台・そのほか',
    '2.5ji': '舞台・そのほか', 'gakusai': '舞台・そのほか', 'talkshow': '舞台・そのほか',
    'circus': '舞台・そのほか', 'magic': '舞台・そのほか', 'dinnershow': '舞台・そのほか',
    'fanevent': '舞台・そのほか', 'hanabi': '舞台・そのほか', 'gourmet': '舞台・そのほか',
    'douyou': '舞台・そのほか', 'kaidan': '舞台・そのほか', 'vtuber': '舞台・そのほか',
    'youtuber': '舞台・そのほか', 'chanson': 'JPOPなどの音楽',
}


def capa_rank(venue):
    v = venue or ''
    if 'ドーム' in v:
        return 0
    if 'アリーナ' in v or '体育館' in v or 'スタジアム' in v:
        return 1
    if '大ホール' in v or 'サントリーホール' in v or 'オペラシティ' in v or '国際フォーラム' in v:
        return 2
    if 'ホール' in v or '劇場' in v or '会館' in v:
        return 3
    return 4


src = open('index.html', encoding='utf-8', newline='').read()
EVENTS = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S).group(2))

rows = collections.defaultdict(list)
seen = set()
for e in EVENTS:
    g = e.get('genre') or ''
    # 新着プールは下書きジャンル(_genre)があればそれで束ねる
    gg = e.get('_genre') if g == 'new' and e.get('_genre') else g
    for t in e.get('tickets', []):
        if t.get('soldout'):
            continue
        sd = t.get('startDate')
        if sd != TOMORROW and sd not in LATER:
            continue
        ty = t.get('type', '')
        m = re.search(r'(\d{1,2})/(\d{1,2})\s+(\d{1,2}:\d{2})発売', ty)
        if not m:
            continue
        hhmm = m.group(3)
        pref = e.get('prefecture') or ''
        pm = re.search(r'（([^（）]*?)\s+(?:R\d年\s*)?\d{1,2}/\d{1,2}', ty)
        if pm and pm.group(1).strip():
            pref = pm.group(1).strip()
        if pref not in ('京都', '東京'):
            pref = pref.replace('都', '').replace('府', '').replace('県', '')
        kind = '（先行）' if re.match(
            r'^(先行|.*先行|プレリザーブ|プリセール|抽選|.*次受付|.*次プレリザーブ)', ty) else ''
        artist = e.get('artist') or e.get('name') or ''
        key = (sd, hhmm, artist, pref, kind)
        if key in seen:
            continue
        seen.add(key)
        rows[sd].append({'time': hhmm, 'artist': artist, 'pref': pref, 'kind': kind,
                         'venue': e.get('venue', ''), 'bundle': BUNDLE.get(gg, '舞台・そのほか'),
                         'genre': GLABEL.get(gg, gg), 'id': e['id']})


def maru(n):
    if n < 10:
        return '%d件' % n
    if n < 20:
        return '%d件近く' % (round(n / 10) * 10 + (0 if n % 10 < 5 else 0))
    return '%d件以上' % (n // 10 * 10)


out = []
dt = datetime.date.fromisoformat(TOMORROW)
out.append('# その日の素材（2026-09-03 夜の投稿ぶん）\n')
out.append('明日＝**%s(%s)** 発売開始。\n' % (TOMORROW, WD[dt.weekday()]))

bundles = collections.defaultdict(list)
for r in rows[TOMORROW]:
    bundles[r['bundle']].append(r)

for b, lst in sorted(bundles.items(), key=lambda kv: -len(kv[1])):
    out.append('\n## 【まとめ投稿】%s … %d件（**この束は1件も削らずに全部並べる**）\n' % (b, len(lst)))
    for r in sorted(lst, key=lambda x: (x['time'], x['artist'])):
        out.append('%s %s／%s%s' % (r['time'], r['artist'], r['pref'], r['kind']))

for d in LATER:
    dt2 = datetime.date.fromisoformat(d)
    lst = rows[d]
    big = sorted(lst, key=lambda x: (capa_rank(x['venue']), x['time']))[:5]
    big = sorted(big, key=lambda x: x['time'])
    out.append('\n## 【%s(%s)発売】…この日は %s（**大物5件だけ並べて「他」で締める**）\n'
               % (d, WD[dt2.weekday()], maru(len(lst))))
    for r in big:
        out.append('%s %s／%s%s   ［会場 %s／%s］' % (r['time'], r['artist'], r['pref'], r['kind'],
                                                 (r['venue'] or '')[:26], r['genre']))

open('tmp/x_fable_material_0903.md', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('\n'.join(out[:8]))
print('...')
print('→ tmp/x_fable_material_0903.md（%d行）' % len(out))
for b, lst in sorted(bundles.items(), key=lambda kv: -len(kv[1])):
    print('   まとめ「%s」= %d件' % (b, len(lst)))
