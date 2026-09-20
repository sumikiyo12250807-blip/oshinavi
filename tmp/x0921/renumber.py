# -*- coding: utf-8 -*-
"""ぴあ27件の id を仮番号(91000台)から本番の連番に振り直す。
投入直後（push前）にその場で直す＝[[feedback_candidate_list_stable_numbering]]。
index.html は投入前バックアップに戻してから入れ直す。
"""
import io, json, re, shutil, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

shutil.copy('index.html.bak_0921_piainj', 'index.html')
h = io.open('index.html', encoding='utf-8', newline='').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
lb = json.load(io.open('.claude/state/last_batch.json', encoding='utf-8'))['batches']
base = max([e['id'] for e in ev] + [b.get('id_to') or 0 for b in lb])
print('戻したindex.html＝%d件 / 次のidは %d から' % (len(ev), base + 1))

ent = json.load(io.open('tmp/x0921/entries.json', encoding='utf-8'))
for i, e in enumerate(sorted(ent, key=lambda x: x['id']), start=1):
    e['id'] = base + i
json.dump(ent, io.open('tmp/x0921/entries.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('id を %d〜%d に振り直した（%d件）'
      % (ent[0]['id'], ent[-1]['id'], len(ent)))
