# -*- coding: utf-8 -*-
# 枠0の再照合でMISSINGが出たエントリを、ぴあから取り直すための候補jsonを作る
import re, json, io
IDS = [747, 1390, 2743, 4051, 4328, 4390, 4396, 4999, 5157, 7116, 7333, 7335, 7753]
h = open('index.html', encoding='utf-8', newline='').read()
ev = json.loads(re.search(r'const EVENTS = (\[.*?\]);', h, re.S).group(1))
by = {e['id']: e for e in ev}
cands = []
miss = []
for n, i in enumerate(IDS, start=1):
    e = by.get(i)
    if not e:
        miss.append(i)
        continue
    urls = []
    L = e.get('links') or {}
    if L.get('pia'):
        urls.append(L['pia'])
    for t in e.get('tickets', []):
        u = t.get('url') or ''
        if 'pia.jp' in u and u not in urls:
            urls.append(u)
    if not urls:
        miss.append(i)
        continue
    cands.append({'newid': 91000 + n, 'artist': e.get('artist', ''), 'urls': urls[:1], 'target': i})
io.open('tmp/cands_zero_0918.json', 'w', encoding='utf-8').write(
    json.dumps(cands, ensure_ascii=False, indent=1))
print('cands', len(cands), 'miss', miss)
