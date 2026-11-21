# -*- coding: utf-8 -*-
# 抜き打ちの🟠9件：出演者・売り場・m_ids.json に入っていたか
import io, json, sys
root = 'C:/Users/user/oshinavi/'
sys.path.insert(0, root + 'tools')
import compact_events as C
E = {e['id']: e for e in C.load(io.open(root + 'index.html', encoding='utf-8', newline='').read())}
M = set(json.load(io.open(root + 'tmp/x1120/spot/m_ids.json', encoding='utf-8')))
out = io.open(root + 'tmp/x1121/spot/peek.txt', 'w', encoding='utf-8')
for i in (36251, 47047, 43144, 49334, 54987, 47746, 29005, 51168, 55604):
    e = E[i]
    out.write('%d m_ids=%s | artist=%s | name=%s | pref=%s | links=%s | urls=%s\n' % (
        i, i in M, e.get('artist'), e.get('name'), e.get('prefecture'), json.dumps(e.get('links'), ensure_ascii=False),
        sorted(set((t.get('url') or '')[:60] for t in e.get('tickets') or []))))
