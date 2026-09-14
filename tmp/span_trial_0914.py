# -*- coding: utf-8 -*-
"""build_pia_entries の会期を「これから行われる全公演」から作る直し（span_rows）を、実ページで試す（2026-09-14 夜）。
登録済みのエントリを、そのぴあURLで組み立て直し、会期の欄（date・dateLabel・venue・prefecture）と枠の数を登録と並べる。
書き込みはしない。ぴあは1件ずつ。
使い方: python tmp/span_trial_0914.py 9855,3406
"""
import io
import json
import re
import sys

sys.path.insert(0, 'tools')
import build_pia_entries as B
import heal_stale_deadlines as H

sys.stdout.reconfigure(encoding='utf-8')
src = io.open('index.html', encoding='utf-8').read()
by = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))}
for i in [int(x) for x in sys.argv[1].split(',')]:
    e = by[i]
    urls = H.pia_urls(e)
    cand = {'newid': i, 'artist': e.get('artist') or e.get('name'), 'urls': urls}
    o = B.build(cand)
    print('## id%s %s（ぴあURL %d本）' % (i, e.get('name'), len(urls)))
    for k in ('date', 'dateLabel', 'venue', 'prefecture'):
        a, b = e.get(k), (o or {}).get(k)
        print('  %-10s 登録 %s\n  %-10s 新   %s%s' % (k, a, '', b, '' if a == b else '   ←違う'))
    print('  枠の数    登録 %d ／ 新 %d（枠は買える行だけ＝今までと同じ作り）' % (len(e.get('tickets') or []), len((o or {}).get('tickets') or [])))
    reg = {(H.base_type(t.get('type')), t.get('date')) for t in e.get('tickets') or []}
    for t in (o or {}).get('tickets') or []:
        if (H.base_type(t.get('type')), t.get('date')) not in reg:
            print('  ＋登録に無い枠 %s ｜締切 %s｜発売 %s｜%s' % (t.get('type'), t.get('date'), t.get('startDate') or '-', H._url_id(t.get('url'))))
