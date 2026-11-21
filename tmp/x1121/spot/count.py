# -*- coding: utf-8 -*-
# 11/21 番人 M を広げたあとの件数（登録済み・これからの公演）＋ 49334 の古い「記載なし」の記録を外す → 夜通しの取り直しの id
import collections, io, json, sys
root = 'C:/Users/user/oshinavi/'
sys.path.insert(0, root + 'tools')
NC = root + 'tools/artist_nocast.json'
nc = json.load(io.open(NC, encoding='utf-8'))
nc.pop('49334', None)
json.dump(nc, io.open(NC, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
import compact_events as C
import gate_fields as GF
TODAY = '2026-11-21'
E = C.load(io.open(root + 'index.html', encoding='utf-8', newline='').read())
ok = GF._artist_ok()
def vend(e):
    L = e.get('links') or {}
    return '/'.join(k for k, v in L.items() if v and k != 'amazon') or '?'
m = [e for e in E if e.get('genre') != 'new' and (e.get('date') or '') >= TODAY and GF.artist_looks_like_title(e, ok)]
out = io.open(root + 'tmp/x1121/spot/count.txt', 'w', encoding='utf-8')
out.write('登録済み・これからの公演で出演者が公演名のまま %d\n' % len(m))
for k, v in collections.Counter(vend(e) for e in m).most_common(15):
    out.write('   %s %d\n' % (k, v))
for i in (49334, 51168, 43144):
    out.write('%d 今は M に出る=%s\n' % (i, any(e['id'] == i for e in m)))
json.dump(sorted(e['id'] for e in m), io.open(root + 'tmp/x1121/spot/m_ids.json', 'w'), indent=0)
print(len(m))
