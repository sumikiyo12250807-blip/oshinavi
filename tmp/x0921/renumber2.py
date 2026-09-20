# -*- coding: utf-8 -*-
"""組み上がりJSONの id を、いまのindex.htmlとlast_batchの最大idの次から振り直す。
  python tmp/x0921/renumber2.py tmp/x0921/entries_uke.json
"""
import io, json, re, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
src = sys.argv[1]
h = io.open('index.html', encoding='utf-8', newline='').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
lb = json.load(io.open('.claude/state/last_batch.json', encoding='utf-8'))['batches']
base = max([e['id'] for e in ev] + [b.get('id_to') or 0 for b in lb])

ent = json.load(io.open(src, encoding='utf-8'))
for i, e in enumerate(sorted(ent, key=lambda x: x['id']), start=1):
    e['id'] = base + i
json.dump(ent, io.open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('%s の id を %d〜%d に振り直した（%d件）' % (src, ent[0]['id'], ent[-1]['id'], len(ent)))
