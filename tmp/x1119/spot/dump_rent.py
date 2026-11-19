# -*- coding: utf-8 -*-
import io, json, sys
root = 'C:/Users/user/oshinavi/'
sys.path.insert(0, root + 'tools')
import compact_events as C
E = C.load(io.open(root + 'index.html', encoding='utf-8', newline='').read())
out = io.open(root + 'tmp/x1119/spot/dump_rent.txt', 'w', encoding='utf-8')
for e in E:
    if e['id'] in (2440, 40695, 28257):
        out.write(json.dumps(e, ensure_ascii=False, indent=1) + '\n\n')
