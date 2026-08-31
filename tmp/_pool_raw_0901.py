# -*- coding: utf-8 -*-
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
src = open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'const EVENTS = (\[.*?\]);\n', src, re.S).group(1))
for e in ev:
    if e.get('id') in (5991, 5996, 6024):
        print(json.dumps(e, ensure_ascii=False, indent=1)[:1600]); print('-----')
