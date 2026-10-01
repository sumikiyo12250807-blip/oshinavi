# -*- coding: utf-8 -*-
"""投稿ごと（ジャンルの束）に、10/2(金)・10/3(土)発売の行を出す（予告5件を箱の大きさで選ぶため）。"""
import sys, json
sys.path.insert(0, 'tmp/x1001/x')
import importlib.util
spec = importlib.util.spec_from_file_location('m', 'tmp/x1001/x/material_1002.py')
POSTS = {
 'post04': ['owarai'], 'post05': ['jpop', 'rock', 'utaite', 'vtuber', 'anime', 'fes', 'kpop', 'yougaku'], 'post06': ['idol'],
 'post07': ['classic', 'enka', 'dento', 'jazz', 'dinnershow'], 'post08': ['sports'],
 'post09': ['musical', 'engeki', 'aisatsu', 'talkshow', 'seiyuu', '2.5ji', 'movie'],
 'post10': ['dance', 'kids', 'fanevent', 'event', 'art', 'hanabi', 'musicetc', 'gakusai', 'circus', 'magic', 'douyou', 'gourmet'],
}
src = open('tmp/x1001/x/material_1002.py', encoding='utf-8').read()
src = src[:src.index("out = io.open(")]
ns = {}
exec(src, ns)
allg = set(g for v in POSTS.values() for g in v)
for d in ('2026-10-03', '2026-10-04'):
    rows = ns['collect'](d, False)
    other = sorted(set(r[4].get('genre') for r in rows) - allg)
    print('#####', d, '束に入らないジャンル:', other)
    for p, gs in POSTS.items():
        g = ns['group']([r for r in rows if r[4].get('genre') in gs])
        print('==', p, gs, '行', len(g), '→5行載せたら残り', ('全部載せる（残り0か1）' if len(g) <= 6 else ns['rough'](len(g) - 5)))
        for k, v in g.items():
            print('   ', ns['line'](k, v), '｜', ' / '.join(v['venues'][:2]), '｜id', v['ids'][0])
