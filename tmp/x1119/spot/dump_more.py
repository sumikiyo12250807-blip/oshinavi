# -*- coding: utf-8 -*-
import io, json, sys
root = 'C:/Users/user/oshinavi/'
sys.path.insert(0, root + 'tools')
import compact_events as C
E = C.load(io.open(root + 'index.html', encoding='utf-8', newline='').read())
out = io.open(root + 'tmp/x1119/spot/dump_more.txt', 'w', encoding='utf-8')
for e in E:
    if e['id'] in (3533, 20300, 31834, 55779, 7520):
        out.write(json.dumps({k: e.get(k) for k in ('id', 'artist', 'name', 'date', 'dateLabel', 'venue', 'prefecture', 'links')}, ensure_ascii=False) + '\n')
