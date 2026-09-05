# -*- coding: utf-8 -*-
import json, io
d = json.load(io.open('tmp/eplus_built.json', encoding='utf-8'))
io.open('tmp/raw1_0905.txt','w',encoding='utf-8').write(
    json.dumps(d[0], ensure_ascii=False, indent=1) + '\n----KEYS----\n' + ', '.join(sorted({k for e in d for k in e})))
print('OK')
