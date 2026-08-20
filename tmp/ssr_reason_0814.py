# -*- coding: utf-8 -*-
"""一部soldoutの6件がSSRに載らない理由を build_ai_page の実関数で確かめる。"""
import sys, datetime
sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import build_ai_page as B

today = datetime.date.today()
evs = B.extract_events_array('index.html')
ids = {1071, 1149, 1487, 2265, 2401, 3651, 3513, 2300}
for e in evs:
    if e.get('id') not in ids:
        continue
    na = B.next_action(e, today)
    print('id%-5s next_action=%s verified=%s' % (e.get('id'), na[:2] if na else None, e.get('verified')))
    for t in e.get('tickets') or []:
        print('    soldout=%-5s startDate=%-11s date=%-11s %s' % (
            bool(t.get('soldout')), t.get('startDate'), t.get('date'), (t.get('type') or '')[:44]))
