# -*- coding: utf-8 -*-
"""B班の指摘に出たエントリの登録内容を見る（突合用）。"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
IDS = [6136, 6137, 6141, 6126, 6133, 6123, 6144, 6154, 6157, 6168, 6140, 6145, 6146]
h = open('index.html', encoding='utf-8').read()
EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
by = {e['id']: e for e in EV}
for i in IDS:
    e = by.get(i)
    if not e:
        print(f'id{i} 見つからない')
        continue
    print(f'=== id{i} {e.get("artist")}')
    print(f'    name={e.get("name")}')
    print(f'    venue={e.get("venue")} / date={e.get("date")} / pref={e.get("pref")} / _genre={e.get("_genre")}')
    print(f'    dateLabel={e.get("dateLabel")}')
    for j, t in enumerate(e.get('tickets') or []):
        print(f'    t{j} date={t.get("date")} start={t.get("startDate")} | {t.get("type")}')
        print(f'         {t.get("url")}')
    print()
