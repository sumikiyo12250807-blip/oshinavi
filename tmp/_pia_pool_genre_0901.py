# -*- coding: utf-8 -*-
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
src = open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'const EVENTS = (\[.*?\]);\n', src, re.S).group(1))
for e in ev:
    if e.get('genre')=='new' and (e.get('links') or {}).get('pia'):
        print(f"{e['id']}  _genre={e.get('_genre','')!s:10} _piaSub={e.get('_piaSub','')!s:22} extra={e.get('_extraGenres')} | {e.get('artist','')[:44]}")
