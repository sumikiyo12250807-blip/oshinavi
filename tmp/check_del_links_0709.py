# -*- coding: utf-8 -*-
import re, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DEL = [138,157,402,878,957,1316,1320,1326,1330,1448,1588,1589,1646,1662,1687,1732,1846,1897,887]
h = open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', h, re.S).group(1))
byid = {e['id']: e for e in EVENTS}
for i in DEL:
    e = byid.get(i)
    if not e:
        print(i, "MISSING"); continue
    links = e.get('links') or {}
    nonpia = {k: v for k, v in links.items() if v and 'pia' not in str(v)}
    tv = [t.get('vendor') or ('rakuten' if 'rakuten' in (t.get('url') or '') else 'eplus' if 'eplus' in (t.get('url') or '') else 'pia' if 'pia' in (t.get('url') or '') else '?') for t in e.get('tickets', [])]
    print(f"{i} | {e.get('artist','')[:24]} | date={e.get('date')} | links={list(links.keys())} | 非ぴあ={list(nonpia.keys())} | ticket_vendors={tv}")
