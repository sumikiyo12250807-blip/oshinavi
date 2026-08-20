# -*- coding: utf-8 -*-
"""id4176 に取りこぼしていた枠を足す（ぴあが後から出した抽選受付）。
券種名はぴあの statustext「近日抽選受付」に忠実に「抽選受付」とする（推測の種別名を作らない）。
"""
import re, json, io, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

built = json.load(io.open('tmp/entries_4176.json', encoding='utf-8'))[0]
assert built['id'] == 4176

tickets = []
for t in built['tickets']:
    ty = t['type']
    # build はぴあの券種名（＝公演名）をそのまま拾うので、ぴあの状態文言に合わせて言い換える
    if ty.startswith('沖仁（'):
        ty = ty.replace('沖仁（', '抽選受付（', 1)
    t = dict(t)
    t['type'] = ty
    tickets.append(t)

h = io.open('index.html', encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
e = [x for x in EVENTS if x['id'] == 4176][0]
print('BEFORE tickets=%d genre=%s' % (len(e.get('tickets') or []), e.get('genre')))
for k in ('name', 'artist', 'date', 'dateLabel', 'venue', 'prefecture', 'verified', 'verifiedAt'):
    e[k] = built[k]
e['tickets'] = tickets
links = e.get('links') or {}
links['pia'] = built['links']['pia']
for k, v in (built.get('links') or {}).items():
    if v and not links.get(k):
        links[k] = v
e['links'] = links
print('AFTER  tickets=%d genre=%s' % (len(e['tickets']), e.get('genre')))
for t in e['tickets']:
    print('  枠|', t['type'])

bak = 'index.html.bak_%s_fix4176' % datetime.date.today().strftime('%m%d')
io.open(bak, 'w', encoding='utf-8', newline='').write(h)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
io.open('index.html', 'w', encoding='utf-8', newline='').write(
    h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print('適用完了 (backup %s)' % bak)
