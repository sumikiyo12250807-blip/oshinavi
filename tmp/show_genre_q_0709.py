# -*- coding: utf-8 -*-
import re, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
h = open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', h, re.S).group(1))
byid = {e['id']: e for e in EVENTS}
for i in [2144, 2240]:
    e = byid.get(i)
    if not e:
        print(i, "NOT FOUND"); continue
    print("====", i, e.get('artist'))
    print("  title:", e.get('title'))
    print("  genre:", e.get('genre'), "| extraGenres:", e.get('extraGenres'))
    print("  venue:", e.get('venue'), "| pref:", e.get('prefecture'), "| date:", e.get('date'))
    print("  pia:", (e.get('links') or {}).get('pia'))
    print("  desc:", (e.get('description') or '')[:200])
