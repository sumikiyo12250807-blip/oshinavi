# -*- coding: utf-8 -*-
import re, json

built = json.load(open('tmp/eplus_built.json', encoding='utf-8'))
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
maxid = max(e['id'] for e in EVENTS)
start = maxid + 1
newids = []
for i, e in enumerate(built):
    e['id'] = start + i
    newids.append(e['id'])
    EVENTS.append(e)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
h2 = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]

# NEW_ORDER 追記
mo = re.search(r'(const NEW_ORDER = )(\[[^\]]*\])(;)', h2)
cur = json.loads(mo.group(2))
cur = cur + newids
h2 = h2[:mo.start()] + mo.group(1) + json.dumps(cur) + mo.group(3) + h2[mo.end():]

open('index.html', 'w', encoding='utf-8').write(h2)
print('投入', len(built), '件 id', newids[0], '〜', newids[-1])
print('NEW_ORDER =', cur)
print('全件数', len(EVENTS))
