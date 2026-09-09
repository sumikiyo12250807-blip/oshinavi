# -*- coding: utf-8 -*-
"""楽天由来で「多会場なのに枠が1つ」＝締切を最終公演日に丸めている疑いのエントリを数える。"""
import io, re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

h = io.open('index.html', encoding='utf-8', newline='').read()
EV = json.loads(re.search(r'const EVENTS = (\[.*?\]);\r?\n', h, re.S).group(1))

def is_rakuten(e):
    blob = json.dumps(e, ensure_ascii=False)
    return 'ticket.rakuten.co.jp' in blob

rows = []
for e in EV:
    if not is_rakuten(e):
        continue
    tks = e.get('tickets') or []
    venues = (e.get('venue') or '')
    nven = venues.count('／') + 1 if '全国ツアー' in venues or '／' in venues else 1
    if len(tks) == 1 and nven >= 3:
        t = tks[0]
        rows.append((e['id'], (e.get('name') or '')[:34], nven, t.get('date'), e.get('date'),
                     (t.get('type') or '')[:40]))

print('楽天由来で「会場3つ以上なのに枠が1つ」= %d件' % len(rows))
print('%-7s %-36s %-5s %-12s %-12s' % ('id', '公演名', '会場数', '枠の締切', 'エントリの公演日'))
for i, name, nven, tdate, edate, ty in rows:
    mark = ' 🚨同じ' if tdate == edate else ''
    print('%-7s %-36s %-5s %-12s %-12s%s' % (i, name, nven, tdate, edate, mark))
print('\n🚨「枠の締切」と「エントリの公演日（＝千秋楽）」が同じものは、')
print('   実ページに終わりが書かれていないのに最終公演日を締切として作った疑いが濃い。')
