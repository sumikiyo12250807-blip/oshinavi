import sys, json, re
sys.path.insert(0, 'C:/Users/user/oshinavi/tools')
import compact_events as C
E = C.load(open('C:/Users/user/oshinavi/index.html', encoding='utf-8', newline='').read())
out = []
DAYS = ('2026-11-24', '2026-11-25', '2026-11-26')
for e in E:
    for t in e.get('tickets', []) or []:
        sd = str(t.get('startDate') or '')
        if sd[:10] in DAYS:
            ty = t.get('type') or ''
            m = re.search(r'(\d{1,2}:\d{2})発売', ty)
            art = (e.get('artist') or '')[:80]
            out.append((sd[:10], m.group(1) if m else '--', e.get('id'), (e.get('name') or '')[:70], art, e.get('prefecture') or '', e.get('genre'), ty[:120], t.get('date'), t.get('url')))
out.sort(key=lambda r: (r[0], r[1], str(r[2])))
with open('C:/Users/user/oshinavi/tmp/x1123/x/fcx_1124_list.txt', 'w', encoding='utf-8') as f:
    for r in out:
        f.write(' | '.join(str(x) for x in r) + '\n')
    f.write('keys sample: ' + json.dumps(list(E[0].keys()), ensure_ascii=False) + '\n')
print(len(out))
