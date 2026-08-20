# -*- coding: utf-8 -*-
"""X投稿の候補抽出＝「明日(7/28)発売開始」の枠だけを機械で拾う。
   🚨 date は締切のことが多いので採用しない。startDate があるか、
      券種名に「M/D HH:MM発売」と明示されている枠だけを発売開始とみなす
      （memory: feedback_sale_start_vs_deadline）。
"""
import sys, io, re, json, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TARGET = datetime.date(2026, 7, 28)
MD = f'{TARGET.month}/{TARGET.day}'

src = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'const EVENTS = (\[.*?\n\s*\]);', src, re.S)
events = json.loads(m.group(1))

hits = []
for e in events:
    for t in e.get('tickets') or []:
        typ = t.get('type') or ''
        sd = t.get('startDate')
        explicit = re.search(rf'(?<!\d){re.escape(MD)}\s*\d{{1,2}}:\d{{2}}発売', typ)
        if (sd == TARGET.isoformat()) or explicit:
            hits.append((e, t, bool(explicit)))
            break

print(f'=== {TARGET} 発売開始の枠を持つエントリ {len(hits)}件 ===\n')
for e, t, ex in sorted(hits, key=lambda x: x[0].get('genre') or ''):
    links = e.get('links') or {}
    url = links.get('pia') or links.get('rakuten') or links.get('eplus') or links.get('lawson')
    print(f"[{e.get('genre')}] id{e['id']} {e['name']}")
    print(f"   公演: {e.get('dateLabel')}")
    print(f"   会場: {e.get('venue')}")
    print(f"   枠  : {t.get('type')}  (明示表記={ex})")
    print(f"   URL : {url}")
    print()
