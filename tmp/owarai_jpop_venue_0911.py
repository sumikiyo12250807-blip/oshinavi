# -*- coding: utf-8 -*-
"""明日9/11発売の「お笑い」と「音楽(JPOPほか)」を会場の大きさ順に並べる。

ユーザー（2026-09-10）＝「お笑いはフォローの数」「JPOPもフォロワーがおおいので」
→ ただし**フォロワー数が検索で取れない**（落語家は240位までのランキングにも出てこない）。
   ログイン済みブラウザでプロフィールを開けば読めるが、タブの切り替えが要る。
   返事が来るまでの控えとして、**箱の大きさ版**も出しておく。
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

CAP = {
    '大阪城ホール': 16000,
    '横浜みなとみらいホール 大ホール': 2020,
    'ミューザ川崎シンフォニーホール': 1997,
    '梅田芸術劇場メインホール': 1905,
    '札幌文化芸術劇場hitaru': 2302,
    'かめありリリオホール': 1000,
    '天満天神繁昌亭': 216,
    'あうるすぽっと': 301,
    '高崎芸術劇場 スタジオシアター': 300,
    'チキンジョージ': 500,
    'なかの芸能小劇場': 100,
    '軽井沢大賀ホール': 784,
    'あしや夢リアホール': 700,
    '吹田市文化会館（メイシアター） 中ホール': 600,
    'Yogibo HOLY MOUNTAIN': 350,
    '新横浜プリンスホテル シンフォニア': 400,
    '渋谷CLUB QUATTRO': 750,
    '川崎Serbian Night': 200,
    'Zepp Sapporo': 2000,
}


def cap_of(v):
    v = v or ''
    best, hit = 0, ''
    for k, c in CAP.items():
        if k[:7] in v or (v[:7] and v[:7] in k):
            if c > best:
                best, hit = c, k
    return best, hit


h = io.open('index.html', encoding='utf-8').read()
EV = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))

BUNDLES = [
    ('お笑い', ['owarai']),
    ('音楽（JPOPほか）', ['jpop', 'rock', 'kpop', 'enka', 'dinnershow',
                    'hougaku', 'musicetc', 'yougaku']),
]

for title, genres in BUNDLES:
    rows = []
    for e in EV:
        if e.get('genre') not in genres:
            continue
        for t in e.get('tickets') or []:
            if t.get('startDate') == '2026-09-11' and not t.get('soldout'):
                rows.append((e, t))
    print('=' * 70)
    print('■ %s … 明日9/11発売 %d枠（会場の大きい順）' % (title, len(rows)))
    out = [(cap_of(e.get('venue'))[0], cap_of(e.get('venue'))[1], e, t) for e, t in rows]
    for c, hit, e, t in sorted(out, key=lambda x: -x[0]):
        print('  %6s席  %-32s' % (c if c else '不明', (e.get('artist') or e.get('name') or '')[:32]))
        print('            会場 %s' % (e.get('venue') or '')[:56])
    print('')
