# -*- coding: utf-8 -*-
import io, json, sys
root = 'C:/Users/user/oshinavi/'
sys.path.insert(0, root + 'tools')
import compact_events as C
E = C.load(io.open(root + 'index.html', encoding='utf-8', newline='').read())
want = {40637, 20204, 22817, 37549, 2908, 54089, 23411}
o = io.open(root + 'tmp/x1123/spot/peek.txt', 'w', encoding='utf-8')
for e in E:
    if e.get('id') in want:
        o.write(json.dumps(e, ensure_ascii=False, indent=1) + '\n\n')
