# -*- coding: utf-8 -*-
import json, io, sys, shutil, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
txt = open('index.html', encoding='utf-8').read()
i = txt.index('const EVENTS = [') + len('const EVENTS = ')
arr, _ = json.JSONDecoder().raw_decode(txt, i)
byid = {e['id']: e for e in arr}
def tickets_block(tks):
    dumped = json.dumps(tks, ensure_ascii=False, indent=2); lines = dumped.split('\n')
    return lines[0] + '\n' + '\n'.join('    ' + l for l in lines[1:])
def replace_tickets(text, eid, newtks):
    e = byid[eid]; key = f'\n    "id": {eid},\n'; si = text.find(key)
    m = re.search(r'\n  \},?\n', text[si:]); ei = si + m.end(); span = text[si:ei]
    old = '"tickets": ' + tickets_block(e['tickets'])
    assert span.count(old) == 1, (eid, span.count(old))
    return text[:si] + span.replace(old, '"tickets": ' + tickets_block(newtks)) + text[ei:]
new = txt
new = replace_tickets(new, 296, [{'type':'当日引換券（大阪 6/19〜6/23公演）〜6/22 9:30','date':'2026-06-22'}])
new = replace_tickets(new, 372, [{'type':'先行販売〈特典付き〉（東京 7/17〜9/27公演）〜7/9 23:59','date':'2026-07-09'}])
shutil.copy('index.html','index.html.bak_0621_296_372')
open('index.html','w',encoding='utf-8').write(new)
print('OK patched 296 & 372')
