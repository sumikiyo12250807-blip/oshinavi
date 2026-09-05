# -*- coding: utf-8 -*-
import json, io, re
hh = io.open('index.html', encoding='utf-8', newline='').read()
db = {e['id']: e for e in json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', hh, re.S).group(1))}
with io.open('tmp/peek6944_0905.txt', 'w', encoding='utf-8') as f:
    for i in (6944, 583):
        e = db[i]
        f.write(json.dumps(e, ensure_ascii=False, indent=1) + '\n\n')
print('OK')
