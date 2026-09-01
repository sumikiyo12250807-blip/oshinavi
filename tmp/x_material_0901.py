# -*- coding: utf-8 -*-
"""X投稿の素材を「投稿の束ごと」に整える（2026-09-01 夜の便）。
1エントリ1行に畳んで（同じ枠が公演ごとに何本もあるため）、時刻順に並べる。
"""
import collections
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

DAYS = {'2026-09-02': '明日9/2(水)', '2026-09-03': '9/3(木)', '2026-09-04': '9/4(金)'}

# 投稿の束＝読む人の言葉で。新着プールは中身で振り分ける
BUCKET = [
    ('音楽', {'jpop', 'rock', 'enka', 'idol', 'kpop', 'yougaku', 'anime', 'musicetc', 'chanson'}),
    ('クラシック', {'classic', 'dento', 'jazz'}),
    ('舞台・映画', {'engeki', 'musical', '2.5ji', 'aisatsu', 'art'}),
    ('お笑い', {'owarai'}),
    ('スポーツ', {'sports'}),
]
# 新着プール（genre:"new"）の行き先。e+は _genre を持たないので名前で決める
NEWMAP = {
    5996: '音楽', 6009: '音楽', 6010: '音楽', 6014: '音楽', 6040: '音楽', 6044: '音楽',
    6045: '音楽', 6053: '音楽', 6063: '音楽', 6183: '音楽', 6086: '音楽',
    6119: 'お笑い', 6127: 'お笑い', 6134: 'お笑い',
    6136: '舞台・映画', 6137: '舞台・映画', 6145: '舞台・映画', 6146: '舞台・映画',
    6139: 'スポーツ', 6140: 'スポーツ', 6142: 'スポーツ', 6143: 'スポーツ',
}

PREFS = set(re.findall(r'"([^"]+)":\s*"(?:hokkaido|tohoku|kanto|chubu|kinki|chugoku|shikoku|kyushu|kaigai)"',
                       open('index.html', encoding='utf-8').read()))

src = open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'const EVENTS = (\[.*?\]);\n', src, re.S).group(1))

G2B = {}
for b, gs in BUCKET:
    for g in gs:
        G2B[g] = b

data = collections.defaultdict(lambda: collections.defaultdict(dict))
for e in EVENTS:
    g = e.get('genre') or ''
    b = NEWMAP.get(e['id']) if g == 'new' else G2B.get(g)
    if g == 'new' and not b:
        b = G2B.get(e.get('_genre') or '')
    if not b:
        continue
    for t in e.get('tickets', []):
        if t.get('soldout'):
            continue
        sd = t.get('startDate')
        if sd not in DAYS:
            continue
        m = re.search(r'(\d{1,2})/(\d{1,2})\s+(\d{1,2}:\d{2})発売', t.get('type', ''))
        if not m:
            continue
        hhmm = m.group(3)
        pm = re.search(r'（([^（）]*?)\s+(?:R\d年\s*)?\d{1,2}/\d{1,2}', t.get('type', ''))
        pref = (pm.group(1).strip() if pm and pm.group(1).strip() else (e.get('prefecture') or ''))
        if pref not in PREFS and re.sub(r'(都|府|県)$', '', pref) in PREFS:
            pref = re.sub(r'(都|府|県)$', '', pref)
        senko = bool(re.match(r'^(?!一般)(.*(先行|プレリザーブ|プリセール|抽選|次受付))', t['type']))
        key = re.sub(r'\s+', '', e.get('artist', ''))
        cur = data[sd][b].get(key)
        if cur is None:
            data[sd][b][key] = {'time': hhmm, 'artist': e.get('artist', ''),
                                    'prefs': {pref}, 'senko': senko, 'show': e.get('date', '')}
        else:
            cur['prefs'].add(pref)
            cur['time'] = min(cur['time'], hhmm)
            cur['senko'] = cur['senko'] and senko

for sd in DAYS:
    print('\n' + '#' * 72)
    print('# %s に発売開始' % DAYS[sd])
    print('#' * 72)
    for b, _ in BUCKET:
        lst = data[sd].get(b) or {}
        if not lst:
            continue
        print('\n【%s】%d組' % (b, len(lst)))
        for r in sorted(lst.values(), key=lambda x: (x['time'], x['artist'])):
            p = '・'.join(sorted(x for x in r['prefs'] if x))
            tag = '（先行）' if r['senko'] else ''
            print('  %s %s／%s%s' % (r['time'], r['artist'], p, tag))
