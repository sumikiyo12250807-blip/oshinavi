# -*- coding: utf-8 -*-
"""ぴあビルド結果を「最も遠い締切」つきで一覧化（どれを50件に入れるか選ぶため）。"""
import json

d = json.load(open('tmp/built_pia_0730b.json', encoding='utf-8'))
rows = []
for e in d:
    ts = e.get('tickets') or []
    last = max((t.get('date') or '') for t in ts) if ts else ''
    first_start = min((t.get('startDate') or '9999') for t in ts) if ts else ''
    rows.append((last, e, first_start))
rows.sort(key=lambda x: x[0], reverse=True)

out = [f'エントリ {len(d)}件（最遅締切の遠い順）', '']
out.append('最遅締切   | 枠 | _genre     | id   | 名前')
out.append('-' * 100)
for last, e, fs in rows:
    out.append('{:<10} | {:>2} | {:<10} | {:<5}| {}'.format(
        last, len(e.get('tickets') or []), e.get('_genre') or '(空)', e['id'], (e.get('artist') or '')[:44]))

out.append('')
out.append('=== 枠の中身（全件） ===')
for last, e, fs in rows:
    out.append('')
    out.append(f"id={e['id']}  {(e.get('artist') or '')[:56]}   _genre={e.get('_genre') or '(空)'} _piaSub={e.get('_piaSub') or '(空)'}")
    out.append(f"  venue={e.get('venue')}  date={e.get('date')}")
    for t in e.get('tickets') or []:
        out.append(f"    {t.get('type')}   [date={t.get('date')} start={t.get('startDate')}]")
open('tmp/peek_built_pia_0730.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote tmp/peek_built_pia_0730.txt')
