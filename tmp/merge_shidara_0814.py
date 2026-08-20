# -*- coding: utf-8 -*-
"""志多ら「つながる和太鼓 おもやひ」の岡崎(4231)・静岡(4232)を1エントリに統合。
ぴあ実ページで同一興行の2会場と確認済（2616813=愛知12/13 / 2616816=静岡2027-1/17・発売はどちらも9/12 10:00）。
（memory: feedback_tour_consolidate / feedback_tour_per_ticket_url＝別eventCd由来はticketごとにURL）
"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = json.loads(m.group(2))

a = next(e for e in EV if e['id'] == 4231)   # 岡崎（残す）
b = next(e for e in EV if e['id'] == 4232)   # 静岡（吸収）
print('統合前 4231:', a.get('name'), '/', a.get('dateLabel'))
print('統合前 4232:', b.get('name'), '/', b.get('dateLabel'))

# 各ticketに由来ページのURLを付ける（別eventCd由来＝multi扱い）
for t in a.get('tickets') or []:
    t['url'] = a['links']['pia']
for t in b.get('tickets') or []:
    t['url'] = b['links']['pia']

a['name'] = '志多ら つながる和太鼓 おもやひ'
a['artist'] = '志多ら'
a['venue'] = '全国ツアー（岡崎市民会館 あおいホール／グランシップ 中ホール・大地）'
a['prefecture'] = '愛知・静岡'
a['dateLabel'] = '2026年12月13日(日)〜2027年1月17日(日) 愛知・静岡'
a['date'] = '2027-01-17'          # 千秋楽
a['tickets'] = (a.get('tickets') or []) + (b.get('tickets') or [])

EV = [e for e in EV if e['id'] != 4232]
print('統合後 4231:', a['name'], '/', a['dateLabel'], '/ date=', a['date'])
for t in a['tickets']:
    print('   枠:', t.get('type'), '| url=', t.get('url'))

new_arr = json.dumps(EV, ensure_ascii=False, indent=2).replace('\n', NL)
h2 = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]

# NEW_ORDER から 4232 を落とす（欠番のまま詰めない＝他の番号は動かさない）
mo = re.search(r'(NEW_ORDER\s*=\s*)\[([0-9,\s]*)\]', h2)
cur = [int(x) for x in re.findall(r'\d+', mo.group(2))]
new_order = [i for i in cur if i != 4232]
h2, n = re.subn(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]',
                lambda mm: mm.group(1) + '[' + ', '.join(str(i) for i in new_order) + ']', h2, count=1)
assert n == 1
print('NEW_ORDER %d件 → %d件（4232を除去）' % (len(cur), len(new_order)))

open('index.html.bak_0814_shidara', 'w', encoding='utf-8', newline='').write(h)
open('index.html', 'w', encoding='utf-8', newline='').write(h2)
print('→ 適用（backup index.html.bak_0814_shidara）')
