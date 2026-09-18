# -*- coding: utf-8 -*-
"""保留していた89件（TIGETカテゴリ41「アニメ／ゲーム／声優」）を振り分ける（2026-09-18 夜）。

ユーザー指示＝「**声優の名前が出てるものだけseiyuuに分けて**」。

🚨名前だけで決めない＝**1人ずつWebSearchで裏を取った**（[[feedback_x_artist_fact_check]]）。
   声優と確認できたのは2人だけ。歌手・作曲家・クリエイターは anime に置く。
   裏が取れなかった人も anime に置く（[[feedback_no_speculation]]＝確信が無いほうに寄せない）。

   ✅藍原ことみ … アトミックモンキー所属の声優（アイドルマスター 一ノ瀬志希 ほか）
   ✅金月真美  … ときめきメモリアル 藤崎詩織役の声優
   ❌霜月はるか（シンガーソングライター）／松山あおい（アニソンシンガー）／
     有馬ゆみこ＝ex.関ゆみ子（ちびまる子ちゃん「ゆめいっぱい」の歌手）／小池雅也（作曲家・ギタリスト）
   ⚠️涼城えみ・花木みなと … 声優という裏が取れなかった＝anime

ℹ️TIGETには「2.5次元」が別カテゴリ(82)で存在する＝41番に2.5次元は混ざっていない。

  python tmp/x0919/assign_anime89.py [--apply]
"""
import collections
import datetime
import io
import json
import re
import sys

APPLY = '--apply' in sys.argv
SEIYUU_IDS = {12813, 12928}

h = io.open('index.html', encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

rows = []
for e in EVENTS:
    if e.get('genre') != 'new':
        continue
    g = 'seiyuu' if e['id'] in SEIYUU_IDS else 'anime'
    rows.append((e['id'], e.get('name'), g))
    if APPLY:
        e['genre'] = g
        for k in ('_genre', '_extraGenres', '_piaSub'):
            e.pop(k, None)

cnt = collections.Counter(g for _, _, g in rows)
print('振り分け %d件 %s' % (len(rows), dict(cnt)))

if APPLY:
    ids = {r[0] for r in rows}
    io.open('index.html.bak_0918_anime89', 'w', encoding='utf-8', newline='').write(h)
    mo = re.search(r'(NEW_ORDER\s*=\s*)\[([0-9,\s]*)\]', h)
    arr = [int(x) for x in re.findall(r'\d+', mo.group(2)) if int(x) not in ids]
    h2 = re.sub(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]',
                r'\g<1>' + '[' + ', '.join(map(str, arr)) + ']', h, count=1)
    m2 = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h2, re.S)
    io.open('index.html', 'w', encoding='utf-8', newline='').write(
        h2[:m2.start()] + m2.group(1)
        + json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
        + m2.group(3) + h2[m2.end():])
    pool = {e['id'] for e in EVENTS if e.get('genre') == 'new'}
    b = open('index.html', 'rb').read()
    print('プール %d / NEW_ORDER %d / 一致=%s / CRCRLF=%d 素のLF=%d'
          % (len(pool), len(arr), pool == set(arr),
             b.count(b'\r\r\n'), b.count(b'\n') - b.count(b'\r\n')))
    lg = io.open('logs/assigned_2026-09-18_anime.md', 'a', encoding='utf-8')
    lg.write('\n# TIGETカテゴリ41「アニメ／ゲーム／声優」の振り分け（%s・%d件）\n\n'
             % (datetime.date.today().isoformat(), len(rows)))
    lg.write('ユーザー「声優の名前が出てるものだけseiyuuに分けて」。'
             '名前はWebSearchで1人ずつ裏を取った。\n\n## seiyuu\n\n')
    for i, nm, g in rows:
        if g == 'seiyuu':
            lg.write('- id%d %s\n' % (i, nm))
    lg.write('\n## anime\n\n')
    for i, nm, g in rows:
        if g == 'anime':
            lg.write('- id%d %s\n' % (i, nm))
    lg.close()
