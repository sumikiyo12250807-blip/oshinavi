# -*- coding: utf-8 -*-
"""時刻欠FAILの5エントリについて、登録の枠と実ページのLD（公演日・時刻・会場・県）を並べる。
「同一会場・同日で開演時刻だけ違う」時にだけ時刻を入れる＝条件を確かめてから直す
（feedback_same_day_show_time_badge）。"""
import re, json, sys
sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
from eplus_harvest import fetch, parse_ld

IDS = [5994, 5996, 6013, 6014, 6019]
h = open('index.html', encoding='utf-8').read()
EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
by = {e['id']: e for e in EV}
cache = {}
for i in IDS:
    e = by[i]
    print(f"\n=== id{i} {e.get('artist')} / 公演日 {e.get('date')} / 会場 {e.get('venue')}")
    for ti, t in enumerate(e.get('tickets') or []):
        u = t.get('url') or ''
        if u and u not in cache:
            try:
                lds = parse_ld(fetch(u))
                cache[u] = lds[0] if lds else {}
            except Exception as ex:
                cache[u] = {'err': str(ex)[:40]}
        L = cache.get(u, {})
        print(f"  t{ti} | {t.get('type')}")
        print(f"       LD日={L.get('date')} 時刻={L.get('time')} 会場={L.get('venue')} 県={L.get('pref')}")
