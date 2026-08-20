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
e = byid[640]
key = '\n    "id": 640,\n'; si = txt.find(key)
m = re.search(r'\n  \},?\n', txt[si:]); ei = si + m.end(); span = txt[si:ei]
old_t = '"tickets": ' + tickets_block(e['tickets'])
assert span.count(old_t) == 1
newtks = [{'type':'一般発売（広島 9/27公演）〜9/17 23:59','date':'2026-09-17',
           'url':'https://t.pia.jp/pia/event/event.do?eventCd=2621292'}]
span = span.replace(old_t, '"tickets": ' + tickets_block(newtks))
# scalar fields (unique within span)
reps = [
 ('"date": "2026-09-12"', '"date": "2026-09-27"'),
 ('"dateLabel": "2026年9月12日(土)埼玉／9月27日(日)広島"', '"dateLabel": "2026年9月27日(日)広島"'),
 ('"venue": "サンシティ越谷市民ホール 大ホール（埼玉）／東広島芸術文化ホールくらら 大ホール（広島）"', '"venue": "東広島芸術文化ホールくらら 大ホール（広島）"'),
 ('"prefecture": "全国"', '"prefecture": "広島"'),
 ('"pia": "https://t.pia.jp/pia/event/event.do?eventCd=2612463"', '"pia": "https://t.pia.jp/pia/event/event.do?eventCd=2621292"'),
]
for a,b in reps:
    assert span.count(a)==1, ('miss',a,span.count(a))
    span = span.replace(a,b)
new_txt = txt[:si] + span + txt[ei:]
shutil.copy('index.html','index.html.bak_0621_640')
open('index.html','w',encoding='utf-8').write(new_txt)
print('OK patched 640 -> 広島9/27単独 販売中')
