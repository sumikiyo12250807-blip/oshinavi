# -*- coding: utf-8 -*-
"""inject_fany の要確認86件が、どの登録エントリに当たったかを出す（読むだけ・9/21夜）。"""
import io, json, re, sys
sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import inject_fany as F

built = json.load(open('tmp/built_fany_0921n.json', encoding='utf-8'))
built = built['entries'] if isinstance(built, dict) else built
h = io.open('index.html', encoding='utf-8', newline='').read()
EV = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
put, dup, maybe = F.classify(built, EV)
kinds = {}
for b, _ in maybe:
    na, nn, nv, d = F.norm(b.get('artist')), F.norm(b.get('name')), F.norm(b.get('venue')), b['date']
    hits = []
    for e in EV:
        if F.norm(e.get('venue')) != nv:
            continue
        if not ({F.norm(e.get('artist')), F.norm(e.get('name'))} & {na, nn}):
            continue
        ps = F._perfs(e)
        days = {e.get('date')} if ps else set(re.findall(r'\d{4}-\d{2}-\d{2}', json.dumps(e, ensure_ascii=False)))
        if d in days:
            hits.append((e['id'], e.get('genre'), 'FANY' if ps else 'other', F._evt(e), e.get('date'),
                         sorted(k for k, v in (e.get('links') or {}).items() if v)))
    kind = 'other' if any(x[2] == 'other' for x in hits) else 'fany-otherevt'
    kinds[kind] = kinds.get(kind, 0) + 1
    print(b['name'][:30], d, 'evt', F._evt(b), 'perf', sorted(F._perfs(b)))
    for x in hits:
        print('    ->', x)
print(kinds)
