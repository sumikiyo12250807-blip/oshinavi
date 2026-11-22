import sys, json, re
sys.path.insert(0, 'C:/Users/user/oshinavi/tools')
import compact_events as C
E = C.load(open('C:/Users/user/oshinavi/index.html', encoding='utf-8', newline='').read())
print(len(E))
print(json.dumps(E[0], ensure_ascii=False)[:1500])
out = []
for e in E:
    for t in e.get('tickets', []) or []:
        sd = str(t.get('startDate') or '')
        ty = str(t.get('type') or '')
        hit = any(sd.startswith(d) for d in ('2026-11-23', '2026-11-24', '2026-11-25'))
        if not hit and re.search(r'11/2[345] ?\d\d:\d\d発売', ty):
            hit = True
        if hit:
            out.append({'id': e.get('id'), 'name': e.get('name'), 'artist': e.get('artist'),
                        'pref': e.get('pref') or e.get('prefecture'), 'venue': e.get('venue'),
                        'genre': e.get('genre'), 'date': e.get('date'), 't': t})
json.dump(out, open('C:/Users/user/oshinavi/tmp/x1122/x/fcx_dump.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('hits', len(out))
