# -*- coding: utf-8 -*-
# 大相撲 冬巡業の、いま買える座席の枠（弁当・土産・駐車だけの枠は外す）を公演日順に
import io, sys, re
sys.path.insert(0, 'C:/Users/user/oshinavi/tools')
import compact_events as C
E = C.load(io.open('C:/Users/user/oshinavi/index.html', encoding='utf-8', newline='').read())
out = io.open('C:/Users/user/oshinavi/tmp/x1122/x/trend2_1123.txt', 'w', encoding='utf-8')
rows = []
for e in E:
    n = e.get('name') or ''
    if e.get('genre') == 'new' or '大相撲' not in n or '巡業' not in n:
        continue
    ts = [t for t in e.get('tickets') or [] if (t.get('date') or '') >= '2026-11-22' and not t.get('soldout')
          and not re.search(r'弁当|土産|駐車|お土産', t.get('type') or '') and not (t.get('startDate') or '') > '2026-11-22']
    if ts:
        rows.append((e.get('date'), e['id'], n, e.get('prefecture'), e.get('venue'), [(t.get('type'), t.get('date'), t.get('url', '')[:40]) for t in ts]))
rows.sort()
for r in rows:
    out.write('%s id%s %s ｜ %s ｜ %s\n   %s\n' % r)
out.write('計 %d\n' % len(rows))
print(len(rows))
