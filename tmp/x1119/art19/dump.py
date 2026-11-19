# -*- coding: utf-8 -*-
import io, json, sys
root = 'C:/Users/user/oshinavi/'
sys.path.insert(0, root + 'tools')
import compact_events as C
E = C.load(io.open(root + 'index.html', encoding='utf-8', newline='').read())
want = {43373, 34053, 31191, 41733}
# 同じ名前の別カード（DAIBAKUSHOW の二部など）も拾う
keys = ['DAIBAKUSHOW', '阿佐ヶ谷姉妹 ミーツ', 'Plastic Tree', '広瀬香美']
out = io.open(root + 'tmp/x1119/art19/dump.txt', 'w', encoding='utf-8')
for e in E:
    nm = (e.get('name') or '') + ' ' + (e.get('artist') or '')
    if e['id'] in want or any(k in nm for k in keys):
        out.write(json.dumps(e, ensure_ascii=False, indent=1) + '\n\n')
