# -*- coding: utf-8 -*-
# 11/23 発売の名前を、前に調べたフォロワー（followers_*.json）と部分一致で当てて多い順（x1121 rank_1122 の形）
import io, json, glob
R = 'C:/Users/user/oshinavi/'
X = R + 'tmp/x1122/x/'
P = json.load(io.open(X + 'pick_1123.json', encoding='utf-8'))
known = {}
for f in sorted(glob.glob(R + 'tmp/x10*/x/followers_*.json') + glob.glob(R + 'tmp/x11*/x/followers_*.json')):
    try:
        for r in json.load(io.open(f, encoding='utf-8')):
            if r.get('name') and isinstance(r.get('followers'), (int, float)) and r['followers']:
                known[r['name']] = r
    except Exception:
        pass
rows = []
for p in P:
    s = (p['artist'] or '') + ' ' + (p['name'] or '')
    best = None
    for n, r in known.items():
        if len(n) >= 2 and n in s and (best is None or r['followers'] > best['followers']):
            best = r
    if best:
        rows.append((best['followers'], best['name'], p['id'], p['genre'], p['time'], (p['name'] or '')[:40], (p['type'] or '')[:40]))
rows.sort(reverse=True)
out = io.open(X + 'rank_1123.txt', 'w', encoding='utf-8')
for r in rows[:60]:
    out.write('%9d %s ｜ id%s %s %s ｜ %s ｜ %s\n' % r)
need = io.open(X + 'names_1123.txt', encoding='utf-8').read()
out.write('\n--- 調べていない名前 ---\n' + need + '\n')
print(len(rows))
