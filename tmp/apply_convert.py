# -*- coding: utf-8 -*-
"""proposal.json の72件を index.html に適用。各エントリのid範囲内でticketsブロックを置換。"""
import json, io, sys, shutil, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
txt = open('index.html', encoding='utf-8').read()
i = txt.index('const EVENTS = [') + len('const EVENTS = ')
arr, _ = json.JSONDecoder().raw_decode(txt, i)
byid = {e['id']: e for e in arr}
prop = json.load(open('tmp/proposal.json', encoding='utf-8'))

def tickets_block(tks):
    dumped = json.dumps(tks, ensure_ascii=False, indent=2)
    lines = dumped.split('\n')
    return lines[0] + '\n' + '\n'.join('    ' + l for l in lines[1:])

new_txt = txt
applied = 0; problems = []
for eid_s, p in prop.items():
    eid = int(eid_s)
    e = byid[eid]
    # locate entry span by id key
    key = f'\n    "id": {eid},\n'
    si = new_txt.find(key)
    if si < 0:
        problems.append((eid, 'id-not-found')); continue
    # entry end = next '\n  },' or '\n  }\n' at 2-space indent after si
    m = re.search(r'\n  \},?\n', new_txt[si:])
    if not m:
        problems.append((eid, 'end-not-found')); continue
    ei = si + m.end()
    span = new_txt[si:ei]
    old_block = '"tickets": ' + tickets_block(e['tickets'])
    if span.count(old_block) != 1:
        problems.append((eid, 'span-count-'+str(span.count(old_block)))); continue
    newtks = []
    for t in p['new']:
        d = {'type': t['type']}
        if t.get('sd'): d['startDate'] = t['sd']
        d['date'] = t['date']
        newtks.append(d)
    new_block = '"tickets": ' + tickets_block(newtks)
    new_span = span.replace(old_block, new_block)
    new_txt = new_txt[:si] + new_span + new_txt[ei:]
    applied += 1

print('applied', applied, '/', len(prop))
if problems:
    print('PROBLEM:', problems)
else:
    shutil.copy('index.html', 'index.html.bak_0621_morning_presale_convert')
    open('index.html', 'w', encoding='utf-8').write(new_txt)
    print('WROTE index.html (backup: index.html.bak_0621_morning_presale_convert)')
