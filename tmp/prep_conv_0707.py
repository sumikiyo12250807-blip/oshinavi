# -*- coding: utf-8 -*-
"""変換対象15件の候補JSONを作る(build_pia_entries入力用)。"""
import re, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
CONV = [799,1156,1247,1291,1500,1572,1747,1831,1832,1833,1834,1984,1985,1986,1988]
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
byid = {e['id']: e for e in EVENTS}
cands = []
for i in CONV:
    e = byid[i]
    urls = []
    lp = (e.get('links') or {}).get('pia')
    if lp: urls.append(lp)
    for t in e.get('tickets', []):
        u = t.get('url')
        if u and u not in urls and 'pia' in u:
            urls.append(u)
    cands.append({"newid": i, "artist": e.get('artist') or e.get('title'), "urls": urls})
json.dump(cands, open('tmp/cand_conv_0707.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print(f"wrote {len(cands)} candidates")
for c in cands:
    print(c['newid'], c['artist'][:30], len(c['urls']), 'urls')
