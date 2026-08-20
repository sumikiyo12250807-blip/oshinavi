# -*- coding: utf-8 -*-
"""明日(2026-07-09)関連チケット抽出。
A=発売開始(「7/9 HH:MM発売」/〜無し)  B=最終受付(「〜7/9」締切)。"""
import re, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
TARGET = '2026-07-09'
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
GN = {'jpop': 'J-POP', 'rock': 'ROCK', 'kpop': 'K-POP', 'enka': '演歌・邦楽',
      'classic': 'クラシック', 'jazz': 'ジャズ', 'dento': '伝統芸能', 'fes': 'フェス',
      'owarai': 'お笑い', 'engeki': '演劇', 'musical': 'ミュージカル', 'kids': 'キッズ',
      'anime': 'アニメ', 'idol': 'アイドル', 'seiyuu': '声優', '2.5ji': '2.5次元',
      'art': 'イベントアート', 'hiphop': 'HIPHOP'}

EXCLUDE = {217}  # 英国ロイヤル ジゼル7/12=予定枚数終了(e+確認)で売切除外
A, B = [], []
seen_cd = set()
for e in EVENTS:
    if e['id'] in EXCLUDE:
        continue
    cd = ''
    mm = re.search(r'event(?:Bundle)?Cd=(\w+)', e['links'].get('pia') or '')
    if mm:
        cd = mm.group(1)
    for t in e.get('tickets', []):
        if t.get('date') != TARGET or '発売' not in t.get('type', ''):
            continue
        key = (cd, e['id'])
        if cd and cd in seen_cd:
            break
        tm = re.search(r'(\d{1,2}:\d{2})\s*(?:発売)?', t['type'])
        st = tm.group(1) if tm else ''
        rec = (e, t, st)
        if re.search(r'〜\s*7/9', t['type']):   # 「〜7/9」=締切のみB。公演日範囲の〜は無視
            B.append(rec)
        else:
            A.append(rec)
        if cd:
            seen_cd.add(cd)
        break

def dump(title, lst):
    print('\n========== %s = %d件 ==========' % (title, len(lst)))
    for e, t, st in sorted(lst, key=lambda x: (x[0].get('genre', ''), x[0]['artist'])):
        g = GN.get(e.get('genre', ''), e.get('genre', ''))
        print('■ %s【%s】' % (e['artist'], g))
        print('   %s' % e.get('dateLabel', ''))
        print('   %s' % t['type'])

dump('A 明日7/9 発売開始', A)
dump('B 明日7/9 最終受付(締切)', B)
print('\n合計 A=%d / B=%d' % (len(A), len(B)))
