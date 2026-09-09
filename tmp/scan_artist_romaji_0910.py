# -*- coding: utf-8 -*-
"""artist が「ローマ字だけの公演名」になっているエントリを洗い出す。

id4119 の型＝artist も name も「JUNICHI INAGAKI Christmas Dinner Show」。
日本人の公演なのに artist に日本語が1文字も無い＝「稲垣潤一」で検索しても出てこない。
検索候補は artist から作るので、ここが直撃する。
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

JP = re.compile(r'[ぁ-んァ-ヶ一-龥]')
SHOW = re.compile(r'(?i)dinner\s*show|christmas|concert|tour|live|recital|festival|special|'
                  r'anniversary|premium|birthday|presents|show\b')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
events = json.loads(m.group(2))

hit = []
for e in events:
    a = (e.get('artist') or '').strip()
    n = (e.get('name') or '').strip()
    if not a or a != n:
        continue
    if JP.search(a):          # 日本語が入っていれば名前で検索できる
        continue
    if not SHOW.search(a):    # 公演名らしい語が無ければ、ただの英語名アーティスト
        continue
    hit.append(e)

with open('tmp/artist_romaji_0910.txt', 'w', encoding='utf-8') as f:
    f.write('artist が「日本語ゼロ＋公演名らしい語」のエントリ: %d件\n' % len(hit))
    for e in sorted(hit, key=lambda x: x['id']):
        ls = e.get('links') or {}
        u = ls.get('pia') or ls.get('eplus') or ls.get('rakuten') or ls.get('lawson') or ''
        f.write('\nid=%-5s [%s] %s\n   %s\n' % (e['id'], e.get('genre'), e['artist'][:70], u))
print('候補 %d件 → tmp/artist_romaji_0910.txt' % len(hit))
