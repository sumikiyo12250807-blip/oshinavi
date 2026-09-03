# -*- coding: utf-8 -*-
"""直近の新着投入実績を日別に集計（ASCIIだけコンソールへ／詳細はtxtへ）。"""
import json, io, collections

d = json.load(io.open('.claude/state/last_batch.json', encoding='utf-8'))
per_day = collections.OrderedDict()
lines = []
for b in d['batches']:
    day = b.get('date')
    per_day.setdefault(day, 0)
    per_day[day] += (b.get('count') or 0)
    lines.append("%s %-16s id %s-%s count=%s assigned=%s rechecked=%s\n    src=%s\n    note=%s" % (
        day, b.get('slot'), b.get('id_from'), b.get('id_to'), b.get('count'),
        b.get('assigned'), b.get('rechecked'), b.get('source'), (b.get('note') or '')[:300]))
io.open('tmp/batch_stats_0904.txt', 'w', encoding='utf-8').write("\n".join(lines))

days = list(per_day.items())[-10:]
for day, c in days:
    print("%s TOTAL=%d" % (day, c))
