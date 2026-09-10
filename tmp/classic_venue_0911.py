# -*- coding: utf-8 -*-
"""明日9/11発売のクラシック・ジャズを、会場ごとに並べる（冒頭に出す名前を「箱の大きさ」で決めるため）。

ユーザー（2026-09-10）＝「クラシックは箱の大きさで決めて」
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# よく知られたホールの席数（冒頭を決めるための目安・本文には書かない）
CAP = {
    '横浜みなとみらいホール 大ホール': 2020,
    'ミューザ川崎シンフォニーホール': 1997,
    '梅田芸術劇場メインホール': 1905,
    '東京オペラシティ コンサートホール': 1632,
    '札幌文化芸術劇場hitaru': 2302,
    '苫小牧市民文化ホール': 1300,
    '高槻城公園芸術文化劇場': 1500,
    '戸田市文化会館': 1275,
    '浜離宮朝日ホール': 552,
    'サントリーホール ブルーローズ': 384,
    '東京オペラシティ リサイタルホール': 265,
    'Hakuju Hall': 300,
    'KDDIホール': 250,
    '横浜市鶴見区民文化センター サルビアホール': 500,
    'しまなみ交流館': 600,
    '日立システムズホール仙台 シアターホール': 800,
}

h = io.open('index.html', encoding='utf-8').read()
EV = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))

rows = []
for e in EV:
    if e.get('genre') not in ('classic', 'jazz'):
        continue
    for t in e.get('tickets') or []:
        if t.get('startDate') == '2026-09-11' and not t.get('soldout'):
            rows.append((e, t))


def cap_of(venue):
    v = venue or ''
    best = 0
    hit = ''
    for k, c in CAP.items():
        if k[:8] in v or v[:8] in k:
            if c > best:
                best, hit = c, k
    return best, hit


print('明日9/11発売のクラシック・ジャズ %d枠' % len(rows))
print('')
out = []
for e, t in rows:
    c, hit = cap_of(e.get('venue'))
    out.append((c, e, t, hit))
for c, e, t, hit in sorted(out, key=lambda x: -x[0]):
    print('  %5s席  %-34s' % (c if c else '不明', (e.get('artist') or e.get('name') or '')[:34]))
    print('           会場 %s' % (e.get('venue') or '')[:60])
    if hit:
        print('           （%s で照合）' % hit)
