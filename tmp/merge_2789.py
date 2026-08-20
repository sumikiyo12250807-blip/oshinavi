# -*- coding: utf-8 -*-
"""id2789「ピオトル・アレクセヴィッチ（p）」と id3825「ピョートル・アレクセーヴィチ ピアノリサイタル」
の統合。ぴあ実ページで同一公演を確認済（浜離宮朝日ホール 12/3・一般発売〜12/2 23:59）。
2789 を残し、ぴあ正式表記・bundle URL・amazonリンクを 3825 から引き継いで 3825 を落とす。
書き戻しは heal_stale_deadlines と同じ方式（CRLFは open のテキストモードで保たれる）。
"""
import re, json, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
byid = {e['id']: e for e in EVENTS}

keep, drop = byid[2789], byid[3825]
assert keep['date'] == drop['date'] == '2026-12-03'
assert keep['venue'] == drop['venue']

keep['artist'] = drop['artist']
keep['name'] = drop['name']
keep['links']['pia'] = drop['links']['pia']
keep['links']['amazon'] = drop['links'].get('amazon')
keep['verifiedAt'] = datetime.date.today().isoformat()

EVENTS = [e for e in EVENTS if e['id'] != 3825]

bak = 'index.html.bak_%s_merge2789' % datetime.date.today().strftime('%m%d')
open(bak, 'w', encoding='utf-8').write(h)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print('統合完了: 2789 <= 3825 / 残り %d件 (backup: %s)' % (len(EVENTS), bak))
print('  name :', keep['name'])
print('  pia  :', keep['links']['pia'])
print('  枠   :', [t['type'] for t in keep['tickets']])
