# -*- coding: utf-8 -*-
"""新着プール（genre:new）の素性を UTF-8 で書き出す。ぴあは叩かない。"""
import re, io, json

h = io.open('index.html', encoding='utf-8').read()
d = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
out = []
n = 0
for e in d:
    if e.get('genre') != 'new':
        continue
    n += 1
    out.append("## id%s %s" % (e['id'], e.get('artist')))
    out.append("   _genre(ぴあ由来): %s / _piaSub: %s" % (e.get('_genre'), e.get('_piaSub')))
    out.append("   venue: %s / date: %s / pref: %s" % (e.get('venue'), e.get('date'), e.get('prefecture')))
    for k, v in (e.get('links') or {}).items():
        if v and k != 'amazon':
            out.append("   link.%s: %s" % (k, v))
    for t in e.get('tickets') or []:
        out.append("   - %s | date=%s | start=%s" % (t.get('type'), t.get('date'), t.get('startDate')))
    out.append("")
io.open('tmp/newpool_0820.txt', 'w', encoding='utf-8').write("\n".join(out))
print("new entries:", n)
