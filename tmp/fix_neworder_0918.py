# -*- coding: utf-8 -*-
# 削除した 9382・9506 を NEW_ORDER から外し、プールと配列が一致するか数える
import re, json
DEL = {9382, 9506}
h = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(const NEW_ORDER = )(\[[^\]]*\])(;)', h)
arr = json.loads(m.group(2))
before = len(arr)
arr2 = [i for i in arr if i not in DEL]
h2 = h[:m.start(2)] + json.dumps(arr2) + h[m.end(2):]
open('index.html', 'w', encoding='utf-8', newline='').write(h2)

# 突合
h3 = open('index.html', encoding='utf-8', newline='').read()
ev = json.loads(re.search(r'const EVENTS = (\[.*?\]);\n', h3, re.S).group(1))
pool = set(e['id'] for e in ev if e.get('genre') == 'new')
arr3 = set(json.loads(re.search(r'const NEW_ORDER = (\[[^\]]*\])', h3, re.S).group(1)))
print(f"NEW_ORDER {before} -> {len(arr2)} / 新着プール {len(pool)}")
print("配列にあるがプールに無い:", sorted(arr3 - pool))
print("プールにあるが配列に無い:", sorted(pool - arr3))
print("EVENTS件数:", len(ev))
