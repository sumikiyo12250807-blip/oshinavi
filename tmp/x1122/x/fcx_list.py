import json, re
D = json.load(open('C:/Users/user/oshinavi/tmp/x1122/x/fcx_dump.json', encoding='utf-8'))
rows = []
for r in D:
    t = r['t']
    sd = str(t.get('startDate') or '')
    ty = str(t.get('type') or '')
    m = re.search(r'(\d\d?)/(\d\d?) ?(\d\d:\d\d)発売', ty)
    tm = ''
    if m:
        sd2 = '2026-%02d-%02d' % (int(m.group(1)), int(m.group(2)))
        tm = m.group(3)
        if not sd:
            sd = sd2
    else:
        m2 = re.search(r'(\d\d:\d\d)', sd)
        tm = m2.group(1) if m2 else '?'
    dom = re.sub(r'https?://([^/]+).*', r'\1', str(t.get('url') or ''))
    rows.append((sd[:10], tm, r['id'], str(r['artist'])[:60], str(r['name'])[:50], r['pref'], r['genre'], ty[:70], dom, t.get('startTime', '')))
rows.sort(key=lambda x: (x[0], x[1], str(x[6])))
with open('C:/Users/user/oshinavi/tmp/x1122/x/fcx_list.txt', 'w', encoding='utf-8') as f:
    for x in rows:
        f.write(' | '.join(str(v) for v in x) + '\n')
print(len(rows))
