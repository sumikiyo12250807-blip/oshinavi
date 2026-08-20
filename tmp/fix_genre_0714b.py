# -*- coding: utf-8 -*-
"""新着2バッチ目のジャンル下書き補正（_piaSub空→engeki誤フォールバック）。
2655 The Cribs（UKロックバンド）→ yougaku
2693 銀河特急ミルキー☆サブウェイ展（PARCO展覧会）→ art
2694 特別展「生きものたちの性」（国立科学博物館）→ art
2695 伊豆長岡温泉花火大会 狩野川まつり → hanabi
"""
import io, re, json, shutil

FIX = {2655: 'yougaku', 2693: 'art', 2694: 'art', 2695: 'hanabi'}

shutil.copy('index.html', 'index.html.bak_0714b_genre')
src = io.open('index.html', encoding='utf-8').read()

done = []
for eid, g in FIX.items():
    idx = src.find('"id": %d,' % eid)
    assert idx != -1, 'id%d not found' % eid
    gpos = src.find('"_genre": "', idx)
    assert gpos != -1 and gpos - idx < 800, 'genre id%d' % eid
    end = src.find('"', gpos + len('"_genre": "'))
    old = src[gpos + len('"_genre": "'):end]
    src = src[:gpos] + '"_genre": "%s"' % g + src[end + 1:]
    done.append((eid, old, g))

io.open('index.html', 'w', encoding='utf-8').write(src)

m = re.search(r'const EVENTS = (\[.*?\n\]);', src, re.S)
ev = json.loads(m.group(1))
d = {e['id']: e for e in ev}
with io.open('tmp/fix_genre_0714b.txt', 'w', encoding='utf-8') as f:
    for eid, old, g in done:
        f.write('id=%d %s : %s → %s\n' % (eid, d[eid]['name'][:40], old, d[eid]['_genre']))
print('done')
