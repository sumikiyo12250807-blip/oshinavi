# -*- coding: utf-8 -*-
"""削除候補31件が実際にsoldout表示になっているか確認する"""
import io, json, re, sys

IDS = [130,1071,2223,2341,2401,2415,2416,2642,2815,2882,2916,2997,3287,3513,3594,
       3649,3651,3743,3766,3872,3875,3896,3899,3912,3922,3931,3937,4095,4319,4326,4334]

raw = io.open('index.html', 'r', encoding='utf-8', newline='').read()
m = re.search(r'const EVENTS\s*=\s*(\[.*?\]);\s*\n', raw, re.S)
if not m:
    print('EVENTS not found'); sys.exit(1)
events = json.loads(m.group(1))
by_id = {e['id']: e for e in events}

for i in IDS:
    e = by_id.get(i)
    if e is None:
        print('%-5d MISSING' % i); continue
    ts = e.get('tickets') or []
    n_sold = sum(1 for t in ts if t.get('soldout'))
    print('%-5d 枠%d soldout%d date=%s %s' % (i, len(ts), n_sold, e.get('date'), e.get('artist','')[:24]))
