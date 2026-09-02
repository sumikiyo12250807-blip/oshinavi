# -*- coding: utf-8 -*-
"""X投稿の素材出し（9/4=明日 ＋ 9/5・9/6）。x_pick_0901.py の改良版。
🚨同じ公演が券種違い・公演回違いで何行も出るので、(時刻,名前,県,先行/一般) で重複を潰す。
   投稿の1行は「時刻 名前／県」なので、そこが同じなら読者には同じ行にしか見えない。
判定＝startDate が対象日 かつ type に「M/D HH:MM発売」の明示がある枠だけ
（date は締切のことが多い＝memory feedback_sale_start_vs_deadline）。
"""
import collections, datetime, json, re, sys

sys.stdout.reconfigure(encoding='utf-8')

TARGETS = ['2026-09-04', '2026-09-05', '2026-09-06']
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

src = open('index.html', encoding='utf-8', newline='').read()
EVENTS = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S).group(2))

rows = collections.defaultdict(lambda: collections.defaultdict(list))
seen = set()
for e in EVENTS:
    g = e.get('genre') or ''
    for t in e.get('tickets', []):
        if t.get('soldout'):
            continue
        sd = t.get('startDate')
        if sd not in TARGETS:
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
        pref = pref.replace('都', '').replace('府', '').replace('県', '') if pref not in ('京都', '東京') else pref
        kind = '先行' if re.match(
            r'^(先行|.*先行|プレリザーブ|プリセール|抽選|.*次受付|.*次プレリザーブ)', ty) else '一般'
        artist = e.get('artist') or e.get('name') or ''
        key = (sd, hhmm, artist, pref, kind)
        if key in seen:
            continue
        seen.add(key)
        rows[sd][g].append({'time': hhmm, 'artist': artist, 'pref': pref,
                            'venue': e.get('venue', ''), 'kind': kind, 'id': e['id']})

for d in TARGETS:
    dt = datetime.date.fromisoformat(d)
    tot = sum(len(v) for v in rows[d].values())
    print('\n' + '=' * 70)
    print('■ %s(%s) 発売開始 … %d件 / %dジャンル' % (d, WD[dt.weekday()], tot, len(rows[d])))
    print('=' * 70)
    for g, lst in sorted(rows[d].items(), key=lambda kv: -len(kv[1])):
        print('\n【%s】%d件' % (GLABEL.get(g, g), len(lst)))
        for r in sorted(lst, key=lambda x: (x['time'], x['artist'])):
            mark = '（先行）' if r['kind'] == '先行' else ''
            print('  %s %s／%s%s  [%s] #%s' % (r['time'], r['artist'][:40], r['pref'], mark,
                                              (r['venue'] or '')[:24], r['id']))
