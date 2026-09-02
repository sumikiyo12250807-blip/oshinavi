# -*- coding: utf-8 -*-
"""e+由来の新着（_genre を持たない）にジャンルの下書きを当てる。

e+ にはぴあのようなカテゴリが無いので「ぴあの言う通りに写す」が使えない
（feedback_genre_pia_asis_and_other は _piaSub がある時の話）。
名前と会場から機械で当てて、**別エージェントの独立判定と突合してから**確定する。
迷うものは振り分けずプールに残す（feedback_new_pool_ok_before_assign）。

  python tmp/eplus_genre_draft_0902.py          # 一覧を出すだけ
  python tmp/eplus_genre_draft_0902.py --apply  # _genre を書き込む
"""
import re, json, sys
sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
from build_pia_entries import genre_of

APPLY = '--apply' in sys.argv
src = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
EV = json.loads(m.group(2))

# 会場の型でも寄せる（e+はライブハウスが多い）
LIVEHOUSE = re.compile(
    r'LIVE|ライブ|Zepp|CLUB|クラブ|HALL(?! *of)|ホール$|O-EAST|O-WEST|O-nest|O-Crest|'
    r'WWW|Shelter|SHELTER|LOFT|ロフト|RUIDO|QUATTRO|クアトロ|BLITZ|Pangea|磔磔|'
    r'月見ル君想フ|獅子王|GUILTY|Spotify|WildSide|BlackHole|ReNY|二万電圧|7th Floor|'
    r'アリーナ|ドーム|スタジアム|Billboard|ビルボード')

rows = []
for e in EV:
    if e.get('genre') != 'new' or e.get('_genre'):
        continue
    nm = (e.get('artist') or '') + ' ' + (e.get('name') or '')
    vn = e.get('venue') or ''
    g = genre_of(nm)
    # 名前fallbackの既定は engeki。会場がライブハウス／音楽系なら音楽に寄せる
    if g == 'engeki' and LIVEHOUSE.search(vn):
        g = 'jpop'
    rows.append({'id': e['id'], 'artist': (e.get('artist') or '')[:44],
                 'venue': vn[:34], 'date': e.get('date'), 'g': g})

import collections
c = collections.Counter(r['g'] for r in rows)
print(f'e+の新着（下書きなし） {len(rows)}件')
for k, v in c.most_common():
    print(f'  {k:<10} {v}')
out = ['# e+新着のジャンル下書き（2026-09-02）', '',
       '| id | 公演名 | 会場 | 公演日 | 機械の下書き |', '|---|---|---|---|---|']
for r in sorted(rows, key=lambda x: x['id']):
    out.append(f"| {r['id']} | {r['artist']} | {r['venue']} | {r['date']} | {r['g']} |")
open('tmp/eplus_genre_draft_0902.md', 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
print('→ tmp/eplus_genre_draft_0902.md')

if APPLY:
    by = {r['id']: r['g'] for r in rows}
    for e in EV:
        if e['id'] in by:
            e['_genre'] = by[e['id']]
    nl = '\r\n' if '\r\n' in src else '\n'
    arr = json.dumps(EV, ensure_ascii=False, indent=2).replace('\r\n', '\n').replace('\n', nl)
    open('index.html.bak_0902_epgenre', 'w', encoding='utf-8', newline='').write(src)
    open('index.html', 'w', encoding='utf-8', newline='').write(
        src[:m.start()] + m.group(1) + arr + m.group(3) + src[m.end():])
    print(f'_genre を {len(by)}件に書き込んだ（backup: index.html.bak_0902_epgenre）')
