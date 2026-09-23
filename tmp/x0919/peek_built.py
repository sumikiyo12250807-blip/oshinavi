import json, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(open('tmp/x0919/built_tiget_all.json', encoding='utf-8'))
print(type(d), len(d) if isinstance(d, list) else list(d.keys())[:10])
items = d if isinstance(d, list) else d.get('entries') or d.get('built')
e = items[0]
print(json.dumps(e, ensure_ascii=False)[:1500])
print(collections.Counter(x.get('genre') for x in items).most_common(20))
print('past', sum(1 for x in items if x.get('date','') < '2026-09-19'))
