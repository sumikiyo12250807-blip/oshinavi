# -*- coding: utf-8 -*-
"""明日(8/21)に発売が始まる枠を持つエントリを洗い出す（X投稿の候補出し）。
startDate == 明日 の枠を持ち、soldout でないもの。"""
import re, io, json, sys, datetime, collections
sys.stdout.reconfigure(encoding='utf-8')

TOM = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
h = io.open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))

rows = []
for e in EVENTS:
    hit = [t for t in (e.get('tickets') or [])
           if t.get('startDate') == TOM and not t.get('soldout')]
    if hit:
        rows.append((e, hit))

out = ["=== 明日 %s に発売開始する枠を持つエントリ %d件 ===" % (TOM, len(rows))]
for e, hit in sorted(rows, key=lambda x: x[0].get('genre') or ''):
    out.append("## id%s [%s] %s" % (e['id'], e.get('genre'), e.get('artist')))
    out.append("   %s / %s / 公演日 %s" % (e.get('venue'), e.get('prefecture'), e.get('date')))
    out.append("   pia: %s" % ((e.get('links') or {}).get('pia') or ''))
    for t in hit:
        out.append("   - %s" % t.get('type'))
    out.append("")
io.open('tmp/x_cand_0820.txt', 'w', encoding='utf-8').write("\n".join(out))
print("候補", len(rows), "件")
print(collections.Counter(e.get('genre') for e, _ in rows).most_common())
