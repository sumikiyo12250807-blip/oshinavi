# -*- coding: utf-8 -*-
import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')
data = json.load(io.open('tools/x_log.json', encoding='utf-8'))['artists']['data']
print('n=%d' % len(data))
for x in data:
    print(json.dumps(x, ensure_ascii=False))
