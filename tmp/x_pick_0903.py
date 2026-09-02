# -*- coding: utf-8 -*-
"""X投稿の素材出し＝9/4(明日)発売＋9/5・9/6(2〜3日後)発売の枠を、ジャンル別×時間順で並べる。

判定＝startDate が対象日 かつ type に「M/D HH:MM発売」の明示がある枠だけ
（date は締切のことが多い＝memory: feedback_sale_start_vs_deadline）。
"""
import collections
import datetime
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

TARGETS = ['2026-09-04', '2026-09-05', '2026-09-06']
WD = '月火水木金土日'

GLABEL = {
    'jpop': 'J-POP', 'rock': 'ロック', 'kpop': 'K-POP', 'yougaku': '洋楽',
    'hiphop': 'HIP HOP', 'anime': 'アニソン', 'idol': 'アイドル',
    'youtuber': 'YouTuber', 'vtuber': 'VTuber', 'kids': 'キッズ',
    'classic': 'クラシック', 'jazz': 'ジャズ', 'enka': '演歌', 'dento': '伝統',
    'chanson': 'シャンソン', 'musicetc': '音楽そのほか', 'kaidan': '怪談',
    'engeki': '演劇', 'fes': 'フェス', 'sports': 'スポーツ', 'hanabi': '花火大会',
    '2.5ji': '2.5次元', 'seiyuu': '声優', 'owarai': 'お笑い', 'musical': 'ミュージカル',
    'aisatsu': '舞台挨拶', 'dinnershow': 'ディナーショー', 'art': 'アート',
    'gourmet': 'グルメ', 'fanevent': 'ファンイベント', 'douyou': '童謡・唱歌',
    'circus': 'サーカス', 'magic': 'マジック', 'gakusai': '学園祭', 'new': '新着',
}

src = open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'const EVENTS = (\[.*?\]);\n', src, re.S).group(1))

rows = collections.defaultdict(lambda: collections.defaultdict(list))
for e in EVENTS:
    g = e.get('genre') or ''
    for t in e.get('tickets', []):
        if t.get('soldout'):
            continue
        sd = t.get('startDate')
        if sd not in TARGETS:
            continue
        m = re.search(r'(\d{1,2})/(\d{1,2})\s+(\d{1,2}:\d{2})発売', t.get('type', ''))
        if not m:
            continue
        hhmm = m.group(3)
        pref = e.get('prefecture') or ''
        pm = re.search(r'（([^（）]*?)\s+(?:R\d年\s*)?\d{1,2}/\d{1,2}', t.get('type', ''))
        if pm and pm.group(1).strip():
            pref = pm.group(1).strip()
        kind = '先行' if re.match(r'^(先行|.*先行|プレリザーブ|プリセール|抽選|.*次受付|.*次プレリザーブ)', t['type']) else '一般'
        rows[sd][g].append({
            'time': hhmm, 'artist': e.get('artist', ''), 'name': e.get('name', ''),
            'pref': pref, 'venue': e.get('venue', ''), 'showdate': e.get('date', ''),
            'kind': kind, 'type': t['type'], 'id': e['id'],
        })

for d in TARGETS:
    dt = datetime.date.fromisoformat(d)
    tot = sum(len(v) for v in rows[d].values())
    print('\n' + '=' * 70)
    print('■ %s(%s) 発売開始 … %d枠 / %dジャンル' % (d, WD[dt.weekday()], tot, len(rows[d])))
    print('=' * 70)
    for g, lst in sorted(rows[d].items(), key=lambda kv: -len(kv[1])):
        print('\n【%s】%d件' % (GLABEL.get(g, g), len(lst)))
        for r in sorted(lst, key=lambda x: (x['time'], x['artist'])):
            mark = '（先行）' if r['kind'] == '先行' else ''
            print('  %s %s／%s%s  #%s' % (r['time'], r['artist'][:38], r['pref'], mark, r['id']))
