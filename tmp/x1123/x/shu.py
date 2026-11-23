# -*- coding: utf-8 -*-
# 11/24 発売の主役候補とトレンド候補（Snow Man）のカードの中身
import io, json, sys
sys.path.insert(0, 'C:/Users/user/oshinavi/tools')
import compact_events as C
X = 'C:/Users/user/oshinavi/tmp/x1123/x/'
P = json.load(io.open(X + 'pick_1124.json', encoding='utf-8'))
E = {e['id']: e for e in C.load(io.open('C:/Users/user/oshinavi/index.html', encoding='utf-8', newline='').read())}
keys = ['NMB48', '工藤静香', '一之輔', '奇妙礼太郎', 'DEEN', 'DRUM TAO', '小瀧望', '野村萬斎']
out = io.open(X + 'shu_1124.txt', 'w', encoding='utf-8')
KEEP = ('id', 'name', 'artist', 'genre', 'extraGenres', 'prefecture', 'venue', 'date', 'dateLabel', 'links', 'tickets')
for k in keys:
    out.write('##### %s\n' % k)
    seen = set()
    for p in P:
        if k in ((p['artist'] or '') + (p['name'] or '')) and p['id'] not in seen:
            seen.add(p['id'])
            e = E[p['id']]
            out.write(json.dumps({kk: e.get(kk) for kk in KEEP}, ensure_ascii=False) + '\n\n')
out.write('##### トレンド候補 Snow Man\n')
out.write(json.dumps({kk: E[55328].get(kk) for kk in KEEP}, ensure_ascii=False) + '\n')
out.close()
