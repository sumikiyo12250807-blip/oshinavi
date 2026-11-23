# -*- coding: utf-8 -*-
# 振り分け済みで <日付> に発売の受付があるエントリ → pick_MMDD.json ＋ 過去のフォロワー調べに無い名前 names_MMDD.txt ＋ ジャンル別の件数（x1121 の形）
import io, json, re, sys, collections, glob, os
sys.stdout.reconfigure(encoding='utf-8')
R = 'C:/Users/user/oshinavi/'
sys.path.insert(0, R + 'tools')
import compact_events as C
X = R + 'tmp/x1123/x/'
os.makedirs(X, exist_ok=True)
E = C.load(io.open(R + 'index.html', encoding='utf-8', newline='').read())
for D in sys.argv[1:]:
    tag = D[5:7] + D[8:10]
    P = []
    for e in E:
        if e.get('genre') == 'new':
            continue
        ts = [t for t in e.get('tickets') or [] if t.get('startDate') == D and not t.get('soldout')]
        if ts:
            m = re.search(r'(\d{1,2}:\d{2})発売', ts[0].get('type') or '')
            P.append({'id': e['id'], 'genre': e.get('genre'), 'extra': e.get('extraGenres') or [], 'artist': e.get('artist'), 'name': e.get('name'),
                      'pref': e.get('prefecture'), 'time': m.group(1) if m else '', 'type': ts[0].get('type')})
    json.dump(P, io.open(X + f'pick_{tag}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    known = {}
    for f in glob.glob(R + 'tmp/x11*/x/followers_*.json') + glob.glob(R + 'tmp/x10*/x/followers_*.json'):
        try:
            for r in json.load(io.open(f, encoding='utf-8')):
                if r.get('name'):
                    known[r['name']] = r
        except Exception:
            pass
    need = sorted({(p['artist'] or p['name']) for p in P} - set(known))
    io.open(X + f'names_{tag}.txt', 'w', encoding='utf-8').write('\n'.join(need))
    c = collections.Counter(p['genre'] for p in P)
    t = f'{D} 発売 {len(P)}件 {c.most_common()}\n既知のフォロワー {len(known)}名・調べる名前 {len(need)}\n'
    io.open(X + f'pick_{tag}.txt', 'w', encoding='utf-8').write(t)
    print(t)
