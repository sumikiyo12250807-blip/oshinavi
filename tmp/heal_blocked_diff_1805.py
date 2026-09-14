# -*- coding: utf-8 -*-
"""18時のあとのヒールで止まった枠の中身を並べる（2026-09-14 夜）。
id ごとに「元にあって取り直しに無い枠（消える側）」と「取り直しにだけある枠（増える側）」を
券種名・締切・発売日・売り場の番号つきで出す。書き込みはしない。
使い方: python tmp/heal_blocked_diff_1805.py [id,id,...]   （省略時は tmp/heal_blocked_hold_1805.txt）
出力: tmp/heal_blocked_diff_1805.md
"""
import datetime
import io
import json
import re
import sys

sys.path.insert(0, 'tools')
import heal_stale_deadlines as H

sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'  const EVENTS = (\[.*?\]);', src, re.S)
by = {e['id']: e for e in json.loads(m.group(1))}
built = {o['id']: o for o in json.load(io.open('tmp/heal_ids.json', encoding='utf-8'))}
arg = sys.argv[1] if len(sys.argv) > 1 else io.open('tmp/heal_blocked_hold_1805.txt', encoding='utf-8').read()
ids = [int(x) for x in arg.split(',') if x.strip()]


def row(t):
    return '%s ｜締切 %s｜発売 %s｜%s%s' % (
        t.get('type'), t.get('date'), t.get('startDate') or '-', H._url_id(t.get('url')),
        '｜売り切れ' if t.get('soldout') else '')


out = []
for i in ids:
    e, o = by.get(i), built.get(i)
    if not e or not o:
        out.append('## id%s 取り直し無し（%s）\n' % (i, o and o.get('status')))
        continue
    old = [t for t in e.get('tickets') or [] if H.visible_slot(t, TODAY)]
    new = [t for t in o.get('tickets') or [] if H.visible_slot(t, TODAY)]
    ko = {H.slot_key(t) for t in old}
    kn = {H.slot_key(t) for t in new}
    out.append('## id%s %s（元 %d枠 → 取り直し %d枠）' % (i, e.get('name'), len(old), len(new)))
    out.append('消える側:')
    out += ['  - ' + row(t) for t in old if H.slot_key(t) not in kn]
    out.append('増える側:')
    out += ['  + ' + row(t) for t in new if H.slot_key(t) not in ko]
    out.append('')
io.open('tmp/heal_blocked_diff_1805.md', 'w', encoding='utf-8').write('\n'.join(out))
print('書き出し tmp/heal_blocked_diff_1805.md（%d件）' % len(ids))
