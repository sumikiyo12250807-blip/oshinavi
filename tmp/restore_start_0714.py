# -*- coding: utf-8 -*-
"""2回目ヒールで消えた「発売開始日」を、ヒール直前のバックアップから復旧する。
（heal_stale_deadlines.py に carry_start_dates を入れる前に適用した20件が対象）"""
import io, json, re, sys, shutil
sys.path.insert(0, 'tools')
from heal_stale_deadlines import carry_start_dates, load_events

BAK = 'index.html.bak_0714_heal_stale'   # 2回目ヒール直前＝startDate がまだ生きている状態

old_h = io.open(BAK, encoding='utf-8').read()
_, old_ev = load_events(old_h)
old = {e['id']: e for e in old_ev}

cur_h = io.open('index.html', encoding='utf-8').read()
m, cur_ev = load_events(cur_h)

total = 0
hit = []
for e in cur_ev:
    o = old.get(e.get('id'))
    if not o:
        continue
    n = carry_start_dates(o.get('tickets'), e.get('tickets'))
    if n:
        total += n
        hit.append((e['id'], e.get('name', ''), n))

shutil.copy('index.html', 'index.html.bak_0714_restore_start')
new_arr = json.dumps(cur_ev, ensure_ascii=False, indent=2)
io.open('index.html', 'w', encoding='utf-8').write(
    cur_h[:m.start()] + m.group(1) + new_arr + m.group(3) + cur_h[m.end():])

with io.open('tmp/restore_start_0714.txt', 'w', encoding='utf-8') as f:
    f.write('発売日を復旧 %d枠 / %dエントリ\n' % (total, len(hit)))
    for i, n, c in hit:
        f.write('  id=%d %s (%d枠)\n' % (i, n, c))
print('done')
