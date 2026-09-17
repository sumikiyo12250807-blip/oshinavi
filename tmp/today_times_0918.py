# -*- coding: utf-8 -*-
# 本日発売の時刻を集計する（昼・午後のアラーム時刻を決めるため）
import re, json, sys, datetime, io
TODAY = datetime.date.today().isoformat()
src = open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'const EVENTS = (\[.*?\]);\n', src, re.S).group(1))
times = {}
for e in ev:
    for t in e.get('tickets', []):
        if t.get('soldout'):
            continue
        if t.get('startDate') != TODAY:
            continue
        m = re.search(r'(\d{1,2}):(\d{2})\s*発売', t.get('type', ''))
        hm = f"{int(m.group(1)):02d}:{m.group(2)}" if m else '時刻なし'
        times.setdefault(hm, []).append((e['id'], e.get('artist', '')[:26]))
out = io.open('tmp/today_times_0918.txt', 'w', encoding='utf-8')
out.write(f"=== 本日発売({TODAY})の時刻別 ===\n")
for hm in sorted(times):
    rows = times[hm]
    out.write(f"{hm}  {len(rows)}枠\n")
    for r in rows[:8]:
        out.write(f"    id{r[0]} {r[1]}\n")
    if len(rows) > 8:
        out.write(f"    …ほか{len(rows)-8}枠\n")
out.close()
print('ok')
