# -*- coding: utf-8 -*-
"""9/3スイープの未掲載候補を仕分ける（9/2と同じ手順）。
 - URL重複を除く
 - name_in_db=True … 同名の既存あり＝統合行き（投入しない）
 - rlsdate が今日 … 本日発売＝除外（締切が取り込めず隠れ枠になる）
 - rlsdate が空 … 発売日が取れない＝保留
 - 残り … 本当に新規（ビルド対象）
出力: tmp/_triage_0903.json（4群）＋ tmp/_newcand_0903.json（ビルド候補）
"""
import json, glob, io, sys, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
TODAY = '2026/9/3'

rows = []
for p in sorted(glob.glob('tmp/_sw_*_0903.json')):
    d = json.load(open(p, encoding='utf-8'))
    for r in d.get('new') or []:
        r['_lg'] = d.get('lg')
        r['_status'] = d.get('base_filter')
        rows.append(r)

print('未掲載（重複込み）: %d件' % len(rows))
seen = {}
for r in rows:
    u = r.get('url')
    if u not in seen:
        seen[u] = r
uniq = list(seen.values())
print('URL重複を除く: %d件' % len(uniq))

samename, today, unknown, fresh = [], [], [], []
for r in uniq:
    if r.get('name_in_db'):
        samename.append(r)
    elif not (r.get('rlsdate') or '').strip():
        unknown.append(r)
    elif (r.get('rlsdate') or '').strip() == TODAY:
        today.append(r)
    else:
        fresh.append(r)

print('  同名の既存あり（統合行き）: %d件' % len(samename))
print('  本日発売（除外）          : %d件' % len(today))
print('  発売日が取れない（保留）  : %d件' % len(unknown))
print('  本当に新規（ビルド対象）  : %d件' % len(fresh))

json.dump({'samename': samename, 'today': today, 'unknown': unknown, 'fresh': fresh},
          open('tmp/_triage_0903.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

cand = [{'newid': None, 'artist': r.get('artist'), 'urls': [r.get('url')]} for r in fresh]
json.dump(cand, open('tmp/_newcand_0903.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('→ tmp/_triage_0903.json / tmp/_newcand_0903.json')
