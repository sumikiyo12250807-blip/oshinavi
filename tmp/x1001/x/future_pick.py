# -*- coding: utf-8 -*-
"""予告（10/3(土)・10/4(日)発売）に載せる5件を、箱の大きさで選んだ id から行を作る → future_pick.json
 行は material_1002 の group/line をそのまま使う（並びは時刻順）。残りの件数は rough()（四捨五入・X_SCRIPT 3番）。
 残りが1件ならその1件もリストに足す（X_SCRIPT 3番）。"""
import io, json, sys
sys.path.insert(0, 'tmp/x1001/x')
src = open('tmp/x1001/x/material_1002.py', encoding='utf-8').read()
ns = {}
exec(src[:src.index("out = io.open(")], ns)
POSTS = {
 'post04': ['owarai'], 'post05': ['jpop', 'rock', 'utaite', 'vtuber', 'anime', 'fes', 'kpop', 'yougaku'], 'post06': ['idol'],
 'post07': ['classic', 'enka', 'dento', 'jazz', 'dinnershow'], 'post08': ['sports'],
 'post09': ['musical', 'engeki', 'aisatsu', 'talkshow', 'seiyuu', '2.5ji', 'movie'],
 'post10': ['dance', 'kids', 'fanevent', 'event', 'art', 'hanabi', 'musicetc', 'gakusai', 'circus', 'magic', 'douyou', 'gourmet'],
}
PICK = {  # 箱の大きい順に選んだ id（None＝全部載せる）
 'post04': {'2026-10-03': [3491, 4839, 20083, 20221, 7836], '2026-10-04': [20074, 26977, 18641, 22718, 24373]},
 'post05': {'2026-10-03': [3051, 4052, 21210, 5656, 3422], '2026-10-04': [4373, 756, 5349, 5348, 26882]},
 'post06': {'2026-10-03': [21162, 21168, 21161, 21165, 26388], '2026-10-04': [25078, 25118, 12826, 25621, 25216]},
 'post07': {'2026-10-03': [7300, 23681, 4364, 5396, 3406], '2026-10-04': [7012, 7896, 11291, 5401, 27078]},
 'post08': {'2026-10-03': [27011, 23657, 24175, 26993, 27000], '2026-10-04': None},
 'post09': {'2026-10-03': [5391, 8592, 356, 5388, 27017], '2026-10-04': [3161, 4350, 5398, 5400, 6524]},
 'post10': {'2026-10-03': [2949, 5476, 9400, 13820, 7091], '2026-10-04': None},
}
FUT = {}
for p, gs in POSTS.items():
    FUT[p] = {}
    for d in ('2026-10-03', '2026-10-04'):
        g = ns['group']([r for r in ns['collect'](d, False) if r[4].get('genre') in gs])
        ids = PICK[p][d]
        keep = [(k, v) for k, v in g.items() if ids is None or set(v['ids']) & set(ids)]
        rest = len(g) - len(keep)
        if rest == 1:
            keep = list(g.items()); rest = 0
        FUT[p][d] = {'lines': [ns['line'](k, v) for k, v in keep], 'rest': ns['rough'](rest) if rest else ''}
        if ids and len(keep) != len(ids):
            print('!! 選んだ数と行の数が違う', p, d, len(ids), len(keep))
json.dump(FUT, io.open('tmp/x1001/x/future_pick.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for p in FUT:
    for d in FUT[p]:
        print(p, d, len(FUT[p][d]['lines']), FUT[p][d]['rest'])
