# -*- coding: utf-8 -*-
import io, json, sys
root = 'C:/Users/user/oshinavi/'
sys.path.insert(0, root + 'tools')
import compact_events as C
E = C.load(io.open(root + 'index.html', encoding='utf-8', newline='').read())
want = {1934, 13131, 4349, 29800}
o = io.open(root + 'tmp/x1123/spot/peek2.txt', 'w', encoding='utf-8')
for e in E:
    if e.get('id') in want:
        o.write(json.dumps({k: e.get(k) for k in ('id', 'artist', 'name', 'date', 'dateLabel', 'venue', 'links', 'tickets')}, ensure_ascii=False, indent=1) + '\n\n')
