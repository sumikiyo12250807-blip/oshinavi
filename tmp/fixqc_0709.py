# -*- coding: utf-8 -*-
"""7/9 新着QC修正: 空カッコ会場2件(2277/2283)実会場埋め + 重複ticket集約(2280)。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--apply' not in sys.argv
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
byid = {e['id']: e for e in EVENTS}
log = []

# 1) 空カッコ会場
byid[2277]['venue'] = '全国ツアー（セルリアンタワー能楽堂／金剛能楽堂）'
log.append('2277 venue -> ' + byid[2277]['venue'])
byid[2283]['venue'] = '全国ツアー（大須演芸場／近鉄アート館）'
log.append('2283 venue -> ' + byid[2283]['venue'])

# 2) 重複ticket集約 (type+date+startDate完全一致を1つに)
e = byid[2280]
seen, uniq = set(), []
for t in e['tickets']:
    k = (t.get('type'), t.get('date'), t.get('startDate'))
    if k in seen:
        continue
    seen.add(k); uniq.append(t)
log.append('2280 tickets %d -> %d' % (len(e['tickets']), len(uniq)))
e['tickets'] = uniq

for l in log:
    print(' ', l)
if DRY:
    print('(DRY)')
else:
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open('index.html.bak_0709_fixqc', 'w', encoding='utf-8').write(h)
    open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
    print('written (backup: index.html.bak_0709_fixqc)')
