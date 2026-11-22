# -*- coding: utf-8 -*-
# 11/23 発売の主役候補（布袋寅泰・いれいす・梶裕貴・好井まさお）のカードの中身
import io, json, sys
sys.path.insert(0, 'C:/Users/user/oshinavi/tools')
import compact_events as C
X = 'C:/Users/user/oshinavi/tmp/x1122/x/'
P = json.load(io.open(X + 'pick_1123.json', encoding='utf-8'))
E = {e['id']: e for e in C.load(io.open('C:/Users/user/oshinavi/index.html', encoding='utf-8', newline='').read())}
keys = ['布袋', 'いれいす', '梶裕貴', '好井まさお']
out = io.open(X + 'shu_1123.txt', 'w', encoding='utf-8')
for k in keys:
    out.write('##### %s\n' % k)
    for p in P:
        if k in ((p['artist'] or '') + (p['name'] or '')):
            e = E[p['id']]
            out.write(json.dumps({kk: e.get(kk) for kk in ('id', 'name', 'artist', 'genre', 'extraGenres', 'prefecture', 'venue', 'date', 'dateText', 'url', 'tickets')}, ensure_ascii=False) + '\n\n')
out.close()
print('ok')
