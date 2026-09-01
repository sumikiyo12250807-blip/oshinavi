# -*- coding: utf-8 -*-
"""残り3件のFAIL枠の登録内容を見る。"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
h = open('index.html', encoding='utf-8').read()
EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
by = {e['id']: e for e in EV}
for eid, ti in ((6012, 0), (5992, 15), (6190, 0)):
    e = by[eid]
    print(f'=== id{eid} {e.get("artist")} / 公演日 {e.get("date")} / 枠数 {len(e.get("tickets") or [])}')
    for j, t in enumerate(e.get('tickets') or []):
        mark = '★' if j == ti else ' '
        print(f'  {mark}t{j} date={t.get("date")} start={t.get("startDate")} '
              f'soldout={t.get("soldout")} saleEnded={t.get("saleEnded")} | {t.get("type")}')
    print()
