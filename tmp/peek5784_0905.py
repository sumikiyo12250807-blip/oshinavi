# -*- coding: utf-8 -*-
import json, io, re
hh = io.open('index.html', encoding='utf-8', newline='').read()
db = {e['id']: e for e in json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', hh, re.S).group(1))}
io.open('tmp/peek5784_0905.txt', 'w', encoding='utf-8').write(json.dumps(db[5784], ensure_ascii=False, indent=1))
print('OK')
