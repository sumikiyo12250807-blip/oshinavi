# -*- coding: utf-8 -*-
"""FANYの一覧JSONの構造を書き出す（販売枠の中身を確かめる）。"""
import io, json

d = json.load(open('tmp/fany_more0.json', encoding='utf-8'))
out = io.open('tmp/fany_shape.txt', 'w', encoding='utf-8')
p = d['performances'][0]
out.write('perf keys: %s\n\n' % sorted(p.keys()))
for k in ('id', 'event_id', 'venue_id', 'venue_name', 'name', 'class',
          'performance_date', 'valid_period_start_date', 'valid_period_finish_date',
          'opening_time', 'start_time', 'open_start_time_text', 'release_datetime'):
    out.write('  %s = %r\n' % (k, p.get(k)))
out.write('\nsales n=%d\n' % len(p.get('performance_sales', [])))
for s in p.get('performance_sales', []):
    out.write(json.dumps(s, ensure_ascii=False, indent=1) + '\n')
out.write('\n=== 2件目の販売枠 ===\n')
for s in d['performances'][1].get('performance_sales', []):
    out.write(json.dumps(s, ensure_ascii=False, indent=1) + '\n')
out.close()
print('wrote tmp/fany_shape.txt')
